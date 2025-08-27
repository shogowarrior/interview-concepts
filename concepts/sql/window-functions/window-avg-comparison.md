# PostgreSQL Window Functions: AVG with OVER() Clause

## ✅ Advanced Average Comparison with PostgreSQL Window Functions

This comprehensive guide demonstrates how to use PostgreSQL window functions to compare individual values against group aggregates, including advanced PostgreSQL-specific techniques.

### Problem Statement
Find customers whose total sales exceed the average of all customer totals, with additional performance metrics.

### 🏆 PostgreSQL-Specific Solutions

#### Solution 1: Basic Window Function Approach
```sql
WITH customer_totals AS (
  SELECT customer_id,
          SUM(amount) AS total_sales,
          COUNT(*) AS order_count,
          MAX(sale_date) AS last_purchase_date
  FROM sales
  GROUP BY customer_id
),
customer_analysis AS (
  SELECT *,
          AVG(total_sales) OVER () AS overall_avg_sales,
          STDDEV(total_sales) OVER () AS sales_stddev,
          MIN(total_sales) OVER () AS min_sales,
          MAX(total_sales) OVER () AS max_sales,
          COUNT(*) OVER () AS total_customers,
          ROW_NUMBER() OVER (ORDER BY total_sales DESC) AS sales_rank,
          PERCENT_RANK() OVER (ORDER BY total_sales DESC) AS sales_percentile
  FROM customer_totals
)
SELECT
    customer_id,
    total_sales,
    order_count,
    last_purchase_date,
    ROUND(overall_avg_sales, 2) AS overall_avg_sales,
    ROUND(sales_stddev, 2) AS sales_stddev,
    sales_rank,
    ROUND(sales_percentile * 100, 1) AS sales_percentile,
    CASE
        WHEN total_sales > overall_avg_sales THEN 'Above Average'
        WHEN total_sales = overall_avg_sales THEN 'At Average'
        ELSE 'Below Average'
    END AS performance_category,
    ROUND((total_sales - overall_avg_sales) / overall_avg_sales * 100, 2) AS pct_above_avg
FROM customer_analysis
WHERE total_sales > overall_avg_sales
ORDER BY total_sales DESC;
```

#### Solution 2: Advanced PostgreSQL Windowed Aggregate
```sql
SELECT
    customer_id,
    total_sales,
    overall_avg_sales,
    order_count,
    -- PostgreSQL-specific windowed aggregates
    ROUND(AVG(total_sales) OVER (ORDER BY total_sales ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS true_overall_avg,
    -- Cumulative statistics
    SUM(total_sales) OVER (ORDER BY total_sales DESC ROWS UNBOUNDED PRECEDING) AS cumulative_sales,
    ROUND(SUM(total_sales) OVER (ORDER BY total_sales DESC ROWS UNBOUNDED PRECEDING) / SUM(total_sales) OVER () * 100, 2) AS cumulative_pct_of_total,
    -- Performance bands
    NTILE(5) OVER (ORDER BY total_sales DESC) AS performance_quintile
FROM (
    SELECT
        customer_id,
        SUM(amount) AS total_sales,
        COUNT(*) AS order_count,
        AVG(SUM(amount)) OVER () AS overall_avg_sales
    FROM sales
    GROUP BY customer_id
) customer_totals
WHERE total_sales > overall_avg_sales
ORDER BY total_sales DESC;
```

#### Solution 3: PostgreSQL Named Windows
```sql
SELECT
    customer_id,
    total_sales,
    order_count,
    overall_avg_sales,
    dept_avg_sales,
    -- Comparison metrics
    ROUND((total_sales - overall_avg_sales) / overall_avg_sales * 100, 2) AS vs_overall_avg_pct,
    ROUND((total_sales - dept_avg_sales) / dept_avg_sales * 100, 2) AS vs_dept_avg_pct,
    -- Department ranking
    dept_sales_rank,
    dept_sales_percentile
FROM (
    SELECT
        customer_id,
        department,
        SUM(amount) AS total_sales,
        COUNT(*) AS order_count,
        -- Named windows for clarity and performance
        AVG(SUM(amount)) OVER global_window AS overall_avg_sales,
        AVG(SUM(amount)) OVER dept_window AS dept_avg_sales,
        ROW_NUMBER() OVER dept_window AS dept_sales_rank,
        ROUND(PERCENT_RANK() OVER dept_window * 100, 1) AS dept_sales_percentile
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    GROUP BY customer_id, department
    WINDOW
        global_window AS (),
        dept_window AS (PARTITION BY department)
) analysis
WHERE total_sales > overall_avg_sales
ORDER BY total_sales DESC;
```

### 🔍 PostgreSQL Window Function Deep Dive:

#### Empty OVER() Clause Behavior:
* `AVG(total_sales) OVER ()` computes the average across **all rows** in the result set
* The empty parentheses indicate a window with no partitioning or ordering
* **PostgreSQL optimization**: This is computed once, not per row
* **Performance**: O(1) after initial computation vs O(n) for traditional approaches

#### Advanced Frame Specifications:
```sql
-- Running average (PostgreSQL optimized)
AVG(sales) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING)

-- Moving average with PostgreSQL RANGE frames
AVG(sales) OVER (ORDER BY date RANGE BETWEEN INTERVAL '30 days' PRECEDING AND CURRENT ROW)

-- Group-based frames (PostgreSQL 11+)
AVG(sales) OVER (ORDER BY category GROUPS 2 PRECEDING)
```

### 🧠 PostgreSQL-Specific Advantages:

* **Memory Efficiency**: PostgreSQL optimizes window function memory usage
* **Parallel Processing**: Window functions can leverage PostgreSQL's parallel query execution
* **Index Integration**: Smart use of indexes on PARTITION BY and ORDER BY columns
* **Advanced Frames**: Support for RANGE, ROWS, and GROUPS frame types
* **Named Windows**: Improved readability and maintainability

### 📊 Enhanced Sample Data:
| sale_id | customer_id | department | amount | sale_date     |
|---------|-------------|------------|--------|---------------|
| 1       | 100         | Electronics| 500    | 2024-01-01    |
| 2       | 101         | Books      | 700    | 2024-01-03    |
| 3       | 100         | Electronics| 200    | 2024-02-01    |
| 4       | 102         | Electronics| 300    | 2024-02-10    |
| 5       | 100         | Electronics| 1000   | 2024-03-01    |
| 6       | 103         | Books      | 450    | 2024-01-15    |
| 7       | 101         | Books      | 320    | 2024-02-20    |

### 📈 Advanced Expected Results:
| customer_id | total_sales | overall_avg_sales | performance_quintile | vs_overall_avg_pct |
|-------------|-------------|-------------------|---------------------|-------------------|
| 100         | 1700        | 744.29            | 1                   | 128.45%           |
| 101         | 1020        | 744.29            | 2                   | 37.01%            |
| 102         | 300         | 744.29            | 4                   | -59.68%           |
| 103         | 450         | 744.29            | 3                   | -39.55%           |

### ⚡ PostgreSQL Performance Optimizations:

#### Index Strategy:
```sql
-- Optimal index for window functions
CREATE INDEX idx_sales_customer_date ON sales (customer_id, sale_date);
CREATE INDEX idx_sales_customer_amount ON sales (customer_id, amount DESC);
```

#### Query Execution Plan Analysis:
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    customer_id,
    SUM(amount) AS total_sales,
    AVG(SUM(amount)) OVER () AS overall_avg
FROM sales
GROUP BY customer_id;
```

#### Memory Configuration:
```sql
-- For large result sets
SET work_mem = '256MB';
SET temp_buffers = '128MB';
```

### 🚀 Production Considerations:
* **Large Datasets**: Use appropriate frame specifications to limit memory usage
* **Real-time Queries**: Consider materialized views for frequently accessed window function results
* **Partitioning**: Leverage PostgreSQL table partitioning for date-based window functions
* **Monitoring**: Use `pg_stat_statements` to monitor window function query performance

### 📚 PostgreSQL Window Function Best Practices:
1. **Use Named Windows** for complex queries with multiple window functions
2. **Be Explicit** about frame specifications to avoid unexpected results
3. **Index Strategically** on window partitioning and ordering columns
4. **Test Performance** with `EXPLAIN ANALYZE` before production deployment
5. **Consider Alternatives** like CTEs when window functions are overkill

### 🔗 Related PostgreSQL Window Function Topics:
- [`concepts/sql/window-functions/window-functions-overview.md`](window-functions-overview.md) - Complete window functions guide
- [`concepts/sql/window-functions/postgresql-ranking-functions.md`](postgresql-ranking-functions.md) - Ranking functions
- [`concepts/sql/window-functions/postgresql-navigation-functions.md`](postgresql-navigation-functions.md) - Navigation functions
- [`concepts/sql/window-functions/postgresql-advanced-concepts.md`](postgresql-advanced-concepts.md) - Advanced concepts
- [`concepts/sql/window-functions/postgresql-interview-examples.md`](postgresql-interview-examples.md) - Interview examples