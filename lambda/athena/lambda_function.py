import boto3
import os
import random
import logging
import time
import json

BUCKET_NAME=os.getenv('OUTPUT_LAKE_DB_BUCKET_NAME')

def lambda_handler(event, context):
    
    athena_client = boto3.client('athena')

    f = open('./assets/query.json')
    data = json.load(f)

    for map in data['mapping']:

        s3uri = "s3://" + BUCKET_NAME + "/" +  map['prefix']

        # Set the query string. This should be a valid Athena SQL query.
        run_query = f"UNLOAD ({map['query']}) TO '{s3uri}' WITH (format = 'PARQUET', compression='SNAPPY')" 

        # cleanpath
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(map['bucket'])
        bucket.objects.filter(Prefix=f"{map['prefix']}").delete()

        # Execute the query
        response = athena_client.start_query_execution(
                QueryString=run_query,
                WorkGroup="primary",
        )

        # Get the execution ID of the query from the response
        query_execution_id = response["QueryExecutionId"]

        # Poll the query execution until it finishes
        query_status = "RUNNING"
        while query_status == "RUNNING" or query_status == "QUEUED":
            response = athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            query_status = response["QueryExecution"]["Status"]["State"]
            if query_status == "FAILED":
                err_message = response["QueryExecution"]['Status']['StateChangeReason']
                raise Exception(err_message)
            elif query_status == "CANCELLED":
                raise Exception("Query was cancelled")
            time.sleep(1)

        # Get the query results
        response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
