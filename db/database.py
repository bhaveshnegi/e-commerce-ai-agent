"""
SQLite database helpers for orders and tickets.
Both databases are auto-created on first run.
"""
import os
import sqlite3
import uuid
from datetime import datetime
import config


# ── Ensure db/ directory exists ───────────────────────────────────────────────
os.makedirs(config.DB_DIR, exist_ok=True)


def _get_orders_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.ORDERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _get_tickets_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.TICKETS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Init ───────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create tables if they don't exist."""
    with _get_orders_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id      TEXT PRIMARY KEY,
                mobile        TEXT NOT NULL,
                status        TEXT NOT NULL,
                product       TEXT NOT NULL,
                delivery_date TEXT
            )
        """)
    print("[DB] orders.db initialized")

    with _get_tickets_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id  TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                mobile     TEXT NOT NULL,
                issue      TEXT NOT NULL,
                order_id   TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
    print("[DB] tickets.db initialized")


# ── Orders ────────────────────────────────────────────────────────────────────

def get_order(order_id: str, mobile: str) -> dict | None:
    """
    Look up an order by order_id AND mobile number.
    Returns a dict with order details, or None if not found.
    """
    with _get_orders_conn() as conn:
        row = conn.execute(
            "SELECT * FROM orders WHERE order_id = ? AND mobile = ?",
            (order_id.upper().strip(), mobile.strip()),
        ).fetchone()
    return dict(row) if row else None


def order_exists(order_id: str) -> bool:
    with _get_orders_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM orders WHERE order_id = ?",
            (order_id.upper().strip(),),
        ).fetchone()
    return row is not None


# ── Tickets ───────────────────────────────────────────────────────────────────

def create_ticket(name: str, mobile: str, issue: str, order_id: str = "") -> str:
    """
    Insert a new support ticket and return the generated ticket_id.
    ticket_id format: TKT-<8 char UUID prefix>
    """
    ticket_id  = "TCKT" + uuid.uuid4().hex[:4].upper()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _get_tickets_conn() as conn:
        conn.execute(
            "INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?)",
            (ticket_id, name.strip(), mobile.strip(), issue.strip(), order_id.strip(), created_at),
        )
    return ticket_id


def get_ticket(ticket_id: str) -> dict | None:
    with _get_tickets_conn() as conn:
        row = conn.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?",
            (ticket_id.upper().strip(),),
        ).fetchone()
    return dict(row) if row else None
