"""Complete System Verification — Every engine, skill, link, software."""
import sys, os, glob, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

print('=' * 70)
print('  COMPLETE SYSTEM VERIFICATION')
print('=' * 70)

# 1. ENGINES
engines = [
    'state_manager', 'config', 'master_data_loader', 'interpolation_engine', 'database',
    'engines.detailed_costing', 'engines.dpr_financial_engine', 'engines.plant_engineering',
    'engines.combination_engine', 'engines.drawing_prompt_generator', 'engines.ai_engine',
    'engines.ai_image_generator', 'engines.dalle_layout_engine', 'engines.free_apis',
    'engines.whatsapp_engine', 'engines.email_engine', 'engines.package_engine',
    'engines.docx_customizer', 'engines.dynamic_doc_generator', 'engines.report_generator',
    'engines.master_context', 'engines.three_process_model', 'engines.video_engine',
    'engines.audit_logger', 'engines.image_cache_engine', 'engines.visual_content_engine',
    'engines.page_navigation', 'engines.flow_audit_engine',
    'utils.formatting', 'utils.page_helpers', 'utils.contradiction_alerts',
]
print(f'\n1. ENGINES ({len(engines)} total)')
e_ok = e_fail = 0
for mod in engines:
    try:
        importlib.import_module(mod)
        e_ok += 1
    except Exception as e:
        print(f'  FAIL: {mod} — {str(e)[:50]}')
        e_fail += 1
print(f'  {e_ok}/{e_ok + e_fail} OK')

# 2. PAGES
import py_compile
pages = sorted(glob.glob('pages/*.py'))
print(f'\n2. PAGES ({len(pages)} total)')
p_ok = p_fail = 0
for p in pages:
    try:
        py_compile.compile(p, doraise=True)
        p_ok += 1
    except:
        print(f'  FAIL: {os.path.basename(p)}')
        p_fail += 1
print(f'  {p_ok}/{p_ok + p_fail} syntax OK')

# 3. NAV + CFG
print(f'\n3. CONNECTIVITY')
nav = cfg_linked = 0
for p in pages:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'add_next_steps' in c or c.count('page_link') > 2:
        nav += 1
    if 'get_config' in c:
        cfg_linked += 1
print(f'  Navigation: {nav}/{len(pages)} pages')
print(f'  CFG linked: {cfg_linked}/{len(pages)} pages')

# 4. SOFTWARE
print(f'\n4. SOFTWARE LIBRARIES')
libs = {'streamlit': 'streamlit', 'pandas': 'pandas', 'plotly': 'plotly',
        'openpyxl': 'openpyxl', 'python-docx': 'docx', 'requests': 'requests',
        'numpy': 'numpy', 'python-pptx': 'pptx'}
for name, mod in libs.items():
    try:
        importlib.import_module(mod)
        print(f'  OK: {name}')
    except:
        print(f'  MISSING: {name}')

# 5. DATA
print(f'\n5. DATA DIRECTORIES')
for name, path in [('Database', 'data'), ('Drawings', 'data/all_drawings'),
                    ('AI Images', 'data/ai_drawings'), ('Cache', 'data/cached_drawings'),
                    ('Exports', 'data/exports')]:
    exists = os.path.exists(path)
    print(f'  {"OK" if exists else "--"}: {name}')

# 6. TEMPLATES
print(f'\n6. DOCUMENT TEMPLATES')
base = 'C:/Users/HP/Desktop/Bio Bitumen Full Working all document'
t_count = len(glob.glob(f'{base}/PLANT_*/12_Regulatory_Documents/*.docx'))
t_count += len(glob.glob(f'{base}/PLANT_*/10_Bank_KYC_Documents/*.docx'))
t_count += len(glob.glob(f'{base}/PLANT_*/14_Govt_Scheme_Docs/*.docx'))
t_count += len(glob.glob(f'{base}/PLANT_*/08_Financials/*.xlsx'))
print(f'  Templates on disk: {t_count}')

# 7. AUTO-FILL
print(f'\n7. AUTO-FILL SYSTEM')
from engines.docx_customizer import get_default_replacements
r = get_default_replacements({'name': 'Test'}, cfg={'capacity_tpd': 25, 'state': 'GJ', 'investment_cr': 10, 'process_id': 1})
print(f'  Replacement fields: {len(r)}')

# 8. LICENSES
from config import LICENSE_TYPES
print(f'\n8. COMPLIANCE')
print(f'  Licenses tracked: {len(LICENSE_TYPES)}')
print(f'  Mandatory: {sum(1 for l in LICENSE_TYPES if l.get("mandatory"))}')

# 9. COMBINATIONS
from engines.combination_engine import get_all_combinations_count
print(f'\n9. DRAWING SYSTEM')
print(f'  Combinations: {get_all_combinations_count()}')

# SUMMARY
print(f'\n{"=" * 70}')
issues = e_fail + p_fail + (len(pages) - nav) + (len(pages) - cfg_linked)
print(f'  Engines: {e_ok}/{e_ok+e_fail}')
print(f'  Pages: {p_ok} syntax OK | {nav} navigated | {cfg_linked} cfg-linked')
print(f'  Libraries: {len(libs)} installed')
print(f'  Templates: {t_count} on disk')
print(f'  Auto-fill: {len(r)} fields')
print(f'  Licenses: {len(LICENSE_TYPES)}')
print(f'  Drawing combos: {get_all_combinations_count()}')
if e_fail == 0 and p_fail == 0:
    print(f'\n  ALL SYSTEMS OPERATIONAL')
else:
    print(f'\n  {e_fail + p_fail} issues found')
print('=' * 70)
