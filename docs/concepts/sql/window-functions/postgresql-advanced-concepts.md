# PostgreSQL Advanced Window Functions - Complete Guide

## 🔹 Overview

This guide covers advanced PostgreSQL window function concepts including frame specifications, named windows, performance optimization, and complex analytical patterns.

## 🖼️ Window Frame Specifications

### Understanding Window Frames

Window frames define which rows are included in the calculation for each row. PostgreSQL supports three frame types:

#### ROWS - Physical Row-Based Frames

```sql
ROWS frame_extent
```

**Frame Extents:**:

- `UNBOUNDED PRECEDING` - All rows from partition start to current row
- `n PRECEDING` - n rows before current row
- `CURRENT ROW` - Current row only
- `n FOLLOWING` - n rows after current row
- `UNBOUNDED FOLLOWING` - All rows from current row to partition end

**Examples:**:

```sql
-- Last 3 rows including current
ROWS 2 PRECEDING

-- Current row and next 2
ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING

-- All rows from start to end (complete partition)
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
```

#### RANGE - Logical Value-Based Frames

```sql
RANGE frame_extent
```

**Frame Extents (with ORDER BY required):**:

- `UNBOUNDED PRECEDING` - All rows with values <= current row's value
- `n PRECEDING` - Rows with values in range [current - n, current]
- `CURRENT ROW` - Rows with same value as current row
- `n FOLLOWING` - Rows with values in range [current, current + n]
- `UNBOUNDED FOLLOWING` - All rows with values >= current row's value

**Examples:**:

```sql
-- All rows with same or smaller ORDER BY value
RANGE UNBOUNDED PRECEDING

-- Rows within 5 units of current value
RANGE BETWEEN 5 PRECEDING AND 5 FOLLOWING
```

#### GROUPS - Group-Based Frames

```sql
GROUPS frame_extent
```

**Frame Extents:**:

- `UNBOUNDED PRECEDING` - All peer groups from start to current
- `n PRECEDING` - n peer groups before current group
- `CURRENT ROW` - Current peer group
- `n FOLLOWING` - n peer groups after current group
- `UNBOUNDED FOLLOWING` - All peer groups from current to end

### Default Frame Behavior

When no frame is specified:

- **With ORDER BY**: `RANGE UNBOUNDED PRECEDING`
- **Without ORDER BY**: `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`

## 🏷️ Named Window Specifications

### Basic Named Windows

Use the `WINDOW` clause to define reusable window specifications:

```sql
SELECT
    col1,
    col2,
    function1() OVER my_window,
    function2() OVER my_window
FROM table1
WINDOW my_window AS (PARTITION BY col1 ORDER BY col2);
```

### Advanced Named Window Techniques

#### Window Inheritance

```sql
SELECT
    col1, col2, col3,
    SUM(col3) OVER base_window,
    AVG(col3) OVER (base_window ROWS 2 PRECEDING),
    MAX(col3) OVER (base_window ORDER BY col1)
FROM table1
WINDOW base_window AS (PARTITION BY col1 ORDER BY col2);
```

#### Complex Window Combinations

```sql
SELECT
    employee_id,
    department,
    salary,
    hire_date,

    -- Department ranking
    ROW_NUMBER() OVER dept_window AS dept_rank,

    -- Department salary percentile
    PERCENT_RANK() OVER dept_window AS dept_percentile,

    -- Company-wide ranking
    ROW_NUMBER() OVER company_window AS company_rank,

    -- Moving average in department
    AVG(salary) OVER (dept_window ROWS 2 PRECEDING) AS dept_moving_avg,

    -- Cumulative salary by hire date
    SUM(salary) OVER (hire_window ROWS UNBOUNDED PRECEDING) AS cumulative_salary

FROM employees
WINDOW
    dept_window AS (PARTITION BY department ORDER BY salary DESC),
    company_window AS (ORDER BY salary DESC),
    hire_window AS (ORDER BY hire_date);
```

## 🎯 Advanced Interview Examples

### Example 1 Complex Sales Analysis

```sql
CREATE TABLE sales_data (
    sale_id INT,
    product_id INT,
    store_id INT,
    sale_date DATE,
    quantity INT,
    price DECIMAL(10,2)
);

INSERT INTO sales_data VALUES
(1, 1, 1, '2024-01-01', 10, 100),
(2, 1, 1, '2024-01-02', 15, 100),
(3, 1, 2, '2024-01-01', 8, 100),
(4, 2, 1, '2024-01-01', 20, 50),
(5, 2, 2, '2024-01-02', 25, 50);

SELECT
    sale_date,
    product_id,
    store_id,
    quantity,
    price,
    quantity * price AS revenue,

    -- Product's daily share within store
    ROUND(
        (quantity * price) /
        SUM(quantity * price) OVER (
            PARTITION BY store_id, sale_date
        ) * 100, 2
    ) AS store_daily_share_pct,

    -- Product's performance vs previous day (same store)
    quantity - LAG(quantity) OVER (
        PARTITION BY product_id, store_id
        ORDER BY sale_date
    ) AS qty_change_from_prev_day,

    -- 7-day moving average (same product, same store)
    ROUND(
        AVG(quantity) OVER (
            PARTITION BY product_id, store_id
            ORDER BY sale_date
            ROWS 6 PRECEDING
        ), 2
    ) AS moving_avg_7d,

    -- Rank within day across all stores
    ROW_NUMBER() OVER (
        PARTITION BY sale_date
        ORDER BY quantity * price DESC
    ) AS daily_rank,

    -- Cumulative revenue by product across all stores
    SUM(quantity * price) OVER (
        PARTITION BY product_id
        ORDER BY sale_date
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_product_revenue,

    -- Best performing store for this product so far
    FIRST_VALUE(store_id) OVER (
        PARTITION BY product_id
        ORDER BY quantity * price DESC
        ROWS UNBOUNDED PRECEDING
    ) AS best_store_so_far

FROM sales_data
ORDER BY product_id, sale_date, store_id;
```

### Example 2 Financial Time Series Analysis

```sql
CREATE TABLE stock_prices (
    symbol VARCHAR(10),
    trade_date DATE,
    price DECIMAL(10,2),
    volume INT
);

-- Advanced financial metrics
SELECT
    symbol,
    trade_date,
    price,
    volume,

    -- Price momentum (vs 5 days ago)
    ROUND(
        (price - LAG(price, 5) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
        )) / LAG(price, 5) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
        ) * 100, 2
    ) AS momentum_5d_pct,

    -- 20-day moving average
    ROUND(
        AVG(price) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS 19 PRECEDING
        ), 2
    ) AS ma_20d,

    -- Bollinger Band (simplified)
    ROUND(
        AVG(price) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS 19 PRECEDING
        ) + 2 * STDDEV(price) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS 19 PRECEDING
        ), 2
    ) AS bollinger_upper,

    -- Volume weighted average price (VWAP)
    ROUND(
        SUM(price * volume) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) / SUM(volume) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2
    ) AS vwap,

    -- Relative Strength Index (simplified)
    CASE
        WHEN ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY trade_date
        ) >= 14 THEN
            ROUND(
                100 - 100 / (1 + (
                    AVG(CASE WHEN price > LAG(price) OVER (
                        PARTITION BY symbol ORDER BY trade_date
                    ) THEN price - LAG(price) OVER (
                        PARTITION BY symbol ORDER BY trade_date
                    ) END) OVER (
                        PARTITION BY symbol
                        ORDER BY trade_date
                        ROWS 13 PRECEDING
                    ) /
                    AVG(CASE WHEN price < LAG(price) OVER (
                        PARTITION BY symbol ORDER BY trade_date
                    ) THEN LAG(price) OVER (
                        PARTITION BY symbol ORDER BY trade_date
                    ) - price END) OVER (
                        PARTITION BY symbol
                        ORDER BY trade_date
                        ROWS 13 PRECEDING
                    )
                )), 2
            )
    END AS rsi_14

FROM stock_prices
ORDER BY symbol, trade_date;
```

### Example 3 Customer Behavior Analysis

```sql
CREATE TABLE customer_events (
    customer_id INT,
    event_date DATE,
    event_type VARCHAR(20),
    event_value DECIMAL(10,2)
);

-- Advanced customer analytics
WITH customer_metrics AS (
    SELECT
        customer_id,
        event_date,
        event_type,
        event_value,

        -- Days since first event
        event_date - MIN(event_date) OVER (
            PARTITION BY customer_id
        ) AS days_since_first_event,

        -- Days since previous event
        event_date - LAG(event_date) OVER (
            PARTITION BY customer_id
            ORDER BY event_date
        ) AS days_since_prev_event,

        -- Event sequence number
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY event_date
        ) AS event_sequence,

        -- Cumulative value by customer
        SUM(event_value) OVER (
            PARTITION BY customer_id
            ORDER BY event_date
            ROWS UNBOUNDED PRECEDING
        ) AS cumulative_value,

        -- Rolling 30-day activity
        COUNT(*) OVER (
            PARTITION BY customer_id
            ORDER BY event_date
            RANGE BETWEEN INTERVAL '30 days' PRECEDING AND CURRENT ROW
        ) AS activity_30d,

        -- Customer lifetime value percentile
        PERCENT_RANK() OVER (
            ORDER BY SUM(event_value) OVER (
                PARTITION BY customer_id
                ORDER BY event_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            )
        ) AS lifetime_value_percentile

    FROM customer_events
)
SELECT
    customer_id,
    event_date,
    event_type,
    event_value,
    days_since_first_event,
    days_since_prev_event,
    event_sequence,
    cumulative_value,
    activity_30d,
    lifetime_value_percentile,

    -- Customer segment based on activity
    CASE
        WHEN activity_30d >= 10 THEN 'High Activity'
        WHEN activity_30d >= 5 THEN 'Medium Activity'
        ELSE 'Low Activity'
    END AS activity_segment,

    -- Value segment based on percentile
    CASE
        WHEN lifetime_value_percentile >= 0.8 THEN 'Top 20%'
        WHEN lifetime_value_percentile >= 0.6 THEN '60-80%'
        ELSE 'Bottom 60%'
    END AS value_segment

FROM customer_metrics
ORDER BY customer_id, event_date;
```

## ⚡ Performance Optimization

### Index Strategy for Window Functions

#### Optimal Indexing Patterns

```sql
-- For PARTITION BY + ORDER BY
CREATE INDEX idx_table_partition_order ON table_name (partition_col, order_col);

-- For time-based windows
CREATE INDEX idx_table_time ON table_name (partition_col, timestamp_col);

-- For range frames
CREATE INDEX idx_table_range ON table_name (partition_col, numeric_col);
```

### Performance Best Practices

1. **Choose Appropriate Frame Types**:
   - Use `ROWS` for physical row navigation
   - Use `RANGE` for value-based calculations
   - Use `GROUPS` for peer group analysis

2. **Minimize Frame Size**:
   - Explicit frames perform better than defaults
   - Smaller frames use less memory and CPU

3. **Partition Strategy**:
   - Smaller partitions = better performance
   - Consider partition pruning with proper indexes

4. **Memory Management**:
   - Monitor work_mem for large result sets
   - Consider temp_file_limit for disk spilling

### PostgreSQL-Specific Optimizations

```sql
-- Enable parallel processing (if beneficial)
SET max_parallel_workers_per_gather = 4;

-- Monitor window function performance
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    id,
    SUM(value) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING)
FROM large_table;

-- Use appropriate work memory
SET work_mem = '256MB';
```

## 🔍 Troubleshooting Common Issues

### Issue 1 Unexpected Results with Default Frames

```sql
-- Problem: LAST_VALUE returns wrong result
SELECT id, value, LAST_VALUE(value) OVER (ORDER BY id) FROM table1;

-- Solution: Specify explicit frame
SELECT id, value, LAST_VALUE(value) OVER (
    ORDER BY id
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
) FROM table1;
```

### Issue 2 Performance Degradation

```sql
-- Problem: Slow query with large partitions
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY large_partition ORDER BY col) rn
    FROM huge_table
) t WHERE rn <= 10;

-- Solution: Filter before window function
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY col) rn
    FROM (SELECT * FROM huge_table WHERE large_partition = 'target' LIMIT 1000) t
) t WHERE rn <= 10;
```

### Issue 3 Memory Issues

```sql
-- Problem: Out of memory with large frames
SELECT id, SUM(value) OVER (ORDER BY date) FROM large_table;

-- Solution: Use smaller frames or increase work_mem
SET work_mem = '1GB';
SELECT id, SUM(value) OVER (
    ORDER BY date
    ROWS 1000 PRECEDING
) FROM large_table;
```

## 🎯 Advanced Patterns

### Pattern 1 Complex Aggregations

```sql
SELECT
    category,
    subcategory,
    value,
    -- Category total
    SUM(value) OVER (category_window) AS category_total,
    -- Category average
    AVG(value) OVER (category_window) AS category_avg,
    -- Category rank
    ROW_NUMBER() OVER (category_window) AS category_rank,
    -- Subcategory contribution to category
    ROUND(value / SUM(value) OVER (category_window) * 100, 2) AS category_contribution_pct,
    -- Global rank within category
    ROW_NUMBER() OVER (ORDER BY value DESC) AS global_rank
FROM data_table
WINDOW category_window AS (PARTITION BY category);
```

### Pattern 2 Time Series with Gaps

```sql
SELECT
    date,
    value,
    -- Fill gaps using last known value
    COALESCE(
        value,
        LAST_VALUE(value) IGNORE NULLS OVER (
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        )
    ) AS filled_value,
    -- Moving average excluding NULLs
    AVG(value) IGNORE NULLS OVER (
        ORDER BY date
        ROWS 6 PRECEDING
    ) AS moving_avg_ignore_nulls
FROM time_series;
```

### Pattern 3 Sessionization

```sql
SELECT
    user_id,
    event_time,
    event_type,
    -- Session ID based on 30-minute gaps
    SUM(
        CASE WHEN EXTRACT(EPOCH FROM (
            event_time - LAG(event_time) OVER (
                PARTITION BY user_id ORDER BY event_time
            )
        )) / 60 > 30 THEN 1 ELSE 0 END
    ) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id,
    -- Events in current session
    COUNT(*) OVER (
        PARTITION BY user_id
        ORDER BY event_time
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) - COALESCE(
        SUM(
            CASE WHEN EXTRACT(EPOCH FROM (
                event_time - LAG(event_time) OVER (
                    PARTITION BY user_id ORDER BY event_time
                )
            )) / 60 > 30 THEN COUNT(*) OVER (
                PARTITION BY user_id
                ORDER BY event_time
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) END
        ) OVER (PARTITION BY user_id ORDER BY event_time), 0
    ) AS session_event_count
FROM user_events;
```

## 📚 Related Topics

- [`concepts/sql/window-functions/window-functions-overview.md`](window-functions-overview.md) - Complete window functions guide
- [`concepts/sql/window-functions/postgresql-ranking-functions.md`](postgresql-ranking-functions.md) - Ranking functions
- [`concepts/sql/window-functions/postgresql-navigation-functions.md`](postgresql-navigation-functions.md) - Navigation functions
- [`companies/interviews/netflix/sql-problems/02-ranking-window-functions/`](../../../../interviews/netflix/sql-problems/02-ranking-window-functions/) - Real interview problems
