import json
import boto3
import jwt  # Add this for JWT creation
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')

# Table for storing subscription data
newsletter_table = dynamodb.Table('landingnewsletter')

# Table for storing registration data
register_table = dynamodb.Table('Register_Data')  # Replace with your actual table name

# Secret key for JWT signing (Store this securely in a secret manager or environment variable)
SECRET_KEY = "your_secret_key"  # Replace this with a secure key

# =======================|| JWT Creation and Validation Functions ||========================

def create_jwt_token(email, expiration_minutes=60):
    """Generate JWT Token with expiration"""
    payload = {
        'email': email,
        'exp': datetime.utcnow() + timedelta(minutes=expiration_minutes)  # Token expires in 60 minutes by default
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_jwt_token(token):
    """Decode JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload  # Returns the decoded payload if token is valid
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

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

        # Generate a JWT token for the user
        token = create_jwt_token(email)

        # Return success response with CORS headers and JWT token
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'message': 'User registered successfully!', 'token': token})
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

# =======================|| Subscribe User Function with Token Validation ||========================

def subscribe_user(event, context):
    try:
        # Parse the input data from the event
        body = json.loads(event['body'])
        token = body.get('token')  # Token provided by the client in request body
        first_name = body.get('firstName')

        # Validate JWT token
        decoded_token = decode_jwt_token(token)
        if decoded_token is None:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',  # Allow all origins
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'message': 'Unauthorized: Invalid or expired token.'})
            }

        email = decoded_token['email']  # Extract email from the decoded token

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
