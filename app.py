import os
from dotenv import load_dotenv
import streamlit as st
from googleapiclient.discovery import build
from groq import Groq
from langchain.memory import ConversationBufferMemory
from gtts import gTTS
from io import BytesIO
from datetime import date

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

st.markdown(
    """
    <style>
    body, html {
      margin: 0;
      padding: 0;
      height: 100%;
      overflow: hidden;
    }

    .background-video-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      z-index: -1;
    }

    .background-video-container video {
      min-width: 100%;
      min-height: 100%;
      object-fit: cover;
    }

    .main {
      position: relative;
      z-index: 1;
    }
    </style>
    <div class="background-video-container">
        <video autoplay muted loop>
            <source src="https://videos.pexels.com/video-files/4761806/4761806-uhd_2732_1440_25fps.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    """,
    unsafe_allow_html=True
)

st.title('🥋 ZenFight AI')

st.write("Welcome to the Martial Arts & Self-Defense App! Type your questions below to learn about techniques, tips, and exercises.")

conversation_memory = ConversationBufferMemory(memory_key='chat_history', input_key='input', output_key='output')

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def reset_chat():
    st.session_state['chat_history'] = []

if st.sidebar.button('Start New Chat'):
    reset_chat()

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

def meditation_and_breathing():
    st.sidebar.title("Meditation & Breathing")
    st.sidebar.write("Calm your mind with these exercises.")

    breathing_exercises = [
        "4-7-8 Breathing: Inhale for 4 seconds, hold for 7 seconds, exhale for 8 seconds.",
        "Box Breathing: Inhale for 4 seconds, hold for 4 seconds, exhale for 4 seconds, hold for 4 seconds.",
        "Diaphragmatic Breathing: Focus on breathing deeply into your diaphragm."
    ]

    meditation_tips = [
        "Find a quiet place, sit comfortably, and close your eyes.",
        "Focus on your breath and try to clear your mind.",
        "Start with 5 minutes a day and gradually increase the time."
    ]

    selected_exercise = st.sidebar.selectbox("Choose an exercise", breathing_exercises)
    st.sidebar.write(selected_exercise)

    st.sidebar.write("### Meditation Tips")
    for tip in meditation_tips:
        st.sidebar.write(f"- {tip}")

def personalized_training_plans():
    st.sidebar.title("Personalized Training Plans")
    st.sidebar.write("Create and follow a personalized training plan based on your goals.")

    if 'training_plans' not in st.session_state:
        st.session_state['training_plans'] = []

    goal = st.sidebar.selectbox(
        "Select your main goal",
        ("Lose Weight", "Build Muscle", "Self-Defense", "Fitness", "Learning a Specific Martial Art")
    )

    plan_name = st.sidebar.text_input("Plan Name")
    plan_duration = st.sidebar.number_input("Plan Duration (weeks)", min_value=1, step=1)
    plan_notes = st.sidebar.text_area("Plan Notes")

    if st.sidebar.button("Create Training Plan"):
        if not plan_name.strip():
            st.sidebar.error("Plan name cannot be empty. Please enter a valid name.")
        else:
            exercises = []
            tips = []

            if goal == "Lose Weight":
                exercises = [
                    "Cardio: 30 minutes of running or cycling",
                    "High-Intensity Interval Training (HIIT): 20 minutes",
                    "Strength Training: 30 minutes of full-body workout"
                ]
                tips = [
                    "Maintain a calorie deficit diet.",
                    "Stay hydrated.",
                    "Get enough sleep to aid recovery."
                ]

            elif goal == "Build Muscle":
                exercises = [
                    "Strength Training: 45 minutes of weight lifting focusing on different muscle groups",
                    "Protein Intake: Ensure adequate protein intake before and after workouts",
                    "Compound Exercises: Include squats, deadlifts, and bench presses"
                ]
                tips = [
                    "Consume a high-protein diet.",
                    "Increase your calorie intake to support muscle growth.",
                    "Allow adequate rest for muscle recovery."
                ]

            elif goal == "Self-Defense":
                exercises = [
                    "Martial Arts Drills: 30 minutes",
                    "Strength and Conditioning: 30 minutes",
                    "Practice Self-Defense Techniques: 30 minutes"
                ]
                tips = [
                    "Practice regularly to improve your techniques.",
                    "Focus on speed and agility.",
                    "Stay aware of your surroundings."
                ]

            elif goal == "Fitness":
                exercises = [
                    "Cardio: 30 minutes of running, cycling, or swimming",
                    "Strength Training: 30 minutes of full-body workout",
                    "Flexibility: 20 minutes of stretching or yoga"
                ]
                tips = [
                    "Stay consistent with your workouts.",
                    "Mix different types of exercises to avoid monotony.",
                    "Listen to your body to avoid overtraining."
                ]

            elif goal == "Learning a Specific Martial Art":
                exercises = [
                    "Technique Practice: 45 minutes of practicing specific martial arts techniques",
                    "Conditioning: 30 minutes of strength and endurance training",
                    "Sparring: 30 minutes (if possible)"
                ]
                tips = [
                    "Focus on mastering the basics.",
                    "Practice regularly to build muscle memory.",
                    "Learn from a qualified instructor."
                ]

            plan = {
                "goal": goal,
                "name": plan_name,
                "duration": plan_duration,
                "notes": plan_notes,
                "exercises": exercises,
                "tips": tips
            }
            st.session_state['training_plans'].append(plan)
            st.sidebar.success("Training plan created!")

    st.sidebar.write("### Your Training Plans")
    for plan in st.session_state['training_plans']:
        st.sidebar.write(f"- **{plan['name']}** ({plan['duration']} weeks)")
        st.sidebar.write(f"  - Goal: {plan['goal']}")
        if plan['notes']:
            st.sidebar.write(f"  - Notes: {plan['notes']}")
        st.sidebar.write("  - Exercises:")
        for exercise in plan['exercises']:
            st.sidebar.write(f"    - {exercise}")
        st.sidebar.write("  - Tips:")
        for tip in plan['tips']:
            st.sidebar.write(f"    - {tip}")

with st.form(key='input_form'):
    user_input = st.text_input('You:', key='input_field')
    submit_button = st.form_submit_button(label='Send')

if submit_button:
    if user_input:
        chat_history = st.session_state['chat_history']
        bot_response = get_chatbot_response(user_input, chat_history)

        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": bot_response})
        st.session_state['chat_history'] = chat_history

        st.write(f"**You:** {user_input}")
        st.write(f"**ZenFight AI:** {bot_response}")

        audio = text_to_speech(bot_response)
        st.audio(audio, format='audio/mp3')

        video_url = get_martial_arts_video(user_input)
        st.video(video_url)

with st.expander("Chat History", expanded=False):
    st.write("### Conversation")
    for i, message in enumerate(st.session_state['chat_history']):
        if message['role'] == 'user':
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**ZenFight AI:** {message['content']}")

st.sidebar.title("Daily Tip")
daily_tip = st.sidebar.radio(
    "Choose an area to focus on",
    ("General Tips", "Technique of the Day", "Self-Defense Scenario")
)

def play_audio_tip(tip):
    tts = gTTS(text=tip, lang='en')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    st.sidebar.audio(audio_fp, format='audio/mp3')

if daily_tip == "General Tips":
    tip = "Stay consistent with your training, warm up properly before exercises, and cool down afterward to prevent injuries."
    st.sidebar.write(tip)
    play_audio_tip(tip)

elif daily_tip == "Technique of the Day":
    tip = "Today's Technique: Front Kick - Start with your feet shoulder-width apart. Lift your knee to your chest and snap your foot forward, striking with the ball of your foot."
    st.sidebar.write(tip)
    play_audio_tip(tip)

elif daily_tip == "Self-Defense Scenario":
    tip = "Scenario: Someone grabs your wrist. React by twisting your wrist towards the attacker's thumb and pull your hand back quickly to break free."
    st.sidebar.write(tip)
    play_audio_tip(tip)

st.sidebar.title("Daily Goal Setter")
daily_goal_setter()

st.write("---")

st.write("© 2024 Martial Arts & Self-Defense. All rights reserved.")

training_tracker()
meditation_and_breathing()
personalized_training_plans()
