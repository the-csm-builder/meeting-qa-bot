import openai
import boto3
import json
from boto3.dynamodb.conditions import Key
import os

openai.api_key = os.environ["OPENAI_API_KEY"]
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Assume we have a DynamoDB table 'ConversationHistory' with a primary key 'userID'
table = dynamodb.Table('ConversationHistory')

def lambda_handler(event, context):
    # Get the summary from S3
    file_obj = s3.get_object(Bucket='transcribed-data-outbound', Key='summary.txt')
    summary_string = file_obj["Body"].read().decode('utf-8')

    # Get the user's question from the event
    user_question = event["question"]

    # Get the user's ID from the event
    user_id = event['userId']

    # Retrieve conversation history from DynamoDB
    response = table.query(
        KeyConditionExpression=Key('userID').eq(user_id)
    )

    # If there is no existing history, initialize it with the summary
    if response['Count'] == 0:
        conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"This is the summary of the meeting: {summary_string}"},
        ]
    else:
        # If there is existing history, retrieve it and convert it from a JSON string
        conversation_history = json.loads(response['Items'][0]['conversationHistory'])

    # Add the user's question to the conversation history
    conversation_history.append({"role": "user", "content": user_question})

    # Generate a response using the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )

    # Get the assistant's message from the response
    answer = response['choices'][0]['message']['content']

    # Add the assistant's answer to the conversation history
    conversation_history.append({"role": "assistant", "content": answer})

    # Update the conversation history in DynamoDB
    table.put_item(
        Item={
            'userID': user_id,
            'conversationHistory': json.dumps(conversation_history)  # Store it as a JSON string
        }
    )

    # Return the assistant's answer
    return {"answer": answer}
