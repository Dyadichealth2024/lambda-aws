import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def calculate_bmi(height, weight):
    """
    Function to calculate BMI based on height (in cm) and weight (in kg).
    """
    try:
        height_in_meters = height / 100  # Convert height from cm to meters
        bmi_value = weight / (height_in_meters * height_in_meters)
        return round(bmi_value, 2)  # Return BMI rounded to 2 decimal places
    except Exception as e:
        logging.error(f"Error calculating BMI: {str(e)}")
        return None

def get_bmi_category(bmi):
    """
    Function to categorize BMI into points and health ranges.
    """
    if bmi < 18.5:
        return {
            "bmi": bmi,
            "category": "underweight",
            "message": "You are underweight. You might need to increase your calorie intake to reach a healthier weight.",
            "points": 1  # Point assignment for underweight
        }
    elif 18.5 <= bmi < 24.9:
        return {
            "bmi": bmi,
            "category": "normal",
            "message": "You are in the normal BMI range. Keep up the good work maintaining a balanced diet and regular exercise.",
            "points": 2  # Point assignment for normal BMI
        }
    elif 25 <= bmi < 29.9:
        return {
            "bmi": bmi,
            "category": "overweight",
            "message": "You are overweight. Incorporating more physical activity and a balanced diet can help reach a healthier weight.",
            "points": 3  # Point assignment for overweight
        }
    else:
        return {
            "bmi": bmi,
            "category": "obese",
            "message": "You are in the obese range. It might be beneficial to consult with a healthcare provider for personalized advice.",
            "points": 4  # Point assignment for obese
        }

def lambda_handler(event, context):
    """
    Lambda function handler to process the event and calculate BMI.
    Expects a POST request with `height` and `weight` in the body.
    """
    logging.debug("Received event: %s", json.dumps(event))

    try:
        # Parse request body
        body = json.loads(event['body'])
        logging.debug("Parsed body: %s", json.dumps(body))

        # Extract height and weight from the request body
        height = body.get('height')
        weight = body.get('weight')

        # Validate that both height and weight are provided
        if None in (height, weight):
            logging.error("Validation failed: missing height or weight")
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({"error": "Invalid input: height and weight are required"})
            }

        # Convert height and weight to float for calculation
        height = float(height)
        weight = float(weight)

        # Calculate BMI
        bmi = calculate_bmi(height, weight)
        if bmi is None:
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({"error": "Failed to calculate BMI"})
            }

        # Get BMI category and points
        bmi_result = get_bmi_category(bmi)

        # Return the BMI, category, message, and points as a response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps(bmi_result)
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
