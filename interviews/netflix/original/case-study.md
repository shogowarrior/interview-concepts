# ⚠️ DEPRECATED CONTENT

This file has been migrated to the new structured format. Please use the updated content at:
**[Advanced Concepts → Case Studies → Top 10 Feature Implementation](../advanced-concepts/case-studies.md#top-10-feature-implementation)**

---

Awesome — here’s a complete, interview-ready **Netflix “Top 10” case study** you can use to practice end-to-end. It blends **data modeling, pipeline design, SQL (CTEs + window functions), warehousing choices, and data quality** — the exact mix Netflix loves.

---

# 🎬 Case Study: Netflix “Top 10” Feature

## 0) Problem

Build the backend for the **Top 10 shows by country per day** shown on the homepage. It must be:

* **Accurate** (deduped, reconciled)
* **Fresh** (ready by 06:00 local time)
* **Fast** (sub-second read latency)
* **Explainable** (traceable to source events)

---

## 1) Data Model (Lake/Warehouse)

### Core tables (Iceberg/Delta/Snowflake/BigQuery friendly)

**Dimensions**

* `dim_users(user_id, signup_date, country, device_type, is_active, …)`

  * SCD2 if you need history: `valid_from`, `valid_to`, `is_current`
* `dim_shows(show_id, title, genre, is_original BOOLEAN, release_date, maturity_rating, …)`
* `dim_geo(country, region_group, language, …)`

**Facts**

* `fact_watch_events( event_id, user_id, show_id, country, watch_seconds, event_ts, src, ingestion_ts )`

  * **Partition**: `event_date = DATE(event_ts)`
  * **Cluster/Z-order**: `country, show_id`
  * **Uniqueness**: `(event_id)` globally unique
* `fact_recommendations(user_id, show_id, recommendation_ts, algo_version, surface, rank_position)`

  * Partition by `DATE(recommendation_ts)`

**Derived (serving)**

* `agg_watch_day_country_show( event_date, country, show_id, total_watch_seconds, viewers, rank_in_country )`

  * Materialized nightly; supports homepage reads.
* `top10_country_day( event_date, country, rank_position, show_id, total_watch_seconds )`

> Tip: Precompute the Top 10 per (country, day) to avoid heavy window functions at read time.

---

## 2) Ingestion & Pipeline (High-level)

**Streaming path**: Player emits events → Kafka → (Flink/Spark Structured Streaming) → bronze (raw) → silver (cleaned/deduped) → **Iceberg table** `fact_watch_events`.

**Batch consolidation** (late data): hourly micro-batches up to **T+2 days** to catch stragglers; recompute daily aggregates idempotently.

**Dedupe policy**:

* Keep first event per `event_id`; if duplicates with different payload, prefer latest `ingestion_ts` but log a **quality exception**.

**Schema evolution**: Iceberg schema with nullable new columns; consumers read by column name.

**Orchestration/SLA**:

* Nightly job (e.g., 02:00 UTC) builds `agg_watch_day_country_show` for **yesterday**;
* Completes by **06:00 local country time**; freshness alerts if miss.

---

## 3) SQL for the Feature

### 3.1 Build daily aggregates (CTEs + window functions)

```sql
-- 1) Clean, deduped daily rollup from watch events
CREATE OR REPLACE TABLE agg_watch_day_country_show AS
WITH base AS (
  SELECT
    DATE(event_ts) AS event_date,
    country,
    show_id,
    SUM(watch_seconds) AS total_watch_seconds,
    COUNT(DISTINCT user_id) AS viewers
  FROM fact_watch_events
  WHERE event_ts >= DATEADD(day, -2, CURRENT_DATE())  -- window for late data if running daily
    AND event_ts < CURRENT_DATE()
  GROUP BY 1,2,3
),
ranked AS (
  SELECT
    event_date,
    country,
    show_id,
    total_watch_seconds,
    viewers,
    RANK() OVER (
      PARTITION BY event_date, country
      ORDER BY total_watch_seconds DESC, viewers DESC, show_id
    ) AS rnk
  FROM base
)
SELECT *
FROM ranked;
```

### 3.2 Materialize Top 10 serving table

```sql
CREATE OR REPLACE TABLE top10_country_day AS
SELECT
  event_date,
  country,
  rnk AS rank_position,
  show_id,
  total_watch_seconds
FROM agg_watch_day_country_show
WHERE rnk <= 10;
```

### 3.3 Read API query (homepage)

```sql
-- Get today’s Top 10 for a user’s country (e.g., US) for yesterday
SELECT rank_position, show_id, total_watch_seconds
FROM top10_country_day
WHERE country = 'US'
  AND event_date = CURRENT_DATE - INTERVAL '1' DAY
ORDER BY rank_position;
```

---

## 4) Supporting Analytics (Interview-favorite queries)

### A) **WoW trend** for Top shows (window + CTE)

```sql
WITH this_week AS (
  SELECT country, show_id, SUM(total_watch_seconds) AS w_watch
  FROM agg_watch_day_country_show
  WHERE event_date >= DATE_TRUNC('week', CURRENT_DATE) - INTERVAL '7' DAY
    AND event_date <  DATE_TRUNC('week', CURRENT_DATE)
  GROUP BY 1,2
),
prev_week AS (
  SELECT country, show_id, SUM(total_watch_seconds) AS w_watch_prev
  FROM agg_watch_day_country_show
  WHERE event_date >= DATE_TRUNC('week', CURRENT_DATE) - INTERVAL '14' DAY
    AND event_date <  DATE_TRUNC('week', CURRENT_DATE) - INTERVAL '7' DAY
  GROUP BY 1,2
)
SELECT
  t.country, t.show_id,
  t.w_watch,
  p.w_watch_prev,
  (t.w_watch - COALESCE(p.w_watch_prev,0)) AS delta,
  CASE WHEN COALESCE(p.w_watch_prev,0) = 0 THEN NULL
       ELSE (t.w_watch - p.w_watch_prev) * 100.0 / p.w_watch_prev END AS pct_change
FROM this_week t
LEFT JOIN prev_week p
  ON t.country = p.country AND t.show_id = p.show_id
ORDER BY pct_change DESC NULLS LAST
LIMIT 20;
```

### B) **Originals vs Licensed share** by country/day

```sql
SELECT
  a.event_date,
  a.country,
  SUM(CASE WHEN s.is_original THEN a.total_watch_seconds ELSE 0 END) AS originals_watch,
  SUM(a.total_watch_seconds) AS total_watch,
  CASE WHEN SUM(a.total_watch_seconds) = 0 THEN 0
       ELSE SUM(CASE WHEN s.is_original THEN a.total_watch_seconds ELSE 0 END) * 100.0
            / SUM(a.total_watch_seconds) END AS originals_share_pct
FROM agg_watch_day_country_show a
JOIN dim_shows s ON a.show_id = s.show_id
GROUP BY 1,2
ORDER BY 1,2;
```

### C) **Recommendation acceptance rate** (watched within 24h)

```sql
WITH rec AS (
  SELECT user_id, show_id, DATE(recommendation_ts) AS rec_date, recommendation_ts
  FROM fact_recommendations
  WHERE DATE(recommendation_ts) = CURRENT_DATE - INTERVAL '1' DAY
),
watch AS (
  SELECT user_id, show_id, event_ts
  FROM fact_watch_events
  WHERE DATE(event_ts) BETWEEN CURRENT_DATE - INTERVAL '1' DAY
                           AND CURRENT_DATE
)
SELECT
  COUNT(DISTINCT r.user_id, r.show_id) AS recs,
  COUNT(DISTINCT CASE
    WHEN w.user_id IS NOT NULL
     AND w.event_ts <= r.recommendation_ts + INTERVAL '24' HOUR
    THEN (r.user_id, r.show_id) END) AS accepted,
  COUNT(DISTINCT CASE
    WHEN w.user_id IS NOT NULL
     AND w.event_ts <= r.recommendation_ts + INTERVAL '24' HOUR
    THEN (r.user_id, r.show_id) END) * 100.0
    / NULLIF(COUNT(DISTINCT r.user_id, r.show_id),0) AS acceptance_pct
FROM rec r
LEFT JOIN watch w
  ON r.user_id = w.user_id AND r.show_id = w.show_id;
```

### D) **7-day streak** (robust streak grouping)

> Works on engines with `DATEDIFF` to an epoch.

```sql
WITH daily AS (
  SELECT DISTINCT user_id, DATE(event_ts) AS d
  FROM fact_watch_events
),
numbered AS (
  SELECT
    user_id,
    d,
    DATEDIFF(day, DATE '1970-01-01', d)
      - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY d) AS grp
  FROM daily
),
streaks AS (
  SELECT user_id, grp, COUNT(*) AS streak_len
  FROM numbered
  GROUP BY 1,2
)
SELECT DISTINCT user_id
FROM streaks
WHERE streak_len >= 7;
```

### E) **Approximate DAU** (big data friendly)

* Use HLL/HyperLogLog if available:

```sql
SELECT
  DATE(event_ts) AS d,
  HLL_COUNT.INIT(user_id) AS dau_hll  -- engine-specific
FROM fact_watch_events
GROUP BY 1;
```

---

## 5) Data Quality (critical for Netflix)

### Categories & example tests (SQL/dbt-style)

**Completeness**

```sql
-- Expect partitions for all countries yesterday
SELECT country
FROM dim_geo
WHERE country NOT IN (
  SELECT DISTINCT country
  FROM agg_watch_day_country_show
  WHERE event_date = CURRENT_DATE - INTERVAL '1' DAY
);
-- Alert if any rows returned
```

**Freshness**

```sql
-- Max ingestion time for yesterday’s data
SELECT MAX(ingestion_ts) AS last_arrival
FROM fact_watch_events
WHERE DATE(event_ts) = CURRENT_DATE - INTERVAL '1' DAY;
-- Alert if last_arrival > 06:00 local cutoff or NULL
```

**Uniqueness**

```sql
-- event_id must be unique
SELECT event_id
FROM fact_watch_events
GROUP BY event_id
HAVING COUNT(*) > 1;
```

**Validity**

```sql
-- No negative or absurd watch_seconds
SELECT COUNT(*) AS bad_rows
FROM fact_watch_events
WHERE watch_seconds < 0 OR watch_seconds > 24*60*60;
```

**Referential integrity**

```sql
-- Orphan watch events
SELECT COUNT(*) AS orphans
FROM fact_watch_events e
LEFT JOIN dim_users u ON e.user_id = u.user_id
WHERE u.user_id IS NULL;
```

**Reconciliation**

```sql
-- Compare rollup to source within tolerance
WITH src AS (
  SELECT DATE(event_ts) d, country, show_id, SUM(watch_seconds) s
  FROM fact_watch_events
  WHERE DATE(event_ts) = CURRENT_DATE - INTERVAL '1' DAY
  GROUP BY 1,2,3
),
agg AS (
  SELECT event_date d, country, show_id, total_watch_seconds s
  FROM agg_watch_day_country_show
  WHERE event_date = CURRENT_DATE - INTERVAL '1' DAY
)
SELECT *
FROM src s
JOIN agg a USING (d, country, show_id)
WHERE ABS(s.s - a.s) > 5; -- >5 seconds tolerance
```

**SLA guardrail (serving table)**

```sql
SELECT COUNT(*) AS top10_ready
FROM top10_country_day
WHERE event_date = CURRENT_DATE - INTERVAL '1' DAY;
-- Alert if 0
```

---

## 6) Performance Tips

* **Partition pruning**: always filter by `event_date` first.
* **Clustering**: `country, show_id` → speeds Top-10 ranking scans.
* **Stats**: ANALYZE/OPTIMIZE tables post-load to keep metadata fresh.
* **Precompute**: `top10_country_day` avoids runtime window sorts.
* **Late data**: rerun last 2 days aggregates idempotently; keep a watermark column.

---

## 7) Edge Cases (call these out in interviews)

* **Title merges/splits** (show id changes) → maintain a `show_canonical_id` map table.
* **Kids profiles** → optionally exclude from certain leaderboards.
* **Bots/test traffic** → filter by `device_type`, `src`, or an allowlist of real players.
* **Multiple accounts per household** → country inference from IP vs billing; pick a consistent rule.

---

## 8) What to say out loud (meta)

* Start with the **serving question** (“Top 10 by country per day”).
* Propose a **star schema**; justify **partitioning** and **clustering**.
* Show **one precise SQL** for rank + a **serving table**.
* Call out **data quality** checks and **SLA**.
* Mention **late data** and **idempotent recompute**.
* Offer **WoW deltas** and **Originals share** for PMs.

---

If you want, I can turn this into a **one-pager you can print** or a **dbt-style checklist** with the exact tests/materializations.
