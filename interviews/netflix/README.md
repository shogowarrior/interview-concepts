# Netflix Interview Preparation

Welcome to the reorganized Netflix interview preparation guide. This repository contains comprehensive content covering SQL problems, data modeling concepts, and advanced technical topics commonly asked in Netflix interviews.

## Directory Structure

### 📊 [sql-problems](sql-problems/)
SQL-focused interview problems organized by complexity and topic.

- **[01-basic-analytics](sql-problems/01-basic-analytics/)** - Fundamental SQL analytics problems
- **[02-ranking-window-functions](sql-problems/02-ranking-window-functions/)** - Advanced ranking and window function problems
- **[Advanced Patterns](sql-problems/advanced-patterns.md)** - Complex SQL patterns and recursive queries
- **[Optimization Challenges](sql-problems/optimization-challenges.md)** - Query optimization and performance tuning

### 🏗️ [data-modeling](data-modeling/)
Data architecture and modeling concepts for large-scale systems.

- **[01-core-entities](data-modeling/01-core-entities/)** - Fundamental data entities and basic modeling
- **[02-relationships-patterns](data-modeling/02-relationships-patterns/)** - Complex relationships and design patterns
- **[03-event-streaming](data-modeling/03-event-streaming/)** - Event-driven architecture and streaming data
- **[04-scalability-patterns](data-modeling/04-scalability-patterns/)** - Distributed systems and scalability patterns

### 🚀 [advanced-concepts](advanced-concepts/)
Advanced technical concepts and system design patterns.

- **[System Architecture](advanced-concepts/system-architecture.md)** - Microservices and distributed system design
- **[Performance Optimization](advanced-concepts/performance-optimization.md)** - Caching, load balancing, and performance
- **[Experimentation](advanced-concepts/experimentation.md)** - A/B testing and experimentation platforms
- **[Case Studies](advanced-concepts/case-studies.md)** - Real-world architectural case studies

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

1. **SQL Focus**: Start with [basic analytics](sql-problems/01-basic-analytics/) if you're new to SQL
2. **Data Architecture**: Explore [core entities](data-modeling/01-core-entities/) for data modeling fundamentals
3. **System Design**: Check [system architecture](advanced-concepts/system-architecture.md) for senior-level topics
4. **Real-world Application**: Study the [Top 10 case study](advanced-concepts/case-studies.md#top-10-feature-implementation) for end-to-end understanding

## Key Content Areas

### 📊 [SQL Problems](sql-problems/)
- **[Basic Analytics](sql-problems/01-basic-analytics/)** - DAU, retention, most-watched content
- **[Ranking & Window Functions](sql-problems/02-ranking-window-functions/)** - Top-N queries, consecutive days, power users
- **[Advanced Patterns](sql-problems/advanced-patterns.md)** - Complex CTEs and recursive queries
- **[Optimization Challenges](sql-problems/optimization-challenges.md)** - Query performance and indexing

### 🏗️ [Data Modeling](data-modeling/)
- **[Core Entities](data-modeling/01-core-entities/)** - Content catalog, accounts/profiles, subscriptions
- **[Relationships & Patterns](data-modeling/02-relationships-patterns/)** - User history, recommendations, many-to-many relationships
- **[Event Streaming](data-modeling/03-event-streaming/)** - Real-time events, engagement metrics, A/B testing
- **[Scalability Patterns](data-modeling/04-scalability-patterns/)** - Partitioning, sharding, event streaming at scale

### 🏗️ **Unified Data Modeling Framework**
For comprehensive data modeling concepts beyond Netflix-specific implementations:
- **[Complete Data Modeling Guide](../../concepts/data-modeling/)** - Unified framework with streaming platform patterns
- **[Core Entities](../../concepts/data-modeling/01-core-entities/)** - Universal content, user, and billing models
- **[Advanced Patterns](../../concepts/data-modeling/02-relationships-patterns/)** - Relationship modeling and behavioral analytics
- **[Event Streaming](../../concepts/data-modeling/03-event-streaming/)** - Real-time data patterns and experimentation
- **[Scalability](../../concepts/data-modeling/04-scalability-patterns/)** - Distributed systems and performance

### 🚀 [Advanced Concepts](advanced-concepts/)
- **[System Architecture](advanced-concepts/system-architecture.md)** - Microservices and distributed systems
- **[Performance Optimization](advanced-concepts/performance-optimization.md)** - Caching, load balancing, optimization techniques
- **[Experimentation](advanced-concepts/experimentation.md)** - A/B testing and experimentation platforms
- **[Case Studies](advanced-concepts/case-studies.md)** - Real-world architectural challenges and solutions

## Cross-References

### From SQL to Data Modeling
- [Top 3 Shows per Region](sql-problems/02-ranking-window-functions/top-3-shows-per-region.md) → [Content Catalog Modeling](../../concepts/data-modeling/01-core-entities/content-catalog-modeling.md)
- [Recommendation Acceptance](sql-problems/02-ranking-window-functions/) → [Recommendations Storage](../../concepts/data-modeling/02-relationships-patterns/recommendations-storage.md)

### From Data Modeling to Advanced Concepts
- [Unified Data Modeling](../../concepts/data-modeling/) → Complete data modeling framework
- [Event Streaming](../../concepts/data-modeling/03-event-streaming/) → [Top 10 Feature Implementation](advanced-concepts/case-studies.md#top-10-feature-implementation)
- [User Viewing History](../../concepts/data-modeling/02-relationships-patterns/user-viewing-history.md) → [Personalization Engine](advanced-concepts/case-studies.md#personalization-engine-at-scale)

### From General Concepts to Netflix Problems
- [SQL Learning Hub](../../concepts/sql/README.md) → SQL fundamentals and Netflix examples
- [Aggregate Functions](../../concepts/sql/aggregation/aggregate-functions.md) → [Daily Active Users](sql-problems/01-basic-analytics/daily-active-users.md)
- [Window Functions](../../concepts/sql/window-functions/) → [Ranking Problems](sql-problems/02-ranking-window-functions/)

### End-to-End Case Studies
- [Top 10 Feature](advanced-concepts/case-studies.md#top-10-feature-implementation) - Complete data pipeline from ingestion to serving
- [Personalization Engine](advanced-concepts/case-studies.md#personalization-engine-at-scale) - ML-driven recommendation systems

## Resources

- [Original Netflix Content](original/netflix.md) - Data modeling and architecture source
- [Original SQL Problems](original/sql.md) - SQL interview questions and solutions source
- [Original Case Study](original/case-study.md) - "Top 10" feature comprehensive implementation source

## Interview Preparation Tips

1. **Start with SQL**: Master the [basic analytics](sql-problems/01-basic-analytics/) and [window functions](sql-problems/02-ranking-window-functions/)
2. **Learn Data Modeling**: Understand the [core entities](data-modeling/01-core-entities/) and [relationships](data-modeling/02-relationships-patterns/)
3. **Study Real Cases**: Dive deep into the [Top 10 case study](advanced-concepts/case-studies.md) for end-to-end understanding
4. **Practice Scale**: Focus on [scalability patterns](data-modeling/04-scalability-patterns/) and [performance optimization](advanced-concepts/performance-optimization.md)

## Contributing

Content has been migrated from authoritative sources in the `original/` directory. The reorganization improves accessibility while maintaining content integrity. All content now uses consistent terminology and includes comprehensive cross-references.

---

*Last updated: Content Migration Complete - All sections consolidated from original authoritative sources with enhanced navigation and cross-references*