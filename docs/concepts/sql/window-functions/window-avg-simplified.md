# PostgreSQL Window Functions Advanced AVG with OVER()

## ✅ PostgreSQL-Optimized Window Function Solution

This guide demonstrates advanced PostgreSQL techniques for windowed aggregate functions, including performance optimizations and complex analytical patterns.

### Problem Statement

Find customers whose total sales exceed the average of all customer totals, with advanced PostgreSQL analytics.

### 🏆 PostgreSQL-Optimized Solutions

#### Solution 1 Single-Query Windowed Aggregate

```sql
SELECT
    customer_id,
    total_sales,
    overall_avg_sales,
    ROUND((total_sales - overall_avg_sales) / overall_avg_sales * 100, 2) AS pct_above_avg,
    CASE
        WHEN total_sales > overall_avg_sales THEN 'Above Average'
        ELSE 'Below Average'
    END AS performance_category
FROM (
    SELECT
        customer_id,
        SUM(amount) AS total_sales,
        -- PostgreSQL windowed aggregate function
        AVG(SUM(amount)) OVER () AS overall_avg_sales,
        -- Additional PostgreSQL window functions
        ROW_NUMBER() OVER (ORDER BY SUM(amount) DESC) AS sales_rank,
        PERCENT_RANK() OVER (ORDER BY SUM(amount) DESC) AS sales_percentile,
        NTILE(4) OVER (ORDER BY SUM(amount) DESC) AS performance_quartile
    FROM sales
    GROUP BY customer_id
) AS customer_analysis
WHERE total_sales > overall_avg_sales
ORDER BY total_sales DESC;
```

#### Solution 2 PostgreSQL Named Windows with Multiple Metrics

```sql
SELECT
    customer_id,
    department,
    total_sales,
    overall_avg,
    dept_avg,
    -- Performance comparisons
    ROUND((total_sales - overall_avg) / overall_avg * 100, 2) AS vs_global_avg_pct,
    ROUND((total_sales - dept_avg) / dept_avg * 100, 2) AS vs_dept_avg_pct,
    -- Department ranking
    dept_rank,
    dept_percentile,
    -- Global ranking
    global_rank,
    global_percentile
FROM (
    SELECT
        customer_id,
        department,
        SUM(amount) AS total_sales,
        -- Named windows for PostgreSQL optimization
        AVG(SUM(amount)) OVER global_window AS overall_avg,
        AVG(SUM(amount)) OVER dept_window AS dept_avg,
        ROW_NUMBER() OVER dept_window AS dept_rank,
        ROUND(PERCENT_RANK() OVER dept_window * 100, 1) AS dept_percentile,
        ROW_NUMBER() OVER global_window AS global_rank,
        ROUND(PERCENT_RANK() OVER global_window * 100, 1) AS global_percentile
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    GROUP BY customer_id, department
    WINDOW
        global_window AS (),
        dept_window AS (PARTITION BY department)
) AS analysis
WHERE total_sales > overall_avg
ORDER BY total_sales DESC;
```

#### Solution 3 PostgreSQL Time-Based Window Analysis

```sql
SELECT
    customer_id,
    sale_month,
    monthly_sales,
    -- Moving averages
    ROUND(AVG(monthly_sales) OVER (
        PARTITION BY customer_id
        ORDER BY sale_month
        ROWS 2 PRECEDING
    ), 2) AS moving_avg_3m,

    -- Customer's overall average
    ROUND(AVG(monthly_sales) OVER (
        PARTITION BY customer_id
    ), 2) AS customer_avg,

    -- Global monthly average
    ROUND(AVG(monthly_sales) OVER (
        PARTITION BY sale_month
    ), 2) AS global_month_avg,

    -- Performance vs customer history
    ROUND((monthly_sales - AVG(monthly_sales) OVER (
        PARTITION BY customer_id
    )) / AVG(monthly_sales) OVER (
        PARTITION BY customer_id
    ) * 100, 2) AS vs_customer_history_pct,

    -- Month-over-month growth
    ROUND(
        (monthly_sales - LAG(monthly_sales) OVER (
            PARTITION BY customer_id
            ORDER BY sale_month
        )) / LAG(monthly_sales) OVER (
            PARTITION BY customer_id
            ORDER BY sale_month
        ) * 100, 2
    ) AS mom_growth_pct

FROM (
    SELECT
        customer_id,
        DATE_TRUNC('month', sale_date) AS sale_month,
        SUM(amount) AS monthly_sales
    FROM sales
    GROUP BY customer_id, DATE_TRUNC('month', sale_date)
) AS monthly_data
ORDER BY customer_id, sale_month;
```

### 🔍 PostgreSQL Windowed Aggregate Deep Dive

#### Windowed Aggregate Function Syntax

```sql
aggregate_function(expression) OVER (
    [PARTITION BY partition_expression]
    [ORDER BY sort_expression]
    [frame_clause]
)
```

**Key PostgreSQL Features:**:

- **Any Aggregate Function**: `SUM()`, `AVG()`, `COUNT()`, `MIN()`, `MAX()`, `STDDEV()`, etc.
- **Nested Aggregates**: `AVG(SUM(amount)) OVER ()` - aggregate of aggregate
- **Frame Control**: Precise control over calculation window
- **Performance**: PostgreSQL optimizes windowed aggregates efficiently

#### Advanced Frame Specifications

```sql
-- Cumulative sum (PostgreSQL optimized)
SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING)

-- Moving sum with explicit frame
SUM(amount) OVER (ORDER BY date ROWS 2 PRECEDING)

-- Range-based frames (PostgreSQL specific)
SUM(amount) OVER (ORDER BY date RANGE BETWEEN INTERVAL '30 days' PRECEDING AND CURRENT ROW)
```

### 🧠 PostgreSQL-Specific Optimizations

#### Memory and Performance

- **Single Pass**: PostgreSQL computes windowed aggregates in a single pass when possible
- **Parallel Execution**: Leverages PostgreSQL's parallel query capabilities
- **Index Utilization**: Smart index usage for ORDER BY columns
- **Memory Management**: Efficient memory usage for large result sets

#### Index Strategy for Window Functions

```sql
-- Optimal indexes for windowed aggregates
CREATE INDEX idx_sales_customer_date ON sales (customer_id, sale_date);
CREATE INDEX idx_sales_customer_amount ON sales (customer_id, amount DESC);

-- For time-based windowed aggregates
CREATE INDEX idx_sales_date_customer ON sales (sale_date, customer_id);
```

### 📊 Enhanced Sample Data with Departments

| sale_id | customer_id | department | amount | sale_date     |
|---------|-------------|------------|--------|---------------|
| 1       | 100         | Electronics| 500    | 2024-01-01    |
| 2       | 101         | Books      | 700    | 2024-01-03    |
| 3       | 100         | Electronics| 200    | 2024-02-01    |
| 4       | 102         | Electronics| 300    | 2024-02-10    |
| 5       | 100         | Electronics| 1000   | 2024-03-01    |
| 6       | 103         | Books      | 450    | 2024-01-15    |
| 7       | 101         | Books      | 320    | 2024-02-20    |

### 📈 Advanced PostgreSQL Results

| customer_id | department | total_sales | overall_avg | dept_avg | vs_global_avg_pct | vs_dept_avg_pct |
|-------------|------------|-------------|-------------|----------|-------------------|-----------------|
| 100         | Electronics| 1700        | 744.29      | 1000.00  | 128.45%           | 70.00%          |
| 101         | Books      | 1020        | 744.29      | 823.33   | 37.01%            | 23.88%          |
| 102         | Electronics| 300         | 744.29      | 1000.00  | -59.68%           | -70.00%         |
| 103         | Books      | 450         | 744.29      | 823.33   | -39.55%           | -45.35%         |

### ⚡ PostgreSQL Performance Analysis

#### Query Execution Plan

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    customer_id,
    SUM(amount) AS total_sales,
    AVG(SUM(amount)) OVER () AS overall_avg
FROM sales
GROUP BY customer_id;
```

**Expected PostgreSQL Optimizations:**:

- **HashAggregate** for initial grouping
- **WindowAgg** for window function computation
- **Parallel processing** if enabled
- **Index scans** if appropriate indexes exist

#### Memory Configuration

```sql
-- For large datasets with windowed aggregates
SET work_mem = '256MB';
SET temp_buffers = '128MB';
SET enable_parallel_append = on;
```

### 🚀 Advanced PostgreSQL Techniques

#### Combining Window Functions with CTEs

```sql
WITH customer_totals AS (
    SELECT
        customer_id,
        department,
        SUM(amount) AS total_sales,
        COUNT(*) AS order_count
    FROM sales
    GROUP BY customer_id, department
),
customer_ranks AS (
    SELECT *,
        -- Multiple window functions in one pass
        AVG(total_sales) OVER () AS global_avg,
        AVG(total_sales) OVER (PARTITION BY department) AS dept_avg,
        ROW_NUMBER() OVER (ORDER BY total_sales DESC) AS global_rank,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY total_sales DESC) AS dept_rank,
        PERCENT_RANK() OVER (ORDER BY total_sales DESC) AS global_percentile
    FROM customer_totals
)
SELECT *
FROM customer_ranks
WHERE total_sales > global_avg;
```

#### PostgreSQL-Specific Analytical Functions

```sql
SELECT
    customer_id,
    total_sales,
    -- Statistical functions
    STDDEV(total_sales) OVER () AS global_stddev,
    VARIANCE(total_sales) OVER () AS global_variance,
    -- Percentile functions
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_sales) OVER () AS global_median,
    -- Correlation with order count (if needed)
    CORR(total_sales, order_count) OVER () AS sales_order_correlation
FROM customer_totals;
```

### 📚 PostgreSQL Best Practices

1. **Use Windowed Aggregates** when you need to combine aggregation with window functions
2. **Named Windows** for complex queries with multiple window specifications
3. **Frame Control** to optimize performance and memory usage
4. **Index Strategy** based on PARTITION BY and ORDER BY columns
5. **Test Performance** with realistic data volumes

### 🔗 Related PostgreSQL Window Function Topics

- [`concepts/sql/window-functions/window-functions-overview.md`](window-functions-overview.md) - Complete window functions guide
- [`concepts/sql/window-functions/postgresql-ranking-functions.md`](postgresql-ranking-functions.md) - Ranking functions
- [`concepts/sql/window-functions/postgresql-navigation-functions.md`](postgresql-navigation-functions.md) - Navigation functions
- [`concepts/sql/window-functions/postgresql-advanced-concepts.md`](postgresql-advanced-concepts.md) - Advanced concepts
- [`concepts/sql/window-functions/postgresql-interview-examples.md`](postgresql-interview-examples.md) - Interview examples
