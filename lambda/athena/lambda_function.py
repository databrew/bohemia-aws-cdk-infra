import json
import boto3
import os
import random
import logging
import time

BUCKET_TARGET = os.getenv('OUTPUT_BUCKET_NAME')
FOLDER_NAME = 'test'
SQL_STATEMENT = """
SELECT extid FROM metadata.safety
"""

# Set the query string. This should be a valid Athena SQL query.
run_query = f"CREATE TABLE test WITH (format = 'PARQUET', external_location='{BUCKET_TARGET}/{FOLDER_NAME}/', write_compression='SNAPPY') AS {SQL_STATEMENT}" 

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    athena_client = boto3.client('athena')
    
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
            raise Exception("Query failed to execute")
        elif query_status == "CANCELLED":
            raise Exception("Query was cancelled")
        time.sleep(1)
    
    # Get the query results
    response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
