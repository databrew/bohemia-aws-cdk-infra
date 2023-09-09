import boto3
import os

def get_sf_history(event):
    client = boto3.client('stepfunctions') # Connect to Step Functions Client
    lastexecutionarn = event['detail']['executionArn']
    statemachinename = lastexecutionarn.split(':')[-2]
    response = client.get_execution_history(
    executionArn=lastexecutionarn, maxResults=300)

    # initial temp storage
    name = []
    event_type = []
    start_time = ''
    end_time = ''
    curr_state = ''

    # parse through events
    for event in response['events']:
        if 'stateEnteredEventDetails' in event.keys():
            curr_state = event['stateEnteredEventDetails']['name']
        if event['type'] == 'ExecutionStarted':
            start_time = event['timestamp'].strftime('%d-%m-%Y %H:%M:%S') # Get the start time for the step functions execution
        if event['type'] in 'TaskSucceeded':
            name.append(curr_state) # Get the name of the task run
            event_type.append('Succeeded') # Get the id of the previous event
        if event['type'] in 'TaskFailed':
            name.append(curr_state) # Get the name of the task run
            event_type.append('Failed') # Get the id of the previous event
        if event['type'] in ['ExecutionSucceeded', 'ExecutionFailed']:
            end_time = event['timestamp'].strftime('%d-%m-%Y %H:%M:%S') # Get the end time for the step functions execution

    return statemachinename, lastexecutionarn, start_time, name, end_time, event_type


def build_slack_message(name, event_type, statemachinename, lastexecutionarn, aws_region, start_time, end_time):
    text = ''
    block = ''
    image_url = 'https://api.slack.com/img/blocks/bkb_template_images/approvalsNewDevice.png'
    alt_tex_image = 'standard image'
    for name_i, event_type_i in zip(name,event_type):
        if 'Succeeded' in event_type_i:
            result = ':white_check_mark:'
            text = f"*Step:* {name_i} - *Status:* {event_type_i} {result}"
        elif 'Failed' in event_type_i:
            result = ':x:'
            text = f"*Step:* {name_i} - *Status:* {event_type_i} {result}"
        else:
            text = f"*Step:* {name_i} - *Status:* {event_type_i}"
        block += f"""
            {{
                "type": "section",
                "text": {{
                    "type": "mrkdwn",
                    "text": "{text}"
                }}
            }}, """
        message = f"""
            {{
                "blocks": [
                    {{
                        "type": "section",
                        "text": {{
                            "type": "mrkdwn",
                            "text": "*{statemachinename} Failure Report*\n\n*Execution Arn:* {lastexecutionarn}"
                        }},
                        "accessory": {{
                            "type": "image",
                            "image_url": "{image_url}",
                            "alt_text": "{alt_tex_image}"
                        }}
                    }},
                    {{
                        "type": "section",
                        "text": {{
                            "type": "mrkdwn",
                            "text": "*Start time:* {start_time}"
                        }}
                    }},
                    {{
                        "type": "section",
                        "text": {{
                            "type": "mrkdwn",
                            "text": "*End time:* {end_time}"
                        }}
                    }},
                    {{
                        "type": "divider"
                    }},
                    {block}
                    {{
                        "type": "divider"
                    }},
                    {{
                        "type": "actions",
                        "elements": [
                            {{
                                "type": "button",
                                "text": {{
                                    "type": "plain_text",
                                    "text": "State machine execution detail",
                                    "emoji": true
                                }},
                                "value": "lastexecutionarn",
                                "url": "https://console.aws.amazon.com/states/home?region={aws_region}#/executions/details/{lastexecutionarn}"
                            }}
                        ]
                    }}
                ]
            }}"""
    return message


def send_message_to_sqs(aws_account_id, aws_region, block):
    sqs = boto3.client('sqs')
    queue_url = os.getenv('QUEUE_URL')
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=2,
        MessageBody=(block))
        

def lambda_handler(event, context):
    # Client info
    aws_region = 'us-east-1'
    aws_account_id = '381386504386'
    statemachinename, lastexecutionarn, start_time, name, end_time, event_type = get_sf_history(event)
    message = build_slack_message(name, 
                                event_type, 
                                statemachinename, 
                                lastexecutionarn, 
                                aws_region, 
                                start_time, 
                                end_time)
    send_message_to_sqs(aws_account_id, aws_region, message)