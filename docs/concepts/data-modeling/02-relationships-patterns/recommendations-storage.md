# Recommendations Storage Modeling

## Overview

Design a data model to store relationships for "Because you watched X..." recommendations, including interactions, similarity graphs, and personalized recommendation lists.

## Schema Design

### 1. Interactions & Training Data

```sql
CREATE TABLE user_content_interaction (
  profile_id BIGINT,
  title_id BIGINT,
  interaction_type STRING,           -- VIEW, LIKE, DISLIKE, RATING, SHARE
  interaction_value DOUBLE,          -- 1.0 for view, 5.0 for rating
  event_ts TIMESTAMP,
  session_id STRING,
  PRIMARY KEY (profile_id, title_id, event_ts)
);

CREATE TABLE user_content_rating (
  profile_id BIGINT,
  title_id BIGINT,
  rating_value INT,                 -- 1-5 stars
  rated_at TIMESTAMP,
  PRIMARY KEY (profile_id, title_id)
);

CREATE TABLE viewing_session (
  session_id STRING PRIMARY KEY,
  profile_id BIGINT,
  title_id BIGINT,
  watch_duration_sec INT,
  completion_rate DOUBLE,           -- 0.0 to 1.0
  started_at TIMESTAMP,
  ended_at TIMESTAMP
);
```

### 2. Similarity Graph & Models

```sql
CREATE TABLE item_item_edge (
  src_title_id BIGINT,
  dst_title_id BIGINT,
  score DOUBLE,                      -- similarity score
  model VARCHAR,                     -- 'itemCF', 'graphSage', 'contentBased'
  model_version STRING,
  computed_at TIMESTAMP,
  PRIMARY KEY (src_title_id, dst_title_id, model, model_version)
);

CREATE TABLE user_user_edge (
  src_profile_id BIGINT,
  dst_profile_id BIGINT,
  similarity_score DOUBLE,
  computed_at TIMESTAMP,
  PRIMARY KEY (src_profile_id, dst_profile_id)
);

CREATE TABLE content_embedding (
  title_id BIGINT PRIMARY KEY,
  embedding VECTOR(256),             -- vector representation
  model_version STRING,
  updated_at TIMESTAMP
);
```

### 3. Personalized Recommendations

```sql
CREATE TABLE recommendation_list (
  profile_id BIGINT,
  context STRING,                   -- 'home', 'because_you_watched', 'genre_drama'
  rank_position INT,
  title_id BIGINT,
  score DOUBLE,                     -- recommendation confidence
  model STRING,
  model_version STRING,
  generated_at TIMESTAMP,
  expires_at TIMESTAMP,
  PRIMARY KEY (profile_id, context, rank_position, generated_at)
);

CREATE TABLE recommendation_explanation (
  profile_id BIGINT,
  title_id BIGINT,
  explanation_type STRING,          -- 'similar_to', 'because_you_watched', 'popular'
  explanation_text STRING,
  related_title_id BIGINT NULL,
  generated_at TIMESTAMP,
  PRIMARY KEY (profile_id, title_id, generated_at)
);
```

## Serving Layer Optimization

```sql
-- Materialized view for fast serving
CREATE TABLE current_recommendations AS
SELECT *
FROM recommendation_list
WHERE generated_at >= (
  SELECT MAX(generated_at)
  FROM recommendation_list
  WHERE profile_id = recommendation_list.profile_id
    AND context = recommendation_list.context
);

-- Cache for frequently accessed recommendations
CREATE TABLE recommendation_cache (
  profile_id BIGINT,
  context STRING,
  recommendations JSON,             -- serialized list
  last_accessed TIMESTAMP,
  ttl_minutes INT,
  PRIMARY KEY (profile_id, context)
);
```

## Common Queries

```sql
-- Get personalized recommendations for homepage
SELECT
  rl.*,
  t.title,
  re.explanation_text
FROM current_recommendations rl
JOIN title t ON rl.title_id = t.title_id
LEFT JOIN recommendation_explanation re
  ON rl.profile_id = re.profile_id
  AND rl.title_id = re.title_id
WHERE rl.profile_id = ?
  AND rl.context = 'home'
ORDER BY rl.rank_position;

-- Find similar content (for "More Like This")
SELECT
  iie.*,
  t.title AS similar_title
FROM item_item_edge iie
JOIN title t ON iie.dst_title_id = t.title_id
WHERE iie.src_title_id = ?
  AND iie.model = 'contentBased'
ORDER BY iie.score DESC
LIMIT 10;

-- A/B test different recommendation models
SELECT
  model,
  model_version,
  COUNT(*) AS impressions,
  AVG(CASE WHEN interaction_type = 'VIEW' THEN 1 ELSE 0 END) AS ctr
FROM recommendation_list rl
LEFT JOIN user_content_interaction uci
  ON rl.profile_id = uci.profile_id
  AND rl.title_id = uci.title_id
  AND uci.event_ts BETWEEN rl.generated_at AND rl.expires_at
WHERE rl.generated_at >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY model, model_version;
```

## Model Training & Updates

```sql
-- Aggregate training data for model updates
CREATE TABLE training_interactions AS
SELECT
  profile_id,
  title_id,
  AVG(interaction_value) AS avg_interaction,
  COUNT(*) AS interaction_count,
  MAX(event_ts) AS last_interaction
FROM user_content_interaction
WHERE event_ts >= CURRENT_DATE - INTERVAL '90' DAY
GROUP BY profile_id, title_id;

-- Track model performance
CREATE TABLE model_performance (
  model_name STRING,
  model_version STRING,
  evaluation_date DATE,
  metric_name STRING,               -- 'precision@10', 'recall@20'
  metric_value DOUBLE,
  PRIMARY KEY (model_name, model_version, evaluation_date, metric_name)
);
```

## Design Considerations

- **Multi-Model Support**: Store edges from different algorithms
- **Version Control**: Track model versions for A/B testing and rollback
- **Real-time Updates**: Incremental updates for new user behavior
- **Explainability**: Store reasoning for user trust and debugging
- **Performance**: Pre-compute recommendations, use caching for serving

## Follow-up Questions

- How would you handle cold-start problem for new users/content?
- How would you design A/B testing framework for recommendation models?
- How would you ensure recommendation diversity and avoid filter bubbles?
- How would you handle real-time feedback and model updates?
