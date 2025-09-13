import streamlit as st
import openai
import sys
import os
from audio_recorder_streamlit import audio_recorder

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.ski_expert import SkiExpert
    from src.voice_handler import VoiceHandler
    from src.ui_components import render_ski_recommendations, render_conversation_history, render_user_profile, create_skiing_terrain_chart
    from config.settings import Config
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please make sure all required modules are installed and the project structure is correct.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="🎿 Ski Concierge - Your Personal Ski Expert",
    page_icon="🎿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .ski-rec-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1d5f8a;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'ski_expert' not in st.session_state:
        st.session_state.ski_expert = SkiExpert()
    
    if 'voice_handler' not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if api_key:
            client = openai.OpenAI(api_key=api_key)
            st.session_state.voice_handler = VoiceHandler(client)
            st.session_state.openai_client = client
        else:
            st.session_state.voice_handler = None
            st.session_state.openai_client = None
    
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    
    if 'current_recommendations' not in st.session_state:
        st.session_state.current_recommendations = []

def main():
    initialize_session_state()
    
    # Header
    st.markdown("<h1 class='main-header'>🎿 Ski Concierge</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: #666;'>Your Personal AI Ski Expert - Find Your Perfect Skis Through Natural Conversation</p>", unsafe_allow_html=True)
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("🔑 OpenAI API key not found!")
        st.info("Please set your OPENAI_API_KEY environment variable or add it to Streamlit secrets.")
        
        # Allow users to input API key temporarily
        with st.expander("Enter API Key Temporarily"):
            temp_api_key = st.text_input("OpenAI API Key:", type="password")
            if temp_api_key:
                os.environ["OPENAI_API_KEY"] = temp_api_key
                client = openai.OpenAI(api_key=temp_api_key)
                st.session_state.voice_handler = VoiceHandler(client)
                st.session_state.openai_client = client
                st.success("API key set! You can now use the application.")
            else:
                st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎿 How It Works")
        st.markdown("""
        1. **Talk or Type** - Share your skiing experience and what you're looking for
        2. **Expert Analysis** - I'll understand your needs and ask clarifying questions
        3. **Perfect Match** - Get 2-3 personalized ski recommendations with purchase links
        """)
        
        st.markdown("---")
        
        # User profile display
        if st.session_state.ski_expert.user_profile:
            render_user_profile(st.session_state.ski_expert.user_profile)
            st.markdown("---")
        
        # Reset conversation
        if st.button("🔄 Start New Conversation"):
            st.session_state.ski_expert.reset_conversation()
            st.session_state.conversation_started = False
            st.session_state.current_recommendations = []
            st.rerun()
        
        # Terrain info chart
        st.markdown("### 📊 Ski Terrain Guide")
        try:
            terrain_chart = create_skiing_terrain_chart()
            st.plotly_chart(terrain_chart, use_container_width=True)
        except Exception as e:
            st.write("Chart loading...")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 💬 Let's Find Your Perfect Skis!")
        
        if not st.session_state.conversation_started:
            st.markdown("""
            Hi there! I'm your personal ski concierge with over 20 years of experience matching skiers with their perfect equipment.
            
            **Tell me about your skiing:** What's your experience level? What kind of terrain do you love? Any specific needs or budget considerations?
            
            You can either type your message or use the voice recorder below!
            """)
        
        # Voice input
        st.markdown("### 🎤 Voice Input")
        audio_bytes = audio_recorder(
            text="Click to record your message",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="2x",
        )
        
        # Text input
        st.markdown("### ⌨️ Text Input")
        text_input = st.text_area(
            "Or type your message here:",
            placeholder="Tell me about your skiing experience, what you're looking for, budget, etc.",
            height=100
        )
        
        # Process input
        user_message = ""
        
        if audio_bytes and st.session_state.voice_handler:
            with st.spinner("🎧 Processing your voice message..."):
                try:
                    user_message = st.session_state.voice_handler.transcribe_audio(audio_bytes)
                    st.success(f"You said: *{user_message}*")
                except Exception as e:
                    st.error(f"Error processing audio: {e}")
        
        elif text_input and st.button("Send Message", type="primary"):
            user_message = text_input
        
        # Generate response
        if user_message and st.session_state.ski_expert and st.session_state.openai_client:
            with st.spinner("🧠 Analyzing your needs..."):
                try:
                    ai_response, recommendations = st.session_state.ski_expert.generate_response(
                        user_message, 
                        st.session_state.openai_client
                    )
                    
                    st.session_state.conversation_started = True
                    st.session_state.current_recommendations = recommendations
                    
                    # Display AI response
                    with st.chat_message("assistant"):
                        st.write(ai_response)
                        
                        # Play audio response if voice was used
                        if audio_bytes and st.session_state.voice_handler:
                            try:
                                with st.spinner("🔊 Generating voice response..."):
                                    st.session_state.voice_handler.play_audio_response(ai_response)
                            except Exception as e:
                                st.warning("Audio response not available")
                
                except Exception as e:
                    st.error(f"Error generating response: {e}")
        
        # Display conversation history
        if st.session_state.ski_expert.conversation_history:
            st.markdown("---")
            render_conversation_history(st.session_state.ski_expert.conversation_history)
    
    with col2:
        st.markdown("## 🎿 Current Recommendations")
        
        if st.session_state.current_recommendations:
            render_ski_recommendations(st.session_state.current_recommendations)
        else:
            st.info("Share your skiing preferences and I'll recommend the perfect skis for you!")
        
        # Quick tips
        st.markdown("---")
        st.markdown("## 💡 Quick Tips")
        st.markdown("""
        **To get the best recommendations, tell me about:**
        - Your skiing ability (beginner/intermediate/advanced)
        - Favorite terrain (groomed runs, powder, all-mountain)
        - Your budget range
        - Height and weight
        - Current skis (if any)
        - How often you ski
        """)
        
        st.markdown("---")
        st.markdown("## 🏔️ Popular Categories")
        
        # Quick input buttons
        if st.button("🏂 All-Mountain Skis"):
            st.session_state.quick_message = "I'm looking for versatile all-mountain skis"
        
        if st.button("❄️ Powder Skis"):
            st.session_state.quick_message = "I want skis for deep powder skiing"
        
        if st.button("🏁 Carving Skis"):
            st.session_state.quick_message = "I love carving on groomed runs"
        
        if st.button("👶 Beginner Skis"):
            st.session_state.quick_message = "I'm a beginner looking for my first skis"

if __name__ == "__main__":
    main()