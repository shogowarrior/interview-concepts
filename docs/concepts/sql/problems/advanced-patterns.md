# Advanced SQL Patterns

## CTE (Common Table Expressions)

### Example Heavy Watchers Retention

Find users who watched >100 minutes in a day, and then find how many of them watched again the next day.

```sql
WITH daily_watch AS (
  SELECT
    user_id,
    DATE(event_ts) AS watch_date,
    SUM(watch_time) AS total_minutes
  FROM watch_events
  GROUP BY user_id, DATE(event_ts)
),
heavy_watchers AS (
  SELECT user_id, watch_date
  FROM daily_watch
  WHERE total_minutes > 100
)
SELECT COUNT(DISTINCT h1.user_id) AS retained_users
FROM heavy_watchers h1
JOIN heavy_watchers h2
  ON h1.user_id = h2.user_id
  AND h2.watch_date = DATE_ADD(h1.watch_date, INTERVAL 1 DAY);
```

## Recursive CTEs

### Example Content Hierarchy

Model content hierarchy (seasons, episodes) using recursive CTEs:

```sql
WITH RECURSIVE content_hierarchy AS (
  -- Base case: top-level content
  SELECT
    content_id,
    parent_id,
    title,
    0 AS level,
    CAST(content_id AS VARCHAR) AS path
  FROM content
  WHERE parent_id IS NULL

  UNION ALL

  -- Recursive case: child content
  SELECT
    c.content_id,
    c.parent_id,
    c.title,
    ch.level + 1,
    CONCAT(ch.path, '>', c.content_id)
  FROM content c
  JOIN content_hierarchy ch ON c.parent_id = ch.content_id
)
SELECT * FROM content_hierarchy ORDER BY path;
```

## Advanced Window Functions

### Example Percentile Analysis

Find the top 1% of users by total watch time:

```sql
WITH user_totals AS (
  SELECT
    user_id,
    SUM(watch_time) AS total_watch_time
  FROM watch_events
  GROUP BY user_id
),
ranked AS (
  SELECT
    user_id,
    total_watch_time,
    PERCENT_RANK() OVER (ORDER BY total_watch_time DESC) AS pct_rank
  FROM user_totals
)
SELECT user_id, total_watch_time
FROM ranked
WHERE pct_rank <= 0.01;
```

## Complex Joins with Filtering

### Example Recommendation Acceptance Rate

Measure how many recommended shows were actually watched:

```sql
SELECT
  COUNT(DISTINCT CASE WHEN w.user_id IS NOT NULL THEN r.user_id END) * 100.0 /
  COUNT(DISTINCT r.user_id) AS acceptance_rate_pct
FROM recommendations r
LEFT JOIN watch_events w
  ON r.user_id = w.user_id
  AND r.show_id = w.show_id
  AND w.event_ts BETWEEN r.recommendation_ts
                     AND r.recommendation_ts + INTERVAL '24' HOUR;
```

## Notes

- CTEs improve readability and allow step-by-step problem solving
- Recursive CTEs handle hierarchical or tree-like data structures
- Advanced window functions like `PERCENT_RANK()` enable statistical analysis
- Complex joins with time-based filtering common in event analysis
