import streamlit as st
import boto3
import json

# Set up AWS Lambda client
lambda_client = boto3.client('lambda')

# Set up Streamlit interface
st.title("Chat with AI Assistant")

user_input = st.text_input("Ask something:")

if st.button("Send"):
    # Prepare the payload for the Lambda function
    payload = {
        "userId": "test_user",
        "inputTranscript": user_input,
    }

    # Invoke the Lambda function
    response = lambda_client.invoke(
        FunctionName="Summary_QA_Lambda",  # Replace with your actual function name
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )

    # Parse the response from the Lambda function
    response_payload = json.load(response['Payload'])
    assistant_message = response_payload["dialogAction"]["message"]["content"]

    # Display the assistant's message
    st.write(assistant_message)
