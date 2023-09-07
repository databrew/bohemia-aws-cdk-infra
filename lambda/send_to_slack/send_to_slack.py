import urllib3 
import json
http = urllib3.PoolManager() 

SLACK_URL = "https://hooks.slack.com/services/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"

def lambda_handler(event, context): 
    payload = event['Records'][0]['body']
    url = SLACK_URL
    resp = http.request(
        'POST', url, body=payload)