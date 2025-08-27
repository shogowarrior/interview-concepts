# Relationships & Patterns

This section covers common relationship patterns in streaming platform data models, focusing on many-to-many relationships, viewing history, and recommendation systems.

## Files in this section

* **[Many-to-Many Relationships](many-to-many-relationships.md)** - Junction tables, bridge tables, temporal relationships, and optimization patterns
* **[User Viewing History](user-viewing-history.md)** - Playback sessions, granular events, resume functionality, and multi-device sync
* **[Recommendations Storage](recommendations-storage.md)** - Similarity graphs, personalized recommendations, feature stores, and model lineage

## Key Design Patterns

### Many-to-Many Relationships

* Simple junction tables for basic relationships
* Bridge tables with additional attributes
* Temporal relationships for historical tracking
* Self-referencing relationships for content similarity
* Performance optimization through clustering and indexing

### User Behavior Modeling

* Session-based event tracking
* Append-only event storage for audit trails
* Denormalized resume state for fast queries
* Device and profile context preservation

### Recommendation Systems

* Item-item similarity graphs
* Precomputed personalized recommendations
* Model versioning and A/B testing support
* Feature stores for machine learning

## Common Interview Questions

* How do you optimize many-to-many relationship queries?
* What are the trade-offs between normalized and denormalized approaches?
* How would you design for efficient recommendation serving at scale?
* How do you handle the cold start problem in recommendations?

## Performance Considerations

* **Indexing**: Composite indexes for common query patterns
* **Partitioning**: Time-based partitioning for event data
* **Materialized Views**: Pre-aggregated data for common queries
* **Clustering**: Data co-location for join optimization

---

Navigate back to [Data Modeling Index](../README.md)
