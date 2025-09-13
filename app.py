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
    from src.continuous_voice_agent import create_voice_agent_interface
    from config.settings import Config
except ImportError as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="🎿 Ski Concierge - Voice Agent",
    page_icon="🎿",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state"""
    if 'ski_expert' not in st.session_state:
        st.session_state.ski_expert = SkiExpert()
    
    if 'openai_client' not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if api_key:
            st.session_state.openai_client = openai.OpenAI(api_key=api_key)
        else:
            st.session_state.openai_client = None
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

def handle_voice_input(user_speech: str) -> str:
    """Handle voice input and return AI response"""
    try:
        # Get AI response using ski expert
        ai_response, recommendations = st.session_state.ski_expert.generate_response(
            user_speech,
            st.session_state.openai_client
        )
        
        # Store conversation
        st.session_state.conversation_history.append({
            'user': user_speech,
            'assistant': ai_response,
            'recommendations': recommendations,
            'timestamp': time.time()
        })
        
        # Store current recommendations
        st.session_state.current_recommendations = recommendations
        
        return ai_response
        
    except Exception as e:
        error_response = f"I'm sorry, I encountered an error: {str(e)}. Please try again."
        return error_response

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    # 🎿 Ski Concierge Voice Agent
    ## Continuous Voice Dialog to Find Your Perfect Skis
    
    **Talk naturally - I'll listen and respond just like a real conversation!**
    """)
    
    # API Key check
    if not st.session_state.openai_client:
        st.error("🔑 OpenAI API Key Required")
        with st.expander("Enter API Key"):
            temp_key = st.text_input("API Key:", type="password")
            if temp_key and st.button("Activate"):
                try:
                    client = openai.OpenAI(api_key=temp_key)
                    client.models.list()
                    st.session_state.openai_client = client
                    st.success("✅ Voice agent activated!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Invalid key: {e}")
        st.stop()
    
    # Main voice interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Continuous voice agent interface
        create_voice_agent_interface(
            st.session_state.openai_client,
            handle_voice_input
        )
    
    with col2:
        # Live recommendations
        if st.session_state.get('current_recommendations'):
            st.markdown("## 🎿 Live Recommendations")
            for i, ski in enumerate(st.session_state.current_recommendations, 1):
                st.write(f"**{i}. {ski['name']}**")
                st.write(f"💰 {ski['price_range']}")
                st.write(ski['description'][:100] + "...")
        
        # Conversation log
        if st.session_state.conversation_history:
            st.markdown("## 💬 Conversation")
            for exchange in st.session_state.conversation_history[-3:]:  # Last 3 exchanges
                st.write(f"**You:** {exchange['user'][:50]}...")
                st.write(f"**Me:** {exchange['assistant'][:50]}...")
                st.markdown("---")

if __name__ == "__main__":
    main()