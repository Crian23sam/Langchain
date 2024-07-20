import os
import base64
import requests
import streamlit as st
#from apikey import groqcloud_apikey, stability_ai_apikey
from groq import Groq
from langchain.memory import ConversationBufferMemory

# Set your API keys
GROQ_API_KEY = "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"
STABILITY_AI_API_KEY = "sk-M2z8OBnk94qnu6cRALXInGU8bPHcKeCPEF5ufkTbVsSSwgha"

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Streamlit App Framework
st.title('💬 Chat with SmartBot')

# Memory for conversation history
conversation_memory = ConversationBufferMemory(memory_key='chat_history', input_key='input', output_key='output')

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Define function to get chatbot response
def get_chatbot_response(user_message, chat_history):
    messages = chat_history + [{"role": "user", "content": user_message}]
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Function to generate image using Stability AI
def generate_image(prompt):
    stability_ai_api_key = os.environ.get(STABILITY_AI_API_KEY)
    url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    headers = {
        "authorization": f"Bearer {stability_ai_api_key}",
        "accept": "image/*"
    }
    data = {
        "prompt": prompt,
        "output_format": "webp",
    }
    response = requests.post(url, headers=headers, files={"none": ''}, data=data)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(str(response.json()))

# Input form for user to type messages
with st.form(key='input_form'):
    user_input = st.text_input('You:', key='input_field')
    submit_button = st.form_submit_button(label='Send')

if submit_button:
    if user_input:
        # Get the chat history from session state
        chat_history = st.session_state['chat_history']

        # Get the chatbot response
        bot_response = get_chatbot_response(user_input, chat_history)

        # Update the chat history
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": bot_response})
        st.session_state['chat_history'] = chat_history

# Button to generate image
if st.button('Generate Image'):
    if user_input:
        try:
            image_result = generate_image(user_input)
            image_base64 = base64.b64encode(image_result).decode("utf-8")
            st.image(f"data:image/webp;base64,{image_base64}", use_column_width=True)
        except Exception as e:
            st.error(f"Error generating image: {e}")

# Display chat history
for i, message in enumerate(st.session_state['chat_history']):
    if message['role'] == 'user':
        st.text_area('You:', value=message['content'], height=50, max_chars=None, key=f"user_{i}")
    else:
        st.text_area('SmartBot:', value=message['content'], height=50, max_chars=None, key=f"bot_{i}")
