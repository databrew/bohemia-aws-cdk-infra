import urllib3 
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
http = urllib3.PoolManager() 

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
    logger.info('Fetch event from SQS Queue')
    payload = event['Records'][0]['body']
    url = get_slack_webhook_url('SLACK_WEBHOOK_URL')
    resp = http.request('POST', url, body=payload)