# Subscriptions & Billing Modeling

## Overview
Design a data model to store subscription plans, billing cycles, promotions, and payment history with support for mid-cycle plan changes.

## Schema Design

### Core Tables

```sql
CREATE TABLE plan (
  plan_id STRING PRIMARY KEY,        -- 'STANDARD_ADS', 'PREMIUM'
  name STRING,
  price_cents INT,
  currency STRING,
  max_screens INT,
  hdr BOOLEAN,
  ads_supported BOOLEAN,
  is_active BOOLEAN DEFAULT TRUE
);

-- Effective-dated subscription records (SCD-2 style)
CREATE TABLE subscription (
  subscription_id BIGINT PRIMARY KEY,
  account_id BIGINT,
  plan_id STRING REFERENCES plan(plan_id),
  status STRING,                     -- ACTIVE, PAUSED, CANCELED
  start_date DATE,
  end_date DATE NULL                 -- null = current
);

CREATE TABLE promotion (
  promo_code STRING PRIMARY KEY,
  discount_type STRING,              -- PCT or FIXED
  discount_value DOUBLE,
  start_date DATE,
  end_date DATE
);
```

### Billing and Payment Tables

```sql
CREATE TABLE subscription_event (
  event_id BIGINT PRIMARY KEY,
  subscription_id BIGINT REFERENCES subscription(subscription_id),
  event_time TIMESTAMP,
  event_type STRING,                 -- UPGRADE, DOWNGRADE, CANCEL, RESUME, RENEW
  old_plan_id STRING,
  new_plan_id STRING,
  note STRING
);

CREATE TABLE invoice (
  invoice_id BIGINT PRIMARY KEY,
  account_id BIGINT,
  period_start DATE,
  period_end DATE,
  amount_due_cents INT,
  currency STRING,
  promo_code STRING NULL REFERENCES promotion(promo_code),
  created_at TIMESTAMP,
  status STRING                      -- OPEN, PAID, VOID
);

CREATE TABLE payment (
  payment_id BIGINT PRIMARY KEY,
  invoice_id BIGINT REFERENCES invoice(invoice_id),
  amount_cents INT,
  currency STRING,
  method STRING,                     -- card, paypal, gift
  status STRING,                     -- AUTH, CAPTURED, REFUNDED, FAILED
  created_at TIMESTAMP
);
```

## Business Logic Implementation

```sql
-- Handle mid-cycle plan changes
CREATE PROCEDURE process_plan_change(
  p_subscription_id BIGINT,
  p_new_plan_id STRING,
  p_effective_date DATE
) AS
BEGIN
  -- Create credit line for current invoice
  INSERT INTO invoice_line_items (invoice_id, amount_cents, description)
  SELECT
    i.invoice_id,
    -1 * (p.price_cents * days_remaining / days_in_period),
    'Proration credit for plan change'
  FROM invoices i
  JOIN plans p ON p.plan_id = p_new_plan_id
  WHERE i.subscription_id = p_subscription_id
    AND i.status = 'OPEN';

  -- Create new pro-rated charge
  INSERT INTO invoice_line_items (invoice_id, amount_cents, description)
  SELECT
    i.invoice_id,
    p.price_cents * days_remaining / days_in_period,
    'Prorated charge for new plan'
  FROM invoices i
  JOIN plans p ON p.plan_id = p_new_plan_id
  WHERE i.subscription_id = p_subscription_id;
END;
```

## Lakehouse Optimization

- **Partitioning**: `subscription` by `account_id`, `invoice` by `period_start`
- **Clustering**: `payment` by `(account_id, created_at)` for account history
- **Retention**: Keep full history for financial auditing and compliance

## Common Queries

```sql
-- Get current subscription for account
SELECT s.*, p.name, p.price_cents
FROM subscription s
JOIN plan p ON s.plan_id = p.plan_id
WHERE s.account_id = ?
  AND s.end_date IS NULL;

-- Calculate monthly recurring revenue (MRR)
SELECT
  DATE_TRUNC('month', i.period_start) AS billing_month,
  SUM(i.amount_due_cents) / 100.0 AS mrr_usd
FROM invoice i
WHERE i.status = 'PAID'
  AND i.period_start >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12' MONTH)
GROUP BY DATE_TRUNC('month', i.period_start)
ORDER BY billing_month;

-- Track plan change history
SELECT
  se.*,
  p_old.name AS old_plan_name,
  p_new.name AS new_plan_name
FROM subscription_event se
LEFT JOIN plan p_old ON se.old_plan_id = p_old.plan_id
LEFT JOIN plan p_new ON se.new_plan_id = p_new.plan_id
WHERE se.subscription_id = ?
ORDER BY se.event_time DESC;
```

## Design Considerations

- **Effective Dating**: SCD-2 pattern for subscription history
- **Event Sourcing**: `subscription_event` table tracks all state changes
- **Financial Accuracy**: Separate invoice and payment for accounting
- **Proration Logic**: Handle mid-cycle changes with proper credits/charges
- **Audit Trail**: Complete history for financial reporting and compliance

## Follow-up Questions

- How do you handle users upgrading/downgrading mid-cycle?
- How would you model gift subscriptions or promotional periods?
- How would you handle failed payments and dunning processes?
- How would you design for multi-currency billing?