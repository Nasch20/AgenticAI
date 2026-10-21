
from pathlib import Path
from datetime import date
import csv
import json
import sqlite3

# TD1 - Step 1: calculate and check the 20 references
ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "boutique.sqlite"
OUTPUT = ROOT / "reference-td1.csv"

# Each question uses a period, a product list and/or an age condition.
CASES = {
    "C01": {"start": "2026-03-01 00:00:00", "end": "2026-06-01 00:00:00"},
    "C02": {"age_date": "2026-09-25"},
    "C03": {"start": "2026-01-01 00:00:00", "end": "2026-07-01 00:00:00", "products": ("a", "b", "c")},
    "C04": {"start": "2026-01-01 00:00:00", "end": "2026-10-01 00:00:00"},
    "C05": {"start": "2026-06-01 00:00:00", "end": "2026-06-02 00:00:00"},
    "C06": {"start": "2025-01-01 00:00:00", "end": "2026-01-01 00:00:00"},
    "C07": {"start": "2026-05-31 00:00:00", "end": "2026-06-01 00:00:00"},
    "C08": {"age_date": "2026-09-24"},
    "C09": {"age_date": "2026-09-26"},
    "C10": {"age_at_order": True},
    "C11": {"age_date": "2026-12-01"},
    "C12": {"products": ("a", "b", "c")},
    "C13": {"start": "2026-04-01 00:00:00", "end": "2026-05-01 00:00:00", "products": ("a", "c")},
    "C14": {"start": "2026-10-01 00:00:00", "end": "2026-12-01 00:00:00", "products": ("a", "b", "c")},
    "C15": {"start": "2026-03-01 00:00:00", "end": "2026-06-01 00:00:00", "age_date": "2026-09-25"},
    "C16": {"age_date": "2026-09-25", "products": ("a", "b", "c")},
    "C17": {"start": "2026-01-01 00:00:00", "end": "2026-07-01 00:00:00", "age_date": "2026-09-25", "products": ("a", "b", "c")},
    "C18": {"start": "2026-05-01 00:00:00", "end": "2026-06-01 00:00:00", "age_at_order": True},
    "C19": {"start": "2026-09-01 00:00:00", "end": "2026-10-01 00:00:00", "age_date": "2026-09-25", "products": ("d",)},
    "C20": {"start": "2026-06-01 00:00:00", "end": "2026-09-01 00:00:00"},
}


def make_sql(spec):
    """Build a complete SQL query without external parameters."""
    needs_customers = "age_date" in spec or spec.get("age_at_order", False)
    joins = "JOIN product p ON o.product_id = p.product_id"
    if needs_customers:
        joins += " JOIN customers c ON o.customer_id = c.customer_id"

    conditions = []
    if "start" in spec:
        conditions.append(f"o.date >= '{spec['start']}'")
        conditions.append(f"o.date < '{spec['end']}'")
    if "products" in spec:
        product_list = ", ".join(f"'{p}'" for p in spec["products"])
        conditions.append(f"o.product_id IN ({product_list})")

    if "age_date" in spec or spec.get("age_at_order", False):
        day = "o.date" if spec.get("age_at_order", False) else f"'{spec['age_date']}'"
        age = (
            f"(CAST(strftime('%Y', {day}) AS INTEGER) "
            f"- CAST(strftime('%Y', c.birth_date) AS INTEGER) "
            f"- (strftime('%m-%d', {day}) < strftime('%m-%d', c.birth_date)))"
        )
        conditions.append(f"{age} = 25")

    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    return (
        "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents "
        f"FROM orders o {joins}{where};"
    )


def age_on(birth, day):
    """Completed age, taking the birthday into account."""
    return day.year - birth.year - ((day.month, day.day) < (birth.month, birth.day))


def load_csv(name):
    with (ROOT / "data" / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def calculate_from_csv(spec, orders, prices, births):
    """Independent calculation directly from source CSVs, without SQLite."""
    total = 0
    target_date = date.fromisoformat(spec["age_date"]) if "age_date" in spec else None

    for order in orders:
        timestamp = order["date"]
        if "start" in spec and not (spec["start"] <= timestamp < spec["end"]):
            continue
        if "products" in spec and order["product_id"] not in spec["products"]:
            continue
        if target_date or spec.get("age_at_order", False):
            day = target_date or date.fromisoformat(timestamp[:10])
            if age_on(births[order["customer_id"]], day) != 25:
                continue
        total += int(order["quantity_product"]) * prices[order["product_id"]]

    return total


def main():
    questions_path = ROOT / "questions-td1.json"
    if questions_path.exists():
        with questions_path.open(encoding="utf-8") as f:
            expected = [q["id"] for q in json.load(f)["questions"]]
        if expected != list(CASES):
            raise ValueError("Question IDs do not match questions-td1.json")

    orders = load_csv("orders.csv")
    prices = {r["product_id"]: int(r["price"]) for r in load_csv("product.csv")}
    births = {r["customer_id"]: date.fromisoformat(r["birth_date"])
              for r in load_csv("customers.csv")}

    results = []
    mismatches = []
    with sqlite3.connect(DB.resolve().as_uri() + "?mode=ro", uri=True) as conn:
        for case_id, spec in CASES.items():
            sql = make_sql(spec)
            value_sql = conn.execute(sql).fetchone()[0]
            value_csv = calculate_from_csv(spec, orders, prices, births)
            ok = value_sql == value_csv
            print(f"{case_id}: SQL={value_sql:>8} | CSV={value_csv:>8} | {'OK' if ok else 'ERROR'}")
            results.append({"case_id": case_id, "sql": sql, "revenue_cents": value_sql})
            if not ok:
                mismatches.append(case_id)

    if mismatches:
        raise ValueError(f"Mismatches: {', '.join(mismatches)}. CSV not modified.")

    # Only replace the reference file if every independent check succeeded.
    temp_path = OUTPUT.with_suffix(".csv.tmp")
    with temp_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "sql", "revenue_cents"])
        writer.writeheader()
        writer.writerows(results)
    temp_path.replace(OUTPUT)
    print(f"\n20/20 checks OK. Saved: {OUTPUT.name}")
    print("Ask another group member to cross-check the answers before instructor validation.")


if __name__ == "__main__":
    main()
