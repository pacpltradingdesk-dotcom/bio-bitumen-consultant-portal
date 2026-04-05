"""
Session State Keys — SINGLE SOURCE OF TRUTH for all state key names.
Every page MUST import these constants instead of using raw strings.
This prevents key mismatches across pages.
"""

# Plant Configuration
CAPACITY_KEY = "capacity_tpd"
WORKING_DAYS_KEY = "working_days"
PRODUCT_MODEL_KEY = "product_model"

# Revenue
SELLING_PRICE_KEY = "selling_price_per_mt"
BIOCHAR_PRICE_KEY = "biochar_price_per_mt"
SYNGAS_VALUE_KEY = "syngas_value_per_mt"

# Costs
RAW_MATERIAL_COST_KEY = "raw_material_cost_per_mt"
POWER_COST_KEY = "power_cost_per_mt"
LABOUR_COST_KEY = "labour_cost_per_mt"
TRANSPORT_COST_KEY = "transport_cost_per_mt"

# Finance
INTEREST_RATE_KEY = "interest_rate"
EQUITY_RATIO_KEY = "equity_ratio"
EMI_TENURE_KEY = "emi_tenure_months"

# Derived (auto-calculated)
INVESTMENT_CR_KEY = "investment_cr"
INVESTMENT_LAC_KEY = "investment_lac"
LOAN_CR_KEY = "loan_cr"
EQUITY_CR_KEY = "equity_cr"
ROI_KEY = "roi_pct"
IRR_KEY = "irr_pct"
DSCR_KEY = "dscr_yr3"
BREAK_EVEN_KEY = "break_even_months"
EMI_LAC_KEY = "emi_lac_mth"
MONTHLY_PROFIT_KEY = "monthly_profit_lac"
PROFIT_PER_MT_KEY = "profit_per_mt"
REVENUE_YR5_KEY = "revenue_yr5_lac"

# Client
CLIENT_NAME_KEY = "client_name"
CLIENT_COMPANY_KEY = "client_company"
PROJECT_NAME_KEY = "project_name"
STATE_KEY = "state"
LOCATION_KEY = "location"

# Market (live)
CRUDE_PRICE_KEY = "crude_price_usd"
VG30_PRICE_KEY = "vg30_price_inr"
FX_RATE_KEY = "usd_inr_rate"
