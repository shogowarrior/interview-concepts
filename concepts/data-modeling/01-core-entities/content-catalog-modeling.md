# Content Catalog Modeling

## Overview
Design a data model to represent Netflix's content library where each title can be a movie or a show with multiple seasons and episodes.

## Schema Design

### Core Tables

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
```

### Localization Support

```sql
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

## Lakehouse Implementation

- **Storage**: Delta/Iceberg format with Parquet
- **Partitioning**: Sparse partitioning (not usually necessary for titles)
- **Clustering**: `title_id` for episodes table for efficient season lookups
- **Optimization**: Z-Order on frequently queried columns

## Common Queries

```sql
-- Get all episodes of S2 for a show
SELECT e.*, l.localized_title
FROM episode e
LEFT JOIN localized_metadata l
  ON e.episode_id = l.object_id
  AND l.object_type = 'EPISODE'
  AND l.locale = 'en-US'
WHERE e.title_id = ?
  AND e.season_number = 2
ORDER BY e.episode_number;

-- Find all action movies
SELECT t.*, l.localized_title
FROM title t
JOIN title_genre tg ON t.title_id = tg.title_id
JOIN genre g ON tg.genre_id = g.genre_id
LEFT JOIN localized_metadata l
  ON t.title_id = l.object_id
  AND l.object_type = 'TITLE'
  AND l.locale = ?
WHERE g.name = 'Action'
  AND t.type = 'MOVIE';
```

## Design Considerations

- **Unified Content Model**: Single `title` table handles both movies and shows
- **Flexible Localization**: Separate table supports multiple languages efficiently
- **Genre Relationships**: Many-to-many relationship for flexible categorization
- **Scalability**: Partitioning and clustering optimized for common access patterns

## Follow-up Questions

- How would you handle localized metadata for multiple languages?
- How would you model multiple genres per title?
- How would you optimize for "continue watching" functionality?