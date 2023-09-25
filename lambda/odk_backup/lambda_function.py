# This script is used for capturing ODK Backup via API
# Author: atediarjo@gmail.com

import os
import json
import boto3
import logging
import time
from datetime import datetime
from botocore.exceptions import ClientError
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
secrets_manager = boto3.client('secretsmanager')

CURRENT_DATE = datetime.utcnow().strftime('%Y-%m-%d')
OUTPUT_FILEPATH = f'/tmp/databrew-odk-central-backup.zip'
OBJECT_NAME = os.path.basename(OUTPUT_FILEPATH)
SECRET_ID = os.getenv('SECRET_ID')
ENDPOINT = 'https://databrew.org/v1/backup'
AUTH_DICT = json.loads(
    secrets_manager.get_secret_value(
        SecretId = SECRET_ID)['SecretString']
)


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# Handler, event will go through here
def lambda_handler(event, context):
    start = time.time()

    headers = {
        'Content-Type': 'application/json'
    }

    # try POST request to ODK
    try:
        response = requests.post(
            ENDPOINT, 
            headers = headers,
            auth= (AUTH_DICT['username'], AUTH_DICT['password'])
        )
    except Exception as e:
        logging.error(str(e))

    # # Check if the request was successful
    if response.status_code == 200:
        # Assuming the response contains the ZIP file as content
        zip_file_content = response.content
        
        # Save the ZIP backup to /tmp
        with open(OUTPUT_FILEPATH, "wb") as f:
            f.write(zip_file_content)
        logging.info("ZIP file downloaded successfully.")
    else:
        logging.info("Error:", response.status_code)

    # upload s3 file to bucket
    upload_file(
        file_name = OUTPUT_FILEPATH,
        bucket = os.getenv('BUCKET_NAME'),
        object_name = OBJECT_NAME
    )

    end = time.time()
    logging.info(f'Lambda ran for {int(end - start)} secs')
