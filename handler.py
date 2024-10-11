import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')

# Initialize SES
ses_client = boto3.client('ses', region_name='us-west-2')  # Replace with your actual SES region

# Table for storing subscription data
newsletter_table = dynamodb.Table('landingnewsletter')

# Table for storing registration data
register_table = dynamodb.Table('Register_Data')  # Replace with your actual table name

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

# =======================|| Subscribe User Function ||========================

def subscribe_user(event, context):
    try:
        # Parse the input data from the event
        body = json.loads(event['body'])
        email = body.get('email')
        first_name = body.get('firstName')

        # Check if required fields are present
        if not email or not first_name:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'message': 'Email and First Name are required!'})
            }

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
                'Access-Control-Allow-Origin': '*',
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
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

# =======================|| Send Email Function Using SES ||========================

def send_email(email, first_name):
    sender_email = "info@dyadic.health"  # Replace with your verified sender email
    subject = "Subscription Confirmation"
    body_text = f"Hello {first_name},\n\nThank you for subscribing to our newsletter!"
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>Hello {first_name},</h1>
      <p>Thank you for subscribing to our newsletter!</p>
    </body>
    </html>
    """

    try:
        # Use AWS SES to send the email
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [email],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
            },
            Source=sender_email,
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending email: {e}")
