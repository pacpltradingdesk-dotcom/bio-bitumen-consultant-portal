"""
Bio Bitumen Consultant Portal — Package Engine
Assembles document packages for customers, with optional DOCX customization.
"""
import os
import shutil
import zipfile
import json
from datetime import datetime, timezone, timedelta
from config import (DOC_ROOT, SUBMISSION_DIR, PACKAGE_OUTPUT_DIR,
                    CAPACITY_KEYS, SUBMISSION_CATEGORIES)
from engines.docx_customizer import customize_docx, get_default_replacements

IST = timezone(timedelta(hours=5, minutes=30))


def get_suggested_documents(capacity, recipient_type):
    """
    Get list of files from READY_FOR_SUBMISSION/{recipient_type}/{capacity}/
    Returns list of dicts with filename and absolute_path.
    """
    # Map capacity key to folder name (e.g. "05MT" -> "05MT" or "5MT")
    base_dir = SUBMISSION_DIR / recipient_type
    cap_folder = None

    # Try exact capacity key match
    for folder_name in os.listdir(str(base_dir)) if base_dir.exists() else []:
        if capacity.lstrip("0") + "MT" in folder_name or capacity in folder_name:
            cap_folder = base_dir / folder_name
            break

    if not cap_folder or not cap_folder.exists():
        # Try with leading zero stripped
        cap_stripped = capacity.lstrip("0") + "MT"
        cap_folder = base_dir / cap_stripped
        if not cap_folder.exists():
            cap_folder = base_dir / capacity
            if not cap_folder.exists():
                return []

    files = []
    for fname in sorted(os.listdir(str(cap_folder))):
        fpath = cap_folder / fname
        if fpath.is_file():
            files.append({
                "filename": fname,
                "absolute_path": str(fpath),
                "size": os.path.getsize(str(fpath)),
                "extension": os.path.splitext(fname)[1].lower(),
            })

    return files


def get_state_forms(state, capacity):
    """Get state-wise application forms for a given state and capacity."""
    state_dir = DOC_ROOT / "STATE_WISE_APPLICATION_FORMS" / state.replace(" ", "_")
    cap_stripped = capacity.lstrip("0") + "MT"
    cap_dir = state_dir / cap_stripped

    if not cap_dir.exists():
        cap_dir = state_dir / capacity
        if not cap_dir.exists():
            return []

    files = []
    for fname in sorted(os.listdir(str(cap_dir))):
        fpath = cap_dir / fname
        if fpath.is_file():
            files.append({
                "filename": fname,
                "absolute_path": str(fpath),
                "size": os.path.getsize(str(fpath)),
                "extension": os.path.splitext(fname)[1].lower(),
            })
    return files


def build_package(customer, capacity, document_paths, customize=False, plant=None):
    """
    Copy selected documents to a customer-specific package folder.
    Optionally customize DOCX files with customer details.

    Returns the package folder path.
    """
    now = datetime.now(IST)
    date_str = now.strftime("%Y%m%d_%H%M")
    company_name = (customer.get("company") or customer.get("name", "Customer")).replace(" ", "_")
    folder_name = f"{company_name}_{capacity}_{date_str}"
    package_dir = PACKAGE_OUTPUT_DIR / folder_name

    os.makedirs(str(package_dir), exist_ok=True)

    copied_files = []

    for doc_path in document_paths:
        if not os.path.exists(doc_path):
            continue

        fname = os.path.basename(doc_path)
        dest_path = str(package_dir / fname)

        if customize and fname.lower().endswith(".docx"):
            # Customize DOCX with customer details
            try:
                replacements = get_default_replacements(customer, plant)
                customize_docx(doc_path, dest_path, replacements)
            except Exception:
                # Fallback: just copy the file
                shutil.copy2(doc_path, dest_path)
        else:
            shutil.copy2(doc_path, dest_path)

        copied_files.append(fname)

    # Write a manifest
    manifest = {
        "customer": customer.get("name", ""),
        "company": customer.get("company", ""),
        "capacity": capacity,
        "created": now.isoformat(),
        "files": copied_files,
        "customized": customize,
    }
    manifest_path = package_dir / "PACKAGE_MANIFEST.json"
    with open(str(manifest_path), "w") as f:
        json.dump(manifest, f, indent=2)

    return str(package_dir)


def zip_package(package_folder):
    """Create a ZIP archive of the package folder. Returns ZIP path."""
    zip_path = f"{package_folder}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(package_folder):
            for fname in files:
                fpath = os.path.join(root, fname)
                arcname = os.path.relpath(fpath, os.path.dirname(package_folder))
                zf.write(fpath, arcname)

    return zip_path


def get_available_recipient_types():
    """Return list of recipient types that have actual files."""
    available = {}
    if not SUBMISSION_DIR.exists():
        return SUBMISSION_CATEGORIES

    for folder_name in sorted(os.listdir(str(SUBMISSION_DIR))):
        if folder_name in SUBMISSION_CATEGORIES:
            available[folder_name] = SUBMISSION_CATEGORIES[folder_name]

    return available if available else SUBMISSION_CATEGORIES
