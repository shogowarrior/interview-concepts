# Basic Analytics Problems

This directory contains fundamental SQL problems that test basic analytics skills commonly asked in Netflix data engineering interviews.

## Problems

### [`daily-active-users.md`](daily-active-users.md)
Calculate daily active users (DAU) from user activity data using basic aggregation.

### [`most-watched-show-per-day.md`](most-watched-show-per-day.md)
Find the most watched show per day based on total watch time using window functions.

### [`day-1-retention.md`](day-1-retention.md)
Calculate Day-1 user retention using joins and date arithmetic.

## Key Concepts Covered

- **Basic Aggregation**: COUNT, SUM, GROUP BY
- **Date Functions**: DATE operations for time-based analysis
- **User Metrics**: DAU, retention analysis
- **Window Functions**: RANK for top-N analysis

## Common Patterns

```sql
-- Basic DAU calculation
SELECT
  activity_date,
  COUNT(DISTINCT user_id) AS daily_active_users
FROM user_activity
GROUP BY activity_date;

-- Retention analysis
SELECT
  COUNT(DISTINCT a.user_id) * 1.0 / COUNT(DISTINCT s.user_id) AS retention_rate
FROM user_signup s
LEFT JOIN user_activity a
  ON s.user_id = a.user_id
  AND a.activity_date = DATE_ADD(s.signup_date, INTERVAL 1 DAY);
```

## Interview Tips

- Start with basic aggregation for user counts
- Use LEFT JOIN for retention to include users who didn't return
- Consider NULL handling in percentage calculations
- Practice date arithmetic for retention periods