# CLAUDE CODE — MASTER AUDIT & AUTO-FIX PROMPT
# Bio-Bitumen Consultant Portal — Complete System Check
# Paste this entire prompt when starting a new Claude Code session

---

## PROJECT LOCATION
```
Primary: C:\Users\HP\Desktop\Bio Bitumen Full Working all document\consultant_portal
GitHub: https://github.com/pacpltradingdesk-dotcom/bio-bitumen-consultant-portal
Run: python -m streamlit run app.py --server.port 8502
```

## WHAT THIS SYSTEM IS
A Streamlit multi-page dashboard (52 pages, 36 engines, 8 utilities) for bio-bitumen plant consulting.
- Single source of truth: `state_manager.py` → `DEFAULTS` dict + `recalculate()` function
- ALL financial values flow from cfg (session state) — ZERO hardcoded outputs
- 82-item BOQ across 15 plant zones (A-O), auto-scaled by capacity
- 7 AI providers with auto-fallback chain (OpenAI→Claude→Gemini→DeepSeek→Groq→Free→Offline)
- Plant engineering with deterministic equipment sizing from capacity
- Drawing prompt generator with IS standards, safety clearances, colour codes

---

## TASK: COMPLETE CROSS-FUNCTIONAL AUDIT + AUTO-FIX

### STEP 1 — Run the existing audit script first
```bash
cd "C:/Users/HP/Desktop/Bio Bitumen Full Working all document/consultant_portal"
python audit_all_financials.py
```
This runs 57 checks across 8 phases. If any ERRORS appear, fix them before proceeding.

### STEP 2 — Check input propagation (THE MOST IMPORTANT TEST)
The golden rule: **Change ANY input → ALL outputs must update.**

Test this by:
1. Read `state_manager.py` — find all fields in DEFAULTS dict
2. For each key field (capacity_tpd, state, selling_price_per_mt, bio_blend_pct):
   - Search ALL pages/*.py for where that field is used
   - Verify it reads from `cfg.get('field_name')` not hardcoded
   - If hardcoded: FIX IT to read from cfg
3. Specifically check these high-risk files:
   - `pages/01_🎯_Presenter.py` — 52 slides, all must use cfg values
   - `pages/02_📊_Dashboard.py` — plant config section
   - `pages/13_📈_Market.py` — VG30 price, bio-bitumen price
   - `pages/22_Process_Flow.py` — capacity, plot dimensions
   - `pages/23_⚙️_Plant_Design.py` — equipment list, BOQ
   - `pages/30_💰_Financial.py` — all financial inputs
   - `pages/31_Detailed_Costing.py` — 10 cost heads
   - `pages/38_Sensitivity.py` — base prices for stress test
   - `pages/43_🛣️_NHAI_Tenders.py` — revenue calculation
   - `pages/51_AI_Drawings.py` — AI image prompts
   - `pages/52_AI_Plant_Layouts.py` — DALL-E prompts
   - `pages/64_Send.py` — email/WhatsApp message values

### STEP 3 — Check drawing prompts update with inputs
The drawing system has 3 engines that must ALL use computed specs:

1. **engines/ai_image_generator.py** → `get_prompts(tpd, cfg)` 
   - Must include: reactor Ø×H, dryer Ø×L, tank volumes, plot dimensions
   - Must change when capacity changes (test 20 TPD vs 50 TPD)

2. **engines/dalle_layout_engine.py** → `build_dalle_prompt(..., cfg=cfg)`
   - Must include: computed machinery specs from plant_engineering
   - Must include: safety clearances (15m reactor, 30m control room)

3. **engines/drawing_prompt_generator.py** → `generate_drawing_prompt(cfg, type)`
   - Must include: anti-randomness clause
   - Must include: IS 2379 colour codes, IS 14489 clearances

**TEST:** Generate prompts for 20 TPD and 50 TPD — they MUST be different.
If same: the engine is not reading cfg. Fix it.

### STEP 4 — Check cross-calculation consistency
These values must be consistent across ALL pages:

| Value | Source | Must Match In |
|-------|--------|---------------|
| capacity_tpd | cfg | ALL 52 pages, ALL drawing prompts, ALL financial tables |
| investment_cr | cfg (from recalculate) | Dashboard, Financial, DPR, Send, Packages |
| roi_pct | cfg (from recalculate) | Dashboard, Financial, ROI Calc, Presenter |
| irr_pct | cfg (from recalculate) | Dashboard, Financial, Presenter, Send |
| dscr_yr3 | cfg (from recalculate) | Dashboard, Financial, Document Hub |
| selling_price_per_mt | cfg | Market, Sensitivity, ROI Calc, NHAI, Product Grades |
| price_conv_bitumen | cfg | Detailed Costing, Market, Break-Even |

For each: grep ALL pages for the field name. If any page uses a hardcoded 
number instead of cfg.get(), that's a bug. Fix it.

### STEP 5 — Check config CAPACITY_LABELS match MASTER_DATA
```python
from master_data_loader import PLANTS
from config import CAPACITY_LABELS
for key in PLANTS:
    plant_inv = PLANTS[key]["inv_cr"]
    label_inv = float(CAPACITY_LABELS[key].split("INR")[1].split("Cr")[0].strip())
    assert abs(plant_inv - label_inv) < 0.5, f"MISMATCH {key}"
```

### STEP 6 — Check navigation works
In `pages/01_🎯_Presenter.py`:
- TOTAL_SLIDES must equal number of `elif slide == N:` blocks
- Navigation callbacks must use `st.session_state` directly (not captured args)
- No selectbox `if jump != slide: st.rerun()` pattern (causes race condition)
- 25 TPD must be in capacity dropdown

### STEP 7 — Check download buttons work
Search ALL pages for this broken pattern:
```python
if st.button("Download"):
    st.download_button(...)  # BROKEN — disappears on rerun
```
Replace with:
```python
st.download_button("Download", data, filename)  # Direct — always visible
```

### STEP 8 — Check page_link references match filenames
After any file rename, ALL `st.page_link("pages/XX_...")` calls must 
point to existing files. Run:
```python
import glob, re
pages = {os.path.basename(f) for f in glob.glob('pages/*.py')}
for f in glob.glob('**/*.py', recursive=True):
    for match in re.findall(r'pages/\S+\.py', open(f, encoding='utf-8').read()):
        if os.path.basename(match) not in pages:
            print(f"BROKEN LINK: {f} → {match}")
```

### STEP 9 — Check encoding
ALL `open()` calls reading text files must have `encoding="utf-8"`.
Windows defaults to cp1252 which crashes on emoji/special chars.

### STEP 10 — Deploy required engines if missing
These engines MUST exist and work:

| Engine | Purpose | Must Have |
|--------|---------|-----------|
| state_manager.py | Single source of truth | DEFAULTS (48+ fields), recalculate(), calculate_boq() |
| engines/detailed_costing.py | DPR cost sheet | 10 cost heads, 9 states, annual P&L |
| engines/dpr_financial_engine.py | WC, BE, CF, FG | 4 calculator functions |
| engines/plant_engineering.py | Equipment sizing | compute_all(), get_machinery_list(), SAFETY_CLEARANCES |
| engines/drawing_prompt_generator.py | Drawing prompts | 6 types, anti-randomness, IS standards |
| engines/ai_engine.py | 7 AI providers | ask_ai() with fallback chain, offline engine |
| engines/ai_image_generator.py | AI drawings | get_prompts(tpd, cfg) with computed specs |
| engines/dalle_layout_engine.py | DALL-E prompts | build_dalle_prompt(..., cfg=cfg) |
| engines/free_apis.py | Live data | exchange rate, crude oil, mandi prices |

If any is missing or broken: CREATE or FIX it.

---

## HOW TO VERIFY SUCCESS
After all fixes, run:
```bash
python audit_all_financials.py
python full_audit_test.py
```
Both must show: **0 ERRORS, 0 WARNINGS, AAA+ RATING**

Then manually test:
1. Open http://localhost:8502
2. Go to Presenter → Set capacity to 25 TPD, state Gujarat
3. Click Next through all 52 slides — verify no crashes
4. Go to Detailed Costing → verify cost/tonne updates
5. Go to AI Plant Layouts → verify prompt shows 25 TPD specs
6. Go to Dashboard → verify plant config shows 25 TPD

---

## RULES FOR FIXING
1. NEVER hardcode a financial number — always read from cfg
2. NEVER use `st.button()` wrapping `st.download_button()` — use direct download
3. NEVER define nav callbacks as closures inside if blocks — use top-level functions
4. NEVER use `open()` without `encoding="utf-8"` on Windows
5. ALWAYS test with multiple capacities (5, 20, 25, 50 TPD) after any fix
6. ALWAYS commit and push after fixing — user needs changes on GitHub
7. ALWAYS run syntax check on ALL files before committing
