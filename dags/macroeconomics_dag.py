from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from datetime import datetime

with DAG(
    'macroeconomics_ingestion',
    start_date=datetime(2025, 5, 10),
    schedule_interval='@monthly',
    catchup=False
) as dag:
    fetch_macro_data = SimpleHttpOperator(
        task_id='fetch_macro_data',
        http_conn_id='http_local',
        endpoint='keyword_sheetcopy.txt',
        method='GET',
        response_filter=lambda response: response.text,
        dag=dag
    )
    upload_macro_data_to_gcs = GCSToGCSOperator(
        task_id='upload_macro_data_to_gcs',
        src='macro_data.txt',
        dst='gs://anz-macroeconomics-data/macroeconomics/keyword_sheetcopy_{{ ds }}.txt',
        gcp_conn_id='google_cloud_default',
        dag=dag
    )
    fetch_macro_data >> upload_macro_data_to_gcs
