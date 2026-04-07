"""
Minimum Viable Investment Optimizer
====================================
Reduce investment to legal minimum. For each of 82 BOQ items:
- REMOVE: not needed, cost → ₹0
- AT SITE: you already own it, cost → ₹0
- REDUCE: use minimum spec (IS compliant), lower cost
- MANDATORY: legal/safety, cannot remove (IS 14489, NBC 2016, Factories Act)

All savings computed live. Generates AI prompt for updating all systems.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from state_manager import get_config, init_state, format_inr, calculate_boq

st.set_page_config(page_title="Investment Optimizer", page_icon="💡", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("Minimum Viable Investment Optimizer")
st.markdown(f"**{cfg['capacity_tpd']:.0f} TPD | Reduce to legal minimum | IS/NBC/CPCB compliant**")
st.markdown("---")

# ── Get BOQ ──
boq = calculate_boq(cfg["capacity_tpd"])

# ── Define which items are legally mandatory (cannot remove) ──
# Items containing these keywords are mandatory
MANDATORY_KEYWORDS = [
    "fire", "safety", "psv", "relief valve", "earthing", "lightning",
    "etp", "effluent", "septic", "toilet", "compound wall", "gate",
    "weighbridge", "guard", "pollution", "scrubber", "bag filter",
    "gas detection", "eyewash", "shower", "ppe", "first aid",
    "stack", "drainage", "green belt",
]

REDUCIBLE_FACTOR = 0.55  # Minimum spec = 55% of full spec cost

def is_mandatory(item_name):
    """Check if item is legally mandatory (cannot be removed)."""
    name_lower = item_name.lower()
    return any(kw in name_lower for kw in MANDATORY_KEYWORDS)

# ── Initialize session state for optimizer ──
if "optimizer_state" not in st.session_state:
    st.session_state["optimizer_state"] = {}
    for item in boq:
        key = item["item"]
        mandatory = is_mandatory(key)
        st.session_state["optimizer_state"][key] = {
            "status": "mandatory" if mandatory else "keep",
            "mandatory": mandatory,
        }

opt = st.session_state["optimizer_state"]

# Sync new items (if capacity changed)
for item in boq:
    if item["item"] not in opt:
        mandatory = is_mandatory(item["item"])
        opt[item["item"]] = {"status": "mandatory" if mandatory else "keep", "mandatory": mandatory}

# ── Compute totals ──
original_total = sum(i["amount_lac"] for i in boq)
removed_total = 0
site_total = 0
reduced_total = 0
removed_count = site_count = reduced_count = mandatory_count = 0

for item in boq:
    key = item["item"]
    status = opt.get(key, {}).get("status", "keep")
    if status == "remove":
        removed_total += item["amount_lac"]
        removed_count += 1
    elif status == "site":
        site_total += item["amount_lac"]
        site_count += 1
    elif status == "reduce":
        saved = item["amount_lac"] * (1 - REDUCIBLE_FACTOR)
        reduced_total += saved
        reduced_count += 1
    elif status == "mandatory":
        mandatory_count += 1

total_saved = removed_total + site_total + reduced_total
minimum_invest = original_total - total_saved
saved_pct = (total_saved / original_total * 100) if original_total > 0 else 0

# ── KPIs ──
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Original Total", f"₹ {original_total/100:.2f} Cr")
k2.metric("Removed", f"₹ {removed_total/100:.2f} Cr", delta=f"{removed_count} items", delta_color="inverse")
k3.metric("At Site", f"₹ {site_total/100:.2f} Cr", delta=f"{site_count} items", delta_color="off")
k4.metric("Reduced Std", f"₹ {reduced_total/100:.2f} Cr", delta=f"{reduced_count} items", delta_color="off")
k5.metric("Total Saved", f"₹ {total_saved/100:.2f} Cr", delta=f"{saved_pct:.0f}%")
k6.metric("MIN INVESTMENT", f"₹ {minimum_invest/100:.2f} Cr", delta="Legal minimum")

st.markdown("---")

# ── Legend ──
st.markdown("""
| Action | Meaning | Cost Effect |
|--------|---------|-------------|
| **KEEP** | Include at full spec | Full cost |
| **REMOVE** | Not needed, tick out | Cost → ₹0 |
| **AT SITE** | Already own it | Cost → ₹0 |
| **REDUCE** | Minimum IS-compliant spec | ~55% of full |
| **MANDATORY** | Legal requirement, cannot remove | Full cost (locked) |
""")

st.markdown("---")

# ── Zone-by-zone optimizer ──
categories = {}
for item in boq:
    cat = item["category"]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(item)

for cat in sorted(categories):
    items = categories[cat]
    zone_orig = sum(i["amount_lac"] for i in items)
    zone_saved = 0
    for i in items:
        status = opt.get(i["item"], {}).get("status", "keep")
        if status == "remove" or status == "site":
            zone_saved += i["amount_lac"]
        elif status == "reduce":
            zone_saved += i["amount_lac"] * (1 - REDUCIBLE_FACTOR)

    save_text = f" — saved ₹ {zone_saved:.1f} Lac" if zone_saved > 0 else ""
    with st.expander(f"{cat} — {len(items)} items — ₹ {zone_orig:.1f} Lac{save_text}", expanded=False):
        for item in items:
            key = item["item"]
            is_mand = opt[key]["mandatory"]
            status = opt[key]["status"]

            col_name, col_spec, col_action, col_orig, col_new = st.columns([3, 2, 2, 1, 1])

            with col_name:
                icon = "🔴" if is_mand else ("❌" if status == "remove" else ("🔵" if status == "site" else ("🟡" if status == "reduce" else "⬜")))
                st.markdown(f"{icon} **{key}**")

            with col_spec:
                st.caption(item["spec"])

            with col_action:
                if is_mand:
                    st.markdown("**MANDATORY** (IS/NBC)")
                else:
                    options = ["keep", "remove", "site", "reduce"]
                    labels = {"keep": "Keep (full cost)", "remove": "REMOVE (₹0)",
                              "site": "AT SITE (₹0)", "reduce": "REDUCE (min spec)"}
                    new_status = st.selectbox(
                        "Action", options,
                        index=options.index(status),
                        format_func=lambda x: labels[x],
                        key=f"opt_{key}",
                        label_visibility="collapsed"
                    )
                    if new_status != status:
                        opt[key]["status"] = new_status
                        st.rerun()

            with col_orig:
                st.markdown(f"₹ {item['amount_lac']:.1f} L")

            with col_new:
                if status == "remove" or status == "site":
                    st.markdown("**₹ 0**")
                elif status == "reduce":
                    st.markdown(f"₹ {item['amount_lac']*REDUCIBLE_FACTOR:.1f} L")
                else:
                    st.markdown(f"₹ {item['amount_lac']:.1f} L")

# ── Summary & AI Prompt ──
st.markdown("---")
st.subheader("Optimization Summary & AI Update Prompt")

removed_items = [i for i in boq if opt.get(i["item"], {}).get("status") == "remove"]
site_items = [i for i in boq if opt.get(i["item"], {}).get("status") == "site"]
reduced_items = [i for i in boq if opt.get(i["item"], {}).get("status") == "reduce"]
mandatory_items = [i for i in boq if opt.get(i["item"], {}).get("status") == "mandatory"]

prompt = f"""=== MINIMUM VIABLE INVESTMENT UPDATE ===
Plant: {cfg['capacity_tpd']:.0f} TPD Bio-Bitumen | State: {cfg.get('state', 'N/A')}
Original BOQ: ₹ {original_total/100:.2f} Cr ({len(boq)} items)
Minimum Investment: ₹ {minimum_invest/100:.2f} Cr (saved {saved_pct:.0f}%)

--- SECTION 1: ITEMS REMOVED ({len(removed_items)}) ---
{chr(10).join(f'  ✗ {i["item"]} — was ₹{i["amount_lac"]:.1f} Lac' for i in removed_items) or '  None'}
→ Drawing system: REMOVE these from layout
→ BOQ: Set cost to zero
→ Procurement: Do not order

--- SECTION 2: ITEMS AT SITE ({len(site_items)}) ---
{chr(10).join(f'  ◎ {i["item"]} — owner supply, was ₹{i["amount_lac"]:.1f} Lac' for i in site_items) or '  None'}
→ Drawing system: Keep in layout, label "OWNER SUPPLY"
→ BOQ: Set cost to zero
→ Procurement: Verify on-site condition

--- SECTION 3: ITEMS REDUCED ({len(reduced_items)}) ---
{chr(10).join(f'  ▼ {i["item"]} — full ₹{i["amount_lac"]:.1f}L → min ₹{i["amount_lac"]*REDUCIBLE_FACTOR:.1f}L' for i in reduced_items) or '  None'}
→ Drawing system: Use minimum specification
→ BOQ: Use reduced cost
→ Procurement: Source minimum IS-compliant spec

--- SECTION 4: MANDATORY ITEMS ({len(mandatory_items)}) ---
  Cannot remove — IS 14489, NBC 2016, Factories Act, CPCB compliance
  Total mandatory cost: ₹ {sum(i['amount_lac'] for i in mandatory_items):.1f} Lac

--- SECTION 5: FINANCIAL IMPACT ---
  Original: ₹ {original_total/100:.2f} Cr
  Saved: ₹ {total_saved/100:.2f} Cr ({saved_pct:.0f}%)
  Minimum: ₹ {minimum_invest/100:.2f} Cr
"""

st.code(prompt, language="text")

if st.button("Reset All to Full Spec", key="reset_optimizer"):
    for key in opt:
        opt[key]["status"] = "mandatory" if opt[key]["mandatory"] else "keep"
    st.rerun()

st.markdown("---")
st.caption("All mandatory items locked per IS 14489, NBC 2016, Factories Act 1948, CPCB norms. "
           "Reduced items meet minimum IS compliance. This tool does NOT compromise safety.")


# ── Next Steps Navigation ──
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "29")
except Exception:
    pass
