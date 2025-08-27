# Ranking Window Functions Problems

This directory contains intermediate-level SQL problems that focus on window functions and ranking operations commonly asked in Netflix data engineering interviews.

## Navigation

- [Back to SQL Problems](../README.md)
- [Back to SQL Concepts](../../README.md)

## Problems

### [`top-3-shows-per-region.md`](top-3-shows-per-region.md)

Find the top 3 most watched shows per region using DENSE_RANK() window function for ranking within partitions.

### [`consecutive-days-watching.md`](consecutive-days-watching.md)

Identify users who have watched content for 3 consecutive days using LAG() window function and date arithmetic.

## Key Concepts Covered

- **Window Functions**: PARTITION BY, ORDER BY in OVER clauses
- **Ranking Functions**: DENSE_RANK() vs RANK() for top-N analysis
- **Navigation Functions**: LAG() for accessing previous rows
- **Date Arithmetic**: DATEDIFF() for consecutive day calculations
- **Partitioning**: Grouping data for per-category analysis

## Common Patterns

```sql
-- Top N per group using DENSE_RANK
SELECT category, item, metric
FROM (
  SELECT
    category,
    item,
    SUM(metric) AS total_metric,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(metric) DESC) AS rnk
  FROM data_table
  GROUP BY category, item
) t
WHERE rnk <= 3;

-- Consecutive days pattern with LAG
SELECT DISTINCT user_id
FROM (
  SELECT
    user_id,
    activity_date,
    LAG(activity_date, 1) OVER (PARTITION BY user_id ORDER BY activity_date) AS prev_day,
    LAG(activity_date, 2) OVER (PARTITION BY user_id ORDER BY activity_date) AS prev2_day
  FROM user_activity
) t
WHERE DATEDIFF(activity_date, prev_day) = 1
  AND DATEDIFF(prev_day, prev2_day) = 1;
```

## Interview Tips

- Choose DENSE_RANK() over RANK() when you need consecutive ranking without gaps
- Use PARTITION BY to create separate ranking contexts for each group
- Combine aggregation with window functions by wrapping in subqueries
- Consider date boundaries and NULL handling in consecutive day problems
- Practice both ranking and navigation window functions for comprehensive coverage
