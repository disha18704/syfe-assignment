# Incident Report: August 15th Data Pipeline Outage

## Incident Summary

On August 15, 2025, at 02:14 UTC, the production data pipeline experienced a complete failure that lasted approximately 4 hours. The incident was caused by an unannounced schema change in the upstream application database, which broke the data ingestion DAGs in Airflow. The issue was resolved at 06:22 UTC by the on-call data engineer, Priya Patel.

## Timeline

- **02:14 UTC** — Airflow DAG `ingest_user_events` fails with a `SchemaValidationError`. The error is caused by a new column `user_preferences_v2` added to the `user_events` table by the application team without prior notification to the data engineering team.
- **02:14–02:45 UTC** — Cascading failures. Downstream DAGs (`compute_behavioral_features`, `update_feature_store`, `generate_training_data`) begin failing as they depend on the output of the ingestion DAG.
- **02:47 UTC** — PagerDuty alert fires. On-call engineer Priya Patel is paged.
- **03:05 UTC** — Priya identifies the root cause: the new column has a nullable JSON type that conflicts with the expected Parquet schema in the ingestion pipeline.
- **03:05–05:50 UTC** — Priya works on a fix: updating the ingestion DAG to handle the new column, adding it to the schema registry, and validating that downstream DAGs can process the updated schema.
- **05:50 UTC** — Fix deployed. Pipeline begins reprocessing the backlog of events accumulated during downtime.
- **06:22 UTC** — All backlogged events processed. Feature store fully updated. Model performance returns to normal levels.

## Impact

During the 4-hour outage, the ML models serving production traffic were operating on stale features from the Redis cache. The Q3 Model Performance Report notes that model accuracy degraded to approximately 87% during this window (down from the usual 94.7%). Approximately 180,000 user recommendations were served using outdated features.

No customer-facing errors occurred because the model serving layer has a fallback mechanism that serves cached predictions when fresh features are unavailable. However, recommendation quality was measurably degraded.

## Root Cause Analysis

The root cause was the absence of a formal schema change notification process between the application engineering team and the data engineering team. The application team deployed a database migration adding the `user_preferences_v2` column as part of a routine release, unaware that this would break the downstream data pipeline.

Contributing factors: (1) The Great Expectations validation suite did not include schema version checks—it only validated data quality within the existing schema. (2) There was no automated schema diff detection between the source database and the pipeline's expected schema.

## Remediation Actions

1. **Schema validation rules (Completed):** Added 23 new Great Expectations rules that compare incoming data schemas against a registered schema version (see Data Pipeline Architecture document for details).
2. **Cross-team notification process (Completed):** Established a mandatory review process where any application database migration must be approved by the data engineering team at least 48 hours before deployment.
3. **Schema registry integration (In Progress):** Integrating Apache Avro schema registry to automatically detect and flag schema changes. Owner: Marcus Johnson, ETA: October 2025.
4. **Stale feature alerting (Planned):** Adding monitoring to detect when the feature store is serving features older than a configurable threshold. This will be part of the Model Monitoring Dashboard (see Feature Roadmap).
