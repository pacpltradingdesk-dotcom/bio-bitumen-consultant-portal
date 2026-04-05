"""Add contextual AI skill to every page that doesn't have one."""
import os

PAGE_AI = {
    "02_📊_Dashboard.py": "Executive Summary",
    "03_📝_Project_Setup.py": "Smart Suggestions",
    "04_📈_Market.py": "Market Analysis",
    "05_📍_Location.py": "Site Selection Advice",
    "06_🌾_Raw_Material.py": "Biomass Sourcing Plan",
    "07_⚙️_Plant_Design.py": "Equipment Recommendations",
    "08_📐_Drawings.py": "Drawing Checklist",
    "12_🛣️_NHAI_Tenders.py": "Tender Strategy",
    "14_👥_Customers.py": "Client Outreach Email",
    "40_Buyers.py": "Buyer Pitch Script",
    "44_DPR_Generator.py": "DPR Section Writer",
    "45_Analytics.py": "Business Insights",
    "51_Technology.py": "Technology Explainer",
    "53_Process_Flow.py": "Process Optimization",
    "54_Timeline.py": "Timeline Risk Analysis",
    "57_Three_Process.py": "Process Comparison",
    "58_State_Profitability.py": "State Investment Brief",
    "59_Sensitivity.py": "Risk Narrative",
    "60_ROI_Quick_Calc.py": "ROI Explanation",
    "61_Loan_EMI.py": "Bank Pitch Points",
    "62_Capacity_Compare.py": "Capacity Recommendation",
    "63_Competitor_Intel.py": "Competitive Positioning",
    "64_Project_Gantt.py": "Milestone Brief",
    "65_Environmental.py": "ESG Report Section",
    "66_Risk_Matrix.py": "Risk Mitigation Plan",
    "67_Export_Center.py": "Export Summary",
    "68_News_Feed.py": "Industry Brief",
    "69_Training.py": "Training Schedule",
    "70_Meeting_Planner.py": "Meeting Agenda",
    "71_Weather_Site.py": "Construction Calendar",
}

added = 0
for filename, skill_name in PAGE_AI.items():
    filepath = f"pages/{filename}"
    if not os.path.exists(filepath):
        continue
    content = open(filepath, encoding='utf-8').read()
    if 'ai_engine' in content or 'ai_skills' in content:
        print(f"  SKIP (already has AI): {filename}")
        continue

    # Build unique key
    page_key = filename[:8].replace('_','').replace('.','')

    block = f'''

# ── AI Skill: {skill_name} ──────────────────────────────────────
st.markdown("---")
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("🤖 AI: {skill_name}"):
            if st.button("Generate", type="primary", key="ai_{page_key}"):
                with st.spinner("AI working..."):
                    _p = f"As a senior bio-bitumen consultant, generate: {skill_name}. "
                    _p += f"Plant: {{cfg.get('capacity_tpd',20):.0f}} TPD, Investment: Rs {{cfg.get('investment_cr',8):.2f}} Cr, "
                    _p += f"Location: {{cfg.get('location','')}}, {{cfg.get('state','')}}. "
                    _p += "Be specific with numbers. Professional format."
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 1000)
                if _r:
                    st.markdown(_r)
except Exception:
    pass
'''

    content += block
    open(filepath, 'w', encoding='utf-8').write(content)
    added += 1
    print(f"  Added: {filename} → {skill_name}")

print(f"\nTotal: {added} pages updated")
