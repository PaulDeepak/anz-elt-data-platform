from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 29),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'dataflow_default_options': {
        'project': 'anz-data-platform',
        'region': 'us-central1',
        'tempLocation': 'gs://anz-dataflow-temp/tmp/'
    }
}

with DAG('dataflow_elt',
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False) as dag:

    # Option 1: Recommended approach using template + parameters
    process_transactions = DataflowStartFlexTemplateOperator(
        task_id="process_transactions",
        template="gs://dataflow-templates/latest/flex/Python_Parquet_To_BigQuery",
        parameters={
            "input": "gs://anz-raw-data-anz-data-platform/transactions/transactions.parquet/transaction_date={{ ds }}",
            "output": "anz_analytics.fact_transactions${{ ds_nodash }}",
            "num_workers": "2",
            "max_workers": "10",
            "worker_machine_type": "n1-standard-4"
        },
        location="us-central1"
    )
