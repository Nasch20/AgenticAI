
import sqlite3
from pathlib import Path

# Project root directory
ROOT = Path(__file__).resolve().parents[2]

# Connect to the TD1 SQLite database
conn = sqlite3.connect(ROOT / "data" / "boutique.sqlite")

# 1. Correct reference query for C08
reference_query = """
SELECT COALESCE(SUM(o.quantity_product * p.price), 0)
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date > '2000-09-24'
  AND c.birth_date <= '2001-09-24';
"""

# 2. Incorrect query from GPT-OSS-20B
gpt_query = """
SELECT COALESCE(SUM(o.quantity_product * p.price), 0)
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date BETWEEN '2001-09-23' AND '2001-09-24';
"""

# 3. Incorrect query from Dots 3
dots_query = """
SELECT COALESCE(SUM(o.quantity_product * p.price), 0)
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date IS NOT NULL
  AND CAST(SUBSTR('2026-09-24', 1, 4) AS INTEGER)
      - CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) = 25
  AND SUBSTR(c.birth_date, 6, 2) = '09'
  AND SUBSTR(c.birth_date, 9, 2) = '24';
"""

# 4. Execute the three queries
reference = conn.execute(reference_query).fetchone()[0]
gpt_value = conn.execute(gpt_query).fetchone()[0]
dots_value = conn.execute(dots_query).fetchone()[0]

# 5. Diagnostic queries: identify missed customers
gpt_diagnostic = """
SELECT
    c.customer_id,
    c.birth_date,
    SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date > '2000-09-24'
  AND c.birth_date <= '2001-09-24'
  AND c.birth_date NOT BETWEEN '2001-09-23' AND '2001-09-24'
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;
"""

dots_diagnostic = """
SELECT
    c.customer_id,
    c.birth_date,
    SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date > '2000-09-24'
  AND c.birth_date <= '2001-09-24'
  AND c.birth_date <> '2001-09-24'
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;
"""

# 6. Display both models with the same format
def display_diagnostic(model_name, model_value, diagnostic_query):
    rows = conn.execute(diagnostic_query).fetchall()
    missing_total = sum(row[2] for row in rows)

    print(f"MODEL: {model_name}")

    print(f"Reference: {reference} cents")
    print(f"Model result: {model_value} cents")
    print(f"Difference: {reference - model_value} cents")

    print(f"\nCustomers missed by {model_name}:")
    for customer_id, birth_date, revenue in rows:
        print(f"{customer_id} | {birth_date} | {revenue} cents")

    print(f"\nNumber of missed customers: {len(rows)}")
    print(f"Total missed revenue: {missing_total} cents")
    print(f"Difference explained: {missing_total == reference - model_value}")


display_diagnostic("GPT-OSS-20B", gpt_value, gpt_diagnostic)
display_diagnostic("Dots 3", dots_value, dots_diagnostic)

print(f"\nSame wrong value: {gpt_value == dots_value}")

conn.close()
