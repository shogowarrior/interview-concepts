# SQL Question 2: Analyzing Monthly Average Ratings of Airbnb Property Listings

## Problem Description

Given the `reviews` table with columns: `review_id`, `user_id`, `submit_date`, `listing_id`, `stars`, write a SQL query to get the average rating of each Airbnb property listing per month.

- The `submit_date` column represents when the review was submitted
- The `listing_id` column represents the unique ID of the Airbnb property
- The `stars` column represents the rating given by the user (1 is the lowest, 5 is the highest rating)

## Input Data

### reviews Table

| review_id | user_id | submit_date         | listing_id | stars |
|-----------|---------|--------------------|------------|-------|
| 6171      | 123     | 01/02/2022 00:00:00| 50001      | 4     |
| 7802      | 265     | 01/15/2022 00:00:00| 69852      | 4     |
| 5293      | 362     | 01/22/2022 00:00:00| 50001      | 3     |
| 6352      | 192     | 02/05/2022 00:00:00| 69852      | 3     |
| 4517      | 981     | 02/10/2022 00:00:00| 69852      | 2     |

## Solution

```sql
-- Extract month and listing_id, calculate average stars per month
SELECT
    EXTRACT(MONTH FROM submit_date) AS mth,
    listing_id,
    AVG(stars) AS avg_stars
FROM
    reviews
GROUP BY
    mth,
    listing_id
ORDER BY
    listing_id,
    mth;
```

## Explanation

This SQL query performs the following operations:

1. **Grouping**: Groups the data by month (extracted from `submit_date`) and `listing_id`
2. **Aggregation**: For each group, calculates the average `stars` rating using the `AVG()` function
3. **Month Extraction**: Uses `EXTRACT(MONTH FROM submit_date)` to get the month number from the timestamp
4. **Ordering**: Orders the results by `listing_id` first, then by month (`mth`)

This approach ensures we get one row per listing per month with the average rating for that period.

## Output

| mth | listing_id | avg_stars |
|-----|------------|-----------|
| 1   | 50001      | 3.50      |
| 1   | 69852      | 4.00      |
| 2   | 69852      | 2.50      |
