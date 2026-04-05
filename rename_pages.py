"""
Rename all 52 page files to match the 7-section navigation structure.
Streamlit sorts sidebar by filename prefix — rename controls the order.

Sections:
  01-02: Quick Access (Presenter, Dashboard)
  10-14: Client Setup
  20-26: Technology
  30-39: Financial Model
  40-43: Compliance & Legal
  50-54: Drawings & Timeline
  60-64: Documents & Export
  70-83: Tools & Admin
"""
import os
import sys
import shutil

PAGES_DIR = os.path.join(os.path.dirname(__file__), "pages")

# Mapping: old filename → new filename
# Only the prefix number changes. Page name stays same.
RENAMES = {
    # ── QUICK ACCESS (01-02) — keep as-is ──
    "01_🎯_Presenter.py": "01_🎯_Presenter.py",
    "02_📊_Dashboard.py": "02_📊_Dashboard.py",

    # ── SECTION 1: CLIENT SETUP (10-14) ──
    "03_📝_Project_Setup.py": "10_📝_Project_Setup.py",
    "14_👥_Customers.py": "11_👥_Customers.py",
    "05_📍_Location.py": "12_📍_Location.py",
    "04_📈_Market.py": "13_📈_Market.py",
    "50_Client_Journey.py": "14_Client_Journey.py",

    # ── SECTION 2: TECHNOLOGY (20-26) ──
    "51_Technology.py": "20_Technology.py",
    "57_Three_Process.py": "21_Three_Process.py",
    "53_Process_Flow.py": "22_Process_Flow.py",
    "07_⚙️_Plant_Design.py": "23_⚙️_Plant_Design.py",
    "06_🌾_Raw_Material.py": "24_🌾_Raw_Material.py",
    "55_Lab_Testing.py": "25_Lab_Testing.py",
    "52_Product_Grades.py": "26_Product_Grades.py",

    # ── SECTION 3: FINANCIAL MODEL (30-39) ──
    "09_💰_Financial.py": "30_💰_Financial.py",
    "75_Detailed_Costing.py": "31_Detailed_Costing.py",
    "76_Working_Capital.py": "32_Working_Capital.py",
    "61_Loan_EMI.py": "33_Loan_EMI.py",
    "78_Cash_Flow_5Year.py": "34_Cash_Flow_5Year.py",
    "77_Break_Even.py": "35_Break_Even.py",
    "60_ROI_Quick_Calc.py": "36_ROI_Quick_Calc.py",
    "62_Capacity_Compare.py": "37_Capacity_Compare.py",
    "59_Sensitivity.py": "38_Sensitivity.py",
    "58_State_Profitability.py": "39_State_Profitability.py",

    # ── SECTION 4: COMPLIANCE & LEGAL (40-43) ──
    "11_📋_Compliance.py": "40_📋_Compliance.py",
    "65_Environmental.py": "41_Environmental.py",
    "66_Risk_Matrix.py": "42_Risk_Matrix.py",
    "12_🛣️_NHAI_Tenders.py": "43_🛣️_NHAI_Tenders.py",

    # ── SECTION 5: DRAWINGS & TIMELINE (50-54) ──
    "08_📐_Drawings.py": "50_📐_Drawings.py",
    "56_AI_Drawings.py": "51_AI_Drawings.py",
    "73_AI_Plant_Layouts.py": "52_AI_Plant_Layouts.py",
    "54_Timeline.py": "53_Timeline.py",
    "64_Project_Gantt.py": "54_Project_Gantt.py",

    # ── SECTION 6: DOCUMENTS & EXPORT (60-64) ──
    "44_DPR_Generator.py": "60_DPR_Generator.py",
    "13_📁_Document_Hub.py": "61_📁_Document_Hub.py",
    "67_Export_Center.py": "62_Export_Center.py",
    "42_Packages.py": "63_Packages.py",
    "43_Send.py": "64_Send.py",

    # ── SECTION 7: TOOLS & ADMIN (70-83) ──
    "40_Buyers.py": "70_Buyers.py",
    "10_🏭_Procurement.py": "71_🏭_Procurement.py",
    "63_Competitor_Intel.py": "72_Competitor_Intel.py",
    "45_Analytics.py": "73_Analytics.py",
    "68_News_Feed.py": "74_News_Feed.py",
    "71_Weather_Site.py": "75_Weather_Site.py",
    "70_Meeting_Planner.py": "76_Meeting_Planner.py",
    "41_Files.py": "77_Files.py",
    "69_Training.py": "78_Training.py",
    "72_System_Calculations.py": "79_System_Calculations.py",
    "74_Advanced_Tools.py": "80_Advanced_Tools.py",
    "15_🤖_AI_Advisor.py": "81_🤖_AI_Advisor.py",
    "16_🏥_System_Health.py": "82_🏥_System_Health.py",
    "17_🔑_AI_Settings.py": "83_🔑_AI_Settings.py",
}


def main():
    sys.stdout.reconfigure(encoding='utf-8')

    # Verify all source files exist
    missing = []
    for old_name in RENAMES:
        old_path = os.path.join(PAGES_DIR, old_name)
        if not os.path.exists(old_path):
            missing.append(old_name)

    if missing:
        print(f"ERROR: {len(missing)} source files not found:")
        for m in missing:
            print(f"  MISSING: {m}")
        print("Aborting.")
        return

    # Check for conflicts (new name already exists as a different file)
    # Use two-phase rename: old → temp, then temp → new
    temp_dir = os.path.join(PAGES_DIR, "__temp_rename__")
    os.makedirs(temp_dir, exist_ok=True)

    # Phase 1: Move all to temp
    print("Phase 1: Moving to temp...")
    for old_name in RENAMES:
        old_path = os.path.join(PAGES_DIR, old_name)
        temp_path = os.path.join(temp_dir, old_name)
        shutil.move(old_path, temp_path)

    # Phase 2: Move from temp to new names
    print("Phase 2: Renaming...")
    renamed = 0
    kept = 0
    for old_name, new_name in RENAMES.items():
        temp_path = os.path.join(temp_dir, old_name)
        new_path = os.path.join(PAGES_DIR, new_name)
        shutil.move(temp_path, new_path)
        if old_name != new_name:
            print(f"  {old_name} → {new_name}")
            renamed += 1
        else:
            kept += 1

    # Cleanup temp dir
    os.rmdir(temp_dir)

    # Clean up __pycache__
    cache_dir = os.path.join(PAGES_DIR, "__pycache__")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("  Cleared __pycache__")

    print(f"\nDone: {renamed} renamed, {kept} kept same. Total: {renamed + kept} files.")


if __name__ == "__main__":
    main()
