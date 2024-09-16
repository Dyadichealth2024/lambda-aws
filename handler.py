import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')

# Table for storing subscription data
newsletter_table = dynamodb.Table('landingnewsletter')

# Table for storing registration data
register_table = dynamodb.Table('Register_Data')  # Replace with your actual table name

# =======================|| Subscribe User Function ||========================

def subscribe_user(event, context):
    try:
        # Parse the input data from the event
        body = json.loads(event['body'])
        email = body.get('email')
        first_name = body.get('firstName')

        # Store the subscription data in the DynamoDB table
        newsletter_table.put_item(
            Item={
                'email': email,
                'firstName': first_name,
                'subscribed_at': str(datetime.utcnow())  # Add a timestamp for the subscription
            }
        )

        # Send subscription confirmation email
        send_email(email, first_name)

        # Return success response with CORS headers
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Allow all origins
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'message': 'Subscription successful!'})
        }

    except ClientError as e:
        # Log the error and return error response with CORS headers
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Ensure CORS headers are included in error response
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

# =======================|| Register User Function ||========================

def register_user(event, context):
    try:
        # Parse the input data from the event
        body = json.loads(event['body'])
        email = body.get('email')
        first_name = body.get('firstName')
        last_name = body.get('lastName')
        password = body.get('password')  # Ideally, hash this password

        # Check if any required field is missing
        if not email or not first_name or not last_name or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',  
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'message': 'All fields are required!'})
            }

        # Store the registration data in the DynamoDB table
        register_table.put_item(
            Item={
                'email': email,
                'firstName': first_name,
                'lastName': last_name,
                'password': password,  # This should be hashed before saving
                'created_at': str(datetime.utcnow())  # Add a timestamp of the registration
            }
        )

        # Return success response with CORS headers
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'message': 'User registered successfully!'})
        }

    except ClientError as e:
        # Log the error and return error response with CORS headers
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

# =======================|| Email Sending Function ||========================

def send_email(email, first_name):
    SUBJECT = "Thank you for subscribing to our newsletter!"
    BODY_TEXT = f"Hello {first_name},\n\nThank you for subscribing to our newsletter. We will keep you updated!"
    SENDER = "info@dyadic.health"  # This should be a verified email in SES
    RECIPIENT = email

    ses = boto3.client('ses')  # Initialize SES client

    try:
        # Attempt to send the email via SES
        response = ses.send_email(
            Source=SENDER,
            Destination={
                'ToAddresses': [RECIPIENT],
            },
            Message={
                'Subject': {'Data': SUBJECT},
                'Body': {
                    'Text': {'Data': BODY_TEXT},
                },
            },
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Failed to send email. Error: {e}")
        raise e
