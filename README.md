# anz-elt-data-platform
High-level architecture diagram for both transaction and macroeconomic data pipelines.

┌──────────────────────────────────────────────────────┐     ┌──────────────────────────────────────────────────────┐
│             TRANSACTION DATA PIPELINE                │     │           MACROECONOMIC DATA PIPELINE               │
│                  (Daily Processing)                  │     │                (Monthly Processing)                 │
└──────────────────────────────────────────────────────┘     └──────────────────────────────────────────────────────┘
                     │                                                          │
                     ▼                                                          ▼
┌───────────────────────────────────────────────┐    ┌────────────────────────────────────────────────┐
│                ON-PREMISES UNIX               │    │              EXTERNAL VENDOR SFTP              │
│                   SERVER                      │    │                  (or HTTP API)                 │
│  - Contains 21-day rolling transactions      │    │  - Provides monthly CSV/JSON files            │
│  - 25GB/day of payment terminal data         │    │  - ~100MB files with economic indicators      │
└───────────────────────────────────────────────┘    └────────────────────────────────────────────────┘
                     │                                                          │
                     ▼                                                          ▼
┌───────────────────────────────────────────────┐    ┌────────────────────────────────────────────────┐
│            GOOGLE CLOUD STORAGE               │    │            GOOGLE CLOUD STORAGE               │
│  - Raw zone: gs://anz-raw-data/transactions/  │    │  - Landing zone: gs://anz-macroeconomics/     │
│  - Partitioned by transaction_date            │    │  - Files stored as YYYYMM_macro_data.csv      │
└───────────────────────────────────────────────┘    └────────────────────────────────────────────────┘
                     │                                                          │
                     ▼                                                          ▼
┌───────────────────────────────────────────────┐    ┌────────────────────────────────────────────────┐
│            CLOUD COMPOSER (AIRFLOW)           │    │            CLOUD COMPOSER (AIRFLOW)           │
│  - DAG: dataflow_elt.py                       │    │  - DAG: macroeconomics_dag.py                 │
│  - Triggers Dataflow job daily                │    │  - Runs monthly workflow                      │
│  - Handles incremental loads                  │    │  - Validates and transforms data              │
└───────────────────────────────────────────────┘    └────────────────────────────────────────────────┘
                     │                                                          │
                     ▼                                                          ▼
┌───────────────────────────────────────────────┐    ┌────────────────────────────────────────────────┐
│             DATAFLOW (PARQUET → BQ)           │    │              BIGQUERY DATA LOAD               │
│  - Processes 25GB/day efficiently             │    │  - Direct CSV load to partitioned tables      │
│  - Output to partitioned BigQuery tables      │    │  - Schema enforcement                        │
└───────────────────────────────────────────────┘    └────────────────────────────────────────────────┘
                     │                                                          │
                     ▼                                                          ▼
┌───────────────────────────────────────────────┐    ┌────────────────────────────────────────────────┐
│              BIGQUERY ANALYTICS               │    │              BIGQUERY ANALYTICS               │
│  - Dataset: anz_analytics                     │    │  - Dataset: anz_analytics                     │
│  - Table: fact_transactions                   │    │  - Table: macro_economic_indicators           │
│  - Partitioned by transaction_date            │    │  - Partitioned by month                       │
└───────────────────────────────────────────────┘    └────────────────────────────────────────────────┘
                     │                                                          │
                     ▼                                                          ▼
┌───────────────────────────────────────────────┐    ┌────────────────────────────────────────────────┐
│              DATA SCIENCE TEAM                │    │                 REPORTING                     │
│  - Analyze spending patterns                  │    │  - Monthly customer reports                   │
│  - Build ML models                           │    │  - Impact of economic changes                 │
└───────────────────────────────────────────────┘    └────────────────────────────────────────────────┘
