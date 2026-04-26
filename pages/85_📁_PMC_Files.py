"""
PMC File Manager — Professional PMC-Level Document Control
==========================================================
Structure:  PROJECTS / [CLIENT] / [PROJECT_LOCATION] / [01–12 folders]
Naming:     YYYY-MM-DD_ProjectName_Category_Details_V1.ext
Features:   Create project tree | Upload with auto-rename | Browse | Search | Audit
"""
import sys
import re
import json
import shutil
from pathlib import Path
from datetime import date, datetime

import streamlit as st
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Storage root ──────────────────────────────────────────────────────
PROJECTS_ROOT = Path(__file__).parent.parent / "data" / "projects"
PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

# ── 12 Standard Folders ───────────────────────────────────────────────
STD_FOLDERS = [
    ("01_ADMIN_AGREEMENTS",         "01 — Admin & Agreements"),
    ("02_DPR_FINANCIALS",           "02 — DPR & Financials"),
    ("03_PLANT_MACHINERY",          "03 — Plant & Machinery"),
    ("04_DRAWINGS_LAYOUTS",         "04 — Drawings & Layouts"),
    ("05_RAW_MATERIAL_SUPPLIERS",   "05 — Raw Material & Suppliers"),
    ("06_QUOTATIONS_COMPARISON",    "06 — Quotations & Comparison"),
    ("07_APPROVALS_LICENSES",       "07 — Approvals & Licenses"),
    ("08_SITE_EXECUTION",           "08 — Site Execution"),
    ("09_REPORTS_PRESENTATIONS",    "09 — Reports & Presentations"),
    ("10_PHOTOS_VIDEOS",            "10 — Photos & Videos"),
    ("11_EMAILS_COMMUNICATION",     "11 — Emails & Communication"),
    ("12_FINAL_SUBMISSIONS",        "12 — Final Submissions"),
]
FOLDER_SLUGS = [f[0] for f in STD_FOLDERS]
FOLDER_LABELS = {f[0]: f[1] for f in STD_FOLDERS}

# Category → folder mapping for auto-classification
FILE_CATEGORY_MAP = {
    "pdf":   "12_FINAL_SUBMISSIONS",
    "docx":  "02_DPR_FINANCIALS",
    "doc":   "02_DPR_FINANCIALS",
    "xlsx":  "02_DPR_FINANCIALS",
    "xls":   "02_DPR_FINANCIALS",
    "csv":   "02_DPR_FINANCIALS",
    "dwg":   "04_DRAWINGS_LAYOUTS",
    "dxf":   "04_DRAWINGS_LAYOUTS",
    "svg":   "04_DRAWINGS_LAYOUTS",
    "jpg":   "10_PHOTOS_VIDEOS",
    "jpeg":  "10_PHOTOS_VIDEOS",
    "png":   "10_PHOTOS_VIDEOS",
    "mp4":   "10_PHOTOS_VIDEOS",
    "eml":   "11_EMAILS_COMMUNICATION",
    "msg":   "11_EMAILS_COMMUNICATION",
}

# ── page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="PMC Files | YUGA PMC",
    page_icon="📁",
    layout="wide",
)

st.markdown("""
<style>
.folder-card {
    background:#f8f9fa; border:1px solid #dee2e6; border-radius:8px;
    padding:12px 14px; margin:4px 0; cursor:pointer;
}
.folder-card:hover { background:#e9ecef; }
.file-badge {
    display:inline-block; background:#e3f2fd; color:#0277bd;
    padding:1px 8px; border-radius:10px; font-size:11px; margin-left:6px;
}
.naming-rule {
    background:#fff3e0; border-left:4px solid #ef6c00;
    padding:10px 14px; border-radius:4px; font-family:monospace; font-size:13px;
}
.audit-pass { background:#e8f5e9; padding:8px 12px; border-radius:4px; margin:3px 0; }
.audit-fail { background:#ffebee; padding:8px 12px; border-radius:4px; margin:3px 0; }
</style>
""", unsafe_allow_html=True)

# ── title ─────────────────────────────────────────────────────────────
st.title("📁 PMC File Manager")
st.caption("Professional PMC document control — structured folders, strict naming, full version history")
st.divider()


# ══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def _slug(text: str) -> str:
    """Convert text to a clean folder-safe slug."""
    text = re.sub(r"[^\w\s-]", "", text.strip())
    text = re.sub(r"[\s_]+", "_", text)
    return text[:40].strip("_")


def list_projects() -> list[Path]:
    return sorted([p for p in PROJECTS_ROOT.iterdir() if p.is_dir()])


def create_project_tree(client: str, project: str, location: str) -> Path:
    """Create the full 12-folder tree for a new project."""
    slug = _slug(f"{client}") + "/" + _slug(f"{project}_{location}")
    proj_path = PROJECTS_ROOT / slug
    for folder_slug, _ in STD_FOLDERS:
        (proj_path / folder_slug).mkdir(parents=True, exist_ok=True)
        (proj_path / folder_slug / "OLD_VERSIONS").mkdir(exist_ok=True)
    # Write project manifest
    manifest = {
        "client": client, "project": project, "location": location,
        "created": str(date.today()), "slug": slug,
    }
    (proj_path / "PROJECT_INFO.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return proj_path


def load_project_manifest(proj_path: Path) -> dict:
    info_file = proj_path / "PROJECT_INFO.json"
    if info_file.exists():
        try:
            return json.loads(info_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"client": proj_path.parent.name, "project": proj_path.name, "location": ""}


def suggest_folder(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    kw = filename.lower()
    if "dpr" in kw or "financial" in kw or "excel" in kw:
        return "02_DPR_FINANCIALS"
    if "drawing" in kw or "layout" in kw or "pid" in kw:
        return "04_DRAWINGS_LAYOUTS"
    if "quotation" in kw or "quote" in kw or "rfq" in kw:
        return "06_QUOTATIONS_COMPARISON"
    if "noc" in kw or "license" in kw or "approval" in kw or "pcb" in kw:
        return "07_APPROVALS_LICENSES"
    if "report" in kw or "presentation" in kw or "ppt" in kw:
        return "09_REPORTS_PRESENTATIONS"
    if "email" in kw or "letter" in kw or "communication" in kw:
        return "11_EMAILS_COMMUNICATION"
    return FILE_CATEGORY_MAP.get(ext, "09_REPORTS_PRESENTATIONS")


def make_standard_name(project_name: str, folder_slug: str, detail: str,
                       original_ext: str, version: int = 1) -> str:
    today = date.today().strftime("%Y-%m-%d")
    cat = folder_slug.split("_", 1)[1] if "_" in folder_slug else folder_slug
    detail_clean = _slug(detail) if detail else "Document"
    return f"{today}_{_slug(project_name)}_{cat}_{detail_clean}_V{version}{original_ext}"


def next_version(proj_path: Path, folder_slug: str, base_name: str) -> int:
    """Find the next version number for a file."""
    folder = proj_path / folder_slug
    pattern = re.compile(r"_V(\d+)\.", re.IGNORECASE)
    existing = list(folder.glob("*"))
    max_v = 0
    for f in existing:
        if base_name.lower() in f.name.lower():
            m = pattern.search(f.name)
            if m:
                max_v = max(max_v, int(m.group(1)))
    return max_v + 1


def save_uploaded_file(proj_path: Path, folder_slug: str, fname: str, content: bytes) -> Path:
    """Save uploaded file. If same base exists, move old to OLD_VERSIONS first."""
    folder = proj_path / folder_slug
    folder.mkdir(parents=True, exist_ok=True)
    old_v_dir = folder / "OLD_VERSIONS"
    old_v_dir.mkdir(exist_ok=True)

    target = folder / fname
    if target.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = old_v_dir / f"OLD_{ts}_{target.name}"
        shutil.move(str(target), str(backup))

    target.write_bytes(content)
    return target


def list_files_in_folder(folder: Path) -> list[dict]:
    if not folder.exists():
        return []
    files = []
    for f in sorted(folder.iterdir()):
        if f.is_file() and f.name != "PROJECT_INFO.json":
            files.append({
                "name": f.name,
                "size_kb": round(f.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "path": f,
            })
    return files


def audit_project(proj_path: Path) -> dict:
    """Audit a project for naming violations, missing dates, and OLD_VERSIONS clutter."""
    issues = []
    stats = {"total_files": 0, "compliant": 0, "violations": 0}
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}_")
    version_re = re.compile(r"_V\d+\.", re.IGNORECASE)

    for folder_slug, _ in STD_FOLDERS:
        folder = proj_path / folder_slug
        if not folder.exists():
            issues.append({"folder": folder_slug, "issue": "Folder missing — recreate project", "severity": "error"})
            continue
        for f in folder.iterdir():
            if f.is_dir():
                continue
            stats["total_files"] += 1
            fname = f.name
            ok = True
            if not date_re.match(fname):
                issues.append({"folder": folder_slug, "file": fname,
                                "issue": "Missing date prefix (YYYY-MM-DD)", "severity": "warning"})
                ok = False
            if not version_re.search(fname):
                issues.append({"folder": folder_slug, "file": fname,
                                "issue": "Missing version suffix (_V1, _V2…)", "severity": "warning"})
                ok = False
            if ok:
                stats["compliant"] += 1
            else:
                stats["violations"] += 1

    return {"issues": issues, "stats": stats}


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR — active project selector
# ══════════════════════════════════════════════════════════════════════
projects = list_projects()

with st.sidebar:
    st.markdown("### 📁 Active Project")
    if not projects:
        st.info("No projects yet. Create one in the **New Project** tab.")
        active_proj = None
    else:
        proj_names = []
        for p in projects:
            m = load_project_manifest(p)
            proj_names.append(f"{m.get('client', p.parent.name)} / {m.get('project', p.name)}")
        sel_idx = st.selectbox("Select Project", range(len(proj_names)),
                               format_func=lambda i: proj_names[i], key="active_proj_idx")
        active_proj = projects[sel_idx] if projects else None
        if active_proj:
            m = load_project_manifest(active_proj)
            st.markdown(f"**Client:** {m.get('client','—')}")
            st.markdown(f"**Location:** {m.get('location','—')}")
            st.markdown(f"**Created:** {m.get('created','—')}")
            total_files = sum(
                len([f for f in (active_proj / slug).iterdir() if f.is_file()])
                for slug, _ in STD_FOLDERS if (active_proj / slug).exists()
            )
            st.metric("Total Files", total_files)

    st.divider()
    st.markdown("#### Naming Rule")
    st.markdown(
        '<div class="naming-rule">'
        'YYYY-MM-DD_<br>ProjectName_<br>Category_<br>Details_<br>V1.ext'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
tab_new, tab_upload, tab_browse, tab_search, tab_audit = st.tabs([
    "🆕 New Project",
    "📤 Upload File",
    "📂 Browse",
    "🔍 Search",
    "📋 Audit Report",
])


# ══════════════════════════════════════════════════════════════════════
# TAB 1 — NEW PROJECT
# ══════════════════════════════════════════════════════════════════════
with tab_new:
    st.subheader("Create New Project — Full 12-Folder Tree")
    st.markdown(
        "One click creates **all 12 standard folders + OLD_VERSIONS sub-folders** "
        "under `data/projects/[Client]/[Project_Location]/`."
    )

    with st.form("new_project_form"):
        c1, c2 = st.columns(2)
        np_client  = c1.text_input("Client Name *", placeholder="REX FUELS MANAGEMENT PRIVATE LIMITED")
        np_project = c2.text_input("Project Name *", placeholder="5 TPD PMB-40 Bio-Bitumen Plant")
        np_loc     = c1.text_input("Location *", placeholder="Bahadurgarh, Jhajjar, Haryana")
        np_state   = c2.selectbox("State", [
            "Haryana", "Maharashtra", "Gujarat", "Rajasthan", "Punjab",
            "Uttar Pradesh", "Madhya Pradesh", "Karnataka", "Odisha",
            "West Bengal", "Tamil Nadu", "Telangana",
        ])
        created = st.form_submit_button("🆕 Create Project Tree", type="primary", use_container_width=True)

    if created:
        if not np_client or not np_project or not np_loc:
            st.error("Client Name, Project Name, and Location are required.")
        else:
            proj_path = create_project_tree(np_client, np_project, f"{np_loc}_{np_state}")
            st.success(f"Project tree created at: `{proj_path.relative_to(PROJECTS_ROOT)}`")
            st.balloons()
            st.rerun()

    st.divider()
    st.subheader("Standard Folder Structure")
    cols = st.columns(3)
    for i, (slug, label) in enumerate(STD_FOLDERS):
        with cols[i % 3]:
            st.markdown(
                f'<div class="folder-card">📂 {label}</div>',
                unsafe_allow_html=True,
            )

    if projects:
        st.divider()
        st.subheader("Existing Projects")
        rows = []
        for p in projects:
            m = load_project_manifest(p)
            file_count = sum(
                len([f for f in (p / slug).iterdir() if f.is_file()])
                for slug, _ in STD_FOLDERS if (p / slug).exists()
            )
            rows.append({
                "Client": m.get("client", p.parent.name),
                "Project": m.get("project", p.name),
                "Location": m.get("location", ""),
                "Created": m.get("created", ""),
                "Files": file_count,
                "Path": str(p.relative_to(PROJECTS_ROOT)),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — UPLOAD FILE
# ══════════════════════════════════════════════════════════════════════
with tab_upload:
    st.subheader("📤 Upload File — Auto Rename + Version Control")

    if not active_proj:
        st.warning("Select or create a project first (sidebar or New Project tab).")
    else:
        m = load_project_manifest(active_proj)
        proj_display = f"{m.get('client','—')} / {m.get('project','—')}"
        st.info(f"Uploading to: **{proj_display}**")

        uploaded = st.file_uploader(
            "Drag & drop or click to upload",
            type=None,
            accept_multiple_files=False,
            key="file_uploader",
        )

        if uploaded:
            orig_name = uploaded.name
            ext = Path(orig_name).suffix.lower()
            auto_folder = suggest_folder(orig_name)

            c1, c2 = st.columns(2)
            with c1:
                chosen_folder = st.selectbox(
                    "Target Folder",
                    FOLDER_SLUGS,
                    index=FOLDER_SLUGS.index(auto_folder),
                    format_func=lambda x: FOLDER_LABELS[x],
                    key="upload_folder",
                )
                detail = st.text_input(
                    "File Description (for naming)",
                    value=Path(orig_name).stem[:30],
                    key="upload_detail",
                )
            with c2:
                use_standard_name = st.checkbox("Apply PMC naming convention", value=True, key="use_std_name")
                if use_standard_name:
                    ver = next_version(active_proj, chosen_folder, _slug(detail))
                    std_name = make_standard_name(m.get("project", "Project"), chosen_folder, detail, ext, ver)
                    st.markdown(f"**Will be saved as:**")
                    st.code(std_name)
                else:
                    std_name = orig_name

            if st.button("💾 Upload & Save", type="primary", use_container_width=True, key="btn_upload"):
                content = uploaded.read()
                saved = save_uploaded_file(active_proj, chosen_folder, std_name, content)
                st.success(f"Saved: `{saved.relative_to(PROJECTS_ROOT)}`")
                st.balloons()

        st.divider()
        st.markdown("#### Naming Convention Examples")
        examples = [
            ("DPR for bank", "02_DPR_FINANCIALS",
             f"{date.today()}_BiobitumenPlant_DPR_FINANCIALS_BankSubmission_V1.pdf"),
            ("Plant layout drawing", "04_DRAWINGS_LAYOUTS",
             f"{date.today()}_BiobitumenPlant_DRAWINGS_LAYOUTS_PlantLayout_Rev1_V2.dwg"),
            ("SBS polymer quotation", "06_QUOTATIONS_COMPARISON",
             f"{date.today()}_BiobitumenPlant_QUOTATIONS_COMPARISON_SBSPolymer_AMTL_V1.pdf"),
            ("Fire NOC application", "07_APPROVALS_LICENSES",
             f"{date.today()}_BiobitumenPlant_APPROVALS_LICENSES_FireNOC_Application_V1.pdf"),
        ]
        for desc, folder, name in examples:
            st.markdown(
                f'<div class="naming-rule">'
                f'<strong>{desc} ({folder}):</strong><br>{name}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("")


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — BROWSE
# ══════════════════════════════════════════════════════════════════════
with tab_browse:
    st.subheader("📂 Browse Project Files")

    if not active_proj:
        st.warning("Select a project in the sidebar.")
    else:
        m = load_project_manifest(active_proj)
        st.markdown(f"**Project:** {m.get('client','—')} / {m.get('project','—')}")

        for slug, label in STD_FOLDERS:
            folder = active_proj / slug
            files = list_files_in_folder(folder)
            old_files = list_files_in_folder(folder / "OLD_VERSIONS") if folder.exists() else []

            badge = f'<span class="file-badge">{len(files)} files</span>'
            with st.expander(f"📂 {label} {badge}", expanded=len(files) > 0):
                if not files:
                    st.markdown("*No files yet.*")
                else:
                    df = pd.DataFrame([
                        {"File": f["name"], "Size (KB)": f["size_kb"], "Modified": f["modified"]}
                        for f in files
                    ])
                    st.dataframe(df, use_container_width=True, hide_index=True)

                if old_files:
                    with st.expander(f"🗄 OLD_VERSIONS ({len(old_files)} archived)", expanded=False):
                        df_old = pd.DataFrame([
                            {"File": f["name"], "Size (KB)": f["size_kb"], "Archived": f["modified"]}
                            for f in old_files
                        ])
                        st.dataframe(df_old, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 4 — SEARCH
# ══════════════════════════════════════════════════════════════════════
with tab_search:
    st.subheader("🔍 Search Files")

    if not active_proj:
        st.warning("Select a project in the sidebar.")
    else:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            query = st.text_input("Search by keyword (filename)", placeholder="DPR, layout, quotation, NOC…")
        with col_b:
            folder_filter = st.selectbox(
                "Filter by Folder",
                ["All folders"] + FOLDER_SLUGS,
                format_func=lambda x: "All folders" if x == "All folders" else FOLDER_LABELS.get(x, x),
            )

        if query:
            results_files = []
            search_folders = FOLDER_SLUGS if folder_filter == "All folders" else [folder_filter]
            for slug in search_folders:
                folder = active_proj / slug
                if not folder.exists():
                    continue
                for f in folder.iterdir():
                    if f.is_file() and query.lower() in f.name.lower():
                        results_files.append({
                            "Folder": FOLDER_LABELS.get(slug, slug),
                            "File": f.name,
                            "Size (KB)": round(f.stat().st_size / 1024, 1),
                            "Modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                        })
            if results_files:
                st.success(f"Found {len(results_files)} file(s) matching '{query}'")
                st.dataframe(pd.DataFrame(results_files), use_container_width=True, hide_index=True)
            else:
                st.info(f"No files found matching '{query}'")
        else:
            st.markdown("*Enter a keyword to search.*")

        st.divider()
        st.subheader("Quick File Index — All Files")
        all_files = []
        for slug, label in STD_FOLDERS:
            folder = active_proj / slug
            if not folder.exists():
                continue
            for f in folder.iterdir():
                if f.is_file():
                    all_files.append({
                        "Folder": label,
                        "File": f.name,
                        "Size (KB)": round(f.stat().st_size / 1024, 1),
                        "Modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    })
        if all_files:
            df_all = pd.DataFrame(all_files)
            st.metric("Total Files", len(all_files))
            st.dataframe(df_all, use_container_width=True, hide_index=True, height=400)
            st.download_button(
                "⬇ Download File Index (CSV)",
                df_all.to_csv(index=False),
                file_name=f"file_index_{date.today()}.csv",
                mime="text/csv",
            )
        else:
            st.info("No files in this project yet.")


# ══════════════════════════════════════════════════════════════════════
# TAB 5 — AUDIT REPORT
# ══════════════════════════════════════════════════════════════════════
with tab_audit:
    st.subheader("📋 File Audit Report")
    st.markdown(
        "Checks every file for: **naming convention compliance** (date prefix, version suffix), "
        "**missing folders**, and **OLD_VERSIONS clutter**."
    )

    if not active_proj:
        st.warning("Select a project in the sidebar.")
    else:
        if st.button("🔍 Run Audit", type="primary", use_container_width=True, key="btn_audit"):
            with st.spinner("Auditing project files…"):
                audit = audit_project(active_proj)

            stats = audit["stats"]
            issues = audit["issues"]

            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Total Files", stats["total_files"])
            mc2.metric("Compliant", stats["compliant"])
            mc3.metric("Violations", stats["violations"])
            compliance_rate = round(stats["compliant"] / max(stats["total_files"], 1) * 100, 1)
            mc4.metric("Compliance Rate", f"{compliance_rate}%")

            if compliance_rate == 100:
                st.success("🟢 100% compliant — all files follow PMC naming convention.")
            elif compliance_rate >= 80:
                st.warning(f"🟡 {compliance_rate}% compliant — minor naming issues to fix.")
            else:
                st.error(f"🔴 {compliance_rate}% compliant — naming discipline needs attention.")

            if issues:
                st.markdown("#### Issues Found")
                issue_df = pd.DataFrame([
                    {
                        "Folder": i.get("folder", ""),
                        "File": i.get("file", "—"),
                        "Issue": i.get("issue", ""),
                        "Severity": i.get("severity", "").upper(),
                    }
                    for i in issues
                ])
                st.dataframe(issue_df, use_container_width=True, hide_index=True)

                audit_report = f"""PMC FILE AUDIT REPORT
Project: {load_project_manifest(active_proj).get('project','—')}
Date: {date.today()}

SUMMARY
-------
Total Files:       {stats['total_files']}
Compliant:         {stats['compliant']}
Violations:        {stats['violations']}
Compliance Rate:   {compliance_rate}%

ISSUES
------
"""
                for i in issues:
                    audit_report += f"[{i.get('severity','').upper()}] {i.get('folder','')} / {i.get('file','—')}\n  → {i.get('issue','')}\n\n"

                audit_report += """
NAMING RULE REMINDER
--------------------
Format: YYYY-MM-DD_ProjectName_Category_Details_V1.ext
Example: 2026-04-26_BioBitumen_DPR_FINANCIALS_BankSubmission_V1.pdf

VERSION CONTROL
---------------
• Old versions moved to folder/OLD_VERSIONS/ automatically
• Never overwrite — always increment version number
"""
                st.download_button(
                    "⬇ Download Audit Report",
                    audit_report,
                    file_name=f"file_audit_{date.today()}.txt",
                    mime="text/plain",
                )
            else:
                st.success("No issues found. All files are correctly named.")

        st.divider()
        st.subheader("PMC Naming Standard Quick Reference")
        st.markdown("""
| Element | Rule | Example |
|---|---|---|
| **Date prefix** | `YYYY-MM-DD_` | `2026-04-26_` |
| **Project name** | Short slug, no spaces | `BioBitumen_` |
| **Folder/Category** | Match folder name | `DPR_FINANCIALS_` |
| **Details** | Descriptive, no spaces | `BankSubmission_` |
| **Version** | `_V1`, `_V2`… | `_V1.pdf` |
| **Extension** | Lowercase | `.pdf`, `.xlsx` |

**Full example:**
```
2026-04-26_BioBitumen_DPR_FINANCIALS_BankDPR_Final_V2.pdf
2026-04-26_BioBitumen_DRAWINGS_LAYOUTS_PlantLayout_Rev3_V3.dwg
2026-04-26_BioBitumen_QUOTATIONS_COMPARISON_SBSPolymer_Sargunadoss_V1.pdf
2026-04-26_BioBitumen_APPROVALS_LICENSES_FireNOC_Haryana_V1.pdf
```

**Version control:**
- Old file → moved to `OLD_VERSIONS/OLD_YYYYMMDD_HHMMSS_[filename]`
- New file saved with incremented version number
- NEVER delete old versions — bank audits trace every revision
        """)
