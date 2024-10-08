import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dietreport')

def lambda_handler(event, context):
    try:
        # Get user input from the body of the request
        body = json.loads(event['body'])  # Assuming you are sending a JSON payload
        veggies = body.get('veggies', 0)  # Provide default value if not found
        protein = body.get('protein', 0)
        grains = body.get('grains', 0)
        nutsSeeds = body.get('nutsSeeds', 0)
        dairy = body.get('dairy', 0)
        fruits = body.get('fruits', 0)
        
        # Define the recommended values for each food group
        recommended_values = {
            "vegetables": 3,
            "protein": 2,
            "grains": 5,
            "nutsSeeds": 1,
            "dairy": 2,
            "fruits": 2
        }
        
        # Function to determine intake category (below, at, above)
        def determine_category(foodGroup, servings):
            if servings < recommended_values[foodGroup]:
                return "below"
            elif servings == recommended_values[foodGroup]:
                return "at"
            else:
                return "above"
        
        # Prepare recommendations
        food_groups = ["vegetables", "protein", "grains", "nutsSeeds", "dairy", "fruits"]
        user_intake = [veggies, protein, grains, nutsSeeds, dairy, fruits]
        recommendations = {}

        for i, group in enumerate(food_groups):
            intake_category = determine_category(group, user_intake[i])
            report_id = f"{group}-{intake_category}"  # e.g., "veg-below"
            
            try:
                # Query DynamoDB for the recommendation based on reportId
                response = table.query(
                    KeyConditionExpression=Key('reportId').eq(report_id)
                )
                
                # Get the message from DynamoDB
                items = response.get('Items', [])
                if items:
                    recommendations[group] = items[0].get('recommendation', 'No recommendation available')
                else:
                    recommendations[group] = "No recommendation available"
            except Exception as e:
                recommendations[group] = f"Error fetching recommendation: {str(e)}"
        
        # Return the recommendations with CORS headers
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Change this to your frontend domain in production
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(recommendations)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
