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
BUCKET_NAME = os.getenv('DLAKE_BUCKET_NAME')

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

    # object reference
    anomalies_resolution =  's3://' + BUCKET_NAME + '/' + 'bohemia_prod/anomalies_resolution/anomalies_resolution.csv'
    anomalies_detection =  's3://' + BUCKET_NAME + '/' + 'bohemia_prod/anomalies_detection/anomalies_detection.csv'
    v0_repeat =  's3://' + 'databrew.org' + '/' + 'kwale/clean-form/v0demography/v0demography-repeat_individual.csv'

    logger.info('Fetch dataframe ..')
    anomalies_resolution_df = aw.s3.read_csv(anomalies_resolution)
    anomalies_detection_df = aw.s3.read_csv(anomalies_detection)
    anomalies_detection_summary_df = (anomalies_detection_df[~anomalies_detection_df['form_id'].isin(['v0demography', 
                                                                                                    'v0demography-repeat_individual'])]\
                                                                .groupby('form_id')\
                                                                .agg(anomalies = pd.NamedAgg(column = "resolution_id",
                                                                                                aggfunc= "nunique"))\
                                                                .reset_index())

    anomalies_resolution_summary_df = (anomalies_resolution_df[~anomalies_resolution_df['form_id'].isin(['v0demography',
                                                                                                        'v0demography-repeat_individual'])]\
                                                                .groupby(['form_id'])\
                                                                .agg(resolved = pd.NamedAgg(column = "resolution_id",
                                                                                                aggfunc= "nunique"))\
                                                                .reset_index())
    

    merged_summary = pd.merge(
            anomalies_detection_summary_df, 
            anomalies_resolution_summary_df, 
            how="left", 
            on='form_id'
    )
    
    merged_summary['resolved'] = merged_summary['resolved'].fillna(0)
    merged_summary['completion'] = 100 * (merged_summary['resolved'] / merged_summary['anomalies'])
    merged_summary['completion'] = merged_summary['completion'].fillna(0)
    merged_summary['completion'] = merged_summary['completion'].apply(lambda x: "{:.1f}%".format(x))


    anomalies_completion = merged_summary.set_index('form_id').to_markdown()
    top_10_anomalies_id = anomalies_detection_df.groupby('anomalies_id').agg(
        anomalies = pd.NamedAgg(
            column = 'resolution_id',
            aggfunc= "nunique")).sort_values('anomalies', ascending = False).head(10).to_markdown()
    top_10_wid_anomalies = anomalies_detection_df.groupby('anomalies_reports_to_wid').agg(
        anomalies = pd.NamedAgg(
            column = 'resolution_id',
            aggfunc= "nunique")).sort_values('anomalies', ascending = False).head(10).to_markdown()
    
    anomalies = anomalies_detection_summary_df['anomalies'].sum()
    resolved = anomalies_resolution_summary_df['resolved'].sum()
    burn_rate = "{:.1f}%".format(100* resolved/anomalies)
    summary_anomalies = f"\nTotal anomalies: {anomalies}\nTotal resolved: {resolved}\nAnomalies Burn Rate: {burn_rate}\n \n"

    anomalies_completion_data_blob = "*Anomalies Completion:* \n" + summary_anomalies + "```\n" + anomalies_completion + "\n```"
    top_10_anomalies_id_data_blob = "\n \n*Top 10 Anomalies:* \n ```\n" + top_10_anomalies_id + "\n```"
    top_10_wid_anomalies_data_blob = "\n \n*Top 10 Workers with most anomalies:* \n ```\n" + top_10_wid_anomalies  + "\n```"
    output_string = anomalies_completion_data_blob + top_10_anomalies_id_data_blob + top_10_wid_anomalies_data_blob

    today = str(date.today())
    slack_table = {"text":f"*{today} Daily Anomalies Updates:* \n \n"+ output_string}
    info = json.dumps(slack_table)
    
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
