"""
Audit Event Logger + Dependency Registry + Self-Healing
=========================================================
Logs every action, tracks dependencies, auto-retries failures.

Blueprint Rule: No UI control should exist without:
- mapped backend action
- dependency list
- success/failure state
- audit log entry
"""
import json
import time
import os
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent.parent / "data" / "audit_logs"
LOG_FILE = LOG_DIR / "event_log.json"
MAX_LOG_SIZE = 500  # Keep last 500 events


def _ensure():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _load_log():
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save_log(events):
    _ensure()
    # Keep only last MAX_LOG_SIZE events
    events = events[-MAX_LOG_SIZE:]
    LOG_FILE.write_text(json.dumps(events, indent=2, default=str), encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════
# EVENT LOGGING
# ══════════════════════════════════════════════════════════════════════
def log_event(event_type, source_page, action, status="success", details=None, affected_modules=None):
    """Log an audit event.

    Args:
        event_type: CONFIGURATION_CHANGED, DRAWING_GENERATED, EXPORT_CREATED,
                    FINANCIAL_RECALCULATED, DATA_FETCHED, USER_ACTION, ERROR
        source_page: Page name where action happened
        action: What was done (e.g., "capacity changed 20→50")
        status: success, failed, queued, retrying
        details: dict with additional info
        affected_modules: list of modules that need to update
    """
    events = _load_log()
    events.append({
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "source_page": source_page,
        "action": action,
        "status": status,
        "details": details or {},
        "affected_modules": affected_modules or [],
    })
    _save_log(events)


def get_recent_events(limit=20, event_type=None):
    """Get recent audit events."""
    events = _load_log()
    if event_type:
        events = [e for e in events if e.get("event_type") == event_type]
    return events[-limit:]


def get_error_events(limit=10):
    """Get recent failed events."""
    events = _load_log()
    return [e for e in events if e.get("status") == "failed"][-limit:]


# ══════════════════════════════════════════════════════════════════════
# DEPENDENCY REGISTRY — What changes when input changes
# ══════════════════════════════════════════════════════════════════════
DEPENDENCY_REGISTRY = {
    "capacity_tpd": {
        "affected": [
            "machinery_list", "boq", "plant_engineering", "detailed_costing",
            "financial_model", "working_capital", "break_even", "cash_flow",
            "drawing_prompts", "image_prompts", "presenter_slides",
            "civil_specs", "manpower", "utilities", "dpr_content",
        ],
        "invalidates_exports": True,
        "invalidates_cache": True,
    },
    "process_id": {
        "affected": [
            "machinery_list", "boq", "process_flow", "drawing_prompts",
            "image_prompts", "financial_model", "dpr_content",
        ],
        "invalidates_exports": True,
        "invalidates_cache": True,
    },
    "state": {
        "affected": [
            "location_multipliers", "detailed_costing", "civil_specs",
            "financial_model", "drawing_prompts", "compliance_list",
        ],
        "invalidates_exports": True,
        "invalidates_cache": True,
    },
    "selling_price_per_mt": {
        "affected": [
            "detailed_costing", "financial_model", "sensitivity",
            "break_even", "market_page", "nhai_revenue",
        ],
        "invalidates_exports": True,
        "invalidates_cache": False,
    },
    "bio_blend_pct": {
        "affected": [
            "detailed_costing", "process_outputs", "blend_output",
            "conv_bitumen_needed", "drawing_prompts",
        ],
        "invalidates_exports": True,
        "invalidates_cache": True,
    },
    "plot_length_m": {
        "affected": ["civil_specs", "drawing_prompts", "layout_drawings", "compound_wall"],
        "invalidates_exports": True,
        "invalidates_cache": True,
    },
    "plot_width_m": {
        "affected": ["civil_specs", "drawing_prompts", "layout_drawings", "compound_wall"],
        "invalidates_exports": True,
        "invalidates_cache": True,
    },
    "bio_oil_yield_pct": {
        "affected": ["process_outputs", "detailed_costing", "revenue", "drawing_prompts"],
        "invalidates_exports": True,
        "invalidates_cache": False,
    },
}


def get_affected_modules(changed_field):
    """Get list of modules affected by a field change."""
    entry = DEPENDENCY_REGISTRY.get(changed_field, {})
    return entry.get("affected", [])


def should_invalidate_exports(changed_field):
    """Check if exports need regeneration after this change."""
    entry = DEPENDENCY_REGISTRY.get(changed_field, {})
    return entry.get("invalidates_exports", False)


def should_invalidate_cache(changed_field):
    """Check if image cache needs clearing after this change."""
    entry = DEPENDENCY_REGISTRY.get(changed_field, {})
    return entry.get("invalidates_cache", False)


# ══════════════════════════════════════════════════════════════════════
# SELF-HEALING — Auto-retry failed operations
# ══════════════════════════════════════════════════════════════════════
RETRY_QUEUE = []


def add_retry(action_fn, action_name, max_retries=3):
    """Add a failed action to retry queue."""
    RETRY_QUEUE.append({
        "action_fn": action_fn,
        "action_name": action_name,
        "max_retries": max_retries,
        "attempts": 0,
    })


def process_retries():
    """Process all items in retry queue."""
    results = {"success": 0, "failed": 0}
    remaining = []

    for item in RETRY_QUEUE:
        item["attempts"] += 1
        try:
            item["action_fn"]()
            results["success"] += 1
            log_event("SELF_HEAL", "retry_engine", f"Retried: {item['action_name']}", "success")
        except Exception as e:
            if item["attempts"] < item["max_retries"]:
                remaining.append(item)
            else:
                results["failed"] += 1
                log_event("SELF_HEAL", "retry_engine",
                          f"Failed after {item['attempts']} retries: {item['action_name']}",
                          "failed", {"error": str(e)[:100]})

    RETRY_QUEUE.clear()
    RETRY_QUEUE.extend(remaining)
    return results


# ══════════════════════════════════════════════════════════════════════
# EXPORT VERSIONING
# ══════════════════════════════════════════════════════════════════════
EXPORT_DIR = Path(__file__).parent.parent / "data" / "exports"
EXPORT_INDEX = EXPORT_DIR / "_export_index.json"


def _load_export_index():
    if EXPORT_INDEX.exists():
        try:
            return json.loads(EXPORT_INDEX.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_export_index(index):
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_INDEX.write_text(json.dumps(index, indent=2, default=str), encoding="utf-8")


def register_export(export_type, file_path, cfg_snapshot=None):
    """Register a generated export with version tracking."""
    index = _load_export_index()
    version = len(index.get(export_type, [])) + 1

    if export_type not in index:
        index[export_type] = []

    index[export_type].append({
        "version": version,
        "path": str(file_path),
        "generated_at": datetime.now().isoformat(),
        "capacity_tpd": cfg_snapshot.get("capacity_tpd") if cfg_snapshot else None,
        "state": cfg_snapshot.get("state") if cfg_snapshot else None,
        "process_id": cfg_snapshot.get("process_id") if cfg_snapshot else None,
    })

    _save_export_index(index)
    log_event("EXPORT_CREATED", "export_engine", f"{export_type} v{version}", "success",
              {"path": str(file_path)})
    return version


def get_latest_export(export_type):
    """Get latest export for a type."""
    index = _load_export_index()
    exports = index.get(export_type, [])
    if exports:
        latest = exports[-1]
        if os.path.exists(latest["path"]):
            return latest
    return None
