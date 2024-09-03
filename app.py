import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def calculate_lung_health(age, gender, pulse, breathHoldTime):
    pulse = float(pulse)
    breathHoldTime = float(breathHoldTime)
    score = (breathHoldTime / pulse) * 100
    return score

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

        score = calculate_lung_health(age, gender, pulse, breathHoldTime)
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
