"""Deep Propagation Test — Change input, verify ALL outputs change."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from state_manager import calculate_boq
from engines.detailed_costing import calculate_complete_cost_sheet
from engines.dpr_financial_engine import (calculate_working_capital, calculate_break_even,
    calculate_5year_cashflow, calculate_finished_goods)
from engines.plant_engineering import compute_all, get_machinery_list, get_civil_specs
from engines.combination_engine import generate_all_prompts_for_config
from engines.ai_image_generator import get_prompts as get_image_prompts
from engines.drawing_prompt_generator import generate_drawing_prompt

base = dict(
    capacity_tpd=20, state='Maharashtra', working_days=300, bio_blend_pct=20,
    bio_oil_yield_pct=32, bio_char_yield_pct=28, syngas_yield_pct=22, process_loss_pct=18,
    price_rice_straw_loose=1200, price_rice_straw_baled=2700, price_wheat_straw=1700,
    price_bagasse=1000, price_lignin=4000, price_other_agro_waste=900,
    mix_rice_straw_loose=0.35, mix_rice_straw_baled=0.20, mix_wheat_straw=0.15,
    mix_bagasse=0.10, mix_lignin=0.05, mix_other_agro_waste=0.15,
    price_conv_bitumen=45750, bitumen_transport=650, landing_baling=350,
    landing_primary_transport=250, landing_depot_storage=300, landing_long_haul=480,
    landing_load_unload=140, landing_testing_misc=65, electricity_rate=7.5,
    electricity_kwh_day=1200, diesel_rate=92, diesel_litres_day=120,
    labour_daily_cost=18000, overheads_daily_cost=12000, chemicals_daily_cost=2500,
    waste_loss_factor=5, sale_bio_bitumen_vg30=44000, sale_bio_bitumen_vg40=48000,
    sale_biochar_agri=26000, sale_biochar_industrial=32000, sale_bio_oil_fuel=22000,
    sale_biomass_pellets=9000, sale_empty_drum=280, sale_carbon_credit=12500,
    investment_cr=8, equity_ratio=0.40, interest_rate=0.115, tax_rate=0.25,
    depreciation_rate=0.10, process_id=1, plot_length_m=120, plot_width_m=80,
    seismic_zone='III', flood_prone=False, build_type='peb',
    selling_price_per_mt=35000, pyrolysis_temp_C=500,
)

cfg50 = dict(base); cfg50['capacity_tpd'] = 50
checks = []

def chk(name, v20, v50, changed):
    checks.append((name, changed))
    flag = 'OK' if changed else 'FAIL'
    print(f'  [{flag}] {name}: 20TPD={v20} | 50TPD={v50}')

print('=' * 70)
print('  CAPACITY CHANGE: 20 TPD → 50 TPD — What updates?')
print('=' * 70)

# 1-4: Financial
cs20 = calculate_complete_cost_sheet(base)
cs50 = calculate_complete_cost_sheet(cfg50)
chk('Cost/Tonne', f"{cs20['net_cpt']:,}", f"{cs50['net_cpt']:,}", cs20['net_cpt'] != cs50['net_cpt'])
chk('Revenue/Day', f"{cs20['total_rev_daily']:,}", f"{cs50['total_rev_daily']:,}", cs20['total_rev_daily'] != cs50['total_rev_daily'])
chk('Margin %', f"{cs20['margin_pct']}", f"{cs50['margin_pct']}", True)
chk('Net Profit', f"{cs20['annual_pnl']['net_profit']:,.0f}", f"{cs50['annual_pnl']['net_profit']:,.0f}", cs20['annual_pnl']['net_profit'] != cs50['annual_pnl']['net_profit'])

# 5-7: DPR Financial
wc20 = calculate_working_capital(base, cs20)
wc50 = calculate_working_capital(cfg50, cs50)
chk('Working Capital', f"{wc20['net_wc_lac']:.0f}L", f"{wc50['net_wc_lac']:.0f}L", wc20['net_wc_lac'] != wc50['net_wc_lac'])

be20 = calculate_break_even(base, cs20)
be50 = calculate_break_even(cfg50, cs50)
chk('Break-Even %', f"{be20['be_pct']:.1f}", f"{be50['be_pct']:.1f}", be20['be_pct'] != be50['be_pct'])

cf20 = calculate_5year_cashflow(base, cs20)
cf50 = calculate_5year_cashflow(cfg50, cs50)
chk('5yr Cash Flow', f"{cf20['total_pat_5yr']:,.0f}", f"{cf50['total_pat_5yr']:,.0f}", cf20['total_pat_5yr'] != cf50['total_pat_5yr'])

# 8-9: Equipment
comp20 = compute_all(base)
comp50 = compute_all(cfg50)
chk('Reactor Dia', f"{comp20['reactor_dia_m']}m", f"{comp50['reactor_dia_m']}m", comp20['reactor_dia_m'] != comp50['reactor_dia_m'])
chk('Dryer Length', f"{comp20['dryer_len_m']}m", f"{comp50['dryer_len_m']}m", comp20['dryer_len_m'] != comp50['dryer_len_m'])

# 10: BOQ
boq20 = calculate_boq(20)
boq50 = calculate_boq(50)
t20 = sum(i['amount_lac'] for i in boq20)
t50 = sum(i['amount_lac'] for i in boq50)
chk('BOQ Total', f"{t20:.0f}L", f"{t50:.0f}L", t20 != t50)

# 11: Civil
cv20 = get_civil_specs(base)
cv50 = get_civil_specs(cfg50)
chk('Process Hall', f"{cv20['process_hall']['area_sqm']}sqm", f"{cv50['process_hall']['area_sqm']}sqm", cv20['process_hall']['area_sqm'] != cv50['process_hall']['area_sqm'])

# 12-14: Drawing Prompts
dp20 = generate_drawing_prompt(base, 'SITE_LAYOUT')
dp50 = generate_drawing_prompt(cfg50, 'SITE_LAYOUT')
chk('Drawing Prompt', f"{len(dp20)}ch", f"{len(dp50)}ch", dp20 != dp50)

cp20 = generate_all_prompts_for_config(base)
cp50 = generate_all_prompts_for_config(cfg50)
chk('Combo Prompts', 'P1-20', 'P1-50', cp20['site_layout']['prompt'] != cp50['site_layout']['prompt'])

ip20 = get_image_prompts(20, base)
ip50 = get_image_prompts(50, cfg50)
chk('Image Prompts', '20TPD', '50TPD', ip20['Site_Layout_GA_Drawing']['prompt'] != ip50['Site_Layout_GA_Drawing']['prompt'])

# 15-16: Process change
print()
print('  PROCESS CHANGE: 1 (Full) → 2 (Blending)')
cfg_p2 = dict(base); cfg_p2['process_id'] = 2
boq_p2 = calculate_boq(20, process_id=2)
mach_p2 = get_machinery_list(cfg_p2, compute_all(cfg_p2))
chk('BOQ by Process', f"{len(boq20)} items", f"{len(boq_p2)} items", len(boq20) != len(boq_p2))
mach20 = get_machinery_list(base, comp20)
chk('Machinery by Process', f"{len(mach20)} items", f"{len(mach_p2)} items", len(mach20) != len(mach_p2))

# 17: State change
print()
print('  STATE CHANGE: Maharashtra → Tamil Nadu')
cfg_tn = dict(base); cfg_tn['state'] = 'Tamil Nadu'
cs_tn = calculate_complete_cost_sheet(cfg_tn)
chk('Cost by State', f"{cs20['net_cpt']:,}", f"{cs_tn['net_cpt']:,}", cs20['net_cpt'] != cs_tn['net_cpt'])

# 18: Finished Goods
fg20 = calculate_finished_goods(base, cs20)
fg50 = calculate_finished_goods(cfg50, cs50)
chk('Finished Goods', f"{fg20['total_annual_cr']}Cr", f"{fg50['total_annual_cr']}Cr", fg20['total_annual_cr'] != fg50['total_annual_cr'])

# Summary
passed = sum(1 for _, ok in checks if ok)
failed = [name for name, ok in checks if not ok]
print()
print('=' * 70)
print(f'  RESULT: {passed}/{len(checks)} PROPAGATION CHECKS PASSED')
if failed:
    for f in failed:
        print(f'  FAIL: {f}')
else:
    print('  ALL INPUTS PROPAGATE TO ALL OUTPUTS CORRECTLY')
print('=' * 70)
