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
    from src.working_continuous_voice import WorkingContinuousVoice, handle_voice_message_data
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
    defaults = {
        'ski_expert': SkiExpert(),
        'openai_client': None,
        'conversation_history': [],
        'current_recommendations': [],
        'voice_conversation_active': False
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
        # Mark voice conversation as active
        st.session_state.voice_conversation_active = True
        
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
        
        # Update current recommendations
        st.session_state.current_recommendations = recommendations
        
        return ai_response
        
    except Exception as e:
        error_response = f"I apologize, I encountered an error: {str(e)}. Please try again."
        return error_response

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    # 🎿 Ski Concierge - Continuous Voice Agent
    ### Talk naturally and I'll respond with voice in real-time!
    """)
    
    # API Key check
    if not st.session_state.openai_client:
        st.error("🔑 **OpenAI API Key Required for Voice Features**")
        
        with st.expander("💡 Enter API Key to Activate Voice"):
            temp_key = st.text_input("OpenAI API Key:", type="password")
            if temp_key and st.button("🔓 Activate Voice Agent", type="primary"):
                try:
                    client = openai.OpenAI(api_key=temp_key)
                    # Test the key
                    client.models.list()
                    
                    st.session_state.openai_client = client
                    st.success("✅ Voice agent activated! Ready for conversation.")
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Invalid API key: {str(e)}")
        st.stop()
    
    # JavaScript message handler
    handle_voice_message_data()
    
    # Main layout
    voice_col, sidebar_col = st.columns([2, 1])
    
    with voice_col:
        # Continuous voice dialog interface
        voice_agent = WorkingContinuousVoice(
            st.session_state.openai_client,
            handle_voice_input
        )
        voice_agent.render_continuous_voice_dialog()
        
        # Voice conversation examples (for testing)
        st.markdown("---")
        st.markdown("### 🗣️ Quick Voice Examples (Click to Test)")
        st.info("Use these buttons to test the voice conversation system!")
        
        example_cols = st.columns(2)
        
        voice_examples = [
            "I'm an intermediate skier looking for all-mountain skis under $600",
            "I ski powder in Colorado about 15 days a year, what do you recommend?",
            "What's the difference between these ski recommendations?",
            "Help me choose the right ski length for my height and weight",
            "Show me some alternatives in different price ranges", 
            "I need skis for carving on groomed runs on the East Coast"
        ]
        
        for i, example in enumerate(voice_examples):
            col = example_cols[i % 2]
            with col:
                if st.button(f"🎤 \"{example[:30]}...\"", key=f"voice_test_{i}", help=example):
                    # Process as voice input
                    ai_response = handle_voice_input(example)
                    st.success(f"✅ **Processed:** {example}")
                    st.info(f"🎿 **Response:** {ai_response[:100]}...")
                    st.rerun()
    
    with sidebar_col:
        # Voice status
        st.markdown("## 🎤 Voice Status")
        
        if st.session_state.voice_conversation_active:
            st.success("✅ Voice conversation active")
        else:
            st.info("🎤 Ready to start voice conversation")
        
        st.markdown("""
        **Voice Features:**
        - 🎤 Speech Recognition: Active
        - 🧠 AI Processing: Ready
        - 🔊 Voice Response: Enabled
        - 💬 Continuous Dialog: Available
        """)
        
        # Current recommendations
        if st.session_state.current_recommendations:
            st.markdown("## 🎿 Current Recommendations")
            for i, ski in enumerate(st.session_state.current_recommendations, 1):
                with st.expander(f"{i}. {ski['name']}", expanded=False):
                    st.write(f"**Price:** {ski['price_range']}")
                    st.write(f"**Why:** {ski['description'][:100]}...")
        
        # Recent conversation
        if st.session_state.conversation_history:
            st.markdown("## 💬 Recent Conversation")
            # Show last 3 exchanges
            for exchange in st.session_state.conversation_history[-3:]:
                st.write(f"**You:** {exchange['user'][:40]}...")
                st.write(f"**Me:** {exchange['assistant'][:40]}...")
                st.markdown("---")
        
        # Reset conversation
        if st.button("🔄 Reset Conversation", use_container_width=True):
            st.session_state.ski_expert.reset_conversation()
            st.session_state.conversation_history = []
            st.session_state.current_recommendations = []
            st.session_state.voice_conversation_active = False
            st.success("✨ Conversation reset! Ready for fresh start.")
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()