# PostgreSQL Ranking Functions - Complete Guide

## 🔹 Overview

PostgreSQL provides several ranking functions that assign sequential numbers or ranks to rows based on specified ordering. These are essential for analytical queries and interview problems.

## 📊 Available Ranking Functions

### ROW_NUMBER()
**Returns**: Unique sequential integer for each row (1, 2, 3, ...)

```sql
ROW_NUMBER() OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column [ASC|DESC]
)
```

**Key Characteristics:**
- No gaps in numbering
- Different values for tied rows
- Deterministic within partition

### RANK()
**Returns**: Rank with gaps for tied values

```sql
RANK() OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column [ASC|DESC]
)
```

**Key Characteristics:**
- Same rank for tied values
- Gaps in ranking sequence (e.g., 1, 2, 2, 4, ...)
- Non-consecutive ranking

### DENSE_RANK()
**Returns**: Rank without gaps for tied values

```sql
DENSE_RANK() OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column [ASC|DESC]
)
```

**Key Characteristics:**
- Same rank for tied values
- No gaps in ranking sequence (e.g., 1, 2, 2, 3, 4, ...)
- Consecutive ranking

### PERCENT_RANK()
**Returns**: Relative rank as decimal (0.0 to 1.0)

```sql
PERCENT_RANK() OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column [ASC|DESC]
)
```

**Formula**: `(rank - 1) / (total_rows_in_partition - 1)`

### CUME_DIST()
**Returns**: Cumulative distribution as decimal (0.0 to 1.0)

```sql
CUME_DIST() OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column [ASC|DESC]
)
```

**Formula**: `number_of_rows_with_value <= current_value / total_rows_in_partition`

### NTILE(n)
**Returns**: Bucket number (1 to n) dividing rows into equal groups

```sql
NTILE(num_buckets) OVER (
    [PARTITION BY partition_column]
    ORDER BY sort_column [ASC|DESC]
)
```

## 🎯 Interview-Ready Examples

### Example 1: Employee Salary Ranking
```sql
-- Sample data setup
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    department VARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE
);

INSERT INTO employees (name, department, salary, hire_date) VALUES
('Alice', 'Engineering', 120000, '2020-01-15'),
('Bob', 'Engineering', 110000, '2020-03-20'),
('Charlie', 'Engineering', 110000, '2020-05-10'),
('David', 'Sales', 90000, '2021-01-10'),
('Eve', 'Sales', 95000, '2021-02-15'),
('Frank', 'Marketing', 85000, '2021-03-01');

-- Ranking query
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS overall_row_num,
    RANK() OVER (ORDER BY salary DESC) AS overall_rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS overall_dense_rank,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_row_num,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank,
    PERCENT_RANK() OVER (ORDER BY salary DESC) AS overall_percentile,
    NTILE(4) OVER (ORDER BY salary DESC) AS salary_quartile
FROM employees
ORDER BY salary DESC;
```

**Expected Results:**
| name   | department | salary | overall_row_num | overall_rank | overall_dense_rank | dept_row_num | dept_rank | overall_percentile | salary_quartile |
|--------|------------|--------|-----------------|--------------|-------------------|--------------|-----------|-------------------|------------------|
| Alice  | Engineering| 120000 | 1               | 1            | 1                 | 1            | 1         | 0.0               | 1                |
| Bob    | Engineering| 110000 | 2               | 2            | 2                 | 2            | 2         | 0.2               | 1                |
| Charlie| Engineering| 110000 | 3               | 2            | 2                 | 3            | 2         | 0.2               | 2                |
| Eve    | Sales      | 95000  | 4               | 4            | 3                 | 1            | 1         | 0.6               | 2                |
| David  | Sales      | 90000  | 5               | 5            | 4                 | 2            | 2         | 0.8               | 3                |
| Frank  | Marketing  | 85000  | 6               | 6            | 5                 | 1            | 1         | 1.0               | 4                |

### Example 2: Top 3 Performers by Department
```sql
WITH ranked_employees AS (
    SELECT
        name,
        department,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_row_num,
        RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
    FROM employees
)
SELECT
    name,
    department,
    salary,
    dept_rank
FROM ranked_employees
WHERE dept_rank <= 3
ORDER BY department, dept_rank;
```

### Example 3: Cumulative Distribution for Performance Analysis
```sql
SELECT
    department,
    salary,
    CUME_DIST() OVER (ORDER BY salary DESC) AS cumulative_dist,
    PERCENT_RANK() OVER (ORDER BY salary DESC) AS percent_rank,
    NTILE(5) OVER (ORDER BY salary DESC) AS performance_quintile
FROM employees
ORDER BY salary DESC;
```

## 🔍 Key Differences Summary

| Function | Handles Ties | Gaps in Sequence | Use Case |
|----------|--------------|------------------|----------|
| ROW_NUMBER() | Assigns unique numbers | No gaps | When you need unique row identifiers |
| RANK() | Same rank for ties | Creates gaps | When tied values should have same rank |
| DENSE_RANK() | Same rank for ties | No gaps | When you want consecutive ranking |
| PERCENT_RANK() | Works with ties | N/A | For percentile calculations |
| CUME_DIST() | Works with ties | N/A | For cumulative distribution analysis |
| NTILE() | Divides into buckets | N/A | For grouping into equal-sized buckets |

## ⚡ Performance Tips

1. **Index Strategy**: Create indexes on ORDER BY columns for better performance
2. **Partitioning**: Use PARTITION BY wisely - smaller partitions are faster
3. **Materialization**: Consider CTEs for complex ranking scenarios
4. **Memory**: Large result sets may require significant memory for sorting

## 🎯 Common Interview Patterns

### Pattern 1: Top N per Group
```sql
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY group_column ORDER BY value_column DESC) AS rn
    FROM your_table
) ranked
WHERE rn <= N;
```

### Pattern 2: Remove Duplicates (Keep First/Last)
```sql
DELETE FROM your_table
WHERE id NOT IN (
    SELECT id
    FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY duplicate_column ORDER BY created_at) AS rn
        FROM your_table
    ) ranked
    WHERE rn = 1
);
```

### Pattern 3: Running Totals with Ranks
```sql
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total,
    ROW_NUMBER() OVER (ORDER BY date) AS day_number
FROM daily_sales;
```

## 🚀 PostgreSQL-Specific Optimizations

1. **Parallel Execution**: PostgreSQL can parallelize ranking functions in some cases
2. **Index-Only Scans**: Properly indexed ORDER BY columns enable fast ranking
3. **Memory-Efficient**: PostgreSQL optimizes memory usage for ranking operations
4. **Stable Results**: Ranking functions are deterministic within partitions

## 📚 Related Topics
- [`concepts/sql/window-functions/window-functions-overview.md`](window-functions-overview.md) - Complete window functions guide
- [`concepts/sql/aggregation/aggregate-functions.md`](aggregate-functions.md) - Aggregation concepts
- [`companies/interviews/netflix/sql-problems/02-ranking-window-functions/`](../../../companies/interviews/netflix/sql-problems/02-ranking-window-functions/) - Real interview problems