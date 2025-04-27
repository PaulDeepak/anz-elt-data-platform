import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import argparse

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='GCS path to transactions')
    parser.add_argument('--output', required=True, help='BigQuery table')
    known_args, pipeline_args = parser.parse_known_args(argv)

    options = PipelineOptions(pipeline_args)

    with beam.Pipeline(options=options) as p:
        (p
         | 'ReadFromGCS' >> beam.io.ReadFromParquet(known_args.input)
         | 'FilterValid' >> beam.Filter(lambda x: x['status'] == 'SUCCESS')
         | 'EnrichData' >> beam.Map(lambda x: {
            'transaction_id': x['transaction_id'],
            'terminal_id': x['terminal_id'],
            'customer_id': x['customer_id'],
            'amount': float(x['amount']),
            'currency': x['currency'],
            'status': x['status'],
         })
         | 'WriteToBQ' >> beam.io.WriteToBigQuery(
            known_args.output,
            schema='transaction_id:STRING,terminal_id:STRING,customer_id:STRING,amount:FLOAT,currency:STRING,status:STRING',
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
         )

if __name__ == '__main__':
    run()
