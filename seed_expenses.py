"""One-off script: seed realistic dummy expenses for a given user.

Usage: python seed_expenses.py <user_id> <count> <months>
"""

import random
import sys
from datetime import date, timedelta

from database.db import get_db

# Per-category config: (amount_min, amount_max, weight, descriptions).
# Weights set rough proportions — Food most common, Health/Entertainment least.
CATEGORY_CONFIG = {
    "Food": (50, 800, 30, [
        "Lunch at local dhaba", "Groceries from kirana store", "Swiggy order",
        "Zomato dinner", "Vegetables from sabzi mandi", "Chai and samosa",
        "Weekend biryani", "Milk and bread",
    ]),
    "Transport": (20, 500, 20, [
        "Auto rickshaw fare", "Ola cab ride", "Metro recharge",
        "Petrol top-up", "Uber to office", "Bus pass", "Local train ticket",
    ]),
    "Bills": (200, 3000, 18, [
        "Electricity bill", "Mobile recharge", "Broadband bill",
        "DTH recharge", "Water bill", "Gas cylinder booking",
    ]),
    "Shopping": (200, 5000, 15, [
        "Myntra clothing", "Amazon order", "Flipkart purchase",
        "Footwear from Bata", "Big Bazaar haul", "Reliance Trends shopping",
    ]),
    "Other": (50, 1000, 9, [
        "Temple donation", "Gift for friend", "Stationery",
        "Salon visit", "Miscellaneous", "App subscription",
    ]),
    "Health": (100, 2000, 4, [
        "Apollo pharmacy", "Doctor consultation", "Diagnostic lab test",
        "Gym membership", "Medicines",
    ]),
    "Entertainment": (100, 1500, 4, [
        "PVR movie tickets", "Netflix subscription", "BookMyShow event",
        "Bowling with friends", "Concert ticket",
    ]),
}


def parse_args(argv):
    if len(argv) != 3:
        return None
    try:
        return int(argv[0]), int(argv[1]), int(argv[2])
    except ValueError:
        return None


def user_exists(conn, user_id):
    return conn.execute(
        "SELECT 1 FROM users WHERE id = ?", (user_id,)
    ).fetchone() is not None


def random_date_within(months):
    """Return a random date between today and `months` ago (~30 days/month)."""
    span_days = months * 30
    offset = random.randint(0, span_days)
    return date.today() - timedelta(days=offset)


def generate_expenses(user_id, count, months):
    categories = list(CATEGORY_CONFIG.keys())
    weights = [CATEGORY_CONFIG[c][2] for c in categories]
    rows = []
    for _ in range(count):
        category = random.choices(categories, weights=weights, k=1)[0]
        amt_min, amt_max, _w, descriptions = CATEGORY_CONFIG[category]
        amount = round(random.uniform(amt_min, amt_max), 2)
        description = random.choice(descriptions)
        expense_date = random_date_within(months).isoformat()
        rows.append((user_id, amount, category, expense_date, description))
    return rows


def main():
    args = parse_args(sys.argv[1:])
    if args is None:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        return

    user_id, count, months = args

    conn = get_db()
    if not user_exists(conn, user_id):
        conn.close()
        print(f"No user found with id {user_id}.")
        return

    rows = generate_expenses(user_id, count, months)

    try:
        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        conn.close()
        print(f"Insert failed, rolled back all changes: {exc}")
        return

    dates = sorted(r[3] for r in rows)
    sample = conn.execute(
        """
        SELECT id, amount, category, date, description
        FROM expenses
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (user_id,),
    ).fetchall()
    conn.close()

    print(f"Inserted {len(rows)} expenses for user {user_id}.")
    print(f"Date range: {dates[0]} to {dates[-1]}")
    print("Sample of 5 inserted records:")
    for r in sample:
        print(
            f"  #{r['id']}  ₹{r['amount']:>8.2f}  {r['category']:<14} "
            f"{r['date']}  {r['description']}"
        )


if __name__ == "__main__":
    main()
