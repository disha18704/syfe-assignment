# Q4 Feature Roadmap

## Overview

This document outlines the planned features and initiatives for Q4 2025 (October–December). The roadmap builds on the strong Q3 model performance results and addresses key gaps identified during the August incident. All timelines are contingent on current team capacity (see Team Structure document for staffing details).

## Priority 1: Real-Time Inference Pipeline

Target completion: End of October 2025. Owner: Sarah Chen (ML Engineer) and Priya Patel (Data Engineer).

We plan to transition our primary recommendation model from batch inference (currently running every 15 minutes) to true real-time inference. This involves deploying the Transformer model behind a low-latency serving layer (likely using NVIDIA Triton Inference Server) and connecting it directly to the Kafka-based real-time feature path described in the Data Pipeline Architecture document.

Expected impact: Reduce recommendation staleness from 15 minutes to under 2 seconds. This is projected to improve click-through rates by 5–8% based on our offline simulation experiments conducted in Q3.

## Priority 2: A/B Testing Framework

Target completion: Mid-November 2025. Owner: James Liu (ML Engineer) and David Kim (MLOps Engineer).

Currently, we have no standardized way to run controlled experiments comparing model versions. The new framework will support: (1) traffic splitting at the user level with configurable ratios, (2) automated metric collection and statistical significance testing, (3) integration with the model registry for one-click rollback, and (4) a dashboard showing experiment results in real-time.

This framework is critical for safely deploying the real-time inference pipeline and any future model updates. Without it, we are effectively deploying model changes blind.

## Priority 3: Model Monitoring Dashboard

Target completion: End of December 2025. Owner: David Kim (MLOps Engineer).

The August 15th incident highlighted the need for better real-time visibility into model performance. The monitoring dashboard will track: (1) prediction accuracy and confidence distribution, (2) feature drift using Population Stability Index (PSI), (3) inference latency percentiles (p50, p95, p99), and (4) data pipeline health indicators.

The dashboard will integrate with PagerDuty for automated alerting when metrics breach defined thresholds. David Kim will leverage the model performance data described in the Q3 Model Performance Report to establish baseline thresholds.

## Resource Constraints

The team is currently at capacity with 6 members (see Team Structure document). The real-time inference project requires significant cross-functional collaboration between ML and Data Engineering. If any team member is unavailable for an extended period, the monitoring dashboard (Priority 3) will be deferred to Q1 2026. We have submitted a request to hire one additional ML Engineer to support the growing scope.
