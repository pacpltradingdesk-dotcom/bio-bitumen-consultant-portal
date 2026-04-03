"""Complete System Audit — Rating & Ranking"""
import sys, os, ast, json, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("  BIO BITUMEN CONSULTANT PORTAL — COMPLETE SYSTEM AUDIT")
print("  Date: 2026-04-03")
print("=" * 70)

scores = {}
errors = []

# 1. SYNTAX
print("\n1. SYNTAX CHECK")
all_py = glob.glob("*.py") + glob.glob("pages/*.py") + glob.glob("pages/_detail/*.py") + glob.glob("engines/*.py")
syntax_pass = 0
for f in all_py:
    try:
        ast.parse(open(f, encoding='utf-8').read())
        syntax_pass += 1
    except SyntaxError as e:
        errors.append(f"SYNTAX: {f}: {e}")
scores["Syntax"] = 100 if syntax_pass == len(all_py) else 80
print(f"   {syntax_pass}/{len(all_py)} files | Score: {scores['Syntax']}/100")

# 2. CONFIG CONNECTION
print("\n2. CONFIG CONNECTION")
pages = glob.glob("pages/*.py") + glob.glob("pages/_detail/*.py")
connected = sum(1 for f in pages if 'init_state' in open(f, encoding='utf-8').read())
scores["Config Link"] = int(connected / len(pages) * 100)
print(f"   {connected}/{len(pages)} pages | Score: {scores['Config Link']}/100")

# 3. DATABASE
print("\n3. DATABASE")
try:
    from database import init_db, get_connection
    init_db()
    with get_connection() as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        tc = len([t for t in tables if t['name'] != 'sqlite_sequence'])
    scores["Database"] = min(100, int(tc / 14 * 100))
    print(f"   {tc}/14 tables | Score: {scores['Database']}/100")
except Exception as e:
    scores["Database"] = 0; print(f"   FAIL: {e}")

# 4. CONFIG DATA
print("\n4. CONFIG DATA")
try:
    from config import NHAI_TENDERS, COMPETITORS, RISK_REGISTRY, STATES, LICENSE_TYPES, EMI_PRESETS, TRAINING_MODULES, INDUSTRY_NEWS, STATE_SCORES, STATE_COSTS, PPS_SWOT, COMPANY
    checks = {"STATES":len(STATES)==18, "LICENSES":len(LICENSE_TYPES)==25, "TENDERS":len(NHAI_TENDERS)>=30,
              "COMPETITORS":len(COMPETITORS)>=8, "RISKS":len(RISK_REGISTRY)>=18, "EMI":len(EMI_PRESETS)>=5,
              "TRAINING":len(TRAINING_MODULES)>=7, "NEWS":len(INDUSTRY_NEWS)>=12, "SCORES":len(STATE_SCORES)==18,
              "COSTS":len(STATE_COSTS)==18, "SWOT":"strengths" in PPS_SWOT, "COMPANY":"name" in COMPANY}
    p = sum(1 for v in checks.values() if v)
    scores["Config Data"] = int(p / len(checks) * 100)
    print(f"   {p}/{len(checks)} checks | Score: {scores['Config Data']}/100")
except Exception as e:
    scores["Config Data"] = 0

# 5. CALCULATIONS
print("\n5. CALCULATIONS")
try:
    from engines.three_process_model import calculate_process
    cp = 0
    for tpd in [5,10,15,20,30,40,50]:
        for proc in [1,2,3]:
            r = calculate_process(proc, float(tpd))
            if r.get("capex_lac",0) > 0: cp += 1
    scores["Calculations"] = int(cp / 21 * 100)
    print(f"   {cp}/21 scenarios | Score: {scores['Calculations']}/100")
except Exception as e:
    scores["Calculations"] = 0

# 6. DOC GENERATION
print("\n6. DOCUMENT GENERATION")
from state_manager import _full_default
cfg = _full_default()
cfg.update({"capacity_tpd":20,"investment_cr":6.4,"roi_pct":44,"irr_pct":67,"dscr_yr3":3.47,
            "break_even_months":30,"monthly_profit_lac":23,"revenue_yr5_lac":821,"equity_ratio":0.4,
            "loan_cr":3.84,"equity_cr":2.56,"emi_lac_mth":6.68,"profit_per_mt":25744,
            "interest_rate":0.115,"selling_price_per_mt":35000,"total_variable_cost_per_mt":14506,
            "staff":18,"power_kw":100,"working_days":300,"state":"Gujarat","location":"Vadodara",
            "product_model":"bitumen","client_name":"Test","project_name":"Test Project",
            "break_even_month":30,"biochar_price_per_mt":4000,"total_revenue_per_mt":40250,
            "biomass_mt_day":50,"biomass_cost_per_mt":2000})
dg = 0
try:
    from engines.dynamic_doc_generator import generate_dpr_docx, generate_bank_proposal_docx, generate_investor_pptx, generate_financial_xlsx
    if generate_dpr_docx(cfg, COMPANY): dg += 1; print("   DOCX: OK")
    if generate_bank_proposal_docx(cfg, COMPANY): dg += 1; print("   Bank: OK")
    if generate_investor_pptx(cfg, COMPANY): dg += 1; print("   PPTX: OK")
    if generate_financial_xlsx(cfg, COMPANY): dg += 1; print("   XLSX: OK")
except Exception as e:
    print(f"   Error: {e}")
scores["Doc Generation"] = int(dg / 4 * 100)
print(f"   {dg}/4 formats | Score: {scores['Doc Generation']}/100")

# 7. DRAWINGS
print("\n7. DRAWINGS")
td = sum(len([f for f in os.listdir(d) if f.endswith(('.png','.jpg'))]) for d in ["data/all_drawings","data/cad_drawings","data/professional_drawings","data/ai_drawings","data/generated_drawings"] if os.path.exists(d))
scores["Drawings"] = min(100, int(td / 150 * 100))
print(f"   {td} drawing files | Score: {scores['Drawings']}/100")

# 8. APIs
print("\n8. FREE APIs")
ap = 0
try:
    from engines.free_apis import get_weather_current, get_exchange_rates, get_india_gdp, detect_visitor_location, get_india_holidays
    if "error" not in get_weather_current("Vadodara"): ap += 1
    if "error" not in get_exchange_rates(): ap += 1
    if get_india_gdp(3): ap += 1
    if detect_visitor_location().get("city"): ap += 1
    if get_india_holidays(): ap += 1
except: pass
scores["Free APIs"] = int(ap / 5 * 100)
print(f"   {ap}/5 working | Score: {scores['Free APIs']}/100")

# 9. AI ENGINE
print("\n9. AI ENGINE")
try:
    from engines.ai_engine import load_ai_config, is_ai_available
    scores["AI Engine"] = 80 if is_ai_available() else 60
    print(f"   Available: {is_ai_available()} | Score: {scores['AI Engine']}/100")
except:
    scores["AI Engine"] = 40

# 10. SELF-HEALING
print("\n10. SELF-HEALING")
try:
    from engines.self_healing_worker import run_health_cycle
    _, sc = run_health_cycle()
    scores["Self-Healing"] = sc
    print(f"   Health score: {sc}% | Score: {scores['Self-Healing']}/100")
except:
    scores["Self-Healing"] = 50

# 11. SIDEBAR
print("\n11. ORGANIZATION")
sp = len(glob.glob("pages/*.py"))
dp = len(glob.glob("pages/_detail/*.py"))
scores["Organization"] = 100 if sp <= 20 else 70
print(f"   Sidebar: {sp} | Detail: {dp} | Score: {scores['Organization']}/100")

# 12. CLIENT FLOW
print("\n12. CLIENT INFO FLOW")
sm = open("state_manager.py", encoding='utf-8').read()
cf = sum(1 for f in ["client_name","project_name","site_address","client_company"] if f in sm)
dgen = "client_name" in open("engines/dynamic_doc_generator.py",encoding='utf-8').read()
pgen = "client_name" in open("engines/report_generator_engine.py",encoding='utf-8').read()
scores["Client Flow"] = 100 if cf == 4 and dgen and pgen else 70
print(f"   Fields: {cf}/4 | DOCX: {dgen} | PDF: {pgen} | Score: {scores['Client Flow']}/100")

# 13. PRESENTER
print("\n13. PRESENTER")
pf = "pages/01_\U0001f3af_Presenter.py"
if os.path.exists(pf):
    pc = open(pf, encoding='utf-8').read()
    sl = len(re.findall(r'elif slide == \d+:|if slide == \d+:', pc))
    scores["Presenter"] = 100 if sl >= 14 else 80
    print(f"   Slides: {sl} | Score: {scores['Presenter']}/100")
else:
    scores["Presenter"] = 0

# 14. AGRO
print("\n14. AGRO ENGINE")
try:
    from engines.agro_engine import get_crop_list, get_quality_specs
    scores["Agro Engine"] = 100
    print(f"   Crops: {len(get_crop_list())} | Specs: {len(get_quality_specs())} | Score: 100/100")
except:
    scores["Agro Engine"] = 50

# ═══════════════════════════════════════════════════════════
# FINAL SCORE
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  DETAILED SCORECARD")
print("=" * 70)

weights = {"Syntax":10,"Config Link":8,"Database":8,"Config Data":8,"Calculations":12,
           "Doc Generation":10,"Drawings":6,"Free APIs":8,"AI Engine":6,"Self-Healing":6,
           "Organization":5,"Client Flow":8,"Presenter":5,"Agro Engine":5}

wt = 0; ws = 0
for cat in sorted(scores, key=lambda x: -scores[x]):
    s = scores[cat]
    w = weights.get(cat, 5)
    wt += s * w; ws += w
    bar = "\u2588" * (s // 5) + "\u2591" * (20 - s // 5)
    tag = "EXCELLENT" if s >= 90 else ("GOOD" if s >= 75 else ("FAIR" if s >= 60 else "WEAK"))
    print(f"   {cat:20s} {bar} {s:3d}/100  {tag}")

overall = int(wt / ws) if ws > 0 else 0

if overall >= 90: rating, label = "AAA+", "PRODUCTION READY"
elif overall >= 85: rating, label = "AAA", "EXCELLENT"
elif overall >= 80: rating, label = "AA+", "VERY GOOD"
elif overall >= 75: rating, label = "AA", "GOOD"
elif overall >= 65: rating, label = "A", "FAIR"
else: rating, label = "B", "NEEDS WORK"

print("\n" + "=" * 70)
print(f"  OVERALL SCORE: {overall}/100")
print(f"  RATING: {rating} — {label}")
print("=" * 70)
print(f"\n  Files: {len(all_py)} | Pages: {sp}+{dp} | Engines: {len(glob.glob('engines/*.py'))}")
print(f"  Tables: {tc} | Drawings: {td} | APIs: {ap}/5 | Slides: {sl}")
print(f"  Errors: {len(errors)} | Scenarios: {cp}/21 | Doc formats: {dg}/4")
print("=" * 70)
