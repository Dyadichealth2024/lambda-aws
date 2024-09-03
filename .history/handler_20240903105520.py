import json
import logging
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize DynamoDB client and resource
dynamodb_client = boto3.client('dynamodb', region_name='us-west-2')
dynamodb_resource = boto3.resource('dynamodb', region_name='us-west-2')
training_points_table = dynamodb_resource.Table('landingnewsletter')

# Initialize SES client
ses_client = boto3.client('ses', region_name='us-west-2')

# Handler to register a user
# def register(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        body = json.loads(event['body'])
        user_id = body['user_id']
        name = body['name']

        # Storing user in DynamoDB
        response = dynamodb_client.put_item(
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

# # Handler to calculate lung health
# def calculate_lung_health_route(event, context):
#     logging.debug("Received event: %s", json.dumps(event))
#     try:
#         body = json.loads(event['body'])
#         age = body['age']
#         smoking_history = body['smoking_history']

#         # Example calculation (simplified)
#         lung_health_score = max(0, 100 - (age / 2) - (smoking_history * 10))

#         logging.info("Lung health score calculated: %d", lung_health_score)

#         return {
#             "statusCode": 200,
#             "headers": {
#                 "Access-Control-Allow-Origin": "*",
#                 "Access-Control-Allow-Headers": "Content-Type",
#                 "Access-Control-Allow-Methods": "OPTIONS,POST"
#             },
#             "body": json.dumps({"lung_health_score": lung_health_score})
#         }
#     except Exception as e:
#         logging.error("Exception: %s", str(e))
#         return {
#             "statusCode": 500,
#             "headers": {
#                 "Access-Control-Allow-Origin": "*",
#                 "Access-Control-Allow-Headers": "Content-Type",
#                 "Access-Control-Allow-Methods": "OPTIONS,POST"
#             },
#             "body": json.dumps({"error": "Internal server error: " + str(e)})
#         }

# Handler to get training points
# def get_training_points(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        relationship_type = event.get('queryStringParameters', {}).get('type')
        category = event.get('queryStringParameters', {}).get('category')

        if not relationship_type:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                'body': json.dumps('Missing required parameter: type')
            }

        if category:
            response = training_points_table.query(
                KeyConditionExpression=Key('Type').eq(relationship_type) & Key('Category').eq(category)
            )
        else:
            response = training_points_table.query(
                KeyConditionExpression=Key('Type').eq(relationship_type)
            )

        items = response.get('Items', [])
        if not isinstance(items, list):
            items = [items]

        logging.debug(f"Fetched items: {items}")

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

# Handler to subscribe a user
def subscribe(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        body = json.loads(event['body'])
        email = body['email']
        first_name = body['firstName']
        last_name = body['lastName']

        # Save to DynamoDB
        response = newsletter_table.put_item(
            Item={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'verification_status': 'Pending'
            }
        )
        logging.info("User subscribed: %s", json.dumps(response))

        # Send verification email
        verify_link = f"https://your-frontend-url.com/verify?email={email}"
        subject = "Please verify your subscription"
        body_text = f"Hello {first_name},\nPlease verify your email by clicking the link below:\n{verify_link}"
        body_html = f"<html><body><h3>Hello {first_name},</h3><p>Please verify your email by clicking the link below:</p><a href='{verify_link}'>Verify Email</a></body></html>"

        ses_response = ses_client.send_email(
            Source='info@dyadic.health',  # Ensure this email is verified in SES
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )
        logging.info("Verification email sent: %s", ses_response)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"message": "Verification email sent"})
        }
    except ClientError as e:
        logging.error("Client error: %s", e.response['Error']['Message'])
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

# Handler to verify a user
def verify(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        email = event['queryStringParameters']['email']

        response = newsletter_table.update_item(
            Key={'email': email},
            UpdateExpression="set verification_status = :s",
            ExpressionAttributeValues={':s': 'Verified'}
        )
        logging.info("Verification status updated: %s", json.dumps(response))

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,GET"
            },
            "body": json.dumps({"message": "Email verified successfully"})
        }
    except Exception as e:
        logging.error("Exception: %s", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,GET"
            },
            "body": json.dumps({"error": "Internal server error: " + str(e)})
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