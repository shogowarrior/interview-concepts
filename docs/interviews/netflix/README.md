# Netflix Interview Preparation

Welcome to the reorganized Netflix interview preparation guide. This repository contains comprehensive content covering SQL problems, data modeling concepts, and advanced technical topics commonly asked in Netflix interviews.

## Directory Structure

### 📊 [sql-problems](../../concepts/sql/problems/README.md)

SQL-focused interview problems organized by complexity and topic.

- **[01-basic-analytics](../../concepts/sql/problems/01-basic-analytics/README.md)** - Fundamental SQL analytics problems
- **[02-ranking-window-functions](../../concepts/sql/problems/02-ranking-window-functions/README.md)** - Advanced ranking and window function problems
- **[Advanced Patterns](../../concepts/sql/problems/advanced-patterns.md)** - Complex SQL patterns and recursive queries
- **[Optimization Challenges](../../concepts/sql/problems/optimization-challenges.md)** - Query optimization and performance tuning

### 🏗️ [data-modeling](../../concepts/data-modeling/README.md)

Data architecture and modeling concepts for large-scale systems.

- **[01-core-entities](../../concepts/data-modeling/01-core-entities/README.md)** - Fundamental data entities and basic modeling
- **[02-relationships-patterns](../../concepts/data-modeling/02-relationships-patterns/README.md)** - Complex relationships and design patterns
- **[03-event-streaming](../../concepts/data-modeling/03-event-streaming/README.md)** - Event-driven architecture and streaming data
- **[04-scalability-patterns](../../concepts/data-modeling/04-scalability-patterns/README.md)** - Distributed systems and scalability patterns

### 🚀 [advanced-concepts](../../concepts/system-design/README.md)

Advanced technical concepts and system design patterns.

- **[System Architecture](../../concepts/system-design/system-architecture.md)** - Microservices and distributed system design
- **[Performance Optimization](../../concepts/system-design/performance-optimization.md)** - Caching, load balancing, and performance
- **[Experimentation](../../concepts/system-design/experimentation.md)** - A/B testing and experimentation platforms
- **[Case Studies](../../concepts/system-design/case-studies.md)** - Real-world architectural case studies

## Content Migration Status

- [x] Directory structure created
- [x] Index files created for all subdirectories
- [x] Structure simplification completed
- [x] Nested READMEs removed and navigation consolidated
- [x] Single-file directories converted to simplified naming
- [x] Content migration completed - using original files as authoritative source
- [x] Data modeling section - consolidated from original/netflix.md
- [x] SQL problems section - aligned with original/sql.md
- [x] Advanced concepts section - updated with original/case-study.md
- [x] Cross-references and navigation updated throughout

## Quick Start

1. **SQL Focus**: Start with [basic analytics](../../concepts/sql/problems/01-basic-analytics/README.md) if you're new to SQL
2. **Data Architecture**: Explore [core entities](../../concepts/data-modeling/01-core-entities/README.md) for data modeling fundamentals
3. **System Design**: Check [system architecture](../../concepts/system-design/system-architecture.md) for senior-level topics
4. **Real-world Application**: Study the [Top 10 case study](../../concepts/system-design/case-studies.md#top-10-feature-implementation-case-study) for end-to-end understanding

## Key Content Areas

### 📊 [SQL Problems](../../concepts/sql/problems/README.md)

- **[Basic Analytics](../../concepts/sql/problems/01-basic-analytics/README.md)** - DAU, retention, most-watched content
- **[Ranking & Window Functions](../../concepts/sql/problems/02-ranking-window-functions/README.md)** - Top-N queries, consecutive days, power users
- **[Advanced Patterns](../../concepts/sql/problems/advanced-patterns.md)** - Complex CTEs and recursive queries
- **[Optimization Challenges](../../concepts/sql/problems/optimization-challenges.md)** - Query performance and indexing

### 🏗️ [Data Modeling](../../concepts/data-modeling/README.md)

- **[Core Entities](../../concepts/data-modeling/01-core-entities/README.md)** - Content catalog, accounts/profiles, subscriptions
- **[Relationships & Patterns](../../concepts/data-modeling/02-relationships-patterns/README.md)** - User history, recommendations, many-to-many relationships
- **[Event Streaming](../../concepts/data-modeling/03-event-streaming/README.md)** - Real-time events, engagement metrics, A/B testing
- **[Scalability Patterns](../../concepts/data-modeling/04-scalability-patterns/README.md)** - Partitioning, sharding, event streaming at scale

### 🏗️ **Unified Data Modeling Framework**

For comprehensive data modeling concepts beyond Netflix-specific implementations:

- **[Complete Data Modeling Guide](../../concepts/data-modeling/README.md)** - Unified framework with streaming platform patterns
- **[Core Entities](../../concepts/data-modeling/01-core-entities/README.md)** - Universal content, user, and billing models
- **[Advanced Patterns](../../concepts/data-modeling/02-relationships-patterns/README.md)** - Relationship modeling and behavioral analytics
- **[Event Streaming](../../concepts/data-modeling/03-event-streaming/README.md)** - Real-time data patterns and experimentation
- **[Scalability](../../concepts/data-modeling/04-scalability-patterns/README.md)** - Distributed systems and performance

### 🚀 [Advanced Concepts](../../concepts/system-design/README.md)

- **[System Architecture](../../concepts/system-design/system-architecture.md)** - Microservices and distributed systems
- **[Performance Optimization](../../concepts/system-design/performance-optimization.md)** - Caching, load balancing, optimization techniques
- **[Experimentation](../../concepts/system-design/experimentation.md)** - A/B testing and experimentation platforms
- **[Case Studies](../../concepts/system-design/case-studies.md)** - Real-world architectural challenges and solutions

## Cross-References

### From SQL to Data Modeling

- [Top 3 Shows per Region](../../concepts/sql/problems/02-ranking-window-functions/top-3-shows-per-region.md) → [Content Catalog Modeling](../../concepts/data-modeling/01-core-entities/content-catalog-modeling.md)
- [Recommendation Acceptance](../../concepts/sql/problems/02-ranking-window-functions/README.md) → [Recommendations Storage](../../concepts/data-modeling/02-relationships-patterns/recommendations-storage.md)

### From Data Modeling to Advanced Concepts

- [Unified Data Modeling](../../concepts/data-modeling/README.md) → Complete data modeling framework
- [Event Streaming](../../concepts/data-modeling/03-event-streaming/README.md) → [Top 10 Feature Implementation](../../concepts/system-design/case-studies.md#top-10-feature-implementation-case-study)

- [User Viewing History](../../concepts/data-modeling/02-relationships-patterns/user-viewing-history.md) → [Personalization Engine](../../concepts/system-design/case-studies.md#personalization-engine-at-scale)

### From General Concepts to Netflix Problems

- [SQL Learning Hub](../../concepts/sql/README.md) → SQL fundamentals and Netflix examples
- [Aggregate Functions](../../concepts/sql/aggregation/aggregate-functions.md) → [Daily Active Users](../../concepts/sql/problems/01-basic-analytics/daily-active-users.md)
- [Window Functions](../../concepts/sql/window-functions/README.md) → [Ranking Problems](../../concepts/sql/problems/02-ranking-window-functions/README.md)

### End-to-End Case Studies

- [Top 10 Feature](../../concepts/system-design/case-studies.md#top-10-feature-implementation-case-study) - Complete data pipeline from ingestion to serving

- [Personalization Engine](../../concepts/system-design/case-studies.md#personalization-engine-at-scale) - ML-driven recommendation systems

## Resources

- [Data Modeling Concepts](../../concepts/data-modeling/README.md) - Comprehensive data modeling and architecture source
- [SQL Interview Problems](../../concepts/sql/problems/README.md) - SQL interview questions and solutions source
- [System Design Case Studies](../../concepts/system-design/case-studies.md) - "Top 10" feature comprehensive implementation source

## Interview Preparation Tips

1. **Start with SQL**: Master the [basic analytics](../../concepts/sql/problems/01-basic-analytics/README.md) and [window functions](../../concepts/sql/problems/02-ranking-window-functions/README.md)
2. **Learn Data Modeling**: Understand the [core entities](../../concepts/data-modeling/01-core-entities/README.md) and [relationships](../../concepts/data-modeling/02-relationships-patterns/README.md)
3. **Study Real Cases**: Dive deep into the [Top 10 case study](../../concepts/system-design/case-studies.md) for end-to-end understanding
4. **Practice Scale**: Focus on [scalability patterns](../../concepts/data-modeling/04-scalability-patterns/README.md) and [performance optimization](../../concepts/system-design/performance-optimization.md)
