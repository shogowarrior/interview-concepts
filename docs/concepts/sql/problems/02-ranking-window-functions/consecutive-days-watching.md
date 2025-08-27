# Consecutive Days Watching

## Question

From `user_activity(user_id, activity_date)`, find users who have watched content for **3 consecutive days**.

## Answer

```sql
SELECT DISTINCT user_id
FROM (
  SELECT
    user_id,
    activity_date,
    LAG(activity_date,1) OVER (PARTITION BY user_id ORDER BY activity_date) AS prev_day,
    LAG(activity_date,2) OVER (PARTITION BY user_id ORDER BY activity_date) AS prev2_day
  FROM user_activity
) t
WHERE DATEDIFF(activity_date, prev_day) = 1
  AND DATEDIFF(prev_day, prev2_day) = 1;
```

## Notes

- Uses `LAG()` window function to look back at previous activity dates
- `DATEDIFF()` checks for consecutive days (difference = 1)
- Alternative approach: use `ROW_NUMBER()` and date arithmetic for more complex streak detection
- Common pattern for "consecutive days" or "streak" problems
