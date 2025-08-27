# Experimentation and A/B Testing

This section covers experimentation platforms, A/B testing frameworks, and statistical methodologies for measuring the impact of product changes at large-scale streaming platforms.

## 🧪 A/B Testing Framework

### Core Components

**Experiment Design:**
```sql
-- Experiment metadata table
CREATE TABLE experiments (
  exp_id STRING PRIMARY KEY,
  name STRING,
  hypothesis STRING,
  owner_team STRING,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status STRING,  -- DRAFT, RUNNING, COMPLETED, CANCELLED
  unit_type STRING,  -- PROFILE, ACCOUNT, DEVICE
  primary_kpi STRING,  -- watch_hours, retention_rate, etc.
  secondary_kpis ARRAY<STRING>,
  target_population STRING,  -- ALL, NEW_USERS, PREMIUM, etc.
  randomization_method STRING,  -- SIMPLE, STRATIFIED, CUPED
  created_at TIMESTAMP
);

-- Variant definitions
CREATE TABLE experiment_variants (
  exp_id STRING REFERENCES experiments(exp_id),
  variant_id STRING,  -- control, treatment_a, treatment_b
  variant_name STRING,
  traffic_percentage DOUBLE,
  description STRING,
  PRIMARY KEY (exp_id, variant_id)
);
```

### User Assignment and Randomization

**Consistent Hashing for User Assignment:**
```python
def assign_variant(user_id: str, experiment_id: str, traffic_pct: float) -> str:
    """
    Deterministic user assignment using consistent hashing.
    Ensures same user always gets same variant for same experiment.
    """
    hash_input = f"{experiment_id}:{user_id}"
    hash_value = hash_function(hash_input)
    normalized_hash = hash_value / max_hash_value

    if normalized_hash < traffic_pct / 100:
        return "treatment"
    else:
        return "control"
```

### Stratified Randomization

**By User Segments:**
```sql
-- Stratified assignment by subscription tier
WITH user_segments AS (
  SELECT
    profile_id,
    CASE
      WHEN subscription_tier = 'BASIC' THEN 'segment_a'
      WHEN subscription_tier = 'STANDARD' THEN 'segment_b'
      WHEN subscription_tier = 'PREMIUM' THEN 'segment_c'
    END as segment
  FROM user_profiles
),
segmented_assignment AS (
  SELECT
    profile_id,
    segment,
    -- Each segment gets independent randomization
    CASE
      WHEN hash_function(profile_id, exp_id) % 100 < 50 THEN 'treatment'
      ELSE 'control'
    END as variant
  FROM user_segments
)
SELECT * FROM segmented_assignment;
```

## 📊 Statistical Analysis

### Power Analysis and Sample Size

**Sample Size Calculation:**
```python
def calculate_sample_size(baseline_rate: float, mde: float,
                         power: float = 0.8, alpha: float = 0.05) -> int:
    """
    Calculate required sample size for A/B test.

    Args:
        baseline_rate: Current conversion rate (e.g., 0.05 for 5%)
        mde: Minimum detectable effect (e.g., 0.01 for 1% absolute increase)
        power: Statistical power (1 - beta)
        alpha: Significance level

    Returns:
        Required sample size per variant
    """
    import statsmodels.stats.power as power

    effect_size = mde / (baseline_rate * (1 - baseline_rate))**0.5
    sample_size = power.tt_ind_solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        nobs1=None,
        ratio=1
    )

    return int(sample_size)
```

### Guardrail Metrics and Early Stopping

**Automated Experiment Monitoring:**
```sql
-- Daily guardrail checks
CREATE TABLE experiment_guardrails (
  exp_id STRING,
  metric_date DATE,
  metric_name STRING,
  control_value DOUBLE,
  treatment_value DOUBLE,
  relative_change DOUBLE,
  statistical_significance DOUBLE,
  PRIMARY KEY (exp_id, metric_date, metric_name)
);

-- Alert on significant degradation
SELECT
  exp_id,
  metric_name,
  relative_change,
  statistical_significance
FROM experiment_guardrails
WHERE metric_date = CURRENT_DATE - INTERVAL '1' DAY
  AND ABS(relative_change) > 0.05  -- 5% change threshold
  AND statistical_significance < 0.01;  -- p-value threshold
```

## 📈 Advanced Statistical Methods

### CUPED (Controlled-experiment Using Pre-experiment Data)

**Variance Reduction:**
```sql
-- CUPED implementation for more sensitive A/B tests
WITH pre_experiment_data AS (
  SELECT
    profile_id,
    AVG(daily_watch_hours) as pre_avg_watch_hours
  FROM watch_history
  WHERE watch_date BETWEEN exp_start_date - INTERVAL '30' DAY
                       AND exp_start_date - INTERVAL '1' DAY
  GROUP BY profile_id
),
experiment_results AS (
  SELECT
    profile_id,
    variant,
    AVG(daily_watch_hours) as post_avg_watch_hours
  FROM watch_history w
  JOIN experiment_assignments e ON w.profile_id = e.profile_id
  WHERE watch_date BETWEEN exp_start_date AND exp_end_date
  GROUP BY profile_id, variant
),
cuped_adjusted AS (
  SELECT
    e.variant,
    e.post_avg_watch_hours - 0.5 * (p.pre_avg_watch_hours - overall_pre_avg) as adjusted_metric
  FROM experiment_results e
  JOIN pre_experiment_data p ON e.profile_id = p.profile_id
  CROSS JOIN (SELECT AVG(pre_avg_watch_hours) as overall_pre_avg
              FROM pre_experiment_data) overall
)
SELECT
  variant,
  AVG(adjusted_metric) as mean_adjusted_watch_hours,
  STDDEV(adjusted_metric) as std_adjusted_watch_hours,
  COUNT(*) as sample_size
FROM cuped_adjusted
GROUP BY variant;
```

### Sequential Testing

**P-value Monitoring Over Time:**
```python
def sequential_test(control_data: List[float], treatment_data: List[float],
                   alpha: float = 0.05) -> str:
    """
    Sequential testing for early stopping decisions.

    Returns:
        'continue', 'stop_early_positive', 'stop_early_negative'
    """
    # Use cumulative data for sequential analysis
    cumulative_control = np.cumsum(control_data)
    cumulative_treatment = np.cumsum(treatment_data)

    # Calculate cumulative statistics
    n_control = len(control_data)
    n_treatment = len(treatment_data)

    if n_control == 0 or n_treatment == 0:
        return 'continue'

    # Sequential probability ratio test
    likelihood_ratio = calculate_likelihood_ratio(cumulative_control, cumulative_treatment)

    # Decision boundaries
    upper_bound = math.log(1/alpha)
    lower_bound = math.log(alpha)

    if likelihood_ratio > upper_bound:
        return 'stop_early_positive'
    elif likelihood_ratio < lower_bound:
        return 'stop_early_negative'
    else:
        return 'continue'
```

## 🎯 Experimentation Platform Architecture

### Event Tracking and Collection

**Client-Side Event Tracking:**
```javascript
// Modern event tracking implementation
class ExperimentTracker {
  static trackExperimentEvent(experimentId, variant, eventName, metadata) {
    const event = {
      experiment_id: experimentId,
      variant_id: variant,
      event_name: eventName,
      user_id: this.getUserId(),
      session_id: this.getSessionId(),
      timestamp: Date.now(),
      metadata: metadata,
      platform: 'web', // or mobile, tv, etc.
      user_agent: navigator.userAgent
    };

    // Send to data collection service
    this.sendEvent(event);
  }
}
```

### Real-Time Experiment Results

**Streaming Analytics:**
```sql
-- Real-time experiment metrics with Kafka streams
CREATE STREAM experiment_events (
  exp_id STRING,
  profile_id BIGINT,
  variant STRING,
  event_name STRING,
  event_value DOUBLE,
  event_timestamp TIMESTAMP
) WITH (
  KAFKA_TOPIC = 'experiment_events',
  KEY_FORMAT = 'JSON',
  VALUE_FORMAT = 'JSON'
);

-- Streaming aggregation for real-time dashboard
CREATE TABLE experiment_metrics AS
SELECT
  exp_id,
  variant,
  event_name,
  COUNT(*) as event_count,
  AVG(event_value) as avg_value,
  TUMBLE_START(event_timestamp, INTERVAL '5' MINUTE) as window_start
FROM experiment_events
GROUP BY exp_id, variant, event_name, TUMBLE(event_timestamp, INTERVAL '5' MINUTE);
```

## 🚫 Common Pitfalls and Solutions

### Selection Bias
**Problem:** Non-random assignment leads to biased results.

**Solutions:**
- Use proper randomization methods
- Stratify by key user characteristics
- Monitor for sample ratio mismatch (SRM)

### Multiple Testing Problem
**Problem:** Running many statistical tests increases false positive rate.

**Solutions:**
- Bonferroni correction for multiple comparisons
- False Discovery Rate (FDR) control
- Pre-register hypothesis and analysis plan

### Simpson's Paradox
**Problem:** Aggregate results differ from subgroup results.

**Solutions:**
- Always analyze by key segments
- Include interaction terms in statistical models
- Use stratified analysis

## 📊 Platform-Specific Experimentation Challenges

### Global Experimentation
- **Content Localization**: Different content libraries per region
- **Device Diversity**: Experiments across web, mobile, smart TVs
- **Time Zones**: Coordinated experiment timing globally

### Content Discovery Experiments
- **Algorithm Changes**: Testing new recommendation algorithms
- **UI Changes**: Homepage layout and personalization
- **Content Promotion**: Featured content and editorial curation

### Performance Impact Experiments
- **Loading Speed**: Impact on engagement metrics
- **Streaming Quality**: Adaptive bitrate algorithms
- **Caching Strategies**: Content delivery optimization

## 🛠️ Experimentation Best Practices

### Experiment Design Checklist
- [ ] Clear hypothesis statement
- [ ] Defined primary and secondary metrics
- [ ] Power analysis for sample size
- [ ] Proper randomization method
- [ ] Guardrail metrics defined
- [ ] Analysis plan documented

### During Experiment
- [ ] Monitor for data quality issues
- [ ] Check for unexpected side effects
- [ ] Communicate with stakeholders
- [ ] Prepare contingency plans

### After Experiment
- [ ] Comprehensive statistical analysis
- [ ] Segment analysis for insights
- [ ] Document learnings and decisions
- [ ] Plan follow-up experiments

## 📚 Key Takeaways

- **Statistical Rigor**: Always use proper statistical methods and power analysis
- **Monitoring**: Continuous monitoring prevents bad experiments from running too long
- **Segmentation**: Analyze results by key user segments for deeper insights
- **Platform Integration**: Seamless integration with product development workflow
- **Ethical Considerations**: Consider user experience and potential harm

---

**🔗 Cross-References:**
- [System Architecture](system-architecture.md) - Platform architecture for experimentation
- [Performance Optimization](performance-optimization.md) - Measuring performance impact
- [Data Modeling Patterns](../data-modeling/) - Event tracking schemas

Navigate back to [System Design & Advanced Concepts](README.md)