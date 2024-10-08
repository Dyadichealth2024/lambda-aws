import json
import boto3
from boto3.dynamodb.conditions import Key
import os

# Initialize the DynamoDB resource
TABLE_NAME = 'posturereport'
TABLE_NAME = os.environ.get('posturereport')

if not TABLE_NAME:
    raise ValueError("DynamoDB table name not set. Ensure 'posturereport' environment variable is configured.")



def get_posture_report(posture_id):
    table = dynamodb.Table(TABLE_NAME)

    # Query the DynamoDB table for the selected posture report
    response = table.query(
        KeyConditionExpression=Key('posture_id').eq(posture_id)
    )

    # Assuming the report is in the 'report' attribute
    if 'Items' in response and len(response['Items']) > 0:
        return response['Items'][0]['report']
    else:
        return None

def lambda_handler(event, context):
    try:
        posture_id = event['pathParameters']['postureId']
    except KeyError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Enable CORS
            },
            'body': json.dumps({'error': 'Missing posture ID'})
        }

    # Get the posture report from DynamoDB
    report = get_posture_report(posture_id)

    if not report:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Enable CORS
            },
            'body': json.dumps({'error': 'Posture report not found'})
        }

    # Return the report as a response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Enable CORS
        },
        'body': json.dumps({'report': report})
    }
