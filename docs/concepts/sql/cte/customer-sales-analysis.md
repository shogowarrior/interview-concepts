# Customer Sales Analysis Using CTE

## ✅ Scenario Use CTE to avoid repeating complex logic (non-recursive)

Let’s say you have a `sales` table:

| sale\_id | customer\_id | amount | sale\_date |
| -------- | ------------ | ------ | ---------- |
| 1        | 100          | 500    | 2024-01-01 |
| 2        | 101          | 700    | 2024-01-03 |
| 3        | 100          | 200    | 2024-02-01 |
| 4        | 102          | 300    | 2024-02-10 |
| 5        | 100          | 1000   | 2024-03-01 |

You want to:

1. Calculate **total sales per customer**,
2. Then get customers with **above-average** total sales.

---

### ✅ CTE version (clean and readable)

```sql
WITH customer_totals AS (
    SELECT customer_id, SUM(amount) AS total_sales
    FROM sales
    GROUP BY customer_id
),
average_total AS (
    SELECT AVG(total_sales) AS avg_sales
    FROM customer_totals
)
SELECT ct.*
FROM customer_totals ct, average_total at
WHERE ct.total_sales > at.avg_sales;
```

---

### Why CTE helps

* You calculate **total sales per customer once**, and reuse it.
* You **can't use `AVG(SUM(...))` directly** in one query without nesting it awkwardly.
* If you tried doing it in one SELECT with subqueries, it gets messy, like this:

---

### ✅ Windowing version (clean and readable)

```sql
SELECT customer_id, total_sales
FROM (
    SELECT customer_id,
           SUM(amount) AS total_sales,
           AVG(SUM(amount)) OVER () AS avg_sales
    FROM sales
    GROUP BY customer_id
) AS t
WHERE total_sales > avg_sales;
```
