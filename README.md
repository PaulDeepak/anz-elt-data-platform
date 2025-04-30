# ANZ ELT Data Platform
High-level architecture diagram for both transaction and macroeconomic data pipelines.

## Data Pipeline Architecture

### Overview
Two parallel pipelines processing:
1. **Daily transaction data** (25GB/day from on-prem)
2. **Monthly macroeconomic data** (100MB/month from vendor)

```mermaid
flowchart TD
    subgraph Macro[Monthly Macroeconomic Pipeline]
        direction TB
        B1[Vendor SFTP • 100MB/month • CSV files] -->|Monthly Upload| B2[GCS Landing Zone • gs://anz-macroeconomics]
        B2 --> B3[Cloud Composer • Monthly Trigger]
        B3 --> B4[BigQuery Load • Schema Validation]
        B4 --> B5[BigQuery • macro_indicators • Month-partitioned]
        B5 --> B6[Reporting Dashboards]
    end

    subgraph Transaction[Daily Transaction Pipeline]
        direction TB
        A1[On-Prem UNIX Server • 25GB/day • 21-day window] -->|SFTP/Storage Transfer| A2[GCS Raw Zone • gs://anz-raw-data]
        A2 --> A3[Cloud Composer • Daily Trigger]
        A3 --> A4[Dataflow Job • Parquet→BigQuery]
        A4 --> A5[BigQuery • fact_transactions • Date-partitioned]
        A5 --> A6[Data Science Team]
    end

    style Transaction fill:#f5f5f5,stroke:#333
    style Macro fill:#f0f7ff,stroke:#333
