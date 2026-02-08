# ML Team Structure and Responsibilities

## Overview

The Machine Learning team consists of 6 members reporting to VP of Engineering, Lisa Wang. The team is organized into three functional areas: ML Engineering, Data Engineering, and MLOps. This structure was established in Q1 2025 to support the growing complexity of our ML systems and the increasing volume of model development work.

## Team Members and Roles

### ML Engineers
- **Sarah Chen (Senior ML Engineer):** Leads model development and architecture decisions. Key contributor to the Q3 XGBoost-to-Transformer migration (see Q3 Model Performance Report). Currently leading the real-time inference pipeline project for Q4 (see Feature Roadmap). 4 years at the company.
- **James Liu (ML Engineer):** Focuses on model training, evaluation, and experimentation infrastructure. Co-led the Transformer migration with Sarah. Currently leading the A/B testing framework development for Q4 (see Feature Roadmap). 2 years at the company.

### Data Engineers
- **Priya Patel (Senior Data Engineer):** Owns the production data pipeline and feature store (see Data Pipeline Architecture). Led the incident response for the August 15th outage (see Incident Report). Currently collaborating with Sarah on the real-time inference pipeline. 3 years at the company.
- **Marcus Johnson (Data Engineer):** Focuses on data quality, validation, and schema management. Currently leading the Avro schema registry integration as part of the incident remediation. Also maintains the Great Expectations validation suite. 1.5 years at the company.

### MLOps
- **David Kim (MLOps Engineer):** Manages model deployment, serving infrastructure, and CI/CD pipelines for ML. Responsible for the model registry and production monitoring. Currently leading the A/B testing framework (with James) and the model monitoring dashboard planned for Q4 (see Feature Roadmap). 2.5 years at the company.

### Product
- **Rachel Torres (Product Manager):** Defines product requirements for ML features, prioritizes the roadmap, and coordinates with stakeholders. Manages the Q4 planning and resource allocation (see Feature Roadmap). 1 year at the company.

## Key Responsibilities by Function

| Function | Primary Responsibilities | Key Systems Owned |
|---|---|---|
| ML Engineering | Model development, training, evaluation, architecture | Models, training pipelines, experiments |
| Data Engineering | Data ingestion, transformation, feature engineering, data quality | Airflow DAGs, Feast feature store, Great Expectations |
| MLOps | Deployment, serving, monitoring, CI/CD | Model registry, Triton server, monitoring |
| Product | Roadmap, prioritization, stakeholder management | Product specs, OKRs |

## Capacity and Hiring

The team is currently at full capacity. All six members are committed to Q4 roadmap items. The real-time inference project is particularly resource-intensive, requiring close collaboration between Sarah Chen (ML) and Priya Patel (Data Engineering). A hiring request for one additional ML Engineer has been submitted and is currently in the interview pipeline, with an expected start date of Q1 2026 if approved.

If any team member is unavailable for an extended period, the Q4 monitoring dashboard project (owned by David Kim) would be the first item deferred, as it has the least direct impact on end-user experience compared to real-time inference and A/B testing.
