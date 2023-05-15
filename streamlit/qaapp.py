
import streamlit as st
import boto3
import json

# Set up AWS Lambda client
lambda_client = boto3.client('lambda')

# Set up Streamlit interface
st.title("Chat with AI Assistant about recent meetings")

user_question = st.text_input("Ask something:")

# Initialize or get chat log from session state
if 'chat_log' not in st.session_state:
    st.session_state['chat_log'] = []

if st.button("Send"):
    # Prepare the payload for the Lambda function
    payload = {
        "userId": "test_user",
        "question": user_question,
    }

    # Invoke the Lambda function
    response = lambda_client.invoke(
        FunctionName="Summary_QA_Lambda",  # Replace with your actual function name
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )

    # Parse the response from the Lambda function
    response_payload = json.load(response['Payload'])
    assistant_message = response_payload['answer']

    # Update the chat log
    st.session_state['chat_log'].append("You: " + user_question)
    st.session_state['chat_log'].append("AI: " + assistant_message)

    # Display the chat log
    for message in st.session_state['chat_log']:
        st.write(message)


