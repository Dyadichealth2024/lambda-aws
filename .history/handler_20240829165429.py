import json
import logging
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-west-2')

# Handler to register a user
def register(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        body = json.loads(event['body'])
        user_id = body['user_id']
        name = body['name']
        
        # Storing user in DynamoDB
        response = dynamodb.put_item(
            TableName='Users',
            Item={
                'user_id': {'S': user_id},
                'name': {'S': name}
            }
        )
        logging.info("User registered: %s", json.dumps(response))
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"message": "User registered successfully"})
        }
    except ClientError as e:
        logging.error("DynamoDB error: %s", e.response['Error']['Message'])
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": "DynamoDB error: " + e.response['Error']['Message']})
        }
    except Exception as e:
        logging.error("Exception: %s", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": "Internal server error: " + str(e)})
        }

# Handler to calculate lung health
def calculate_lung_health_route(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        body = json.loads(event['body'])
        age = body['age']
        smoking_history = body['smoking_history']
        
        # Example calculation (simplified)
        lung_health_score = max(0, 100 - (age / 2) - (smoking_history * 10))
        
        logging.info("Lung health score calculated: %d", lung_health_score)
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"lung_health_score": lung_health_score})
        }
    except Exception as e:
        logging.error("Exception: %s", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": "Internal server error: " + str(e)})
        }

# Handler to get training points
# Example function with CORS headers included
import json
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('TrainingPoints')

def get_training_points(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        type_param = event['queryStringParameters'].get('type', 'default')
        category_param = event['queryStringParameters'].get('category', 'default')

        if not type_param:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing required parameter: type')
            }

        # Query DynamoDB with the parameters
        if category_param:
            response = table.query(
                KeyConditionExpression=Key('Type').eq(type_param) & Key('Category').eq(category_param)
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('Type').eq(type_param)
            )

        items = response.get('Items', [])

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': json.dumps(items)
        }
        
    except Exception as e:
        logging.error("Exception: %s", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': json.dumps({"error": "Internal server error: " + str(e)})
        }
# Example function to test the setup (optional)
def hello(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps({"message": "Hello, World!"})
    }
