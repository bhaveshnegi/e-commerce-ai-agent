"""
Seed sample orders into orders.db for testing.
Only inserts if the table is empty.
"""
import sqlite3
import config
from db import database


SAMPLE_ORDERS = [
    ("ORD001", "9999999999", "shipped",    "Wireless Headphones",      "2026-04-02"),
    ("ORD002", "8888888888", "delivered",  "Running Shoes",            "2026-03-25"),
    ("ORD003", "7777777777", "processing", "Smart Watch",              "2026-04-05"),
    ("ORD004", "6666666666", "cancelled",  "Laptop Stand",             None),
    ("ORD005", "5555555555", "shipped",    "Bluetooth Speaker",        "2026-04-03"),
    ("ORD006", "4444444444", "delivered",  "Cotton T-Shirt (Pack of 3)","2026-03-20"),
    ("ORD007", "3333333333", "processing", "Gaming Mouse",             "2026-04-07"),
    ("ORD008", "2222222222", "shipped",    "Yoga Mat",                 "2026-04-01"),
    ("ORD009", "1111111111", "delivered",  "Stainless Steel Bottle",   "2026-03-22"),
    ("ORD010", "9876543210", "processing", "Winter Jacket",            "2026-04-10"),
]


def seed_orders() -> None:
    """Insert sample orders only if the orders table is empty."""
    with sqlite3.connect(config.ORDERS_DB_PATH) as conn:
        count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        if count > 0:
            print(f"[Seed] Orders already seeded ({count} rows). Skipping.")
            return
        conn.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
            SAMPLE_ORDERS,
        )
        print(f"[Seed] Inserted {len(SAMPLE_ORDERS)} sample orders.")
