import json

# Function to generate personalized feedback based on sleep, workout recovery, and relaxation
def generate_personalized_report(sleep, workoutRecovery, relaxation):
    feedback = ""

    # Sleep feedback
    if sleep < 7:
        feedback += "You should try to sleep more. Aim for at least 7-8 hours of sleep per night.\n"
    elif sleep > 9:
        feedback += "You are sleeping a lot! Make sure that long sleep doesn’t leave you feeling sluggish.\n"
    else:
        feedback += "Your sleep duration is perfect. Keep maintaining 7-9 hours of sleep per night.\n"

    # Workout recovery feedback
    if workoutRecovery < 30:
        feedback += "Consider spending more time on workout recovery. 30-60 minutes of post-workout recovery is ideal.\n"
    else:
        feedback += "You are spending enough time on workout recovery. Great job!\n"

    # Relaxation feedback
    if relaxation < 30:
        feedback += "Try to spend at least 30 minutes a day on relaxation or meditation to reduce stress.\n"
    else:
        feedback += "Your relaxation time is sufficient. Keep it up to maintain good mental health!\n"

    return feedback

def lambda_handler(event, context):
    # Parse the request body
    body = json.loads(event['body'])
    sleep = body.get('sleep', 0)
    workoutRecovery = body.get('workoutRecovery', 0)
    relaxation = body.get('relaxation', 0)

    # Generate the personalized feedback
    personalized_feedback = generate_personalized_report(sleep, workoutRecovery, relaxation)

    # Generate a recovery report based on the input data and personalized feedback
    report = {
        "message": "Your Recovery Report",
        "data": {
            "sleep": f"You slept for {sleep} hours.",
            "workoutRecovery": f"You spent {workoutRecovery} minutes on workout recovery.",
            "relaxation": f"You had {relaxation} minutes of relaxation/meditation.",
            "personalizedFeedback": personalized_feedback  # Add personalized feedback to the report
        }
    }

    # Return the report in JSON format
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(report)
    }
