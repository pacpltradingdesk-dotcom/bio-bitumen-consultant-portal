"""
Seed vendor database — all 80 vendors from VENDOR_ENQUIRY_PACK_2026-04-21.
Run: python seed_vendors.py
Idempotent — safe to re-run.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_connection
from datetime import datetime, timezone, timedelta

init_db()
IST = timezone(timedelta(hours=5, minutes=30))

# Sr numbers match VENDOR_ENQUIRY_PACK tracker (1-80)
VENDORS = [
    # ══════════════════════════════════════════════════════════════════
    # A — PLANT & MACHINERY  (Sr 1-39)
    # ══════════════════════════════════════════════════════════════════

    # A.01 Pyrolysis Reactors (Sr 1-3)
    {"sr": 1,  "vendor_name": "BIOMAX FUEL TECH",
     "equipment": "Pyrolysis Reactor 5 MT Batch (SS316)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 85.0, "delivery_weeks": 20, "warranty_months": 24,
     "city": "Bangalore", "email": "enquiry@biomaxfueltech.com", "contact": "biomaxfueltech.com"},

    {"sr": 2,  "vendor_name": "PRAJ BIOMOBILITY",
     "equipment": "Pyrolysis Reactor 5 MT Batch (SS316)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 95.0, "delivery_weeks": 24, "warranty_months": 24,
     "city": "Pune", "email": "biomobility@praj.net", "contact": "praj.net"},

    {"sr": 3,  "vendor_name": "KIS GREEN ENERGY",
     "equipment": "Pyrolysis Reactor 5 MT Batch (SS316)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 78.0, "delivery_weeks": 18, "warranty_months": 18,
     "city": "Delhi", "email": "info@kisgreen.in", "contact": "kisgreen.in"},

    # A.02 Husk / Dryer / Processing Line (Sr 4-6)
    {"sr": 4,  "vendor_name": "TECHNO DESIGNS",
     "equipment": "Rice Husk Processing Line (Shredder+Dryer+Pelletizer)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 35.0, "delivery_weeks": 14, "warranty_months": 18,
     "city": "Ahmedabad", "email": "sales@technodesigns.in", "contact": "technodesigns.in"},

    {"sr": 5,  "vendor_name": "SWAN ENVIRONMENTAL",
     "equipment": "Biomass Processing Line (Shredder+Dryer)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 32.0, "delivery_weeks": 12, "warranty_months": 18,
     "city": "Hyderabad", "email": "sales@swanenvironmental.com", "contact": "swanenvironmental.com"},

    {"sr": 6,  "vendor_name": "SPRAYING SYSTEMS INDIA",
     "equipment": "Rice Husk Processing Line", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 38.0, "delivery_weeks": 16, "warranty_months": 18,
     "city": "Mumbai", "email": "india@spray.com", "contact": "spray.com"},

    # A.03 Condensers + ESP (Sr 7-9)
    {"sr": 7,  "vendor_name": "THERMOPAC ENGINEERS",
     "equipment": "Shell & Tube Condenser for Bio-Oil Recovery", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 8.5, "delivery_weeks": 10, "warranty_months": 18,
     "city": "Pune", "email": "sales@thermopac.in", "contact": "thermopac.in"},

    {"sr": 8,  "vendor_name": "THERMAX LTD",
     "equipment": "Shell & Tube Heat Exchanger / Condenser", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 12.0, "delivery_weeks": 12, "warranty_months": 24,
     "city": "Pune", "email": "process@thermax.com", "contact": "thermax.com"},

    {"sr": 9,  "vendor_name": "ALFA LAVAL INDIA",
     "equipment": "Plate Heat Exchanger / Condenser", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 14.0, "delivery_weeks": 14, "warranty_months": 24,
     "city": "Mumbai", "email": "india.sales@alfalaval.com", "contact": "alfalaval.com"},

    # A.04 Thin Film Evaporators (Sr 10-12)
    {"sr": 10, "vendor_name": "SUMIT ENGINEERING",
     "equipment": "Thin Film Evaporator (TFE) for Bio-Oil Refining", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 22.0, "delivery_weeks": 16, "warranty_months": 18,
     "city": "Vadodara", "email": "sales@sumitengg.com", "contact": "sumitengg.com"},

    {"sr": 11, "vendor_name": "CHEM PROCESS SYSTEMS",
     "equipment": "Thin Film Evaporator (TFE)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 25.0, "delivery_weeks": 18, "warranty_months": 24,
     "city": "Ahmedabad", "email": "sales@chemprocess.co.in", "contact": "chemprocess.co.in"},

    {"sr": 12, "vendor_name": "POPE SCIENTIFIC (India Agent)",
     "equipment": "Thin Film Evaporator (TFE)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 32.0, "delivery_weeks": 24, "warranty_months": 24,
     "city": "Mumbai", "email": "india@popescientific.com", "contact": "popescientific.com"},

    # A.05 Colloid Mills (Sr 13-15)
    {"sr": 13, "vendor_name": "FRYMAKORUMA INDIA",
     "equipment": "Colloid Mill for Bitumen Blending", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 9.5, "delivery_weeks": 12, "warranty_months": 18,
     "city": "Mumbai", "email": "india@frymakoruma.com", "contact": "frymakoruma.com"},

    {"sr": 14, "vendor_name": "AHUJA GROUP",
     "equipment": "High Shear Colloid Mill / Mixer", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 7.0, "delivery_weeks": 10, "warranty_months": 18,
     "city": "Yamuna Nagar", "email": "sales@ahujagroup.in", "contact": "ahujagroup.in"},

    {"sr": 15, "vendor_name": "SPARX ENGINEERS",
     "equipment": "Colloid Mill / Inline Homogenizer", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 8.0, "delivery_weeks": 10, "warranty_months": 18,
     "city": "Mumbai", "email": "sales@sparxengineers.com", "contact": "sparxengineers.com"},

    # A.06 VG-10 Heated Tanks (Sr 16-18)
    {"sr": 16, "vendor_name": "THERMOPAC ENGINEERS",
     "equipment": "VG10 Bitumen Storage Tank (Insulated, Heated)", "category": "A_PLANT_MACHINERY",
     "capacity": "50 KL", "price_lac": 6.5, "delivery_weeks": 8, "warranty_months": 18,
     "city": "Pune", "email": "sales@thermopac.in", "contact": "thermopac.in"},

    {"sr": 17, "vendor_name": "RAY ENGINEERING",
     "equipment": "VG10 Hot Bitumen Storage Tank", "category": "A_PLANT_MACHINERY",
     "capacity": "50 KL", "price_lac": 5.8, "delivery_weeks": 8, "warranty_months": 12,
     "city": "Ahmedabad", "email": "sales@rayengg.com", "contact": "rayengg.com"},

    {"sr": 18, "vendor_name": "HEATEX INDIA",
     "equipment": "Insulated Bitumen Storage Tank", "category": "A_PLANT_MACHINERY",
     "capacity": "50 KL", "price_lac": 6.0, "delivery_weeks": 10, "warranty_months": 18,
     "city": "Mumbai", "email": "sales@heatexindia.com", "contact": "heatexindia.com"},

    # A.07 PMB Maturation Tanks (Sr 19-21)
    {"sr": 19, "vendor_name": "SSVM PROJECTS",
     "equipment": "PMB-40 Storage Tank (Insulated 160C)", "category": "A_PLANT_MACHINERY",
     "capacity": "30 KL", "price_lac": 7.5, "delivery_weeks": 10, "warranty_months": 18,
     "city": "Ahmedabad", "email": "sales@ssvmprojects.com", "contact": "ssvmprojects.com"},

    {"sr": 20, "vendor_name": "SIGMA THERMAL INDIA",
     "equipment": "PMB Storage Tank with Heating Coils", "category": "A_PLANT_MACHINERY",
     "capacity": "30 KL", "price_lac": 8.5, "delivery_weeks": 12, "warranty_months": 18,
     "city": "Mumbai", "email": "sales@sigmathermal.in", "contact": "sigmathermal.in"},

    {"sr": 21, "vendor_name": "VAIBHAV TANK & VESSELS",
     "equipment": "PMB-40 Insulated Storage Tank", "category": "A_PLANT_MACHINERY",
     "capacity": "30 KL", "price_lac": 6.8, "delivery_weeks": 8, "warranty_months": 12,
     "city": "Ahmedabad", "email": "sales@vaibhavtank.com", "contact": "vaibhavtank.com"},

    # A.08 DG Sets (Sr 22-24)
    {"sr": 22, "vendor_name": "KIRLOSKAR OIL ENGINES",
     "equipment": "Diesel Generator Set 80 kVA (CPCB-IV+)", "category": "A_PLANT_MACHINERY",
     "capacity": "80 kVA", "price_lac": 9.5, "delivery_weeks": 8, "warranty_months": 24,
     "city": "Pune", "email": "koel@kirloskar.com", "contact": "kirloskar.com"},

    {"sr": 23, "vendor_name": "CUMMINS INDIA",
     "equipment": "Diesel Generator Set 82.5 kVA (CPCB-IV+)", "category": "A_PLANT_MACHINERY",
     "capacity": "82.5 kVA", "price_lac": 10.5, "delivery_weeks": 8, "warranty_months": 24,
     "city": "Pune", "email": "power.india@cummins.com", "contact": "cummins.in"},

    {"sr": 24, "vendor_name": "MAHINDRA POWEROL",
     "equipment": "Diesel Generator Set 82.5 kVA", "category": "A_PLANT_MACHINERY",
     "capacity": "82.5 kVA", "price_lac": 9.8, "delivery_weeks": 6, "warranty_months": 24,
     "city": "Mumbai", "email": "powerol@mahindra.com", "contact": "mahindra.com"},

    # A.09 Transformers (Sr 25-27)
    {"sr": 25, "vendor_name": "CG POWER & INDUSTRIAL",
     "equipment": "Distribution Transformer 250 kVA 11kV/415V", "category": "A_PLANT_MACHINERY",
     "capacity": "250 kVA", "price_lac": 4.5, "delivery_weeks": 10, "warranty_months": 60,
     "city": "Mumbai", "email": "sales@cgpower.com", "contact": "cgpower.com"},

    {"sr": 26, "vendor_name": "VIJAI ELECTRICALS",
     "equipment": "Transformer 250 kVA 11kV/415V CRGO", "category": "A_PLANT_MACHINERY",
     "capacity": "250 kVA", "price_lac": 4.2, "delivery_weeks": 10, "warranty_months": 60,
     "city": "Hyderabad", "email": "sales@vijaielectricals.com", "contact": "vijaielectricals.com"},

    {"sr": 27, "vendor_name": "RAYCHEM RPG",
     "equipment": "Transformer & HT Switchgear Package", "category": "A_PLANT_MACHINERY",
     "capacity": "250 kVA", "price_lac": 5.5, "delivery_weeks": 12, "warranty_months": 60,
     "city": "Mumbai", "email": "sales@raychemindia.com", "contact": "raychemindia.com"},

    # A.10 MCC + PLC + SCADA (Sr 28-30)
    {"sr": 28, "vendor_name": "ROCKWELL AUTOMATION (via L&T SI)",
     "equipment": "MCC Panel + Allen Bradley PLC/SCADA", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 18.0, "delivery_weeks": 16, "warranty_months": 24,
     "city": "Pune", "email": "india.sales@ra.rockwell.com", "contact": "rockwellautomation.com"},

    {"sr": 29, "vendor_name": "SIEMENS INDIA",
     "equipment": "MCC Panel + Siemens S7 PLC + WinCC SCADA", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 20.0, "delivery_weeks": 16, "warranty_months": 36,
     "city": "Mumbai", "email": "processindustries.in@siemens.com", "contact": "siemens.co.in"},

    {"sr": 30, "vendor_name": "MITSUBISHI ELECTRIC INDIA",
     "equipment": "MCC Panel + MELSEC PLC", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD", "price_lac": 17.0, "delivery_weeks": 14, "warranty_months": 24,
     "city": "Pune", "email": "factory.in@melco.com", "contact": "mitsubishielectric.co.in"},

    # A.11 Weighbridges (Sr 31-33)
    {"sr": 31, "vendor_name": "SANSUI ELECTRONICS",
     "equipment": "Pitless Weighbridge 60 MT Electronic", "category": "A_PLANT_MACHINERY",
     "capacity": "60 MT", "price_lac": 6.0, "delivery_weeks": 8, "warranty_months": 24,
     "city": "Delhi", "email": "sales@sansui.in", "contact": "sansui.in"},

    {"sr": 32, "vendor_name": "ESSAE TERAOKA",
     "equipment": "Pit-type Weighbridge 60 MT (ESSAE)", "category": "A_PLANT_MACHINERY",
     "capacity": "60 MT", "price_lac": 6.5, "delivery_weeks": 8, "warranty_months": 24,
     "city": "Bangalore", "email": "sales@essae.in", "contact": "essae.in"},

    {"sr": 33, "vendor_name": "ADEPT SCALES",
     "equipment": "Pitless Weighbridge 60 MT with Software", "category": "A_PLANT_MACHINERY",
     "capacity": "60 MT", "price_lac": 5.8, "delivery_weeks": 6, "warranty_months": 18,
     "city": "Delhi", "email": "sales@adeptscales.com", "contact": "adeptscales.com"},

    # A.12 Fire Safety (Sr 34-36)
    {"sr": 34, "vendor_name": "CEASEFIRE INDUSTRIES",
     "equipment": "Fire Safety System (Hydrants+Extinguishers+Hose)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD Plant", "price_lac": 8.0, "delivery_weeks": 6, "warranty_months": 12,
     "city": "Delhi", "email": "sales@ceasefire.in", "contact": "ceasefire.in"},

    {"sr": 35, "vendor_name": "MINIMAX FIRE SAFETY",
     "equipment": "Fire Hydrant + Foam System (NFPA 15)", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD Plant", "price_lac": 9.5, "delivery_weeks": 8, "warranty_months": 12,
     "city": "Mumbai", "email": "sales@minimax.in", "contact": "minimax.in"},

    {"sr": 36, "vendor_name": "NEWAGE FIRE",
     "equipment": "Fire Hydrant System + Portable Extinguishers", "category": "A_PLANT_MACHINERY",
     "capacity": "5 TPD Plant", "price_lac": 7.5, "delivery_weeks": 6, "warranty_months": 12,
     "city": "Hyderabad", "email": "sales@newagefire.com", "contact": "newagefire.com"},

    # A.13 QC Laboratory (Sr 37-39)
    {"sr": 37, "vendor_name": "PRESTO GROUP",
     "equipment": "QC Lab Equipment Package (Bitumen Testing)", "category": "A_PLANT_MACHINERY",
     "capacity": "Full Lab", "price_lac": 12.0, "delivery_weeks": 8, "warranty_months": 12,
     "city": "Faridabad", "email": "sales@prestogroup.com", "contact": "prestogroup.com"},

    {"sr": 38, "vendor_name": "LABOMED INC (India)",
     "equipment": "Laboratory Instruments (Viscometer+Penetrometer)", "category": "A_PLANT_MACHINERY",
     "capacity": "Full Lab", "price_lac": 10.5, "delivery_weeks": 10, "warranty_months": 12,
     "city": "Mumbai", "email": "india@labomed.com", "contact": "labomed.com"},

    {"sr": 39, "vendor_name": "AIMIL LTD",
     "equipment": "QC Lab Package (IS:73 Testing Equipment)", "category": "A_PLANT_MACHINERY",
     "capacity": "Full Lab", "price_lac": 11.0, "delivery_weeks": 8, "warranty_months": 12,
     "city": "Delhi", "email": "sales@aimil.com", "contact": "aimil.com"},

    # ══════════════════════════════════════════════════════════════════
    # B — RAW MATERIAL SUPPLIERS  (Sr 40-53)
    # ══════════════════════════════════════════════════════════════════

    # B.01 Rice Husk (Sr 40-42)
    {"sr": 40, "vendor_name": "HARYANA BASMATI RICE MILLS",
     "equipment": "Rice Husk Supply (Loose) — 800 MT/yr", "category": "B_RAW_MATERIAL",
     "capacity": "800 MT/yr", "price_lac": 0.06, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Karnal, Haryana", "email": "procurement@haryanabasmati.com",
     "contact": "Rs 6,000/MT landed"},

    {"sr": 41, "vendor_name": "KISAN RICE INDUSTRIES",
     "equipment": "Rice Husk Supply (Baled) — 600 MT/yr", "category": "B_RAW_MATERIAL",
     "capacity": "600 MT/yr", "price_lac": 0.12, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Kaithal, Haryana", "email": "sales@kisanrice.in",
     "contact": "Rs 6,000/MT baled"},

    {"sr": 42, "vendor_name": "SHIV SHAKTI AGRO",
     "equipment": "Rice Husk + Wheat Straw Supply — Backup", "category": "B_RAW_MATERIAL",
     "capacity": "400 MT/yr", "price_lac": 0.08, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Panipat, Haryana", "email": "sales@shivshaktiagro.com",
     "contact": "Rs 6,000/MT"},

    # B.02 VG-10 Bitumen (Sr 43-44)
    {"sr": 43, "vendor_name": "IOCL PANIPAT REFINERY",
     "equipment": "VG-10 Base Bitumen Supply (3.5 MT/day)", "category": "B_RAW_MATERIAL",
     "capacity": "Bulk tanker", "price_lac": 4.80, "delivery_weeks": 1, "warranty_months": 0,
     "city": "Panipat, Haryana", "email": "bitumen.panipat@iocl.com",
     "contact": "Rs 48,000/MT ex-decanter"},

    {"sr": 44, "vendor_name": "HPCL PANIPAT TERMINAL",
     "equipment": "VG-10 Base Bitumen Supply", "category": "B_RAW_MATERIAL",
     "capacity": "Bulk tanker", "price_lac": 4.80, "delivery_weeks": 1, "warranty_months": 0,
     "city": "Panipat, Haryana", "email": "bitumen.panipat@hpcl.in",
     "contact": "Rs 48,000/MT ex-terminal"},

    # B.03 SBS Polymer (Sr 45-46)
    {"sr": 45, "vendor_name": "RELIANCE SIBUR ELASTOMERS",
     "equipment": "SBS Polymer Linear 30:70 for PMB-40", "category": "B_RAW_MATERIAL",
     "capacity": "35 kg/MT product", "price_lac": 2.50, "delivery_weeks": 2, "warranty_months": 6,
     "city": "Jamnagar", "email": "sales@reliance-sibur.com",
     "contact": "Rs 2,50,000/MT"},

    {"sr": 46, "vendor_name": "LG CHEM INDIA",
     "equipment": "SBS Rubber Polymer — Backup Supply", "category": "B_RAW_MATERIAL",
     "capacity": "35 kg/MT product", "price_lac": 2.60, "delivery_weeks": 3, "warranty_months": 6,
     "city": "Dahej", "email": "india@lgchem.com",
     "contact": "Rs 2,60,000/MT"},

    # B.04 Chemicals / Additives (Sr 47-53)
    {"sr": 47, "vendor_name": "DHANUKA CHEMICAL",
     "equipment": "Hydrated Lime (Ca(OH)2) for Process", "category": "B_RAW_MATERIAL",
     "capacity": "Monthly supply", "price_lac": 0.05, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Rewari, Haryana", "email": "sales@dhanukachem.com",
     "contact": "Local Haryana supplier"},

    {"sr": 48, "vendor_name": "TAG IMPEX",
     "equipment": "Sulfur 99% Prilled for Additive", "category": "B_RAW_MATERIAL",
     "capacity": "Monthly supply", "price_lac": 0.08, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Panipat", "email": "sales@tagimpex.com",
     "contact": "Panipat region"},

    {"sr": 49, "vendor_name": "DCM SHRIRAM CHEMICALS",
     "equipment": "NaOH Pellets 98% for Effluent Treatment", "category": "B_RAW_MATERIAL",
     "capacity": "Monthly supply", "price_lac": 0.12, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Delhi", "email": "chemicals@dcmshriram.com",
     "contact": "dcmshriram.com"},

    {"sr": 50, "vendor_name": "CLARIANT INDIA",
     "equipment": "Demulsifier for Bio-Oil Water Separation", "category": "B_RAW_MATERIAL",
     "capacity": "Monthly supply", "price_lac": 0.35, "delivery_weeks": 1, "warranty_months": 0,
     "city": "Mumbai", "email": "oilservices.india@clariant.com",
     "contact": "clariant.com"},

    {"sr": 51, "vendor_name": "SAVITA OIL TECHNOLOGIES",
     "equipment": "Thermic Fluid (Therminol 66 / Savita HT-300)", "category": "B_RAW_MATERIAL",
     "capacity": "Initial fill + annual top-up", "price_lac": 0.80, "delivery_weeks": 2, "warranty_months": 0,
     "city": "Mumbai", "email": "sales@savitaoil.com",
     "contact": "savitaoil.com"},

    {"sr": 52, "vendor_name": "BHAGWATI PRODUCTS",
     "equipment": "Thermic Fluid — Backup Supply", "category": "B_RAW_MATERIAL",
     "capacity": "Initial fill + top-up", "price_lac": 0.75, "delivery_weeks": 2, "warranty_months": 0,
     "city": "Mumbai", "email": "sales@bhagwatiproducts.com",
     "contact": "bhagwatiproducts.com"},

    {"sr": 53, "vendor_name": "INDIAN ADDITIVES",
     "equipment": "Cleaning Solvents for Equipment Maintenance", "category": "B_RAW_MATERIAL",
     "capacity": "Monthly supply", "price_lac": 0.10, "delivery_weeks": 1, "warranty_months": 0,
     "city": "Faridabad", "email": "sales@indianadditives.com",
     "contact": "Faridabad, Haryana"},

    # ══════════════════════════════════════════════════════════════════
    # C — CIVIL, UTILITIES & LOGISTICS  (Sr 54-63)
    # ══════════════════════════════════════════════════════════════════

    # C.01 PEB Sheds (Sr 54-55)
    {"sr": 54, "vendor_name": "TATA BLUESCOPE STEEL",
     "equipment": "PEB Shed Package (Main 396+Utility 48+Storage 120 sqm)", "category": "C_CIVIL_LOGISTICS",
     "capacity": "564 sqm total", "price_lac": 45.0, "delivery_weeks": 16, "warranty_months": 120,
     "city": "Mumbai", "email": "blueScope.enquiry@tata.com",
     "contact": "tatabluescope.com"},

    {"sr": 55, "vendor_name": "KIRBY BUILDING SYSTEMS",
     "equipment": "PEB Shed Package (Main+Utility+Storage)", "category": "C_CIVIL_LOGISTICS",
     "capacity": "564 sqm total", "price_lac": 42.0, "delivery_weeks": 14, "warranty_months": 120,
     "city": "Hyderabad", "email": "india@kirbybuildingsystems.in",
     "contact": "kirbybuildingsystems.in"},

    # C.02 Electrical (Sr 56)
    {"sr": 56, "vendor_name": "MANCHANDA ELECTRICALS",
     "equipment": "11kV HT Line + LT Panel + Earthing + Plant Wiring", "category": "C_CIVIL_LOGISTICS",
     "capacity": "147 kW connected load", "price_lac": 18.0, "delivery_weeks": 12, "warranty_months": 12,
     "city": "Rohtak, Haryana", "email": "manchandaelectricals@gmail.com",
     "contact": "DHBVN empanelled contractor, Rohtak"},

    # C.03 Insulation (Sr 57)
    {"sr": 57, "vendor_name": "ROCKWOOL INDIA LTD",
     "equipment": "Pipe + Equipment Insulation (Rockwool slabs/blankets)", "category": "C_CIVIL_LOGISTICS",
     "capacity": "Full plant", "price_lac": 4.5, "delivery_weeks": 6, "warranty_months": 60,
     "city": "Delhi NCR", "email": "sales@rockwool.in",
     "contact": "rockwool.in"},

    # C.04 Civil / RCC Contractor (Sr 58)
    {"sr": 58, "vendor_name": "HSVP PANEL GRADE-A CONTRACTOR",
     "equipment": "Civil RCC Foundation + Flooring + Drainage", "category": "C_CIVIL_LOGISTICS",
     "capacity": "644 sqm plot", "price_lac": 28.0, "delivery_weeks": 16, "warranty_months": 12,
     "city": "Bahadurgarh / Jhajjar", "email": "hsvp.bahadurgarh@haryanapwa.gov.in",
     "contact": "HSVP empanelled Grade-A civil contractor"},

    # C.05 VG-10 Tanker Logistics (Sr 59-61)
    {"sr": 59, "vendor_name": "GATI KINTETSU EXPRESS",
     "equipment": "VG-10 Insulated Tanker Transport (Panipat-Bahadurgarh)", "category": "C_CIVIL_LOGISTICS",
     "capacity": "Per trip", "price_lac": 0.35, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Haryana hub", "email": "enquiry@gati.com",
     "contact": "Rs 650/MT | gati.com"},

    {"sr": 60, "vendor_name": "ALLCARGO LOGISTICS",
     "equipment": "VG-10 Insulated Tanker Transport", "category": "C_CIVIL_LOGISTICS",
     "capacity": "Per trip", "price_lac": 0.38, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Mumbai / PAN India", "email": "enquiry@allcargo.com",
     "contact": "allcargo.com"},

    {"sr": 61, "vendor_name": "DRS LOGISTICS",
     "equipment": "Bitumen + PMB Finished Goods Logistics", "category": "C_CIVIL_LOGISTICS",
     "capacity": "Per trip", "price_lac": 0.30, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Delhi NCR", "email": "sales@drslogistics.in",
     "contact": "drslogistics.in"},

    # C.06 SBS / Bagged LTL (Sr 62-63)
    {"sr": 62, "vendor_name": "VRL LOGISTICS",
     "equipment": "SBS Polymer Bagged LTL Freight (Jamnagar-Bahadurgarh)", "category": "C_CIVIL_LOGISTICS",
     "capacity": "LTL parcels", "price_lac": 0.15, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Hubli / PAN India", "email": "cs@vrlgroup.in",
     "contact": "vrlgroup.in"},

    {"sr": 63, "vendor_name": "SHREE MARUTI COURIER",
     "equipment": "SBS Polymer Bagged LTL — Backup", "category": "C_CIVIL_LOGISTICS",
     "capacity": "LTL parcels", "price_lac": 0.14, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Ahmedabad / PAN India", "email": "info@shreemaruti.com",
     "contact": "shreemaruti.com"},

    # ══════════════════════════════════════════════════════════════════
    # D — APPROVALS & STATUTORY CONSULTANTS  (Sr 64-68)
    # ══════════════════════════════════════════════════════════════════

    {"sr": 64, "vendor_name": "PERFACT ENVIRO SOLUTIONS",
     "equipment": "CPCB CTE/CTO + HW Authorization + EIA (HSPCB Haryana)",
     "category": "D_APPROVALS",
     "capacity": "Full service", "price_lac": 3.5, "delivery_weeks": 12, "warranty_months": 0,
     "city": "Faridabad, Haryana", "email": "info@perfactenviro.com",
     "contact": "HSPCB empanelled | perfactenviro.com"},

    {"sr": 65, "vendor_name": "NEWAGE FIRE SAFETY CONSULTANTS",
     "equipment": "Fire NOC Drafting + Filing (Haryana Fire Dept)", "category": "D_APPROVALS",
     "capacity": "Full service", "price_lac": 1.5, "delivery_weeks": 8, "warranty_months": 0,
     "city": "Gurugram, Haryana", "email": "info@newagefireindia.com",
     "contact": "Haryana Fire Dept empanelled"},

    {"sr": 66, "vendor_name": "RAGNAR LABOUR CONSULTANTS",
     "equipment": "Labour Law Compliance (Factory Act + ESI + PF + Shops)", "category": "D_APPROVALS",
     "capacity": "Full service", "price_lac": 1.2, "delivery_weeks": 4, "warranty_months": 0,
     "city": "Rohtak, Haryana", "email": "ragnar.labour@gmail.com",
     "contact": "Rohtak, Haryana"},

    {"sr": 67, "vendor_name": "M/S VERMA & ASSOCIATES",
     "equipment": "Electrical Load Study + CEIG Certificate (Class A)", "category": "D_APPROVALS",
     "capacity": "147 kW load", "price_lac": 0.80, "delivery_weeks": 4, "warranty_months": 0,
     "city": "Faridabad", "email": "verma.associates.elec@gmail.com",
     "contact": "Haryana CEIG empanelled"},

    {"sr": 68, "vendor_name": "CSIR-CRRI",
     "equipment": "Bio-Bitumen Technology Licence (IS 15462:2019) + Technical Support",
     "category": "D_APPROVALS",
     "capacity": "5 TPD licence", "price_lac": 12.0, "delivery_weeks": 0, "warranty_months": 0,
     "city": "New Delhi", "email": "director@crri.res.in",
     "contact": "Dr Ambika Behl | crri.res.in"},

    # ══════════════════════════════════════════════════════════════════
    # E — FINANCE, AUDIT, BANKING, INSURANCE, TReDS  (Sr 69-74)
    # ══════════════════════════════════════════════════════════════════

    {"sr": 69, "vendor_name": "M/S AGARWAL & CO.",
     "equipment": "CA Firm — Statutory Audit + GST + Tax Advisory + CMA Report",
     "category": "E_FINANCE_AUDIT",
     "capacity": "Annual engagement", "price_lac": 2.5, "delivery_weeks": 4, "warranty_months": 0,
     "city": "Karol Bagh, Delhi", "email": "ca.agarwal.karolbagh@gmail.com",
     "contact": "M/s Agarwal & Co., Karol Bagh"},

    {"sr": 70, "vendor_name": "HDFC BANK — ROHTAK BRANCH",
     "equipment": "Term Loan + Working Capital (MSME SME)", "category": "E_FINANCE_AUDIT",
     "capacity": "Rs 3.90 Cr term + Rs 1.20 Cr WC", "price_lac": 0.0, "delivery_weeks": 8,
     "warranty_months": 0,
     "city": "Rohtak, Haryana", "email": "rohtak.branch@hdfcbank.com",
     "contact": "HDFC Bank Rohtak SME desk"},

    {"sr": 71, "vendor_name": "SIDBI",
     "equipment": "MSME Term Loan / SMILE Scheme Co-lending", "category": "E_FINANCE_AUDIT",
     "capacity": "Rs 3.90 Cr term loan", "price_lac": 0.0, "delivery_weeks": 12,
     "warranty_months": 0,
     "city": "New Delhi", "email": "delhi@sidbi.in",
     "contact": "sidbi.in | SMILE / SPEED + scheme"},

    {"sr": 72, "vendor_name": "ICICI LOMBARD",
     "equipment": "Industrial All-Risk + Plant & Machinery Insurance", "category": "E_FINANCE_AUDIT",
     "capacity": "Rs 6.50 Cr sum insured", "price_lac": 0.65, "delivery_weeks": 1,
     "warranty_months": 12,
     "city": "Mumbai", "email": "corporate@icicilombard.com",
     "contact": "icicilombard.com"},

    {"sr": 73, "vendor_name": "NEW INDIA ASSURANCE",
     "equipment": "Fire + Stock + Machinery Breakdown Insurance", "category": "E_FINANCE_AUDIT",
     "capacity": "Rs 6.50 Cr sum insured", "price_lac": 0.60, "delivery_weeks": 1,
     "warranty_months": 12,
     "city": "Delhi", "email": "headoffice@niaindia.com",
     "contact": "newindia.co.in"},

    {"sr": 74, "vendor_name": "RXIL + M1EXCHANGE (TReDS)",
     "equipment": "TReDS Bill Discounting Platform for Receivables", "category": "E_FINANCE_AUDIT",
     "capacity": "Invoice financing", "price_lac": 0.0, "delivery_weeks": 2,
     "warranty_months": 0,
     "city": "Mumbai", "email": "onboarding@rxil.in",
     "contact": "rxil.in | m1xchange.com"},

    # ══════════════════════════════════════════════════════════════════
    # F — TESTING & CERTIFICATION LABS  (Sr 75-80)
    # ══════════════════════════════════════════════════════════════════

    # F.01 BIS IS 15462:2019 Sample Testing (Sr 75-77)
    {"sr": 75, "vendor_name": "CSIR-CRRI LAB",
     "equipment": "BIS IS 15462:2019 PMB-40 Sample Testing (12 parameters)",
     "category": "F_TESTING_CERTIFICATION",
     "capacity": "Monthly samples", "price_lac": 0.50, "delivery_weeks": 0, "warranty_months": 0,
     "city": "New Delhi", "email": "lab@crri.res.in",
     "contact": "crri.res.in | NABL accredited"},

    {"sr": 76, "vendor_name": "ARBRO PHARMACEUTICALS (Lab Wing)",
     "equipment": "BIS IS 15462:2019 PMB-40 Sample Testing", "category": "F_TESTING_CERTIFICATION",
     "capacity": "Monthly samples", "price_lac": 0.45, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Delhi", "email": "lab@arbro.com",
     "contact": "arbro.com | NABL accredited"},

    {"sr": 77, "vendor_name": "SHRIRAM INSTITUTE FOR INDUSTRIAL RESEARCH",
     "equipment": "BIS IS 15462:2019 PMB-40 Testing", "category": "F_TESTING_CERTIFICATION",
     "capacity": "Monthly samples", "price_lac": 0.50, "delivery_weeks": 0, "warranty_months": 0,
     "city": "Delhi", "email": "lab@shriraminstitute.org",
     "contact": "shriraminstitute.org | NABL"},

    # F.02 Puro.earth Biochar Carbon Credit Verifiers (Sr 78-80)
    {"sr": 78, "vendor_name": "DNV (Det Norske Veritas India)",
     "equipment": "Puro.earth Biochar Carbon Credit Verification + CO2 MRV",
     "category": "F_TESTING_CERTIFICATION",
     "capacity": "Annual verification", "price_lac": 4.0, "delivery_weeks": 8, "warranty_months": 0,
     "city": "Mumbai", "email": "india@dnv.com",
     "contact": "dnv.com | Puro.earth verifier"},

    {"sr": 79, "vendor_name": "SCS GLOBAL SERVICES (India Rep)",
     "equipment": "Puro.earth Biochar Verification — Alternative", "category": "F_TESTING_CERTIFICATION",
     "capacity": "Annual verification", "price_lac": 3.5, "delivery_weeks": 8, "warranty_months": 0,
     "city": "Delhi", "email": "india@scsglobalservices.com",
     "contact": "scsglobalservices.com"},

    {"sr": 80, "vendor_name": "EARTHOOD SERVICES",
     "equipment": "Puro.earth / Gold Standard Biochar Verification", "category": "F_TESTING_CERTIFICATION",
     "capacity": "Annual verification", "price_lac": 2.5, "delivery_weeks": 6, "warranty_months": 0,
     "city": "Gurugram", "email": "info@earthood.in",
     "contact": "earthood.in | Gurugram"},
]


# Map category labels for display
CATEGORY_LABEL = {
    "A_PLANT_MACHINERY":      "A — Plant & Machinery",
    "B_RAW_MATERIAL":         "B — Raw Material Suppliers",
    "C_CIVIL_LOGISTICS":      "C — Civil, Utilities & Logistics",
    "D_APPROVALS":            "D — Approvals & Consultants",
    "E_FINANCE_AUDIT":        "E — Finance, Audit & Banking",
    "F_TESTING_CERTIFICATION":"F — Testing & Certification",
}


def run_seed():
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0
    updated = 0
    skipped = 0

    with get_connection() as conn:
        for v in VENDORS:
            existing = conn.execute(
                "SELECT id FROM vendor_quotes WHERE vendor_name=? AND equipment=?",
                (v["vendor_name"], v["equipment"])
            ).fetchone()

            if existing:
                # Update category/email/city for existing records
                conn.execute("""
                    UPDATE vendor_quotes
                    SET category=?, email=?, city=?, source=?
                    WHERE id=?
                """, (v.get("category",""), v.get("email",""),
                      v.get("city",""), "RFQ-Apr2026", existing["id"]))
                updated += 1
                continue

            conn.execute("""
                INSERT INTO vendor_quotes
                (vendor_name, equipment, capacity, price_lac, delivery_weeks,
                 warranty_months, contact, source, created_at, category, email, city, rfq_status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                v["vendor_name"], v["equipment"], v["capacity"],
                v["price_lac"], v["delivery_weeks"], v["warranty_months"],
                v.get("contact",""), "RFQ-Apr2026", now_str,
                v.get("category",""), v.get("email",""), v.get("city",""), "TO_SEND"
            ))
            inserted += 1
        conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM vendor_quotes").fetchone()[0] if False else inserted + updated
    print(f"Inserted: {inserted} new vendors")
    print(f"Updated:  {updated} existing vendors (category/email/city)")
    print(f"Total vendors in DB: {inserted + updated}")


if __name__ == "__main__":
    run_seed()
