import streamlit as st
import openai
import os
from dotenv import load_dotenv
import base64
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
        layout="centered"
    )
    
    # Simple, clean CSS
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu, footer, header, .stDeployButton {
        visibility: hidden;
    }
    
    /* Reduce top padding */
    .main > div {
        padding-top: 1rem !important;
    }
    
    .block-container {
        padding-top: 1rem !important;
        max-width: 700px !important;
    }
    
    /* App styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Title styling */
    .main-title {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #e2e8f0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Chat container */
    .chat-box {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Messages */
    .message {
        margin: 1rem 0;
        padding: 0.75rem 1rem;
        border-radius: 15px;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .message.user {
        background: #007aff;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    .message.assistant {
        background: #f1f1f1;
        color: #333;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    
    /* Audio styling */
    audio {
        width: 100%;
        margin: 0.5rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        font-size: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }
    
    /* Text input */
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border: 2px solid #ddd !important;
        font-size: 1rem !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
    }
    
    /* Ski cards */
    .ski-recommendations {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .ski-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .ski-name {
        font-weight: 700;
        color: #2d3748;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .ski-description {
        color: #4a5568;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    .shop-links {
        display: flex;
        gap: 0.5rem;
    }
    
    .shop-link {
        background: #667eea;
        color: white;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 500;
        flex: 1;
        text-align: center;
    }
    
    .shop-link:hover {
        background: #5a67d8;
        text-decoration: none;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'recommended_skis' not in st.session_state:
        st.session_state.recommended_skis = []
    
    # Header
    st.markdown('''
    <div class="main-title">🎿 Ski Concierge</div>
    <div class="subtitle">Your AI ski expert with voice responses</div>
    ''', unsafe_allow_html=True)
    
    # Main chat interface
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    
    # Always show input form - no separate start state
    st.markdown("### Ask me about skis!")
    
    with st.form("ski_form", clear_on_submit=True):
        user_input = st.text_area(
            "What would you like to know?",
            placeholder="e.g., I'm a beginner looking for all-mountain skis under $400...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("🎿 Get Recommendations")
        with col2:
            clear = st.form_submit_button("🔄 Clear Chat")
        
        if submit and user_input:
            # Add user message
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input
            })
            
            # Get AI response
            with st.spinner("Getting ski recommendations..."):
                response = get_ski_advice(user_input)
                audio_html = create_openai_audio(response)
            
            # Extract ski recommendations
            skis = extract_ski_recommendations(response)
            if skis:
                st.session_state.recommended_skis = skis[:3]
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "audio": audio_html
            })
            
            st.rerun()
        
        if clear:
            st.session_state.messages = []
            st.session_state.recommended_skis = []
            st.rerun()
    
    # Display conversation
    if st.session_state.messages:
        st.markdown("### Conversation")
        
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            st.markdown(f'<div class="message {role}">{content}</div>', unsafe_allow_html=True)
            
            if role == "assistant" and "audio" in message and message["audio"]:
                st.markdown(message["audio"], unsafe_allow_html=True)
    
    else:
        # Show welcome message when no conversation yet
        st.info("👋 Hi! I'm your ski concierge. Ask me anything about skis - your experience level, what you're looking for, budget, terrain preferences, etc. I'll give you personalized recommendations with voice responses!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show ski recommendations
    if st.session_state.recommended_skis:
        st.markdown('<div class="ski-recommendations">', unsafe_allow_html=True)
        st.markdown("### 🎿 Recommended Skis")
        
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

def get_ski_advice(user_input):
    """Get AI ski advice"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert ski consultant. Provide helpful advice in a conversational tone.
                    
                    When recommending skis, use this format:
                    SKI: [Brand Model] - [Description with key features]
                    
                    Always recommend 2-3 specific ski models maximum.
                    Keep responses under 120 words but be informative."""
                },
                {"role": "user", "content": user_input}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception:
        return "I'd be happy to help you find the perfect skis! Could you tell me more about your skiing experience, preferred terrain, and budget?"

def create_openai_audio(text):
    """Create audio using OpenAI voice API"""
    try:
        # Clean text
        clean_text = re.sub(r'SKI:', '', text)
        clean_text = re.sub(r'[*#]', '', clean_text).strip()
        
        if len(clean_text) < 10:
            return ""
        
        # Generate speech
        response = openai.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=clean_text,
            speed=1.0
        )
        
        # Convert to base64
        audio_data = response.content
        audio_b64 = base64.b64encode(audio_data).decode()
        
        return f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
        
    except Exception:
        return ""

def extract_ski_recommendations(text):
    """Extract ski recommendations"""
    ski_pattern = r'SKI:\s*([^-\n]+)\s*-\s*([^\n]+)'
    matches = re.findall(ski_pattern, text, re.IGNORECASE)
    return [{"name": match[0].strip(), "description": match[1].strip()} for match in matches[:3]]

if __name__ == "__main__":
    main()