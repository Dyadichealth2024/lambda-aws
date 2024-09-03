import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TrainingPoints')

def lambda_handler(event, context):
    try:
        # Extract the 'type' and 'category' from query string parameters
        relationship_type = event.get('queryStringParameters', {}).get('type')
        category = event.get('queryStringParameters', {}).get('category')
        
        if not relationship_type:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing required parameter: type')
            }
        
        # Query DynamoDB based on type and optionally category
        if category:
            response = table.query(
                KeyConditionExpression=Key('Type').eq(relationship_type) & Key('Category').eq(category)
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('Type').eq(relationship_type)
            )
        
        items = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error fetching data: {str(e)}')
        }
