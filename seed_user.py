"""One-off script: insert a single realistic random Indian user."""

import random
from datetime import datetime

from werkzeug.security import generate_password_hash

from database.db import get_db

FIRST_NAMES = [
    "Rahul", "Priya", "Amit", "Sneha", "Vikram", "Ananya", "Arjun", "Kavya",
    "Rohan", "Divya", "Karthik", "Meera", "Aditya", "Pooja", "Sanjay",
    "Aishwarya", "Manish", "Nisha", "Suresh", "Deepika", "Rajesh", "Swati",
    "Naveen", "Lakshmi", "Imran", "Fatima", "Gurpreet", "Harpreet",
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Gupta", "Mehta",
    "Singh", "Kumar", "Rao", "Joshi", "Das", "Bose", "Chowdhury", "Pillai",
    "Menon", "Bhat", "Kapoor", "Malhotra", "Desai", "Naidu", "Khan",
]


def generate_user():
    """Return (name, email, password_hash) for a random Indian user."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    suffix = random.randint(10, 999)
    email = f"{first.lower()}.{last.lower()}{suffix}@gmail.com"
    password_hash = generate_password_hash("password123")
    return name, email, password_hash


def email_exists(conn, email):
    row = conn.execute(
        "SELECT 1 FROM users WHERE email = ?", (email,)
    ).fetchone()
    return row is not None


def main():
    conn = get_db()

    name, email, password_hash = generate_user()
    while email_exists(conn, email):
        name, email, password_hash = generate_user()

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) "
        "VALUES (?, ?, ?, ?)",
        (name, email, password_hash, datetime.now().isoformat(sep=" ", timespec="seconds")),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    print("User created:")
    print(f"  id    : {user_id}")
    print(f"  name  : {name}")
    print(f"  email : {email}")


if __name__ == "__main__":
    main()
