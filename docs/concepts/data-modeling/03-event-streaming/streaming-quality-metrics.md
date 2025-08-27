# Streaming Quality Metrics

## Overview

Designing a schema to log playback quality metrics including bitrate, buffering, errors, and streaming session data for monitoring and analytics.

## Core Concepts

* Use `playback_event` (from viewing history) with QoS fields; or a dedicated QoS topic/table.
* Granular event logging enables detailed analysis of streaming performance and user experience.

## Core Schema

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

## Rollup Aggregations

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

## Lakehouse Layout

* `qos_event` **partition** by `dt = DATE(event_time)` for time-based analysis
* **Cluster** by `session_id` to keep related events together
* Consider additional partitioning by `cdn` or `region` for geo-specific analysis
* `qos_session_summary` can be partitioned by session date for efficient rollup queries

## Query Examples

* **Rebuffer analysis**: `SELECT AVG(rebuffer_ratio) FROM qos_session_summary WHERE dt >= '2024-01-01'`
* **CDN performance**: `SELECT cdn, AVG(avg_bitrate), COUNT(*) FROM qos_session_summary GROUP BY cdn`
* **Error investigation**: `SELECT error_code, COUNT(*) FROM qos_event WHERE dt = '2024-01-01' GROUP BY error_code`

## Metric Definitions

* `rebuffer_ratio = rebuffer_time / session_time` - Primary QoS metric
* `startup_time` - Time from play button to first frame
* `bitrate_switches` - Count of adaptive bitrate changes during session
* `error_rate` - Percentage of sessions with streaming errors

## Trade-offs Discussion

* **Granular vs. Aggregated**: Store detailed events for analysis vs. pre-computed metrics for dashboards
* **Real-time vs. Batch**: Stream processing for real-time alerts vs. batch processing for historical analysis
* **Storage cost**: Detailed events provide flexibility but increase storage costs significantly

## Streaming Platform Context

* **Global CDN optimization**: Multiple CDNs need performance monitoring across all
* **Device diversity**: QoS metrics vary significantly by device type (mobile, TV, web, gaming consoles)
* **Content-adaptive streaming**: Different content types have different quality requirements
* **Regional performance**: Internet infrastructure varies dramatically by region
* **Real-time monitoring**: Critical for detecting and responding to streaming issues immediately

## Performance Monitoring Use Cases

### Real-time Alerts

* Sudden spike in rebuffer rates
* Regional streaming degradation
* CDN performance issues

### Capacity Planning

* Peak concurrent streams by region
* Bandwidth utilization trends
* Content popularity vs. quality trade-offs

### Product Optimization

* A/B tests of different bitrate algorithms
* Device-specific quality optimizations
* Content encoding improvements

## Follow-up Considerations

* How would you design real-time QoS monitoring and alerting?
* What are the trade-offs between different QoS metrics for different content types?
* How do you handle the volume of QoS events at scale?

---

Navigate back to [Event Streaming](./) | [Data Modeling Index](../README.md)
