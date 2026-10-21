
import sqlite3
import csv

# C01 - Revenue from March 1 to June 1
sql = """
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN product p ON o.product_id = p.product_id
WHERE o.date >= '2026-03-01 00:00:00'
  AND o.date < '2026-06-01 00:00:00'
"""

# SQL calculation
with sqlite3.connect("file:data/boutique.sqlite?mode=ro", uri=True) as conn:
    result_sql = conn.execute(sql).fetchone()[0]

# Independent CSV calculation
with open("data/product.csv", newline="", encoding="utf-8-sig") as f:
    prices = {r["product_id"]: int(r["price"]) for r in csv.DictReader(f)}

with open("data/orders.csv", newline="", encoding="utf-8-sig") as f:
    result_csv = sum(
        int(r["quantity_product"]) * prices[r["product_id"]]
        for r in csv.DictReader(f)
        if "2026-03-01 00:00:00" <= r["date"] < "2026-06-01 00:00:00"
    )

print("C01 SQL:", result_sql)
print("C01 CSV:", result_csv)
print("Check:", "OK" if result_sql == result_csv else "ERROR")


# Save a verified reference
def save_reference(case_id, query, value):
    with open("reference-td1.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    for row in rows:
        if row["case_id"] == case_id:
            row["sql"] = " ".join(query.split())
            row["revenue_cents"] = str(value)

    with open("reference-td1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

if result_sql != result_csv:
    raise ValueError("C01 verification failed")

save_reference("C01", sql, result_sql)
print("C01 saved!")
