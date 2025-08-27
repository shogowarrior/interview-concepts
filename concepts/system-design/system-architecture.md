# System Architecture

## Overview
Netflix's system architecture handles massive scale with billions of events daily, supporting real-time recommendations, global content delivery, and analytics.

## Core Architecture Components

### 1. Data Ingestion Layer

```sql
-- Kafka topic structure for different event types
CREATE TABLE event_topics (
  topic_name STRING,
  event_type STRING,                -- 'playback', 'recommendation', 'billing'
  partition_key STRING,             -- 'user_id', 'session_id', 'title_id'
  retention_hours INT,
  replication_factor INT
);

-- Raw event storage in data lake
CREATE TABLE raw_events (
  event_id STRING,
  event_type STRING,
  event_data JSON,
  ingestion_ts TIMESTAMP,
  source STRING,                    -- 'client', 'server', 'partner'
  partition_date DATE
) PARTITIONED BY (partition_date);
```

### 2. Stream Processing Architecture

```sql
-- Real-time stream processing jobs
CREATE TABLE stream_jobs (
  job_id STRING PRIMARY KEY,
  job_name STRING,
  source_topic STRING,
  sink_table STRING,
  processing_logic STRING,         -- SQL or code reference
  window_type STRING,              -- tumbling, sliding, session
  window_size_seconds INT,
  watermark_delay_seconds INT
);

-- State stores for streaming analytics
CREATE TABLE stream_state (
  state_key STRING,
  state_value JSON,
  last_updated TIMESTAMP,
  ttl_seconds INT,
  PRIMARY KEY (state_key)
);
```

### 3. Lambda Architecture Pattern

```sql
-- Speed layer (real-time)
CREATE TABLE realtime_metrics (
  metric_name STRING,
  metric_value DOUBLE,
  window_start TIMESTAMP,
  window_end TIMESTAMP,
  computed_at TIMESTAMP,
  PRIMARY KEY (metric_name, window_start)
);

-- Batch layer (historical accuracy)
CREATE TABLE batch_metrics (
  metric_name STRING,
  date_partition DATE,
  metric_value DOUBLE,
  computed_at TIMESTAMP,
  PRIMARY KEY (metric_name, date_partition)
);

-- Serving layer (merged view)
CREATE VIEW unified_metrics AS
SELECT
  m.metric_name,
  m.window_start,
  m.metric_value,
  'realtime' AS source
FROM realtime_metrics m
WHERE m.window_end > CURRENT_TIMESTAMP - INTERVAL '1' HOUR

UNION ALL

SELECT
  m.metric_name,
  m.date_partition AS window_start,
  m.metric_value,
  'batch' AS source
FROM batch_metrics m
WHERE m.date_partition < CURRENT_DATE - INTERVAL '1' DAY;
```

## Scalability Patterns

### 1. Database Sharding Strategy

```sql
-- User data sharding by consistent hashing
CREATE TABLE user_shard_map (
  user_id BIGINT,
  shard_id INT,
  shard_host STRING,
  created_at TIMESTAMP,
  PRIMARY KEY (user_id)
);

-- Content metadata sharding
CREATE TABLE content_shard_map (
  title_id BIGINT,
  shard_id INT,
  shard_host STRING,
  PRIMARY KEY (title_id)
);

-- Cross-shard queries using scatter-gather
CREATE TABLE distributed_query_cache (
  query_hash STRING,
  results JSON,
  completed_shards INT,
  total_shards INT,
  created_at TIMESTAMP,
  PRIMARY KEY (query_hash)
);
```

### 2. Caching Layer Architecture

```sql
-- Multi-level caching strategy
CREATE TABLE cache_layers (
  layer_name STRING PRIMARY KEY,
  cache_type STRING,               -- 'local', 'distributed', 'edge'
  ttl_seconds INT,
  max_size_mb INT,
  hit_rate_target DOUBLE
);

-- Cache invalidation events
CREATE TABLE cache_invalidation_events (
  event_id STRING PRIMARY KEY,
  cache_key STRING,
  invalidation_reason STRING,
  triggered_at TIMESTAMP,
  processed_at TIMESTAMP
);
```

## Content Delivery Network (CDN) Integration

```sql
-- CDN log analysis for performance monitoring
CREATE TABLE cdn_logs (
  request_id STRING,
  user_id BIGINT,
  title_id BIGINT,
  cdn_edge_location STRING,
  response_time_ms INT,
  bytes_transferred BIGINT,
  http_status INT,
  request_ts TIMESTAMP,
  user_country STRING
) PARTITIONED BY (dt DATE);

-- Adaptive bitrate decisioning
CREATE TABLE playback_quality_decisions (
  session_id STRING,
  title_id BIGINT,
  user_id BIGINT,
  device_type STRING,
  connection_speed_mbps DOUBLE,
  selected_bitrate_kbps INT,
  buffer_health_seconds INT,
  decision_ts TIMESTAMP
);
```

## Microservices Architecture

```sql
-- Service registry for microservices discovery
CREATE TABLE service_registry (
  service_name STRING,
  service_instance STRING,
  host STRING,
  port INT,
  health_status STRING,
  last_heartbeat TIMESTAMP,
  PRIMARY KEY (service_name, service_instance)
);

-- Distributed tracing for request correlation
CREATE TABLE trace_events (
  trace_id STRING,
  span_id STRING,
  parent_span_id STRING,
  service_name STRING,
  operation_name STRING,
  start_time TIMESTAMP,
  duration_ms INT,
  tags JSON
);
```

## Global Data Replication

```sql
-- Cross-region replication status
CREATE TABLE replication_status (
  table_name STRING,
  source_region STRING,
  target_region STRING,
  last_replication_ts TIMESTAMP,
  replication_lag_seconds INT,
  status STRING,
  PRIMARY KEY (table_name, source_region, target_region)
);

-- Regional data sovereignty compliance
CREATE TABLE data_residency_rules (
  data_type STRING,
  allowed_regions ARRAY<STRING>,
  retention_days INT,
  encryption_required BOOLEAN,
  PRIMARY KEY (data_type)
);
```

## Design Principles

### 1. Failure Handling
- **Circuit Breakers**: Automatic failure detection and recovery
- **Graceful Degradation**: Core features remain available during outages
- **Idempotent Operations**: Safe retry of failed operations

### 2. Observability
- **Metrics Collection**: Comprehensive monitoring of all systems
- **Distributed Tracing**: End-to-end request visibility
- **Log Aggregation**: Centralized logging for debugging

### 3. Security Architecture
- **Zero Trust**: Authentication for all service-to-service communication
- **Data Encryption**: At rest and in transit
- **Access Control**: Fine-grained permissions and audit trails

## Performance Considerations

- **Hot Data Path**: Optimize for 99th percentile performance
- **Cold Data Path**: Cost-effective storage for historical data
- **Data Locality**: Process data close to where it's generated
- **Auto-scaling**: Automatic resource adjustment based on load

## Follow-up Questions

- How would you design for 99.99% uptime across global regions?
- How would you handle data consistency in a multi-region architecture?
- How would you implement canary deployments for microservices?
- How would you design the system to handle 10x traffic growth?