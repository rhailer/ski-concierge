import streamlit as st
import openai
import os
from dotenv import load_dotenv
import base64
import time
import re

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Check for API key
if not openai.api_key:
    st.error("⚠️ OpenAI API key not found. Please add OPENAI_API_KEY to Streamlit secrets.")
    st.stop()

def main():
    st.set_page_config(
        page_title="Ski Concierge",
        page_icon="🎿",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Premium Perplexity-inspired CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global reset and base */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Hide all Streamlit elements */
    #MainMenu, footer, header, .stDeployButton, .stDecoration {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* Main app container */
    .stApp {
        background: #0a0a0a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #ffffff;
    }
    
    .main .block-container {
        padding: 0 !important;
        max-width: none !important;
    }
    
    /* Custom app container */
    .app-container {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        position: relative;
        overflow: hidden;
    }
    
    .app-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 200px;
        background: radial-gradient(ellipse at center top, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    
    /* Header section */
    .header-section {
        text-align: center;
        padding: 60px 20px 40px;
        position: relative;
        z-index: 2;
    }
    
    .app-logo {
        font-size: 4rem;
        margin-bottom: 16px;
        filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.3));
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.1);
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 0;
    }
    
    /* Main content area */
    .content-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 20px 40px;
        position: relative;
        z-index: 2;
    }
    
    /* Chat container */
    .chat-container {
        width: 100%;
        max-width: 800px;
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(51, 65, 85, 0.3);
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 32px;
        box-shadow: 
            0 20px 25px -5px rgba(0, 0, 0, 0.4),
            0 10px 10px -5px rgba(0, 0, 0, 0.2);
    }
    
    /* Input section */
    .input-section {
        margin-bottom: 24px;
    }
    
    .input-label {
        display: block;
        font-size: 14px;
        font-weight: 500;
        color: #cbd5e1;
        margin-bottom: 12px;
        text-align: left;
    }
    
    .custom-input {
        width: 100%;
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(51, 65, 85, 0.5);
        border-radius: 16px;
        padding: 16px 20px;
        font-size: 16px;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        resize: none;
        min-height: 60px;
    }
    
    .custom-input:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        background: rgba(30, 41, 59, 0.9);
    }
    
    .custom-input::placeholder {
        color: #64748b;
    }
    
    /* Buttons */
    .button-row {
        display: flex;
        gap: 16px;
        margin-top: 16px;
    }
    
    .premium-button {
        flex: 1;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        border: none;
        border-radius: 12px;
        padding: 14px 24px;
        font-size: 15px;
        font-weight: 600;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow: hidden;
    }
    
    .premium-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
    }
    
    .premium-button:active {
        transform: translateY(0);
    }
    
    .premium-button.secondary {
        background: rgba(51, 65, 85, 0.8);
        color: #e2e8f0;
    }
    
    .premium-button.secondary:hover {
        background: rgba(51, 65, 85, 1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    /* Messages */
    .messages-area {
        max-height: 400px;
        overflow-y: auto;
        margin: 24px 0;
    }
    
    .message {
        margin-bottom: 20px;
        animation: slideIn 0.5s ease-out;
    }
    
    .message-bubble {
        padding: 16px 20px;
        border-radius: 18px;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 15px;
        line-height: 1.5;
        position: relative;
    }
    
    .message.user {
        text-align: right;
    }
    
    .message.user .message-bubble {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 6px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .message.assistant {
        text-align: left;
    }
    
    .message.assistant .message-bubble {
        background: rgba(30, 41, 59, 0.9);
        color: #e2e8f0;
        border: 1px solid rgba(51, 65, 85, 0.3);
        border-bottom-left-radius: 6px;
        margin-right: auto;
    }
    
    /* Audio player */
    .audio-player {
        margin: 12px 0;
        padding: 12px;
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(51, 65, 85, 0.3);
    }
    
    .audio-player audio {
        width: 100%;
        height: 40px;
        filter: brightness(1.2) contrast(1.1);
    }
    
    .audio-status {
        font-size: 12px;
        color: #64748b;
        text-align: center;
        margin-top: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    
    /* Ski recommendations */
    .recommendations-container {
        width: 100%;
        max-width: 1000px;
        margin-top: 32px;
    }
    
    .recommendations-header {
        text-align: center;
        margin-bottom: 32px;
    }
    
    .recommendations-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }
    
    .recommendations-subtitle {
        color: #94a3b8;
        font-size: 1rem;
    }
    
    .ski-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 24px;
        margin-bottom: 40px;
    }
    
    .ski-card {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(51, 65, 85, 0.3);
        border-radius: 20px;
        padding: 28px;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .ski-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8, #7c3aed);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .ski-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    .ski-card:hover::before {
        opacity: 1;
    }
    
    .ski-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
        line-height: 1.3;
    }
    
    .ski-description {
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 24px;
    }
    
    .shop-links {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 8px;
    }
    
    .shop-link {
        background: rgba(51, 65, 85, 0.8);
        color: #e2e8f0;
        text-decoration: none;
        padding: 10px 16px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(71, 85, 105, 0.3);
    }
    
    .shop-link:hover {
        background: #3b82f6;
        color: white;
        text-decoration: none;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Scrollbar styling */
    .messages-area::-webkit-scrollbar {
        width: 6px;
    }
    
    .messages-area::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.3);
        border-radius: 3px;
    }
    
    .messages-area::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.5);
        border-radius: 3px;
    }
    
    .messages-area::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.7);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .app-logo {
            font-size: 3rem;
        }
        
        .app-title {
            font-size: 2rem;
        }
        
        .chat-container {
            margin: 0 10px 20px;
            padding: 24px 20px;
        }
        
        .message-bubble {
            max-width: 90%;
        }
        
        .ski-grid {
            grid-template-columns: 1fr;
            gap: 20px;
        }
        
        .shop-links {
            grid-template-columns: 1fr;
            gap: 8px;
        }
    }
    
    /* Hide Streamlit elements more aggressively */
    .stTextInput, .stButton {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'recommended_skis' not in st.session_state:
        st.session_state.recommended_skis = []
    
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    
    # Main app structure
    st.markdown('<div class="app-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('''
    <div class="header-section">
        <div class="app-logo">🎿</div>
        <h1 class="app-title">Ski Concierge</h1>
        <p class="app-subtitle">AI-powered ski expert with natural voice responses</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Content section
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    # Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.conversation_started:
        st.markdown('''
        <div class="input-section">
            <label class="input-label">Ready to find your perfect skis?</label>
            <div style="text-align: center; padding: 20px 0;">
                <button class="premium-button" onclick="startConversation()">
                    🚀 Start Ski Consultation
                </button>
            </div>
        </div>
        
        <script>
        function startConversation() {
            // This will trigger the Streamlit rerun
            document.querySelector('[data-testid="stButton"] button').click();
        }
        </script>
        ''', unsafe_allow_html=True)
        
        # Hidden Streamlit button
        if st.button("Start", key="start_hidden"):
            st.session_state.conversation_started = True
            welcome = "Hi! I'm your personal ski concierge. Tell me about your skiing experience, preferred terrain, and budget, and I'll recommend the perfect skis for you."
            welcome_audio = create_openai_audio(welcome)
            st.session_state.messages.append({
                "role": "assistant",
                "content": welcome,
                "audio": welcome_audio
            })
            st.rerun()
    
    else:
        # Input form
        with st.form("ski_question_form", clear_on_submit=True):
            st.markdown('''
            <label class="input-label">What would you like to know about skis?</label>
            ''', unsafe_allow_html=True)
            
            user_question = st.text_area(
                "",
                placeholder="e.g., I'm an intermediate skier looking for all-mountain skis under $500 for East Coast conditions...",
                height=80,
                key="question_input"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("💬 Get Recommendations")
            with col2:
                reset = st.form_submit_button("🔄 New Consultation")
            
            if submit and user_question:
                process_question(user_question)
            
            if reset:
                st.session_state.messages = []
                st.session_state.recommended_skis = []
                st.session_state.conversation_started = False
                st.rerun()
    
    # Display messages
    if st.session_state.messages:
        st.markdown('<div class="messages-area">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            st.markdown(f'''
            <div class="message {role}">
                <div class="message-bubble">{content}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if role == "assistant" and "audio" in message and message["audio"]:
                st.markdown(message["audio"], unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container
    
    # Ski recommendations
    if st.session_state.recommended_skis:
        st.markdown('''
        <div class="recommendations-container">
            <div class="recommendations-header">
                <h2 class="recommendations-title">🎿 Recommended Skis</h2>
                <p class="recommendations-subtitle">Curated selections based on your needs</p>
            </div>
            <div class="ski-grid">
        ''', unsafe_allow_html=True)
        
        for ski in st.session_state.recommended_skis:
            search_term = ski["name"].replace(" ", "+")
            rei_url = f"https://www.rei.com/search?q={search_term}"
            bc_url = f"https://www.backcountry.com/search?q={search_term}"
            evo_url = f"https://www.evo.com/search?text={search_term}"
            
            st.markdown(f'''
            <div class="ski-card">
                <h3 class="ski-name">{ski["name"]}</h3>
                <p class="ski-description">{ski["description"]}</p>
                <div class="shop-links">
                    <a href="{rei_url}" target="_blank" class="shop-link">REI</a>
                    <a href="{bc_url}" target="_blank" class="shop-link">Backcountry</a>
                    <a href="{evo_url}" target="_blank" class="shop-link">Evo</a>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close content-section
    st.markdown('</div>', unsafe_allow_html=True)  # Close app-container

def process_question(user_question):
    """Process user question and generate response"""
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })
    
    # Get AI response
    with st.spinner("🤔 Analyzing your needs..."):
        response = get_ski_advice(user_question)
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

def get_ski_advice(user_input):
    """Get AI ski advice"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert ski consultant. Provide detailed, helpful advice in a conversational tone.
                    
                    When recommending skis, use this EXACT format:
                    SKI: [Brand Model] - [Detailed description including key features]
                    
                    Always recommend 2-3 specific ski models maximum.
                    Consider the user's experience level, preferred terrain, budget, and skiing style.
                    Keep responses under 100 words but be informative and engaging."""
                },
                {"role": "user", "content": user_input}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return "I'd be happy to help you find the perfect skis! Could you tell me more about your skiing experience, preferred terrain, and budget? I'm having a brief connection issue but I'm here to help!"

def create_openai_audio(text):
    """Create natural audio using OpenAI voice API"""
    try:
        # Clean text for speech
        clean_text = re.sub(r'SKI:', '', text)
        clean_text = re.sub(r'[*#]', '', clean_text).strip()
        
        if len(clean_text) < 10:  # Skip very short text
            return ""
        
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
        
        return f'''
        <div class="audio-player">
            <audio controls autoplay>
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            <div class="audio-status">
                🎤 <span>AI voice response</span>
            </div>
        </div>
        '''
        
    except Exception as e:
        # Fail silently - no red error message
        return ""

def extract_ski_recommendations(text):
    """Extract ski recommendations from AI response"""
    ski_pattern = r'SKI:\s*([^-\n]+)\s*-\s*([^\n]+)'
    matches = re.findall(ski_pattern, text, re.IGNORECASE)
    return [{"name": match[0].strip(), "description": match[1].strip()} for match in matches[:3]]

if __name__ == "__main__":
    main()