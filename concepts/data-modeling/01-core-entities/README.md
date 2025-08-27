# Core Entities

This section covers the fundamental entities in a streaming platform data model, including content catalog, user accounts/profiles, and subscription/billing systems.

## Files in this section:

* **[Content Catalog Modeling](content-catalog-modeling.md)** - Designing data models for movies, shows, seasons, episodes, genres, and localization
* **[Accounts & Profiles](accounts-profiles.md)** - User account and profile management with device relationships
* **[Subscriptions & Billing](subscriptions-billing.md)** - Subscription plans, billing cycles, promotions, and payment processing

## Key Design Patterns:

### Content Catalog
- Unified `title` table for movies and shows
- Hierarchical season/episode structure
- Many-to-many relationships with genres
- Localized metadata for global content

### User Management
- Account-level device registration
- Profile-level content access and preferences
- Many-to-many profile-device relationships
- Maturity ratings and parental controls

### Billing & Subscriptions
- Effective-dated subscription changes (SCD-2)
- Separate invoice and payment tracking
- Complex promotion and discount systems
- Audit trails for regulatory compliance

## Common Interview Questions:

* How would you model content localization across multiple regions?
* How do you handle device limits and concurrent streaming?
* What are the trade-offs between real-time vs. end-of-cycle billing?
* How would you track subscription changes and calculate prorated charges?

---

Navigate back to [Data Modeling Index](../README.md)