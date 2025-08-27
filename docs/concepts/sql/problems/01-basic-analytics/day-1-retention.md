# Day-1 Retention

## Question

From `user_signup(user_id, signup_date)` and `user_activity(user_id, activity_date)`, calculate **Day-1 retention** (users who signed up on Day X and came back on Day X+1).

## Answer

```sql
SELECT
  s.signup_date,
  COUNT(DISTINCT a.user_id) * 1.0 / COUNT(DISTINCT s.user_id) AS day1_retention
FROM user_signup s
LEFT JOIN user_activity a
  ON s.user_id = a.user_id
  AND a.activity_date = DATE_ADD(s.signup_date, INTERVAL 1 DAY)
GROUP BY s.signup_date;
```

## Notes

- Numerator: users active next day after signup
- Denominator: total signups for that day
- Uses `LEFT JOIN` with date filtering for the retention logic
- Common cohort analysis pattern in user analytics
