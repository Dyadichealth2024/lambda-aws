import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('QuestionsTable')  # Updated table name

def decimal_to_native_type(obj):
    """Convert DynamoDB Decimal types to native Python types."""
    if isinstance(obj, list):
        return [decimal_to_native_type(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native_type(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 else int(obj)
    return obj

def fetch_questions(event, context):
    try:
        # Extract the relationship type from query string parameters
        query_params = event.get('queryStringParameters', {})
        relationship_type = query_params.get('relationshipType', None)
        
        if not relationship_type:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing relationshipType query parameter'}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  # Enable CORS
                }
            }

        # Query DynamoDB to get questions based on the relationshipType
        response = table.query(
            KeyConditionExpression=Key('RelationshipType').eq(relationship_type)
        )
        
        items = response.get('Items', [])
        native_items = decimal_to_native_type(items)

        return {
            'statusCode': 200,
            'body': json.dumps(native_items),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Enable CORS
            }
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': e.response['Error']['Message']}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Enable CORS
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Enable CORS
            }
        }
