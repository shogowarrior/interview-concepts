## 🔹 Subqueries

### ✅ Definition:

A **subquery** is a query nested inside another query. It can return scalar, single-row, or multi-row results.

Types:

* **Scalar subquery**: Returns one value
* **Correlated subquery**: Refers to outer query
* **IN/EXISTS subquery**: Checks for inclusion

### 🧩 Syntax:

```sql
SELECT ...
FROM ...
WHERE column IN (
    SELECT column FROM ...
);
```

### 📘 Examples:

#### a. Scalar subquery:

Get employees who earn more than the average salary:

```sql
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

#### b. Correlated subquery:

Get employees who earn more than the average in their department:

```sql
SELECT e1.name, e1.salary
FROM employees e1
WHERE e1.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
);
```

#### c. EXISTS:

List departments that have employees:

```sql
SELECT d.department_id, d.name
FROM departments d
WHERE EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.department_id = d.department_id
);