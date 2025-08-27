# Many-to-Many Relationships

## Overview

Common patterns for handling many-to-many relationships in a streaming platform's data architecture, including junction tables, bridge tables, and relationship modeling strategies.

## Core Patterns

### 1. Simple Junction Table

**Use Case**: Title-Genre relationships (one title can have multiple genres, one genre can apply to multiple titles)

```sql
CREATE TABLE title_genre (
  title_id BIGINT REFERENCES title(title_id),
  genre_id INT REFERENCES genre(genre_id),
  assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (title_id, genre_id)
);
```

### 2. Bridge Table with Attributes

**Use Case**: Profile-Device relationships with usage context

```sql
CREATE TABLE profile_device (
  profile_id BIGINT REFERENCES profile(profile_id),
  device_id STRING REFERENCES device(device_id),
  first_used_at TIMESTAMP,
  last_used_at TIMESTAMP,
  usage_count INT DEFAULT 0,
  PRIMARY KEY (profile_id, device_id)
);
```

### 3. Temporal Many-to-Many

**Use Case**: Subscription-Plan changes over time

```sql
CREATE TABLE account_plan_history (
  account_id BIGINT,
  plan_id STRING,
  start_date DATE,
  end_date DATE NULL,
  monthly_price_cents INT,
  PRIMARY KEY (account_id, start_date)
);
```

## Advanced Patterns

### 4. Self-Referencing Many-to-Many

**Use Case**: Title-Title relationships (sequels, franchises, recommendations)

```sql
CREATE TABLE title_relationship (
  src_title_id BIGINT REFERENCES title(title_id),
  dst_title_id BIGINT REFERENCES title(title_id),
  relationship_type STRING,  -- 'sequel', 'prequel', 'spin_off', 'similar'
  strength_score DOUBLE,
  created_at TIMESTAMP,
  PRIMARY KEY (src_title_id, dst_title_id, relationship_type)
);
```

### 5. Hierarchical Many-to-Many

**Use Case**: Content categorization with multiple taxonomies

```sql
CREATE TABLE title_category (
  title_id BIGINT,
  category_id INT,
  taxonomy_type STRING,      -- 'genre', 'mood', 'theme', 'demographic'
  weight DOUBLE,             -- importance score
  PRIMARY KEY (title_id, category_id, taxonomy_type)
);
```

## Query Patterns

### Efficient Many-to-Many Queries

```sql
-- Get all genres for multiple titles
SELECT t.title_id, g.name
FROM title t
JOIN title_genre tg ON t.title_id = tg.title_id
JOIN genre g ON tg.genre_id = g.genre_id
WHERE t.title_id IN (?)

-- Find titles with specific genre combinations
SELECT t.title_id, t.title_name
FROM title t
JOIN title_genre tg ON t.title_id = tg.title_id
WHERE tg.genre_id IN (1, 2, 3)  -- Action, Drama, Comedy
GROUP BY t.title_id, t.title_name
HAVING COUNT(DISTINCT tg.genre_id) = 3  -- Must have all three genres
```

## Lakehouse Optimization

* **Clustering**: For frequent access patterns, cluster junction tables by the most queried dimension
* **Partitioning**: Consider partitioning large junction tables by time dimensions when applicable
* **Materialized Views**: Pre-aggregate many-to-many relationships for common query patterns

## Trade-offs Discussion

### Normalization vs. Denormalization
* **Normalized**: Pure junction tables minimize redundancy but require joins
* **Denormalized**: Array/JSON fields reduce joins but complicate updates and analytics
* **Hybrid**: Balance based on query patterns and update frequency

### Storage Considerations
* **Small relationships**: Keep normalized (genres, categories)
* **Large relationships**: Consider denormalization (user preferences, viewing history)
* **Temporal relationships**: Always keep historical records for audit and analytics

## Streaming Platform Context

* **Content tagging**: Multiple taxonomies (genre, mood, themes, demographics)
* **Personalization**: User preferences across multiple dimensions
* **Global localization**: Content availability varies by region and device type
* **A/B testing**: Different recommendation algorithms create different relationship graphs

## Performance Patterns

### Indexing Strategies
```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_title_genre_genre ON title_genre(genre_id, title_id);
CREATE INDEX idx_profile_device_last_used ON profile_device(last_used_at, profile_id);
```

### Aggregation Tables
```sql
-- Pre-computed genre statistics
CREATE TABLE genre_stats (
  genre_id INT PRIMARY KEY,
  title_count INT,
  total_views BIGINT,
  last_updated TIMESTAMP
);
```

## Follow-up Considerations

* How do you handle referential integrity in distributed systems?
* What are the trade-offs between different many-to-many modeling approaches?
* How do you optimize for both OLTP updates and OLAP analytics?

---

Navigate back to [Relationships & Patterns](./) | [Data Modeling Index](../README.md)