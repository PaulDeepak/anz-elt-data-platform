from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from airflow.providers.google.cloud.sensors.dataflow import DataflowJobStatusSensor
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 4, 29),
    'retries': 3,
    'retry_delay': timedelta(minutes=15),
    'dataflow_default_options': {
        'project': 'anz-data-platform',
        'region': 'us-central1',
        'tempLocation': 'gs://anz-dataflow-temp/tmp/',
        'serviceAccountEmail': 'anz-dataflow-sa@anz-data-platform.iam.gserviceaccount.com'
    }
}

with DAG('transaction_processing',
         schedule_interval='@daily',
         default_args=default_args,
         max_active_runs=1,
         catchup=False) as dag:

    process_transactions = DataflowStartFlexTemplateOperator(
        task_id="process_transactions",
        template="gs://dataflow-templates/latest/flex/Python_Parquet_To_BigQuery",
        parameters={
            "input": "gs://anz-raw-data-anz-data-platform/transactions/transactions.parquet/transaction_date={{ ds }}",
            "output": "anz_analytics.fact_transactions${{ ds_nodash }}",
            "window_size": "21"
        },
        location="us-central1",
        wait_until_finished=False  # Async operation
    )

    monitor_job = DataflowJobStatusSensor(
        task_id="monitor_job",
        job_id="{{ task_instance.xcom_pull(task_ids='process_transactions')['job_id'] }}",
        expected_statuses={"JOB_STATE_DONE"},
        location="us-central1"
    )

    process_transactions >> monitor_job
