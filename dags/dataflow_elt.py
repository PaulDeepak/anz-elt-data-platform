from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
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
        body={
            "launchParameter": {
                "containerSpecGcsPath": "gs://dataflow-templates/latest/flex/Python_Parquet_To_BigQuery",
                "parameters": {
                    "input": "gs://anz-raw-data-anz-data-platform/transactions/transactions.parquet/transaction_date={{ ds }}",
                    "output": "anz_analytics.fact_transactions"
                },
                "environment": {
                    "numWorkers": 2,
                    "maxWorkers": 10,
                    "tempLocation": "gs://anz-dataflow-temp/tmp/"
                },
                "projectId": "{{ dag_run.conf.get('project_id', params['project_id']) }}",
                "location": "{{ params['region'] }}"
            }
        },
        location="us-central1"
    )
