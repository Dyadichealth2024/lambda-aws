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
newsletter_table = dynamodb_resource.Table('landingnewsletter')

# Initialize SES client
ses_client = boto3.client('ses', region_name='us-west-2')

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
        logging.info("Verification email sent: %s", json.dumps(ses_response))

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
        logging.error("DynamoDB/SES error: %s", e.response['Error']['Message'])
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": "DynamoDB/SES error: " + e.response['Error']['Message']})
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
            Key={'email': {'S': email}},
            UpdateExpression="set verification_status = :s",
            ExpressionAttributeValues={':s': {'S': 'Verified'}}
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
