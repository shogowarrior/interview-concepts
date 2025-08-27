# SQL Exercises from Wikibooks

A comprehensive collection of SQL exercises organized by difficulty level, designed to build practical SQL skills from basic concepts to advanced patterns. These exercises are adapted from real-world scenarios and interview problems, particularly focusing on analytics and data manipulation common in streaming platforms and business intelligence.

## Table of Contents

- [Beginner Level: Basic Analytics](#beginner-level-basic-analytics)
- [Intermediate Level: Window Functions & Ranking](#intermediate-level-window-functions--ranking)
- [Advanced Level: Complex Patterns & Optimization](#advanced-level-complex-patterns--optimization)

---

## Beginner Level: Basic Analytics

Exercises focusing on fundamental SQL operations including aggregation, grouping, and basic data manipulation.

### 1. Daily Active Users (DAU)

**Learning Objectives:**
- Understand basic aggregation with `COUNT DISTINCT`
- Practice `GROUP BY` with date-based grouping
- Learn to calculate user metrics per time period

**Question:**  
You have a table `user_activity`:

| user_id | activity_date | activity_type |
|---------|---------------|---------------|
| 101     | 2025-08-01    | play          |
| 101     | 2025-08-01    | pause         |
| 102     | 2025-08-01    | play          |
| 103     | 2025-08-02    | play          |

Write a query to find the number of **unique active users per day**.

**Solution:**
```sql
SELECT
  activity_date,
  COUNT(DISTINCT user_id) AS daily_active_users
FROM user_activity
GROUP BY activity_date
ORDER BY activity_date;
```

**Explanation:**
- Groups by day and counts distinct users
- Basic aggregation pattern for DAU calculation
- Common Netflix interview question for analytics basics

**Cross-references:**
- [Aggregate Functions](../aggregation/aggregate-functions.md)
- [SQL Concepts Overview](../README.md#core-sql-fundamentals)

### 2. Day-1 Retention

**Learning Objectives:**
- Practice self-joins with date arithmetic
- Calculate retention metrics using percentages
- Understand cohort analysis patterns

**Question:**  
From `user_signup(user_id, signup_date)` and `user_activity(user_id, activity_date)`, calculate **Day-1 retention** (users who signed up on Day X and came back on Day X+1).

**Solution:**
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

**Explanation:**
- Numerator: users active next day after signup
- Denominator: total signups for that day
- Uses `LEFT JOIN` with date filtering for the retention logic
- Common cohort analysis pattern in user analytics

**Cross-references:**
- [JOINs and Relationships](../joins/)
- [Aggregate Functions](../aggregation/aggregate-functions.md)

### 3. Most Watched Show per Day

**Learning Objectives:**
- Implement ranking without window functions
- Practice subqueries for top-N queries
- Understand content analytics patterns

**Question:**  
Table `watch_history`:

| user_id | show_id | watch_date | watch_time_minutes |
|---------|---------|------------|-------------------|
| 1       | A       | 2025-08-01 | 30                |
| 2       | A       | 2025-08-01 | 50                |
| 3       | B       | 2025-08-01 | 80                |

Find the **most watched show per day** (based on total minutes).

**Solution:**
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

**Explanation:**
- Uses window function `RANK()` to find the top show per day
- Groups by date and show first, then ranks within each date
- Basic ranking pattern for top-N per category problems

**Cross-references:**
- [Window Functions](../window-functions/)
- [Aggregate Functions](../aggregation/aggregate-functions.md)

---

## Intermediate Level: Window Functions & Ranking

Exercises focusing on advanced analytics using window functions, ranking, and navigation functions.

### 4. Top 3 Shows per Region

**Learning Objectives:**
- Master `DENSE_RANK()` vs `RANK()` functions
- Practice partitioning for grouped rankings
- Understand regional analytics patterns

**Question:**  
Table `viewership(user_id, show_id, region, watch_time)`.  
Find the **top 3 most watched shows per region** by total minutes.

**Solution:**
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

**Explanation:**
- Uses `DENSE_RANK()` for ranking within each region
- `DENSE_RANK()` vs `RANK()`: no gaps in ranking (1,2,2,3 vs 1,2,2,4)
- Groups by region and show first, then applies ranking window function
- Common pattern for "top N per category" problems

**Cross-references:**
- [Ranking Functions](../window-functions/postgresql-ranking-functions.md)
- [Window Functions Overview](../window-functions/window-functions-overview.md)

### 5. Consecutive Days Watching

**Learning Objectives:**
- Use navigation functions (`LAG`/`LEAD`) for pattern detection
- Implement streak analysis with window functions
- Practice date arithmetic for consecutive patterns

**Question:**  
From `user_activity(user_id, activity_date)`, find users who have watched content for **3 consecutive days**.

**Solution:**
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

**Explanation:**
- Uses `LAG()` window function to look back at previous activity dates
- `DATEDIFF()` checks for consecutive days (difference = 1)
- Alternative approach: use `ROW_NUMBER()` and date arithmetic for more complex streak detection
- Common pattern for "consecutive days" or "streak" problems

**Cross-references:**
- [Navigation Functions](../window-functions/postgresql-navigation-functions.md)
- [Common Table Expressions (CTEs)](../cte/)

---

## Advanced Level: Complex Patterns & Optimization

Exercises covering advanced SQL patterns including CTEs, recursive queries, and performance optimization techniques.

### 6. Heavy Watchers Retention (CTEs)

**Learning Objectives:**
- Build multi-step analysis using CTEs
- Implement complex retention calculations
- Practice CTE chaining for readability

**Question:**  
Find users who watched >100 minutes in a day, and then find how many of them watched again the next day.

**Solution:**
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

**Explanation:**
- Uses CTEs to break down the problem into logical steps
- First CTE calculates daily watch time per user
- Second CTE identifies heavy watchers
- Final query joins to find retention
- CTEs improve readability and allow step-by-step problem solving

**Cross-references:**
- [Common Table Expressions (CTEs)](../cte/)
- [CTE vs Window Functions](../cte/cte-vs-window-comparison.md)

### 7. Content Hierarchy (Recursive CTEs)

**Learning Objectives:**
- Implement recursive CTEs for hierarchical data
- Understand tree-like data structures in SQL
- Practice path generation and level calculation

**Question:**  
Model content hierarchy (seasons, episodes) using recursive CTEs.

**Solution:**
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

**Explanation:**
- Recursive CTE handles hierarchical or tree-like data structures
- Base case starts with root content (no parent)
- Recursive case builds the hierarchy level by level
- Generates path and level information for each item

**Cross-references:**
- [Common Table Expressions (CTEs)](../cte/)
- [Vacant Days Analysis](../cte/vacant-days-detailed.md)

### 8. Percentile Analysis (Advanced Window Functions)

**Learning Objectives:**
- Use statistical window functions like `PERCENT_RANK()`
- Implement percentile-based user segmentation
- Practice advanced ranking techniques

**Question:**  
Find the top 1% of users by total watch time.

**Solution:**
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

**Explanation:**
- `PERCENT_RANK()` enables statistical analysis
- Identifies top percentage of users by any metric
- Useful for user segmentation and targeting

**Cross-references:**
- [Advanced Concepts](../window-functions/postgresql-advanced-concepts.md)
- [Window Functions Overview](../window-functions/window-functions-overview.md)

### 9. Query Performance Optimization

**Learning Objectives:**
- Optimize queries for large datasets
- Use approximate functions for performance
- Implement date range filtering effectively

**Question:**  
Optimizing daily active users query for large datasets.

**Solution:**
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

**Explanation:**
- Date range filtering reduces data scanned
- `APPROX_COUNT_DISTINCT()` trades accuracy for performance
- Partitioning by date enables efficient queries

**Cross-references:**
- [SQL Optimization](../optimization/sql-optimization-challenges.md)
- [Advanced SQL Patterns](../advanced/advanced-sql-patterns.md)

### 10. Indexing Strategy

**Learning Objectives:**
- Design composite indexes for query patterns
- Understand covering indexes vs regular indexes
- Implement partial indexes for filtered data

**Question:**  
Key indexes for common Netflix query patterns.

**Solution:**
```sql
-- Composite index for user activity queries
CREATE INDEX idx_user_date ON watch_events (user_id, event_ts);

-- Covering index for content analytics
CREATE INDEX idx_content_metrics ON watch_events (show_id, event_ts, watch_time);

-- Partial index for active users only
CREATE INDEX idx_recent_activity ON watch_events (user_id, event_ts)
WHERE event_ts >= CURRENT_DATE - INTERVAL '90' DAY;
```

**Explanation:**
- Composite indexes optimize multi-column queries
- Covering indexes avoid table lookups
- Partial indexes reduce index size for filtered data

**Cross-references:**
- [SQL Optimization](../optimization/sql-optimization-challenges.md)
- [Performance Optimization](../../system-design/performance-optimization.md)

---

## Learning Progression

Start with **Beginner Level** exercises to build confidence with basic SQL operations. Progress to **Intermediate Level** to master window functions and ranking. Finally, tackle **Advanced Level** exercises to handle complex analytical patterns and optimization challenges.

Each exercise includes:
- **Learning Objectives**: What you'll master
- **Solution**: Complete SQL code with best practices
- **Explanation**: Key concepts and patterns demonstrated
- **Cross-references**: Links to detailed concept documentation

For additional practice, explore the [Netflix SQL Interview Problems](../../companies/interviews/netflix/sql-problems/) which demonstrate these concepts in real-world scenarios.

**Next Steps:**
- [SQL Concepts Overview](../README.md)
- [Aggregate Functions](../aggregation/aggregate-functions.md)
- [Window Functions](../window-functions/)
- [Advanced SQL Patterns](../advanced/advanced-sql-patterns.md)
---

## Appendix: Contributor Guidelines and Organizational Templates

# Wikibooks SQL Exercises

This directory contains SQL exercises and examples adapted from [Wikibooks SQL tutorials](https://en.wikibooks.org/wiki/SQL_Exercises). Content focuses on practical SQL learning with hands-on exercises.

## 📚 Content Overview

### Exercise Categories

#### [basic-sql](basic-sql/) - *In Development*
- SELECT statements and basic queries
- Simple WHERE clauses and filtering
- Basic aggregation functions
- Simple JOIN operations

#### [intermediate-joins](intermediate-joins/) - *In Development*
- Multi-table JOIN patterns
- Complex WHERE conditions
- Subqueries introduction
- Data relationship exercises

#### [advanced-patterns](advanced-patterns/) - *In Development*
- Window functions practice
- Common Table Expressions (CTEs)
- Recursive queries
- Performance optimization exercises

## 🎯 Exercise Structure

Each exercise follows this format:

### Problem Statement
*Clear, concise description of the SQL challenge*

### Sample Data
```sql
-- Table schemas and sample data
CREATE TABLE example_table (
    id INT,
    name VARCHAR(50),
    value DECIMAL(10,2)
);

INSERT INTO example_table VALUES
(1, 'Example 1', 100.50),
(2, 'Example 2', 200.75);
```

### Solution
```sql
-- Well-commented SQL query
SELECT
    name,
    SUM(value) as total_value
FROM example_table
WHERE value > 100
GROUP BY name;
```

### Explanation
- **Concepts Demonstrated**: Aggregation functions, filtering, GROUP BY
- **Key Learning Points**: How to filter before aggregation, proper column selection
- **Difficulty**: 🟢 Beginner

## 🔗 Wikibooks Source Material

Based on the following Wikibooks chapters:
- [SQL Exercises](https://en.wikibooks.org/wiki/SQL_Exercises)
- [SQL Dialects Reference](https://en.wikibooks.org/wiki/SQL_Dialects_Reference)
- [SQL Queries](https://en.wikibooks.org/wiki/Category:SQL_Queries)

## 📊 Difficulty Distribution

| Difficulty | Count | Topics |
|------------|-------|---------|
| 🟢 Beginner | ~15 exercises | Basic SELECT, aggregation, simple JOINs |
| 🟡 Intermediate | ~10 exercises | Complex JOINs, subqueries |
| 🟠 Advanced | ~5 exercises | Window functions, CTEs |

## 🎯 Learning Integration

These exercises complement the main SQL concepts:
- Practice basic skills from [aggregation](../../aggregation/)
- Apply JOIN patterns from [joins](../../joins/)
- Build toward [window functions](../../window-functions/)

## 📝 Adding New Exercises

When adding new Wikibooks exercises:
1. Follow the established naming convention: `01-basic-aggregation.md`
2. Include complete schema setup and sample data
3. Provide multiple solution approaches where applicable
4. Tag with relevant SQL concepts and difficulty level
5. Cross-reference related main concepts

---

*Navigate back to [SQL Extras](../README.md) | [SQL Concepts](../../README.md)*