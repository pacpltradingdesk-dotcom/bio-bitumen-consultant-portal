"""
Bio Bitumen — Professional Drawing Generator
==============================================
Generates plant layout, process flow, P&ID, electrical SLD, fire layout,
civil foundation, piping layout, and 3D isometric views for ANY capacity.
Uses matplotlib for professional engineering-grade drawings.
"""
import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "generated_drawings")


def _ensure_dir(path):
    os.makedirs(os.path.dirname(path) if not os.path.isdir(path) else path, exist_ok=True)


def _scale_factor(tpd):
    """Scale dimensions based on capacity (30 TPD = 1.0 reference)."""
    return max(0.5, min(2.5, tpd / 30))


# ═══════════════════════════════════════════════════════════════════════
# 1. PLANT LAYOUT (Top View — like 30TPD reference image)
# ═══════════════════════════════════════════════════════════════════════
def generate_plant_layout(tpd, state="", location=""):
    """Generate professional plant layout drawing (top view)."""
    _ensure_dir(OUTPUT_DIR)
    scale = _scale_factor(tpd)
    plot_w = int(60 * scale)
    plot_h = int(35 * scale)

    fig, ax = plt.subplots(1, 1, figsize=(20, 12))
    ax.set_xlim(0, plot_w)
    ax.set_ylim(0, plot_h)
    ax.set_aspect('equal')

    # Plot boundary
    boundary = patches.Rectangle((0, 0), plot_w, plot_h, linewidth=3,
                                   edgecolor='black', facecolor='#f5f5f0', fill=True)
    ax.add_patch(boundary)

    # Section definitions (proportional to capacity)
    sections = [
        {"name": "RAW MATERIAL\nRECEIVING AREA", "x": 0, "y": plot_h * 0.5, "w": plot_w * 0.2, "h": plot_h * 0.5, "color": "#90EE90",
         "items": ["Truck Access", "Weigh Bridge", "Open Storage", "Covered Shed"]},
        {"name": "RAW MATERIAL\nPROCESSING", "x": plot_w * 0.2, "y": plot_h * 0.45, "w": plot_w * 0.22, "h": plot_h * 0.55, "color": "#FFFF99",
         "items": ["Biomass Hopper", "Belt Conveyor", "Shredder", "Hammer Mill", "Rotary Dryer", "Cyclone Dust Collector", "Storage Silo"]},
        {"name": "PYROLYSIS\nREACTOR SECTION\n(CORE)", "x": plot_w * 0.42, "y": plot_h * 0.35, "w": plot_w * 0.18, "h": plot_h * 0.45, "color": "#FFB3B3",
         "items": [f"Reactor R-101 ({max(1,int(tpd/10))}x)", "Thermic Fluid Heater", "Bio-Oil Condenser", "Gas Cooling Tower", "5m SAFETY ZONE"]},
        {"name": "BIO-OIL &\nBITUMEN\nPROCESSING", "x": plot_w * 0.6, "y": plot_h * 0.35, "w": plot_w * 0.18, "h": plot_h * 0.45, "color": "#FFDAB9",
         "items": ["Bio-Oil Storage", "Bitumen Heating Tank", "High Shear Mixer", "Colloid Mill", "Additive Dosing", "Blending Tank"]},
        {"name": "STORAGE\nAREA", "x": plot_w * 0.78, "y": plot_h * 0.6, "w": plot_w * 0.22, "h": plot_h * 0.4, "color": "#ADD8E6",
         "items": [f"Bitumen Tank T-201 ({max(2,int(tpd/10))}x)", "Bio-Oil Tank", "Bund Wall", "4m Fire Spacing", "Pipe Racks"]},
        {"name": "POLLUTION\nCONTROL", "x": plot_w * 0.42, "y": plot_h * 0.8, "w": plot_w * 0.15, "h": plot_h * 0.2, "color": "#D2B48C",
         "items": ["Bag Filter", "Gas Scrubber", f"Chimney Stack (20m)"]},
        {"name": "PRODUCT\nDISPATCH", "x": plot_w * 0.5, "y": 0, "w": plot_w * 0.35, "h": plot_h * 0.3, "color": "#DDA0DD",
         "items": ["Tanker Loading", "Drum Filling Machine", "Drum Storage", "Forklift Area", "Truck Parking"]},
        {"name": "UTILITY", "x": plot_w * 0.85, "y": plot_h * 0.2, "w": plot_w * 0.15, "h": plot_h * 0.4, "color": "#D3D3D3",
         "items": [f"DG Set ({max(250,int(tpd*5*1.2))} kVA)", "PLC Control Room", "Air Compressor", "Cooling Tower", "Water Tank"]},
        {"name": "ADMIN &\nSAFETY", "x": 0, "y": 0, "w": plot_w * 0.25, "h": plot_h * 0.35, "color": "#FFFFFF",
         "items": ["Office Building", "Fire Water Tank", "Emergency Assembly", "Fire Extinguishers"]},
    ]

    for sec in sections:
        rect = patches.FancyBboxPatch((sec["x"] + 0.5, sec["y"] + 0.5),
                                       sec["w"] - 1, sec["h"] - 1,
                                       boxstyle="round,pad=0.3",
                                       facecolor=sec["color"], edgecolor='#333333',
                                       linewidth=1.5, alpha=0.85)
        ax.add_patch(rect)

        # Section title
        ax.text(sec["x"] + sec["w"] / 2, sec["y"] + sec["h"] - 1.5,
                sec["name"], ha='center', va='top', fontsize=8, fontweight='bold',
                color='#003366')

        # Equipment list
        y_pos = sec["y"] + sec["h"] - 3.5
        for item in sec["items"][:5]:
            if y_pos > sec["y"] + 1:
                ax.text(sec["x"] + 1.5, y_pos, f"- {item}", fontsize=5.5, color='#333333')
                y_pos -= 1.2

    # Internal road
    road = patches.Rectangle((0, plot_h * 0.32), plot_w, plot_h * 0.03,
                               facecolor='#808080', alpha=0.5)
    ax.add_patch(road)
    ax.text(plot_w / 2, plot_h * 0.335, "6m INTERNAL CONCRETE ROAD",
            ha='center', va='center', fontsize=6, color='white', fontweight='bold')

    # Title
    title = f"BIO-BITUMEN PLANT LAYOUT — {tpd:.0f} TPD CAPACITY ({plot_w}m x {plot_h}m PLOT)"
    ax.set_title(title, fontsize=14, fontweight='bold', color='#003366', pad=15)

    # Dimensions
    ax.text(plot_w / 2, -1.5, f"{plot_w}m Plot Boundary", ha='center', fontsize=8)
    ax.text(-2, plot_h / 2, f"{plot_h}m", ha='center', va='center', fontsize=8, rotation=90)

    # Info box
    info = f"Capacity: {tpd:.0f} MT/Day | Plot: {plot_w}m x {plot_h}m = {plot_w * plot_h:,} sqm"
    if location:
        info += f" | Location: {location}, {state}"
    ax.text(plot_w / 2, -3, info, ha='center', fontsize=7, color='#666666')

    ax.axis('off')
    plt.tight_layout()

    fname = f"Layout_TopView_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 2. PROCESS FLOW DIAGRAM (PFD)
# ═══════════════════════════════════════════════════════════════════════
def generate_pfd(tpd):
    """Generate Process Flow Diagram."""
    _ensure_dir(OUTPUT_DIR)
    fig, ax = plt.subplots(1, 1, figsize=(22, 10))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 10)

    # Process boxes with flow
    steps = [
        {"name": "BIOMASS\nSTORAGE", "x": 0.5, "y": 4, "w": 2, "h": 2, "color": "#90EE90"},
        {"name": "SHREDDER\n& DRYER", "x": 3.5, "y": 4, "w": 2, "h": 2, "color": "#FFFF99"},
        {"name": "PELLETIZER", "x": 6.5, "y": 4, "w": 2, "h": 2, "color": "#FFD700"},
        {"name": f"PYROLYSIS\nREACTOR\n({max(1,int(tpd/10))}x units)\n450-550C", "x": 9.5, "y": 3, "w": 2.5, "h": 3.5, "color": "#FF6347"},
        {"name": "CONDENSER\nSYSTEM\n(4 units\nin series)", "x": 13, "y": 4, "w": 2, "h": 2.5, "color": "#FFA500"},
        {"name": "BIO-OIL\nBLENDING\nwith VG-30", "x": 16, "y": 4, "w": 2, "h": 2, "color": "#DDA0DD"},
        {"name": "QUALITY\nTESTING\nLAB", "x": 19, "y": 4, "w": 2, "h": 2, "color": "#87CEEB"},
    ]

    # Draw boxes and arrows
    for i, step in enumerate(steps):
        rect = FancyBboxPatch((step["x"], step["y"]), step["w"], step["h"],
                               boxstyle="round,pad=0.2", facecolor=step["color"],
                               edgecolor='#333333', linewidth=2)
        ax.add_patch(rect)
        ax.text(step["x"] + step["w"] / 2, step["y"] + step["h"] / 2,
                step["name"], ha='center', va='center', fontsize=7, fontweight='bold')

        # Arrow to next
        if i < len(steps) - 1:
            next_step = steps[i + 1]
            ax.annotate('', xy=(next_step["x"], next_step["y"] + next_step["h"] / 2),
                        xytext=(step["x"] + step["w"], step["y"] + step["h"] / 2),
                        arrowprops=dict(arrowstyle='->', color='#003366', lw=2))

    # Byproducts
    # Biochar output
    ax.annotate('', xy=(10.75, 1.5), xytext=(10.75, 3),
                arrowprops=dict(arrowstyle='->', color='#8B4513', lw=2))
    rect_char = FancyBboxPatch((9.5, 0.3), 2.5, 1.2, boxstyle="round,pad=0.2",
                                facecolor='#D2B48C', edgecolor='#333333', linewidth=1.5)
    ax.add_patch(rect_char)
    ax.text(10.75, 0.9, f"BIOCHAR\n({tpd * 0.3:.0f} MT/day)\n30% yield", ha='center', va='center', fontsize=6, fontweight='bold')

    # Syngas output
    ax.annotate('', xy=(10.75, 8), xytext=(10.75, 6.5),
                arrowprops=dict(arrowstyle='->', color='#4169E1', lw=2))
    rect_gas = FancyBboxPatch((9.5, 8), 2.5, 1.2, boxstyle="round,pad=0.2",
                               facecolor='#ADD8E6', edgecolor='#333333', linewidth=1.5)
    ax.add_patch(rect_gas)
    ax.text(10.75, 8.6, "SYNGAS\n(Captive Fuel)\n25% yield", ha='center', va='center', fontsize=6, fontweight='bold')

    # Output
    rect_out = FancyBboxPatch((19, 1), 2.5, 2.5, boxstyle="round,pad=0.2",
                               facecolor='#003366', edgecolor='#003366', linewidth=2)
    ax.add_patch(rect_out)
    ax.text(20.25, 2.25, f"BIO-BITUMEN\nOUTPUT\n{tpd * 0.4:.0f} MT/day\nVG30 Grade",
            ha='center', va='center', fontsize=7, fontweight='bold', color='white')
    ax.annotate('', xy=(20.25, 3.5), xytext=(20.25, 4),
                arrowprops=dict(arrowstyle='->', color='#003366', lw=2))

    # Input label
    ax.text(1.5, 7, f"INPUT:\n{tpd:.0f} MT/Day\nAgro-Waste", ha='center', fontsize=8,
            fontweight='bold', color='#006400',
            bbox=dict(boxstyle="round", facecolor="#90EE90", alpha=0.8))

    ax.set_title(f"PROCESS FLOW DIAGRAM — {tpd:.0f} TPD BIO-BITUMEN PLANT",
                  fontsize=14, fontweight='bold', color='#003366')
    ax.axis('off')
    plt.tight_layout()

    fname = f"PFD_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 3. ELECTRICAL SINGLE LINE DIAGRAM (SLD)
# ═══════════════════════════════════════════════════════════════════════
def generate_electrical_sld(tpd):
    """Generate Electrical Single Line Diagram."""
    _ensure_dir(OUTPUT_DIR)
    power_kw = max(25, int(tpd * 5))
    transformer_kva = int(power_kw * 1.25)
    dg_kva = int(power_kw * 1.2)

    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)

    # Grid supply
    ax.text(9, 11.5, f"STATE DISCOM GRID SUPPLY\n{int(tpd * 0.2 + 11)} kV HT", ha='center',
            fontsize=10, fontweight='bold', color='#CC0000',
            bbox=dict(boxstyle="round", facecolor="#FFE0E0"))

    # HT Panel
    ax.plot([9, 9], [10.8, 10], 'k-', lw=3)
    rect = FancyBboxPatch((7, 9.2), 4, 0.8, boxstyle="round,pad=0.1",
                           facecolor='#FFD700', edgecolor='black', lw=2)
    ax.add_patch(rect)
    ax.text(9, 9.6, "HT PANEL (METERING + PROTECTION)", ha='center', fontsize=7, fontweight='bold')

    # Transformer
    ax.plot([9, 9], [9.2, 8.2], 'k-', lw=3)
    circle1 = plt.Circle((9, 7.8), 0.5, facecolor='#ADD8E6', edgecolor='black', lw=2)
    ax.add_patch(circle1)
    ax.text(9, 7.8, f"TR\n{transformer_kva}\nkVA", ha='center', fontsize=6, fontweight='bold')

    # Main LT Panel
    ax.plot([9, 9], [7.3, 6.5], 'k-', lw=3)
    rect2 = FancyBboxPatch((5, 5.8), 8, 0.7, boxstyle="round,pad=0.1",
                            facecolor='#90EE90', edgecolor='black', lw=2)
    ax.add_patch(rect2)
    ax.text(9, 6.15, "MAIN LT DISTRIBUTION PANEL (415V, 3-Phase)", ha='center', fontsize=7, fontweight='bold')

    # DG Set
    rect_dg = FancyBboxPatch((14, 7), 3.5, 1.5, boxstyle="round,pad=0.2",
                              facecolor='#FFA500', edgecolor='black', lw=2)
    ax.add_patch(rect_dg)
    ax.text(15.75, 7.75, f"DG SET\n{dg_kva} kVA\nAuto Changeover", ha='center', fontsize=7, fontweight='bold')
    ax.plot([13, 14], [6.15, 7.5], 'k--', lw=2)

    # Sub-panels (loads)
    loads = [
        (f"REACTOR\nMOTORS\n{int(power_kw*0.35)} kW", 1.5),
        (f"DRYER &\nSHREDDER\n{int(power_kw*0.2)} kW", 4.5),
        (f"PUMPS &\nBLENDING\n{int(power_kw*0.15)} kW", 7.5),
        (f"COMPRESSOR\nCOOLING\n{int(power_kw*0.1)} kW", 10.5),
        (f"LIGHTING\nPLC/SCADA\n{int(power_kw*0.1)} kW", 13.5),
        (f"UTILITY\nSPARE\n{int(power_kw*0.1)} kW", 16.5),
    ]

    for label, x in loads:
        ax.plot([x, x], [5.8, 4.5], 'k-', lw=2)
        rect_l = FancyBboxPatch((x - 1.2, 3), 2.4, 1.5, boxstyle="round,pad=0.15",
                                 facecolor='#E6E6FA', edgecolor='#333333', lw=1.5)
        ax.add_patch(rect_l)
        ax.text(x, 3.75, label, ha='center', va='center', fontsize=6, fontweight='bold')

    # Earth bus
    ax.plot([1, 17], [2, 2], 'g-', lw=3)
    ax.text(9, 1.7, "EARTH BUS (All equipment earthed as per IS:3043)", ha='center', fontsize=7, color='green')

    ax.set_title(f"ELECTRICAL SINGLE LINE DIAGRAM — {tpd:.0f} TPD PLANT ({power_kw} kW Total Load)",
                  fontsize=12, fontweight='bold', color='#003366')

    info = f"Grid: {int(tpd*0.2+11)}kV | Transformer: {transformer_kva} kVA | DG: {dg_kva} kVA | Total Load: {power_kw} kW"
    ax.text(9, 0.5, info, ha='center', fontsize=7, color='#666666')

    ax.axis('off')
    plt.tight_layout()

    fname = f"Electrical_SLD_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 4. FIRE SAFETY LAYOUT
# ═══════════════════════════════════════════════════════════════════════
def generate_fire_layout(tpd):
    """Generate Fire Safety & Emergency Layout."""
    _ensure_dir(OUTPUT_DIR)
    scale = _scale_factor(tpd)
    pw, ph = int(60 * scale), int(35 * scale)

    fig, ax = plt.subplots(1, 1, figsize=(18, 10))
    ax.set_xlim(0, pw)
    ax.set_ylim(0, ph)
    ax.set_aspect('equal')

    # Plot boundary
    ax.add_patch(patches.Rectangle((0, 0), pw, ph, lw=3, edgecolor='red', facecolor='#fff5f5', fill=True))

    # Fire zones
    zones = [
        {"name": "HIGH RISK\n(Reactor Zone)", "x": pw * 0.4, "y": ph * 0.35, "w": pw * 0.2, "h": ph * 0.35, "color": "#FF0000", "alpha": 0.15},
        {"name": "MEDIUM RISK\n(Storage)", "x": pw * 0.75, "y": ph * 0.55, "w": pw * 0.2, "h": ph * 0.35, "color": "#FFA500", "alpha": 0.15},
        {"name": "LOW RISK\n(Admin)", "x": 1, "y": 1, "w": pw * 0.2, "h": ph * 0.3, "color": "#00FF00", "alpha": 0.15},
    ]

    for z in zones:
        ax.add_patch(patches.Rectangle((z["x"], z["y"]), z["w"], z["h"],
                                        facecolor=z["color"], alpha=z["alpha"], edgecolor=z["color"], lw=2, ls='--'))
        ax.text(z["x"] + z["w"] / 2, z["y"] + z["h"] / 2, z["name"],
                ha='center', va='center', fontsize=9, fontweight='bold', color=z["color"])

    # Fire hydrant positions
    hydrant_positions = [(pw * 0.1, ph * 0.5), (pw * 0.3, ph * 0.8), (pw * 0.5, ph * 0.1),
                          (pw * 0.7, ph * 0.5), (pw * 0.9, ph * 0.3), (pw * 0.5, ph * 0.5)]
    for hx, hy in hydrant_positions:
        ax.plot(hx, hy, 'rs', markersize=12)
        ax.text(hx, hy - 1.5, "FH", ha='center', fontsize=6, color='red', fontweight='bold')

    # Fire extinguisher positions
    ext_x = np.linspace(5, pw - 5, int(pw / 8))
    for ex in ext_x:
        ax.plot(ex, ph * 0.33, 'r^', markersize=8)
        ax.plot(ex, ph * 0.67, 'r^', markersize=8)

    # Fire water tank
    ax.add_patch(patches.Circle((pw * 0.15, ph * 0.15), 3, facecolor='#4169E1', alpha=0.5, edgecolor='blue', lw=2))
    ax.text(pw * 0.15, ph * 0.15, f"FIRE\nWATER\nTANK\n{max(50, int(tpd * 5))}KL", ha='center', fontsize=6, fontweight='bold', color='blue')

    # Emergency exits
    exits = [(0, ph / 2), (pw, ph / 2), (pw / 2, 0)]
    for ex, ey in exits:
        ax.plot(ex, ey, 'g>', markersize=15)
        ax.text(ex + 1.5 if ex < pw / 2 else ex - 3, ey, "EXIT", fontsize=7, color='green', fontweight='bold')

    # Assembly point
    ax.add_patch(patches.Rectangle((pw * 0.02, ph * 0.4), 5, 3, facecolor='#00FF00', alpha=0.3, edgecolor='green', lw=2))
    ax.text(pw * 0.02 + 2.5, ph * 0.4 + 1.5, "EMERGENCY\nASSEMBLY\nPOINT", ha='center', fontsize=6, fontweight='bold', color='green')

    # Legend
    ax.text(pw - 8, 3, "LEGEND:", fontsize=7, fontweight='bold')
    ax.plot(pw - 7, 2, 'rs', markersize=8); ax.text(pw - 6, 2, "Fire Hydrant", fontsize=6)
    ax.plot(pw - 7, 1, 'r^', markersize=8); ax.text(pw - 6, 1, "Fire Extinguisher", fontsize=6)
    ax.plot(pw - 3, 2, 'g>', markersize=8); ax.text(pw - 2, 2, "Emergency Exit", fontsize=6)

    ax.set_title(f"FIRE SAFETY & EMERGENCY LAYOUT — {tpd:.0f} TPD PLANT",
                  fontsize=13, fontweight='bold', color='#CC0000')
    ax.axis('off')
    plt.tight_layout()

    fname = f"Fire_Layout_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 5. CIVIL FOUNDATION DRAWING
# ═══════════════════════════════════════════════════════════════════════
def generate_civil_foundation(tpd):
    """Generate civil foundation layout."""
    _ensure_dir(OUTPUT_DIR)
    scale = _scale_factor(tpd)

    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)

    # Foundation blocks
    foundations = [
        {"name": f"REACTOR FOUNDATION\nRCC M30, {int(3*scale)}m x {int(4*scale)}m x 1.5m deep\nHolding Down Bolts: {max(8,int(tpd/3))} nos",
         "x": 35, "y": 35, "w": 15 * scale, "h": 12 * scale, "color": "#D3D3D3"},
        {"name": f"DRYER FOUNDATION\nRCC M25, {int(2.5*scale)}m x {int(6*scale)}m\nVibration isolators",
         "x": 15, "y": 40, "w": 12 * scale, "h": 8 * scale, "color": "#C0C0C0"},
        {"name": f"TANK FARM FOUNDATION\nRCC M25 Slab + Bund Wall\n{int(4*scale)}m dia x 0.3m thick",
         "x": 65, "y": 40, "w": 15 * scale, "h": 15 * scale, "color": "#B0C4DE"},
        {"name": f"DG SET FOUNDATION\n{int(2*scale)}m x {int(3*scale)}m x 0.5m\nAnti-vibration pads",
         "x": 75, "y": 15, "w": 10 * scale, "h": 8 * scale, "color": "#D3D3D3"},
        {"name": f"OFFICE BUILDING\nRCC Frame, {int(6*scale)}m x {int(4*scale)}m\nPlinth: 0.6m above GL",
         "x": 5, "y": 5, "w": 15 * scale, "h": 10 * scale, "color": "#F5DEB3"},
        {"name": f"WEIGHBRIDGE PIT\n{int(3*scale+12)}m x 3m x 1.2m deep\n{max(30,int(tpd+10))} MT capacity",
         "x": 5, "y": 20, "w": 18, "h": 5, "color": "#808080"},
    ]

    for f in foundations:
        ax.add_patch(FancyBboxPatch((f["x"], f["y"]), f["w"], f["h"],
                                     boxstyle="round,pad=0.3", facecolor=f["color"],
                                     edgecolor='#333333', lw=2))
        ax.text(f["x"] + f["w"] / 2, f["y"] + f["h"] / 2, f["name"],
                ha='center', va='center', fontsize=6, fontweight='bold')

    ax.set_title(f"CIVIL FOUNDATION LAYOUT — {tpd:.0f} TPD BIO-BITUMEN PLANT",
                  fontsize=13, fontweight='bold', color='#003366')
    ax.text(50, 1, f"All foundations as per IS:456 | Soil bearing capacity: 15 T/sqm assumed | Grade of concrete: M25/M30",
            ha='center', fontsize=7, color='#666666')
    ax.axis('off')
    plt.tight_layout()

    fname = f"Civil_Foundation_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 6. WATER SUPPLY & DRAINAGE LAYOUT
# ═══════════════════════════════════════════════════════════════════════
def generate_water_layout(tpd):
    """Water supply, drainage, and rainwater harvesting layout."""
    _ensure_dir(OUTPUT_DIR)
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 28)

    water_kld = max(5, int(tpd))
    tank_cap = max(10, int(water_kld * 2))

    # OHT (Overhead Tank)
    ax.add_patch(FancyBboxPatch((2, 20), 4, 4, boxstyle="round,pad=0.2",
                                 facecolor='#ADD8E6', edgecolor='#003366', lw=2))
    ax.text(4, 22, f"OHT\n{tank_cap} KL\n(Elevated)", ha='center', fontsize=6, fontweight='bold')

    # UG Sump
    ax.add_patch(FancyBboxPatch((2, 14), 4, 3, boxstyle="round,pad=0.2",
                                 facecolor='#87CEEB', edgecolor='#003366', lw=2))
    ax.text(4, 15.5, f"UG SUMP\n{tank_cap*2} KL", ha='center', fontsize=6, fontweight='bold')

    # Bore well
    ax.plot(2, 12, 'bv', markersize=12)
    ax.text(2, 11, "BORE\nWELL", ha='center', fontsize=5)

    # Water Treatment
    ax.add_patch(FancyBboxPatch((9, 18), 5, 3, boxstyle="round,pad=0.2",
                                 facecolor='#E0F0FF', edgecolor='#0066CC', lw=2))
    ax.text(11.5, 19.5, f"WATER\nTREATMENT\nSand Filter + Softener", ha='center', fontsize=5, fontweight='bold')

    # Distribution to sections
    sections = [
        ("REACTOR\nCOOLING", 18, 22, '#FF6347'),
        ("PROCESS\nWATER", 18, 18, '#FFA500'),
        ("DOMESTIC\n(Office/Canteen)", 18, 14, '#90EE90'),
        ("FIRE WATER\nTANK", 18, 10, '#FF0000'),
        ("GREEN BELT\nIRRIGATION", 18, 6, '#006400'),
    ]
    for name, x, y, color in sections:
        ax.add_patch(FancyBboxPatch((x, y), 5, 2.5, boxstyle="round,pad=0.2",
                                     facecolor=color, alpha=0.3, edgecolor=color, lw=1.5))
        ax.text(x + 2.5, y + 1.25, name, ha='center', va='center', fontsize=5, fontweight='bold')

    # Pipes (blue lines)
    ax.plot([4, 4], [17, 20], 'b-', lw=2)  # Sump to OHT
    ax.plot([6, 9], [22, 19.5], 'b-', lw=2)  # OHT to WTP
    for _, x, y, _ in sections:
        ax.plot([14, x], [19.5, y + 1.25], 'b--', lw=1.5)

    # ETP
    ax.add_patch(FancyBboxPatch((26, 18), 6, 4, boxstyle="round,pad=0.2",
                                 facecolor='#DEB887', edgecolor='#8B4513', lw=2))
    ax.text(29, 20, f"EFFLUENT\nTREATMENT\nPLANT (ETP)\n{max(2,int(tpd*0.3))} KLD", ha='center', fontsize=5, fontweight='bold')

    # ETP to recycle
    ax.annotate('', xy=(26, 19), xytext=(23, 18),
                arrowprops=dict(arrowstyle='->', color='brown', lw=2))
    ax.text(24, 17, "Effluent\ncollection", fontsize=4, color='brown')

    ax.annotate('', xy=(29, 18), xytext=(29, 14),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(30, 16, "Treated\nwater\nrecycled", fontsize=4, color='green')

    # Rainwater
    ax.add_patch(FancyBboxPatch((26, 6), 6, 4, boxstyle="round,pad=0.2",
                                 facecolor='#E6F2FF', edgecolor='#4169E1', lw=2))
    ax.text(29, 8, "RAINWATER\nHARVESTING\nRecharge Pits\n+ Collection Tank", ha='center', fontsize=5, fontweight='bold')

    # Storm water drain
    ax.plot([26, 32], [12, 12], color='#4169E1', lw=1.5, ls='--')
    ax.text(29, 12.5, "Storm Water Drain", ha='center', fontsize=4, color='#4169E1')

    ax.set_title(f"WATER SUPPLY, DRAINAGE & RAINWATER HARVESTING — {tpd:.0f} TPD\n"
                  f"Total Water Requirement: {water_kld} KLD | ETP: {max(2,int(tpd*0.3))} KLD | Zero Liquid Discharge",
                  fontsize=11, fontweight='bold', color='#003366')

    # Legend
    ax.text(1, 3, "LEGEND:", fontsize=6, fontweight='bold')
    ax.plot([1, 3], [2, 2], 'b-', lw=2); ax.text(3.5, 2, "Fresh water supply", fontsize=5)
    ax.plot([1, 3], [1, 1], 'b--', lw=1.5); ax.text(3.5, 1, "Distribution", fontsize=5)

    ax.text(20, 1, "Standards: IS:1172 (Water Supply) | CPCB ZLD Guidelines | NBC 2016 Rainwater Harvesting",
            ha='center', fontsize=5, color='#666')
    ax.axis('off')
    plt.tight_layout()

    fname = f"Water_Layout_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 7. PIPING & CABLE ROUTING LAYOUT
# ═══════════════════════════════════════════════════════════════════════
def generate_piping_cable_layout(tpd):
    """Piping routing and cable tray layout."""
    _ensure_dir(OUTPUT_DIR)
    fig, ax = plt.subplots(1, 1, figsize=(20, 12))
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 30)

    sf = max(0.5, tpd / 30)

    # Main pipe rack (elevated steel structure)
    rack_y = 15
    ax.add_patch(FancyBboxPatch((3, rack_y - 0.5), 44, 1, boxstyle="square",
                                 facecolor='#D3D3D3', edgecolor='black', lw=2))
    ax.text(25, rack_y, "MAIN PIPE RACK (Elevated Steel, 4.5m Height)", ha='center', fontsize=7, fontweight='bold')

    # Pipe lines on rack (color coded)
    pipes = [
        {"name": f"Process Line (Bio-Oil) — {int(3+tpd*0.05)}\" MS", "y": rack_y + 2, "color": "black", "lw": 2},
        {"name": f"Hot Bitumen — {int(4+tpd*0.05)}\" MS (Jacketed)", "y": rack_y + 3.5, "color": "#8B0000", "lw": 2.5},
        {"name": f"Compressed Air — {int(2+tpd*0.02)}\" GI", "y": rack_y + 5, "color": "green", "lw": 1.5},
        {"name": f"Fire Water — {int(3+tpd*0.03)}\" MS", "y": rack_y + 6.5, "color": "red", "lw": 2},
        {"name": f"Fresh Water — {int(2+tpd*0.02)}\" GI", "y": rack_y + 8, "color": "blue", "lw": 1.5},
        {"name": f"Drain / Effluent — {int(3+tpd*0.03)}\" RCC/PVC", "y": rack_y - 3, "color": "brown", "lw": 1.5},
    ]

    for p in pipes:
        ax.plot([5, 45], [p["y"], p["y"]], color=p["color"], lw=p["lw"])
        ax.text(25, p["y"] + 0.5, p["name"], ha='center', fontsize=5, color=p["color"])

    # Cable trays (below pipe rack)
    ax.add_patch(FancyBboxPatch((3, rack_y - 6), 44, 1.5, boxstyle="square",
                                 facecolor='#FFE4B5', edgecolor='#FF8C00', lw=1.5))
    ax.text(25, rack_y - 5.25, "CABLE TRAY (Perforated GI, 300mm wide)", ha='center', fontsize=6, fontweight='bold')

    cables = [
        f"HT Cable (11kV XLPE 3C x {int(50+tpd*2)} sqmm) — Transformer to HT Panel",
        f"LT Power Cable (1.1kV XLPE 4C x {int(25+tpd)} sqmm) — MCC to Motors",
        "Control Cable (1.1kV PVC 10C x 1.5 sqmm) — PLC to Field Instruments",
        "Instrument Cable (Shielded 2C x 1.5 sqmm) — Sensors to Control Room",
    ]
    for i, cable in enumerate(cables):
        ax.text(25, rack_y - 7.5 - i * 1.2, f"— {cable}", ha='center', fontsize=4.5, color='#FF8C00')

    # Equipment connections (drop-down from rack)
    equip = [
        ("REACTOR\nR-101", 8), ("DRYER\nDR-101", 15), ("CONDENSER\nHE-101", 22),
        ("BLENDING\nMX-101", 29), ("STORAGE\nT-201", 36), ("DG SET\nDG-101", 43),
    ]
    for name, x in equip:
        ax.plot([x, x], [rack_y - 0.5, rack_y - 2.5], 'k-', lw=1)
        ax.plot([x, x], [rack_y + 1.5, rack_y + 2], 'k-', lw=1)
        ax.add_patch(FancyBboxPatch((x - 2, rack_y - 4), 4, 1.5, boxstyle="round,pad=0.2",
                                     facecolor='#E0E0E0', edgecolor='black', lw=1))
        ax.text(x, rack_y - 3.25, name, ha='center', fontsize=4.5, fontweight='bold')

    # Valves on pipes
    for x in [10, 18, 26, 34, 42]:
        ax.plot(x, rack_y + 2, 'k^', markersize=6)  # Gate valve symbol

    ax.set_title(f"PIPING & CABLE ROUTING LAYOUT — {tpd:.0f} TPD BIO-BITUMEN PLANT",
                  fontsize=12, fontweight='bold', color='#003366')

    # Legend
    ax.text(2, 2, "PIPE COLOR CODE:", fontsize=6, fontweight='bold')
    legend = [("Black", "Process"), ("Dark Red", "Hot Bitumen"), ("Green", "Compressed Air"),
              ("Red", "Fire Water"), ("Blue", "Fresh Water"), ("Brown", "Drain/Effluent")]
    for i, (color, label) in enumerate(legend):
        ax.text(2 + i * 7.5, 1, f"{color} = {label}", fontsize=4.5)

    ax.text(25, -0.5, "Standards: IS:11655 (Piping) | IS:1554/7098 (Cables) | OISD-117 (Fire Protection) | IE Rules 1956",
            ha='center', fontsize=5, color='#666')
    ax.axis('off')
    plt.tight_layout()

    fname = f"Piping_Cable_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# 8. EARTHING & LIGHTNING PROTECTION
# ═══════════════════════════════════════════════════════════════════════
def generate_earthing_layout(tpd):
    """Earthing and lightning protection layout."""
    _ensure_dir(OUTPUT_DIR)
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    sf = max(0.5, tpd / 30)
    pw, ph = int(60 * sf), int(35 * sf)
    ax.set_xlim(-2, pw + 2)
    ax.set_ylim(-3, ph + 2)
    ax.set_aspect('equal')

    ax.add_patch(FancyBboxPatch((0, 0), pw, ph, boxstyle="square",
                                 fill=False, edgecolor='black', lw=2))

    # Earth pits (at corners and key locations)
    pit_positions = [
        (3, 3), (pw - 3, 3), (3, ph - 3), (pw - 3, ph - 3),  # 4 corners
        (pw / 2, 3), (pw / 2, ph - 3),  # Mid sides
        (pw * 0.3, ph * 0.5), (pw * 0.7, ph * 0.5),  # Internal
    ]

    for i, (px, py) in enumerate(pit_positions):
        ax.add_patch(FancyBboxPatch((px - 0.8, py - 0.8), 1.6, 1.6,
                                     boxstyle="round,pad=0.1", facecolor='#FFD700',
                                     edgecolor='#333', lw=1.5))
        ax.text(px, py, f"EP-{i+1}", ha='center', va='center', fontsize=5, fontweight='bold')

    # Earth strip (connecting all pits — green line)
    strip_x = [p[0] for p in pit_positions]
    strip_y = [p[1] for p in pit_positions]
    # Connect in a ring
    ordered = [(3, 3), (pw/2, 3), (pw-3, 3), (pw-3, ph-3), (pw/2, ph-3),
               (3, ph-3), (3, 3)]
    for i in range(len(ordered) - 1):
        ax.plot([ordered[i][0], ordered[i+1][0]], [ordered[i][1], ordered[i+1][1]],
                'g-', lw=2.5)

    # Internal connections
    ax.plot([pw*0.3, pw*0.7], [ph*0.5, ph*0.5], 'g-', lw=2)
    ax.plot([pw*0.3, pw/2], [ph*0.5, 3], 'g--', lw=1.5)
    ax.plot([pw*0.7, pw/2], [ph*0.5, ph-3], 'g--', lw=1.5)

    # Equipment earthing connections (dashed green to equipment)
    equip_pos = [
        ("Reactor", pw*0.45, ph*0.5),
        ("Transformer", pw*0.85, ph*0.3),
        ("DG Set", pw*0.85, ph*0.15),
        ("MCC Panel", pw*0.8, ph*0.45),
        ("Tank T-201", pw*0.8, ph*0.7),
        ("Tank T-202", pw*0.85, ph*0.7),
    ]
    for name, ex, ey in equip_pos:
        # Find nearest pit
        nearest = min(pit_positions, key=lambda p: ((p[0]-ex)**2 + (p[1]-ey)**2)**0.5)
        ax.plot([ex, nearest[0]], [ey, nearest[1]], 'g:', lw=1)
        ax.plot(ex, ey, 'ks', markersize=6)
        ax.text(ex, ey + 1, name, ha='center', fontsize=4, color='#333')

    # Lightning protection
    la_positions = [(pw*0.2, ph*0.8), (pw*0.5, ph*0.85), (pw*0.8, ph*0.8)]
    for lx, ly in la_positions:
        ax.plot(lx, ly, 'r^', markersize=12)
        ax.text(lx, ly + 1.5, "LA", ha='center', fontsize=5, color='red', fontweight='bold')
        # Down conductor to earth pit
        nearest = min(pit_positions, key=lambda p: ((p[0]-lx)**2 + (p[1]-ly)**2)**0.5)
        ax.plot([lx, nearest[0]], [ly, nearest[1]], 'r--', lw=1)

    ax.set_title(f"EARTHING & LIGHTNING PROTECTION LAYOUT — {tpd:.0f} TPD PLANT\n"
                  f"Earth Pits: {len(pit_positions)} nos | Earth Strip: 25x3mm GI | "
                  f"Lightning Arrestors: {len(la_positions)} nos | Target Resistance: <1 ohm (substation), <5 ohm (general)",
                  fontsize=10, fontweight='bold', color='#003366')

    # Legend
    ax.text(1, -1.5, "Legend:", fontsize=5, fontweight='bold')
    ax.add_patch(FancyBboxPatch((4, -2), 1, 1, facecolor='#FFD700', edgecolor='#333', lw=1))
    ax.text(5.5, -1.5, "Earth Pit", fontsize=5)
    ax.plot(10, -1.5, 'ks', markersize=6); ax.text(11, -1.5, "Equipment", fontsize=5)
    ax.plot([14, 16], [-1.5, -1.5], 'g-', lw=2.5); ax.text(16.5, -1.5, "Earth Strip (GI 25x3mm)", fontsize=5)
    ax.plot(24, -1.5, 'r^', markersize=8); ax.text(25, -1.5, "Lightning Arrestor", fontsize=5)

    ax.text(pw/2, -2.5, "Standards: IS:3043 (Earthing) | IS:2309 (Lightning Protection) | IE Rules 1956",
            ha='center', fontsize=5, color='#666')
    ax.axis('off')
    plt.tight_layout()

    fname = f"Earthing_Layout_{tpd:.0f}TPD.png"
    path = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════════════
# MASTER: Generate ALL drawings for a capacity
# ═══════════════════════════════════════════════════════════════════════
def generate_all_drawings(tpd, state="", location=""):
    """Generate complete set of engineering drawings for a given capacity."""
    results = {}
    generators = [
        ("Plant Layout (Top View)", generate_plant_layout, {"tpd": tpd, "state": state, "location": location}),
        ("Process Flow Diagram", generate_pfd, {"tpd": tpd}),
        ("Electrical SLD", generate_electrical_sld, {"tpd": tpd}),
        ("Fire Safety Layout", generate_fire_layout, {"tpd": tpd}),
        ("Civil Foundation", generate_civil_foundation, {"tpd": tpd}),
        ("Water & Drainage Layout", generate_water_layout, {"tpd": tpd}),
        ("Piping & Cable Routing", generate_piping_cable_layout, {"tpd": tpd}),
        ("Earthing & Lightning", generate_earthing_layout, {"tpd": tpd}),
    ]

    for name, func, kwargs in generators:
        try:
            path = func(**kwargs)
            results[name] = path
        except Exception as e:
            results[name] = f"ERROR: {e}"

    return results


def generate_all_capacities():
    """Generate drawings for ALL standard capacities."""
    capacities = [5, 10, 15, 20, 30, 40, 50, 75, 100]
    all_results = {}
    for tpd in capacities:
        all_results[tpd] = generate_all_drawings(tpd)
    return all_results
