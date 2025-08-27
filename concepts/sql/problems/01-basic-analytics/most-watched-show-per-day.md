# Most Watched Show per Day

## Question
Table `watch_history`:

| user_id | show_id | watch_date | watch_time_minutes |
|---------|---------|------------|-------------------|
| 1       | A       | 2025-08-01 | 30                |
| 2       | A       | 2025-08-01 | 50                |
| 3       | B       | 2025-08-01 | 80                |

Find the **most watched show per day** (based on total minutes).

## Answer

```sql
SELECT watch_date, show_id
FROM (
  SELECT
    watch_date,
    show_id,
    SUM(watch_time_minutes) AS total_watch_time,
    RANK() OVER (PARTITION BY watch_date ORDER BY SUM(watch_time_minutes) DESC) AS rnk
  FROM watch_history
  GROUP BY watch_date, show_id
) t
WHERE rnk = 1;
```

## Notes
- Uses window function `RANK()` to find the top show per day
- Groups by date and show first, then ranks within each date
- Basic ranking pattern for top-N per category problems