import streamlit as st
import openai
import sys
import os
import time

# Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.ski_expert import SkiExpert
    from src.real_continuous_voice import RealContinuousVoice, render_js_handler
    from config.settings import Config
except ImportError as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="🎿 Ski Concierge - Continuous Voice",
    page_icon="🎿",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state"""
    defaults = {
        'ski_expert': SkiExpert(),
        'openai_client': None,
        'conversation_history': [],
        'current_recommendations': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize OpenAI client
    if not st.session_state.openai_client:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if api_key:
            st.session_state.openai_client = openai.OpenAI(api_key=api_key)

def handle_voice_input(user_speech: str) -> str:
    """Handle voice input and return AI response"""
    try:
        # Get AI response
        ai_response, recommendations = st.session_state.ski_expert.generate_response(
            user_speech,
            st.session_state.openai_client
        )
        
        # Store conversation
        st.session_state.conversation_history.append({
            'user': user_speech,
            'assistant': ai_response,
            'recommendations': recommendations
        })
        
        st.session_state.current_recommendations = recommendations
        
        return ai_response
        
    except Exception as e:
        return f"I apologize, there was an error: {str(e)}. Please try again."

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    # 🎿 Ski Concierge - Continuous Voice Agent
    ### Talk naturally and I'll respond in real-time!
    """)
    
    # API Key check
    if not st.session_state.openai_client:
        st.error("🔑 OpenAI API Key Required")
        with st.expander("Enter API Key"):
            temp_key = st.text_input("API Key:", type="password")
            if temp_key and st.button("Activate Voice Agent"):
                try:
                    client = openai.OpenAI(api_key=temp_key)
                    client.models.list()
                    st.session_state.openai_client = client
                    st.success("✅ Voice agent ready!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Invalid key: {e}")
        st.stop()
    
    # JavaScript handler
    render_js_handler()
    
    # Main voice interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Continuous voice dialog
        voice_agent = RealContinuousVoice(st.session_state.openai_client, handle_voice_input)
        voice_agent.render_continuous_voice_dialog()
    
    with col2:
        # Live recommendations
        if st.session_state.current_recommendations:
            st.markdown("## 🎿 Current Recommendations")
            for i, ski in enumerate(st.session_state.current_recommendations, 1):
                with st.expander(f"{i}. {ski['name']} - {ski['price_range']}"):
                    st.write(ski['description'])

if __name__ == "__main__":
    main()