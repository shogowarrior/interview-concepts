# SQL Practice Problems Hub

## Overview

This directory serves as a comprehensive collection of SQL practice problems designed to help developers master various SQL concepts through hands-on problem-solving. The problems are organized by difficulty level and cover essential SQL topics including aggregation, joins, window functions, CTEs, subqueries, and advanced patterns.

### Directory Structure

```
problems/
├── 01-basic-analytics/          # Fundamental analytics problems
├── 02-ranking-window-functions/ # Window function ranking problems
├── advanced-patterns.md         # Complex CTEs and advanced techniques
├── optimization-challenges.md   # Performance optimization problems
└── README.md                    # This file
```

### Purpose

These problems are designed to:
- Build foundational SQL skills through progressive difficulty
- Practice real-world scenarios commonly encountered in data analysis
- Master advanced SQL concepts like window functions and CTEs
- Understand query optimization techniques for large datasets
- Prepare for technical interviews at top technology companies

## Table of Contents

- [Beginner Level Problems](#beginner-level-problems)
- [Intermediate Level Problems](#intermediate-level-problems)
- [Advanced Level Problems](#advanced-level-problems)
- [Expert Level Problems](#expert-level-problems)
- [Related Concept Documentation](#related-concept-documentation)

## Beginner Level Problems

### Basic Analytics
- [`01-basic-analytics/daily-active-users.md`](01-basic-analytics/daily-active-users.md) - Calculate daily active users with COUNT DISTINCT
- [`01-basic-analytics/day-1-retention.md`](01-basic-analytics/day-1-retention.md) - User retention analysis with JOINs
- [`01-basic-analytics/most-watched-show-per-day.md`](01-basic-analytics/most-watched-show-per-day.md) - Find most popular content per day

### Aggregation Fundamentals
- [`../aggregation/aggregate-functions.md`](../aggregation/aggregate-functions.md) - Basic aggregation functions (SUM, AVG, COUNT)
- [`../aggregation/monthly-ratings.md`](../aggregation/monthly-ratings.md) - Monthly average calculations with GROUP BY

## Intermediate Level Problems

### Window Functions & Ranking
- [`02-ranking-window-functions/top-3-shows-per-region.md`](02-ranking-window-functions/top-3-shows-per-region.md) - Top N per group using DENSE_RANK
- [`02-ranking-window-functions/consecutive-days-watching.md`](02-ranking-window-functions/consecutive-days-watching.md) - Consecutive day analysis patterns

### CTEs (Common Table Expressions)
- [`../cte/customer-sales-analysis.md`](../cte/customer-sales-analysis.md) - Multi-step analysis with CTEs
- [`../cte/cte-vs-window-comparison.md`](../cte/cte-vs-window-comparison.md) - CTE vs Window function comparison
- [`../cte/vacant-days-detailed.md`](../cte/vacant-days-detailed.md) - Complex date range calculations

### Joins
- [`../joins/page-impressions-analysis.md`](../joins/page-impressions-analysis.md) - Multi-table join analysis

## Advanced Level Problems

### Advanced SQL Patterns
- [`advanced-patterns.md`](advanced-patterns.md) - CTEs, recursive CTEs, and complex joins
- [`../advanced/advanced-sql-patterns.md`](../advanced/advanced-sql-patterns.md) - Advanced SQL techniques

### Window Functions Deep Dive
- [`../window-functions/window-functions-overview.md`](../window-functions/window-functions-overview.md) - Complete window functions guide
- [`../window-functions/postgresql-interview-examples.md`](../window-functions/postgresql-interview-examples.md) - Real interview problems with window functions
- [`../window-functions/postgresql-advanced-concepts.md`](../window-functions/postgresql-advanced-concepts.md) - Advanced window function concepts
- [`../window-functions/postgresql-navigation-functions.md`](../window-functions/postgresql-navigation-functions.md) - LAG, LEAD, and navigation functions
- [`../window-functions/postgresql-ranking-functions.md`](../window-functions/postgresql-ranking-functions.md) - Ranking and percentile functions
- [`../window-functions/window-avg-comparison.md`](../window-functions/window-avg-comparison.md) - Moving averages and comparisons
- [`../window-functions/window-avg-simplified.md`](../window-functions/window-avg-simplified.md) - Simplified window function examples

### Subqueries
- [`../subqueries/subqueries.md`](../subqueries/subqueries.md) - Subquery patterns and techniques

## Expert Level Problems

### Query Optimization
- [`optimization-challenges.md`](optimization-challenges.md) - Database optimization techniques
- [`../optimization/sql-optimization-challenges.md`](../optimization/sql-optimization-challenges.md) - Advanced optimization strategies

## Related Concept Documentation

For a deeper understanding of SQL concepts, explore these related guides:

### Core SQL Concepts
- [`../../README.md`](../../README.md) - SQL concepts overview and comprehensive reference

### Data Modeling
- [`../../data-modeling/README.md`](../../data-modeling/README.md) - Data modeling principles
- [`../../data-modeling/01-core-entities/`](../../data-modeling/01-core-entities/) - Core entity modeling
- [`../../data-modeling/02-relationships-patterns/`](../../data-modeling/02-relationships-patterns/) - Relationship patterns

### Company-Specific Problems
- [`../../../companies/interviews/netflix/sql-problems/`](../../../companies/interviews/netflix/sql-problems/) - Netflix SQL interview problems
- [`../../../companies/interviews/netflix/sql-problems/advanced-patterns.md`](../../../companies/interviews/netflix/sql-problems/advanced-patterns.md) - Netflix advanced patterns
- [`../../../companies/interviews/netflix/sql-problems/optimization-challenges.md`](../../../companies/interviews/netflix/sql-problems/optimization-challenges.md) - Netflix optimization challenges

## Getting Started

1. **Start with Beginner problems** to build foundational skills
2. **Progress to Intermediate** to master joins and window functions
3. **Tackle Advanced problems** to understand complex patterns
4. **Challenge yourself with Expert problems** focusing on optimization

Each problem includes:
- Clear problem statement
- Sample data schema
- Expected output format
- Solution with detailed explanations
- Performance considerations

## Contributing

To add new problems:
1. Create a new markdown file in the appropriate subdirectory
2. Follow the existing format with problem statement, solution, and notes
3. Update this README with the new problem link
4. Test the solution to ensure correctness

## Tips for Success

- **Understand the data model** before writing queries
- **Think step-by-step** for complex problems
- **Consider performance** implications of your solutions
- **Practice explaining** your thought process
- **Review edge cases** and NULL handling

---

*Happy querying! Mastering SQL takes practice, and these problems provide the perfect opportunity to hone your skills.*