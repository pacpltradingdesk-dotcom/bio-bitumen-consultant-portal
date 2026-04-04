"""Audit every document output for quality and completeness."""
import sys,os,re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['STREAMLIT_SERVER_HEADLESS']='true'

from state_manager import _full_default, calculate_boq, format_inr, format_inr_lac
from config import COMPANY

cfg = _full_default()
cfg.update({"capacity_tpd":20,"investment_cr":6.4,"roi_pct":44.4,"irr_pct":67,"dscr_yr3":3.47,
    "break_even_months":30,"monthly_profit_lac":23.7,"revenue_yr5_lac":821,"equity_ratio":0.4,
    "loan_cr":3.84,"equity_cr":2.56,"emi_lac_mth":6.68,"profit_per_mt":25744,"interest_rate":0.115,
    "selling_price_per_mt":35000,"total_variable_cost_per_mt":14506,"staff":18,"power_kw":100,
    "working_days":300,"state":"Gujarat","location":"Vadodara","product_model":"bitumen",
    "client_name":"Raj Industries Pvt Ltd","client_company":"Raj Bio-Bitumen Manufacturing LLP",
    "project_name":"Bio-Modified Bitumen Plant - Vadodara","break_even_month":30,
    "biochar_price_per_mt":4000,"total_revenue_per_mt":40250,"biomass_mt_day":50,
    "biomass_cost_per_mt":2000,"site_address":"Plot 45, GIDC Industrial Estate, Makarpura, Vadodara",
    "site_pincode":"390010","project_id":"PPS/2026/BIO-001","site_area_acres":3,
    "site_ownership":"GIDC Allotment","oil_ltr_day":3200,"char_kg_day":6000,"payroll_lac_yr":45,
    "investment_lac":640,"biomass_source":"Rice Straw","client_phone":"+91 98765 43210",
    "sensitivity_matrix":[[150,280,410],[200,330,460],[250,380,510]]})
cfg["roi_timeline"] = [
    {"Year":yr,"Utilization":f"{u:.0%}","Production (MT)":round(2400*u),
     "Revenue (Lac)":round(2400*u*40250/1e5,2),"Variable Cost (Lac)":round(2400*u*14506/1e5,2),
     "Fixed Cost (Lac)":38.4,"EBITDA (Lac)":round(2400*u*(40250-14506)/1e5-38.4,2),
     "Depreciation (Lac)":64,"Interest (Lac)":44.16,
     "PBT (Lac)":round(2400*u*(40250-14506)/1e5-38.4-64-44.16,2),
     "Tax (Lac)":round(max(0,(2400*u*(40250-14506)/1e5-38.4-64-44.16)*0.25),2),
     "PAT (Lac)":round((2400*u*(40250-14506)/1e5-38.4-64-44.16)*0.75,2),
     "Cash Accrual (Lac)":round((2400*u*(40250-14506)/1e5-38.4-64-44.16)*0.75+64,2),
     "DSCR":round(((2400*u*(40250-14506)/1e5-38.4-64-44.16)*0.75+64)/(6.68*12),2)}
    for yr,u in [(1,.4),(2,.55),(3,.7),(4,.8),(5,.85),(6,.9),(7,.9)]
]
cfg["plant_data"]={"civil_lac":40,"mach_lac":350,"gst_mach_lac":63,"wc_lac":50,"idc_lac":22,"preop_lac":15,"cont_lac":10,"sec_lac":10}
cfg["monthly_pnl"]={"Revenue":68.4,"Variable Cost":-15,"Fixed Cost":-3.2,"EBITDA":50.2,"EMI":6.68,"Net":23.7}

OUT="data/test_outputs"
os.makedirs(OUT, exist_ok=True)
total=0; passed=0; issues=[]

def test(name, ok, detail=""):
    global total, passed
    total+=1
    if ok: passed+=1; print(f"  PASS: {name}")
    else: issues.append(f"{name}: {detail}"); print(f"  FAIL: {name} - {detail}")

print("="*70)
print("  OUTPUT QUALITY AUDIT")
print("="*70)

# 1. DOCX DPR
print("\n[1] DOCX DPR")
try:
    from engines.dynamic_doc_generator import generate_dpr_docx
    doc = generate_dpr_docx(cfg, COMPANY)
    p1=f"{OUT}/Q_DPR.docx"; doc.save(p1); sz=os.path.getsize(p1)
    txt="\n".join([p.text for p in doc.paragraphs])
    test(f"Size {sz//1024}KB", sz>15000, f"{sz} bytes")
    test("Client: Raj Industries", "Raj Industries" in txt, "missing")
    test("Company: Raj Bio-Bitumen", "Raj Bio-Bitumen" in txt, "missing")
    test("Site: GIDC", "GIDC" in txt, "missing")
    test("Pincode: 390010", "390010" in txt, "missing")
    test("Project ID", "PPS/2026" in txt, "missing")
    test("Consultant: PPS Anantams", "PPS Anantams" in txt, "missing")
    test("CONFIDENTIAL", "CONFIDENTIAL" in txt, "missing")
    sects=["EXECUTIVE SUMMARY","MARKET","TECHNICAL","INVESTMENT","FINANCIAL","COST","RISK",
           "LICENSE","BILL OF QUANTITIES","RAW MATERIAL SOURCING","ENVIRONMENTAL","GOVERNMENT SUBSIDIES",
           "IMPLEMENTATION TIMELINE","MANPOWER","SENSITIVITY","CONSULTANT PROFILE"]
    found=sum(1 for s in sects if s in txt)
    test(f"Sections {found}/{len(sects)}", found>=14, f"only {found}")
    pgs=len(doc.paragraphs)//15
    test(f"~{pgs} pages ({len(doc.paragraphs)} paras)", pgs>=10, f"only ~{pgs}")
except Exception as e:
    test("DOCX DPR", False, str(e))

# 2. DOCX Bank
print("\n[2] DOCX BANK PROPOSAL")
try:
    from engines.dynamic_doc_generator import generate_bank_proposal_docx
    doc=generate_bank_proposal_docx(cfg,COMPANY,{"name":"Raj Industries","company":"Raj LLP"})
    p2=f"{OUT}/Q_Bank.docx"; doc.save(p2); sz=os.path.getsize(p2)
    txt="\n".join([p.text for p in doc.paragraphs])
    test(f"Size {sz//1024}KB", sz>8000)
    test("Has loan amount", "3.84" in txt, "missing")
    test("Has EMI", "6.68" in txt, "missing")
    test("Has consultant", "PPS Anantams" in txt, "missing")
except Exception as e:
    test("DOCX Bank", False, str(e))

# 3. PPTX
print("\n[3] PPTX INVESTOR PITCH")
try:
    from engines.dynamic_doc_generator import generate_investor_pptx
    pptx=generate_investor_pptx(cfg,COMPANY)
    p3=f"{OUT}/Q_Pitch.pptx"; pptx.save(p3)
    test(f"Size {os.path.getsize(p3)//1024}KB", os.path.getsize(p3)>5000)
    test(f"Slides: {len(pptx.slides)}", len(pptx.slides)>=6)
except Exception as e:
    test("PPTX", False, str(e))

# 4. XLSX
print("\n[4] XLSX FINANCIAL")
try:
    from engines.dynamic_doc_generator import generate_financial_xlsx
    wb=generate_financial_xlsx(cfg,COMPANY)
    p4=f"{OUT}/Q_Financial.xlsx"; wb.save(p4)
    test(f"Size {os.path.getsize(p4)//1024}KB", os.path.getsize(p4)>3000)
    test(f"Sheets: {len(wb.sheetnames)}", len(wb.sheetnames)>=3)
except Exception as e:
    test("XLSX", False, str(e))

# 5. PDF
print("\n[5] PDF DPR")
try:
    from engines.report_generator_engine import generate_dpr_pdf
    p5=f"{OUT}/Q_DPR.pdf"; generate_dpr_pdf(p5,cfg,COMPANY)
    sz=os.path.getsize(p5)
    test(f"Size {sz//1024}KB", sz>3000)
    with open(p5,'rb') as f: test("Valid PDF header", f.read(5)==b'%PDF-')
except Exception as e:
    test("PDF", False, str(e))

# 6. PDF Quotation
print("\n[6] PDF QUOTATION")
try:
    from engines.pdf_quotation_engine import generate_quotation_pdf
    from interpolation_engine import get_all_known_plants
    import pandas as pd
    plants=get_all_known_plants(); plant=plants.get("20MT",{})
    cust={"name":"Raj Industries","company":"Raj LLP","city":"Vadodara","state":"Gujarat"}
    roi_df=pd.DataFrame(cfg["roi_timeline"])
    p6=f"{OUT}/Q_Quote.pdf"; generate_quotation_pdf(p6,cust,plant,roi_df=roi_df,company=COMPANY)
    test(f"Size {os.path.getsize(p6)//1024}KB", os.path.getsize(p6)>2000)
except Exception as e:
    test("Quotation", False, str(e))

# 7. Drawings
print("\n[7] DRAWINGS")
dd="data/all_drawings"
if os.path.exists(dd):
    files=[f for f in os.listdir(dd) if f.endswith('.png')]
    caps=set(re.search(r'(\d+)TPD',f).group(1) for f in files if re.search(r'(\d+)TPD',f))
    types=set()
    for t in ["Layout","PFD","SLD","Fire","Civil","ETP","Tank","Piping","Earthing","Water","CAD","Machinery"]:
        if any(t in f for f in files): types.add(t)
    test(f"Total: {len(files)}", len(files)>=100)
    test(f"Capacities: {len(caps)} ({sorted(caps)})", len(caps)>=7)
    test(f"Types: {len(types)} ({sorted(types)})", len(types)>=8)

# 8. BOQ
print("\n[8] BOQ")
boq=calculate_boq(20); tot=sum(i['amount_lac'] for i in boq)
test(f"Items: {len(boq)}", len(boq)>=15)
test(f"Total: {format_inr_lac(tot)}", tot>100)

# 9. Format
print("\n[9] INR FORMAT")
test("500 -> Rs 500", format_inr(500)=="Rs 500" or "500" in format_inr(500))
test("Lac format", "Lac" in format_inr_lac(6.4))
test("Cr format", "Cr" in format_inr_lac(640))

print("\n"+"="*70)
print(f"  RESULT: {passed}/{total} PASSED | {total-passed} FAILED")
print("="*70)
if issues:
    for i in issues: print(f"    X {i}")
else:
    print("  ALL OUTPUTS PROFESSIONAL QUALITY - ZERO ISSUES")
print("\n  FILES:")
for f in sorted(os.listdir(OUT)):
    if f.startswith("Q_"):
        print(f"    [{f.split('.')[-1].upper():4s}] {f}: {os.path.getsize(os.path.join(OUT,f))//1024} KB")
print("="*70)
