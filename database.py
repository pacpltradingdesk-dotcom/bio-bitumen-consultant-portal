"""
Bio Bitumen Consultant Portal — SQLite Database Layer (UPGRADED)
14 tables: customers, packages, communications, analytics_events,
configurations, feasibility_assessments, compliance_items, vendor_quotes,
report_generations + NEW: project_milestones, meetings, price_alerts,
risk_items, document_versions
"""
import sqlite3
import json
import os
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager
from config import DB_PATH

IST = timezone(timedelta(hours=5, minutes=30))


def _now():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def _ensure_dir():
    os.makedirs(os.path.dirname(str(DB_PATH)), exist_ok=True)


@contextmanager
def get_connection():
    _ensure_dir()
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT DEFAULT '',
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                whatsapp TEXT DEFAULT '',
                state TEXT DEFAULT '',
                city TEXT DEFAULT '',
                interested_capacity TEXT DEFAULT '',
                budget_cr REAL DEFAULT 0,
                status TEXT DEFAULT 'New',
                notes TEXT DEFAULT '',
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                capacity TEXT,
                recipient_type TEXT,
                documents TEXT DEFAULT '[]',
                output_folder TEXT DEFAULT '',
                customized INTEGER DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS communications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                package_id INTEGER,
                channel TEXT DEFAULT '',
                subject TEXT DEFAULT '',
                content_summary TEXT DEFAULT '',
                attachments TEXT DEFAULT '[]',
                sent_at TEXT,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                customer_id INTEGER,
                details TEXT DEFAULT '{}',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                name TEXT DEFAULT 'Default',
                config_json TEXT DEFAULT '{}',
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS feasibility_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                state TEXT,
                scores_json TEXT DEFAULT '{}',
                total_score REAL DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS compliance_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                license_name TEXT NOT NULL,
                category TEXT DEFAULT '',
                status TEXT DEFAULT 'Not Started',
                applied_date TEXT,
                received_date TEXT,
                expiry_date TEXT,
                notes TEXT DEFAULT '',
                updated_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS vendor_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT,
                equipment TEXT,
                capacity TEXT,
                price_lac REAL DEFAULT 0,
                delivery_weeks INTEGER DEFAULT 0,
                warranty_months INTEGER DEFAULT 0,
                contact TEXT DEFAULT '',
                source TEXT DEFAULT '',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS report_generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                report_type TEXT,
                capacity_tpd REAL,
                file_path TEXT DEFAULT '',
                config_snapshot TEXT DEFAULT '{}',
                created_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS project_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                milestone_name TEXT NOT NULL,
                phase TEXT DEFAULT '',
                planned_start TEXT,
                planned_end TEXT,
                actual_start TEXT,
                actual_end TEXT,
                status TEXT DEFAULT 'Not Started',
                notes TEXT DEFAULT '',
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                meeting_date TEXT,
                meeting_type TEXT DEFAULT 'In-Person',
                agenda TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                action_items TEXT DEFAULT '',
                created_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                threshold REAL,
                direction TEXT DEFAULT 'above',
                is_active INTEGER DEFAULT 1,
                last_triggered TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS risk_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                category TEXT DEFAULT '',
                description TEXT DEFAULT '',
                probability INTEGER DEFAULT 3,
                impact INTEGER DEFAULT 3,
                mitigation TEXT DEFAULT '',
                status TEXT DEFAULT 'Open',
                created_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS document_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_path TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                generated_at TEXT,
                config_snapshot TEXT DEFAULT '{}',
                notes TEXT DEFAULT ''
            );
        """)


# ── CUSTOMERS CRUD ────────────────────────────────────────────────────

def insert_customer(data):
    now = _now()
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO customers (name, company, email, phone, whatsapp, state, city,
                                   interested_capacity, budget_cr, status, notes,
                                   created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("name", ""), data.get("company", ""), data.get("email", ""),
            data.get("phone", ""), data.get("whatsapp", ""), data.get("state", ""),
            data.get("city", ""), data.get("interested_capacity", ""),
            data.get("budget_cr", 0), data.get("status", "New"),
            data.get("notes", ""), now, now,
        ))
        cid = cur.lastrowid
    insert_event("customer_added", cid, {"name": data.get("name", "")})
    return cid


def update_customer(cid, data):
    with get_connection() as conn:
        conn.execute("""
            UPDATE customers SET
                name=?, company=?, email=?, phone=?, whatsapp=?, state=?, city=?,
                interested_capacity=?, budget_cr=?, status=?, notes=?, updated_at=?
            WHERE id=?
        """, (
            data.get("name", ""), data.get("company", ""), data.get("email", ""),
            data.get("phone", ""), data.get("whatsapp", ""), data.get("state", ""),
            data.get("city", ""), data.get("interested_capacity", ""),
            data.get("budget_cr", 0), data.get("status", "New"),
            data.get("notes", ""), _now(), cid,
        ))


def delete_customer(cid):
    with get_connection() as conn:
        conn.execute("DELETE FROM customers WHERE id=?", (cid,))


def get_all_customers():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM customers ORDER BY updated_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_customer(cid):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone()
        return dict(row) if row else None


def search_customers(query):
    with get_connection() as conn:
        q = f"%{query}%"
        rows = conn.execute("""
            SELECT * FROM customers
            WHERE name LIKE ? OR company LIKE ? OR email LIKE ? OR phone LIKE ? OR state LIKE ?
            ORDER BY updated_at DESC
        """, (q, q, q, q, q)).fetchall()
        return [dict(r) for r in rows]


def get_customer_count_by_status():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT status, COUNT(*) as count FROM customers GROUP BY status
        """).fetchall()
        return {r["status"]: r["count"] for r in rows}


# ── PACKAGES CRUD ─────────────────────────────────────────────────────

def insert_package(data):
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO packages (customer_id, capacity, recipient_type, documents,
                                  output_folder, customized, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("customer_id"), data.get("capacity", ""),
            data.get("recipient_type", ""),
            json.dumps(data.get("documents", [])),
            data.get("output_folder", ""), data.get("customized", 0), _now(),
        ))
        pid = cur.lastrowid
    insert_event("package_created", data.get("customer_id"),
                 {"capacity": data.get("capacity"), "recipient_type": data.get("recipient_type")})
    return pid


def get_packages_for_customer(customer_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM packages WHERE customer_id=? ORDER BY created_at DESC",
            (customer_id,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["documents"] = json.loads(d["documents"]) if d["documents"] else []
            result.append(d)
        return result


def get_all_packages():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM packages ORDER BY created_at DESC").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["documents"] = json.loads(d["documents"]) if d["documents"] else []
            result.append(d)
        return result


# ─�� COMMUNICATIONS CRUD ──────────────────────────────────────────────

def insert_communication(data):
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO communications (customer_id, package_id, channel, subject,
                                        content_summary, attachments, sent_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("customer_id"), data.get("package_id"),
            data.get("channel", ""), data.get("subject", ""),
            data.get("content_summary", ""),
            json.dumps(data.get("attachments", [])), _now(),
            data.get("status", "sent"),
        ))
        cid = cur.lastrowid
    insert_event("package_sent", data.get("customer_id"),
                 {"channel": data.get("channel"), "package_id": data.get("package_id")})
    return cid


def get_communications_for_customer(customer_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM communications WHERE customer_id=? ORDER BY sent_at DESC",
            (customer_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_communications():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM communications ORDER BY sent_at DESC").fetchall()
        return [dict(r) for r in rows]


# ── ANALYTICS EVENTS ─────────────────────────────────────────────────

def insert_event(event_type, customer_id=None, details=None):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO analytics_events (event_type, customer_id, details, created_at)
            VALUES (?, ?, ?, ?)
        """, (event_type, customer_id, json.dumps(details or {}), _now()))


def get_events(limit=50):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM analytics_events ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["details"] = json.loads(d["details"]) if d["details"] else {}
            result.append(d)
        return result


def get_package_stats():
    with get_connection() as conn:
        by_cap = conn.execute(
            "SELECT capacity, COUNT(*) as count FROM packages GROUP BY capacity"
        ).fetchall()
        by_type = conn.execute(
            "SELECT recipient_type, COUNT(*) as count FROM packages GROUP BY recipient_type"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) as count FROM packages").fetchone()
        return {
            "total": total["count"] if total else 0,
            "by_capacity": {r["capacity"]: r["count"] for r in by_cap},
            "by_recipient_type": {r["recipient_type"]: r["count"] for r in by_type},
        }


def get_communication_stats():
    with get_connection() as conn:
        by_channel = conn.execute(
            "SELECT channel, COUNT(*) as count FROM communications GROUP BY channel"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) as count FROM communications").fetchone()
        return {
            "total": total["count"] if total else 0,
            "by_channel": {r["channel"]: r["count"] for r in by_channel},
        }


# ── CONFIGURATIONS CRUD ──────────────────────────────────────────────

def save_configuration(customer_id, name, config_json):
    with get_connection() as conn:
        now = _now()
        cur = conn.execute("""
            INSERT INTO configurations (customer_id, name, config_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_id, name, json.dumps(config_json), now, now))
        return cur.lastrowid


def get_configurations(customer_id=None):
    with get_connection() as conn:
        if customer_id:
            rows = conn.execute("SELECT * FROM configurations WHERE customer_id=? ORDER BY updated_at DESC",
                                (customer_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM configurations ORDER BY updated_at DESC").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["config_json"] = json.loads(d["config_json"]) if d["config_json"] else {}
            result.append(d)
        return result


# ── COMPLIANCE CRUD ──────────────────────────────────────────────────

def insert_compliance_item(customer_id, license_name, category=""):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO compliance_items (customer_id, license_name, category, status, updated_at)
            VALUES (?, ?, ?, 'Not Started', ?)
        """, (customer_id, license_name, category, _now()))


def update_compliance_item(item_id, data):
    with get_connection() as conn:
        conn.execute("""
            UPDATE compliance_items SET status=?, applied_date=?, received_date=?,
            expiry_date=?, notes=?, updated_at=? WHERE id=?
        """, (data.get("status", "Not Started"), data.get("applied_date"),
              data.get("received_date"), data.get("expiry_date"),
              data.get("notes", ""), _now(), item_id))


def get_compliance_items(customer_id):
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM compliance_items WHERE customer_id=? ORDER BY license_name",
                            (customer_id,)).fetchall()
        return [dict(r) for r in rows]


def init_compliance_for_customer(customer_id, license_types):
    """Initialize compliance checklist for a customer with all license types."""
    existing = get_compliance_items(customer_id)
    existing_names = {item["license_name"] for item in existing}
    for lt in license_types:
        if lt["name"] not in existing_names:
            insert_compliance_item(customer_id, lt["name"], lt.get("category", ""))


# ── VENDOR QUOTES CRUD ──────────────────────────────────────────────

def insert_vendor_quote(data):
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO vendor_quotes (vendor_name, equipment, capacity, price_lac,
            delivery_weeks, warranty_months, contact, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data.get("vendor_name"), data.get("equipment"), data.get("capacity"),
              data.get("price_lac", 0), data.get("delivery_weeks", 0),
              data.get("warranty_months", 0), data.get("contact", ""),
              data.get("source", ""), _now()))
        return cur.lastrowid


def get_vendor_quotes(equipment=None):
    with get_connection() as conn:
        if equipment:
            rows = conn.execute("SELECT * FROM vendor_quotes WHERE equipment LIKE ? ORDER BY price_lac",
                                (f"%{equipment}%",)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM vendor_quotes ORDER BY equipment, price_lac").fetchall()
        return [dict(r) for r in rows]


# ── REPORT GENERATIONS CRUD ──────────────────────────────────────────

def insert_report_generation(data):
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO report_generations (customer_id, report_type, capacity_tpd,
            file_path, config_snapshot, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data.get("customer_id"), data.get("report_type"),
              data.get("capacity_tpd", 0), data.get("file_path", ""),
              json.dumps(data.get("config_snapshot", {})), _now()))
        return cur.lastrowid


def get_report_generations(customer_id=None, limit=20):
    with get_connection() as conn:
        if customer_id:
            rows = conn.execute("SELECT * FROM report_generations WHERE customer_id=? ORDER BY created_at DESC LIMIT ?",
                                (customer_id, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM report_generations ORDER BY created_at DESC LIMIT ?",
                                (limit,)).fetchall()
        return [dict(r) for r in rows]


# ── PROJECT MILESTONES ───────────────────────────────────────────────

def insert_milestone(customer_id, milestone_name, phase="", planned_start="", planned_end=""):
    with get_connection() as conn:
        now = _now()
        conn.execute("""INSERT INTO project_milestones
            (customer_id, milestone_name, phase, planned_start, planned_end, status, created_at, updated_at)
            VALUES (?,?,?,?,?,'Not Started',?,?)""",
            (customer_id, milestone_name, phase, planned_start, planned_end, now, now))


def update_milestone(milestone_id, data):
    with get_connection() as conn:
        sets = ", ".join(f"{k}=?" for k in data)
        vals = list(data.values()) + [_now(), milestone_id]
        conn.execute(f"UPDATE project_milestones SET {sets}, updated_at=? WHERE id=?", vals)


def get_milestones(customer_id):
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM project_milestones WHERE customer_id=? ORDER BY planned_start",
                            (customer_id,)).fetchall()
        return [dict(r) for r in rows]


def init_milestones_for_customer(customer_id, start_date="2026-05-01"):
    """Create default milestones from the 10-phase template."""
    from datetime import datetime, timedelta
    start = datetime.strptime(start_date, "%Y-%m-%d")
    phases = [
        ("Pre-Feasibility & DPR", "Planning", 0, 30),
        ("Company Setup (ROC/GST/PAN)", "Legal", 30, 30),
        ("Land Acquisition & Approvals", "Land", 30, 90),
        ("Environmental Clearances (CTE/CTO)", "Regulatory", 60, 150),
        ("Bank Loan Sanction", "Finance", 60, 90),
        ("Detailed Engineering & Design", "Engineering", 90, 90),
        ("Equipment Procurement", "Procurement", 120, 120),
        ("Civil Construction", "Construction", 150, 150),
        ("Installation & Commissioning", "Installation", 270, 90),
        ("Trial Run & Commercial Production", "Operations", 360, 180),
    ]
    with get_connection() as conn:
        now = _now()
        for name, phase, offset_start, duration in phases:
            p_start = (start + timedelta(days=offset_start)).strftime("%Y-%m-%d")
            p_end = (start + timedelta(days=offset_start + duration)).strftime("%Y-%m-%d")
            conn.execute("""INSERT INTO project_milestones
                (customer_id, milestone_name, phase, planned_start, planned_end, status, created_at, updated_at)
                VALUES (?,?,?,?,?,'Not Started',?,?)""",
                (customer_id, name, phase, p_start, p_end, now, now))


# ── MEETINGS ─────────────────────────────────────────────────────────

def insert_meeting(customer_id, meeting_date, meeting_type="In-Person", agenda="", notes="", action_items=""):
    with get_connection() as conn:
        conn.execute("""INSERT INTO meetings
            (customer_id, meeting_date, meeting_type, agenda, notes, action_items, created_at)
            VALUES (?,?,?,?,?,?,?)""",
            (customer_id, meeting_date, meeting_type, agenda, notes, action_items, _now()))


def get_meetings(customer_id=None, limit=20):
    with get_connection() as conn:
        if customer_id:
            rows = conn.execute("SELECT * FROM meetings WHERE customer_id=? ORDER BY meeting_date DESC LIMIT ?",
                                (customer_id, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM meetings ORDER BY meeting_date DESC LIMIT ?",
                                (limit,)).fetchall()
        return [dict(r) for r in rows]


# ── PRICE ALERTS ─────────────────────────────────────────────────────

def insert_price_alert(metric_name, threshold, direction="above"):
    with get_connection() as conn:
        conn.execute("""INSERT INTO price_alerts (metric_name, threshold, direction, is_active, created_at)
            VALUES (?,?,?,1,?)""", (metric_name, threshold, direction, _now()))


def get_price_alerts(active_only=True):
    with get_connection() as conn:
        if active_only:
            rows = conn.execute("SELECT * FROM price_alerts WHERE is_active=1 ORDER BY created_at DESC").fetchall()
        else:
            rows = conn.execute("SELECT * FROM price_alerts ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def delete_price_alert(alert_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM price_alerts WHERE id=?", (alert_id,))


# ── RISK ITEMS ───────────────────────────────────────────────────────

def insert_risk_item(customer_id, category, description, probability=3, impact=3, mitigation=""):
    with get_connection() as conn:
        conn.execute("""INSERT INTO risk_items
            (customer_id, category, description, probability, impact, mitigation, status, created_at)
            VALUES (?,?,?,?,?,?,'Open',?)""",
            (customer_id, category, description, probability, impact, mitigation, _now()))


def get_risk_items(customer_id=None):
    with get_connection() as conn:
        if customer_id:
            rows = conn.execute("SELECT * FROM risk_items WHERE customer_id=? ORDER BY created_at DESC",
                                (customer_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM risk_items ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════════════
# CLIENT CONFIG — Save / Load full project config per client
# ══════════════════════════════════════════════════════════════════════

def save_client_config(customer_id, config_dict, name="Default"):
    """Save or update a client's full project configuration."""
    now = _now()
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM configurations WHERE customer_id=? AND name=?",
            (customer_id, name)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE configurations SET config_json=?, updated_at=? WHERE id=?",
                (json.dumps(config_dict), now, existing["id"])
            )
        else:
            conn.execute(
                "INSERT INTO configurations (customer_id, name, config_json, created_at, updated_at) VALUES (?,?,?,?,?)",
                (customer_id, name, json.dumps(config_dict), now, now)
            )


def load_client_config(customer_id, name="Default"):
    """Load a client's saved project configuration. Returns dict or None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT config_json FROM configurations WHERE customer_id=? AND name=? ORDER BY updated_at DESC LIMIT 1",
            (customer_id, name)
        ).fetchone()
        if row and row["config_json"]:
            try:
                return json.loads(row["config_json"])
            except Exception:
                return None
    return None


def get_all_client_profiles():
    """Return all customers with their latest config summary for the client switcher."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT c.id, c.name, c.company, c.state, c.city, c.status,
                   cfg.config_json, cfg.updated_at as config_updated
            FROM customers c
            LEFT JOIN configurations cfg ON cfg.customer_id = c.id AND cfg.name = 'Default'
            ORDER BY c.updated_at DESC
        """).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if d.get("config_json"):
                try:
                    cfg_data = json.loads(d["config_json"])
                    d["capacity_tpd"] = cfg_data.get("capacity_tpd", 0)
                    d["investment_cr"] = cfg_data.get("investment_cr", 0)
                    d["project_name"] = cfg_data.get("project_name", "")
                except Exception:
                    d["capacity_tpd"] = 0
                    d["investment_cr"] = 0
                    d["project_name"] = ""
            else:
                d["capacity_tpd"] = 0
                d["investment_cr"] = 0
                d["project_name"] = ""
            del d["config_json"]
            result.append(d)
        return result


def seed_client_if_missing(name, company, seed_config, customer_data=None):
    """Insert a client + config only if they don't exist yet. Returns customer_id."""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM customers WHERE company=? OR name=?", (company, name)
        ).fetchone()
        if existing:
            return existing["id"]

    data = {"name": name, "company": company, "status": "Active"}
    if customer_data:
        data.update(customer_data)
    cid = insert_customer(data)
    save_client_config(cid, seed_config)
    return cid
