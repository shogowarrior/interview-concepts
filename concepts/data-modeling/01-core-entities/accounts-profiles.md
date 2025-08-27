# Accounts & Profiles Modeling

## Overview
Design a schema to model Netflix accounts, profiles, and devices where one account can have multiple profiles, and each profile can be accessed on multiple devices.

## Schema Design

### Core Tables

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
  is_kids BOOLEAN DEFAULT FALSE,
  maturity_setting STRING,
  language_pref STRING,
  created_at TIMESTAMP
);

CREATE TABLE device (
  device_id STRING PRIMARY KEY,
  account_id BIGINT REFERENCES account(account_id),
  device_type STRING,                 -- TV, mobile, web
  device_name STRING,
  registered_at TIMESTAMP
);

CREATE TABLE profile_device_link (
  profile_id BIGINT REFERENCES profile(profile_id),
  device_id STRING REFERENCES device(device_id),
  linked_at TIMESTAMP,
  PRIMARY KEY (profile_id, device_id)
);
```

### Extended Schema for Advanced Features

```sql
-- Device sessions for concurrent stream limits
CREATE TABLE device_session (
  session_id STRING PRIMARY KEY,
  device_id STRING REFERENCES device(device_id),
  profile_id BIGINT REFERENCES profile(profile_id),
  started_at TIMESTAMP,
  ended_at TIMESTAMP NULL,
  ip_address STRING
);

-- Profile preferences and viewing history summary
CREATE TABLE profile_preferences (
  profile_id BIGINT PRIMARY KEY REFERENCES profile(profile_id),
  favorite_genres ARRAY<STRING>,
  preferred_languages ARRAY<STRING>,
  autoplay_enabled BOOLEAN DEFAULT TRUE,
  last_updated TIMESTAMP
);
```

## Business Rules Implementation

```sql
-- Enforce device limits (simplified example)
CREATE VIEW active_device_count AS
SELECT
  account_id,
  COUNT(DISTINCT device_id) AS active_devices
FROM device_session
WHERE ended_at IS NULL
GROUP BY account_id;

-- Kids profile restrictions
CREATE VIEW kids_content_access AS
SELECT
  p.profile_id,
  CASE
    WHEN p.is_kids THEN 'Y'
    ELSE 'N'
  END AS can_access_mature_content
FROM profile p;
```

## Lakehouse Optimization

- **Partitioning**: `account` by `home_country`, `profile` by `account_id`
- **Clustering**: `profile` by `account_id` for efficient account-level queries
- **Z-Ordering**: `device_session` by `(profile_id, started_at)` for time-series analysis

## Common Queries

```sql
-- Get all profiles for an account
SELECT p.*, pd.device_count
FROM profile p
LEFT JOIN (
  SELECT profile_id, COUNT(*) AS device_count
  FROM profile_device_link
  GROUP BY profile_id
) pd ON p.profile_id = pd.profile_id
WHERE p.account_id = ?;

-- Find active sessions per account (for concurrent stream limits)
SELECT
  a.account_id,
  COUNT(ds.session_id) AS active_sessions
FROM account a
LEFT JOIN profile p ON a.account_id = p.account_id
LEFT JOIN device_session ds ON p.profile_id = ds.profile_id
  AND ds.ended_at IS NULL
GROUP BY a.account_id;

-- Device management for account
SELECT
  d.*,
  COUNT(pdl.profile_id) AS linked_profiles
FROM device d
LEFT JOIN profile_device_link pdl ON d.device_id = pdl.device_id
WHERE d.account_id = ?
GROUP BY d.device_id, d.device_type, d.device_name, d.registered_at;
```

## Design Considerations

- **Account-Profile Relationship**: One-to-many with clear ownership
- **Device Management**: Many-to-many between profiles and devices
- **Session Tracking**: Critical for enforcing business rules like concurrent stream limits
- **Kids Content**: Metadata-driven restrictions for compliance
- **Scalability**: Optimized for account-level operations and device management

## Follow-up Questions

- How would you handle multiple concurrent profiles per account?
- How would you design for efficient "continue watching" queries?
- How would you enforce device limits and concurrent streaming restrictions?