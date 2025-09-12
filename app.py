import streamlit as st
import openai
import os
from dotenv import load_dotenv
import speech_recognition as sr
import base64
import time
import re

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def main():
    st.set_page_config(
        page_title="Ski Concierge",
        page_icon="🎿",
        layout="centered"
    )
    
    # Clean, working CSS
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Content container */
    .main-content {
        background: white;
        border-radius: 25px;
        padding: 40px 30px;
        margin: 20px auto;
        max-width: 450px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        text-align: center;
    }
    
    /* Title */
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 10px;
    }
    
    .app-subtitle {
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    
    /* Status text */
    .status-text {
        color: #4a5568;
        font-size: 16px;
        margin-bottom: 20px;
        font-weight: 500;
    }
    
    /* Speak button */
    .speak-btn-container {
        margin: 30px 0;
    }
    
    .speak-button {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        color: white;
        font-size: 32px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    
    .speak-button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.5);
    }
    
    .speak-button:active {
        transform: translateY(-1px) scale(0.98);
    }
    
    .speak-button.listening {
        background: linear-gradient(135deg, #ef4444, #f97316);
        animation: listening-pulse 1.5s infinite;
    }
    
    @keyframes listening-pulse {
        0%, 100% { 
            transform: scale(1); 
            box-shadow: 0 15px 35px rgba(239, 68, 68, 0.4); 
        }
        50% { 
            transform: scale(1.1); 
            box-shadow: 0 25px 50px rgba(239, 68, 68, 0.6); 
        }
    }
    
    /* Messages */
    .messages-container {
        max-height: 300px;
        overflow-y: auto;
        margin: 25px 0;
        padding: 0 10px;
    }
    
    .message {
        margin: 15px 0;
        padding: 12px 18px;
        border-radius: 20px;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 15px;
        line-height: 1.4;
    }
    
    .message.user {
        background: #007aff;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 6px;
    }
    
    .message.assistant {
        background: #f1f3f4;
        color: #2d3748;
        margin-right: auto;
        border-bottom-left-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    
    /* Audio player */
    .audio-container {
        margin: 12px 0;
        background: #f8f9fa;
        border-radius: 12px;
        padding: 8px;
    }
    
    .audio-container audio {
        width: 100%;
        height: 40px;
    }
    
    /* Ski recommendations */
    .recommendations-section {
        margin-top: 30px;
        padding-top: 25px;
        border-top: 2px solid #e2e8f0;
    }
    
    .recommendations-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 20px;
    }
    
    .ski-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .ski-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    .ski-name {
        font-weight: 600;
        color: #2d3748;
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    .ski-description {
        color: #4a5568;
        font-size: 14px;
        margin-bottom: 15px;
        line-height: 1.4;
    }
    
    .shop-links {
        display: flex;
        gap: 8px;
    }
    
    .shop-link {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 500;
        flex: 1;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .shop-link:hover {
        background: linear-gradient(135deg, #5a67d8, #6b46c1);
        text-decoration: none;
        color: white;
        transform: translateY(-1px);
    }
    
    /* Control buttons */
    .control-section {
        margin: 25px 0;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #48bb78, #38a169) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 8px 20px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #38a169, #2f855a) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Scrollbar */
    .messages-container::-webkit-scrollbar {
        width: 4px;
    }
    
    .messages-container::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .messages-container::-webkit-scrollbar-thumb {
        background: #cbd5e0;
        border-radius: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'listening' not in st.session_state:
        st.session_state.listening = False
    
    if 'recommended_skis' not in st.session_state:
        st.session_state.recommended_skis = []
    
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    
    # Main content container
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Header
    st.markdown('''
    <div class="app-title">🎿 Ski Concierge</div>
    <div class="app-subtitle">Your AI ski expert</div>
    ''', unsafe_allow_html=True)
    
    # Status text
    if not st.session_state.conversation_started:
        status = "Tap the button to start chatting about skis"
    elif st.session_state.listening:
        status = "🎙️ Listening... speak now!"
    else:
        status = "Tap to ask about skis"
    
    st.markdown(f'<div class="status-text">{status}</div>', unsafe_allow_html=True)
    
    # Speak button
    button_class = "listening" if st.session_state.listening else ""
    button_icon = "🎙️" if st.session_state.listening else "🎤"
    
    st.markdown(f'''
    <div class="speak-btn-container">
        <button class="speak-button {button_class}" onclick="document.getElementById('hidden_speak').click();">
            {button_icon}
        </button>
    </div>
    ''', unsafe_allow_html=True)
    
    # Hidden Streamlit button
    if st.button("Speak", key="hidden_speak"):
        st.session_state.listening = True
        
        if not st.session_state.conversation_started:
            st.session_state.conversation_started = True
            welcome = "Hi! I'm your ski concierge. What's your experience level and what skis are you looking for?"
            welcome_audio = create_openai_audio(welcome)
            st.session_state.messages.append({
                "role": "assistant",
                "content": welcome,
                "audio": welcome_audio
            })
            st.session_state.listening = False
            st.rerun()
        else:
            # Listen for speech
            with st.spinner("🎧 Listening..."):
                user_speech = listen_for_speech()
            
            st.session_state.listening = False
            
            if user_speech and user_speech not in ["TIMEOUT", "UNCLEAR", "ERROR"]:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_speech
                })
                
                # Get AI response
                with st.spinner("🤔 Getting recommendations..."):
                    response = get_ski_advice(user_speech)
                    audio_html = create_openai_audio(response)
                
                # Extract ski recommendations
                skis = extract_ski_recommendations(response)
                if skis:
                    st.session_state.recommended_skis = skis[:3]  # Max 3 skis
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "audio": audio_html
                })
                
                st.rerun()
            else:
                if user_speech == "TIMEOUT":
                    st.info("💭 No speech detected - try again when ready")
                else:
                    st.warning("🎯 Couldn't understand - please speak clearly")
    
    # Display messages
    if st.session_state.messages:
        st.markdown('<div class="messages-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            st.markdown(f'<div class="message {role}">{content}</div>', unsafe_allow_html=True)
            
            if role == "assistant" and "audio" in message and message["audio"]:
                st.markdown(f'<div class="audio-container">{message["audio"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Ski recommendations
    if st.session_state.recommended_skis:
        st.markdown('<div class="recommendations-section">', unsafe_allow_html=True)
        st.markdown('<div class="recommendations-title">🎿 Recommended Skis</div>', unsafe_allow_html=True)
        
        for ski in st.session_state.recommended_skis:
            search_term = ski["name"].replace(" ", "+")
            rei_url = f"https://www.rei.com/search?q={search_term}"
            bc_url = f"https://www.backcountry.com/search?q={search_term}"
            evo_url = f"https://www.evo.com/search?text={search_term}"
            
            st.markdown(f'''
            <div class="ski-card">
                <div class="ski-name">{ski["name"]}</div>
                <div class="ski-description">{ski["description"]}</div>
                <div class="shop-links">
                    <a href="{rei_url}" target="_blank" class="shop-link">REI</a>
                    <a href="{bc_url}" target="_blank" class="shop-link">Backcountry</a>
                    <a href="{evo_url}" target="_blank" class="shop-link">Evo</a>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Control section
    if st.session_state.messages:
        st.markdown('<div class="control-section">', unsafe_allow_html=True)
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.session_state.recommended_skis = []
            st.session_state.conversation_started = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def listen_for_speech(timeout=8):
    """Listen for speech input"""
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        with microphone as source:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
        
        text = recognizer.recognize_google(audio)
        return text
        
    except sr.WaitTimeoutError:
        return "TIMEOUT"
    except sr.UnknownValueError:
        return "UNCLEAR"
    except Exception:
        return "ERROR"

def get_ski_advice(user_input):
    """Get AI ski advice"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a ski expert. Keep responses under 60 words. When recommending skis, use format: SKI: [Brand Model] - [Description]. Recommend maximum 2-3 specific ski models."
                },
                {"role": "user", "content": user_input}
            ],
            max_tokens=120,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, having connection issues: {str(e)}"

def create_openai_audio(text):
    """Create natural audio using OpenAI voice API"""
    try:
        # Clean text for speech
        clean_text = re.sub(r'SKI:', '', text)
        clean_text = re.sub(r'[*#]', '', clean_text).strip()
        
        # Generate speech
        response = openai.audio.speech.create(
            model="tts-1",
            voice="nova",  # Natural female voice
            input=clean_text,
            speed=1.0
        )
        
        # Convert to base64
        audio_data = response.content
        audio_b64 = base64.b64encode(audio_data).decode()
        
        return f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
        
    except Exception as e:
        st.error(f"Voice generation error: {str(e)}")
        return ""

def extract_ski_recommendations(text):
    """Extract ski recommendations from AI response"""
    ski_pattern = r'SKI:\s*([^-\n]+)\s*-\s*([^\n]+)'
    matches = re.findall(ski_pattern, text, re.IGNORECASE)
    return [{"name": match[0].strip(), "description": match[1].strip()} for match in matches[:3]]

if __name__ == "__main__":
    main()