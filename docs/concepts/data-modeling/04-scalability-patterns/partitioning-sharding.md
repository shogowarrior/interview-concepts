# Partitioning & Sharding

## Overview

Designing partitioning keys and sharding strategies for storing user watch history in distributed systems, balancing write load and enabling common queries.

## Core Goals

* **Balance write load**: Avoid hot partitions that cause performance bottlenecks
* **Enable common queries**: Optimize for frequently accessed data patterns
* **Support scale**: Handle massive user base and content catalog
* **Ensure availability**: Maintain service during failures and maintenance

## Partitioning Strategies

### Lakehouse Partitioning

**Date-based partitioning** (most common):

```sql
-- Primary partitioning by event time
CREATE TABLE playback_event (
  session_id STRING,
  profile_id BIGINT,
  event_time TIMESTAMP,
  event_type STRING,
  position_sec INT
) PARTITIONED BY (dt DATE);  -- dt = DATE(event_time)
```

**Composite partitioning** (for complex queries):

```sql
-- Multiple levels of partitioning
PARTITIONED BY (
  year INT,     -- Year for long-term retention
  month INT,    -- Month for medium-term analysis
  dt DATE       -- Day for operational queries
)
```

### Clustering/Bucketing

**Co-locate related data** for efficient joins:

```sql
-- Cluster by session_id for session analysis
CLUSTER BY (session_id)

-- Bucket by profile_id for user analytics
CLUSTER BY (profile_id) INTO 256 BUCKETS
```

## Sharding Strategies

### OLTP Sharding (Real-time Serving)

**Profile-based sharding**:

```python
# Consistent hashing for profile_id

def get_shard(profile_id):
    hash_value = hash(profile_id) % num_shards
    return f"shard_{hash_value}"

# Pros Isolates heavy users, good for per-profile queries

# Cons Complicates account-level queries
```

**Account-based sharding**:

```python
def get_shard(account_id):
    return f"account_shard_{account_id % num_shards}"

# Pros Easy household-level enforcement (device limits)

# Cons Uneven load if account sizes vary significantly
```

### Hot Key Management

**Key salting** for VIP users:

```python
def salt_key(profile_id, num_salt_buckets=10):
    if is_vip_user(profile_id):
        salt = random.randint(0, num_salt_buckets)
        return f"{salt}_{profile_id}"
    return profile_id
```

**Composite keys** for write spreading:

```python
def composite_key(profile_id):
    # Add modulo-based suffix for heavy users
    if is_heavy_user(profile_id):
        suffix = profile_id % 100  # Spread across 100 virtual shards
        return f"{profile_id}_{suffix}"
    return profile_id
```

## Storage Tiers

### Hot Storage (Real-time)

* **Cassandra/DynamoDB**: For serving layer with strict SLAs
* **Sharding**: By user ID for personalization queries
* **Replication**: Multi-region for global availability
* **TTL**: Automatic expiration of old data

### Warm Storage (Analytics)

* **Delta Lake**: For batch analytics and ML feature engineering
* **Partitioning**: Date-based for time-series analysis
* **Clustering**: By user dimensions for efficient queries
* **Compression**: ZSTD for storage efficiency

### Cold Storage (Archive)

* **S3/Cloud Storage**: For long-term retention and compliance
* **Partitioning**: Year/month for cost-effective lifecycle management
* **Compression**: High compression ratios for archival

## Query Optimization

### Serving Layer Queries

```sql
-- Fast user queries (OLTP)
SELECT * FROM user_sessions
WHERE profile_id = ? AND session_id = ?
ORDER BY event_time DESC
LIMIT 10

-- Optimized with composite index on (profile_id, event_time)
```

### Analytics Queries

```sql
-- Aggregation queries (OLAP)
SELECT
  dt,
  COUNT(DISTINCT profile_id) as dau,
  AVG(session_duration) as avg_duration
FROM playback_events
WHERE dt >= '2024-01-01'
GROUP BY dt
ORDER BY dt

-- Optimized with date partitioning and clustering
```

## Trade-offs Discussion

### Partition Size vs. File Count

* **Small partitions**: Better parallelism, more files → higher metadata overhead
* **Large partitions**: Fewer files, better compression → slower queries
* **Optimal**: 128-512 MB files, balance between metadata cost and query performance

### Normalization vs. Denormalization

* **Normalized**: Consistent updates, smaller storage → complex joins
* **Denormalized**: Fast queries, larger storage → update complexity
* **Hybrid**: Normalized dimensions, denormalized facts

### Consistency vs. Availability

* **Strong consistency**: Guaranteed accuracy → higher latency
* **Eventual consistency**: Better performance → potential staleness
* **Context-dependent**: User-facing features need strong consistency

## Streaming Platform Context

* **User scale**: 200M+ profiles requiring massive parallel processing
* **Content velocity**: New releases generate immediate hot keys
* **Global distribution**: Users across 190+ countries with regional preferences
* **Device diversity**: Multiple device types with different usage patterns
* **Real-time requirements**: Resume functionality needs immediate consistency

## Monitoring & Maintenance

### Operational Metrics

* **Partition balance**: Data distribution across partitions
* **Hot spot detection**: Identify and mitigate overloaded partitions
* **Query performance**: Monitor slow queries and optimize access patterns
* **Storage utilization**: Track growth and plan capacity

### Maintenance Operations

* **Rebalancing**: Redistribute data during off-peak hours
* **Compaction**: Merge small files to optimize storage
* **Retention**: Implement data lifecycle policies
* **Backup**: Ensure disaster recovery capabilities

## Migration Strategies

### Zero-Downtime Migration

1. **Dual-write**: Write to both old and new partitioning schemes
2. **Gradual traffic shift**: Move users incrementally to new system
3. **Backfill**: Populate new partitions with historical data
4. **Validation**: Ensure data consistency before full cutover

### Schema Evolution

* **Backward compatibility**: Support old queries during transition
* **Forward compatibility**: New system handles old data formats
* **Gradual rollout**: Test with small user segments first

## Follow-up Considerations

* How would you choose partitioning keys for user watch history at scale?
* What are the trade-offs between different sharding strategies?
* How do you handle hot keys and data skew in a distributed system?

---

Navigate back to [Scalability Patterns](./) | [Data Modeling Index](../README.md)
