import json
import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def register(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        body = json.loads(event['body'])
        logging.debug("Parsed body: %s", json.dumps(body))

        first_name = body.get('firstName')
        last_name = body.get('lastName')
        company_name = body.get('companyName')
        email = body.get('email')
        password = body.get('password')  # Ideally, hash the password before storing it

        if None in (first_name, last_name, company_name, email, password):
            logging.error("Validation failed, missing fields")
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({"error": "Invalid input"})
            }

        # Save user to DynamoDB
        table.put_item(
            Item={
                'email': email,
                'firstName': first_name,
                'lastName': last_name,
                'companyName': company_name,
                'password': password,
            }
        )
        logging.info("User registered successfully: %s", email)

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
        logging.error("DynamoDB ClientError: %s", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": "Internal server error: " + str(e)})
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

def calculate_lung_health_route(event, context):
    logging.debug("Received event: %s", json.dumps(event))
    try:
        body = json.loads(event['body'])
        logging.debug("Parsed body: %s", json.dumps(body))

        age = body.get('age')
        gender = body.get('gender')
        pulse = body.get('pulse')
        breathHoldTime = body.get('breathHoldTime')

        if None in (age, gender, pulse, breathHoldTime):
            logging.error("Validation failed, missing fields")
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({"error": "Invalid input"})
            }

        score = (float(breathHoldTime) / float(pulse)) * 100
        logging.info("Lung health score calculated: %f", score)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"score": score})
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

def hello(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello, World!"})
    }
