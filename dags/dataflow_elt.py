from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'project_id': 'anz-data-platform',
    'region': 'us-central1',
    'location': 'us-central1'
}

with DAG('dataflow_elt',
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False) as dag:

    process_transactions = DataflowStartFlexTemplateOperator(
        task_id="process_transactions",
        template_file_gcs_path="gs://dataflow-templates/latest/flex/Python_Parquet_To_BigQuery",
        parameters={
            'input': f'gs://anz-raw-data-$(gcloud config get-value project)/transactions/date={{{{ ds }}}}/data.parquet',
            'output': 'anz_analytics.fact_transactions'
        },
        location="us-central1",
        flex_template_environment_variables={
            'num_workers': '2',
            'max_workers': '10'
        },
        dataflow_default_options={
            'project': '{{ dag_run.conf["project_id"] or params.project_id }}',
            'region': '{{ params.region }}',
            'temp_location': 'gs://anz-dataflow-temp/tmp/'
        }
    )
