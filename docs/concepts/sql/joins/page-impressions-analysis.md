# Page Impressions and User Actions Analysis

The following SQL questions will be based on these tables schemas:

## Database Schema

### Tables

**page_impression**:

- `id` STRING
- `visitor_id` STRING
- `page_name` STRING
- `referrer_page_name` STRING
- `ts` BIGINT
- `ds` STRING

**user_action**:

- `id` STRING
- `page_impression_id` STRING (foreign key to page_impression.id)
- `action` STRING
- `ts` BIGINT
- `ds` STRING

**Relationship**: page_impression.id ← user_action.page_impression_id (one-to-many)

## Example Data

| id | visitor_id | page_name | referrer_page_name | ts                  | ds         |
|----|------------|-----------|--------------------|---------------------|------------|
| 1  | 10         | HOME      |                    | 2021-03-01 12:00:00 | 2021-03-01 |
| 2  | 20         | HOME      |                    | 2021-03-01 12:01:00 | 2021-03-01 |
| 3  | 30         | HOME      |                    | 2021-03-01 12:02:00 | 2021-03-01 |
| 4  | 10         | LISTING   | HOME               | 2021-03-01 12:04:00 | 2021-03-01 |
| 5  | 30         | LISTING   | HOME               | 2021-03-01 12:04:30 | 2021-03-01 |
| 6  | 30         | LISTING   | LISTING            | 2021-03-01 12:04:46 | 2021-03-01 |
| 7  | 20         | CONTACT   | HOME               | 2021-03-01 12:05:12 | 2021-03-01 |
| 8  | 10         | CONTACT   | LISTING            | 2021-03-01 12:06:12 | 2021-03-01 |
| 9  | 30         | BOOKING   | LISTING            | 2021-03-01 12:06:30 | 2021-03-01 |

| id  | page_impression_id | action      | ts                  | ds         |
|-----|--------------------|-------------|---------------------|------------|
| 100 | 1                  | BUTTON CLICK| 2021-03-01 12:00:10 | 2021-03-01 |
| 200 | 1                  | BUTTON CLICK| 2021-03-01 12:03:59 | 2021-03-01 |
| 300 | 3                  | BUTTON CLICK| 2021-03-01 12:04:29 | 2021-03-01 |
| 400 | 5                  | BUTTON CLICK| 2021-03-01 12:04:38 | 2021-03-01 |
| 500 | 5                  | OPEN MODAL  | 2021-03-01 12:04:56 | 2021-03-01 |
| 600 | 5                  | CLOSE MODAL | 2021-03-01 12:05:30 | 2021-03-01 |
| 700 | 5                  | BUTTON CLICK| 2021-03-01 12:06:29 | 2021-03-01 |

## Helper Functions

Some helpful date functions are: current_date, DATE_ADD(current_date, INTERVAL 1 DAY)

### Question 1: Write a query to find which visitor visited the most number of distinct pages yesterday and how many distinct pages they visited

Note: You may use ANSI SQL date macros such as subdate(current_date, 1) in your query.

```sql
-- Query to find the visitor with the most distinct pages visited yesterday
SELECT visitor_id, COUNT(DISTINCT page_name) AS distinct_pages
FROM page_impression
WHERE ds = SUBDATE(CURRENT_DATE, 1)
GROUP BY visitor_id
ORDER BY distinct_pages DESC
LIMIT 1;
```

### Question 2: Write a query to find the total number of actions taken on each page (i.e. page_name) yesterday

```sql
-- Query to find total actions per page yesterday
SELECT pi.page_name, COUNT(ua.action) AS total_actions
FROM page_impression pi
LEFT JOIN user_action ua ON pi.id = ua.page_impression_id
WHERE pi.ds = SUBDATE(CURRENT_DATE, 1)
GROUP BY pi.page_name;
```

### Question 3: Write a query to list the pages (i.e. page_name) for page_impressions where visitors used the "BUTTON CLICK" action more than once yesterday

```sql
-- CTE to find page impressions with more than one button click
WITH max_actions AS (
    SELECT page_impression_id, COUNT(*) AS action_count
    FROM user_action
    WHERE ds = SUBDATE(CURRENT_DATE, 1)
    AND action = 'BUTTON_CLICK'
    GROUP BY page_impression_id
    HAVING COUNT(*) > 1
)
-- Query to get distinct page names for impressions with multiple button clicks
SELECT DISTINCT pi.page_name
FROM page_impression pi
JOIN max_actions ma ON pi.id = ma.page_impression_id;
```

### Question 4: We want to periodically send a survey to all "super users". "Super users" are defined as visitors who have at least one impression every day over each of the last seven days. Write a query that would return the "super users" as of a given date

```sql
-- Query to find super users: visitors with impressions on every day of the last 7 days
SELECT visitor_id
FROM page_impression
WHERE ds > SUBDATE(CURRENT_DATE, 7) AND ds <= CURRENT_DATE
GROUP BY visitor_id
HAVING COUNT(DISTINCT ds) = 7;
