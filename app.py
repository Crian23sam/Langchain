import os
from dotenv import load_dotenv
import streamlit as st
from googleapiclient.discovery import build
from groq import Groq
from langchain.memory import ConversationBufferMemory
from gtts import gTTS
import base64
from io import BytesIO
from datetime import date
from PIL import Image
import requests
from streamlit_option_menu import option_menu

load_dotenv()

groqcloud_apikey = os.getenv('GROQCLOUD_API_KEY')
youtube_api_key = os.getenv('YOUTUBE_API_KEY')

os.environ['GROQ_API_KEY'] = groqcloud_apikey

def init_groq_client():
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        _ = client.chat.completions.create(
            messages=[{"role": "system", "content": "hello"}],
            model="llama3-8b-8192",
        )
        return client
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        st.stop()

client = init_groq_client()

youtube = build('youtube', 'v3', developerKey=youtube_api_key)

st.set_page_config(
    page_title="ZenFight AI",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS to style the page with a background image and remove unwanted backgrounds
background_image_css = """
<style>
    .stApp {
        background-image: url('https://c4.wallpaperflare.com/wallpaper/628/39/680/1920x1080-px-meditation-monk-selective-coloring-video-games-age-of-conan-hd-art-wallpaper-preview.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Remove white background and borders around main content */
    .block-container {
        background: rgba(0, 0, 0, 0);  /* Transparent background */
        box-shadow: none;              /* Remove shadow */
    }
    
    /* Customize Streamlit header */
    header {
        background: rgba(0, 0, 0, 0);  /* Semi-transparent background */
        padding: 10px;
        border-radius: 10px;
    }
    
    /* Style text input box */
    .stTextInput > div:first-child {
        background-color: rgba(0, 0, 0, 0.6); /* More transparent background */
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Style the text and button within forms */
    .stButton > button {
        background-color: #7B1818;  /* Button background color */
        color: black;               /* Button text color */
        border-radius: 10px;
    }

    .stTextInput > div input {
        color: white; /* Text color */
    }
    
    /* Customize the sidebar */
    .sidebar .sidebar-content {
        background: rgba(0, 0, 0, 0.8); /* More opaque for readability */
        padding: 20px;
        border-radius: 10px;
    }
    
    /* General text styling for readability */
    .stMarkdown {
        background: rgba(0, 0, 0, 0.5);
        color: white; /* Text color */
        padding: 10px;
        border-radius: 10px;
    }
</style>
"""

# Inject CSS into the Streamlit app
st.markdown(background_image_css, unsafe_allow_html=True)

st.markdown("""
<style>
button[data-baseweb="button"] {
    background-color: red;
    color: white;
    border: 1px solid red;
}
button[data-baseweb="button"]:hover {
    background-color: darkred;
    border: 1px solid darkred;
}
</style>
""", unsafe_allow_html=True)

MARTIAL_ARTS_KEYWORDS = [
    "martial arts", "karate", "judo", "taekwondo", "kickboxing", "kung fu", 
    "jiu jitsu", "self-defense", "grappling", "sparring", "muay thai", 
    "wrestling", "boxing", "dojo", "kata", "martial arts techniques", 
    "martial arts exercises", "martial arts training", "martial arts tips","fight",
    "fit","build"
]

def is_martial_arts_related(input_text):
    input_text = input_text.lower()  # Convert input to lowercase
    for keyword in MARTIAL_ARTS_KEYWORDS:
        if keyword in input_text:
            return True
    return False

def fetch_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Error fetching image: {e}")
        return None

def get_chatbot_response(user_message, chat_history):
    if is_martial_arts_related(user_message):
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
    else:
        return "Sorry, please ask something related to martial arts."

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    return mp3_fp

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

def reset_chat():
    st.session_state['chat_history'] = []

def daily_goal_setter():
    today = date.today()
    if 'daily_goals' not in st.session_state or st.session_state['goal_date'] != today:
        st.session_state['daily_goals'] = []
        st.session_state['goal_date'] = today

    st.write("## Set Your Daily Training Goals")
    goal_input = st.text_input("Enter a new goal")
    if st.button("Add Goal"):
        if goal_input.strip() == "":
            st.error("Goal cannot be empty. Please enter a valid goal.")
        else:
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

def training_tracker():
    st.sidebar.title("Training Tracker")
    st.sidebar.write("Log your training sessions and progress.")

    if 'training_log' not in st.session_state:
        st.session_state['training_log'] = []

    session_date = st.sidebar.date_input("Session Date")
    training_activity = st.sidebar.text_input("Training Activity")
    training_duration = st.sidebar.number_input("Duration (minutes)", min_value=0, step=1)
    training_notes = st.sidebar.text_area("Notes")

    if st.sidebar.button("Add Training Session"):
        if not training_activity.strip():
            st.sidebar.error("Training activity cannot be empty. Please enter a valid activity.")
        elif training_duration <= 0:
            st.sidebar.error("Training duration must be greater than 0.")
        else:
            st.session_state['training_log'].append({
                "date": session_date,
                "activity": training_activity,
                "duration": training_duration,
                "notes": training_notes
            })
            st.sidebar.success("Training session added!")

    st.sidebar.write("### Training Log")
    for entry in st.session_state['training_log']:
        st.sidebar.write(f"- **{entry['date']}**: {entry['activity']} for {entry['duration']} minutes")
        if entry['notes']:
            st.sidebar.write(f"  - Notes: {entry['notes']}")

def main():
    st.title('🥋 ZenFight AI')
    st.write("Welcome to the Martial Arts & Self-Defense App! Type your questions below to learn about techniques, tips, and exercises.")
    
    st.sidebar.button('Start New Chat', on_click=reset_chat)

    conversation_memory = ConversationBufferMemory(memory_key='chat_history', input_key='input', output_key='output')

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    with st.form(key='chat_form'):
        user_input = st.text_input('You: ')
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        chatbot_response = get_chatbot_response(user_input, st.session_state['chat_history'])
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        st.session_state['chat_history'].append({"role": "assistant", "content": chatbot_response})
        st.markdown(f"**You:** {user_input}")
        st.markdown(f"**ZenFight AI:** {chatbot_response}")
        
        mp3_fp = text_to_speech(chatbot_response)
        st.audio(mp3_fp, format="audio/mp3")

        video_url = get_martial_arts_video(user_input)
        st.video(video_url)

    # image_url = 'https://c4.wallpaperflare.com/wallpaper/628/39/680/1920x1080-px-meditation-monk-selective-coloring-video-games-age-of-conan-hd-art-wallpaper-preview.jpg'
    # image = fetch_image(image_url)
    # if image:
    #     st.image(image, caption='Martial Arts Background')

if __name__ == "__main__":
    selected = option_menu(
        "ZenFight AI",
        ["Main", "Daily Goals", "Training Tracker"],
        icons=["house", "list-check", "calendar-check"],
        menu_icon="app-indicator",
        default_index=0,
        orientation="horizontal",
    )

    if selected == "Main":
        main()
    elif selected == "Daily Goals":
        daily_goal_setter()
    elif selected == "Training Tracker":
        training_tracker()
