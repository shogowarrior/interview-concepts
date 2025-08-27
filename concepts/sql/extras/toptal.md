# SQL Interview Questions: Streaming & Media Analytics

This comprehensive guide covers SQL interview questions specifically tailored for streaming and media companies like Netflix, focusing on user analytics, content performance, and business metrics.

## Table of Contents

- [Beginner Level](#beginner-level)
- [Intermediate Level](#intermediate-level)
- [Advanced Level](#advanced-level)
- [Optimization Challenges](#optimization-challenges)
- [Cross-References](#cross-references)

## Beginner Level

### 1 Daily Active Users (DAU)

***Business Context: DAU***

     User engagement metrics for streaming platforms.

***Question***

     You have a table `user_activity`:

     | user_id | activity_date | activity_type |
     |---------|---------------|---------------|
     | 101     | 2025-08-01    | play          |
     | 101     | 2025-08-01    | pause         |
     | 102     | 2025-08-01    | play          |
     | 103     | 2025-08-02    | play          |

     Write a query to find the number of **unique active users per day**.

***Solution***

```sql
SELECT
    activity_date,
    COUNT(DISTINCT user_id) AS daily_active_users
FROM user_activity
GROUP BY activity_date
ORDER BY activity_date;
```

***Learning Objectives***

    - Basic aggregation with `COUNT(DISTINCT)`
    - Grouping data by date
    - Understanding user activity metrics

***Related Concepts***

 [`aggregation-functions.md`](aggregation-functions.md)

---

### 2 Day-1 Retention

***Business Context***

     User retention analysis for subscription services.

***Question***

     From `user_signup(user_id, signup_date)` and `user_activity(user_id, activity_date)`, calculate **Day-1 retention** (users who signed up on Day X and came back on Day X+1).

***Solution***

```sql
SELECT
    s.signup_date,
    COUNT(DISTINCT a.user_id) * 1.0 / COUNT(DISTINCT s.user_id) AS day1_retention
FROM user_signup s
LEFT JOIN user_activity a
    ON s.user_id = a.user_id
    AND a.activity_date = DATE_ADD(s.signup_date, INTERVAL 1 DAY)
GROUP BY s.signup_date;
```

***Learning Objectives***

    - Cohort analysis patterns
    - Percentage calculations with joins
    - Understanding retention metrics

***Related Concepts***

 [`joins.md`](joins.md), [`aggregation-functions.md`](aggregation-functions.md)

## Intermediate Level

### 3 Most Watched Show per Day

***Business Context***

     Content popularity analysis.

***Question***

     Table `watch_history`:

     | user_id | show_id | watch_date | watch_time_minutes |
     |---------|---------|------------|-------------------|
     | 1       | A       | 2025-08-01 | 30                |
     | 2       | A       | 2025-08-01 | 50                |
     | 3       | B       | 2025-08-01 | 80                |

     Find the **most watched show per day** (based on total minutes).

***Solution***

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

***Learning Objectives***

    - Window functions for ranking
    - Subquery patterns
    - Top-N per category problems

***Related Concepts***

 [`window-functions-overview.md`](window-functions-overview.md), [`ranking-functions.md`](ranking-functions.md)

---

### 4 Top 3 Shows per Region

***Business Context***

     Regional content performance analysis.

***Question***

     Table `viewership(user_id, show_id, region, watch_time)`. Find the **top 3 most watched shows per region** by total minutes.

***Solution***

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

***Learning Objectives***

    - Difference between RANK() and DENSE_RANK()
    - Multi-level partitioning
    - Top-N queries per category

***Related Concepts***

 [`window-functions-overview.md`](window-functions-overview.md), [`ranking-functions.md`](ranking-functions.md)

---

### 5 Consecutive Days Watching

***Business Context***

     User engagement streak analysis.

***Question***

     From `user_activity(user_id, activity_date)`, find users who have watched content for **3 consecutive days**.

***Solution***

```sql
SELECT DISTINCT user_id
FROM (
    SELECT
        user_id,
        activity_date,
        LAG(activity_date,1) OVER (PARTITION BY user_id ORDER BY activity_date) AS prev_day,
        LAG(activity_date,2) OVER (PARTITION BY user_id ORDER BY activity_date) AS prev2_day
    FROM user_activity
) t
WHERE DATEDIFF(activity_date, prev_day) = 1
AND DATEDIFF(prev_day, prev2_day) = 1;
```

***Learning Objectives***

    - Using LAG() for sequential analysis
    - Date arithmetic in SQL
    - Streak detection patterns

***Related Concepts***

 [`navigation-functions.md`](navigation-functions.md), [`window-functions-overview.md`](window-functions-overview.md)

## Advanced Level

### 6 Heavy Watchers Retention (CTE)

***Business Context***

Advanced user segmentation and retention.

***Question***

Find users who watched >100 minutes in a day, and then find how many of them watched again the next day.

***Solution***

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

***Learning Objectives***

- Common Table Expressions (CTEs)
- Multi-step data transformation
- Advanced retention analysis

***Related Concepts***

 [`cte-overview.md`](cte-overview.md)

---

### 7 Content Hierarchy (Recursive CTE)

***Business Context***

Managing hierarchical content structures.

***Question***

Model content hierarchy (seasons, episodes) using recursive CTEs.

***Solution***

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

***Learning Objectives***

- Recursive CTE patterns
- Hierarchical data modeling
- Tree traversal in SQL

***Related Concepts***

 [`cte-overview.md`](cte-overview.md)

---

### 8 Percentile Analysis

***Business Context***

Statistical analysis of user behavior.

***Question***

Find the top 1% of users by total watch time.

***Solution***

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

***Learning Objectives***

- Statistical functions in SQL
- Percentile calculations
- User segmentation

***Related Concepts***

 [`advanced-window-functions.md`](advanced-window-functions.md)

---

### 9 Recommendation Acceptance Rate

***Business Context***

Measuring recommendation system effectiveness.

***Question***

Measure how many recommended shows were actually watched.

***Solution***

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

***Learning Objectives***

- Complex join conditions with time windows
- Conditional aggregation
- A/B testing analysis patterns

***Related Concepts***

 [`joins.md`](joins.md), [`aggregation-functions.md`](aggregation-functions.md)

## Optimization Challenges

### 10 Efficient DAU Calculation

***Business Context***

Performance optimization for large-scale analytics.

***Question***

Optimizing daily active users query for large datasets.

***Solutions***

```sql
-- Optimized version with date range limiting
SELECT
    DATE(event_ts) AS activity_date,
    COUNT(DISTINCT user_id) AS daily_active_users
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '30' DAY
    AND event_ts < CURRENT_DATE
GROUP BY DATE(event_ts)
ORDER BY activity_date;

-- Approximate counting for very large datasets
SELECT
    DATE(event_ts) AS activity_date,
    APPROX_COUNT_DISTINCT(user_id) AS approx_dau
FROM watch_events
WHERE event_ts >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY DATE(event_ts);
```

#### Learning Objectives

- Query performance optimization
- Approximate vs exact calculations
- Date range filtering

***Related Concepts***

 [`sql-optimization-challenges.md`](sql-optimization-challenges.md)

---

### 11 Time-based Partitioning

***Business Context***

Database design for time-series data.

***Question***

Optimizing for time-series queries with partitioning.

***Solution***

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

***Learning Objectives***

- Database partitioning strategies
- Partition pruning
- Schema design for analytics

***Related Concepts***

 [`partitioning-sharding.md`](partitioning-sharding.md)

---

### 12 Efficient Top-N Queries

***Business Context***

Performance optimization for ranking queries.

***Question***

Optimizing ranking queries with large datasets.

***Solution***

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

***Learning Objectives***

- LIMIT clause optimization
- Materialized views
- Pre-aggregation strategies

***Related Concepts***

 [`sql-optimization-challenges.md`](sql-optimization-challenges.md)

## Cross-References

### Main SQL Concepts Covered

- **Aggregation Functions**: [`aggregation-functions.md`](aggregation-functions.md)
- **Window Functions**: [`window-functions-overview.md`](window-functions-overview.md)
- **Common Table Expressions**: [`cte-overview.md`](cte-overview.md)
- **Joins**: [`joins.md`](joins.md)
- **Subqueries**: [`subqueries.md`](subqueries.md)
- **Optimization**: [`sql-optimization-challenges.md`](sql-optimization-challenges.md)

### Business Domains

- **Streaming Analytics**: User engagement, content performance
- **Subscription Metrics**: Retention, churn analysis
- **Recommendation Systems**: Acceptance rate, personalization
- **Content Management**: Hierarchical data, catalog analytics

### Difficulty Progression

- **Beginner**: Basic aggregation, simple joins
- **Intermediate**: Window functions, ranking, date arithmetic
- **Advanced**: CTEs, recursive queries, statistical functions
- **Expert**: Complex joins, performance optimization, schema design

### Learning Path

1. Start with basic aggregation and joins
2. Learn window functions for advanced analytics
3. Master CTEs and subqueries for complex transformations
4. Study optimization techniques for production environments
5. Explore recursive patterns for hierarchical data

---

## This guide is designed for SQL interviews at streaming companies and covers the most common patterns encountered in data analyst and data engineer roles

## Appendix: Contributor Guidelines and Organizational Templates

## TopTal SQL Interview Questions

This directory contains SQL interview questions and coding challenges adapted from [TopTal's engineering blog](https://www.toptal.com/) and SQL interview preparation resources. Focus is on real-world interview scenarios and advanced SQL patterns.

## 📚 Content Overview

### Interview Question Categories

#### [data-analysis](data-analysis/) - *In Development*

- Business metrics and KPI calculations
- Customer segmentation and analytics
- Revenue and performance analysis
- A/B testing data analysis

#### [ranking-problems](ranking-problems/) - *In Development*

- Top-N queries and ranking patterns
- Percentile calculations and distributions
- Running totals and moving averages
- Competitive analysis queries

#### [complex-joins](complex-joins/) - *In Development*

- Multi-level hierarchical data
- Complex relationship traversals
- Data warehousing patterns
- ETL and data pipeline queries

## 🎯 Interview Question Structure

Each interview question follows this format:

### Problem Statement

Real-world business scenario requiring SQL solution

***Business Context***

- **Company**: Tech startup, e-commerce, SaaS platform
- **Data Scale**: Millions of users, billions of events
- **Performance Requirements**: Sub-second response time
- **Business Impact**: Revenue optimization, user engagement, fraud detection

### Schema Design

```sql
-- Production-ready table schemas
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    created_at TIMESTAMP,
    country VARCHAR(2),
    subscription_status VARCHAR(20)
) PARTITION BY created_at;

CREATE TABLE user_events (
    event_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    event_type VARCHAR(50),
    event_value DECIMAL(10,2),
    event_timestamp TIMESTAMP
) PARTITION BY event_timestamp;
```

### Sample Data

```sql
-- Representative dataset for testing
INSERT INTO users VALUES
(1, '2023-01-01', 'US', 'premium'),
(2, '2023-01-15', 'CA', 'basic');
```

#### Solution Requirements

- **Expected Output**: Specific format and columns
- **Performance Constraints**: Query must complete within time limits
- **Edge Cases**: Handle NULL values, empty results, data quality issues

### Optimal Solution

```sql
-- Production-ready SQL with performance considerations
WITH user_metrics AS (
    SELECT
        u.user_id,
        u.country,
        COUNT(ue.event_id) as event_count,
        SUM(ue.event_value) as total_value,
        AVG(ue.event_value) as avg_value
    FROM users u
    LEFT JOIN user_events ue ON u.user_id = ue.user_id
        AND ue.event_timestamp >= u.created_at
    WHERE u.subscription_status = 'premium'
    GROUP BY u.user_id, u.country
)
SELECT
    country,
    COUNT(*) as premium_users,
    AVG(event_count) as avg_events_per_user,
    SUM(total_value) as total_revenue
FROM user_metrics
GROUP BY country
ORDER BY total_revenue DESC;
```

### Performance Analysis

- **Query Execution Plan**: Index usage, join strategies
- **Optimization Opportunities**: Partitioning, materialized views
- **Scalability Considerations**: Data volume impact, memory usage

## 🔗 TopTal Source Material

Based on TopTal's SQL interview preparation articles:

- [SQL Interview Questions](https://www.toptal.com/sql/interview-questions)
- [Database Design Patterns](https://www.toptal.com/database)
- [Data Engineering Challenges](https://www.toptal.com/data-engineering)

## 📊 Difficulty Distribution

| Difficulty | Count | Focus Areas |
|------------|-------|-------------|
| 🟡 Intermediate | ~12 questions | Complex analytics, multi-table queries |
| 🟠 Advanced | ~8 questions | Window functions, CTEs, optimization |
| 🔴 Expert | ~5 questions | Large-scale data, performance tuning |

## 🎯 Interview Preparation Focus

### Common TopTal SQL Patterns

1. **Revenue Analytics** - Customer lifetime value, cohort analysis
2. **User Behavior Analysis** - Funnel analysis, retention metrics
3. **Performance Optimization** - Query tuning, index strategies
4. **Data Quality** - NULL handling, data validation
5. **Scalability** - Partitioning, query optimization for large datasets

### TopTal-Specific Preparation

- Focus on business context and real-world applications
- Emphasize performance and scalability considerations
- Practice explaining query logic and optimization decisions
- Understand trade-offs between different solution approaches

## 📝 Adding New Interview Questions

When adding TopTal-style questions:

1. Include complete business context and requirements
2. Provide production-ready schema with constraints
3. Include performance analysis and optimization notes
4. Tag with relevant SQL concepts and business domains
5. Reference original TopTal article when applicable

---

## Navigate back to [SQL Extras](../README.md) | [SQL Concepts](../../README.md)
