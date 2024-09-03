def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))  # Log the incoming event

        relationship_type = event.get('queryStringParameters', {}).get('type')
        category = event.get('queryStringParameters', {}).get('category')
        
        if not relationship_type:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing required parameter: type')
            }
        
        if category:
            response = table.query(
                KeyConditionExpression=Key('Type').eq(relationship_type) & Key('Category').eq(category)
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('Type').eq(relationship_type)
            )
        
       items = response.get('Items', [])
       if not isinstance(items, list):
           items = [items]

        # Ensure the response is always an array
        if not isinstance(items, list):
            items = [items]

        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the exception
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error fetching data: {str(e)}')
        }
