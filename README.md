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
        B1[Vendor SFTP\n• 100MB/month\n• CSV files] -->|Monthly Upload| B2[GCS Landing Zone\n• gs://anz-macroeconomics]
        B2 --> B3[Cloud Composer\n• Monthly Trigger]
        B3 --> B4[BigQuery Load\n• Schema Validation]
        B4 --> B5[BigQuery\n• macro_indicators\n• Month-partitioned]
        B5 --> B6[Reporting Dashboards]
    end

    subgraph Transaction[Daily Transaction Pipeline]
        direction TB
        A1[On-Prem UNIX Server\n• 25GB/day\n• 21-day window] -->|SFTP/Storage Transfer| A2[GCS Raw Zone\n• gs://anz-raw-data]
        A2 --> A3[Cloud Composer\n• Daily Trigger]
        A3 --> A4[Dataflow Job\n• Parquet→BigQuery]
        A4 --> A5[BigQuery\n• fact_transactions\n• Date-partitioned]
        A5 --> A6[Data Science Team]
    end

    style Transaction fill:#f5f5f5,stroke:#333
    style Macro fill:#f0f7ff,stroke:#333
