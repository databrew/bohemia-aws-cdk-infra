import urllib3 
import boto3
import os
import pandas as pd
import time
import awswrangler as aw
from datetime import datetime, timedelta, date
import logging
import subprocess
import sys
import json
from tabulate import tabulate


today = str(date.today())
logger = logging.getLogger()
logger.setLevel(logging.INFO)
http = urllib3.PoolManager() 

BUCKET_NAME = os.getenv('BUCKET_NAME')
TARGET_COLS = ['fid', 'submissions_total', 'submissions_today', 'submissions_p7d']

def get_slack_webhook_url(parameter_name):
    # Initialize a Boto3 SSM client
    ssm_client = boto3.client('ssm', region_name='us-east-1')
    try:
        logger.info('Try fetching SLACK URL parameter from SSM')
        # Get the parameter value
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        # Extract the value from the response
        parameter_value = response['Parameter']['Value']
    except ssm_client.exceptions.ParameterNotFound:
        logger.error(f"Parameter '{parameter_name}' not found in SSM.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    return(parameter_value)


def lambda_handler(event, context):
    start = time.time()

    logger.info('Listing objects..')
    objects = objects = boto3.client('s3').list_objects_v2(
        Bucket = BUCKET_NAME, 
        Prefix = 'kwale/clean-form')

    logger.info('Parse through contents ..')
    data_list = {}
    data_list['s3uri'] = []
    data_list['submissions_total'] = []
    data_list['submissions_today'] = []
    data_list['submissions_p7d'] = []
    for obj in objects['Contents']:
        key_name = f's3://{BUCKET_NAME}/' + obj['Key']
        if('-repeat' not in key_name):
            try:
                data = aw.s3.read_csv(key_name)
                nrow = data.shape[0]
                data['todays_date'] = pd.to_datetime(data['todays_date']).dt.date
                nrow_today = data[pd.to_datetime(data['todays_date']) == today].shape[0]
                seven_days_ago = (pd.to_datetime('today')-timedelta(days=7))
                nrow_past_seven_days = data[pd.to_datetime(data['todays_date']) >= seven_days_ago].shape[0]
        
                data_list['s3uri'].append(key_name)
                data_list['submissions_total'].append(nrow)
                data_list['submissions_today'].append(nrow_today)
                data_list['submissions_p7d'].append(nrow_past_seven_days)
            except Exception as err:
                logger.info(f"Unexpected {err=}, {type(err)=}")
                raise 
    
    logger.info('Create dataframe ..')
    try:
        d = pd.DataFrame(data_list)
        d['fid'] = d['s3uri'].apply(lambda x: os.path.splitext(os.path.basename(x))[0])
        d = d[TARGET_COLS].sort_values(
                by=['submissions_p7d'], ascending = False).set_index('fid')
    except Exception as err:
        logger.info(f"Unexpected {err=}, {type(err)=}")
        raise 
        
    logger.info('Create text output ..')
    try:
        output_string = tabulate(d, 
                                headers = TARGET_COLS, 
                                tablefmt = 'orgtbl')
        
        slack_table = {"text":f"*{today} Daily Form Updates:*\n"+"```\n" + output_string + "\n```"}
        info = json.dumps(slack_table)
    except Exception as err:
        logger.info(f"Unexpected {err=}, {type(err)=}")
        raise 
    
    # post to slack
    logger.info('Posting message to Slack ..')
    try:
        url = get_slack_webhook_url('DATA_OPS_BOT_SLACK_WEBHOOK_URL')
        http.request('POST', 
                     url, 
                     body=info)
    except Exception as err:
        logger.info(f"Unexpected {err=}, {type(err)=}")
        raise 
    
    end = time.time()
    logging.info(f'Lambda ran for {int(end - start)} secs')
