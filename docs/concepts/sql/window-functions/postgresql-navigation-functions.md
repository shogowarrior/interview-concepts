# PostgreSQL Navigation Functions - Complete Guide

## 🔹 Overview

Navigation functions in PostgreSQL allow you to access values from different rows within the same result set. These functions are essential for time-series analysis, trend calculations, and comparing values across rows.

## 📊 Available Navigation Functions

### LAG() - Access Previous Rows

**Returns**: Value from a previous row in the partition

```sql
LAG(expression [, offset [, default_value]]) OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column
)
```

**Parameters:**:

- `expression`: The column/expression to retrieve
- `offset`: How many rows back (default: 1)
- `default_value`: Value to return if offset goes beyond partition (default: NULL)

### LEAD() - Access Following Rows

**Returns**: Value from a following row in the partition

```sql
LEAD(expression [, offset [, default_value]]) OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column
)
```

**Parameters:** Same as LAG()

### FIRST_VALUE() - First Value in Window Frame

**Returns**: First value in the current window frame

```sql
FIRST_VALUE(expression) OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column
    [frame_clause]
)
```

### LAST_VALUE() - Last Value in Window Frame

**Returns**: Last value in the current window frame

```sql
LAST_VALUE(expression) OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column
    [frame_clause]
)
```

### NTH_VALUE() - Nth Value in Window Frame

**Returns**: Nth value in the current window frame

```sql
NTH_VALUE(expression, n) OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column
    [frame_clause]
)
```

## 🎯 Interview-Ready Examples

### Example 1 Month-over-Month Sales Growth

```sql
-- Sample data setup
CREATE TABLE monthly_sales (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(50),
    sale_date DATE,
    sales_amount DECIMAL(10,2)
);

INSERT INTO monthly_sales (product_name, sale_date, sales_amount) VALUES
('Widget A', '2024-01-01', 10000),
('Widget A', '2024-02-01', 12000),
('Widget A', '2024-03-01', 15000),
('Widget A', '2024-04-01', 13000),
('Widget B', '2024-01-01', 8000),
('Widget B', '2024-02-01', 9500),
('Widget B', '2024-03-01', 11000);

-- Month-over-month growth calculation
SELECT
    product_name,
    sale_date,
    sales_amount,
    LAG(sales_amount) OVER (PARTITION BY product_name ORDER BY sale_date) AS prev_month_sales,
    ROUND(
        (sales_amount - LAG(sales_amount) OVER (PARTITION BY product_name ORDER BY sale_date))
        / LAG(sales_amount) OVER (PARTITION BY product_name ORDER BY sale_date)
        * 100, 2
    ) AS growth_percentage
FROM monthly_sales
ORDER BY product_name, sale_date;
```

**Results:**:

| product_name | sale_date  | sales_amount | prev_month_sales | growth_percentage |
|--------------|------------|--------------|------------------|-------------------|
| Widget A     | 2024-01-01 | 10000        | NULL             | NULL              |
| Widget A     | 2024-02-01 | 12000        | 10000            | 20.00             |
| Widget A     | 2024-03-01 | 15000        | 12000            | 25.00             |
| Widget A     | 2024-04-01 | 13000        | 15000            | -13.33            |

### Example 2 Running Averages and Trends

```sql
SELECT
    product_name,
    sale_date,
    sales_amount,
    -- 3-month moving average
    ROUND(AVG(sales_amount) OVER (
        PARTITION BY product_name
        ORDER BY sale_date
        ROWS 2 PRECEDING
    ), 2) AS moving_avg_3_month,

    -- Compare with first month of the year
    FIRST_VALUE(sales_amount) OVER (
        PARTITION BY product_name, EXTRACT(YEAR FROM sale_date)
        ORDER BY sale_date
    ) AS first_month_sales,

    -- Get the peak sales so far
    MAX(sales_amount) OVER (
        PARTITION BY product_name
        ORDER BY sale_date
        ROWS UNBOUNDED PRECEDING
    ) AS peak_sales_so_far,

    -- Next month's sales (for prediction analysis)
    LEAD(sales_amount) OVER (
        PARTITION BY product_name
        ORDER BY sale_date
    ) AS next_month_sales
FROM monthly_sales
ORDER BY product_name, sale_date;
```

### Example 3 Employee Performance Tracking

```sql
CREATE TABLE employee_performance (
    employee_id INT,
    review_date DATE,
    performance_score DECIMAL(3,1),
    salary DECIMAL(10,2)
);

INSERT INTO employee_performance VALUES
(1, '2024-01-01', 8.5, 75000),
(1, '2024-04-01', 9.0, 78000),
(1, '2024-07-01', 8.8, 80000),
(2, '2024-01-01', 7.5, 65000),
(2, '2024-04-01', 8.0, 67000),
(2, '2024-07-01', 8.5, 69000);

SELECT
    employee_id,
    review_date,
    performance_score,
    salary,
    -- Performance change from previous review
    performance_score - LAG(performance_score) OVER (
        PARTITION BY employee_id
        ORDER BY review_date
    ) AS performance_change,

    -- Salary growth rate
    ROUND(
        (salary - LAG(salary) OVER (
            PARTITION BY employee_id
            ORDER BY review_date
        )) / LAG(salary) OVER (
            PARTITION BY employee_id
            ORDER BY review_date
        ) * 100, 2
    ) AS salary_growth_pct,

    -- Best performance so far
    MAX(performance_score) OVER (
        PARTITION BY employee_id
        ORDER BY review_date
        ROWS UNBOUNDED PRECEDING
    ) AS best_performance_so_far,

    -- Performance percentile in current review period
    ROUND(
        PERCENT_RANK() OVER (
            PARTITION BY review_date
            ORDER BY performance_score
        ) * 100, 1
    ) AS performance_percentile
FROM employee_performance
ORDER BY employee_id, review_date;
```

## 🔍 Window Frame Behavior

### Understanding Window Frames

Navigation functions depend heavily on window frame specifications:

```sql
-- Default frame (RANGE UNBOUNDED PRECEDING)
FIRST_VALUE(salary) OVER (ORDER BY salary)  -- First salary overall

-- Explicit frame control
FIRST_VALUE(salary) OVER (
    ORDER BY salary
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)  -- First salary up to current row

-- Moving window
FIRST_VALUE(salary) OVER (
    ORDER BY date
    ROWS 2 PRECEDING
)  -- First salary in last 3 rows
```

### Frame Types Impact on Functions

| Function | Default Frame | Common Use Case |
|----------|---------------|-----------------|
| LAG() | Not applicable | Previous row values |
| LEAD() | Not applicable | Next row values |
| FIRST_VALUE() | RANGE UNBOUNDED PRECEDING | Running minimum/maximum |
| LAST_VALUE() | RANGE UNBOUNDED PRECEDING | Running totals, moving averages |
| NTH_VALUE() | RANGE UNBOUNDED PRECEDING | Specific position access |

## ⚡ Performance Considerations

### Optimization Tips

1. **Index Strategy**: Ensure ORDER BY columns are indexed
2. **Frame Specification**: Be explicit about frames to avoid expensive defaults
3. **Partition Size**: Smaller partitions perform better
4. **Memory Usage**: Large frames may require significant memory

### PostgreSQL-Specific Optimizations

```sql
-- Efficient: Uses index on date column
SELECT
    date,
    price,
    LAG(price) OVER (ORDER BY date)
FROM stock_prices;

-- Less efficient: No index on complex expression
SELECT
    date,
    price,
    LAG(price) OVER (ORDER BY EXTRACT(YEAR FROM date))
FROM stock_prices;
```

## 🎯 Common Interview Patterns

### Pattern 1 Time Series Analysis

```sql
SELECT
    date,
    value,
    LAG(value, 1) OVER (ORDER BY date) AS prev_value,
    LEAD(value, 1) OVER (ORDER BY date) AS next_value,
    value - LAG(value, 1) OVER (ORDER BY date) AS change,
    ROUND(
        (value - LAG(value, 1) OVER (ORDER BY date))
        / LAG(value, 1) OVER (ORDER BY date) * 100, 2
    ) AS change_pct
FROM time_series_data;
```

### Pattern 2 Running Statistics

```sql
SELECT
    id,
    value,
    ROW_NUMBER() OVER (ORDER BY value) AS row_num,
    FIRST_VALUE(value) OVER (ORDER BY value) AS min_value,
    LAST_VALUE(value) OVER (
        ORDER BY value
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS max_value,
    AVG(value) OVER (
        ORDER BY value
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_avg
FROM data_table;
```

### Pattern 3 Finding Sequences

```sql
-- Find consecutive rows meeting criteria
SELECT *
FROM (
    SELECT
        *,
        CASE WHEN value > threshold THEN 1 ELSE 0 END AS meets_criteria,
        LAG(CASE WHEN value > threshold THEN 1 ELSE 0 END) OVER (ORDER BY date) AS prev_meets
    FROM data_table
) t
WHERE meets_criteria = 1 AND prev_meets = 1;
```

### Pattern 4 Cohort Analysis

```sql
SELECT
    user_id,
    signup_date,
    first_purchase_date,
    -- Days to first purchase
    first_purchase_date - signup_date AS days_to_first_purchase,
    -- Compare with user's first purchase amount
    amount - FIRST_VALUE(amount) OVER (
        PARTITION BY user_id
        ORDER BY purchase_date
    ) AS amount_vs_first_purchase
FROM user_purchases
WHERE purchase_date >= signup_date;
```

## 🚀 Advanced Examples

### Complex Frame Specifications

```sql
SELECT
    department,
    employee_id,
    salary,
    hire_date,

    -- First hired employee in department
    FIRST_VALUE(employee_id) OVER (
        PARTITION BY department
        ORDER BY hire_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_hired_employee,

    -- Most recent hire before current employee
    LAG(employee_id) OVER (
        PARTITION BY department
        ORDER BY hire_date
    ) AS previous_hire,

    -- Next hire after current employee
    LEAD(employee_id) OVER (
        PARTITION BY department
        ORDER BY hire_date
    ) AS next_hire,

    -- Third most senior employee
    NTH_VALUE(employee_id, 3) OVER (
        PARTITION BY department
        ORDER BY hire_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS third_senior_employee

FROM employees
ORDER BY department, hire_date;
```

### Handling NULL Values

```sql
SELECT
    id,
    value,
    -- Handle NULLs in navigation
    COALESCE(
        LAG(value) OVER (ORDER BY id),
        0
    ) AS prev_value_with_default,

    -- Skip NULL values
    LAG(value) IGNORE NULLS OVER (ORDER BY id) AS prev_non_null_value,

    -- Count consecutive NULLs
    CASE WHEN value IS NULL THEN
        COUNT(*) FILTER (WHERE value IS NULL) OVER (
            ORDER BY id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )
    END AS consecutive_nulls
FROM nullable_data;
```

## 🔧 Troubleshooting Common Issues

### Issue 1 Unexpected NULL Values

```sql
-- Problem: LAG returns NULL for first row
SELECT id, value, LAG(value) OVER (ORDER BY id) FROM table1;

-- Solution: Provide default value
SELECT id, value, LAG(value, 1, 0) OVER (ORDER BY id) FROM table1;
```

### Issue 2 Wrong Frame Behavior

```sql
-- Problem: LAST_VALUE returns current row instead of last row
SELECT id, value, LAST_VALUE(value) OVER (ORDER BY id) FROM table1;

-- Solution: Specify explicit frame
SELECT id, value, LAST_VALUE(value) OVER (
    ORDER BY id
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
) FROM table1;
```

## 📚 Related Topics

- [`concepts/sql/window-functions/window-functions-overview.md`](window-functions-overview.md) - Complete window functions guide
- [`concepts/sql/window-functions/postgresql-ranking-functions.md`](postgresql-ranking-functions.md) - Ranking functions
