from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 29),
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

def _validate_macro_data(**context):
    """Validate the macroeconomic CSV file before processing"""
    file_list = context['ti'].xcom_pull(task_ids='list_macro_files')
    if not file_list:
        raise ValueError("No macroeconomic data file found in GCS bucket")
    
    # Get most recent file (assuming pattern: macro_YYYYMM.csv)
    latest_file = sorted(file_list)[-1]  
    logging.info(f"Processing macroeconomic file: {latest_file}")
    return latest_file

with DAG(
    'macroeconomics_ingestion',
    schedule_interval='@monthly',
    default_args=default_args,
    catchup=False,
    tags=['macroeconomic']
) as dag:
    
    # 1. Check for new files
    list_macro_files = GCSListObjectsOperator(
        task_id='list_macro_files',
        bucket='anz-macroeconomics-data',
        prefix='macro_source/',
        delimiter='.csv',
        gcp_conn_id='google_cloud_default'
    )
    
    # 2. Validate file
    validate_file = PythonOperator(
        task_id='validate_file',
        python_callable=_validate_macro_data,
        provide_context=True
    )
    
    # 3. Load to BigQuery (fixed version)
    load_to_bq = GCSToBigQueryOperator(
        task_id='load_to_bq',
        bucket='anz-macroeconomics-data',
        source_objects=["{{ ti.xcom_pull(task_ids='validate_file') }}"],
        destination_project_dataset_table='anz_analytics.macro_economic_indicators',
        schema_fields=[
            {"name": "month", "type": "DATE", "mode": "REQUIRED"},
            {"name": "cash_rate", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "unemployment_rate", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "cpi", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "processing_date", "type": "TIMESTAMP", "mode": "NULLABLE"}
        ],
        source_format='CSV',
        skip_leading_rows=1,
        write_disposition='WRITE_TRUNCATE',
        time_partitioning={
            'type': 'MONTH',
            'field': 'month'
        },
        allow_quoted_newlines=True,  # Moved from additional_options
        allow_jagged_rows=True       # Moved from additional_options
    )
    
    list_macro_files >> validate_file >> load_to_bq
