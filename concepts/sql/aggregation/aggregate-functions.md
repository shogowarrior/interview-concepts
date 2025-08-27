## 🔹 4. Aggregate Functions

### ✅ Definition:

**Aggregate functions** perform a calculation on a set of values and return a **single value**. They are typically used with `GROUP BY` to summarize data.

These functions **collapse rows into a summary**, unlike window functions.

---

### 📘 Common Aggregate Functions:

| Function  | Description               |
| --------- | ------------------------- |
| `SUM()`   | Total of numeric values   |
| `AVG()`   | Average of numeric values |
| `COUNT()` | Number of rows            |
| `MAX()`   | Maximum value             |
| `MIN()`   | Minimum value             |

---

### 🧩 Syntax:

```sql
SELECT AGG_FUNCTION(column)
FROM table
[WHERE conditions]
[GROUP BY column];
```

---

### 📘 Examples:

#### 1. Total salary of all employees:

```sql
SELECT SUM(salary) AS total_salary
FROM employees;
```

#### 2. Average salary by department:

```sql
SELECT department_id, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id;
```

#### 3. Count of employees per job title:

```sql
SELECT job_title, COUNT(*) AS num_employees
FROM employees
GROUP BY job_title;
```

#### 4. Highest and lowest salary in company:

```sql
SELECT 
    MAX(salary) AS highest_salary,
    MIN(salary) AS lowest_salary
FROM employees;
```

---

## ✅ Comparison with Window Function:

| Feature                 | Aggregate Function      | Window Function             |
| ----------------------- | ----------------------- | --------------------------- |
| Row Output              | Collapses to fewer rows | Maintains all original rows |
| OVER() clause required? | ❌ No                    | ✅ Yes                       |
| Use Case                | Summary per group/table | Per-row contextual metrics  |
| PostgreSQL Support      | All major aggregates    | All aggregates + window-specific |
| Performance             | Fast for grouped data   | Optimized for analytical queries |

---

## 🚀 PostgreSQL Windowed Aggregates:

**Aggregate functions can be used as window functions** in PostgreSQL by adding an `OVER()` clause. This creates powerful analytical capabilities:

### Example: Employee Analysis with Windowed Aggregates
```sql
SELECT
    employee_id,
    department,
    salary,
    -- Traditional aggregate (summary)
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary,

    -- Running calculations
    SUM(salary) OVER (ORDER BY salary ROWS UNBOUNDED PRECEDING) AS running_total,

    -- Moving averages
    AVG(salary) OVER (ORDER BY hire_date ROWS 2 PRECEDING) AS recent_avg,

    -- Statistical functions
    STDDEV(salary) OVER (PARTITION BY department) AS dept_salary_stddev,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) OVER (PARTITION BY department) AS dept_median_salary
FROM employees
ORDER BY department, salary DESC;
```

### Key PostgreSQL Windowed Aggregate Features:
- **All Standard Aggregates**: `SUM()`, `AVG()`, `COUNT()`, `MIN()`, `MAX()`
- **Statistical Functions**: `STDDEV()`, `VARIANCE()`, `CORR()`
- **Ordered-Set Aggregates**: `PERCENTILE_CONT()`, `PERCENTILE_DISC()`
- **Advanced Frames**: `ROWS`, `RANGE`, `GROUPS` frame specifications
- **Named Windows**: Reusable window specifications

---

### 📚 PostgreSQL Window Function Resources:

For comprehensive PostgreSQL window function coverage, see:
- [`concepts/sql/window-functions/window-functions-overview.md`](../window-functions/window-functions-overview.md) - Complete PostgreSQL window functions guide
- [`concepts/sql/window-functions/postgresql-ranking-functions.md`](../window-functions/postgresql-ranking-functions.md) - Ranking functions with examples
- [`concepts/sql/window-functions/postgresql-navigation-functions.md`](../window-functions/postgresql-navigation-functions.md) - Navigation functions (LAG, LEAD, etc.)
- [`concepts/sql/window-functions/postgresql-advanced-concepts.md`](../window-functions/postgresql-advanced-concepts.md) - Advanced concepts and performance
- [`concepts/sql/window-functions/postgresql-interview-examples.md`](../window-functions/postgresql-interview-examples.md) - Interview-ready examples

Would you like to see this combined into one query (e.g., comparing a row's value to a group aggregate using both types)?
