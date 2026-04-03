"""Test all document format generation — DOCX, PPTX, XLSX, PDF, PNG, ZIP"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

from state_manager import _full_default
from config import COMPANY

# Build test config with all required fields
cfg = _full_default()
cfg['capacity_tpd'] = 20.0
cfg['working_days'] = 300
cfg['investment_cr'] = 6.40
cfg['investment_lac'] = 640
cfg['loan_cr'] = 3.84
cfg['equity_cr'] = 2.56
cfg['emi_lac_mth'] = 6.68
cfg['annual_production_mt'] = 2400
cfg['revenue_yr1_lac'] = 386
cfg['revenue_yr5_lac'] = 821
cfg['revenue_yr1_cr'] = 3.86
cfg['revenue_yr5_cr'] = 8.21
cfg['profit_per_mt'] = 25744
cfg['monthly_profit_lac'] = 23.7
cfg['roi_pct'] = 44.4
cfg['irr_pct'] = 67.0
cfg['dscr_yr3'] = 3.47
cfg['break_even_months'] = 30
cfg['break_even_month'] = 30
cfg['staff'] = 18
cfg['power_kw'] = 100
cfg['biomass_mt_day'] = 50
cfg['oil_ltr_day'] = 3200
cfg['char_kg_day'] = 6000
cfg['payroll_lac_yr'] = 45
cfg['selling_price_per_mt'] = 35000
cfg['biochar_price_per_mt'] = 4000
cfg['total_variable_cost_per_mt'] = 14506
cfg['total_revenue_per_mt'] = 40250
cfg['interest_rate'] = 0.115
cfg['equity_ratio'] = 0.40
cfg['state'] = 'Gujarat'
cfg['location'] = 'Vadodara'
cfg['biomass_cost_per_mt'] = 2000

# 7-year timeline
timeline = []
for yr, u in [(1,0.4),(2,0.55),(3,0.7),(4,0.8),(5,0.85),(6,0.9),(7,0.9)]:
    rev = round(2400*u*40250/1e5, 2)
    var = round(2400*u*14506/1e5, 2)
    fixed = 38.4
    ebitda = round(rev - var - fixed, 2)
    depr = 64
    interest = 44.16
    pbt = round(ebitda - depr - interest, 2)
    tax = round(max(0, pbt*0.25), 2)
    pat = round(pbt - tax, 2)
    cash = round(pat + depr, 2)
    dscr = round(cash/(6.68*12), 2)
    timeline.append({
        'Year': yr, 'Utilization': f'{u:.0%}', 'Production (MT)': round(2400*u),
        'Revenue (Lac)': rev, 'Variable Cost (Lac)': var, 'Fixed Cost (Lac)': fixed,
        'EBITDA (Lac)': ebitda, 'Depreciation (Lac)': depr, 'Interest (Lac)': interest,
        'PBT (Lac)': pbt, 'Tax (Lac)': tax, 'PAT (Lac)': pat,
        'Cash Accrual (Lac)': cash, 'DSCR': dscr
    })
cfg['roi_timeline'] = timeline
cfg['sensitivity_matrix'] = [[150,280,410],[200,330,460],[250,380,510]]
cfg['monthly_pnl'] = {'Revenue': 68.4, 'Raw Material': -15.0, 'Power': -8.0,
                       'Labour': -4.0, 'Other Costs': -5.0, 'Net Profit': 23.7}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'data', 'test_outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)
errors = []

print(f"Config: {cfg['capacity_tpd']}TPD, Inv={cfg['investment_cr']}Cr, ROI={cfg['roi_pct']}%")
print(f"Timeline: {len(cfg['roi_timeline'])} years")
print()

# 1. DOCX DPR
print("1. DOCX (DPR)...")
try:
    from engines.dynamic_doc_generator import generate_dpr_docx
    doc = generate_dpr_docx(cfg, COMPANY)
    path = os.path.join(OUTPUT_DIR, "DPR_20TPD.docx")
    doc.save(path)
    print(f"   OK - {os.path.getsize(path)/1024:.1f} KB")
except Exception as e:
    errors.append(f"DOCX DPR: {e}")
    print(f"   FAIL: {e}")

# 2. DOCX Bank
print("2. DOCX (Bank Proposal)...")
try:
    from engines.dynamic_doc_generator import generate_bank_proposal_docx
    doc = generate_bank_proposal_docx(cfg, COMPANY)
    path = os.path.join(OUTPUT_DIR, "Bank_Proposal_20TPD.docx")
    doc.save(path)
    print(f"   OK - {os.path.getsize(path)/1024:.1f} KB")
except Exception as e:
    errors.append(f"DOCX Bank: {e}")
    print(f"   FAIL: {e}")

# 3. PPTX
print("3. PPTX (Investor Pitch)...")
try:
    from engines.dynamic_doc_generator import generate_investor_pptx
    pptx = generate_investor_pptx(cfg, COMPANY)
    path = os.path.join(OUTPUT_DIR, "Investor_Pitch_20TPD.pptx")
    pptx.save(path)
    print(f"   OK - {os.path.getsize(path)/1024:.1f} KB")
except Exception as e:
    errors.append(f"PPTX: {e}")
    print(f"   FAIL: {e}")

# 4. XLSX
print("4. XLSX (Financial Model)...")
try:
    from engines.dynamic_doc_generator import generate_financial_xlsx
    wb = generate_financial_xlsx(cfg, COMPANY)
    path = os.path.join(OUTPUT_DIR, "Financial_Model_20TPD.xlsx")
    wb.save(path)
    print(f"   OK - {os.path.getsize(path)/1024:.1f} KB")
except Exception as e:
    errors.append(f"XLSX: {e}")
    print(f"   FAIL: {e}")

# 5. PDF DPR
print("5. PDF (DPR Report)...")
try:
    from engines.report_generator_engine import generate_dpr_pdf
    pdf_path = os.path.join(OUTPUT_DIR, "DPR_20TPD.pdf")
    generate_dpr_pdf(pdf_path, cfg, COMPANY)
    if os.path.exists(pdf_path):
        print(f"   OK - {os.path.getsize(pdf_path)/1024:.1f} KB")
    else:
        errors.append("PDF DPR: file not created")
        print("   FAIL: file not created")
except Exception as e:
    errors.append(f"PDF DPR: {e}")
    print(f"   FAIL: {e}")

# 6. PDF Quotation
print("6. PDF (Quotation)...")
try:
    from engines.pdf_quotation_engine import generate_quotation_pdf
    pdf_path = os.path.join(OUTPUT_DIR, "Quotation_20TPD.pdf")
    customer_data = {"name": "Test Customer", "company": "Test Corp", "phone": "+91 9999999999"}
    # Use interpolation engine to get proper plant data
    try:
        from interpolation_engine import get_all_known_plants
        all_plants = get_all_known_plants()
        plant_data = all_plants.get("20MT", {})
    except Exception:
        plant_data = {
            "capacity": "20MT", "inv_cr": 6.4, "loan_cr": 3.84, "equity_cr": 2.56,
            "rev_yr1_cr": 3.86, "rev_yr5_cr": 8.21, "emi_lac_mth": 6.68,
            "dscr_yr3": 3.47, "irr_pct": 67.0, "staff": 18,
            "oil_ltr_day": 3200, "char_kg_day": 6000, "power_kw": 100,
            "biomass_mt_day": 50, "biomass_mt_yr": 15000,
            "civil_lac": 120, "mach_lac": 350, "gst_mach_lac": 63,
            "wc_lac": 50, "idc_lac": 22, "preop_lac": 15, "cont_lac": 10, "sec_lac": 10,
        }
    import pandas as _pd
    roi_df = _pd.DataFrame(cfg.get("roi_timeline", [])) if cfg.get("roi_timeline") else None
    generate_quotation_pdf(pdf_path, customer_data, plant_data,
                            roi_df=roi_df, company=COMPANY)
    if os.path.exists(pdf_path):
        print(f"   OK - {os.path.getsize(pdf_path)/1024:.1f} KB")
    else:
        errors.append("PDF Quote: file not created")
        print("   FAIL: file not created")
except Exception as e:
    errors.append(f"PDF Quote: {e}")
    print(f"   FAIL: {e}")

# 7. PNG Drawings
print("7. PNG (Engineering Drawings)...")
try:
    from engines.drawing_generator import generate_all_drawings
    result = generate_all_drawings(20)
    draw_dir = os.path.join(os.path.dirname(__file__), 'data', 'all_drawings')
    pngs = [f for f in os.listdir(draw_dir) if '20TPD' in f and f.endswith('.png')] if os.path.exists(draw_dir) else []
    print(f"   OK - {len(pngs)} drawings for 20TPD")
    for p in pngs[:3]:
        size = os.path.getsize(os.path.join(draw_dir, p))
        print(f"      {p}: {size/1024:.1f} KB")
except Exception as e:
    errors.append(f"PNG: {e}")
    print(f"   FAIL: {e}")

# 8. ZIP Package
print("8. ZIP (Complete Package)...")
try:
    import zipfile, io
    zip_buf = io.BytesIO()
    file_count = 0
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in os.listdir(OUTPUT_DIR):
            fpath = os.path.join(OUTPUT_DIR, f)
            if os.path.isfile(fpath) and not f.endswith('.zip'):
                with open(fpath, 'rb') as fh:
                    zf.writestr(f, fh.read())
                file_count += 1
    zip_buf.seek(0)
    path = os.path.join(OUTPUT_DIR, "Complete_Package_20TPD.zip")
    with open(path, 'wb') as f:
        f.write(zip_buf.getvalue())
    print(f"   OK - {os.path.getsize(path)/1024:.1f} KB ({file_count} files)")
except Exception as e:
    errors.append(f"ZIP: {e}")
    print(f"   FAIL: {e}")

# RESULTS
print()
print(f"{'='*60}")
print(f"RESULT: {8-len(errors)}/8 formats PASSED, {len(errors)} FAILED")
print(f"{'='*60}")
for e in errors:
    print(f"  ERROR: {e}")
if not errors:
    print("  ALL 8 FORMATS WORKING PERFECTLY!")

print()
print("OUTPUT FILES:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, f)
    if os.path.isfile(fpath):
        ext = f.rsplit('.', 1)[-1].upper()
        size = os.path.getsize(fpath) / 1024
        print(f"  [{ext:4s}] {f}: {size:.1f} KB")
