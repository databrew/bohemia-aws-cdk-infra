import os
import zipfile
import boto3
import awswrangler as aw
import pandas as pd
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DQ_TEST_BUCKET_NAME = os.getenv('DQ_TEST_BUCKET_NAME')
TARGET_BUCKET_NAME = os.getenv('TARGET_BUCKET_NAME')

def check_zip_n_content(dir, n_content):
    try:
        logger.info('testing check_zip_n_content')
        data_dict = {}
        if len(list(filter(lambda f: f.endswith('.csv'), os.listdir(dir)))) != n_content:
            data_dict['data_quality_check_result'] = ['FAILED']
        output_data = pd.DataFrame(data_dict)
        output_data['data_quality_check_type'] = 'ZIP File Number of Content Check'
        output_data[
            'data_quality_check_description'] = f'Check for zip to have 2 {n_content} files'
        output_data['metadata_type'] = 'healthecon'
        logger.info('finished testing check_zip_n_content')
        return (output_data)
    except Exception as e:
        logger.info('check_zip_n_content functional err: ' + str(e))
        return (pd.DataFrame())


def check_zip_file_naming(dir, correct_file_list):
    try:
        logger.info('testing check_zip_file_naming')
        data_dict = {}
        if set(list(filter(lambda f: f.endswith('.csv'), os.listdir(dir)))) != set(correct_file_list):
            data_dict['data_quality_check_result'] = ['FAILED']
        output_data = pd.DataFrame(data_dict)
        output_data['data_quality_check_type'] = 'File naming check'
        output_data['data_quality_check_description'] = f'wrong naming requirements'
        output_data['metadata_type'] = 'healthecon'
        logger.info('finished testing check_zip_file_naming')
        return output_data
    except Exception as e:
        logger.info('check_zip_n_content functional err: ' + str(e))
        return (pd.DataFrame())


def check_ever_eos(stg_path,
                   hist_path,
                   identifier_col=None,
                   eos_status_col=None,
                   metadata_type=None,
                   metadata_subtype=None):

    try:
        logger.info('testing check_ever_eos')
        hist = get_most_recent_historical_data(hist_path)
        stg = pd.read_csv(stg_path)
        merged_tbl = pd.merge(
            hist,
            stg,
            on=identifier_col,
            how='left')

        merged_tbl = merged_tbl[merged_tbl[f'{eos_status_col}_x'] == 'out']

        # check if out is still out
        merged_tbl = merged_tbl[merged_tbl[f'{eos_status_col}_x']
                                != merged_tbl[f'{eos_status_col}_y']]

        # report ext id if there is difference in starting hecon_status
        merged_tbl['data_quality_check_type'] = f'EOS Status Check'
        merged_tbl['data_quality_check_description'] = f'INFO: {eos_status_col} EOS needs stays EOS'
        merged_tbl['data_quality_check_result'] = 'FAILED'
        merged_tbl['identifier_key'] = identifier_col
        merged_tbl['identifier_value'] = merged_tbl[identifier_col]
        merged_tbl['metadata_type'] = metadata_type
        merged_tbl['metadata_subtype'] = metadata_subtype
        merged_tbl = merged_tbl[['identifier_key',
                                'identifier_value',
                                 'data_quality_check_type',
                                 'data_quality_check_description',
                                 'data_quality_check_result',
                                 'metadata_type',
                                 'metadata_subtype']]
        logger.info('finished testing check_ever_eos')
        return (merged_tbl)
    except Exception as e:
        logger.info('check_ever_eos err: ' + str(e))
        raise ()


def get_most_recent_historical_data(s3path):
    try:
        logger.info('historical data fetch for validation')
        hist = aw.s3.read_csv(s3path, dataset=True)
        hist['parsed_run_date'] = (pd.to_datetime(hist['run_date']).dt.date)
        max_hist = hist[hist['parsed_run_date']
                        == hist['parsed_run_date'].max()]
        logger.info('successful historical data fetch')
        return max_hist
    except Exception as e:
        logger.info('get_most_recent_historical_data err: ' + str(e))
        raise ()


def get_staging_zipfile(bucket, metadata_type):
    try:
        s3client = boto3.client('s3')
        logger.info('fetching zip file from user')
        local_zip_folder = f'/tmp/{metadata_type}'
        local_zip_file_path = f'/tmp/{metadata_type}.zip'
        s3client.download_file(
            Bucket=f'{bucket}',
            Key=f'zip_staging/{metadata_type}.zip',
            Filename=local_zip_file_path
        )
        # Unzip the file
        with zipfile.ZipFile(local_zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(local_zip_folder)
        logger.info('successful zip file fetch')
    except Exception as e:
        logger.info('get_staging_zipfile err: ' + str(e))
        raise ()


def lambda_handler(event, context):
    if 'healthecon.zip' in (event['Records'][0]['s3']['object']['key']):
        INDIVIDUAL_HISTORICAL_S3_URI = f's3://{TARGET_BUCKET_NAME}/metadata/healthecon_individual_data_hist/'
        HOUSEHOLD_HISTORICAL_S3_URI = f's3://{TARGET_BUCKET_NAME}/metadata/healthecon_household_data_hist/'

        get_staging_zipfile(
            bucket=DQ_TEST_BUCKET_NAME,
            metadata_type='healthecon'
        )
        # ZIP FILE SUBMISSION VALIDATION
        output_check_zip_content = check_zip_n_content(
            dir='/tmp/healthecon',
            n_content=2
        )
        output_check_zip_naming = check_zip_file_naming(
            dir='/tmp/healthecon',
            correct_file_list=['individual_data.csv', 'household_data.csv']
        )

        # DATA VALIDATION
        # eos checker for individuals metadata
        output_check_ever_eos_extid = check_ever_eos(
            hist_path= INDIVIDUAL_HISTORICAL_S3_URI,
            stg_path='/tmp/healthecon/individual_data.csv',
            identifier_col='extid',
            eos_status_col='starting_hecon_status',
            metadata_type='healthecon',
            metadata_subtype='individual'
        )

        # eos checker for househld metadat
        output_check_ever_eos_hhid = check_ever_eos(
            hist=HOUSEHOLD_HISTORICAL_S3_URI,
            stg='/tmp/healthecon/household_data.csv',
            identifier_col='hhid',
            eos_status_col='hecon_hh_status',
            metadata_type='healthecon',
            metadata_subtype='household'
        )

        data_list = [
            output_check_zip_content,
            output_check_zip_naming,
            output_check_ever_eos_extid,
            output_check_ever_eos_hhid
        ]

        output_data = pd.DataFrame(pd.concat(data_list))
        aw.s3.to_csv(
            output_data, 
            path=f's3://{DQ_TEST_BUCKET_NAME}/checks/healthecon-dq-test-results.csv'
        )
