## 🔹 PostgreSQL Window Functions - Complete Guide

### ✅ Definition:

**Window functions** perform calculations across a set of table rows related to the current row. Unlike aggregate functions, window functions **do not collapse rows** and return a value for each row in the result set.

They require an **OVER()** clause to define the window specification (partition, order, and frame).

### 🧩 Core Syntax:

```sql
function_name(expression) OVER (
    [PARTITION BY partition_expression [, ...]]
    [ORDER BY sort_expression [ASC | DESC] [NULLS FIRST | NULLS LAST] [, ...]]
    [frame_clause]
)
```

### 📘 PostgreSQL-Specific Features:

#### Named Window Specifications
Use the `WINDOW` clause to define reusable window specifications:

```sql
SELECT
    employee_id,
    department_id,
    salary,
    AVG(salary) OVER dept_window AS avg_dept_salary,
    ROW_NUMBER() OVER dept_window AS dept_rank
FROM employees
WINDOW dept_window AS (PARTITION BY department_id ORDER BY salary DESC);
```

#### Frame Specifications
PostgreSQL supports three frame types:
- `ROWS`: Physical row-based frames
- `RANGE`: Logical value-based frames
- `GROUPS`: Group-based frames

```sql
-- Running total of last 3 rows
SUM(amount) OVER (ORDER BY date ROWS 2 PRECEDING)

-- Running total within date range
SUM(amount) OVER (ORDER BY date RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW)
```

### 🔢 PostgreSQL Window Function Categories:

#### 1. **Ranking Functions**
- `ROW_NUMBER()` - Unique sequential number per partition
- `RANK()` - Rank with gaps for ties
- `DENSE_RANK()` - Rank without gaps for ties
- `PERCENT_RANK()` - Relative rank (0-1)
- `CUME_DIST()` - Cumulative distribution
- `NTILE(n)` - Divide into n equal buckets

#### 2. **Navigation Functions**
- `LAG(value, offset, default)` - Value from previous row
- `LEAD(value, offset, default)` - Value from next row
- `FIRST_VALUE(value)` - First value in window frame
- `LAST_VALUE(value)` - Last value in window frame
- `NTH_VALUE(value, n)` - Nth value in window frame

#### 3. **Aggregate Functions as Window Functions**
- `SUM()`, `AVG()`, `COUNT()`, `MIN()`, `MAX()`
- `STDDEV()`, `VARIANCE()` (PostgreSQL-specific)
- All standard aggregates work as window functions

### 📊 Practical Example - Employee Analysis:

```sql
SELECT
    employee_id,
    department_id,
    salary,
    -- Department statistics
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg_salary,
    MIN(salary) OVER (PARTITION BY department_id) AS dept_min_salary,
    MAX(salary) OVER (PARTITION BY department_id) AS dept_max_salary,

    -- Employee ranking within department
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_salary_rank,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_salary_rank_with_ties,
    PERCENT_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_percentile,

    -- Compare with previous employee in department
    LAG(salary) OVER (PARTITION BY department_id ORDER BY salary DESC) AS next_highest_salary,
    LEAD(salary) OVER (PARTITION BY department_id ORDER BY salary DESC) AS next_lowest_salary,

    -- Running totals and moving averages
    SUM(salary) OVER (PARTITION BY department_id ORDER BY salary DESC ROWS UNBOUNDED PRECEDING) AS running_dept_total,
    AVG(salary) OVER (ORDER BY salary DESC ROWS 2 PRECEDING) AS moving_avg_3_employees

FROM employees
ORDER BY department_id, salary DESC;
```

### ⚡ Performance Considerations:

1. **Index Usage**: Window functions benefit from indexes on PARTITION BY and ORDER BY columns
2. **Frame Optimization**: PostgreSQL optimizes `ROWS UNBOUNDED PRECEDING` frames efficiently
3. **Memory**: Large partitions may require significant memory for sorting
4. **Parallel Processing**: PostgreSQL can parallelize window function execution in some cases

### 🔄 Comparison with Other Databases:

| Feature | PostgreSQL | SQL Server | Oracle | MySQL |
|---------|------------|------------|--------|-------|
| Named Windows | ✅ | ✅ | ✅ | ❌ |
| RANGE Frames | ✅ | ✅ | ✅ | ❌ |
| GROUPS Frames | ✅ (v11+) | ❌ | ❌ | ❌ |
| LAG/LEAD | ✅ | ✅ | ✅ | ✅ (8.0+) |
| PERCENT_RANK | ✅ | ✅ | ✅ | ❌ |
| CUME_DIST | ✅ | ✅ | ✅ | ❌ |

### 🚀 Best Practices:

1. **Use Named Windows** for complex queries with multiple window functions
2. **Index Strategically** on window partitioning and ordering columns
3. **Be Careful with Frames** - default frame can be expensive for large datasets
4. **Test Performance** - window functions can be resource-intensive
5. **Consider Alternatives** - sometimes CTEs or subqueries are clearer for simple cases

### 📚 Related Topics:
- [`concepts/sql/aggregation/aggregate-functions.md`](aggregate-functions.md) - Basic aggregation concepts
- [`concepts/sql/cte/cte-vs-window-comparison.md`](cte-vs-window-comparison.md) - When to use CTEs vs window functions