# Advanced SQL Patterns

This comprehensive guide covers complex SQL patterns including recursive queries, advanced joins, sophisticated data manipulation techniques, and streaming-specific patterns commonly asked in senior-level interviews. The document combines general advanced SQL patterns with Netflix-style streaming platform examples to provide practical context for real-world applications.

## Table of Contents

- [General Advanced Patterns](#general-advanced-patterns)
- [Netflix Streaming Patterns](#netflix-streaming-patterns)
- [Data Modeling for Streaming Platforms](#data-modeling-for-streaming-platforms)
- [Learning Objectives](#learning-objectives)
- [Difficulty Level](#difficulty-level)
- [Cross-References](#cross-references)

## General Advanced Patterns

These patterns demonstrate core SQL concepts that apply across industries and use cases.

### 1. Employee Management Hierarchy

#### Problem

You have an `employees` table with employee-manager relationships:

| employee_id | name | manager_id | department | salary |
|-------------|------|------------|------------|--------|
| 1 | Alice | NULL | Engineering | 150000 |
| 2 | Bob | 1 | Engineering | 120000 |
| 3 | Charlie | 1 | Engineering | 110000 |
| 4 | David | 2 | Engineering | 100000 |
| 5 | Eve | 2 | Engineering | 95000 |
| 6 | Frank | 3 | Engineering | 90000 |

Find the **complete management chain** for each employee, showing the full path from top-level manager to the employee.

#### Solution

```sql
WITH RECURSIVE management_chain AS (
    -- Base case: top-level managers
    SELECT
        employee_id,
        name,
        manager_id,
        name as management_path,
        0 as level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: employees with managers
    SELECT
        e.employee_id,
        e.name,
        e.manager_id,
        CONCAT(mc.management_path, ' -> ', e.name) as management_path,
        mc.level + 1 as level
    FROM employees e
    JOIN management_chain mc ON e.manager_id = mc.employee_id
)
SELECT
    employee_id,
    name,
    management_path,
    level
FROM management_chain
ORDER BY level, employee_id;
```

#### Explanation

- **RECURSIVE CTE**: Builds the hierarchy by iteratively joining employees to their managers
- **Base case**: Top-level managers (NULL manager_id) start the chains
- **Recursive case**: Each iteration adds one level deeper in the hierarchy
- **CONCAT**: Builds readable management path strings
- **Level tracking**: Shows the depth in the organizational hierarchy

This demonstrates recursive CTEs for hierarchical data, essential for organizational charts and dependency trees.

---

### 2. Customer Lifetime Value Segmentation

#### Problem

You have customer transaction data:

| customer_id | transaction_date | amount | category |
|-------------|------------------|--------|----------|
| 1001 | 2024-01-15 | 150.00 | Electronics |
| 1001 | 2024-02-20 | 75.00 | Books |
| 1001 | 2024-03-10 | 200.00 | Electronics |
| 1002 | 2024-01-05 | 50.00 | Books |
| 1002 | 2024-02-15 | 125.00 | Electronics |
| 1003 | 2024-01-20 | 300.00 | Electronics |
| 1003 | 2024-02-25 | 150.00 | Books |

Segment customers by **lifetime value** and **purchase frequency**, then rank them within each segment.

#### Solution

```sql
WITH customer_metrics AS (
    -- Calculate basic customer metrics
    SELECT
        customer_id,
        COUNT(*) as transaction_count,
        SUM(amount) as total_spent,
        AVG(amount) as avg_transaction,
        MAX(transaction_date) as last_purchase_date,
        MIN(transaction_date) as first_purchase_date
    FROM customer_transactions
    GROUP BY customer_id
),
customer_segments AS (
    -- Segment customers based on lifetime value and frequency
    SELECT
        customer_id,
        total_spent,
        transaction_count,
        CASE
            WHEN total_spent >= 500 THEN 'High Value'
            WHEN total_spent >= 200 THEN 'Medium Value'
            ELSE 'Low Value'
        END as value_segment,
        CASE
            WHEN transaction_count >= 10 THEN 'Frequent'
            WHEN transaction_count >= 5 THEN 'Regular'
            ELSE 'Occasional'
        END as frequency_segment
    FROM customer_metrics
),
ranked_customers AS (
    -- Rank customers within each segment combination
    SELECT
        cs.*,
        ROW_NUMBER() OVER (
            PARTITION BY value_segment, frequency_segment
            ORDER BY total_spent DESC, transaction_count DESC
        ) as segment_rank,
        DENSE_RANK() OVER (ORDER BY total_spent DESC) as overall_rank
    FROM customer_segments cs
)
SELECT
    customer_id,
    total_spent,
    transaction_count,
    value_segment,
    frequency_segment,
    segment_rank,
    overall_rank
FROM ranked_customers
ORDER BY total_spent DESC, transaction_count DESC;
```

#### Explanation

- **Multiple CTEs**: Break down complex analysis into logical steps
- **CASE statements**: Create meaningful customer segments
- **ROW_NUMBER**: Rank within specific segments
- **DENSE_RANK**: Overall ranking without gaps
- **PARTITION BY**: Segment-specific rankings

This pattern combines aggregation, conditional logic, and ranking functions for comprehensive customer analysis.

---

### 3. Content Recommendation Analysis

#### Problem

You have user viewing history and content metadata:

| user_id | content_id | watch_date | watch_duration | content_type | rating |
|---------|------------|------------|----------------|--------------|--------|
| 1 | 100 | 2024-01-01 | 45 | Movie | 4 |
| 1 | 101 | 2024-01-02 | 30 | Series | 5 |
| 1 | 102 | 2024-01-03 | 60 | Movie | 3 |
| 2 | 100 | 2024-01-01 | 50 | Movie | 5 |
| 2 | 103 | 2024-01-02 | 25 | Series | 4 |

Find **users with similar viewing patterns** using a collaborative filtering approach.

#### Solution

```sql
WITH user_content_matrix AS (
    -- Create user-content interaction matrix
    SELECT
        user_id,
        content_id,
        watch_duration,
        rating,
        content_type
    FROM viewing_history
    WHERE watch_date >= CURRENT_DATE - INTERVAL '30 days'
),
user_similarity AS (
    -- Calculate similarity between users based on content overlap
    SELECT
        a.user_id as user_a,
        b.user_id as user_b,
        COUNT(DISTINCT a.content_id) as common_content,
        CORR(a.rating, b.rating) as rating_correlation,
        AVG(ABS(a.watch_duration - b.watch_duration)) as avg_duration_diff
    FROM user_content_matrix a
    JOIN user_content_matrix b ON a.content_id = b.content_id
        AND a.user_id < b.user_id  -- Avoid duplicate pairs
    GROUP BY a.user_id, b.user_id
    HAVING COUNT(DISTINCT a.content_id) >= 3  -- Minimum overlap
),
similar_users AS (
    -- Rank similar users by correlation and overlap
    SELECT
        user_a,
        user_b,
        common_content,
        rating_correlation,
        ROW_NUMBER() OVER (
            PARTITION BY user_a
            ORDER BY rating_correlation DESC, common_content DESC
        ) as similarity_rank
    FROM user_similarity
    WHERE rating_correlation > 0.5  -- Strong positive correlation
)
SELECT
    su.user_a,
    su.user_b,
    su.common_content,
    ROUND(su.rating_correlation::numeric, 3) as correlation,
    su.similarity_rank
FROM similar_users su
WHERE similarity_rank <= 5  -- Top 5 similar users
ORDER BY su.user_a, su.similarity_rank;
```

#### Explanation

- **Matrix-style CTE**: Creates user-content interaction data
- **Self-join**: Compares users based on shared content
- **CORR function**: Calculates correlation between user ratings
- **HAVING clause**: Filters for meaningful overlaps
- **ROW_NUMBER**: Ranks similar users for each target user

This demonstrates advanced analytical patterns for recommendation systems.

---

### 4. Financial Fraud Detection

#### Problem

You have transaction data with potential fraud patterns:

| transaction_id | user_id | transaction_date | amount | merchant_category | location |
|----------------|---------|------------------|--------|-------------------|----------|
| 1001 | 1 | 2024-01-01 10:00 | 50.00 | Grocery | New York |
| 1002 | 1 | 2024-01-01 10:30 | 25.00 | Grocery | New York |
| 1003 | 1 | 2024-01-01 11:00 | 5000.00 | Electronics | New York |
| 1004 | 1 | 2024-01-01 11:30 | 50.00 | Grocery | New York |

Identify **suspicious transaction patterns** using statistical analysis.

#### Solution

```sql
WITH user_transaction_stats AS (
    -- Calculate user-specific transaction statistics
    SELECT
        user_id,
        AVG(amount) as avg_transaction,
        STDDEV(amount) as stddev_transaction,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY amount) as p95_amount,
        COUNT(*) as transaction_count,
        AVG(EXTRACT(EPOCH FROM (transaction_date - LAG(transaction_date) OVER
            (PARTITION BY user_id ORDER BY transaction_date)))) / 60 as avg_time_between_minutes
    FROM transactions
    WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
),
suspicious_transactions AS (
    -- Flag potentially suspicious transactions
    SELECT
        t.transaction_id,
        t.user_id,
        t.transaction_date,
        t.amount,
        t.merchant_category,
        -- Calculate z-score for amount
        (t.amount - uts.avg_transaction) / NULLIF(uts.stddev_transaction, 0) as amount_zscore,
        -- Check if amount is unusually high
        CASE WHEN t.amount > uts.p95_amount THEN 1 ELSE 0 END as high_amount_flag,
        -- Check for rapid succession
        CASE WHEN EXTRACT(EPOCH FROM (t.transaction_date - LAG(t.transaction_date) OVER
            (PARTITION BY t.user_id ORDER BY t.transaction_date))) / 60 < 5
             THEN 1 ELSE 0 END as rapid_succession_flag,
        -- Risk score calculation
        (CASE WHEN t.amount > uts.p95_amount THEN 2 ELSE 0 END +
         CASE WHEN EXTRACT(EPOCH FROM (t.transaction_date - LAG(t.transaction_date) OVER
             (PARTITION BY t.user_id ORDER BY t.transaction_date))) / 60 < 5
              THEN 1 ELSE 0 END) as risk_score
    FROM transactions t
    JOIN user_transaction_stats uts ON t.user_id = uts.user_id
),
flagged_transactions AS (
    -- Final ranking of suspicious transactions
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY risk_score DESC, amount_zscore DESC) as suspicion_rank
    FROM suspicious_transactions
    WHERE risk_score >= 2 OR amount_zscore > 3
)
SELECT
    transaction_id,
    user_id,
    transaction_date,
    amount,
    merchant_category,
    ROUND(amount_zscore::numeric, 2) as amount_zscore,
    risk_score,
    suspicion_rank
FROM flagged_transactions
WHERE suspicion_rank <= 10  -- Top 10 most suspicious
ORDER BY suspicion_rank;
```

#### Explanation

- **Statistical analysis**: Uses standard deviation and percentiles for anomaly detection
- **Window functions**: LAG for time-based pattern analysis
- **Z-score calculation**: Statistical measure for unusual amounts
- **Risk scoring**: Combines multiple suspicious indicators
- **PERCENTILE_CONT**: Advanced PostgreSQL statistical function

This pattern shows advanced analytical SQL for fraud detection and risk analysis.

## Netflix Streaming Patterns

These patterns are specifically tailored for streaming platforms like Netflix, focusing on user engagement, content performance, and recommendation systems.

### 1. Daily Active Users (DAU)

#### Problem

Table: `watch_events(user_id, show_id, event_ts, watch_time)`

Write a query to find the **number of unique active users per day**.

#### Solution

```sql
SELECT
  DATE(event_ts) AS watch_date,
  COUNT(DISTINCT user_id) AS daily_active_users
FROM watch_events
GROUP BY DATE(event_ts)
ORDER BY watch_date;
```

#### Explanation

- **DATE() function**: Extracts date from timestamp for daily aggregation
- **COUNT(DISTINCT)**: Ensures each user is counted only once per day
- **GROUP BY**: Groups events by date for per-day calculations

This is fundamental for measuring platform engagement and growth metrics.

---

### 2. Most Watched Show per Day

#### Problem

Table: `watch_history(user_id, show_id, watch_date, watch_time_minutes)`

Find the **most watched show per day** based on total minutes.

#### Solution

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

#### Explanation

- **RANK() window function**: Ranks shows within each day by total watch time
- **PARTITION BY**: Resets ranking for each day
- **Subquery**: Allows filtering by rank after window function calculation

Critical for content performance analysis and trending content identification.

---

### 3. Day-1 Retention

#### Problem

From `user_signup(user_id, signup_date)` and `watch_events(user_id, event_ts)`, calculate **Day-1 retention** (users who signed up on Day X and came back on Day X+1).

#### Solution

```sql
SELECT
  s.signup_date,
  COUNT(DISTINCT a.user_id) * 100.0 / COUNT(DISTINCT s.user_id) AS day1_retention
FROM user_signup s
LEFT JOIN watch_events a
  ON s.user_id = a.user_id
  AND DATE(a.event_ts) = DATE_ADD(s.signup_date, INTERVAL 1 DAY)
GROUP BY s.signup_date;
```

#### Explanation

- **LEFT JOIN**: Includes all signups, even those without next-day activity
- **DATE_ADD**: Calculates the next day after signup
- **Percentage calculation**: Numerator (returned users) divided by denominator (total signups)

Essential metric for measuring user onboarding success and engagement.

---

### 4. Top 3 Shows per Region

#### Problem

Table: `viewership(user_id, show_id, region, watch_time)`

Find the **top 3 most watched shows per region** by total minutes.

#### Solution

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

#### Explanation

- **DENSE_RANK()**: Provides consecutive ranking without gaps
- **PARTITION BY region**: Ranks within each geographic region separately
- **Top-N pattern**: Filters for rank <= 3 to get top performers

Critical for regional content strategy and localization decisions.

---

### 5. Consecutive Days Watching

#### Problem

From `user_activity(user_id, activity_date)`, find users who have watched content for **3 consecutive days**.

#### Solution

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

#### Explanation

- **LAG() window function**: Accesses previous rows' values
- **DATEDIFF**: Calculates difference between consecutive dates
- **Multiple LAG calls**: Checks for 3-day sequences

Identifies highly engaged users who form watching habits.

---

### 6. Percentage of Users Watching Originals

#### Problem

`shows(show_id, type)` where type = 'original' or 'licensed'
`watch_history(user_id, show_id)`

Find the **percentage of users who watched at least one Netflix Original**.

#### Solution

```sql
SELECT
  COUNT(DISTINCT CASE WHEN s.type = 'original' THEN w.user_id END) * 100.0 /
  COUNT(DISTINCT w.user_id) AS pct_original_watchers
FROM watch_history w
JOIN shows s ON w.show_id = s.show_id;
```

#### Explanation

- **CASE in COUNT DISTINCT**: Counts users who watched originals
- **Conditional aggregation**: Separates original vs licensed content consumption
- **Percentage calculation**: Ratio of original watchers to total watchers

Key metric for measuring success of Netflix's original content strategy.

---

### 7. Power Users

#### Problem

Find the **top 1% of users** by total watch time in `watch_history`.

#### Solution

```sql
WITH ranked AS (
  SELECT
    user_id,
    SUM(watch_time_minutes) AS total_time,
    PERCENT_RANK() OVER (ORDER BY SUM(watch_time_minutes) DESC) AS pct_rank
  FROM watch_history
  GROUP BY user_id
)
SELECT user_id, total_time
FROM ranked
WHERE pct_rank <= 0.01;
```

#### Explanation

- **PERCENT_RANK()**: Calculates percentile rank (0.01 = top 1%)
- **CTE structure**: Breaks down aggregation and ranking
- **HAVING equivalent**: Filters for top percentile

Identifies most valuable users for targeted retention and premium feature testing.

---

### 8. Consecutive Days Streak (7-day binge)

#### Problem

Table: `watch_events(user_id, event_ts)`

Find users who have watched content for **7 consecutive days**.

#### Solution

```sql
WITH daily_watch AS (
  SELECT DISTINCT user_id, DATE(event_ts) AS watch_date
  FROM watch_events
),
with_lags AS (
  SELECT
    user_id,
    watch_date,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY watch_date) -
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY watch_date) AS grp
  FROM daily_watch
)
SELECT user_id
FROM (
  SELECT user_id, grp, COUNT(*) AS streak_length
  FROM with_lags
  GROUP BY user_id, grp
) t
WHERE streak_length >= 7;
```

#### Explanation

- **ROW_NUMBER trick**: Creates group identifiers for consecutive sequences
- **Date-ordered ROW_NUMBER**: Generates sequence numbers
- **Group counting**: Identifies length of consecutive day streaks

Advanced pattern for identifying binge-watching behavior and engagement patterns.

---

### 9. Recommendation Acceptance Rate

#### Problem

Tables:
- `recommendations(user_id, show_id, recommendation_ts)`
- `watch_events(user_id, show_id, event_ts)`

Find the **percentage of recommended shows that were actually watched**.

#### Solution

```sql
SELECT
  COUNT(DISTINCT CASE WHEN w.user_id IS NOT NULL THEN r.user_id END) * 100.0 /
  COUNT(DISTINCT r.user_id) AS acceptance_rate_pct
FROM recommendations r
LEFT JOIN watch_events w
  ON r.user_id = w.user_id
  AND r.show_id = w.show_id;
```

#### Explanation

- **LEFT JOIN**: Includes all recommendations, even unwatched ones
- **Conditional COUNT DISTINCT**: Counts accepted recommendations
- **Acceptance rate**: Measures recommendation algorithm effectiveness

Critical for evaluating recommendation system performance and personalization.

## Data Modeling for Streaming Platforms

### Watch History Modeling

For efficient analytics at Netflix scale:

**Fact Table**: `fact_watch_events(user_id, show_id, region, watch_time, event_ts)`
**Dimension Tables**:
- `dim_users(user_id, signup_date, country, device)`
- `dim_shows(show_id, title, genre, is_original, release_date)`

**Partitioning Strategy**:
- Partition `fact_watch_events` by `region` and `date(event_ts)`
- Enables fast queries for regional analytics and daily reporting

### Content Recommendation Modeling

**Tables**:
- `fact_recommendations(user_id, show_id, recommendation_ts, rank_position)`
- `fact_watch_events` (to track acceptance)

**Benefits**:
- A/B testing of recommendation algorithms
- Measurement of recommendation acceptance rates
- Optimization of recommendation ranking algorithms

### Data Quality Considerations

**Validation Rules**:
- No negative watch_time values
- User_id must exist in dim_users
- Show_id must exist in dim_shows

**Monitoring**:
- Data freshness checks (daily partitions arrive before SLA)
- Deduplication (unique event_id for each watch event)
- Schema evolution tracking for recommendation algorithm changes

## Learning Objectives

### General SQL Patterns
- **Recursive CTEs**: Building hierarchical queries and tree structures
- **Complex multi-CTE queries**: Breaking down complex analysis into manageable steps
- **Advanced window functions**: Statistical analysis and pattern detection
- **Correlation analysis**: Finding relationships between datasets
- **Risk scoring algorithms**: Multi-factor analysis and ranking

### Streaming-Specific Patterns
- **Retention analysis**: Day-N retention and cohort analysis
- **Ranking functions**: Top-N queries with regional partitioning
- **Consecutive sequence detection**: Binge-watching and streak analysis
- **Recommendation system evaluation**: Acceptance rate and performance metrics
- **Percentile analysis**: Power user identification and segmentation

### Data Engineering Skills
- **Data modeling**: Star schema design for analytics
- **Partitioning strategies**: Optimizing for query performance
- **Data quality**: Validation, monitoring, and lineage tracking
- **Streaming platform metrics**: DAU, engagement, and content performance

## Difficulty Level: Advanced

## Cross-References

- [Window Functions Overview](../window-functions/window-functions-overview.md)
- [CTEs and Advanced Patterns](../cte/)
- [SQL Optimization Challenges](../optimization/sql-optimization-challenges.md)
- [Netflix Data Modeling](../../companies/interviews/netflix/data-modeling/)
- [SQL Learning Path](../../README.md)

Navigate back to [SQL Concepts](../README.md) | [Concepts Overview](../../README.md)