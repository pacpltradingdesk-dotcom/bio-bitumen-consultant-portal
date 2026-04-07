"""
Page Navigation Engine — Adds 'Next Step' links to every page
================================================================
Defines the logical flow between pages so users never get stuck.
"""

# Logical flow: what comes after each page
NEXT_STEPS = {
    # Section 1: Client Setup
    "10": [("pages/11_👥_Customers.py", "Save Customer", "👥"),
           ("pages/12_📍_Location.py", "Location Analysis", "📍")],
    "11": [("pages/12_📍_Location.py", "Location Analysis", "📍"),
           ("pages/64_Send.py", "Send Documents", "📧")],
    "12": [("pages/13_📈_Market.py", "Market Intelligence", "📈"),
           ("pages/39_State_Profitability.py", "State Profitability", "📊")],
    "13": [("pages/20_Technology.py", "Technology Details", "🔬"),
           ("pages/43_🛣️_NHAI_Tenders.py", "NHAI Tenders", "🛣️")],
    "14": [("pages/10_📝_Project_Setup.py", "Project Setup", "📝"),
           ("pages/30_💰_Financial.py", "Financial Model", "💰")],

    # Section 2: Technology
    "20": [("pages/21_Three_Process.py", "Compare 3 Processes", "🔄"),
           ("pages/22_Process_Flow.py", "Process Flow", "⚙️")],
    "21": [("pages/22_Process_Flow.py", "Process Flow", "⚙️"),
           ("pages/30_💰_Financial.py", "Financial Model", "💰")],
    "22": [("pages/23_⚙️_Plant_Design.py", "Plant Design & BOQ", "⚙️"),
           ("pages/50_📐_Drawings.py", "Engineering Drawings", "📐")],
    "23": [("pages/50_📐_Drawings.py", "Engineering Drawings", "📐"),
           ("pages/29_Investment_Optimizer.py", "Investment Optimizer", "💡")],
    "24": [("pages/22_Process_Flow.py", "Process Flow", "⚙️"),
           ("pages/31_Detailed_Costing.py", "Detailed Costing", "📊")],
    "25": [("pages/26_Product_Grades.py", "Product Grades", "📋"),
           ("pages/40_📋_Compliance.py", "Compliance", "📋")],
    "26": [("pages/70_Buyers.py", "Buyer Network", "🤝"),
           ("pages/30_💰_Financial.py", "Financial Model", "💰")],

    # Section 3: Financial
    "29": [("pages/30_💰_Financial.py", "Financial Model", "💰"),
           ("pages/23_⚙️_Plant_Design.py", "Plant Design", "⚙️")],
    "30": [("pages/31_Detailed_Costing.py", "DPR Costing", "📊"),
           ("pages/36_ROI_Quick_Calc.py", "ROI Calculator", "🎯")],
    "31": [("pages/32_Working_Capital.py", "Working Capital", "💳"),
           ("pages/35_Break_Even.py", "Break-Even", "⚖️")],
    "32": [("pages/33_Loan_EMI.py", "Loan EMI", "🏦"),
           ("pages/34_Cash_Flow_5Year.py", "5-Year Cash Flow", "📉")],
    "33": [("pages/34_Cash_Flow_5Year.py", "Cash Flow 5-Year", "📉"),
           ("pages/38_Sensitivity.py", "Sensitivity", "🔬")],
    "34": [("pages/35_Break_Even.py", "Break-Even", "⚖️"),
           ("pages/38_Sensitivity.py", "Sensitivity", "🔬")],
    "35": [("pages/38_Sensitivity.py", "Sensitivity Analysis", "🔬"),
           ("pages/60_DPR_Generator.py", "Generate DPR", "📄")],
    "36": [("pages/37_Capacity_Compare.py", "Compare Capacities", "⚖️"),
           ("pages/30_💰_Financial.py", "Full Financial Model", "💰")],
    "37": [("pages/39_State_Profitability.py", "State Profitability", "📊"),
           ("pages/29_Investment_Optimizer.py", "Optimize Investment", "💡")],
    "38": [("pages/39_State_Profitability.py", "State Profitability", "📊"),
           ("pages/60_DPR_Generator.py", "Generate DPR", "📄")],
    "39": [("pages/12_📍_Location.py", "Location Analysis", "📍"),
           ("pages/60_DPR_Generator.py", "Generate DPR", "📄")],

    # Section 4: Compliance
    "40": [("pages/41_Environmental.py", "Environmental", "🌱"),
           ("pages/53_Timeline.py", "Timeline", "📅")],
    "41": [("pages/42_Risk_Matrix.py", "Risk Matrix", "⚠️"),
           ("pages/43_🛣️_NHAI_Tenders.py", "NHAI Tenders", "🛣️")],
    "42": [("pages/43_🛣️_NHAI_Tenders.py", "NHAI Tenders", "🛣️"),
           ("pages/60_DPR_Generator.py", "Generate DPR", "📄")],
    "43": [("pages/70_Buyers.py", "Buyer Network", "🤝"),
           ("pages/63_Packages.py", "Build Package", "📦")],

    # Section 5: Drawings
    "50": [("pages/51_AI_Drawings.py", "AI Drawings", "🎨"),
           ("pages/52_AI_Plant_Layouts.py", "AI Plant Layouts", "🏗️")],
    "51": [("pages/52_AI_Plant_Layouts.py", "AI Plant Layouts", "🏗️"),
           ("pages/61_📁_Document_Hub.py", "Document Hub", "📁")],
    "52": [("pages/50_📐_Drawings.py", "Engineering Drawings", "📐"),
           ("pages/60_DPR_Generator.py", "Generate DPR", "📄")],
    "53": [("pages/54_Project_Gantt.py", "Project Gantt", "📅"),
           ("pages/40_📋_Compliance.py", "Compliance", "📋")],
    "54": [("pages/53_Timeline.py", "Timeline", "📅"),
           ("pages/76_Meeting_Planner.py", "Meeting Planner", "📋")],

    # Section 6: Documents
    "60": [("pages/61_📁_Document_Hub.py", "Document Hub", "📁"),
           ("pages/62_Export_Center.py", "Export Center", "📤")],
    "61": [("pages/62_Export_Center.py", "Export Center", "📤"),
           ("pages/63_Packages.py", "Build Package", "📦")],
    "62": [("pages/63_Packages.py", "Build Package", "📦"),
           ("pages/64_Send.py", "Send to Client", "📧")],
    "63": [("pages/64_Send.py", "Send to Client", "📧"),
           ("pages/62_Export_Center.py", "Export Center", "📤")],
    "64": [("pages/11_👥_Customers.py", "Customer Manager", "👥"),
           ("pages/76_Meeting_Planner.py", "Meeting Planner", "📋")],

    # Section 7: Tools
    "70": [("pages/71_🏭_Procurement.py", "Procurement", "🏭"),
           ("pages/43_🛣️_NHAI_Tenders.py", "NHAI Tenders", "🛣️")],
    "71": [("pages/23_⚙️_Plant_Design.py", "Plant Design", "⚙️"),
           ("pages/70_Buyers.py", "Buyers", "🤝")],
    "72": [("pages/70_Buyers.py", "Buyer Network", "🤝"),
           ("pages/13_📈_Market.py", "Market Intelligence", "📈")],
    "73": [("pages/11_👥_Customers.py", "Customers", "👥"),
           ("pages/64_Send.py", "Send", "📧")],
    "74": [("pages/13_📈_Market.py", "Market Intelligence", "📈"),
           ("pages/43_🛣️_NHAI_Tenders.py", "NHAI Tenders", "🛣️")],
    "75": [("pages/12_📍_Location.py", "Location Analysis", "📍"),
           ("pages/24_🌾_Raw_Material.py", "Raw Material", "🌾")],
    "76": [("pages/64_Send.py", "Send to Client", "📧"),
           ("pages/54_Project_Gantt.py", "Project Gantt", "📅")],
    "77": [("pages/61_📁_Document_Hub.py", "Document Hub", "📁"),
           ("pages/63_Packages.py", "Build Package", "📦")],
    "78": [("pages/81_🤖_AI_Advisor.py", "AI Advisor", "🤖"),
           ("pages/82_🏥_System_Health.py", "System Health", "🏥")],
    "79": [("pages/30_💰_Financial.py", "Financial Model", "💰"),
           ("pages/82_🏥_System_Health.py", "System Health", "🏥")],
    "80": [("pages/60_DPR_Generator.py", "DPR Generator", "📄"),
           ("pages/83_🔑_AI_Settings.py", "AI Settings", "🔑")],
    "81": [("pages/30_💰_Financial.py", "Financial Model", "💰"),
           ("pages/60_DPR_Generator.py", "DPR Generator", "📄")],
    "82": [("pages/83_🔑_AI_Settings.py", "AI Settings", "🔑"),
           ("pages/79_System_Calculations.py", "System Formulas", "🔧")],
    "83": [("pages/81_🤖_AI_Advisor.py", "AI Advisor", "🤖"),
           ("pages/82_🏥_System_Health.py", "System Health", "🏥")],
}


def add_next_steps(st, page_number):
    """Add 'Next Steps' navigation links at the bottom of any page.
    Call this at the end of every page: add_next_steps(st, '20')
    """
    steps = NEXT_STEPS.get(str(page_number), [])
    if not steps:
        return

    st.markdown("---")
    st.markdown("**Next Steps:**")
    cols = st.columns(len(steps))
    for i, (path, label, icon) in enumerate(steps):
        cols[i].page_link(path, label=label, icon=icon)
