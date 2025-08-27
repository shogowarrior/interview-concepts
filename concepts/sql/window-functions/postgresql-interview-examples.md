# PostgreSQL Window Functions - Interview Examples

## 🔹 Overview

This guide provides practical PostgreSQL window function examples commonly encountered in technical interviews at top companies like Google, Amazon, Meta, and Netflix.

## 📊 Common Interview Problem Patterns

### Pattern 1: Top N per Group
**Problem**: Find the top 3 highest-paid employees in each department.

```sql
-- Solution using ROW_NUMBER()
SELECT department, name, salary
FROM (
    SELECT
        department,
        name,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
) ranked
WHERE rn <= 3
ORDER BY department, salary DESC;

-- Alternative using RANK() (handles ties differently)
SELECT department, name, salary
FROM (
    SELECT
        department,
        name,
        salary,
        RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
    FROM employees
) ranked
WHERE rank <= 3
ORDER BY department, rank, name;
```

### Pattern 2: Running Totals and Cumulative Sums
**Problem**: Calculate running total of sales by month for each product.

```sql
SELECT
    product_id,
    sale_date,
    daily_sales,
    SUM(daily_sales) OVER (
        PARTITION BY product_id
        ORDER BY sale_date
        ROWS UNBOUNDED PRECEDING
    ) AS running_total,
    AVG(daily_sales) OVER (
        PARTITION BY product_id
        ORDER BY sale_date
        ROWS 6 PRECEDING
    ) AS moving_avg_7d
FROM sales
ORDER BY product_id, sale_date;
```

### Pattern 3: Month-over-Month Growth
**Problem**: Calculate month-over-month growth rate for each product.

```sql
WITH monthly_sales AS (
    SELECT
        product_id,
        DATE_TRUNC('month', sale_date) AS month,
        SUM(amount) AS monthly_amount
    FROM sales
    GROUP BY product_id, DATE_TRUNC('month', sale_date)
)
SELECT
    product_id,
    month,
    monthly_amount,
    LAG(monthly_amount) OVER (
        PARTITION BY product_id
        ORDER BY month
    ) AS prev_month_amount,
    ROUND(
        (monthly_amount - LAG(monthly_amount) OVER (
            PARTITION BY product_id ORDER BY month
        )) / LAG(monthly_amount) OVER (
            PARTITION BY product_id ORDER BY month
        ) * 100, 2
    ) AS growth_rate_pct
FROM monthly_sales
ORDER BY product_id, month;
```

## 🎯 Netflix-Style Interview Problems

### Problem 1: User Engagement Analysis
**Context**: Given user viewing sessions, find the most engaged users and their viewing patterns.

```sql
-- Sample data
CREATE TABLE viewing_sessions (
    user_id INT,
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    content_id INT,
    minutes_watched INT
);

-- Solution
WITH user_stats AS (
    SELECT
        user_id,
        COUNT(*) AS total_sessions,
        SUM(minutes_watched) AS total_minutes,
        AVG(minutes_watched) AS avg_session_length,
        MAX(session_start) AS last_session_date
    FROM viewing_sessions
    GROUP BY user_id
),
ranked_users AS (
    SELECT
        user_id,
        total_sessions,
        total_minutes,
        avg_session_length,
        last_session_date,
        ROW_NUMBER() OVER (ORDER BY total_minutes DESC) AS engagement_rank,
        PERCENT_RANK() OVER (ORDER BY total_minutes DESC) AS engagement_percentile
    FROM user_stats
)
SELECT
    user_id,
    total_sessions,
    total_minutes,
    avg_session_length,
    last_session_date,
    engagement_rank,
    ROUND(engagement_percentile * 100, 1) AS engagement_percentile
FROM ranked_users
WHERE engagement_rank <= 100  -- Top 100 most engaged users
ORDER BY total_minutes DESC;
```

### Problem 2: Content Popularity Trends
**Context**: Track how content popularity changes over time and identify trending content.

```sql
-- Sample data
CREATE TABLE content_views (
    content_id INT,
    view_date DATE,
    view_count INT,
    unique_viewers INT
);

-- Solution
WITH daily_content_stats AS (
    SELECT
        content_id,
        view_date,
        view_count,
        unique_viewers,
        SUM(view_count) OVER (
            PARTITION BY content_id
            ORDER BY view_date
            ROWS 6 PRECEDING
        ) AS views_7d,
        AVG(view_count) OVER (
            PARTITION BY content_id
            ORDER BY view_date
            ROWS 6 PRECEDING
        ) AS avg_views_7d
    FROM content_views
),
content_trends AS (
    SELECT
        content_id,
        view_date,
        view_count,
        views_7d,
        avg_views_7d,
        -- Trend indicator: current day vs 7-day average
        CASE
            WHEN view_count > avg_views_7d * 1.5 THEN 'Strong Uptrend'
            WHEN view_count > avg_views_7d * 1.2 THEN 'Uptrend'
            WHEN view_count < avg_views_7d * 0.8 THEN 'Downtrend'
            ELSE 'Stable'
        END AS trend_indicator,
        -- Popularity rank for the day
        ROW_NUMBER() OVER (
            PARTITION BY view_date
            ORDER BY view_count DESC
        ) AS daily_popularity_rank
    FROM daily_content_stats
)
SELECT
    content_id,
    view_date,
    view_count,
    views_7d,
    ROUND(avg_views_7d, 2) AS avg_views_7d,
    trend_indicator,
    daily_popularity_rank
FROM content_trends
WHERE trend_indicator IN ('Strong Uptrend', 'Uptrend')
  AND daily_popularity_rank <= 10
ORDER BY view_date DESC, view_count DESC;
```

### Problem 3: A/B Test Analysis
**Context**: Analyze A/B test results with user segmentation and performance metrics.

```sql
-- Sample data
CREATE TABLE ab_test_results (
    user_id INT,
    test_group VARCHAR(10), -- 'control' or 'variant'
    signup_date DATE,
    revenue DECIMAL(10,2),
    sessions INT
);

-- Solution
WITH user_metrics AS (
    SELECT
        user_id,
        test_group,
        signup_date,
        revenue,
        sessions,
        revenue / NULLIF(sessions, 0) AS revenue_per_session,
        ROW_NUMBER() OVER (
            PARTITION BY test_group
            ORDER BY revenue DESC
        ) AS revenue_rank,
        PERCENT_RANK() OVER (
            PARTITION BY test_group
            ORDER BY revenue
        ) AS revenue_percentile
    FROM ab_test_results
),
group_stats AS (
    SELECT
        test_group,
        COUNT(*) AS user_count,
        AVG(revenue) AS avg_revenue,
        MEDIAN(revenue) AS median_revenue,
        STDDEV(revenue) AS revenue_stddev,
        SUM(revenue) AS total_revenue,
        AVG(sessions) AS avg_sessions
    FROM ab_test_results
    GROUP BY test_group
)
SELECT
    u.user_id,
    u.test_group,
    u.signup_date,
    u.revenue,
    u.sessions,
    u.revenue_per_session,
    u.revenue_rank,
    ROUND(u.revenue_percentile * 100, 1) AS revenue_percentile,
    -- Group comparison
    g.avg_revenue,
    ROUND((u.revenue - g.avg_revenue) / g.avg_revenue * 100, 2) AS revenue_vs_group_avg_pct,
    g.median_revenue,
    g.user_count,
    g.total_revenue
FROM user_metrics u
JOIN group_stats g ON u.test_group = g.test_group
ORDER BY u.test_group, u.revenue DESC;
```

## 🏢 Amazon-Style Problems

### Problem 1: Product Category Analysis
**Context**: Analyze product performance within categories and identify top performers.

```sql
CREATE TABLE product_sales (
    product_id INT,
    category VARCHAR(50),
    sales_date DATE,
    units_sold INT,
    revenue DECIMAL(10,2)
);

-- Solution
WITH product_performance AS (
    SELECT
        product_id,
        category,
        SUM(units_sold) AS total_units,
        SUM(revenue) AS total_revenue,
        AVG(revenue) AS avg_daily_revenue,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY SUM(revenue) DESC
        ) AS category_rank,
        PERCENT_RANK() OVER (
            PARTITION BY category
            ORDER BY SUM(revenue) DESC
        ) AS category_percentile
    FROM product_sales
    WHERE sales_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY product_id, category
)
SELECT
    p.product_id,
    p.category,
    p.total_units,
    p.total_revenue,
    p.avg_daily_revenue,
    p.category_rank,
    ROUND(p.category_percentile * 100, 1) AS category_percentile,
    -- Category performance
    c.category_total_revenue,
    ROUND(p.total_revenue / c.category_total_revenue * 100, 2) AS category_share_pct
FROM product_performance p
JOIN (
    SELECT
        category,
        SUM(total_revenue) AS category_total_revenue
    FROM product_performance
    GROUP BY category
) c ON p.category = c.category
WHERE p.category_rank <= 5
ORDER BY p.category, p.category_rank;
```

### Problem 2: Customer Segmentation
**Context**: Segment customers based on purchase behavior and lifetime value.

```sql
CREATE TABLE customer_orders (
    customer_id INT,
    order_date DATE,
    order_value DECIMAL(10,2),
    order_items INT
);

-- Solution
WITH customer_lifetime_value AS (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,
        SUM(order_value) AS lifetime_value,
        AVG(order_value) AS avg_order_value,
        MAX(order_date) AS last_order_date,
        MIN(order_date) AS first_order_date,
        -- Customer age in days
        EXTRACT(DAY FROM MAX(order_date) - MIN(order_date)) AS customer_age_days,
        -- Recency in days
        EXTRACT(DAY FROM CURRENT_DATE - MAX(order_date)) AS recency_days
    FROM customer_orders
    GROUP BY customer_id
),
customer_segments AS (
    SELECT
        customer_id,
        total_orders,
        lifetime_value,
        avg_order_value,
        customer_age_days,
        recency_days,
        -- RFM-style segmentation
        NTILE(5) OVER (ORDER BY recency_days ASC) AS recency_score,
        NTILE(5) OVER (ORDER BY total_orders DESC) AS frequency_score,
        NTILE(5) OVER (ORDER BY lifetime_value DESC) AS monetary_score,
        -- Overall percentile
        PERCENT_RANK() OVER (ORDER BY lifetime_value DESC) AS lifetime_value_percentile
    FROM customer_lifetime_value
)
SELECT
    customer_id,
    total_orders,
    lifetime_value,
    avg_order_value,
    customer_age_days,
    recency_days,
    recency_score,
    frequency_score,
    monetary_score,
    ROUND(lifetime_value_percentile * 100, 1) AS lifetime_value_percentile,
    -- Customer segment based on RFM
    CASE
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
        WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'Loyal Customers'
        WHEN recency_score >= 2 AND frequency_score >= 2 THEN 'Potential Loyalists'
        WHEN recency_score <= 2 THEN 'At Risk'
        ELSE 'Regular Customers'
    END AS customer_segment
FROM customer_segments
ORDER BY lifetime_value DESC;
```

## 📈 Google-Style Analytical Problems

### Problem 1: Search Query Analysis
**Context**: Analyze search query patterns and trending terms.

```sql
CREATE TABLE search_queries (
    query_id INT,
    user_id INT,
    query_text VARCHAR(255),
    search_date TIMESTAMP,
    results_count INT,
    clicked BOOLEAN
);

-- Solution for trending queries
WITH query_daily_stats AS (
    SELECT
        DATE(search_date) AS search_day,
        query_text,
        COUNT(*) AS daily_searches,
        COUNT(*) FILTER (WHERE clicked) AS daily_clicks,
        AVG(results_count) AS avg_results
    FROM search_queries
    WHERE search_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY DATE(search_date), query_text
),
query_trends AS (
    SELECT
        search_day,
        query_text,
        daily_searches,
        daily_clicks,
        ROUND(daily_clicks::DECIMAL / NULLIF(daily_searches, 0) * 100, 2) AS click_rate_pct,
        -- 7-day moving average
        AVG(daily_searches) OVER (
            PARTITION BY query_text
            ORDER BY search_day
            ROWS 6 PRECEDING
        ) AS searches_7d_avg,
        -- Trend vs previous week
        daily_searches - LAG(daily_searches, 7) OVER (
            PARTITION BY query_text
            ORDER BY search_day
        ) AS vs_prev_week,
        -- Popularity rank for the day
        ROW_NUMBER() OVER (
            PARTITION BY search_day
            ORDER BY daily_searches DESC
        ) AS daily_rank
    FROM query_daily_stats
)
SELECT
    search_day,
    query_text,
    daily_searches,
    daily_clicks,
    click_rate_pct,
    ROUND(searches_7d_avg, 2) AS searches_7d_avg,
    vs_prev_week,
    CASE
        WHEN vs_prev_week > 0 THEN 'Trending Up'
        WHEN vs_prev_week < 0 THEN 'Trending Down'
        ELSE 'Stable'
    END AS trend_direction,
    daily_rank
FROM query_trends
WHERE daily_rank <= 20  -- Top 20 queries per day
ORDER BY search_day DESC, daily_searches DESC;
```

## 🚀 Performance Optimization Interview Questions

### Problem 1: Optimize Slow Window Function Query
**Context**: Given a slow query, identify optimization opportunities.

```sql
-- Original slow query
SELECT
    user_id,
    transaction_date,
    amount,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY transaction_date) AS running_total
FROM transactions
WHERE transaction_date >= '2024-01-01'
ORDER BY user_id, transaction_date;

-- Optimization strategies:
-- 1. Add composite index on (user_id, transaction_date)
CREATE INDEX idx_transactions_user_date ON transactions (user_id, transaction_date);

-- 2. Use smaller frame for better performance
SELECT
    user_id,
    transaction_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY user_id
        ORDER BY transaction_date
        ROWS 100 PRECEDING  -- Limit frame size instead of UNBOUNDED
    ) AS recent_running_total
FROM transactions
WHERE transaction_date >= '2024-01-01'
ORDER BY user_id, transaction_date;
```

### Problem 2: Handle Large Dataset Window Functions
**Context**: Process large datasets efficiently with window functions.

```sql
-- Efficient batch processing
WITH numbered_rows AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY id) AS rn,
        COUNT(*) OVER () AS total_count
    FROM large_table
),
batches AS (
    SELECT
        *,
        NTILE(10) OVER (ORDER BY rn) AS batch_number
    FROM numbered_rows
)
SELECT
    batch_number,
    COUNT(*) AS batch_size,
    MIN(id) AS min_id,
    MAX(id) AS max_id
FROM batches
GROUP BY batch_number
ORDER BY batch_number;
```

## 🔧 Common Pitfalls and Solutions

### Pitfall 1: Wrong Default Frame
```sql
-- Problem: Unexpected results with LAST_VALUE
SELECT id, value, LAST_VALUE(value) OVER (ORDER BY id) FROM table1;

-- Solution: Specify explicit frame
SELECT id, value, LAST_VALUE(value) OVER (
    ORDER BY id
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
) FROM table1;
```

### Pitfall 2: NULL Handling in Navigation Functions
```sql
-- Problem: NULL values break navigation functions
SELECT id, value, LAG(value) OVER (ORDER BY id) FROM table_with_nulls;

-- Solution: Use IGNORE NULLS or COALESCE
SELECT
    id,
    value,
    LAG(value) IGNORE NULLS OVER (ORDER BY id) AS prev_non_null_value,
    COALESCE(
        LAG(value) OVER (ORDER BY id),
        0
    ) AS prev_with_default
FROM table_with_nulls;
```

## 📚 Related Topics
- [`concepts/sql/window-functions/window-functions-overview.md`](window-functions-overview.md) - Complete window functions guide
- [`concepts/sql/window-functions/postgresql-ranking-functions.md`](postgresql-ranking-functions.md) - Ranking functions
- [`concepts/sql/window-functions/postgresql-navigation-functions.md`](postgresql-navigation-functions.md) - Navigation functions
- [`concepts/sql/window-functions/postgresql-advanced-concepts.md`](postgresql-advanced-concepts.md) - Advanced concepts
- [`companies/interviews/netflix/sql-problems/02-ranking-window-functions/`](../../../companies/interviews/netflix/sql-problems/02-ranking-window-functions/) - Real Netflix problems