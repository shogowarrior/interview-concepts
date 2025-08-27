# PostgreSQL Window Functions

Window functions perform calculations across related rows while preserving individual row data. Use `OVER()` clause to define window specifications.

```sql
function_name(expression) OVER (
    [PARTITION BY partition_expression]
    [ORDER BY sort_expression]
    [frame_clause]
)
```

## Files

### Core Concepts

- [`window-functions-overview.md`](window-functions-overview.md) - Syntax, categories, examples
- [`postgresql-advanced-concepts.md`](postgresql-advanced-concepts.md) - Frames, named windows, optimization

### Function Categories

- [`postgresql-ranking-functions.md`](postgresql-ranking-functions.md) - ROW_NUMBER(), RANK(), DENSE_RANK(), PERCENT_RANK(), NTILE()
- [`postgresql-navigation-functions.md`](postgresql-navigation-functions.md) - LAG(), LEAD(), FIRST_VALUE(), LAST_VALUE()

### Advanced Applications

- [`postgresql-interview-examples.md`](postgresql-interview-examples.md) - Interview problems from Netflix, Amazon, Google
- [`window-avg-comparison.md`](window-avg-comparison.md) - Advanced AVG comparisons
- [`window-avg-simplified.md`](window-avg-simplified.md) - PostgreSQL-optimized AVG solutions

## Learning Path

1. [`window-functions-overview.md`](window-functions-overview.md) - Basics
2. [`postgresql-ranking-functions.md`](postgresql-ranking-functions.md) - Ranking
3. [`postgresql-navigation-functions.md`](postgresql-navigation-functions.md) - Navigation
4. [`postgresql-advanced-concepts.md`](postgresql-advanced-concepts.md) - Advanced concepts
5. Choose: [`window-avg-comparison.md`](window-avg-comparison.md) or [`window-avg-simplified.md`](window-avg-simplified.md)
6. [`postgresql-interview-examples.md`](postgresql-interview-examples.md) - Real-world problems

## When to Use

- Running totals and moving averages
- Ranking within groups
- Time-series analysis
- Comparing rows to aggregates
- Complex analytical reporting

## Quick Examples

```sql
-- Department average
AVG(salary) OVER (PARTITION BY department)

-- Top 3 per category
ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC)

-- Month-over-month growth
LAG(revenue) OVER (ORDER BY month)
```
