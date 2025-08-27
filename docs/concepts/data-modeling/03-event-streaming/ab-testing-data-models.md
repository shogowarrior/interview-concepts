# A/B Testing Data Models

## Overview

Designing data models to track experiment groups, user assignments, and outcomes for recommendation algorithm experiments and other A/B tests.

## Core Concepts

* Experiment metadata with variants and targeting rules
* User assignment tracking with consistency guarantees
* Outcome measurement and statistical analysis support
* Guardrails and monitoring for experiment integrity

## Core Schema

```sql
CREATE TABLE experiment (
  exp_id STRING PRIMARY KEY,
  name STRING,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  unit STRING,                    -- PROFILE or ACCOUNT
  primary_kpi STRING              -- e.g., '7d hours watched'
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

## Experiment Types

### Algorithm Experiments

* **Recommendation algorithms**: Collaborative filtering vs. content-based
* **Ranking models**: Different ranking functions for content lists
* **Personalization**: User profile vs. demographic targeting

### Product Experiments

* **UI changes**: Homepage layout, navigation, search interface
* **Content presentation**: Artwork, descriptions, metadata display
* **User experience**: Onboarding flows, tutorial effectiveness

### Technical Experiments

* **Performance**: Loading speeds, caching strategies, CDN optimization
* **Quality**: Bitrate algorithms, adaptive streaming, error handling
* **Infrastructure**: Region routing, device optimization

## Assignment Strategies

### Consistent Hashing

* Ensures users see the same variant across sessions
* Prevents assignment changes due to cache misses or device switches
* Critical for recommendation algorithm experiments

### Traffic Allocation

* Gradual rollout: 1% → 5% → 10% → 50% → 100%
* Regional targeting: Roll out to specific countries first
* Device targeting: Test on specific device types

## Lakehouse Layout

* `experiment` and `variant`: Small dimension tables, unpartitioned
* `assignment`: Partitioned by `exp_id` and clustered by `unit_id` for efficient lookups
* `kpi_outcome`: Partitioned by `metric_date` and `exp_id` for time-series analysis
* Use Delta Lake for ACID transactions and time travel

## Query Examples

* **Experiment results**: `SELECT variant_id, AVG(kpi_value) FROM kpi_outcome WHERE exp_id = 'rec_algo_v3' GROUP BY variant_id`
* **Assignment verification**: `SELECT COUNT(DISTINCT unit_id) FROM assignment WHERE exp_id = 'homepage_redesign'`
* **Cross-experiment analysis**: `SELECT exp_id, COUNT(*) FROM assignment GROUP BY exp_id`

## Statistical Analysis

### Guardrails

* **Sample ratio mismatch**: Ensure assignment ratios match traffic percentages
* **Pre-period bias**: Compare pre-experiment behavior between variants
* **CUPED (Controlled-experiment Using Pre-Experiment Data)**: Reduce variance using pre-experiment metrics

### Power Analysis

* **Minimum detectable effect**: Calculate required sample size for statistical significance
* **Duration planning**: Time needed to reach statistical significance
* **Multiple testing correction**: Bonferroni adjustment for multiple KPIs

## Trade-offs Discussion

### Unit Selection

* **Profile-level**: Better for personalization experiments, avoids household contamination
* **Account-level**: Easier for billing/pricing experiments, avoids profile gaming
* **Device-level**: Best for technical/performance experiments

### Assignment Consistency

* **Strict consistency**: Users always see same variant (better for recommendations)
* **Session consistency**: Assignment can change between sessions (simpler implementation)
* **Hybrid**: Consistent within experiment but can change between experiments

## Streaming Platform Context

* **Scale challenges**: 200M+ users require careful experiment design
* **Global experiments**: Different content libraries and user behaviors by region
* **Algorithm complexity**: Recommendation experiments affect long-term user engagement
* **Ethical considerations**: Avoid unfair treatment, ensure user welfare
* **Continuous experimentation**: Thousands of experiments running simultaneously

## Monitoring and Alerting

### Experiment Health

* **Assignment rate**: Percentage of users successfully assigned
* **Variant distribution**: Actual vs. expected traffic allocation
* **Data quality**: Missing or corrupted experiment data

### Business Impact

* **Primary KPIs**: Revenue, engagement, retention metrics
* **Secondary KPIs**: User satisfaction, content discovery
* **Guardrail metrics**: Error rates, performance impact

## Follow-up Considerations

* How would you design experiments for global recommendation systems?
* What are the trade-offs between different experiment assignment strategies?
* How do you ensure statistical rigor in A/B testing at scale?

---

Navigate back to [Event Streaming](./) | [Data Modeling Index](../README.md)
