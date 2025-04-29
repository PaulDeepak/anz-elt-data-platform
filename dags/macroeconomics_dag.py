from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import tempfile

with DAG(
    'macroeconomics_ingestion',
    start_date=datetime(2025, 5, 1),
    schedule_interval='@monthly',
    catchup=False
) as dag:
    
    # 1. Fetch data from HTTP endpoint
    fetch_macro_data = HttpOperator(
        task_id='fetch_macro_data',
        http_conn_id='http_local',
        endpoint='keyword_sheetcopy.txt',
        method='GET',
        response_filter=lambda response: response.text,
        dag=dag
    )
    
    # 2. Save to temporary file
    def save_response_to_file(**context):
        response = context['ti'].xcom_pull(task_ids='fetch_macro_data')
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
            tmp.write(response)
            return tmp.name
    
    create_temp_file = PythonOperator(
        task_id='create_temp_file',
        python_callable=save_response_to_file,
        provide_context=True,
        dag=dag
    )
    
    # 3. Upload to GCS
    upload_to_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_to_gcs',
        src="{{ ti.xcom_pull(task_ids='create_temp_file') }}",
        dst='macroeconomics/keyword_sheetcopy_{{ ds }}.txt',
        bucket='anz-macroeconomics-data',
        gcp_conn_id='google_cloud_default',
        dag=dag
    )
    
    fetch_macro_data >> create_temp_file >> upload_to_gcs
