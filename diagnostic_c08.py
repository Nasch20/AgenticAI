
import sqlite3

# Connexion à la base utilisée pendant le TD1
conn = sqlite3.connect("data/boutique.sqlite")

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

conn.close()
