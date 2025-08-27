# User Viewing History Modeling

## Overview

Model how you would store user viewing history including partially watched episodes, multiple devices, and resume functionality.

## Schema Design

### Core Tables

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

## Lakehouse Implementation

- **Storage**: Delta/Iceberg with time-based partitioning
- **Partitioning**: `playback_event` by `dt=date(event_time)` and `country_code`
- **Clustering**: `playback_event` by `session_id` for efficient session reconstruction
- **Optimization**: `resume_state` is small and kept unpartitioned for fast reads

## Key Design Patterns

### 1. Session-Based Tracking

- Each playback session gets a unique ID
- Events are tied to sessions, not individual users
- Enables multi-device resume functionality

### 2. Event Sourcing Pattern

- Store all playback events in chronological order
- Reconstruct viewing history from events
- Support debugging and analytics

### 3. Denormalized Resume State

- Pre-computed latest position per profile/content
- Updated by streaming jobs processing events
- Fast lookup for "Continue Watching" feature

## Common Queries

```sql
-- Get continue watching list
SELECT
  rs.*,
  t.title,
  e.episode_number
FROM resume_state rs
LEFT JOIN title t ON rs.title_id = t.title_id
LEFT JOIN episode e ON rs.episode_id = e.episode_id
WHERE rs.profile_id = ?
ORDER BY rs.last_update DESC
LIMIT 10;

-- Reconstruct viewing session timeline
SELECT
  pe.*,
  ps.title_id,
  ps.episode_id
FROM playback_session ps
JOIN playback_event pe ON ps.session_id = pe.session_id
WHERE ps.profile_id = ?
  AND ps.started_at >= CURRENT_DATE - INTERVAL '7' DAY
ORDER BY pe.event_time;

-- Calculate total watch time per title
SELECT
  ps.title_id,
  SUM(
    CASE
      WHEN pe.event_type = 'END' THEN pe.position_sec
      ELSE 0
    END
  ) AS total_watch_seconds
FROM playback_session ps
JOIN playback_event pe ON ps.session_id = pe.session_id
WHERE ps.profile_id = ?
  AND pe.event_type = 'END'
GROUP BY ps.title_id;
```

## Data Quality & Processing

```sql
-- Deduplication check
SELECT session_id, event_time, COUNT(*) AS dup_count
FROM playback_event
GROUP BY session_id, event_time
HAVING COUNT(*) > 1;

-- Session completeness check
SELECT
  ps.session_id,
  ps.started_at,
  ps.ended_at,
  COUNT(pe.event_time) AS event_count
FROM playback_session ps
LEFT JOIN playback_event pe ON ps.session_id = pe.session_id
WHERE ps.ended_at IS NULL
  AND ps.started_at < CURRENT_TIMESTAMP - INTERVAL '1' HOUR
GROUP BY ps.session_id, ps.started_at, ps.ended_at;
```

## Design Considerations

- **Event-Driven Architecture**: Store events, derive state
- **Multi-Device Support**: Sessions per device, unified resume state
- **Partial Watching**: Precise position tracking for resume
- **Scale**: Partition by time for efficient querying
- **Real-time Processing**: Streaming jobs for resume state updates

## Follow-up Questions

- How would you handle multiple concurrent sessions per profile?
- How would you design for efficient "continue watching" queries?
- How would you handle session cleanup for abandoned sessions?
- How would you implement cross-device resume synchronization?
