# Daily Active Users (DAU)

## Question
You have a table `user_activity`:

| user_id | activity_date | activity_type |
|---------|---------------|---------------|
| 101     | 2025-08-01    | play          |
| 101     | 2025-08-01    | pause         |
| 102     | 2025-08-01    | play          |
| 103     | 2025-08-02    | play          |

Write a query to find the number of **unique active users per day**.

## Answer

```sql
SELECT
  activity_date,
  COUNT(DISTINCT user_id) AS daily_active_users
FROM user_activity
GROUP BY activity_date
ORDER BY activity_date;
```

## Notes
- Groups by day and counts distinct users
- Basic aggregation pattern for DAU calculation
- Common Netflix interview question for analytics basics