import os
import sqlite3

from werkzeug.security import generate_password_hash

# Database lives in the project root, resolved relative to this file so the
# path is stable regardless of the process working directory.
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "spendly.db")

# Fixed category list — keep in sync with the spec.
CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


def get_db():
    """Return a SQLite connection with dict-like rows and FK enforcement on.

    SQLite disables foreign keys by default, so PRAGMA foreign_keys must run
    on every connection.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not already exist. Safe to call repeatedly."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL NOT NULL,
            category    TEXT NOT NULL,
            date        TEXT NOT NULL,
            description TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()


def get_user_by_email(email):
    """Return the user row matching email, or None if no such user exists."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    """Return the user row matching id, or None if no such user exists."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row


def get_expenses_for_user(user_id):
    """Return all expense rows for a user, most recent first."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def create_user(name, email, password_hash):
    """Insert a new user and return the new row id."""
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def seed_db():
    """Insert demo data for development. Does nothing if users already exist."""
    conn = get_db()

    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
    )
    user_id = cursor.lastrowid

    # 8 expenses spread across the current month, covering every category
    # (Food appears twice to reach 8).
    sample_expenses = [
        (user_id, 12.50, "Food", "2026-06-02", "Lunch at cafe"),
        (user_id, 30.00, "Transport", "2026-06-03", "Monthly metro top-up"),
        (user_id, 85.75, "Bills", "2026-06-04", "Electricity bill"),
        (user_id, 45.00, "Health", "2026-06-06", "Pharmacy"),
        (user_id, 20.00, "Entertainment", "2026-06-08", "Movie tickets"),
        (user_id, 64.20, "Shopping", "2026-06-10", "New shoes"),
        (user_id, 9.99, "Other", "2026-06-11", "App subscription"),
        (user_id, 28.40, "Food", "2026-06-12", "Groceries"),
    ]
    conn.executemany(
        """
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        sample_expenses,
    )

    conn.commit()
    conn.close()
