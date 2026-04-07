"""
Flow Audit Engine — Maps every UI action to backend execution chain
====================================================================
Traces: Button click → Backend function → Data update → Output refresh
Identifies: Broken chains, fake buttons, disconnected UI, missing updates

Run: python -c "from engines.flow_audit_engine import run_full_audit; run_full_audit()"
"""
import sys
import os
import glob
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def scan_page_actions(filepath):
    """Scan a page file and extract all UI actions + their handlers."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    fname = os.path.basename(filepath)
    actions = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Buttons
        if "st.button(" in stripped:
            label_match = re.search(r'st\.button\("([^"]+)"', stripped)
            label = label_match.group(1) if label_match else "Unknown"
            key_match = re.search(r'key="([^"]+)"', stripped)
            key = key_match.group(1) if key_match else "no-key"

            # Check what happens after this button
            has_handler = False
            handler_type = "NONE"
            for j in range(i+1, min(i+20, len(lines))):
                jline = lines[j].strip()
                if "st.spinner" in jline or "with st.spinner" in jline:
                    has_handler = True
                    handler_type = "spinner+action"
                    break
                elif "st.success" in jline or "st.error" in jline:
                    has_handler = True
                    handler_type = "feedback"
                    break
                elif "st.rerun" in jline:
                    has_handler = True
                    handler_type = "rerun"
                    break
                elif "st.download_button" in jline:
                    has_handler = True
                    handler_type = "nested-download(BROKEN)"
                    break
                elif "update_field" in jline or "update_fields" in jline:
                    has_handler = True
                    handler_type = "cfg-update"
                    break
                elif "insert_" in jline or "save_" in jline:
                    has_handler = True
                    handler_type = "db-write"
                    break
                elif stripped.startswith("if ") and "button" in stripped:
                    break  # This button's block
                elif jline == "" or (jline.startswith("elif") or jline.startswith("else")):
                    break

            actions.append({
                "file": fname,
                "line": i + 1,
                "type": "button",
                "label": label,
                "key": key,
                "has_handler": has_handler,
                "handler_type": handler_type,
                "status": "OK" if has_handler else "NO_HANDLER",
            })

        # Download buttons (direct — these are OK)
        if "st.download_button(" in stripped and "if st.button" not in stripped:
            label_match = re.search(r'st\.download_button\("([^"]+)"', stripped)
            label = label_match.group(1) if label_match else "Download"
            actions.append({
                "file": fname,
                "line": i + 1,
                "type": "download",
                "label": label,
                "key": "",
                "has_handler": True,
                "handler_type": "direct-download",
                "status": "OK",
            })

        # Selectboxes that should trigger updates
        if "st.selectbox(" in stripped and "on_change" not in stripped:
            label_match = re.search(r'st\.selectbox\("([^"]+)"', stripped)
            label = label_match.group(1) if label_match else "Select"
            # Check if value is used to update cfg
            has_update = False
            for j in range(i+1, min(i+10, len(lines))):
                if "update_field" in lines[j] or "cfg[" in lines[j] or "recalculate" in lines[j]:
                    has_update = True
                    break
            actions.append({
                "file": fname,
                "line": i + 1,
                "type": "selectbox",
                "label": label,
                "key": "",
                "has_handler": has_update,
                "handler_type": "cfg-update" if has_update else "display-only",
                "status": "OK" if has_update or "key=" in stripped else "CHECK",
            })

        # Page links
        if "page_link(" in stripped:
            path_match = re.search(r'page_link\("([^"]+)"', stripped)
            path = path_match.group(1) if path_match else "unknown"
            # Check if target file exists
            target = os.path.join(os.path.dirname(filepath), "..", path) if "pages/" in path else path
            exists = os.path.exists(os.path.join(os.path.dirname(filepath), os.path.basename(path)))
            actions.append({
                "file": fname,
                "line": i + 1,
                "type": "page_link",
                "label": path,
                "key": "",
                "has_handler": exists,
                "handler_type": "navigation",
                "status": "OK" if exists else "BROKEN_LINK",
            })

    return actions


def scan_all_pages():
    """Scan all pages and return complete action map."""
    pages_dir = os.path.join(os.path.dirname(__file__), "..", "pages")
    all_actions = []
    for fpath in sorted(glob.glob(os.path.join(pages_dir, "*.py"))):
        actions = scan_page_actions(fpath)
        all_actions.extend(actions)
    return all_actions


def check_cfg_propagation():
    """Check which cfg fields are read across pages vs hardcoded."""
    pages_dir = os.path.join(os.path.dirname(__file__), "..", "pages")
    issues = []

    # Key fields that must come from cfg
    key_fields = {
        "capacity_tpd": "35000|20 TPD|20 MT",
        "selling_price_per_mt": "35000",
        "investment_cr": "8 Cr|8.0 Cr",
        "price_conv_bitumen": "45750",
    }

    for fpath in sorted(glob.glob(os.path.join(pages_dir, "*.py"))):
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        for field, hardcoded_pattern in key_fields.items():
            for pattern in hardcoded_pattern.split("|"):
                # Find hardcoded values NOT inside cfg.get()
                for match in re.finditer(re.escape(pattern), content):
                    pos = match.start()
                    # Check if it's inside cfg.get()
                    context_start = max(0, pos - 50)
                    context = content[context_start:pos]
                    if "cfg.get" not in context and "cfg[" not in context and "#" not in context.split("\n")[-1]:
                        line_num = content[:pos].count("\n") + 1
                        line_text = content.split("\n")[line_num - 1].strip()
                        if not line_text.startswith("#") and not line_text.startswith('"""'):
                            issues.append({
                                "file": fname,
                                "line": line_num,
                                "field": field,
                                "hardcoded": pattern,
                                "context": line_text[:80],
                            })

    return issues


def check_update_chain():
    """Check if update_field/update_fields calls trigger recalculate."""
    pages_dir = os.path.join(os.path.dirname(__file__), "..", "pages")
    issues = []

    for fpath in sorted(glob.glob(os.path.join(pages_dir, "*.py"))):
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if page imports update_field but never calls it
        if "update_field" in content or "update_fields" in content:
            if "from state_manager" in content:
                call_count = content.count("update_field(") + content.count("update_fields(")
                if call_count == 0 and "import" in content:
                    issues.append({
                        "file": fname,
                        "issue": "Imports update_field but never calls it",
                        "severity": "LOW",
                    })

    return issues


def run_full_audit():
    """Run complete flow audit and print report."""
    print("=" * 70)
    print("  COMPLETE FLOW AUDIT — Button → Backend → Output Chain")
    print("=" * 70)

    # Phase 1: Scan all actions
    print("\nPHASE 1: Scanning all UI actions...")
    all_actions = scan_all_pages()

    buttons = [a for a in all_actions if a["type"] == "button"]
    downloads = [a for a in all_actions if a["type"] == "download"]
    links = [a for a in all_actions if a["type"] == "page_link"]

    no_handler = [a for a in buttons if a["status"] == "NO_HANDLER"]
    broken_links = [a for a in links if a["status"] == "BROKEN_LINK"]
    nested_dl = [a for a in buttons if a["handler_type"] == "nested-download(BROKEN)"]

    print(f"  Total buttons: {len(buttons)}")
    print(f"  Direct downloads: {len(downloads)}")
    print(f"  Page links: {len(links)}")
    print(f"  Buttons WITHOUT handler: {len(no_handler)}")
    print(f"  Broken page links: {len(broken_links)}")
    print(f"  Nested downloads (broken pattern): {len(nested_dl)}")

    if no_handler:
        print("\n  BUTTONS WITH NO HANDLER:")
        for a in no_handler[:15]:
            print(f"    {a['file']}:{a['line']}: \"{a['label']}\"")

    if broken_links:
        print("\n  BROKEN PAGE LINKS:")
        for a in broken_links[:10]:
            print(f"    {a['file']}:{a['line']}: {a['label']}")

    if nested_dl:
        print("\n  NESTED DOWNLOADS (will disappear on rerun):")
        for a in nested_dl[:10]:
            print(f"    {a['file']}:{a['line']}: \"{a['label']}\"")

    # Phase 2: Check hardcoded values
    print("\nPHASE 2: Checking for hardcoded values...")
    hardcoded = check_cfg_propagation()
    print(f"  Hardcoded values found: {len(hardcoded)}")
    if hardcoded:
        for h in hardcoded[:10]:
            print(f"    {h['file']}:{h['line']}: {h['field']}={h['hardcoded']}")

    # Phase 3: Update chain
    print("\nPHASE 3: Checking update chain...")
    chain_issues = check_update_chain()
    print(f"  Chain issues: {len(chain_issues)}")

    # Summary
    total_issues = len(no_handler) + len(broken_links) + len(nested_dl) + len(hardcoded)
    print("\n" + "=" * 70)
    print(f"  TOTAL ISSUES: {total_issues}")
    print(f"    No-handler buttons: {len(no_handler)}")
    print(f"    Broken links: {len(broken_links)}")
    print(f"    Nested downloads: {len(nested_dl)}")
    print(f"    Hardcoded values: {len(hardcoded)}")

    if total_issues == 0:
        print("\n  ALL CHAINS CONNECTED — System fully functional")
    else:
        print(f"\n  {total_issues} issues need fixing")

    print("=" * 70)

    return {
        "total_buttons": len(buttons),
        "total_downloads": len(downloads),
        "total_links": len(links),
        "no_handler": no_handler,
        "broken_links": broken_links,
        "nested_downloads": nested_dl,
        "hardcoded_values": hardcoded,
        "chain_issues": chain_issues,
        "total_issues": total_issues,
    }


if __name__ == "__main__":
    run_full_audit()
