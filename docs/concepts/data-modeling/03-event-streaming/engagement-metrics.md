# Engagement Metrics

## Overview

Designing data models to capture user engagement metrics like Daily Active Users (DAU) by region, enabling efficient aggregation from client logs and app events.

## Ingest Architecture

* Client/app pings → `app_event` (login, foreground, heartbeat) with `profile_id`, `region`, `event_time`.
* Event streaming platform (Kafka) → Bronze layer (raw events) → Silver layer (cleaned) → Gold layer (metrics).

## Core Schema

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

## Metric Computations

```sql
-- DAU per region (distinct profiles with any event)
CREATE OR REPLACE VIEW dau_by_region AS
SELECT
  dt,
  region,
  COUNT(DISTINCT profile_id) AS dau
FROM app_event
GROUP BY dt, region;

-- Engagement depth metrics
CREATE TABLE engagement_metrics AS
SELECT
  dt,
  region,
  profile_id,
  COUNT(CASE WHEN event_name = 'play' THEN 1 END) AS play_events,
  COUNT(CASE WHEN event_name = 'search' THEN 1 END) AS search_events,
  COUNT(DISTINCT title_id) AS unique_titles_viewed,
  SUM(CASE WHEN event_name = 'play' THEN duration_sec ELSE 0 END) AS total_watch_time_sec
FROM enriched_app_events
GROUP BY dt, region, profile_id;
```

## Lakehouse Layout

* **Bronze layer**: Raw `app_event` partitioned by `dt`, minimal transformation
* **Silver layer**: Enriched events with dimensions (user country, device type, content metadata)
* **Gold layer**: Aggregated metrics pre-computed for dashboard and analysis
* **Incremental processing**: Use Delta Live Tables or Spark Structured Streaming for continuous updates

## Query Examples

* **DAU trend**: `SELECT dt, SUM(dau) FROM dau_by_region WHERE dt >= '2024-01-01' GROUP BY dt ORDER BY dt`
* **Regional analysis**: `SELECT region, AVG(dau) FROM dau_by_region WHERE dt >= '2024-01-01' GROUP BY region`
* **Engagement segments**: `SELECT CASE WHEN play_events >= 5 THEN 'high' ELSE 'low' END as segment, COUNT(*) FROM engagement_metrics GROUP BY 1`

## Event Types

### Core Engagement Events

* `app_start` - Application launched
* `login` - User authentication
* `browse` - Content browsing/scrolling
* `search` - Search queries
* `play` - Content playback started
* `pause` - Playback paused
* `resume` - Playback resumed
* `stop` - Playback stopped
* `heartbeat` - Periodic activity ping

### Business Events

* `subscription_change` - Plan upgrades/downgrades
* `profile_switch` - Switching between profiles
* `device_change` - Switching devices
* `content_rating` - Thumbs up/down

## Metric Definitions

### Primary Metrics

* **DAU (Daily Active Users)**: Distinct profiles active per day
* **MAU (Monthly Active Users)**: Distinct profiles active in rolling 30 days
* **Session duration**: Time spent in app per session
* **Content engagement**: Plays, searches, browsing time

### Derived Metrics

* **Retention rate**: Percentage of users returning after N days
* **Engagement rate**: DAU/MAU ratio
* **Churn rate**: Percentage of users who become inactive
* **Feature adoption**: Usage of specific app features

## Trade-offs Discussion

### Granularity vs. Performance

* **Detailed events**: Enable deep analysis but require significant storage and processing
* **Aggregated metrics**: Fast queries but lose ability to drill down
* **Hybrid approach**: Keep detailed events for recent data, aggregate older data

### Real-time vs. Accuracy

* **Real-time dashboards**: Approximate counts for immediate insights
* **Batch accuracy**: Precise metrics computed with full data
* **Lambda architecture**: Combine both approaches for comprehensive analytics

## Streaming Platform Context

* **Global scale**: 200M+ subscribers across 190+ countries
* **Multiple apps**: TV, mobile, web, gaming console platforms
* **Content diversity**: Movies, TV shows, documentaries, stand-up comedy
* **Regional preferences**: Different content popularity by region
* **Device ecosystem**: Smart TVs, streaming devices, mobile, web browsers

## Analytics Use Cases

### Product Analytics

* Feature usage and adoption rates
* User journey analysis and funnel metrics
* A/B test results and experiment analysis

### Operational Monitoring

* System performance and reliability metrics
* Content delivery and playback success rates
* Regional infrastructure utilization

### Business Intelligence

* Revenue per user and subscription analytics
* Content performance and popularity trends
* Market expansion and growth metrics

## Follow-up Considerations

* How would you design a real-time DAU dashboard that handles scale?
* What are the trade-offs between different event sampling strategies?
* How do you ensure data quality and consistency across different app platforms?

---

Navigate back to [Event Streaming](./) | [Data Modeling Index](../README.md)
