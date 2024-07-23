import os
from dotenv import load_dotenv
import streamlit as st
from googleapiclient.discovery import build
from groq import Groq
from langchain.memory import ConversationBufferMemory
from textblob import TextBlob
from gtts import gTTS
from io import BytesIO
from datetime import date

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
groqcloud_apikey = os.getenv('GROQCLOUD_API_KEY')
youtube_api_key = os.getenv('YOUTUBE_API_KEY')

os.environ['GROQ_API_KEY'] = groqcloud_apikey

# Initialize Groq Client
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    # Attempt to make a simple request to check if the API key is valid
    _ = client.chat.completions.create(
        messages=[{"role": "system", "content": "hello"}],
        model="llama3-8b-8192",
    )
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    st.stop()

# Initialize YouTube API Client
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

# Streamlit App Framework
st.set_page_config(
    page_title="Martial Arts & Self-Defense",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('🥋 Martial Arts & Self-Defense')

# Sidebar Configuration
st.sidebar.title("Settings")
theme = st.sidebar.radio("Choose Theme", ["Light", "Dark", "Colorful"])
if theme == "Dark":
    st.markdown(
        """
        <style>
        .reportview-container {
            background: #333;
            color: white;
        }
        .sidebar .sidebar-content {
            background: #444;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
elif theme == "Colorful":
    st.markdown(
        """
        <style>
        .reportview-container {
            background: linear-gradient(135deg, #ffcc00, #ff6666);
            color: #000;
        }
        .sidebar .sidebar-content {
            background: #ffeebb;
            color: #000;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Welcome Message
st.write("Welcome to the Martial Arts & Self-Defense App! Type your questions below to learn about techniques, tips, and exercises.")

# Memory for conversation history
conversation_memory = ConversationBufferMemory(memory_key='chat_history', input_key='input', output_key='output')

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to reset chat history
def reset_chat():
    st.session_state['chat_history'] = []

# Add a button to start a new chat
if st.sidebar.button('Start New Chat'):
    reset_chat()

# Define function to get chatbot response
def get_chatbot_response(user_message, chat_history):
    try:
        messages = chat_history + [{"role": "user", "content": user_message}]
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting response from SmartBot: {e}")
        return "Sorry, I am having trouble understanding you right now."

# Function for Text-to-Speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    return mp3_fp

# Basic Emotion Analysis using TextBlob
def analyze_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

# Function to get martial arts video from YouTube
def get_martial_arts_video(topic):
    try:
        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=topic + " martial arts",
            type="video"
        )
        response = request.execute()
        video_id = response['items'][0]['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url
    except Exception as e:
        st.error(f"Error fetching video from YouTube: {e}")
        return "https://www.youtube.com/results?search_query=martial+arts"

# Function for quiz
def martial_arts_quiz():
    questions = {
        "What part of the body is used in a front kick?": ["Shin", "Knee", "Ball of the foot", "Heel"],
        "Which martial art is known for its ground fighting techniques?": ["Karate", "Taekwondo", "Brazilian Jiu-Jitsu", "Kung Fu"],
        "What is the primary focus of Taekwondo?": ["Punching", "Kicking", "Grappling", "Blocking"]
    }
    answers = ["Ball of the foot", "Brazilian Jiu-Jitsu", "Kicking"]

    score = 0
    for i, (question, options) in enumerate(questions.items()):
        st.write(question)
        answer = st.radio("", options, key=f"q{i}")
        if answer == answers[i]:
            score += 1

    st.write(f"Your score: {score}/{len(questions)}")

# Daily Goal Setter
def daily_goal_setter():
    today = date.today()
    if 'daily_goals' not in st.session_state or st.session_state['goal_date'] != today:
        st.session_state['daily_goals'] = []
        st.session_state['goal_date'] = today

    st.write("## Set Your Daily Training Goals")
    goal_input = st.text_input("Enter a new goal")
    if st.button("Add Goal"):
        st.session_state['daily_goals'].append({"goal": goal_input, "completed": False})
    
    st.write("### Your Goals for Today")
    for idx, goal in enumerate(st.session_state['daily_goals']):
        col1, col2 = st.columns([4, 1])
        col1.write(goal["goal"])
        if col2.button("Complete", key=f"complete_{idx}"):
            st.session_state['daily_goals'][idx]['completed'] = True

    st.write("### Completed Goals")
    for goal in st.session_state['daily_goals']:
        if goal['completed']:
            st.write(f"✅ {goal['goal']}")

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

        # Get the emotion analysis
        emotion = analyze_emotion(user_input)
        st.write(f"**Detected Emotion:** {emotion}")

        # Update the chat history
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": bot_response})
        st.session_state['chat_history'] = chat_history

        # Display the conversation
        st.write(f"**You:** {user_input}")
        st.write(f"**SmartBot:** {bot_response}")

        # Convert bot response to speech
        audio = text_to_speech(bot_response)
        st.audio(audio, format='audio/mp3')

        # Display relevant video based on user input
        video_url = get_martial_arts_video(user_input)
        st.video(video_url)

# Display chat history in a collapsible dropdown list
with st.expander("Chat History", expanded=False):
    st.write("### Conversation")
    for i, message in enumerate(st.session_state['chat_history']):
        if message['role'] == 'user':
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**SmartBot:** {message['content']}")

# Add a footer
st.write("---")
st.write("© 2024 Martial Arts & Self-Defense. All rights reserved.")

# Section for daily tips and exercises
st.sidebar.title("Daily Tip")
daily_tip = st.sidebar.radio(
    "Choose an area to focus on",
    ("General Tips", "Technique of the Day", "Self-Defense Scenario")
)

if daily_tip == "General Tips":
    st.sidebar.write("Stay consistent with your training, warm up properly before exercises, and cool down afterward to prevent injuries.")
elif daily_tip == "Technique of the Day":
    st.sidebar.write("Today's Technique: Front Kick - Start with your feet shoulder-width apart. Lift your knee to your chest and snap your foot forward, striking with the ball of your foot.")
elif daily_tip == "Self-Defense Scenario":
    st.sidebar.write("Scenario: Someone grabs your wrist. React by twisting your wrist towards the attacker's thumb and pull your hand back quickly to break free.")

# Quiz section
st.sidebar.title("Martial Arts Quiz")
if st.sidebar.button("Start Quiz"):
    martial_arts_quiz()

# Daily Goal Setter section
st.sidebar.title("Daily Goal Setter")
daily_goal_setter()
