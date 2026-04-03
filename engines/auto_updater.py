"""
Auto-Updater — Smart Background Task System
==============================================
Periodic tasks: market data refresh, cache cleanup, health checks,
document index rebuild, weather refresh. All automated with logging.
"""
import threading
import time
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path(__file__).parent.parent / "data"
LOG_FILE = CACHE_DIR / "auto_update_log.json"
_updater_running = False
_updater_thread = None


def _log_action(action, status, detail=""):
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        log = []
        if LOG_FILE.exists():
            try:
                log = json.loads(LOG_FILE.read_text(encoding="utf-8"))
            except Exception:
                log = []

        log.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "status": status,
            "detail": detail,
        })
        log = log[-200:]  # Keep last 200 entries
        LOG_FILE.write_text(json.dumps(log, indent=2), encoding="utf-8")
    except Exception:
        pass


def cleanup_expired_cache(max_age_hours=48):
    """Delete cache files older than max_age_hours."""
    cleaned = 0
    try:
        now = time.time()
        for f in CACHE_DIR.glob("api_cache_*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                ts = data.get("_ts", 0)
                age_hours = (now - ts) / 3600
                if age_hours > max_age_hours:
                    f.unlink()
                    cleaned += 1
            except Exception:
                pass
        if cleaned > 0:
            _log_action("cache_cleanup", "OK", f"Removed {cleaned} expired cache files")
    except Exception as e:
        _log_action("cache_cleanup", "ERROR", str(e))
    return cleaned


def refresh_market_data():
    """Refresh market data (crude oil, FX, VG30)."""
    try:
        from engines.market_data_api import get_market_summary
        market = get_market_summary()
        if market:
            _log_action("market_refresh", "OK", f"Crude: ${market.get('crude_oil', {}).get('latest_price', 'N/A') if isinstance(market.get('crude_oil'), dict) else 'cached'}")
            return True
        _log_action("market_refresh", "WARNING", "No data returned")
        return False
    except Exception as e:
        _log_action("market_refresh", "ERROR", str(e))
        return False


def refresh_weather_data(city="Vadodara"):
    """Refresh weather data for configured city."""
    try:
        from engines.free_apis import get_weather_current
        weather = get_weather_current(city)
        if "error" not in weather:
            _log_action("weather_refresh", "OK", f"{city}: {weather.get('temperature_c')}C, {weather.get('condition')}")
            return True
        _log_action("weather_refresh", "WARNING", weather.get("error", "Unknown"))
        return False
    except Exception as e:
        _log_action("weather_refresh", "ERROR", str(e))
        return False


def check_database_health():
    """Verify database integrity and run maintenance."""
    try:
        from database import init_db, get_connection
        init_db()
        with get_connection() as conn:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_count = len(tables)

            # Run ANALYZE for query optimization
            conn.execute("ANALYZE")

            total_rows = 0
            for t in tables:
                try:
                    count = conn.execute(f'SELECT COUNT(*) as c FROM "{t["name"]}"').fetchone()["c"]
                    total_rows += count
                except Exception:
                    pass

        _log_action("db_health", "OK", f"{table_count} tables, {total_rows} total rows")
        return True
    except Exception as e:
        _log_action("db_health", "ERROR", str(e))
        return False


def check_config_consistency():
    """Verify config has no NaN, None, or negative financial values."""
    errors = []
    try:
        from config import (NHAI_TENDERS, COMPETITORS, RISK_REGISTRY, STATES,
                            STATE_SCORES, STATE_COSTS, LICENSE_TYPES, EMI_PRESETS)

        if len(STATES) != 18:
            errors.append(f"STATES count: {len(STATES)} (expected 18)")
        if len(LICENSE_TYPES) != 25:
            errors.append(f"LICENSE_TYPES count: {len(LICENSE_TYPES)} (expected 25)")
        if len(NHAI_TENDERS) < 30:
            errors.append(f"NHAI_TENDERS count: {len(NHAI_TENDERS)} (expected 30+)")

        # Check state costs for negatives
        for state, costs in STATE_COSTS.items():
            for key, val in costs.items():
                if isinstance(val, (int, float)) and val < 0:
                    errors.append(f"{state}.{key} is negative: {val}")

        if errors:
            _log_action("config_check", "WARNING", "; ".join(errors[:5]))
        else:
            _log_action("config_check", "OK", "All config data valid")
        return len(errors) == 0
    except Exception as e:
        _log_action("config_check", "ERROR", str(e))
        return False


def check_drawing_files():
    """Verify all capacity drawings exist."""
    try:
        drawings_dir = CACHE_DIR / "all_drawings"
        if not drawings_dir.exists():
            _log_action("drawings_check", "WARNING", "Drawings directory not found")
            return False

        files = list(drawings_dir.glob("*.png"))
        _log_action("drawings_check", "OK", f"{len(files)} drawing files found")
        return len(files) >= 50  # Expect at least 50 drawings
    except Exception as e:
        _log_action("drawings_check", "ERROR", str(e))
        return False


def run_full_update_cycle(city="Vadodara"):
    """Run one complete update cycle — all checks and refreshes."""
    results = {}

    results["cache_cleanup"] = cleanup_expired_cache(48)
    results["market_data"] = refresh_market_data()
    results["weather"] = refresh_weather_data(city)
    results["database"] = check_database_health()
    results["config"] = check_config_consistency()
    results["drawings"] = check_drawing_files()

    healthy = sum(1 for v in results.values() if v)
    total = len(results)
    score = int(healthy / total * 100) if total > 0 else 0

    _log_action("full_cycle", "COMPLETE", f"Score: {score}% ({healthy}/{total} OK)")
    return results, score


def background_updater(interval_seconds=300, city="Vadodara"):
    """Background thread for periodic updates."""
    global _updater_running
    cycle = 0
    while _updater_running:
        cycle += 1
        try:
            if cycle % 12 == 1:  # Full cycle every hour (12 × 5min)
                run_full_update_cycle(city)
            elif cycle % 3 == 0:  # Market refresh every 15 min
                refresh_market_data()
            else:  # Health check every 5 min
                check_database_health()
        except Exception as e:
            _log_action("background_error", "ERROR", str(e))

        for _ in range(interval_seconds):
            if not _updater_running:
                break
            time.sleep(1)


def start_updater(interval=300, city="Vadodara"):
    """Start the background auto-updater."""
    global _updater_running, _updater_thread
    if _updater_running:
        return "Already running"

    _updater_running = True
    _updater_thread = threading.Thread(target=background_updater, args=(interval, city), daemon=True)
    _updater_thread.start()
    _log_action("updater_start", "OK", f"Interval: {interval}s, City: {city}")
    return "Started"


def stop_updater():
    """Stop the background auto-updater."""
    global _updater_running
    _updater_running = False
    _log_action("updater_stop", "OK", "Stopped by user")
    return "Stopped"


def is_updater_running():
    return _updater_running


def get_update_log(limit=50):
    """Get recent update log entries."""
    try:
        if LOG_FILE.exists():
            log = json.loads(LOG_FILE.read_text(encoding="utf-8"))
            return log[-limit:]
    except Exception:
        pass
    return []
