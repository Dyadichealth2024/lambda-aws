import boto3
import csv

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')  # Use your correct region

# Update the table name to 'QuestionsTable' as discussed
questions_table = dynamodb.Table('QuestionsTable')

# Update the file path to the uploaded CSV file
file_path = 'C:/Users/Praveen/Desktop/lambda/lambda-aws/Updated_Relationship_Questions_and_Feedback_with_Second_Person_Narration.csv'

# Open the CSV file
with open(file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    
    batch_size = 25  # DynamoDB batch limit
    items_batch = []
    question_id_counter = 1  # Initialize a counter for QuestionID
    
    for row in csv_reader:
        # Generate a unique QuestionID using a counter
        question_id = f"Q{question_id_counter}"
        question_id_counter += 1
        
        # Prepare the item with the appropriate attributes
        item = {
            'RelationshipType': row['Relationship Type'],
            'QuestionID': question_id,  # Generated unique Question ID
            'QuestionText': row['Question'],  # Store the question text
            'AnswerOptions': [1, 2, 3, 4, 5],  # Assuming fixed scale answers from 1 to 5
            'Category': 'General',  # No category provided, defaulting to 'General'
            'FinalOutput': row['Final out put']  # Store the final output text
        }
        items_batch.append(item)
        
        # If the batch is full, write to DynamoDB and clear the batch
        if len(items_batch) == batch_size:
            with questions_table.batch_writer() as batch:
                for item in items_batch:
                    batch.put_item(Item=item)
            items_batch = []  # Clear the batch after writing
    
    # Write remaining items in the last batch
    if items_batch:
        with questions_table.batch_writer() as batch:
            for item in items_batch:
                batch.put_item(Item=item)

print("Data import completed successfully.")
