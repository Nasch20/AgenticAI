
import sqlite3
from pathlib import Path

# Retrouver automatiquement la racine du projet AgenticAI
ROOT = Path(__file__).resolve().parents[2]

# Connexion à la base SQLite
conn = sqlite3.connect(ROOT / "data" / "boutique.sqlite")

# 1. Requête de référence correcte pour C08
reference_query = """
SELECT COALESCE(SUM(o.quantity_product * p.price), 0)
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date > '2000-09-24'
  AND c.birth_date <= '2001-09-24';
"""

# 2. Requête incorrecte de GPT-OSS-20B
wrong_query = """
SELECT COALESCE(SUM(o.quantity_product * p.price), 0)
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date BETWEEN '2001-09-23' AND '2001-09-24';
"""

reference = conn.execute(reference_query).fetchone()[0]
wrong = conn.execute(wrong_query).fetchone()[0]

print("Reference:", reference, "cents")
print("Wrong result:", wrong, "cents")
print("Difference:", reference - wrong, "cents")

# 3. Requête diagnostic : clients oubliés par GPT-OSS-20B
diagnostic_query = """
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

rows = conn.execute(diagnostic_query).fetchall()

print("\nCustomers missed by GPT-OSS-20B:")
for customer_id, birth_date, revenue in rows:
    print(customer_id, birth_date, revenue)

missing_total = sum(row[2] for row in rows)

print("\nTotal missed revenue:", missing_total, "cents")
print("Difference explained:", missing_total == reference - wrong)

# 4. Requête incorrecte de Dots 3
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

dots_value = conn.execute(dots_query).fetchone()[0]

print("\nDots 3 result:", dots_value, "cents")
print("Dots 3 difference:", reference - dots_value, "cents")
print("Same wrong value:", dots_value == wrong)

# Diagnostic des clients oublies par Dots 3
dots_delta_query = """
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

dots_rows = conn.execute(dots_delta_query).fetchall()
dots_missing_total = sum(row[2] for row in dots_rows)

print("Dots 3 missed customers:")
for row in dots_rows:
    print(row)

print("Dots 3 missing revenue:", dots_missing_total, "cents")
print("Dots 3 difference explained:",
      dots_missing_total == reference - dots_value)

conn.close()
