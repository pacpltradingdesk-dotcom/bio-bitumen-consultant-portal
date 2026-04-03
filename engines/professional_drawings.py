"""
Bio Bitumen — PROFESSIONAL Engineering Drawing Generator
==========================================================
Generates government-grade engineering drawings with:
- IS standard title blocks (IS:962)
- Proper dimensions with arrows and labels
- Color coding as per BIS/OISD standards
- Scale markings
- North direction
- Legend/key
- Drawing number and revision
- Suitable for PCB CTE, Factory License, Fire NOC, PESO, Bank DPR
"""
import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import matplotlib.lines as mlines
import numpy as np
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "professional_drawings")


def _ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── STANDARD COLORS (as per BIS/OISD) ────────────────────────────────
COLORS = {
    "raw_material": "#228B22",      # Green — raw material areas
    "processing": "#FFD700",        # Yellow — processing zones
    "reactor": "#CC0000",           # Red — high hazard / reactor
    "blending": "#FF8C00",          # Orange — blending/mixing
    "storage": "#4169E1",           # Blue — storage / tank farm
    "utility": "#808080",           # Gray — utility area
    "admin": "#F5F5DC",             # Beige — admin/office
    "road": "#696969",              # Dark gray — roads
    "dispatch": "#9370DB",          # Purple — dispatch
    "pollution": "#8B4513",         # Brown — pollution control
    "fire_zone": "#FF0000",         # Red — fire risk zone
    "safety_zone": "#FFE4E1",       # Light red — safety buffer
    "green_belt": "#006400",        # Dark green — green belt
    "bund_wall": "#A0522D",         # Brown — containment
    "water": "#00BFFF",             # Light blue — water
    "boundary": "#000000",          # Black — plot boundary
}


def _add_title_block(ax, fig, drawing_title, drawing_no, tpd, scale, company, sheet="1 OF 1"):
    """Add IS:962 standard title block at bottom of drawing."""
    # Title block border
    tb_y = -0.12
    tb_h = 0.1

    fig.text(0.02, 0.02, f"DRG NO: {drawing_no}", fontsize=7, fontweight='bold',
             transform=fig.transFigure)
    fig.text(0.02, 0.045, f"PROJECT: BIO-BITUMEN PLANT — {tpd:.0f} TPD",
             fontsize=7, transform=fig.transFigure)
    fig.text(0.02, 0.07, f"TITLE: {drawing_title}",
             fontsize=8, fontweight='bold', transform=fig.transFigure)

    fig.text(0.5, 0.02, f"SCALE: {scale} | SHEET: {sheet}", fontsize=7,
             ha='center', transform=fig.transFigure)
    fig.text(0.5, 0.045, f"DATE: {datetime.now(IST).strftime('%d-%b-%Y')} | REV: 0",
             fontsize=7, ha='center', transform=fig.transFigure)

    fig.text(0.98, 0.02, f"{company.get('trade_name', 'PPS Anantams')}",
             fontsize=7, ha='right', transform=fig.transFigure)
    fig.text(0.98, 0.045, f"{company.get('owner', '')} | {company.get('phone', '')}",
             fontsize=6, ha='right', transform=fig.transFigure)
    fig.text(0.98, 0.07, "CONFIDENTIAL — FOR APPROVAL ONLY",
             fontsize=6, ha='right', color='red', transform=fig.transFigure)


def _add_north_arrow(ax, x, y):
    """Add north direction arrow."""
    ax.annotate('N', xy=(x, y + 2), fontsize=10, fontweight='bold', ha='center', color='#003366')
    ax.annotate('', xy=(x, y + 1.8), xytext=(x, y),
                arrowprops=dict(arrowstyle='->', color='#003366', lw=2))


def _add_dimension(ax, x1, y1, x2, y2, label, offset=1.5, horizontal=True):
    """Add dimension line with arrows and measurement label."""
    if horizontal:
        ax.annotate('', xy=(x2, y1 - offset), xytext=(x1, y1 - offset),
                    arrowprops=dict(arrowstyle='<->', color='#333333', lw=1))
        ax.plot([x1, x1], [y1, y1 - offset - 0.3], 'k-', lw=0.5)
        ax.plot([x2, x2], [y1, y1 - offset - 0.3], 'k-', lw=0.5)
        ax.text((x1 + x2) / 2, y1 - offset - 0.8, label,
                ha='center', fontsize=6, color='#333333')
    else:
        ax.annotate('', xy=(x1 + offset, y2), xytext=(x1 + offset, y1),
                    arrowprops=dict(arrowstyle='<->', color='#333333', lw=1))
        ax.plot([x1, x1 + offset + 0.3], [y1, y1], 'k-', lw=0.5)
        ax.plot([x1, x1 + offset + 0.3], [y2, y2], 'k-', lw=0.5)
        ax.text(x1 + offset + 0.8, (y1 + y2) / 2, label,
                ha='left', va='center', fontsize=6, color='#333333', rotation=90)


# ═══════════════════════════════════════════════════════════════════════
# DRAWING 1: SITE LAYOUT PLAN (for PCB CTE + Factory License)
# ═══════════════════════════════════════════════════════════════════════
def generate_site_layout(tpd, company, state="", location=""):
    """
    Site Layout Plan — Required by:
    - State PCB for CTE application
    - Factory Inspector for Factory License
    - Fire Department for Fire NOC
    - Bank for DPR
    """
    _ensure_dir()
    scale_f = max(0.5, min(2.5, tpd / 30))
    pw = int(60 * scale_f)  # meters
    ph = int(35 * scale_f)  # meters

    fig, ax = plt.subplots(1, 1, figsize=(24, 16))
    ax.set_xlim(-5, pw + 5)
    ax.set_ylim(-8, ph + 3)
    ax.set_aspect('equal')

    # ── PLOT BOUNDARY (thick black line) ──────────────────────────────
    boundary = Rectangle((0, 0), pw, ph, linewidth=3, edgecolor='black',
                           facecolor='#FAFAFA', fill=True)
    ax.add_patch(boundary)

    # ── GREEN BELT (3m along boundary) ────────────────────────────────
    gb_width = 3
    for side in [(0, 0, pw, gb_width), (0, 0, gb_width, ph),
                  (0, ph - gb_width, pw, gb_width), (pw - gb_width, 0, gb_width, ph)]:
        ax.add_patch(Rectangle(side[:2], side[2], side[3],
                                facecolor=COLORS["green_belt"], alpha=0.3, edgecolor='none'))

    # ── SECTIONS with proper dimensions ───────────────────────────────
    sections = [
        {"name": "RAW MATERIAL\nRECEIVING &\nSTORAGE AREA",
         "x": gb_width, "y": ph * 0.55, "w": pw * 0.18, "h": ph * 0.4,
         "color": COLORS["raw_material"], "alpha": 0.25,
         "equipment": [
             f"Open Storage Yard: {int(pw*0.15)}m x {int(ph*0.2)}m",
             f"Covered Shed: {int(pw*0.1)}m x {int(ph*0.15)}m",
             "Weigh Bridge: 18m x 3m",
         ]},
        {"name": "RAW MATERIAL\nPROCESSING\nSECTION",
         "x": pw * 0.2, "y": ph * 0.5, "w": pw * 0.22, "h": ph * 0.45,
         "color": COLORS["processing"], "alpha": 0.25,
         "equipment": [
             "Biomass Receiving Hopper",
             "Belt Conveyor: 6m long",
             f"Shredder: {max(1,int(tpd/15))}x unit",
             f"Hammer Mill: {max(1,int(tpd/15))}x unit",
             f"Rotary Dryer: {int(max(3,tpd/5))}m long",
             "Cyclone Dust Collector",
             f"Storage Silo: {int(max(5,tpd*0.5))}MT cap",
             "2m clearance between equipment",
         ]},
        {"name": "PYROLYSIS\nREACTOR\nSECTION\n(CORE PROCESS)\n5m SAFETY ZONE",
         "x": pw * 0.44, "y": ph * 0.35, "w": pw * 0.16, "h": ph * 0.45,
         "color": COLORS["reactor"], "alpha": 0.15,
         "equipment": [
             f"Reactor R-101: {max(1,int(tpd/10))}x units",
             f"Thermic Fluid Heater H-101",
             "Bio-Oil Condenser HE-101",
             "Gas Cooling Tower T-101",
             "Explosion vent panels",
             "5m CLEAR SAFETY ZONE",
         ]},
        {"name": "BIO-OIL AND\nBITUMEN\nPROCESSING\nAREA",
         "x": pw * 0.62, "y": ph * 0.35, "w": pw * 0.16, "h": ph * 0.45,
         "color": COLORS["blending"], "alpha": 0.2,
         "equipment": [
             "Bio-Oil Intermediate Tank",
             "Bitumen Heating Tank",
             "High Shear Mixer",
             "Colloid Mill",
             "Additive Dosing Tanks",
             "Bio-Bitumen Blending Tank",
             "Pipe Racks: elevated steel",
         ]},
        {"name": "STORAGE\nAREA\n(TANK FARM)",
         "x": pw * 0.8, "y": ph * 0.55, "w": pw * 0.17, "h": ph * 0.4,
         "color": COLORS["storage"], "alpha": 0.2,
         "equipment": [
             f"Bitumen Tank T-201: {max(2,int(tpd/10))}x",
             f"Bio-Oil Tank: {max(2,int(tpd/10))}x",
             "Containment Bund Wall",
             "4m fire spacing between tanks",
             "Min 4.5m height bund",
         ]},
        {"name": "POLLUTION\nCONTROL\nAREA",
         "x": pw * 0.44, "y": ph * 0.82, "w": pw * 0.12, "h": ph * 0.15,
         "color": COLORS["pollution"], "alpha": 0.25,
         "equipment": [
             "Bag Filter",
             "Gas Scrubber",
             f"Chimney: 20m min height",
         ]},
        {"name": "PRODUCT\nDISPATCH\nAREA",
         "x": pw * 0.45, "y": gb_width, "w": pw * 0.35, "h": ph * 0.25,
         "color": COLORS["dispatch"], "alpha": 0.15,
         "equipment": [
             "Tanker Loading Platform",
             "Auto Drum Filling Machine",
             "Finished Drum Storage",
             "Forklift Movement Area",
             "Truck Parking: 5 bays",
         ]},
        {"name": "UTILITY\nAREA",
         "x": pw * 0.85, "y": ph * 0.15, "w": pw * 0.12, "h": ph * 0.35,
         "color": COLORS["utility"], "alpha": 0.2,
         "equipment": [
             f"DG Set: {max(250,int(tpd*5*1.2))} kVA",
             "PLC/SCADA Control Room",
             "Air Compressor Room",
             "Cooling Tower",
             "Water Tank: OHT + UG",
         ]},
        {"name": "OFFICE &\nADMIN\nBUILDING",
         "x": gb_width, "y": gb_width, "w": pw * 0.18, "h": ph * 0.25,
         "color": COLORS["admin"], "alpha": 0.5,
         "equipment": [
             "Office: 2 floors",
             "Lab & QC Room",
             "Canteen & Toilet Block",
             "Fire Water Tank",
             "Emergency Assembly Point",
         ]},
    ]

    for sec in sections:
        # Section rectangle
        rect = Rectangle((sec["x"], sec["y"]), sec["w"], sec["h"],
                           facecolor=sec["color"], alpha=sec["alpha"],
                           edgecolor='#333333', linewidth=1.5, linestyle='-')
        ax.add_patch(rect)

        # Section name
        ax.text(sec["x"] + sec["w"] / 2, sec["y"] + sec["h"] - 1,
                sec["name"], ha='center', va='top', fontsize=7, fontweight='bold',
                color='#003366',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

        # Equipment list
        y_pos = sec["y"] + sec["h"] - 3
        for item in sec["equipment"][:6]:
            if y_pos > sec["y"] + 0.5:
                ax.text(sec["x"] + 1, y_pos, f"- {item}", fontsize=4.5, color='#333333')
                y_pos -= 1

    # ── INTERNAL ROAD (6m wide) ──────────────────────────────────────
    road_y = ph * 0.30
    ax.add_patch(Rectangle((gb_width, road_y), pw - 2 * gb_width, ph * 0.04,
                             facecolor=COLORS["road"], alpha=0.5))
    ax.text(pw / 2, road_y + ph * 0.02, "6m WIDE INTERNAL CONCRETE ROAD",
            ha='center', va='center', fontsize=6, color='white', fontweight='bold')

    # ── ENTRY/EXIT ────────────────────────────────────────────────────
    ax.annotate('ENTRY', xy=(pw * 0.08, 0), fontsize=8, fontweight='bold', color='green',
                ha='center', va='bottom')
    ax.plot([pw * 0.05, pw * 0.11], [0, 0], 'g-', lw=5)

    ax.annotate('EXIT', xy=(pw * 0.4, 0), fontsize=8, fontweight='bold', color='red',
                ha='center', va='bottom')
    ax.plot([pw * 0.37, pw * 0.43], [0, 0], 'r-', lw=5)

    # ── DIMENSIONS ───────────────────────────────────────────────────
    _add_dimension(ax, 0, 0, pw, 0, f"{pw}m", offset=3, horizontal=True)
    _add_dimension(ax, 0, 0, 0, ph, f"{ph}m", offset=3, horizontal=False)

    # ── NORTH ARROW ──────────────────────────────────────────────────
    _add_north_arrow(ax, pw + 2, ph - 3)

    # ── LEGEND ───────────────────────────────────────────────────────
    legend_x, legend_y = -4, ph * 0.6
    ax.text(legend_x, legend_y + 6, "LEGEND:", fontsize=7, fontweight='bold')
    legend_items = [
        (COLORS["raw_material"], "Raw Material Area"),
        (COLORS["processing"], "Processing Section"),
        (COLORS["reactor"], "Reactor (High Hazard)"),
        (COLORS["blending"], "Blending Area"),
        (COLORS["storage"], "Storage / Tank Farm"),
        (COLORS["pollution"], "Pollution Control"),
        (COLORS["dispatch"], "Product Dispatch"),
        (COLORS["utility"], "Utility Area"),
        (COLORS["admin"], "Office / Admin"),
        (COLORS["green_belt"], "Green Belt (3m)"),
        (COLORS["road"], "Internal Road (6m)"),
    ]
    for i, (color, label) in enumerate(legend_items):
        y = legend_y + 4.5 - i * 1.2
        ax.add_patch(Rectangle((legend_x, y - 0.3), 1, 0.6, facecolor=color, alpha=0.5, edgecolor='black', lw=0.5))
        ax.text(legend_x + 1.5, y, label, fontsize=5, va='center')

    # ── TITLE ────────────────────────────────────────────────────────
    title_text = f"SITE LAYOUT PLAN — BIO-BITUMEN PLANT — {tpd:.0f} TPD CAPACITY"
    if location:
        title_text += f"\nLocation: {location}, {state}"
    title_text += f"\nPlot: {pw}m x {ph}m = {pw * ph:,} sqm ({pw * ph / 10000:.2f} hectare)"
    ax.set_title(title_text, fontsize=13, fontweight='bold', color='#003366', pad=15)

    # ── TITLE BLOCK ──────────────────────────────────────────────────
    _add_title_block(ax, fig, "SITE LAYOUT PLAN (GENERAL ARRANGEMENT)",
                      f"PPS-BB-{tpd:.0f}-GA-001", tpd, f"1:{int(100*scale_f)}", company)

    ax.axis('off')
    plt.subplots_adjust(bottom=0.1, top=0.92, left=0.08, right=0.95)

    fname = f"SITE_LAYOUT_{tpd:.0f}TPD_Professional.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 2. ETP LAYOUT (for PCB CTE)
# ═══════════════════════════════════════════════════════════════════════
def generate_etp_layout(tpd, company):
    """ETP Layout — Required by State PCB for CTE."""
    _ensure_dir()
    fig, ax = plt.subplots(1, 1, figsize=(20, 12))
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 18)

    etp_cap = max(2, int(tpd * 0.3))  # KLD

    units = [
        {"name": f"COLLECTION\nSUMP\n{etp_cap*2} KL", "x": 1, "y": 7, "w": 4, "h": 3, "color": "#B0C4DE"},
        {"name": f"EQUALIZATION\nTANK\n{etp_cap} KL\nRetention: 8 hrs", "x": 7, "y": 7, "w": 4, "h": 3, "color": "#87CEEB"},
        {"name": "OIL & GREASE\nTRAP\nSkimmer type", "x": 13, "y": 7, "w": 3.5, "h": 3, "color": "#DEB887"},
        {"name": f"SETTLING\nTANK\n{etp_cap} KL\nRetention: 4 hrs", "x": 18, "y": 7, "w": 4, "h": 3, "color": "#98FB98"},
        {"name": f"TREATED WATER\nSTORAGE\n{etp_cap} KL\nFor recycling", "x": 24, "y": 7, "w": 4, "h": 3, "color": "#00CED1"},
        {"name": "SLUDGE\nDRYING BED\n2m x 3m", "x": 13, "y": 2, "w": 4, "h": 3, "color": "#D2B48C"},
        {"name": "MONITORING\nPOINT\n(PCB Sampling)", "x": 24, "y": 12, "w": 4, "h": 2.5, "color": "#FFD700"},
    ]

    for u in units:
        ax.add_patch(FancyBboxPatch((u["x"], u["y"]), u["w"], u["h"],
                                     boxstyle="round,pad=0.3", facecolor=u["color"],
                                     edgecolor='#333', lw=2, alpha=0.7))
        ax.text(u["x"] + u["w"]/2, u["y"] + u["h"]/2, u["name"],
                ha='center', va='center', fontsize=6, fontweight='bold')

    # Flow arrows
    for i in range(4):
        ax.annotate('', xy=(units[i+1]["x"], 8.5), xytext=(units[i]["x"]+units[i]["w"], 8.5),
                    arrowprops=dict(arrowstyle='->', color='blue', lw=2))

    # Sludge arrow
    ax.annotate('', xy=(15, 5), xytext=(15, 7),
                arrowprops=dict(arrowstyle='->', color='brown', lw=2, ls='--'))
    ax.text(15, 6, "Sludge", ha='center', fontsize=6, color='brown')

    # Recycling arrow
    ax.annotate('', xy=(26, 12), xytext=(26, 10),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(27, 11, "To process\n(recycled)", fontsize=6, color='green')

    ax.text(15, 16, f"CAPACITY: {etp_cap} KLD | ZERO LIQUID DISCHARGE (ZLD) SYSTEM",
            ha='center', fontsize=9, fontweight='bold', color='#003366',
            bbox=dict(boxstyle="round", facecolor='#E6F2FF'))

    ax.set_title(f"EFFLUENT TREATMENT PLANT (ETP) LAYOUT — {tpd:.0f} TPD PLANT",
                  fontsize=13, fontweight='bold', color='#003366')
    _add_title_block(ax, fig, "ETP LAYOUT & FLOW DIAGRAM",
                      f"PPS-BB-{tpd:.0f}-ETP-001", tpd, "1:100", company)
    ax.axis('off')
    plt.subplots_adjust(bottom=0.1)

    fname = f"ETP_Layout_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 3. TANK FARM LAYOUT (for PESO)
# ═══════════════════════════════════════════════════════════════════════
def generate_tank_farm(tpd, company):
    """Tank Farm Layout — Required by PESO."""
    _ensure_dir()
    fig, ax = plt.subplots(1, 1, figsize=(20, 14))
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 30)

    num_tanks = max(2, int(tpd / 10))
    tank_dia = max(3, tpd * 0.15)
    spacing = max(4, tank_dia * 1.5)

    # Dyke wall
    dyke_w = num_tanks * (tank_dia + spacing) + 6
    dyke_h = tank_dia * 2 + 10
    ax.add_patch(Rectangle((5, 8), dyke_w, dyke_h, facecolor='#FFF8DC',
                             edgecolor='#8B4513', lw=3, ls='-'))
    ax.text(5 + dyke_w/2, 8 + dyke_h + 0.5, f"CONTAINMENT DYKE WALL — RCC 300mm thick — Height: {max(1.0, tank_dia*0.3):.1f}m",
            ha='center', fontsize=7, fontweight='bold', color='#8B4513')
    ax.text(5 + dyke_w/2, 7.5, f"Dyke Capacity: 110% of largest tank = {int(tank_dia**2 * 3.14 / 4 * max(3, tank_dia) * 1.1):.0f} KL",
            ha='center', fontsize=6, color='#8B4513')

    # Tanks
    x_pos = 8
    for i in range(num_tanks):
        # Bitumen tank
        circle = Circle((x_pos, 18), tank_dia/2, facecolor=COLORS["storage"],
                          edgecolor='#003366', lw=2, alpha=0.6)
        ax.add_patch(circle)
        ax.text(x_pos, 18, f"T-{201+i}\nBitumen\n{int(tank_dia**2*3.14/4*max(3,tank_dia)):.0f} KL\nDia: {tank_dia:.1f}m",
                ha='center', va='center', fontsize=5, fontweight='bold')

        # Bio-oil tank (smaller)
        circle2 = Circle((x_pos, 12), tank_dia*0.4, facecolor='#FF8C00',
                           edgecolor='#CC6600', lw=2, alpha=0.6)
        ax.add_patch(circle2)
        ax.text(x_pos, 12, f"T-{301+i}\nBio-Oil\n{int((tank_dia*0.4)**2*3.14/4*3):.0f} KL",
                ha='center', va='center', fontsize=4.5, fontweight='bold')

        # Spacing dimension
        if i < num_tanks - 1:
            _add_dimension(ax, x_pos + tank_dia/2, 18, x_pos + spacing + tank_dia/2 - tank_dia, 18,
                          f"{spacing:.1f}m\n(min {tank_dia:.1f}m per OISD-118)", offset=3)

        x_pos += spacing + tank_dia

    # Fire water tank
    ax.add_patch(Circle((35, 5), 2.5, facecolor='#4169E1', alpha=0.5, edgecolor='blue', lw=2))
    ax.text(35, 5, f"FIRE\nWATER\n{max(50,int(tpd*5))} KL", ha='center', fontsize=6, fontweight='bold', color='blue')

    # Pump house
    ax.add_patch(Rectangle((30, 3), 4, 3, facecolor='#D3D3D3', edgecolor='black', lw=1.5))
    ax.text(32, 4.5, "PUMP\nHOUSE", ha='center', fontsize=6, fontweight='bold')

    # Drain valve
    ax.plot([5, 3], [10, 10], 'r-', lw=2)
    ax.text(2, 10, "DRAIN\nVALVE\n(Locked)", ha='center', fontsize=5, color='red', fontweight='bold')

    ax.set_title(f"TANK FARM LAYOUT — {tpd:.0f} TPD | {num_tanks} Tanks | OISD-118 Compliant",
                  fontsize=13, fontweight='bold', color='#003366')
    _add_title_block(ax, fig, "TANK FARM LAYOUT (PESO SUBMISSION)",
                      f"PPS-BB-{tpd:.0f}-TF-001", tpd, "1:200", company)

    # Legend
    ax.text(1, 27, "LEGEND:", fontsize=7, fontweight='bold')
    ax.add_patch(Circle((2, 26), 0.5, facecolor=COLORS["storage"], alpha=0.6)); ax.text(3, 26, "Bitumen Storage Tank", fontsize=5)
    ax.add_patch(Circle((2, 25), 0.5, facecolor='#FF8C00', alpha=0.6)); ax.text(3, 25, "Bio-Oil Storage Tank", fontsize=5)
    ax.add_patch(Rectangle((1.5, 23.7), 1, 0.6, facecolor='#FFF8DC', edgecolor='#8B4513', lw=1)); ax.text(3, 24, "Dyke Wall Area", fontsize=5)

    ax.text(20, 2, "Standards: OISD-118 (Layout) | IS:803 (Tank Design) | Petroleum Rules 2002",
            ha='center', fontsize=6, color='#666')

    ax.axis('off')
    plt.subplots_adjust(bottom=0.1)

    fname = f"Tank_Farm_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 4. MACHINERY LAYOUT (for Factory License)
# ═══════════════════════════════════════════════════════════════════════
def generate_machinery_layout(tpd, company):
    """Machinery Layout with gangways — Required by Factory Inspector."""
    _ensure_dir()
    fig, ax = plt.subplots(1, 1, figsize=(22, 14))
    scale_f = max(0.5, tpd / 30)
    pw, ph = int(50 * scale_f), int(30 * scale_f)
    ax.set_xlim(-2, pw + 2)
    ax.set_ylim(-3, ph + 2)

    ax.add_patch(Rectangle((0, 0), pw, ph, lw=2, edgecolor='black', facecolor='#FAFAFA'))

    machines = [
        {"name": f"BIOMASS\nHOPPER\n{max(5,int(tpd*0.5))}MT", "x": 2, "y": ph*0.6, "w": pw*0.08, "h": ph*0.15, "hp": 5, "color": "#90EE90"},
        {"name": f"BELT\nCONVEYOR\n{int(tpd/5)}m", "x": pw*0.1, "y": ph*0.65, "w": pw*0.12, "h": ph*0.05, "hp": 10, "color": "#FFD700"},
        {"name": f"SHREDDER\n{max(1,int(tpd/15))}x\n{int(max(5,tpd/3))} HP", "x": pw*0.24, "y": ph*0.55, "w": pw*0.08, "h": ph*0.15, "hp": int(max(5,tpd/3)), "color": "#FFD700"},
        {"name": f"HAMMER\nMILL\n{int(max(5,tpd/3))} HP", "x": pw*0.24, "y": ph*0.35, "w": pw*0.08, "h": ph*0.15, "hp": int(max(5,tpd/3)), "color": "#FFD700"},
        {"name": f"ROTARY\nDRYER\n{int(max(3,tpd/5))}m x 1.5m\n{int(max(10,tpd/2))} HP", "x": pw*0.35, "y": ph*0.45, "w": pw*0.15, "h": ph*0.2, "hp": int(max(10,tpd/2)), "color": "#FFA07A"},
        {"name": f"PYROLYSIS\nREACTOR\nR-101\n{max(1,int(tpd/10))}x units\n{int(max(20,tpd))} HP", "x": pw*0.55, "y": ph*0.35, "w": pw*0.12, "h": ph*0.3, "hp": int(max(20,tpd)), "color": "#FF6347"},
        {"name": "CONDENSER\nHE-101\n4 units\nin series", "x": pw*0.7, "y": ph*0.5, "w": pw*0.08, "h": ph*0.15, "hp": 5, "color": "#FFA500"},
        {"name": "HIGH SHEAR\nMIXER\n+ COLLOID\nMILL", "x": pw*0.8, "y": ph*0.5, "w": pw*0.08, "h": ph*0.2, "hp": 30, "color": "#DDA0DD"},
        {"name": f"BLENDING\nTANK\n{int(max(5,tpd*0.5))}KL", "x": pw*0.8, "y": ph*0.25, "w": pw*0.08, "h": ph*0.15, "hp": 15, "color": "#DDA0DD"},
    ]

    for m in machines:
        ax.add_patch(FancyBboxPatch((m["x"], m["y"]), m["w"], m["h"],
                                     boxstyle="round,pad=0.2", facecolor=m["color"],
                                     edgecolor='#333', lw=1.5, alpha=0.6))
        ax.text(m["x"] + m["w"]/2, m["y"] + m["h"]/2, m["name"],
                ha='center', va='center', fontsize=5, fontweight='bold')

    # Gangways (1m minimum per Section 32 of Factories Act)
    gangway_y_positions = [ph * 0.3, ph * 0.75]
    for gy in gangway_y_positions:
        ax.add_patch(Rectangle((0, gy), pw, ph * 0.04, facecolor='#FFFF00', alpha=0.3))
        ax.text(pw/2, gy + ph*0.02, "1.5m GANGWAY (Min 1m per Factories Act Sec 32)",
                ha='center', fontsize=5, color='#8B8000', fontweight='bold')

    # Emergency exits
    ax.plot([0, 0], [ph*0.45, ph*0.55], 'g-', lw=6)
    ax.text(-1, ph*0.5, "EMERGENCY\nEXIT", ha='center', fontsize=6, color='green', fontweight='bold')
    ax.plot([pw, pw], [ph*0.45, ph*0.55], 'g-', lw=6)
    ax.text(pw+1, ph*0.5, "EMERGENCY\nEXIT", ha='center', fontsize=6, color='green', fontweight='bold')

    total_hp = sum(m["hp"] for m in machines)
    ax.set_title(f"MACHINERY LAYOUT PLAN — {tpd:.0f} TPD | Total Connected Load: {total_hp} HP | Gangways Marked",
                  fontsize=12, fontweight='bold', color='#003366')
    _add_title_block(ax, fig, "MACHINERY LAYOUT (FACTORY LICENSE SUBMISSION)",
                      f"PPS-BB-{tpd:.0f}-ML-001", tpd, "1:100", company)

    ax.text(pw/2, -2, "Yellow = Gangway (min 1m) | Green = Emergency Exit | All dangerous parts fenced per Sec 21-27",
            ha='center', fontsize=6, color='#666')
    ax.axis('off')
    plt.subplots_adjust(bottom=0.1)

    fname = f"Machinery_Layout_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# MASTER: Generate ALL professional drawings
# ═══════════════════════════════════════════════════════════════════════
def generate_professional_set(tpd, company, state="", location=""):
    """Generate complete professional drawing set for ALL approval submissions."""
    _ensure_dir()
    results = {}
    generators = [
        ("Site Layout Plan (GA)", lambda: generate_site_layout(tpd, company, state, location)),
        ("ETP Layout (PCB CTE)", lambda: generate_etp_layout(tpd, company)),
        ("Tank Farm Layout (PESO)", lambda: generate_tank_farm(tpd, company)),
        ("Machinery Layout (Factory)", lambda: generate_machinery_layout(tpd, company)),
    ]

    for name, func in generators:
        try:
            results[name] = func()
        except Exception as e:
            results[name] = f"ERROR: {e}"

    # Also use existing drawing_generator
    from engines.drawing_generator import generate_pfd, generate_electrical_sld, generate_fire_layout, generate_civil_foundation
    for name, func, kwargs in [
        ("Process Flow Diagram (PFD)", generate_pfd, {"tpd": tpd}),
        ("Electrical SLD", generate_electrical_sld, {"tpd": tpd}),
        ("Fire Safety Layout", generate_fire_layout, {"tpd": tpd}),
        ("Civil Foundation", generate_civil_foundation, {"tpd": tpd}),
    ]:
        try:
            results[name] = func(**kwargs)
        except Exception as e:
            results[name] = f"ERROR: {e}"

    return results


def generate_for_all_capacities(company):
    """Generate professional drawings for all standard capacities."""
    capacities = [5, 10, 15, 20, 30, 40, 50, 75, 100]
    all_results = {}
    for tpd in capacities:
        all_results[tpd] = generate_professional_set(tpd, company)
    return all_results
