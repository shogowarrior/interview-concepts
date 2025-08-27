# SQL Optimization Challenges

## Query Performance Optimization

### Example: Efficient DAU Calculation
Optimizing daily active users query for large datasets:

```sql
-- Optimized version with proper partitioning
SELECT
  DATE(event_ts) AS activity_date,
  COUNT(DISTINCT user_id) AS daily_active_users
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '30' DAY  -- Limit date range
  AND event_ts < CURRENT_DATE
GROUP BY DATE(event_ts)
ORDER BY activity_date;

-- Alternative using approximate counting for very large datasets
SELECT
  DATE(event_ts) AS activity_date,
  APPROX_COUNT_DISTINCT(user_id) AS approx_dau
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY DATE(event_ts);
```

## Indexing Strategy

### Example: Optimizing Watch History Queries
Key indexes for common Netflix query patterns:

```sql
-- Composite index for user activity queries
CREATE INDEX idx_user_date ON watch_events (user_id, event_ts);

-- Covering index for content analytics
CREATE INDEX idx_content_metrics ON watch_events (show_id, event_ts, watch_time);

-- Partial index for active users only
CREATE INDEX idx_recent_activity ON watch_events (user_id, event_ts)
WHERE event_ts >= CURRENT_DATE - INTERVAL '90' DAY;
```

## Partitioning Strategy

### Example: Time-based Partitioning
Optimizing for time-series queries:

```sql
-- Partition by day for efficient date range queries
CREATE TABLE watch_events (
  event_id BIGINT,
  user_id BIGINT,
  show_id BIGINT,
  event_ts TIMESTAMP,
  watch_time INT
)
PARTITION BY DATE(event_ts);

-- Query benefits from partition pruning
SELECT COUNT(DISTINCT user_id)
FROM watch_events
WHERE event_ts >= '2025-01-01'
  AND event_ts < '2025-02-01';
```

## Aggregation Optimization

### Example: Efficient Top-N Queries
Optimizing ranking queries with large datasets:

```sql
-- Use LIMIT with proper ordering for Top-N
SELECT show_id, SUM(watch_time) AS total_watch_time
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY show_id
ORDER BY total_watch_time DESC
LIMIT 10;

-- Pre-aggregate for frequently accessed metrics
CREATE MATERIALIZED VIEW daily_show_metrics AS
SELECT
  DATE(event_ts) AS watch_date,
  show_id,
  COUNT(DISTINCT user_id) AS unique_viewers,
  SUM(watch_time) AS total_watch_time
FROM watch_events
GROUP BY DATE(event_ts), show_id;
```

## Join Optimization

### Example: Optimizing Multi-Table Analytics
Efficient joins for cross-dimensional analysis:

```sql
-- Use covering indexes and proper join order
SELECT
  u.country,
  s.genre,
  COUNT(DISTINCT w.user_id) AS unique_users,
  SUM(w.watch_time) AS total_watch_time
FROM watch_events w
JOIN users u ON w.user_id = u.user_id
JOIN shows s ON w.show_id = s.show_id
WHERE w.event_ts >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY u.country, s.genre;

-- Consider denormalization for performance-critical queries
CREATE TABLE user_watch_summary (
  user_id BIGINT,
  country STRING,
  total_watch_time BIGINT,
  favorite_genre STRING,
  last_watch_date DATE
);
```

## Performance Monitoring

### Example: Query Execution Analysis
Monitoring slow queries and bottlenecks:

```sql
-- Identify slow queries
SELECT
  query_id,
  query_text,
  execution_time_ms,
  rows_processed
FROM query_history
WHERE execution_time_ms > 5000
ORDER BY execution_time_ms DESC;

-- Analyze table access patterns
EXPLAIN ANALYZE
SELECT COUNT(DISTINCT user_id)
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '1' DAY;
```

## Notes
- **Partitioning**: Use date-based partitioning for time-series data
- **Indexing**: Balance between read performance and write overhead
- **Approximate functions**: Use for large-scale analytics when exact precision isn't required
- **Materialized views**: Pre-compute expensive aggregations for dashboard queries
- **Query optimization**: Always analyze execution plans for expensive queries