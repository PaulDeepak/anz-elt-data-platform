import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Define the BigQuery table schema
schema = 'transaction_id:STRING,terminal_id:STRING,customer_id:STRING,amount:FLOAT,currency:STRING,status:STRING,transaction_date:DATE'

# Function to extract and format the data
def format_data(element):
    return {
        'transaction_id': element['transaction_id'],
        'terminal_id': element['terminal_id'],
        'customer_id': element['customer_id'],
        'amount': float(element['amount']),
        'currency': element['currency'],
        'status': element['status'],
        'transaction_date': element['transaction_date']
    }

# Function to filter for successful transactions
def is_success(element):
    return element['status'] == 'SUCCESS'

def run(argv=None):
    """Main entry point; defines and runs the pipeline."""
    options = PipelineOptions()
    with beam.Pipeline(options=options) as pipeline:
        (
            pipeline
            | 'ReadFromParquet' >> beam.io.ReadFromParquet('data/transactions.parquet/*/*')
            | 'FilterSuccess' >> beam.Filter(is_success)
            | 'EnrichData' >> beam.Map(format_data)
            | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
                table='anz-data-platform:anz_macroeconomics.fact_macroeco',
                schema=schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )

if __name__ == '__main__':
    run()
