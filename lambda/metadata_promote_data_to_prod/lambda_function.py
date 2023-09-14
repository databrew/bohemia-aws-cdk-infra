import boto3
from datetime import date
import os
import zipfile
import logging
import pandas as pd
import awswrangler as aw

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3client = boto3.client('s3')

DQ_TEST_BUCKET_NAME = os.getenv('DQ_TEST_BUCKET_NAME')
TARGET_BUCKET_NAME = os.getenv('TARGET_BUCKET_NAME')

def get_prod_zipfile(metadata_type):
    try:
        logger.info('fetching zip file from user')
        local_zip_folder = f'/tmp/{metadata_type}'
        local_zip_file_path = f'/tmp/{metadata_type}.zip'
        s3client.download_file(
            Bucket=f'{DQ_TEST_BUCKET_NAME}',
            Key = f'zip_prod/{metadata_type}.zip',
            Filename = local_zip_file_path
        )
        # Unzip the file
        with zipfile.ZipFile(local_zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(local_zip_folder)
        
        logger.info('successful zip file fetch')
    except Exception as e:
        logger.info('get_prod_zipfile err: ' + str(e))
        raise()

def snapshot_current(metadata_type):
    dir = f'/tmp/{metadata_type}'
    csvs = set(list(filter(lambda f: f.endswith('.csv'), os.listdir(dir))))
    for csv in csvs:
        output_key = f'metadata/{metadata_type}_{os.path.splitext(csv)[0]}/{csv}'
        output_key_history = f'metadata/{metadata_type}_{os.path.splitext(csv)[0]}_hist/run_date={date.today().strftime("%Y-%m-%d")}/{csv}'
        df = pd.read_csv(f'{dir}/{csv}')
        aw.s3.to_csv(df, f's3://{TARGET_BUCKET_NAME}/{output_key}')
        aw.s3.to_csv(df, f's3://{TARGET_BUCKET_NAME}/{output_key_history}')

def lambda_handler(event, context):
    s3_event = event['Records'][0]['s3']['object']['key']
    metadata_type = os.path.basename(os.path.splitext(s3_event)[0])
    get_prod_zipfile(metadata_type)
    snapshot_current(metadata_type)