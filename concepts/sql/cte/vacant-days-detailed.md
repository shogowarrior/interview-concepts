# SQL Question: Average Vacant Days for Active Airbnb Listings in 2021

## Problem Statement
Write a query to calculate the average number of vacant days across active Airbnb properties in 2021. Only include currently active properties and round the result to the nearest whole number.

## Schema

### `bookings` Table
| Column Name  | Type      | Description                |
|--------------|-----------|----------------------------|
| listing_id   | integer   | Unique identifier for the property |
| checkin_date | timestamp | Start date of the booking  |
| checkout_date| timestamp | End date of the booking    |

### `listings` Table
| Column Name | Type    | Description                |
|-------------|---------|----------------------------|
| listing_id  | integer | Unique identifier for the property |
| is_active   | integer | 1 if active, 0 otherwise   |

## Assumptions
- A property is considered active if `is_active = 1`
- For bookings that start before 2021, consider January 1, 2021 as the start date
- For bookings that end after 2021, consider December 31, 2021 as the end date
- Active listings with no bookings in 2021 should be considered as having 365 vacant days

## Example Input

### `bookings`
```
| listing_id | checkin_date        | checkout_date       |
|------------|---------------------|---------------------|
| 1          | 2021-08-17 00:00:00 | 2021-08-19 00:00:00 |
| 1          | 2021-08-19 00:00:00 | 2021-08-25 00:00:00 |
| 2          | 2021-08-19 00:00:00 | 2021-09-22 00:00:00 |
| 3          | 2021-12-23 00:00:00 | 2022-01-05 00:00:00 |
```

### `listings`
```
| listing_id | is_active |
|------------|-----------|
| 1          | 1         |
| 2          | 0         |
| 3          | 1         |
```

## Expected Output
```
| avg_vacant_days |
|-----------------|
| 357             |
```

## Solution Explanation
1. **Property 1**:
   - Active (is_active = 1)
   - Total rented days = 8 (Aug 17-19 + Aug 19-25)
   - Vacant days = 365 - 8 = 357

2. **Property 2**:
   - Inactive (is_active = 0)
   - Excluded from calculation

3. **Property 3**:
   - Active (is_active = 1)
   - Total rented days = 9 (Dec 23-31, 2021)
   - Vacant days = 365 - 9 = 356

4. **Calculation**:
   - Average vacant days = (357 + 356) / 2 = 356.5 → 357 (rounded)

> **Note:** The actual query should work with any dataset following this schema, not just the example provided.


## Answer:
```sql
WITH listing_vacancies AS (
SELECT 
  listings.listing_id,
  365 - COALESCE(
    SUM(
      CASE WHEN checkout_date>'12/31/2021' THEN '12/31/2021' ELSE checkout_date END -
      CASE WHEN checkin_date<'01/01/2021' THEN '01/01/2021' ELSE checkin_date END 
  ),0) AS vacant_days
FROM listings 
LEFT JOIN bookings
  ON listings.listing_id = bookings.listing_id 
WHERE listings.is_active = 1
GROUP BY listings.listing_id)

SELECT ROUND(AVG(vacant_days)) 
FROM listing_vacancies;
```

### Explanation of the SQL Query

1. **CTE (`listing_vacancies`)**: 
   - For each active listing, calculates the number of vacant days in 2021.
   - Uses a `LEFT JOIN` to ensure even listings with no bookings are included (they'll have 365 vacant days).

2. **Booked Days Calculation**:
   - For each booking, calculates how many days it overlaps with 2021.
   - If a booking starts before 2021, it considers January 1, 2021 as the start.
   - If a booking ends after 2021, it considers December 31, 2021 as the end.
   - The difference between these two dates gives the number of days the property was booked during 2021.
   - Sums all such days for each listing. If there are no bookings, the sum is `NULL`, so `COALESCE(..., 0)` ensures it's treated as 0.

3. **Vacant Days Calculation**:
   - Subtracts the total booked days from 365 (total days in 2021) for each listing.

4. **Final Output**:
   - The outer query takes the average of all `vacant_days` values across active listings.
   - Uses `ROUND` to return a whole number as required by the problem statement.

This approach ensures:
- Only active listings are included.
- Listings with no bookings are treated as fully vacant.
- Bookings that span outside 2021 are properly bounded to the year.
- The result is the rounded average vacant days for all active listings.


In this query, the COALESCE function ensures that if a listing has no bookings (so the SUM(...) returns NULL), it will be treated as having 0 booked days.

Detailed breakdown:

SUM(...) calculates the total number of days a listing was booked in 2021.
If a listing has no bookings, SUM(...) returns NULL.
COALESCE(SUM(...), 0) replaces that NULL with 0.
Why is this important?

Listings with no bookings should be counted as having all 365 days vacant.
Without COALESCE, the subtraction 365 - NULL would result in NULL (unknown), and that listing would not be counted in the average.
With COALESCE, such listings get 365 - 0 = 365 vacant days, as intended.
Summary:
COALESCE(..., 0) guarantees that listings with no bookings are correctly treated as fully vacant for the year.