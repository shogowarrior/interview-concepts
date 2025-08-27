# ⚠️ DEPRECATED CONTENT

This file has been migrated to the new structured format. Please use the updated content at:

**SQL Problems Section:**
- [Basic Analytics](../sql-problems/01-basic-analytics/) - DAU, retention, most-watched content
- [Ranking & Window Functions](../sql-problems/02-ranking-window-functions/) - Top-N queries, consecutive days, power users
- [Advanced Patterns](../sql-problems/advanced-patterns.md) - Complex CTEs and recursive queries
- [Optimization Challenges](../sql-problems/optimization-challenges.md) - Query performance and indexing

---

Got it 👍 — you’re asking about **SQL interview questions for Netflix (data engineering)** and their solutions. Netflix data engineer interviews often focus on SQL because the job involves querying huge data sets, building reliable pipelines, and optimizing queries for performance.

Here’s a collection of **Netflix-style SQL questions with answers/explanations**:

---

## 1. Find Daily Active Users (DAU)

**Question:**
You have a table `user_activity`:

| user\_id | activity\_date | activity\_type |
| -------- | -------------- | -------------- |
| 101      | 2025-08-01     | play           |
| 101      | 2025-08-01     | pause          |
| 102      | 2025-08-01     | play           |
| 103      | 2025-08-02     | play           |

Write a query to find the number of **unique active users per day**.

**Answer:**

```sql
SELECT 
  activity_date,
  COUNT(DISTINCT user_id) AS daily_active_users
FROM user_activity
GROUP BY activity_date
ORDER BY activity_date;
```

---

## 2. Most Watched Show per Day

**Question:**
Table `watch_history`:

| user\_id | show\_id | watch\_date | watch\_time\_minutes |
| -------- | -------- | ----------- | -------------------- |
| 1        | A        | 2025-08-01  | 30                   |
| 2        | A        | 2025-08-01  | 50                   |
| 3        | B        | 2025-08-01  | 80                   |

Find the **most watched show per day** (based on total minutes).

**Answer:**

```sql
SELECT watch_date, show_id
FROM (
  SELECT 
    watch_date,
    show_id,
    SUM(watch_time_minutes) AS total_watch_time,
    RANK() OVER (PARTITION BY watch_date ORDER BY SUM(watch_time_minutes) DESC) AS rnk
  FROM watch_history
  GROUP BY watch_date, show_id
) t
WHERE rnk = 1;
```

---

## 3. Retention (Day-1 User Retention)

**Question:**
From `user_signup(user_id, signup_date)` and `user_activity(user_id, activity_date)`, calculate **Day-1 retention** (users who signed up on Day X and came back on Day X+1).

**Answer:**

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

---

## 4. Top 3 Shows per Region

**Question:**
Table `viewership(user_id, show_id, region, watch_time)`.
Find the **top 3 most watched shows per region** by total minutes.

**Answer:**

```sql
SELECT region, show_id, total_watch_time
FROM (
  SELECT 
    region,
    show_id,
    SUM(watch_time) AS total_watch_time,
    DENSE_RANK() OVER (PARTITION BY region ORDER BY SUM(watch_time) DESC) AS rnk
  FROM viewership
  GROUP BY region, show_id
) t
WHERE rnk <= 3;
```

---

## 5. Consecutive Days Watching

**Question:**
From `user_activity(user_id, activity_date)`, find users who have watched content for **3 consecutive days**.

**Answer:**

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

---

## 6. Percentage of Users Watching Originals

**Question:**
`shows(show_id, type)` → type = 'original' or 'licensed'
`watch_history(user_id, show_id)`

Find the **percentage of users who watched at least one Netflix Original**.

**Answer:**

```sql
SELECT 
  COUNT(DISTINCT CASE WHEN s.type = 'original' THEN w.user_id END) * 100.0 /
  COUNT(DISTINCT w.user_id) AS pct_original_watchers
FROM watch_history w
JOIN shows s ON w.show_id = s.show_id;
```

---

## 7. Power Users

**Question:**
Find the **top 1% of users** by total watch time in `watch_history`.

**Answer:**

```sql
WITH ranked AS (
  SELECT 
    user_id,
    SUM(watch_time_minutes) AS total_time,
    PERCENT_RANK() OVER (ORDER BY SUM(watch_time_minutes) DESC) AS pct_rank
  FROM watch_history
  GROUP BY user_id
)
SELECT user_id, total_time
FROM ranked
WHERE pct_rank <= 0.01;
```

---

👉 These types of **analytics-style SQL problems** are common at Netflix. They test:

* Window functions (`RANK`, `LAG`, `PERCENT_RANK`)
* Retention & engagement metrics
* Grouping & filtering
* Thinking in terms of business metrics (DAU, top shows, originals vs licensed)

---

Would you like me to also prepare a **mock Netflix SQL interview set (with increasing difficulty, like Easy → Medium → Hard) that you can practice timed**?

Perfect — you’re now asking about **Netflix Data Engineering Fundamentals**: the core concepts that usually get tested in interviews beyond just writing SQL queries. Let’s walk through each of the areas you listed — with **Netflix-style examples**, because they love to test applied thinking.

---

# 🔑 Netflix DE Fundamentals

## 1. **Data Modeling**

Netflix works with massive datasets (watch events, recommendations, payments, CDN logs). You need to know **how to design schemas**.

### Example: Watch History Modeling

You might have:

* `users(user_id, name, signup_date, region)`
* `shows(show_id, title, genre, is_original, release_date)`
* `watch_events(event_id, user_id, show_id, watch_time, event_ts)`

👉 **Question (Netflix style):**
How would you model data to support **Top 10 shows by country** efficiently?

**Answer direction:**

* Use a **fact table**: `fact_watch_events(user_id, show_id, region, watch_time, ts)`
* Dimension tables for `dim_users`, `dim_shows`
* Partition `fact_watch_events` by `region` and `date` for faster queries
* This enables rollups for daily/weekly analytics.

---

## 2. **CTE (Common Table Expressions)**

Netflix SQL interviews love CTEs for **readability & breaking down problems**.

### Example:

“Find users who watched >100 minutes in a day, and then find how many of them watched again the next day.”

```sql
WITH daily_watch AS (
  SELECT 
    user_id,
    DATE(event_ts) AS watch_date,
    SUM(watch_time) AS total_minutes
  FROM watch_events
  GROUP BY user_id, DATE(event_ts)
),
heavy_watchers AS (
  SELECT user_id, watch_date
  FROM daily_watch
  WHERE total_minutes > 100
)
SELECT COUNT(DISTINCT h1.user_id) AS retained_users
FROM heavy_watchers h1
JOIN heavy_watchers h2
  ON h1.user_id = h2.user_id
  AND h2.watch_date = DATE_ADD(h1.watch_date, INTERVAL 1 DAY);
```

---

## 3. **Window Functions**

These are **must-know** for Netflix DE interviews.

### Example:

“Find the top 3 shows watched by each user.”

```sql
SELECT user_id, show_id, total_minutes
FROM (
  SELECT 
    user_id,
    show_id,
    SUM(watch_time) AS total_minutes,
    RANK() OVER (PARTITION BY user_id ORDER BY SUM(watch_time) DESC) AS rnk
  FROM watch_events
  GROUP BY user_id, show_id
) t
WHERE rnk <= 3;
```

👉 You should know:

* `ROW_NUMBER`, `RANK`, `DENSE_RANK`
* `LAG` / `LEAD` (for retention & consecutive days)
* `SUM() OVER(PARTITION BY…)` (running totals)

---

## 4. **Data Warehousing**

Netflix uses data lakes + warehouses (Presto/Trino, Snowflake, Hive, Iceberg).

**Key concepts they test:**

* **Star schema vs Snowflake schema**
* **Partitioning & clustering** (optimize queries over billions of rows)
* **Slowly Changing Dimensions (SCDs)** for evolving user profiles
* **Batch vs Stream ingestion** (Kafka → Spark → Iceberg table)

### Example Interview Q:

“How would you design a warehouse for **tracking content recommendations**?”
👉 Model:

* `fact_recommendations(user_id, show_id, recommendation_ts, rank_position)`
* `fact_watch_events` to track acceptance of recommendations
* This enables **A/B testing** of recommendation algorithms.

---

## 5. **Data Quality**

At Netflix scale, **bad data = bad recommendations & wrong payouts to content providers**.

They expect you to talk about **how you ensure quality**:

* **Validations** (e.g., no negative watch time, user\_id must exist in dim\_users)
* **Deduplication** (same event from multiple sources → need event\_id UUIDs)
* **Monitoring & SLAs** (alerts if partition is missing for today’s data)
* **Data Lineage** (understand where a metric comes from)

### Example:

Netflix might ask:
“Suppose your daily DAU dropped to zero. How would you debug?”

👉 Answer:

* Check upstream ingestion (Kafka/Spark jobs failed?)
* Check partition availability in warehouse (`2025-08-25` partition exists?)
* Validate schema changes (did upstream add a new column that broke parsing?)

---

# ✅ Netflix DE Interview Cheat Sheet

* **Data Modeling** → Be comfortable with **fact/dimension tables, partitioning, schema design for analytics**
* **CTE** → Use them to **break problems into steps** (readability matters)
* **Window Functions** → Master ranking, lag/lead, running totals
* **Data Warehousing** → Know star schema, SCDs, partitioning, batch vs streaming pipelines
* **Data Quality** → Always mention **validation, dedup, monitoring, lineage**

---

👉 Want me to put together a **Netflix DE Interview “Mock Case Study”** (like: “Design the data model + write queries + ensure quality for Top 10 Movies feature”) so you can practice end-to-end like a real interview?


Great 👍 I’ll prepare **two things** for you:

1. **Mock Netflix SQL Interview Set (Easy → Medium → Hard)**
2. **End-to-End Netflix Case Study (data modeling + queries + quality checks)**

This way, you can practice both **querying** and **data engineering fundamentals** like you’d face in Netflix interviews.

---

# 🎯 Mock Netflix SQL Interview Set

## 🟢 Easy (Warm-up)

**Q1. Daily Active Users**
Table: `watch_events(user_id, show_id, event_ts, watch_time)`
Find the **number of unique users per day**.

---

**Q2. First Show Watched by Each User**
Find the **first show** each user watched.

---

## 🟡 Medium

**Q3. Day-1 Retention**
From:

* `user_signup(user_id, signup_date)`
* `watch_events(user_id, event_ts)`
  Find the percentage of users who came back the day after signup.

---

**Q4. Top 3 Shows by Country**
From:

* `watch_events(user_id, show_id, region, watch_time)`
  Find the top 3 shows per region by watch time.

---

## 🔴 Hard

**Q5. Consecutive Days Streak**
Find users with a **watch streak of at least 7 consecutive days**.

---

**Q6. Power Users (Top 1%)**
Find the **top 1% of users** by total watch time.

---

**Q7. Recommendations Acceptance Rate**
From:

* `recommendations(user_id, show_id, recommendation_ts)`
* `watch_events(user_id, show_id, event_ts)`
  Find the percentage of recommended shows that were actually watched.

---

# 📊 End-to-End Netflix Case Study

**Scenario:**
Netflix wants to power the **“Top 10 Shows” feature** you see on the homepage.

### Step 1: Data Modeling

* **Fact Table**: `fact_watch_events(user_id, show_id, region, watch_time, event_ts)`
* **Dimension Tables**:

  * `dim_users(user_id, signup_date, country, device)`
  * `dim_shows(show_id, title, genre, is_original, release_date)`

Partition `fact_watch_events` by `region` and `date(event_ts)` for performance.

---

### Step 2: Queries

**Q1. Top 10 Shows per Country (yesterday)**

```sql
SELECT region, show_id, total_watch_time
FROM (
  SELECT 
    region,
    show_id,
    SUM(watch_time) AS total_watch_time,
    RANK() OVER (PARTITION BY region ORDER BY SUM(watch_time) DESC) AS rnk
  FROM fact_watch_events
  WHERE DATE(event_ts) = CURRENT_DATE - INTERVAL 1 DAY
  GROUP BY region, show_id
) t
WHERE rnk <= 10;
```

---

**Q2. Retention Check for Originals**
What % of users who watched a Netflix Original yesterday came back today?

```sql
WITH yday_watchers AS (
  SELECT DISTINCT user_id
  FROM fact_watch_events w
  JOIN dim_shows s ON w.show_id = s.show_id
  WHERE DATE(w.event_ts) = CURRENT_DATE - INTERVAL 1 DAY
    AND s.is_original = TRUE
),
today_watchers AS (
  SELECT DISTINCT user_id
  FROM fact_watch_events
  WHERE DATE(event_ts) = CURRENT_DATE
)
SELECT 
  COUNT(DISTINCT t.user_id) * 100.0 / COUNT(DISTINCT y.user_id) AS retention_rate
FROM yday_watchers y
LEFT JOIN today_watchers t ON y.user_id = t.user_id;
```

---

### Step 3: Data Quality Checks

Before delivering “Top 10 Shows”:

* **Completeness** → yesterday’s partition exists for all regions.
* **Accuracy** → total watch time ≥ 0.
* **Deduplication** → unique `(user_id, show_id, event_ts)`.
* **Freshness** → ensure yesterday’s data arrived before SLA (e.g., 6am).

---

✅ Practicing both the **SQL set** and this **case study** will prepare you for Netflix’s **two-part interview style**:

1. **SQL / Data modeling questions** (live queries)
2. **Systems / Case study** (designing warehouse & ensuring quality).

---

Do you want me to make the **SQL interview set with answers + hints** so you can try them timed first and then check against solutions?


Perfect 🚀 Let’s do it like a **practice pack** — I’ll give you the **questions first (Easy → Medium → Hard)** with just enough hints so you can try them on your own under a timer. Then, I’ll follow up with **complete worked answers + explanations** so you can check your solutions.

---

# 🎯 Netflix Mock SQL Interview Set (Practice Mode)

## 🟢 Easy (5–7 min each)

**Q1. Daily Active Users (DAU)**
Table: `watch_events(user_id, show_id, event_ts, watch_time)`
👉 Find the **number of unique active users per day**.
*Hint: think `COUNT(DISTINCT user_id)` + `GROUP BY DATE(event_ts)`.*

---

**Q2. First Show Watched by Each User**
👉 Find the **first show each user ever watched**.
*Hint: window function (`ROW_NUMBER`) ordered by `event_ts`.*

---

## 🟡 Medium (10–12 min each)

**Q3. Day-1 Retention**
Tables:

* `user_signup(user_id, signup_date)`
* `watch_events(user_id, event_ts)`

👉 Find the **percentage of users who came back the day after signup**.
*Hint: join signups with events on `signup_date + 1`.*

---

**Q4. Top 3 Shows per Region**
Table: `watch_events(user_id, show_id, region, watch_time)`

👉 Find the **top 3 most watched shows (by total minutes) per region**.
*Hint: `SUM(watch_time)` + `DENSE_RANK()`.*

---

## 🔴 Hard (15–20 min each)

**Q5. Consecutive Days Streak (7-day binge)**
Table: `watch_events(user_id, event_ts)`

👉 Find users who have watched content for **7 consecutive days**.
*Hint: use `LAG` or generate day differences and check streaks.*

---

**Q6. Power Users (Top 1%)**
Table: `watch_events(user_id, watch_time)`

👉 Find the **top 1% of users by total watch time**.
*Hint: aggregate by user, then use `PERCENT_RANK()`.*

---

**Q7. Recommendation Acceptance Rate**
Tables:

* `recommendations(user_id, show_id, recommendation_ts)`
* `watch_events(user_id, show_id, event_ts)`

👉 Find the **percentage of recommended shows that were actually watched**.
*Hint: join on `(user_id, show_id)`.*

---

⏱️ **Timing Tip**:

* Easy → 5–7 min
* Medium → 10–12 min
* Hard → 15–20 min

---

👉 Do you want me to give you the **full SQL answers immediately after this**, or would you prefer to **try a timed round first** (maybe 30–60 min) and then check back against my solutions?


Got it 👍 — since you said **yes**, I’ll now give you the **full worked SQL answers + explanations** for the Netflix-style mock interview set I gave you earlier.

---

# ✅ Netflix Mock SQL Interview Set — Solutions

## 🟢 Easy

**Q1. Daily Active Users (DAU)**

```sql
SELECT 
  DATE(event_ts) AS watch_date,
  COUNT(DISTINCT user_id) AS daily_active_users
FROM watch_events
GROUP BY DATE(event_ts)
ORDER BY watch_date;
```

✔️ Groups by day, counts distinct users.

---

**Q2. First Show Watched by Each User**

```sql
SELECT user_id, show_id, event_ts
FROM (
  SELECT 
    user_id,
    show_id,
    event_ts,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_ts ASC) AS rn
  FROM watch_events
) t
WHERE rn = 1;
```

✔️ `ROW_NUMBER()` picks earliest show per user.

---

## 🟡 Medium

**Q3. Day-1 Retention**

```sql
SELECT 
  s.signup_date,
  COUNT(DISTINCT a.user_id) * 100.0 / COUNT(DISTINCT s.user_id) AS day1_retention_pct
FROM user_signup s
LEFT JOIN watch_events a
  ON s.user_id = a.user_id
  AND DATE(a.event_ts) = DATE_ADD(s.signup_date, INTERVAL 1 DAY)
GROUP BY s.signup_date;
```

✔️ Numerator = users active next day, Denominator = signups.

---

**Q4. Top 3 Shows per Region**

```sql
SELECT region, show_id, total_watch_time
FROM (
  SELECT 
    region,
    show_id,
    SUM(watch_time) AS total_watch_time,
    DENSE_RANK() OVER (PARTITION BY region ORDER BY SUM(watch_time) DESC) AS rnk
  FROM watch_events
  GROUP BY region, show_id
) t
WHERE rnk <= 3;
```

✔️ Ranking inside each region.

---

## 🔴 Hard

**Q5. Consecutive Days Streak (7-day binge)**

```sql
WITH daily_watch AS (
  SELECT DISTINCT user_id, DATE(event_ts) AS watch_date
  FROM watch_events
),
with_lags AS (
  SELECT 
    user_id,
    watch_date,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY watch_date) -
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY watch_date) AS grp
  FROM daily_watch
)
SELECT user_id
FROM (
  SELECT user_id, grp, COUNT(*) AS streak_length
  FROM with_lags
  GROUP BY user_id, grp
) t
WHERE streak_length >= 7;
```

✔️ Trick: **subtract row\_number from date ordering** → constant within streaks.

---

**Q6. Power Users (Top 1%)**

```sql
WITH user_totals AS (
  SELECT 
    user_id,
    SUM(watch_time) AS total_watch_time
  FROM watch_events
  GROUP BY user_id
),
ranked AS (
  SELECT 
    user_id,
    total_watch_time,
    PERCENT_RANK() OVER (ORDER BY total_watch_time DESC) AS pct_rank
  FROM user_totals
)
SELECT user_id, total_watch_time
FROM ranked
WHERE pct_rank <= 0.01;
```

✔️ `PERCENT_RANK()` finds top 1%.

---

**Q7. Recommendation Acceptance Rate**

```sql
SELECT 
  COUNT(DISTINCT CASE WHEN w.user_id IS NOT NULL THEN r.user_id END) * 100.0 /
  COUNT(DISTINCT r.user_id) AS acceptance_rate_pct
FROM recommendations r
LEFT JOIN watch_events w
  ON r.user_id = w.user_id
  AND r.show_id = w.show_id;
```

✔️ Measures how many recommendations resulted in at least one watch.

---

# 🎓 How to Use This

* **Easy** = warm-up (focus on correctness, no syntax slips).
* **Medium** = core interview (Netflix uses these often).
* **Hard** = differentiators — show mastery of window functions, ranking, streak logic.

---

Would you like me to now also build a **“full Netflix case study” problem (Top 10 Shows feature)** with *data model + SQL queries + data quality checks* in one single flow, like a **real system design / analytics interview**?
