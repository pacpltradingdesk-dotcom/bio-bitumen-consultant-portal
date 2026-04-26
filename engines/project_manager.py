"""
Project Manager — Multi-Project Support
=========================================
Save / load / switch between up to 20 named projects.
Each project is a config dict stored in data/projects_store/
"""
from __future__ import annotations
from pathlib import Path
import json, re, shutil
from datetime import datetime

_HERE     = Path(__file__).parent.parent
STORE_DIR = _HERE / "data" / "projects_store"


def _slug(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name.strip())[:40]


def _path(name: str) -> Path:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return STORE_DIR / f"{_slug(name)}.json"


# ── CRUD ────────────────────────────────────────────────────────────────

def list_projects() -> list[dict]:
    """Return list of {name, slug, saved_at, capacity_tpd, state, investment_cr}."""
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    projects = []
    for f in sorted(STORE_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            cfg  = data.get("config", {})
            projects.append({
                "name":        data.get("name", f.stem),
                "slug":        f.stem,
                "saved_at":    data.get("saved_at", ""),
                "capacity_tpd":cfg.get("capacity_tpd", 0),
                "state":       cfg.get("state", ""),
                "location":    cfg.get("location", ""),
                "investment_cr":cfg.get("investment_cr", 0),
                "roi_pct":     cfg.get("roi_pct", 0),
                "irr_pct":     cfg.get("irr_pct", 0),
            })
        except Exception:
            pass
    return projects


def save_project(name: str, cfg: dict, notes: str = "") -> str:
    """Save current config as named project. Returns slug."""
    slug = _slug(name)
    data = {
        "name":     name,
        "slug":     slug,
        "saved_at": datetime.now().isoformat(),
        "notes":    notes,
        "config":   cfg,
    }
    _path(name).write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return slug


def load_project(name_or_slug: str) -> dict | None:
    """Load a project config dict by name or slug. Returns None if not found."""
    p = _path(name_or_slug)
    if not p.exists():
        # try by slug directly
        p2 = STORE_DIR / f"{name_or_slug}.json"
        if p2.exists():
            p = p2
        else:
            return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("config", {})
    except Exception:
        return None


def delete_project(name_or_slug: str) -> bool:
    p = _path(name_or_slug)
    if not p.exists():
        p = STORE_DIR / f"{name_or_slug}.json"
    if p.exists():
        p.unlink()
        return True
    return False


def duplicate_project(src_name: str, new_name: str) -> str | None:
    cfg = load_project(src_name)
    if cfg is None:
        return None
    cfg["project_name"] = new_name
    return save_project(new_name, cfg)


def export_project(name_or_slug: str) -> bytes | None:
    """Return raw JSON bytes for download."""
    p = _path(name_or_slug)
    if not p.exists():
        p = STORE_DIR / f"{name_or_slug}.json"
    if p.exists():
        return p.read_bytes()
    return None


def import_project(json_bytes: bytes) -> str | None:
    """Import a project from uploaded JSON bytes. Returns name."""
    try:
        data = json.loads(json_bytes.decode("utf-8"))
        name = data.get("name", "Imported Project")
        cfg  = data.get("config", data)
        return save_project(name, cfg, notes=data.get("notes", ""))
    except Exception:
        return None


def project_count() -> int:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return len(list(STORE_DIR.glob("*.json")))
