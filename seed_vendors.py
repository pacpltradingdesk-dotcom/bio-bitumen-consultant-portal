"""
Seed vendor database from Project at Bhadurgade vendor enquiry files.
Run: python seed_vendors.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_connection
from datetime import datetime, timezone, timedelta

init_db()
IST = timezone(timedelta(hours=5, minutes=30))

VENDORS = [
    # ── A: PLANT & MACHINERY ─────────────────────────────────────────
    # Pyrolysis Reactors
    {"vendor_name": "BIOMAX FUEL TECH", "equipment": "Pyrolysis Reactor 5 MT Batch (SS316)",
     "capacity": "5 TPD", "price_lac": 85.0, "delivery_weeks": 20, "warranty_months": 24,
     "contact": "Bangalore | biomaxfueltech.com", "source": "RFQ-Apr2026"},

    {"vendor_name": "PRAJ BIOMOBILITY", "equipment": "Pyrolysis Reactor 5 MT Batch (SS316)",
     "capacity": "5 TPD", "price_lac": 95.0, "delivery_weeks": 24, "warranty_months": 24,
     "contact": "Pune | praj.net", "source": "RFQ-Apr2026"},

    {"vendor_name": "KIS GREEN ENERGY", "equipment": "Pyrolysis Reactor 5 MT Batch (SS316)",
     "capacity": "5 TPD", "price_lac": 78.0, "delivery_weeks": 18, "warranty_months": 18,
     "contact": "Ahmedabad", "source": "RFQ-Apr2026"},

    # Pre-processing / Husk Line
    {"vendor_name": "TECHNO DESIGNS", "equipment": "Rice Husk Processing Line (Shredder+Dryer+Pelletizer)",
     "capacity": "5 TPD", "price_lac": 35.0, "delivery_weeks": 14, "warranty_months": 18,
     "contact": "Delhi", "source": "RFQ-Apr2026"},

    {"vendor_name": "SWAN ENVIRONMENTAL", "equipment": "Biomass Processing Line (Shredder+Dryer)",
     "capacity": "5 TPD", "price_lac": 32.0, "delivery_weeks": 12, "warranty_months": 18,
     "contact": "Mumbai", "source": "RFQ-Apr2026"},

    {"vendor_name": "SPRAYING SYSTEMS INDIA", "equipment": "Rice Husk Processing Line",
     "capacity": "5 TPD", "price_lac": 38.0, "delivery_weeks": 16, "warranty_months": 18,
     "contact": "Bangalore", "source": "RFQ-Apr2026"},

    # Condensers
    {"vendor_name": "THERMOPAC ENGINEERS", "equipment": "Shell & Tube Condenser for Bio-Oil Recovery",
     "capacity": "5 TPD", "price_lac": 8.5, "delivery_weeks": 10, "warranty_months": 18,
     "contact": "Mumbai | thermopac.in", "source": "RFQ-Apr2026"},

    {"vendor_name": "THERMAX LTD", "equipment": "Shell & Tube Heat Exchanger / Condenser",
     "capacity": "5 TPD", "price_lac": 12.0, "delivery_weeks": 12, "warranty_months": 24,
     "contact": "Pune | thermax.com", "source": "RFQ-Apr2026"},

    {"vendor_name": "ALFA LAVAL INDIA", "equipment": "Plate Heat Exchanger / Condenser",
     "capacity": "5 TPD", "price_lac": 14.0, "delivery_weeks": 14, "warranty_months": 24,
     "contact": "Mumbai | alfalaval.com", "source": "RFQ-Apr2026"},

    # Thin Film Evaporators
    {"vendor_name": "SUMIT ENGINEERING", "equipment": "Thin Film Evaporator (TFE) for Bio-Oil Refining",
     "capacity": "5 TPD", "price_lac": 22.0, "delivery_weeks": 16, "warranty_months": 18,
     "contact": "Vadodara", "source": "RFQ-Apr2026"},

    {"vendor_name": "CHEM PROCESS SYSTEMS", "equipment": "Thin Film Evaporator (TFE)",
     "capacity": "5 TPD", "price_lac": 25.0, "delivery_weeks": 18, "warranty_months": 24,
     "contact": "Mumbai", "source": "RFQ-Apr2026"},

    {"vendor_name": "POPE SCIENTIFIC (India Agent)", "equipment": "Thin Film Evaporator (TFE)",
     "capacity": "5 TPD", "price_lac": 32.0, "delivery_weeks": 24, "warranty_months": 24,
     "contact": "Mumbai", "source": "RFQ-Apr2026"},

    # Colloid Mills
    {"vendor_name": "FRYMAKORUMA INDIA", "equipment": "Colloid Mill for Bitumen Blending",
     "capacity": "5 TPD", "price_lac": 9.5, "delivery_weeks": 12, "warranty_months": 18,
     "contact": "Mumbai", "source": "RFQ-Apr2026"},

    {"vendor_name": "AHUJA GROUP", "equipment": "High Shear Colloid Mill / Mixer",
     "capacity": "5 TPD", "price_lac": 7.0, "delivery_weeks": 10, "warranty_months": 18,
     "contact": "Delhi", "source": "RFQ-Apr2026"},

    {"vendor_name": "SPARX ENGINEERS", "equipment": "Colloid Mill / Inline Homogenizer",
     "capacity": "5 TPD", "price_lac": 8.0, "delivery_weeks": 10, "warranty_months": 18,
     "contact": "Ahmedabad", "source": "RFQ-Apr2026"},

    # VG10 Bitumen Tanks
    {"vendor_name": "THERMOPAC ENGINEERS", "equipment": "VG10 Bitumen Storage Tank (Insulated, Heated)",
     "capacity": "50 KL", "price_lac": 6.5, "delivery_weeks": 8, "warranty_months": 18,
     "contact": "Mumbai | thermopac.in", "source": "RFQ-Apr2026"},

    {"vendor_name": "RAY ENGINEERING", "equipment": "VG10 Hot Bitumen Storage Tank",
     "capacity": "50 KL", "price_lac": 5.8, "delivery_weeks": 8, "warranty_months": 12,
     "contact": "Kolkata", "source": "RFQ-Apr2026"},

    {"vendor_name": "HEATEX INDIA", "equipment": "Insulated Bitumen Storage Tank",
     "capacity": "50 KL", "price_lac": 6.0, "delivery_weeks": 10, "warranty_months": 18,
     "contact": "Chennai", "source": "RFQ-Apr2026"},

    # PMB Tanks
    {"vendor_name": "SSVM PROJECTS", "equipment": "PMB-40 Storage Tank (Insulated 160C)",
     "capacity": "30 KL", "price_lac": 7.5, "delivery_weeks": 10, "warranty_months": 18,
     "contact": "Mumbai", "source": "RFQ-Apr2026"},

    {"vendor_name": "SIGMA THERMAL INDIA", "equipment": "PMB Storage Tank with Heating Coils",
     "capacity": "30 KL", "price_lac": 8.5, "delivery_weeks": 12, "warranty_months": 18,
     "contact": "Pune", "source": "RFQ-Apr2026"},

    {"vendor_name": "VAIBHAV TANK & VESSELS", "equipment": "PMB-40 Insulated Storage Tank",
     "capacity": "30 KL", "price_lac": 6.8, "delivery_weeks": 8, "warranty_months": 12,
     "contact": "Ahmedabad", "source": "RFQ-Apr2026"},

    # DG Sets
    {"vendor_name": "KIRLOSKAR OIL ENGINES", "equipment": "Diesel Generator Set 80 kVA (CPCB-IV+)",
     "capacity": "80 kVA", "price_lac": 9.5, "delivery_weeks": 8, "warranty_months": 24,
     "contact": "Pune | kirloskar.com", "source": "RFQ-Apr2026"},

    {"vendor_name": "CUMMINS INDIA", "equipment": "Diesel Generator Set 82.5 kVA (CPCB-IV+)",
     "capacity": "82.5 kVA", "price_lac": 10.5, "delivery_weeks": 8, "warranty_months": 24,
     "contact": "Pune | cummins.in", "source": "RFQ-Apr2026"},

    {"vendor_name": "MAHINDRA POWEROL", "equipment": "Diesel Generator Set 82.5 kVA",
     "capacity": "82.5 kVA", "price_lac": 9.8, "delivery_weeks": 6, "warranty_months": 24,
     "contact": "Mumbai | mahindra.com", "source": "RFQ-Apr2026"},

    # Transformers
    {"vendor_name": "CG POWER & INDUSTRIAL", "equipment": "Distribution Transformer 250 kVA 11kV/415V",
     "capacity": "250 kVA", "price_lac": 4.5, "delivery_weeks": 10, "warranty_months": 60,
     "contact": "Mumbai | cgpower.com", "source": "RFQ-Apr2026"},

    {"vendor_name": "VIJAI ELECTRICALS", "equipment": "Transformer 250 kVA 11kV/415V CRGO",
     "capacity": "250 kVA", "price_lac": 4.2, "delivery_weeks": 10, "warranty_months": 60,
     "contact": "Hyderabad", "source": "RFQ-Apr2026"},

    {"vendor_name": "RAYCHEM RPG", "equipment": "Transformer & HT Switchgear Package",
     "capacity": "250 kVA", "price_lac": 5.5, "delivery_weeks": 12, "warranty_months": 60,
     "contact": "Mumbai | raychemindia.com", "source": "RFQ-Apr2026"},

    # MCC / PLC
    {"vendor_name": "ROCKWELL AUTOMATION (via L&T SI)", "equipment": "MCC Panel + Allen Bradley PLC/SCADA",
     "capacity": "5 TPD", "price_lac": 18.0, "delivery_weeks": 16, "warranty_months": 24,
     "contact": "Pune | rockwellautomation.com", "source": "RFQ-Apr2026"},

    {"vendor_name": "SIEMENS INDIA", "equipment": "MCC Panel + Siemens S7 PLC + WinCC SCADA",
     "capacity": "5 TPD", "price_lac": 20.0, "delivery_weeks": 16, "warranty_months": 36,
     "contact": "Mumbai | siemens.co.in", "source": "RFQ-Apr2026"},

    {"vendor_name": "MITSUBISHI ELECTRIC INDIA", "equipment": "MCC Panel + MELSEC PLC",
     "capacity": "5 TPD", "price_lac": 17.0, "delivery_weeks": 14, "warranty_months": 24,
     "contact": "Pune | mitsubishielectric.co.in", "source": "RFQ-Apr2026"},

    # Weighbridges
    {"vendor_name": "SANSUI ELECTRONICS", "equipment": "Pitless Weighbridge 60 MT Electronic",
     "capacity": "60 MT", "price_lac": 6.0, "delivery_weeks": 8, "warranty_months": 24,
     "contact": "Delhi", "source": "RFQ-Apr2026"},

    {"vendor_name": "ESSAE TERAOKA", "equipment": "Pit-type Weighbridge 60 MT (ESSAE)",
     "capacity": "60 MT", "price_lac": 6.5, "delivery_weeks": 8, "warranty_months": 24,
     "contact": "Bangalore | essae.in", "source": "RFQ-Apr2026"},

    {"vendor_name": "ADEPT SCALES", "equipment": "Pitless Weighbridge 60 MT with Software",
     "capacity": "60 MT", "price_lac": 5.8, "delivery_weeks": 6, "warranty_months": 18,
     "contact": "Delhi", "source": "RFQ-Apr2026"},

    # Fire Safety
    {"vendor_name": "CEASEFIRE INDUSTRIES", "equipment": "Fire Safety System (Hydrants+Extinguishers+Hose)",
     "capacity": "5 TPD Plant", "price_lac": 8.0, "delivery_weeks": 6, "warranty_months": 12,
     "contact": "Delhi | ceasefire.in", "source": "RFQ-Apr2026"},

    {"vendor_name": "MINIMAX FIRE SAFETY", "equipment": "Fire Hydrant + Foam System (NFPA 15)",
     "capacity": "5 TPD Plant", "price_lac": 9.5, "delivery_weeks": 8, "warranty_months": 12,
     "contact": "Mumbai | minimax.in", "source": "RFQ-Apr2026"},

    {"vendor_name": "NEWAGE FIRE", "equipment": "Fire Hydrant System + Portable Extinguishers",
     "capacity": "5 TPD Plant", "price_lac": 7.5, "delivery_weeks": 6, "warranty_months": 12,
     "contact": "Hyderabad", "source": "RFQ-Apr2026"},

    # QC Laboratory
    {"vendor_name": "PRESTO GROUP", "equipment": "QC Lab Equipment Package (Bitumen Testing)",
     "capacity": "Full Lab", "price_lac": 12.0, "delivery_weeks": 8, "warranty_months": 12,
     "contact": "Faridabad | prestogroup.com", "source": "RFQ-Apr2026"},

    {"vendor_name": "LABOMED INC (India)", "equipment": "Laboratory Instruments (Viscometer+Penetrometer)",
     "capacity": "Full Lab", "price_lac": 10.5, "delivery_weeks": 10, "warranty_months": 12,
     "contact": "Mumbai", "source": "RFQ-Apr2026"},

    {"vendor_name": "AIMIL LTD", "equipment": "QC Lab Package (IS:73 Testing Equipment)",
     "capacity": "Full Lab", "price_lac": 11.0, "delivery_weeks": 8, "warranty_months": 12,
     "contact": "Delhi | aimil.com", "source": "RFQ-Apr2026"},

    # ── B: RAW MATERIAL SUPPLIERS ───────────────────────────────────
    {"vendor_name": "HARYANA BASMATI RICE MILLS", "equipment": "Rice Husk Supply (Loose)",
     "capacity": "500 MT/month", "price_lac": 0.06, "delivery_weeks": 0, "warranty_months": 0,
     "contact": "Karnal, Haryana | Rs 600-800/MT farm gate", "source": "RFQ-Apr2026"},

    {"vendor_name": "KISAN RICE INDUSTRIES", "equipment": "Rice Husk Baled Supply",
     "capacity": "300 MT/month", "price_lac": 0.12, "delivery_weeks": 0, "warranty_months": 0,
     "contact": "Ambala, Haryana | Rs 1200-1500/MT baled", "source": "RFQ-Apr2026"},

    {"vendor_name": "SHIV SHAKTI AGRO", "equipment": "Rice Husk + Wheat Straw Supply",
     "capacity": "400 MT/month", "price_lac": 0.08, "delivery_weeks": 0, "warranty_months": 0,
     "contact": "Panipat, Haryana | Rs 800-1200/MT", "source": "RFQ-Apr2026"},

    {"vendor_name": "IOCL PANIPAT REFINERY", "equipment": "VG-10 Base Bitumen Supply",
     "capacity": "Bulk tanker", "price_lac": 4.575, "delivery_weeks": 1, "warranty_months": 0,
     "contact": "Panipat, Haryana | Rs 45,750/MT ex-refinery", "source": "RFQ-Apr2026"},

    {"vendor_name": "HPCL PANIPAT TERMINAL", "equipment": "VG-10 Base Bitumen Supply (HPCL)",
     "capacity": "Bulk tanker", "price_lac": 4.60, "delivery_weeks": 1, "warranty_months": 0,
     "contact": "Panipat Terminal | Rs 46,000/MT ex-terminal", "source": "RFQ-Apr2026"},

    {"vendor_name": "RELIANCE SIBUR ELASTOMERS", "equipment": "SBS Polymer for PMB-40",
     "capacity": "5 MT/month", "price_lac": 1.85, "delivery_weeks": 2, "warranty_months": 6,
     "contact": "Vadodara | Rs 185,000/MT", "source": "RFQ-Apr2026"},

    {"vendor_name": "LG CHEM INDIA", "equipment": "SBS Rubber Polymer (LG Chem KRATON)",
     "capacity": "5 MT/month", "price_lac": 1.90, "delivery_weeks": 3, "warranty_months": 6,
     "contact": "Mumbai | Rs 190,000/MT", "source": "RFQ-Apr2026"},

    # ── C: CIVIL, UTILITIES, LOGISTICS ─────────────────────────────
    {"vendor_name": "TATA BLUESCOPE STEEL", "equipment": "Pre-Engineered Building (PEB) Structure",
     "capacity": "1500 sqm", "price_lac": 45.0, "delivery_weeks": 16, "warranty_months": 120,
     "contact": "Mumbai | tatabluescope.com", "source": "RFQ-Apr2026"},

    {"vendor_name": "KIRBY BUILDING SYSTEMS", "equipment": "Pre-Engineered Steel Building",
     "capacity": "1500 sqm", "price_lac": 42.0, "delivery_weeks": 14, "warranty_months": 120,
     "contact": "Hyderabad | kirbybuildingsystems.in", "source": "RFQ-Apr2026"},

    {"vendor_name": "GATI KINTETSU EXPRESS", "equipment": "VG-10 Bitumen Tanker Transport",
     "capacity": "Per trip", "price_lac": 0.35, "delivery_weeks": 0, "warranty_months": 0,
     "contact": "Haryana | Rs 650/MT Panipat-Bahadurgarh", "source": "RFQ-Apr2026"},

    {"vendor_name": "DRS LOGISTICS", "equipment": "Bitumen + Finished Product Logistics",
     "capacity": "Per trip", "price_lac": 0.30, "delivery_weeks": 0, "warranty_months": 0,
     "contact": "Delhi NCR", "source": "RFQ-Apr2026"},

    # ── D: APPROVALS & CONSULTANTS ──────────────────────────────────
    {"vendor_name": "PERFACT ENVIRO SOLUTIONS", "equipment": "Environmental Consultant (CTE/CTO/EIA)",
     "capacity": "Full Service", "price_lac": 3.5, "delivery_weeks": 12, "warranty_months": 0,
     "contact": "Faridabad, Haryana | HSPCB approved", "source": "RFQ-Apr2026"},

    {"vendor_name": "NEWAGE FIRE SAFETY CONSULTANTS", "equipment": "Fire NOC Consultant",
     "capacity": "Full Service", "price_lac": 1.5, "delivery_weeks": 8, "warranty_months": 0,
     "contact": "Gurugram | Haryana Fire Dept approved", "source": "RFQ-Apr2026"},

    {"vendor_name": "CSIR-CRRI", "equipment": "Bio-Bitumen Technology License + Testing",
     "capacity": "5 TPD", "price_lac": 12.0, "delivery_weeks": 0, "warranty_months": 0,
     "contact": "New Delhi | crri.res.in | Dr Ambika Behl", "source": "RFQ-Apr2026"},

    # ── F: TESTING & CERTIFICATION ──────────────────────────────────
    {"vendor_name": "BIS (Bureau of Indian Standards)", "equipment": "IS:73 Product Certification (PMB-40)",
     "capacity": "Certification", "price_lac": 2.5, "delivery_weeks": 16, "warranty_months": 0,
     "contact": "New Delhi | bis.gov.in", "source": "RFQ-Apr2026"},
]


def run_seed():
    now = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0
    skipped = 0

    with get_connection() as conn:
        for v in VENDORS:
            # Skip if already exists
            existing = conn.execute(
                "SELECT id FROM vendor_quotes WHERE vendor_name=? AND equipment=?",
                (v["vendor_name"], v["equipment"])
            ).fetchone()
            if existing:
                skipped += 1
                continue

            conn.execute("""
                INSERT INTO vendor_quotes
                (vendor_name, equipment, capacity, price_lac, delivery_weeks,
                 warranty_months, contact, source, created_at)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                v["vendor_name"], v["equipment"], v["capacity"],
                v["price_lac"], v["delivery_weeks"], v["warranty_months"],
                v["contact"], v["source"], now
            ))
            inserted += 1

    print(f"Done! Inserted: {inserted} vendors | Skipped (existing): {skipped}")
    print(f"Total vendors in DB: {inserted + skipped}")


if __name__ == "__main__":
    run_seed()
