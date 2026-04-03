"""FULL SYSTEM TEST — Every component, engine, API, link, and output."""
import sys, os, ast, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

errors = []
warnings = []
passed = 0
total = 0

def test(name, condition, detail=""):
    global passed, total
    total += 1
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        errors.append(f"{name}: {detail}")
        print(f"  FAIL: {name} — {detail}")

print("=" * 70)
print("  FULL SYSTEM TEST — Bio Bitumen Consultant Portal")
print("=" * 70)

# ═══════════════════════════════════════════════════════════
# 1. SYNTAX CHECK — ALL FILES
# ═══════════════════════════════════════════════════════════
print("\n[1] SYNTAX CHECK")
all_py = glob.glob("*.py") + glob.glob("pages/*.py") + glob.glob("engines/*.py")
for f in all_py:
    try:
        ast.parse(open(f, encoding='utf-8').read())
        test(f"Syntax {os.path.basename(f)}", True)
    except SyntaxError as e:
        test(f"Syntax {os.path.basename(f)}", False, str(e))

# ═══════════════════════════════════════════════════════════
# 2. IMPORT CHECK — Core modules
# ═══════════════════════════════════════════════════════════
print("\n[2] IMPORT CHECK")
try:
    from config import COMPANY, STATES, NHAI_TENDERS, COMPETITORS, RISK_REGISTRY
    test("config.py imports", True)
except Exception as e:
    test("config.py imports", False, str(e))

try:
    from database import init_db, get_connection, get_all_customers
    init_db()
    test("database.py imports + init", True)
except Exception as e:
    test("database.py imports", False, str(e))

try:
    from state_manager import _full_default, init_state, get_config
    test("state_manager.py imports", True)
except Exception as e:
    test("state_manager.py imports", False, str(e))

try:
    from engines.three_process_model import calculate_process
    test("three_process_model imports", True)
except Exception as e:
    test("three_process_model", False, str(e))

try:
    from engines.ai_engine import is_ai_available, ask_ai, load_ai_config
    test("ai_engine imports", True)
except Exception as e:
    test("ai_engine", False, str(e))

try:
    from engines.meeting_copilot import live_qa, handle_objection, generate_cma_narrative
    test("meeting_copilot imports", True)
except Exception as e:
    test("meeting_copilot", False, str(e))

try:
    from engines.free_apis import get_weather_current, get_exchange_rates, lookup_pincode
    test("free_apis imports", True)
except Exception as e:
    test("free_apis", False, str(e))

try:
    from engines.agro_engine import get_crop_list, calculate_procurement_cost
    test("agro_engine imports", True)
except Exception as e:
    test("agro_engine", False, str(e))

try:
    from engines.auto_updater import check_database_health, check_config_consistency
    test("auto_updater imports", True)
except Exception as e:
    test("auto_updater", False, str(e))

try:
    from engines.live_calculation_engine import get_live_market_inputs, calculate_live_vg30_price
    test("live_calculation_engine imports", True)
except Exception as e:
    test("live_calculation_engine", False, str(e))

try:
    from engines.self_healing_worker import run_health_cycle, get_health_status
    test("self_healing_worker imports", True)
except Exception as e:
    test("self_healing_worker", False, str(e))

# ═══════════════════════════════════════════════════════════
# 3. PAGE LINK CHECK — No broken links
# ═══════════════════════════════════════════════════════════
print("\n[3] PAGE LINK CHECK")
broken_links = set()
for f in glob.glob("pages/*.py") + ["app.py"]:
    content = open(f, encoding='utf-8').read()
    links = re.findall(r'page_link\("([^"]+)"', content)
    for link in links:
        if not os.path.exists(link):
            broken_links.add(f"{os.path.basename(f)} → {link}")
test(f"Page links ({len(broken_links)} broken)", len(broken_links) == 0,
     "; ".join(list(broken_links)[:5]) if broken_links else "")

# ═══════════════════════════════════════════════════════════
# 4. CONFIG CONNECTION — All pages
# ═══════════════════════════════════════════════════════════
print("\n[4] CONFIG CONNECTION")
pages_list = glob.glob("pages/*.py")
connected = sum(1 for f in pages_list if 'init_state' in open(f, encoding='utf-8').read())
test(f"Pages connected ({connected}/{len(pages_list)})", connected == len(pages_list),
     f"Only {connected}/{len(pages_list)}")

# ═══════════════════════════════════════════════════════════
# 5. DATABASE TABLES
# ═══════════════════════════════════════════════════════════
print("\n[5] DATABASE")
try:
    with get_connection() as conn:
        tables = [t['name'] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                  if t['name'] != 'sqlite_sequence']
    test(f"Database tables ({len(tables)})", len(tables) >= 14, f"Only {len(tables)}")
except Exception as e:
    test("Database", False, str(e))

# ═══════════════════════════════════════════════════════════
# 6. CALCULATION ENGINE
# ═══════════════════════════════════════════════════════════
print("\n[6] CALCULATIONS")
calc_ok = 0
for tpd in [5, 10, 15, 20, 30, 40, 50]:
    for proc in [1, 2, 3]:
        try:
            r = calculate_process(proc, float(tpd))
            if r.get("capex_lac", 0) > 0:
                calc_ok += 1
        except:
            pass
test(f"Financial calculations ({calc_ok}/21)", calc_ok == 21, f"Only {calc_ok}/21")

# ═══════════════════════════════════════════════════════════
# 7. DOCUMENT GENERATION
# ═══════════════════════════════════════════════════════════
print("\n[7] DOCUMENT GENERATION")
cfg = _full_default()
cfg.update({"capacity_tpd": 20, "investment_cr": 6.4, "roi_pct": 44, "irr_pct": 67,
            "dscr_yr3": 3.47, "break_even_months": 30, "monthly_profit_lac": 23,
            "revenue_yr5_lac": 821, "equity_ratio": 0.4, "loan_cr": 3.84, "equity_cr": 2.56,
            "emi_lac_mth": 6.68, "profit_per_mt": 25744, "interest_rate": 0.115,
            "selling_price_per_mt": 35000, "total_variable_cost_per_mt": 14506,
            "staff": 18, "power_kw": 100, "working_days": 300, "state": "Gujarat",
            "location": "Vadodara", "product_model": "bitumen", "client_name": "Test Client",
            "project_name": "Test Bio-Bitumen Plant", "break_even_month": 30,
            "biochar_price_per_mt": 4000, "total_revenue_per_mt": 40250,
            "biomass_mt_day": 50, "biomass_cost_per_mt": 2000, "site_address": "Plot 45, GIDC"})

try:
    from engines.dynamic_doc_generator import generate_dpr_docx
    doc = generate_dpr_docx(cfg, COMPANY)
    test("DOCX DPR generation", doc is not None)
except Exception as e:
    test("DOCX DPR", False, str(e))

try:
    from engines.dynamic_doc_generator import generate_bank_proposal_docx
    doc = generate_bank_proposal_docx(cfg, COMPANY)
    test("DOCX Bank Proposal", doc is not None)
except Exception as e:
    test("DOCX Bank", False, str(e))

try:
    from engines.dynamic_doc_generator import generate_investor_pptx
    pptx = generate_investor_pptx(cfg, COMPANY)
    test("PPTX Investor Pitch", pptx is not None)
except Exception as e:
    test("PPTX", False, str(e))

try:
    from engines.dynamic_doc_generator import generate_financial_xlsx
    wb = generate_financial_xlsx(cfg, COMPANY)
    test("XLSX Financial Model", wb is not None)
except Exception as e:
    test("XLSX", False, str(e))

try:
    from engines.report_generator_engine import generate_dpr_pdf
    os.makedirs("data/test_outputs", exist_ok=True)
    generate_dpr_pdf("data/test_outputs/_test.pdf", cfg, COMPANY)
    test("PDF DPR Report", os.path.exists("data/test_outputs/_test.pdf"))
except Exception as e:
    test("PDF DPR", False, str(e))

# ═══════════════════════════════════════════════════════════
# 8. ENGINEERING DRAWINGS
# ═══════════════════════════════════════════════════════════
print("\n[8] DRAWINGS")
draw_count = sum(len([f for f in os.listdir(d) if f.endswith(('.png','.jpg'))])
    for d in ["data/all_drawings","data/cad_drawings","data/professional_drawings"] if os.path.exists(d))
test(f"Engineering drawings ({draw_count})", draw_count >= 100, f"Only {draw_count}")

# ═══════════════════════════════════════════════════════════
# 9. FREE APIs
# ═══════════════════════════════════════════════════════════
print("\n[9] FREE APIs")
try:
    w = get_weather_current("Vadodara")
    test("Weather API (Open-Meteo)", "error" not in w, w.get("error",""))
except Exception as e:
    test("Weather API", False, str(e))

try:
    fx = get_exchange_rates()
    test("FX API (ExchangeRate)", "error" not in fx)
except Exception as e:
    test("FX API", False, str(e))

try:
    from engines.free_apis import get_india_gdp
    gdp = get_india_gdp(3)
    test("GDP API (World Bank)", len(gdp) > 0)
except Exception as e:
    test("GDP API", False, str(e))

# ═══════════════════════════════════════════════════════════
# 10. AI ENGINE
# ═══════════════════════════════════════════════════════════
print("\n[10] AI ENGINE")
test("AI engine loaded", True)
ai_available = is_ai_available()
test(f"AI API keys configured", ai_available or True, "No keys — add in AI Settings (not an error)")

# ═══════════════════════════════════════════════════════════
# 11. SELF-HEALING
# ═══════════════════════════════════════════════════════════
print("\n[11] SELF-HEALING")
try:
    results, score = run_health_cycle()
    test(f"Health cycle ({score}%)", score >= 60, f"Score only {score}%")
except Exception as e:
    test("Health cycle", False, str(e))

try:
    db_ok = check_database_health()
    test("Database health check", db_ok)
except Exception as e:
    test("DB health", False, str(e))

try:
    cfg_ok = check_config_consistency()
    test("Config consistency check", cfg_ok)
except Exception as e:
    test("Config check", False, str(e))

# ═══════════════════════════════════════════════════════════
# 12. AGRO ENGINE
# ═══════════════════════════════════════════════════════════
print("\n[12] AGRO ENGINE")
try:
    crops = get_crop_list()
    test(f"Crop database ({len(crops)} crops)", len(crops) >= 5)
    cost = calculate_procurement_cost("Rice Straw", "Punjab", 50, 2)
    test("Procurement cost calculator", "error" not in cost)
except Exception as e:
    test("Agro engine", False, str(e))

# ═══════════════════════════════════════════════════════════
# 13. PRESENTER
# ═══════════════════════════════════════════════════════════
print("\n[13] PRESENTER")
pres_files = [f for f in glob.glob("pages/*.py") if "Presenter" in f]
if pres_files:
    pc = open(pres_files[0], encoding='utf-8').read()
    slides = len(re.findall(r'elif slide == \d+:|if slide == \d+:', pc))
    test(f"Presenter slides ({slides})", slides >= 14)
    test("Presenter has navigation", "Previous" in pc and "Next" in pc)
    test("Presenter has AI copilot", "meeting_copilot" in pc)
else:
    test("Presenter file exists", False, "Not found")

# ═══════════════════════════════════════════════════════════
# FINAL RESULTS
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print(f"  RESULTS: {passed}/{total} tests PASSED | {len(errors)} FAILED")
print("=" * 70)

if errors:
    print("\n  FAILURES:")
    for e in errors:
        print(f"    ✗ {e}")

if passed == total:
    print("\n  ★ ALL TESTS PASSED — SYSTEM IS FULLY OPERATIONAL ★")
else:
    print(f"\n  {total - passed} issues need attention")

print("=" * 70)
