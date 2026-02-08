# Data Pipeline Architecture

## Overview

Our data pipeline is the backbone of the ML system, responsible for ingesting raw data from multiple sources, transforming it into ML-ready features, and serving those features to production models. The pipeline is owned and maintained by the Data Engineering team (see Team Structure document), consisting of two dedicated data engineers: Priya Patel and Marcus Johnson.

## Pipeline Components

The pipeline is built on Apache Airflow, which orchestrates approximately 45 DAGs that run on schedules ranging from every 5 minutes (real-time user events) to daily (batch aggregations). The core DAGs handle: (1) raw data ingestion from the application database and event streams, (2) data validation using Great Expectations, (3) feature computation and transformation, and (4) feature store updates.

We use Feast as our feature store, which provides a unified interface for both batch and online feature serving. The online store is backed by Redis for low-latency serving during inference, while the offline store uses Parquet files on S3 for training data generation. Currently, the feature store manages 87 features across 12 feature groups.

## Data Validation

Data quality is enforced through Great Expectations, which runs validation suites on every data batch before it enters the transformation stage. We currently maintain 156 expectations across all data sources, covering schema validation, null checks, distribution drift detection, and referential integrity. Any validation failure triggers an alert to the on-call data engineer and halts downstream processing.

Following the August 15th incident (see Incident Report document), we added 23 additional schema validation rules specifically targeting upstream schema changes. These new rules compare incoming data schemas against a registered schema version and flag any unexpected column additions, removals, or type changes before data enters the pipeline.

## Performance and Scale

The pipeline processes approximately 2.3 million events per day. End-to-end latency from raw event to feature store update averages 8 minutes for the standard path. The real-time path (for critical user-facing features) achieves sub-30-second latency using Kafka streaming, though this path only handles a subset of 15 high-priority features.

## Integration with ML Models

The feature pipeline directly feeds into model training and inference. During Q3, the introduction of 12 new behavioral sequence features (computed through a new set of Airflow DAGs) was the primary driver behind the model accuracy improvement from 91.2% to 94.7% (see Q3 Model Performance Report). The ML Engineers work closely with Data Engineers to define feature specifications and validate feature quality before promotion to production.
