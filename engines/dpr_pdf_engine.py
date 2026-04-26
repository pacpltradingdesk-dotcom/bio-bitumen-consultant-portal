"""
DPR PDF Auto-Generator
=======================
Generates a professional Detailed Project Report (DPR) PDF from portal config.
Uses fpdf2. Output: data/exports/DPR_<project>_<date>.pdf
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import io

_HERE      = Path(__file__).parent.parent
EXPORT_DIR = _HERE / "data" / "exports"

# Gold theme colors (R, G, B)
GOLD   = (232, 181, 71)
DARK   = (21,  19,  15)
LIGHT  = (240, 230, 211)
GREY   = (154, 138, 106)
GREEN  = (81,  207, 102)
WHITE  = (255, 255, 255)
BG2    = (30,  27,  20)


def _try_fpdf():
    try:
        from fpdf import FPDF
        return FPDF
    except ImportError:
        return None


class DPR_PDF:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        FPDF = _try_fpdf()
        if FPDF is None:
            raise ImportError("fpdf2 not installed — run: pip install fpdf2")
        self.pdf = FPDF(orientation="P", unit="mm", format="A4")
        self.pdf.set_auto_page_break(auto=True, margin=20)
        self.pdf.set_margins(20, 20, 20)

    def _header(self, title: str = ""):
        pdf = self.pdf
        # Gold bar at top
        pdf.set_fill_color(*GOLD)
        pdf.rect(0, 0, 210, 8, "F")
        pdf.set_xy(20, 10)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*DARK)
        company = self.cfg.get("prepared_by", "Bio Bitumen Consultant")
        pdf.cell(170, 5, f"{company}  |  DPR — {self.cfg.get('project_name','Project')}", ln=True)
        pdf.set_text_color(*GREY)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(170, 4, f"Date: {datetime.now().strftime('%d %B %Y')}  |  Page {pdf.page_no()}", ln=True)
        pdf.ln(3)

    def _footer(self):
        pdf = self.pdf
        pdf.set_y(-15)
        pdf.set_fill_color(*GOLD)
        pdf.rect(0, 282, 210, 8, "F")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*DARK)
        pdf.set_x(20)
        pdf.cell(0, 8, f"CONFIDENTIAL — {self.cfg.get('client_company','Client')}  |  "
                       f"Bio-Bitumen Plant DPR  |  Page {pdf.page_no()}", align="C")

    def _section_header(self, title: str):
        pdf = self.pdf
        pdf.ln(4)
        pdf.set_fill_color(*GOLD)
        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"  {title}", fill=True, ln=True)
        pdf.ln(2)
        pdf.set_text_color(50, 50, 50)

    def _kv(self, label: str, value: str, bold_val: bool = True):
        pdf = self.pdf
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GREY)
        pdf.cell(70, 6, label)
        pdf.set_font("Helvetica", "B" if bold_val else "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 6, str(value), ln=True)

    def _table(self, headers: list[str], rows: list[list], col_widths: list[int] | None = None):
        pdf = self.pdf
        if col_widths is None:
            w = 170 // len(headers)
            col_widths = [w] * len(headers)
        # Header row
        pdf.set_fill_color(*GOLD)
        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "B", 9)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 7, h, border=1, fill=True)
        pdf.ln()
        # Data rows
        pdf.set_font("Helvetica", "", 9)
        for ri, row in enumerate(rows):
            pdf.set_fill_color(245, 245, 240) if ri % 2 == 0 else pdf.set_fill_color(*WHITE)
            pdf.set_text_color(30, 30, 30)
            for i, cell in enumerate(row):
                pdf.cell(col_widths[i], 6, str(cell), border=1, fill=True)
            pdf.ln()
        pdf.ln(3)

    # ── Cover Page ──────────────────────────────────────────────────────
    def cover(self):
        pdf = self.pdf
        pdf.add_page()
        # Gold header band
        pdf.set_fill_color(*GOLD)
        pdf.rect(0, 0, 210, 60, "F")
        # Company / logo text
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(*DARK)
        pdf.set_xy(20, 15)
        pdf.cell(170, 12, self.cfg.get("prepared_by", "Bio Bitumen Consultant Portal"),
                 align="C", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_xy(20, 30)
        pdf.cell(170, 8, "Detailed Project Report (DPR)", align="C", ln=True)

        # Dark mid section
        pdf.set_fill_color(*DARK)
        pdf.rect(0, 60, 210, 100, "F")
        pdf.set_xy(20, 75)
        pdf.set_font("Helvetica", "B", 26)
        pdf.set_text_color(*GOLD)
        name = self.cfg.get("project_name", "Bio-Bitumen Plant")
        pdf.multi_cell(170, 14, name, align="C")

        pdf.set_xy(20, 120)
        pdf.set_font("Helvetica", "", 13)
        pdf.set_text_color(*LIGHT)
        cap   = self.cfg.get("capacity_tpd", 20)
        state = self.cfg.get("state", "")
        loc   = self.cfg.get("location", "")
        pdf.cell(170, 8, f"{cap} TPD Bio-Bitumen Plant  ·  {loc}, {state}", align="C", ln=True)
        pdf.set_xy(20, 132)
        inv = self.cfg.get("investment_cr", 0)
        pdf.cell(170, 8, f"Total Project Investment: ₹ {inv:.2f} Crore", align="C", ln=True)

        # Client info box
        pdf.set_fill_color(40, 36, 28)
        pdf.rect(20, 175, 170, 45, "F")
        pdf.set_xy(28, 180)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*GOLD)
        pdf.cell(0, 6, "Prepared For:", ln=True)
        pdf.set_xy(28, 188)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*LIGHT)
        pdf.cell(0, 7, self.cfg.get("client_name", "") or self.cfg.get("client_company", ""), ln=True)
        pdf.set_xy(28, 197)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GREY)
        pdf.cell(0, 5, self.cfg.get("client_company", ""), ln=True)
        pdf.set_xy(28, 204)
        pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d %B %Y')}", ln=True)

        # Footer band
        pdf.set_fill_color(*GOLD)
        pdf.rect(0, 275, 210, 22, "F")
        pdf.set_xy(20, 280)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 6, "CONFIDENTIAL — This document is prepared exclusively for the named recipient.",
                 align="C")

    # ── Section 1: Executive Summary ────────────────────────────────────
    def executive_summary(self):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("1. Executive Summary")

        cfg = self.cfg
        rows = [
            ["Project Name",      cfg.get("project_name", "—")],
            ["Location",          f"{cfg.get('location','')}, {cfg.get('state','')}"],
            ["Capacity",          f"{cfg.get('capacity_tpd',20)} TPD"],
            ["Total Investment",  f"₹ {cfg.get('investment_cr',0):.2f} Crore"],
            ["Equity",            f"₹ {cfg.get('investment_cr',0)*cfg.get('equity_ratio',0.4):.2f} Cr ({cfg.get('equity_ratio',0.4)*100:.0f}%)"],
            ["Loan",              f"₹ {cfg.get('investment_cr',0)*(1-cfg.get('equity_ratio',0.4)):.2f} Cr @ {cfg.get('interest_rate',0.115)*100:.1f}%"],
            ["Annual Revenue",    f"₹ {cfg.get('revenue_lac',0):.0f} Lac"],
            ["Net Profit / Year", f"₹ {cfg.get('net_profit_lac',0):.0f} Lac"],
            ["ROI",               f"{cfg.get('roi_pct',0):.1f}%"],
            ["IRR",               f"{cfg.get('irr_pct',0):.1f}%"],
            ["Break-even",        f"{cfg.get('break_even_months',0)} months"],
            ["DPR Version",       cfg.get("dpr_version", "1.0")],
            ["Prepared By",       cfg.get("prepared_by", "")],
            ["Report Date",       cfg.get("report_date", datetime.now().strftime("%d-%m-%Y"))],
        ]
        self._table(["Parameter", "Value"], rows, [80, 90])
        self._footer()

    # ── Section 2: Project Overview ─────────────────────────────────────
    def project_overview(self):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("2. Project Overview")
        cfg = self.cfg

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        intro = (
            f"This Detailed Project Report presents the feasibility and implementation plan for a "
            f"{cfg.get('capacity_tpd',20)} TPD bio-bitumen manufacturing plant to be established at "
            f"{cfg.get('location','')}, {cfg.get('state','')}. The plant utilises agricultural waste biomass "
            f"(primarily {cfg.get('biomass_source','rice/wheat straw, bagasse')}) as feedstock "
            f"via a pyrolysis process at {cfg.get('pyrolysis_temp_C',450)}°C to produce bio-bitumen "
            f"conforming to IS 73:2013 viscosity grades. "
            f"Total project cost is ₹ {cfg.get('investment_cr',0):.2f} Crore."
        )
        pdf.multi_cell(170, 6, intro)
        pdf.ln(4)

        self._section_header("2.1 Site Details")
        site_rows = [
            ["Site Address",     cfg.get("site_address", cfg.get("location",""))],
            ["District",         cfg.get("site_district", cfg.get("district",""))],
            ["State",            cfg.get("state","")],
            ["Site Area",        f"{cfg.get('site_area_acres',2):.1f} acres"],
            ["Plot Dimensions",  f"{cfg.get('plot_length_m',100)}m × {cfg.get('plot_width_m',80)}m"],
            ["Land Ownership",   cfg.get("site_ownership","Leased / Own")],
            ["Water Source",     cfg.get("water_source","Borewell")],
            ["Power Source",     cfg.get("power_source","Grid + DG backup")],
            ["Seismic Zone",     cfg.get("seismic_zone","Zone II")],
        ]
        self._table(["Parameter", "Details"], site_rows, [80, 90])
        self._footer()

    # ── Section 3: Technical Details ────────────────────────────────────
    def technical_details(self):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("3. Technical Process & Feedstock")
        cfg = self.cfg

        tech_rows = [
            ["Process Technology", "Pyrolysis (Slow/Fast Pyrolysis)"],
            ["Pyrolysis Temperature", f"{cfg.get('pyrolysis_temp_C',450)} °C"],
            ["Feedstock Capacity", f"{cfg.get('capacity_tpd',20)} MT/day"],
            ["Operating Hours", f"{cfg.get('operating_hours',20)} hours/day"],
            ["Working Days / Year", f"{cfg.get('working_days',300)} days"],
            ["No. of Shifts", f"{cfg.get('num_shifts',2)} shifts"],
            ["Annual Biomass Input", f"{cfg.get('capacity_tpd',20) * cfg.get('working_days',300):,.0f} MT/year"],
        ]
        self._table(["Parameter", "Value"], tech_rows, [90, 80])

        self._section_header("3.1 Product Yields")
        oil_y  = cfg.get("bio_oil_yield_pct",32)
        char_y = cfg.get("bio_char_yield_pct",28)
        syn_y  = cfg.get("syngas_yield_pct",15)
        loss   = 100 - oil_y - char_y - syn_y
        yield_rows = [
            ["Bio-Bitumen / Bio-Oil",  f"{oil_y}%",  f"{cfg.get('capacity_tpd',20)*oil_y/100:.1f} MT/day"],
            ["Bio-Char",               f"{char_y}%", f"{cfg.get('capacity_tpd',20)*char_y/100:.1f} MT/day"],
            ["Syngas",                 f"{syn_y}%",  f"{cfg.get('capacity_tpd',20)*syn_y/100:.1f} MT/day"],
            ["Process Loss",           f"{loss:.0f}%", "—"],
        ]
        self._table(["Product", "Yield %", "Daily Output"], yield_rows, [70, 40, 60])

        self._section_header("3.2 Feedstock Mix")
        mix_rows = []
        feedstock_keys = [
            ("mix_rice_straw_baled", "Rice Straw (Baled)"),
            ("mix_rice_straw_loose", "Rice Straw (Loose)"),
            ("mix_wheat_straw", "Wheat Straw"),
            ("mix_bagasse", "Sugarcane Bagasse"),
            ("mix_lignin", "Lignin"),
            ("mix_other_agro_waste", "Other Agro Waste"),
        ]
        for key, label in feedstock_keys:
            pct = cfg.get(key, 0)
            if pct > 0:
                cost_key = "price_" + key.replace("mix_", "")
                cost = cfg.get(cost_key, 1500)
                mix_rows.append([label, f"{pct}%", f"₹ {cost}/MT"])
        if mix_rows:
            self._table(["Feedstock", "Mix %", "Cost / MT"], mix_rows, [80, 35, 55])
        self._footer()

    # ── Section 4: Financial Projections ────────────────────────────────
    def financials(self):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("4. Financial Projections")
        cfg = self.cfg

        inv_cr  = cfg.get("investment_cr", 0)
        eq_r    = cfg.get("equity_ratio", 0.4)
        rm_cost_lac = round(
            cfg.get("capacity_tpd", 20) * cfg.get("working_days", 300)
            * cfg.get("raw_material_cost_per_mt", 2500) / 100000, 0
        )
        fin_rows = [
            ["Total Project Cost",      f"₹ {inv_cr:.2f} Cr"],
            ["Equity (Own Funds)",       f"₹ {inv_cr*eq_r:.2f} Cr ({eq_r*100:.0f}%)"],
            ["Bank Loan",                f"₹ {inv_cr*(1-eq_r):.2f} Cr @ {cfg.get('interest_rate',0.115)*100:.1f}%"],
            ["Loan Tenure",              f"{cfg.get('emi_tenure_months',84)} months"],
            ["Monthly EMI",              f"₹ {cfg.get('emi_lac_mth',0):.2f} Lac"],
            ["Annual Revenue (Yr 3)",    f"₹ {cfg.get('revenue_lac',0):.0f} Lac"],
            ["Raw Material Cost (Yr 3)", f"₹ {rm_cost_lac:.0f} Lac"],
            ["Gross Profit / EBITDA",    f"₹ {cfg.get('gross_profit_lac',0):.0f} Lac"],
            ["Net Profit (PAT Yr 3)",    f"₹ {cfg.get('net_profit_lac',0):.0f} Lac"],
            ["Biomass Feedstock Cost",   f"₹ {cfg.get('biomass_price_per_mt',0):.0f}/MT (weighted avg)"],
            ["Return on Investment",     f"{cfg.get('roi_pct',0):.1f}%"],
            ["Internal Rate of Return",  f"{cfg.get('irr_pct',0):.1f}%"],
            ["Break-even Period",        f"{cfg.get('break_even_months',0)} months"],
            ["Selling Price (Bio-Oil)",  f"₹ {cfg.get('selling_price_per_mt',35000):,}/MT"],
            ["Selling Price (Biochar)",  f"₹ {cfg.get('biochar_price_per_mt',4000):,}/MT"],
        ]
        self._table(["Financial Parameter", "Value"], fin_rows, [100, 70])

        # 5-year projection table (uses roi_timeline — populated by recalculate())
        timeline = cfg.get("roi_timeline", [])
        if timeline:
            self._section_header("4.1 Five-Year Revenue & Profit Projection")
            tl_headers = ["Year", "Utilization", "Revenue (₹L)", "EBITDA (₹L)", "PAT (₹L)", "DSCR"]
            tl_rows = []
            for row in timeline[:5]:
                tl_rows.append([
                    str(row.get("Year", "")),
                    str(row.get("Utilization", "")),
                    f"{row.get('Revenue (Lac)', 0):.0f}",
                    f"{row.get('EBITDA (Lac)', 0):.0f}",
                    f"{row.get('PAT (Lac)', 0):.0f}",
                    f"{row.get('DSCR', 0):.2f}",
                ])
            self._table(tl_headers, tl_rows, [14, 22, 32, 32, 32, 28])
        self._footer()

    # ── Section 5: Govt Schemes ──────────────────────────────────────────
    def govt_schemes(self, schemes: list[dict] | None = None):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("5. Applicable Government Schemes & Subsidies")

        if not schemes:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 6, "Run Scheme Finder to populate this section.", ln=True)
        else:
            total = sum(s.get("est_benefit_cr", 0) for s in schemes)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*GOLD)
            pdf.cell(0, 7, f"Total Estimated Benefit: ₹ {total:.2f} Crore  ({len(schemes)} schemes applicable)", ln=True)
            pdf.set_text_color(40, 40, 40)
            pdf.ln(2)
            scheme_rows = [[
                s["name"][:45],
                s["benefit_type"][:20],
                f"{s['benefit_pct']}%" if s["benefit_pct"] else "—",
                f"₹{s['est_benefit_cr']:.2f}Cr" if s["est_benefit_cr"] else "Non-financial",
            ] for s in schemes[:12]]
            self._table(["Scheme", "Benefit Type", "Rate", "Est. Benefit"],
                        scheme_rows, [75, 40, 20, 35])
        self._footer()

    # ── Section 6: Sustainability ────────────────────────────────────────
    def sustainability(self, carbon: dict | None = None):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("6. Sustainability & Carbon Profile")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(170, 6,
            "Bio-bitumen is produced from agricultural waste biomass (carbon-neutral feedstock), "
            "replacing fossil-derived bitumen and significantly reducing lifecycle CO₂ emissions."
        )
        pdf.ln(3)
        if carbon:
            c_rows = [
                ["Annual CO₂ Savings",        f"{carbon.get('total_co2_saved_tpa',0):,.0f} tCO₂e/year"],
                ["  → From Bitumen Substitution", f"{carbon.get('co2_from_bitumen_sub',0):,.0f} tCO₂e"],
                ["  → From Biochar Sequestration",f"{carbon.get('co2_from_biochar',0):,.0f} tCO₂e"],
                ["  → From Syngas Substitution",  f"{carbon.get('co2_from_syngas',0):,.0f} tCO₂e"],
                ["Equivalent Trees Planted",  f"{carbon.get('trees_equivalent',0):,}"],
                ["Equivalent Cars Removed",   f"{carbon.get('cars_off_road',0):,.0f}"],
                ["Carbon Credit Revenue (est.)",f"₹ {carbon.get('best_rev_lac',0):.1f} Lac/year"],
                ["Best Carbon Scheme",        carbon.get("best_scheme","—")],
            ]
            self._table(["Sustainability Metric", "Value"], c_rows, [95, 75])
        self._footer()

    # ── Section 7: Implementation Timeline ──────────────────────────────
    def implementation(self):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("7. Implementation Timeline")

        milestones = [
            ("Month 1–2",   "Land acquisition / lease finalisation, Udyam/MSME registration"),
            ("Month 2–3",   "DPR finalisation, bank loan application, MNRE subsidy application"),
            ("Month 3–4",   "Civil construction — boundary wall, plant shed, utilities"),
            ("Month 4–6",   "Machinery procurement, installation of pyrolysis reactor"),
            ("Month 6–7",   "Electrical, piping, instrumentation installation"),
            ("Month 7–8",   "Commissioning runs, quality testing (IS 73:2013 certification)"),
            ("Month 8–9",   "Trial production, staff training, EHS compliance"),
            ("Month 9–10",  "Commercial production launch, marketing & first sales"),
            ("Month 10–12", "Ramp up to full capacity, government scheme claims"),
        ]
        self._table(["Period", "Activity"], milestones, [35, 135])
        self._footer()

    # ── Section 8: Risk Analysis ─────────────────────────────────────────
    def risk_analysis(self):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("8. Risk Analysis & Mitigation")

        risks = [
            ("Biomass price volatility", "Medium", "Long-term MoU with farmers / FPOs; price escalation clause"),
            ("Market demand uncertainty", "Low",    "NHAI mandates bio-bitumen in tenders; growing road sector"),
            ("Technology risk",           "Low",    "Proven pyrolysis technology; CSIR-CRRI validated process"),
            ("Regulatory changes",        "Low",    "IS 73:2013 compliance + BIS mark secures market access"),
            ("Working capital shortage",  "Medium", "Bank CC limit + CGTMSE guarantee covers 75–85% loan"),
            ("Competition",               "Low",    "Limited producers in region; NHAI preferred sourcing"),
            ("Monsoon / seasonal supply", "Medium", "6-month biomass buffer stock; baling & storage facility"),
        ]
        self._table(["Risk", "Level", "Mitigation"], risks, [60, 20, 90])
        self._footer()

    # ── Section 9: Conclusion ────────────────────────────────────────────
    def conclusion(self):
        pdf = self.pdf
        pdf.add_page()
        self._header()
        self._section_header("9. Conclusion & Recommendation")
        cfg = self.cfg
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 30, 30)
        text = (
            f"The proposed {cfg.get('capacity_tpd',20)} TPD bio-bitumen plant at "
            f"{cfg.get('location','')}, {cfg.get('state','')} is technically feasible, "
            f"financially viable, and environmentally sustainable.\n\n"
            f"With an IRR of {cfg.get('irr_pct',0):.1f}%, ROI of {cfg.get('roi_pct',0):.1f}%, "
            f"and a payback period of {cfg.get('break_even_months',0)} months, the project offers "
            f"attractive returns for investors and lenders.\n\n"
            f"The project is eligible for multiple government subsidies (MNRE, CGTMSE, state schemes) "
            f"that can significantly reduce the financial burden. The growing demand for sustainable "
            f"road construction materials and NHAI's preference for bio-bitumen provides a secure market.\n\n"
            f"We recommend proceeding with the detailed engineering and loan application immediately."
        )
        pdf.multi_cell(170, 7, text)
        pdf.ln(8)

        # Sign-off box
        pdf.set_fill_color(*BG2)
        pdf.rect(20, pdf.get_y(), 170, 30, "F")
        pdf.set_xy(28, pdf.get_y() + 5)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*GOLD)
        pdf.cell(0, 6, f"Prepared by: {cfg.get('prepared_by','Consultant')}", ln=True)
        pdf.set_xy(28, pdf.get_y())
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GREY)
        pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d %B %Y')}  |  "
                       f"Version: {cfg.get('dpr_version','1.0')}", ln=True)
        self._footer()

    # ── Generate full PDF ────────────────────────────────────────────────
    def generate(self, schemes: list | None = None, carbon: dict | None = None) -> bytes:
        self.cover()
        self.executive_summary()
        self.project_overview()
        self.technical_details()
        self.financials()
        self.govt_schemes(schemes)
        self.sustainability(carbon)
        self.implementation()
        self.risk_analysis()
        self.conclusion()
        buf = io.BytesIO()
        self.pdf.output(buf)
        return buf.getvalue()


def generate_dpr_pdf(cfg: dict, schemes: list | None = None,
                     carbon: dict | None = None) -> bytes:
    """Main entry point.  Auto-fetches carbon + schemes via master_connector
    if not explicitly provided.  Returns PDF bytes."""
    # Auto-enrich cfg with flat summary fields if missing (outside Streamlit)
    if not cfg.get("revenue_lac") and cfg.get("roi_timeline"):
        tl = cfg["roi_timeline"]
        ref = tl[2] if len(tl) >= 3 else tl[0]
        cfg.setdefault("revenue_lac",      ref.get("Revenue (Lac)", 0))
        cfg.setdefault("net_profit_lac",   ref.get("PAT (Lac)", 0))
        cfg.setdefault("gross_profit_lac", ref.get("EBITDA (Lac)", 0))

    # Auto-fetch carbon if not passed
    if carbon is None:
        try:
            from engines.carbon_engine import load_carbon, calculate_carbon
            carbon = load_carbon() or calculate_carbon(cfg)
        except Exception:
            carbon = {}

    # Auto-fetch schemes if not passed
    if schemes is None:
        try:
            from engines.scheme_finder_engine import load_schemes, find_schemes
            schemes = load_schemes() or find_schemes(cfg)
        except Exception:
            schemes = []

    dpr = DPR_PDF(cfg)
    return dpr.generate(schemes=schemes, carbon=carbon)


def save_dpr_pdf(cfg: dict, schemes=None, carbon=None) -> Path:
    """Generate and save PDF to exports dir. Returns path."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    name = cfg.get("project_name", "DPR").replace(" ", "_")[:30]
    date_str = datetime.now().strftime("%Y%m%d")
    path = EXPORT_DIR / f"DPR_{name}_{date_str}.pdf"
    pdf_bytes = generate_dpr_pdf(cfg, schemes=schemes, carbon=carbon)
    path.write_bytes(pdf_bytes)
    return path
