# SQL Optimization Challenges

This comprehensive guide focuses on query optimization, performance tuning, and efficient SQL patterns for large-scale data processing, with practical examples drawn from Netflix's streaming platform architecture.

## Query Performance Optimization

### Example: Efficient DAU Calculation
Optimizing daily active users query for large datasets with billions of watch events:

```sql
-- Optimized version with date range filtering and proper aggregation
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

### Example: Most Watched Show Analysis
Finding top content efficiently with proper aggregation:

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

## Indexing Strategy

### Example: Optimizing Watch History Queries
Key indexes for common Netflix query patterns with millions of users:

```sql
-- Composite index for user activity queries (most common access pattern)
CREATE INDEX idx_user_date ON watch_events (user_id, event_ts);

-- Covering index for content analytics (includes all columns needed)
CREATE INDEX idx_content_metrics ON watch_events (show_id, event_ts, watch_time);

-- Partial index for recent active users only (reduces index size)
CREATE INDEX idx_recent_activity ON watch_events (user_id, event_ts)
WHERE event_ts >= CURRENT_DATE - INTERVAL '90' DAY;

-- Hash index for exact lookups on high-cardinality columns
CREATE INDEX idx_user_hash ON users USING HASH (user_id);
```

## Partitioning Strategy

### Example: Time-based Partitioning
Optimizing for time-series queries across massive event data:

```sql
-- Partition by day for efficient date range queries
CREATE TABLE watch_events (
  event_id BIGINT,
  user_id BIGINT,
  show_id BIGINT,
  event_ts TIMESTAMP,
  watch_time INT,
  device_type STRING,
  region STRING
)
PARTITION BY DATE(event_ts);

-- Query benefits from partition pruning automatically
SELECT COUNT(DISTINCT user_id)
FROM watch_events
WHERE event_ts >= '2025-01-01'
  AND event_ts < '2025-02-01';

-- Subpartition by region for geo-specific queries
PARTITION BY DATE(event_ts), region;
```

## Aggregation Optimization

### Example: Efficient Top-N Queries
Optimizing ranking queries with large datasets using proper techniques:

```sql
-- Use LIMIT with proper ordering for Top-N (prevents full sort)
SELECT show_id, SUM(watch_time) AS total_watch_time
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY show_id
ORDER BY total_watch_time DESC
LIMIT 10;

-- Pre-aggregate for frequently accessed metrics (materialized view)
CREATE MATERIALIZED VIEW daily_show_metrics AS
SELECT
  DATE(event_ts) AS watch_date,
  show_id,
  COUNT(DISTINCT user_id) AS unique_viewers,
  SUM(watch_time) AS total_watch_time,
  AVG(watch_time) AS avg_watch_time
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '90' DAY
GROUP BY DATE(event_ts), show_id;

-- Refresh materialized view periodically
REFRESH MATERIALIZED VIEW daily_show_metrics;
```

## Join Optimization

### Example: Optimizing Multi-Table Analytics
Efficient joins for cross-dimensional analysis across users, content, and regions:

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
  last_watch_date DATE,
  PRIMARY KEY (user_id)
);
```

## Advanced Pattern Optimization

### Example: CTE Optimization for Complex Retention Analysis
Using CTEs for step-by-step optimization of complex user behavior analysis:

```sql
WITH daily_watch AS (
  SELECT
    user_id,
    DATE(event_ts) AS watch_date,
    SUM(watch_time) AS total_minutes
  FROM watch_events
  WHERE event_ts >= CURRENT_DATE - INTERVAL '30' DAY
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

### Example: Recursive CTE for Content Hierarchy
Optimizing hierarchical queries for content organization:

```sql
WITH RECURSIVE content_hierarchy AS (
  -- Base case: top-level content (shows/movies)
  SELECT
    content_id,
    parent_id,
    title,
    0 AS level,
    CAST(content_id AS VARCHAR) AS path
  FROM content
  WHERE parent_id IS NULL

  UNION ALL

  -- Recursive case: child content (seasons, episodes)
  SELECT
    c.content_id,
    c.parent_id,
    c.title,
    ch.level + 1,
    CONCAT(ch.path, '>', c.content_id)
  FROM content c
  JOIN content_hierarchy ch ON c.parent_id = ch.content_id
)
SELECT * FROM content_hierarchy
ORDER BY path;
```

## Performance Monitoring

### Example: Query Execution Analysis
Monitoring slow queries and bottlenecks in real-time:

```sql
-- Identify slow queries with execution metrics
SELECT
  query_id,
  query_text,
  execution_time_ms,
  rows_processed,
  bytes_scanned
FROM query_history
WHERE execution_time_ms > 5000
ORDER BY execution_time_ms DESC;

-- Analyze table access patterns and index usage
EXPLAIN ANALYZE
SELECT COUNT(DISTINCT user_id)
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '1' DAY;

-- Monitor query performance by user region
SELECT
  region,
  AVG(execution_time_ms) AS avg_query_time,
  COUNT(*) AS query_count
FROM query_logs
WHERE query_type = 'recommendation'
GROUP BY region;
```

## Learning Objectives

- Understand query execution plans and optimization techniques
- Design efficient indexes for high-throughput OLAP workloads
- Implement partitioning strategies for time-series data
- Optimize joins and aggregations for complex analytics
- Monitor query performance and identify bottlenecks
- Apply advanced SQL patterns for large-scale data processing

## Best Practices

### Data Distribution & Sharding
```sql
-- Hash-based sharding for user data distribution
CREATE TABLE user_events (
  user_id BIGINT,
  event_ts TIMESTAMP,
  event_type STRING,
  metadata JSONB
) PARTITION BY HASH(user_id) PARTITIONS 64;

-- Range-based sharding for time-series data
PARTITION BY RANGE(event_ts) (
  PARTITION p202401 VALUES LESS THAN ('2024-02-01'),
  PARTITION p202402 VALUES LESS THAN ('2024-03-01'),
  PARTITION p202403 VALUES LESS THAN ('2024-04-01')
);
```

### Query Result Caching
```sql
-- Cache expensive recommendation queries
SELECT user_id, show_id, recommendation_score
FROM user_recommendations
WHERE user_id = ?
  AND generated_at >= CURRENT_TIMESTAMP - INTERVAL '1' HOUR
ORDER BY recommendation_score DESC
LIMIT 50;

-- Use Redis/memcached for frequently accessed results
```

### Connection Pooling & Resource Management
```sql
-- Connection pool configuration for high-concurrency workloads
SET GLOBAL max_connections = 10000;
SET GLOBAL innodb_buffer_pool_size = '64G';

-- Query result streaming for large datasets
SELECT * FROM watch_events
WHERE event_ts >= '2025-01-01'
INTO OUTFILE '/tmp/results.csv'
FIELDS TERMINATED BY ',';
```

## Cross-References

- [Performance Optimization](../../system-design/performance-optimization.md)
- [SQL Learning Path](../README.md)
- [Advanced SQL Patterns](../advanced/advanced-sql-patterns.md)
- [System Architecture](../../system-design/system-architecture.md)

## Notes

- **Partitioning**: Use date-based partitioning for time-series data to enable partition pruning
- **Indexing**: Balance between read performance and write overhead; use covering indexes for common query patterns
- **Approximate functions**: Use `APPROX_COUNT_DISTINCT()` for large-scale analytics when exact precision isn't required
- **Materialized views**: Pre-compute expensive aggregations for dashboard and reporting queries
- **CTEs**: Break down complex queries into logical steps for better readability and optimization
- **Query optimization**: Always analyze execution plans (`EXPLAIN ANALYZE`) for expensive queries
- **Caching**: Implement multi-level caching (query result, application, database) for frequently accessed data
- **Monitoring**: Set up comprehensive monitoring for query performance, resource usage, and slow query detection

Navigate back to [SQL Concepts](../README.md) | [Concepts Overview](../../README.md)