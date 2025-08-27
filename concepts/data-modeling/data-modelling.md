Awesome—here are compact, interview-ready “solutions” for each prompt. I keep them practical (entities, keys, partitions, formats, and a few example queries/trade-offs) so you can speak to both OLTP-ish schemas and analytics/lakehouse patterns.

---

# 1) Content Catalog (titles, seasons, episodes, genres, localization)

**Core entities**

* `title` (movie or show), `season`, `episode`, `genre`, many-to-many `title_genre`
* Localization stored separately per locale.

**Relational-ish DDL**

```sql
-- Type can be MOVIE or SHOW
CREATE TABLE title (
  title_id BIGINT PRIMARY KEY,
  type STRING NOT NULL,
  release_date DATE,
  maturity_rating STRING,
  production_country STRING,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE season (
  season_id BIGINT PRIMARY KEY,
  title_id BIGINT NOT NULL REFERENCES title(title_id),
  season_number INT NOT NULL,
  UNIQUE(title_id, season_number)
);

CREATE TABLE episode (
  episode_id BIGINT PRIMARY KEY,
  title_id BIGINT NOT NULL REFERENCES title(title_id),
  season_id BIGINT REFERENCES season(season_id),
  episode_number INT,
  duration_sec INT,
  UNIQUE(title_id, season_id, episode_number)
);

CREATE TABLE genre (
  genre_id INT PRIMARY KEY,
  name STRING UNIQUE
);

CREATE TABLE title_genre (
  title_id BIGINT REFERENCES title(title_id),
  genre_id INT REFERENCES genre(genre_id),
  PRIMARY KEY (title_id, genre_id)
);

-- Localization (can apply to titles, seasons, or episodes)
CREATE TABLE localized_metadata (
  object_type STRING CHECK (object_type IN ('TITLE','SEASON','EPISODE')),
  object_id BIGINT,
  locale STRING,                      -- e.g., en-US, es-MX
  localized_title STRING,
  localized_description STRING,
  PRIMARY KEY (object_type, object_id, locale)
);
```

**Lakehouse layout**

* Tables in Delta/Iceberg; **partition** `title` sparsely (usually not necessary).
* For big read throughput on `episode`, consider **clustering/bucketing** by `title_id`.
* `localized_metadata` clustered by `(object_type, object_id)`; filter by `locale`.

**Queries**

* Get all episodes of S2 for a show: filter `title_id` + `season_number=2`, join `episode`.
* Localized listing: join `localized_metadata` on requested `locale`, fallback to `en-US`.

**Trade-offs**

* Keep movies and shows unified in `title` to simplify cross-type queries.
* Localization separated avoids column bloat and supports sparse locales.

---

# 2) User Viewing History (partial watch, multiple devices, resume)

**Concepts**

* A *playback session* per device/profile; fine-grained *events*; a compact *resume state*.

**DDL**

```sql
CREATE TABLE account (
  account_id BIGINT PRIMARY KEY
);
CREATE TABLE profile (
  profile_id BIGINT PRIMARY KEY,
  account_id BIGINT REFERENCES account(account_id),
  maturity_setting STRING,
  country_code STRING
);
CREATE TABLE device (
  device_id STRING PRIMARY KEY,       -- GUID or device fingerprint
  device_type STRING,                 -- TV, mobile, web
  os_version STRING
);

CREATE TABLE playback_session (
  session_id STRING PRIMARY KEY,      -- UUID
  profile_id BIGINT REFERENCES profile(profile_id),
  device_id STRING REFERENCES device(device_id),
  title_id BIGINT,
  episode_id BIGINT NULL,
  started_at TIMESTAMP,
  ended_at TIMESTAMP NULL
);

-- Append-only granular timeline
CREATE TABLE playback_event (
  session_id STRING,
  event_time TIMESTAMP,
  event_type STRING,              -- PLAY, PAUSE, SEEK, BITRATE_CHANGE, END, ERROR
  position_sec INT,               -- current playhead
  bitrate_kbps INT NULL,
  PRIMARY KEY (session_id, event_time)
);

-- Denormalized current resume pointer (updated by stream job)
CREATE TABLE resume_state (
  profile_id BIGINT,
  title_id BIGINT,
  episode_id BIGINT NULL,
  last_position_sec INT,
  last_update TIMESTAMP,
  PRIMARY KEY (profile_id, COALESCE(episode_id, title_id))
);
```

**Lakehouse**

* `playback_event` **partition** by `dt=date(event_time)` and optionally `country_code`; **cluster** by `session_id`.
* `resume_state` small, unpartitioned; updated via incremental job from events.

**Continue Watching query**

* Select top N from `resume_state` for a profile ordered by `last_update` desc.

**Trade-offs**

* Store events append-only (immutable) → accurate replays; derive `resume_state` to serve fast UX.

---

# 3) Recommendations storage (relationships & features)

**Layers**

1. **Interactions**: views, ratings, thumbs, dwell time (from events).
2. **Similarity graph**: `item_item_edge` with score & model metadata.
3. **Personalized recs**: per-profile top-K lists per context (home row, genre row).
4. **Model lineage**: which model/version produced which list.

**DDL (analytics)**

```sql
CREATE TABLE item_item_edge (
  src_title_id BIGINT,
  dst_title_id BIGINT,
  score DOUBLE,
  model VARCHAR,            -- e.g., 'itemCF', 'graphSage'
  model_version STRING,
  computed_at TIMESTAMP,
  PRIMARY KEY (src_title_id, dst_title_id, model, model_version)
);

CREATE TABLE personalized_recs (
  profile_id BIGINT,
  context STRING,           -- 'home', 'because_you_watched', 'kids'
  rank INT,
  title_id BIGINT,
  score DOUBLE,
  model STRING,
  model_version STRING,
  generated_at TIMESTAMP,
  PRIMARY KEY (profile_id, context, rank, generated_at)
);

CREATE TABLE feature_store_items (
  title_id BIGINT PRIMARY KEY,
  embedding VECTOR(256)     -- or store in a vector DB; here as opaque blob/bytes
);
```

**Serving**

* Latest `personalized_recs` for `(profile_id, context)`; TTL and regeneration SLAs.
* For candidate gen on the fly: pull `item_item_edge` for last-watched titles.

**Trade-offs**

* Precompute top-K for speed; keep edges for diversity/cold-start logic; store model lineage for A/B/debug.

---

# 4) Accounts, Profiles, Devices

```sql
CREATE TABLE account (
  account_id BIGINT PRIMARY KEY,
  created_at TIMESTAMP,
  home_country STRING,
  billing_currency STRING
);

CREATE TABLE profile (
  profile_id BIGINT PRIMARY KEY,
  account_id BIGINT REFERENCES account(account_id),
  name STRING,
  is_kids BOOLEAN,
  language_pref STRING,
  created_at TIMESTAMP
);

CREATE TABLE device (
  device_id STRING PRIMARY KEY,
  account_id BIGINT REFERENCES account(account_id),
  device_type STRING,
  registered_at TIMESTAMP
);

CREATE TABLE profile_device_link (
  profile_id BIGINT REFERENCES profile(profile_id),
  device_id STRING REFERENCES device(device_id),
  PRIMARY KEY (profile_id, device_id)
);
```

**Notes**

* Device belongs to account; link to profiles many-to-many for usage/permissions.
* Enforce device limits via a separate `active_streams` store or cache keyed by `account_id`.

---

# 5) Subscriptions, Billing, Promotions, Payments

**Concepts**

* Subscription *state machine* with effective-dated changes (SCD-2 style).
* Separate **invoice** and **payment** for accounting; support partials/refunds.

```sql
CREATE TABLE plan (
  plan_id STRING PRIMARY KEY,        -- 'STANDARD_ADS', 'PREMIUM'
  price_cents INT,
  currency STRING,
  max_screens INT,
  hdr BOOLEAN,
  ads_supported BOOLEAN
);

-- Effective-dated subscription records
CREATE TABLE subscription (
  subscription_id BIGINT PRIMARY KEY,
  account_id BIGINT,
  plan_id STRING REFERENCES plan(plan_id),
  status STRING,                     -- ACTIVE, PAUSED, CANCELED
  start_date DATE,
  end_date DATE NULL                 -- null = current
);

CREATE TABLE promotion (
  promo_code STRING PRIMARY KEY,
  discount_type STRING,              -- PCT or FIXED
  discount_value DOUBLE,
  start_date DATE,
  end_date DATE
);

CREATE TABLE subscription_event (
  event_id BIGINT PRIMARY KEY,
  subscription_id BIGINT REFERENCES subscription(subscription_id),
  event_time TIMESTAMP,
  event_type STRING,                 -- UPGRADE, DOWNGRADE, CANCEL, RESUME, RENEW
  old_plan_id STRING,
  new_plan_id STRING,
  note STRING
);

CREATE TABLE invoice (
  invoice_id BIGINT PRIMARY KEY,
  account_id BIGINT,
  period_start DATE,
  period_end DATE,
  amount_due_cents INT,
  currency STRING,
  promo_code STRING NULL REFERENCES promotion(promo_code),
  created_at TIMESTAMP,
  status STRING                      -- OPEN, PAID, VOID
);

CREATE TABLE payment (
  payment_id BIGINT PRIMARY KEY,
  invoice_id BIGINT REFERENCES invoice(invoice_id),
  amount_cents INT,
  currency STRING,
  method STRING,                     -- card, paypal, gift
  status STRING,                     -- AUTH, CAPTURED, REFUNDED, FAILED
  created_at TIMESTAMP
);
```

**Handling mid-cycle plan changes**

* Emit `subscription_event` + proration logic in billing job: create a credit line on current invoice; new pro-rated charge line.

---

# 6) Engagement Metrics (DAU by region)

**Ingest**

* Client/app pings → `app_event` (login, foreground, heartbeat) with `profile_id`, `region`, `event_time`.

**Lakehouse table**

```sql
CREATE TABLE app_event (
  profile_id BIGINT,
  account_id BIGINT,
  region STRING,                      -- e.g., US, BR, IN
  event_name STRING,
  event_time TIMESTAMP
) PARTITIONED BY (dt DATE)            -- dt = DATE(event_time)
CLUSTER BY (region, profile_id);
```

**Metric build**

```sql
-- DAU per region (distinct profiles with any event)
CREATE OR REPLACE VIEW dau_by_region AS
SELECT
  dt,
  region,
  COUNT(DISTINCT profile_id) AS dau
FROM app_event
GROUP BY dt, region;
```

**Notes**

* Use incremental processing per `dt`; compact small files; Z-Order/cluster by `region` if supported.

---

# 7) A/B Testing (experiments, assignments, outcomes)

```sql
CREATE TABLE experiment (
  exp_id STRING PRIMARY KEY,
  name STRING,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  unit STRING,                    -- PROFILE or ACCOUNT
  primary_kpi STRING              -- e.g., 7d hours watched
);

CREATE TABLE variant (
  exp_id STRING REFERENCES experiment(exp_id),
  variant_id STRING,              -- 'control','treatment_a'
  traffic_pct DOUBLE,
  PRIMARY KEY (exp_id, variant_id)
);

CREATE TABLE assignment (
  exp_id STRING,
  unit_id STRING,                 -- profile_id or account_id as text
  variant_id STRING,
  assigned_at TIMESTAMP,
  PRIMARY KEY (exp_id, unit_id)
) PARTITIONED BY (exp_id);

-- Outcomes joined from facts (watch hours, conversions, etc.)
CREATE TABLE kpi_outcome (
  exp_id STRING,
  unit_id STRING,
  metric_date DATE,
  kpi_name STRING,                -- 'watch_hours', 'retention_d30'
  kpi_value DOUBLE,
  PRIMARY KEY (exp_id, unit_id, metric_date, kpi_name)
);
```

**Analysis**

* Guardrails: compare pre-period covariates; use CUPED or stratification.
* Avoid contamination: unit = `profile` for recs; `account` for pricing.

---

# 8) Streaming Quality (bitrate, buffering, errors)

**Granular**

* Use `playback_event` (from #2) with QoS fields; or a dedicated QoS topic/table.

```sql
CREATE TABLE qos_event (
  session_id STRING,
  event_time TIMESTAMP,
  q_event STRING,                 -- STARTUP, BUFFERING_START, BUFFERING_END, BITRATE_CHANGE, ERROR
  position_sec INT,
  bitrate_kbps INT,
  cdn STRING,
  error_code STRING NULL,
  PRIMARY KEY (session_id, event_time)
) PARTITIONED BY (dt DATE);
```

**Rollups**

```sql
-- Per session QoS summary
CREATE TABLE qos_session_summary AS
SELECT
  session_id,
  MIN(event_time) AS start_time,
  MAX(event_time) AS end_time,
  SUM(CASE WHEN q_event='BUFFERING_START' THEN 1 ELSE 0 END) AS rebuffer_count,
  SUM(rebuffer_duration_sec) AS rebuffer_time_sec,   -- computed via pairing START/END
  AVG(bitrate_kbps) AS avg_bitrate
FROM transform_qos_events(/* window/pairs */)
GROUP BY session_id;
```

**Use**

* Monitor `rebuffer_ratio = rebuffer_time / session_time` by device/region/CDN.

---

# 9) Event Streaming @ scale (schema, processing, queryability)

**Ingestion design**

* Kafka topics: `playback_events`, `app_events`, `billing_events`.
* **Schema Registry** with Avro/Protobuf for evolution (backward compatible).
* Keys:

  * `session_id` for `playback_events` (affinity ordering).
  * `profile_id` for `app_events`.
* Partitions sized to peak throughput; enable idempotent producers + exactly-once sinks (e.g., Spark Structured Streaming + Delta).

**Bronze/Silver/Gold**

* **Bronze**: raw JSON/Avro → `dt` partition, no transforms.
* **Silver**: cleaned & typed; dedup on `(session_id, event_time)`; join dims (country, device).
* **Gold**: business aggregates (`resume_state`, `dau_by_region`, `qos_session_summary`).

**Storage formats**

* **Delta/Iceberg** + Parquet; ZSTD or Snappy; optimize file sizes 128–512 MB.

**Queryability**

* Precompute serving tables (resume, top-K recs).
* Enable ad-hoc via Trino/Spark; use clustering for high-selectivity keys.

---

# 10) Partitioning & Sharding user watch history

**Goal**

* Balance write load, avoid hot partitions, enable common queries.

**Choices**

* **Partition column** (lake): `dt = DATE(event_time)`; maybe `region`.
* **Cluster/Bucket** (lake/warehouse): `profile_id` or `session_id` to collocate events.
* **OLTP sharding** (if needed):

  * Shard key = `account_id` or `profile_id` using consistent hashing.
  * Pros `profile_id`: isolates heavy users; good affinity for per-profile queries.
  * Pros `account_id`: easy household-level enforcement (device limits).
* **Hot keys**: VIPs or major launches → add **composite key** (`profile_id` + modulo/random salt) for write spreading; reassemble with map-side combine.
* **Skew management**: periodic **rebalancing** for shards with disproportionate size; use **auto-splitting** if supported.

**Examples**

* Lake: `playback_event` → `PARTITION BY dt` and **CLUSTER BY (session\_id)**.
* Warehouse: **bucketing** `playback_event` by `profile_id` into, say, 256 buckets to speed joins with `profile` and rollups.

**Trade-offs**

* Over-partitioning (`dt`, `hour`, `region`) → too many small files. Prefer `dt` + clustering; run optimize/compaction jobs.
* Using `profile_id` as shard key complicates account-level queries; mitigate via secondary indexes/materialized views.

---

## Extra: Storage & governance guardrails (handy in interviews)

* **PII separation**: store PII (email, payment tokens) in a restricted table/key vault; reference by surrogate IDs.
* **Slowly Changing Dimensions**: use SCD2 for plans/regions to support point-in-time analytics.
* **Data quality**: contracts + expectations (e.g., Great Expectations/Deequ) with fail-open/closed strategy by table.
* **Backfills**: design idempotent jobs and partition filters; track backfill lineage.

---

If you want, I can turn any one of these into a 10–15 min whiteboard walkthrough with sample diagrams and “what would you do if…” follow-ups (perfect mock practice).
