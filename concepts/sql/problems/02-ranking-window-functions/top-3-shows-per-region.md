# Top 3 Shows per Region

## Question
Table `viewership(user_id, show_id, region, watch_time)`.
Find the **top 3 most watched shows per region** by total minutes.

## Answer

```sql
SELECT region, show_id, total_watch_time
FROM (
  SELECT
    region,
    show_id,
    SUM(watch_time) AS total_watch_time,
    DENSE_RANK() OVER (PARTITION BY region ORDER BY SUM(watch_time) DESC) AS rnk
  FROM viewership
  GROUP BY region, show_id
) t
WHERE rnk <= 3;
```

## Notes
- Uses `DENSE_RANK()` for ranking within each region
- `DENSE_RANK()` vs `RANK()`: no gaps in ranking (1,2,2,3 vs 1,2,2,4)
- Groups by region and show first, then applies ranking window function
- Common pattern for "top N per category" problems