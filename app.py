import streamlit as st
import openai
import sys
import os
import time
import asyncio
from typing import Dict, List, Any

# Setup imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.ski_expert import SkiExpert
    from config.settings import Config
    from data.ski_database import get_ski_recommendations
except ImportError as e:
    st.error(f"❌ Setup Error: {e}")
    st.error("Please ensure all project files are properly set up.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="🎿 Ski Concierge",
    page_icon="🎿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS (keeping existing styles but fixing HTML rendering)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* All previous CSS styles remain the same... */
    .main > div {
        padding-top: 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .ski-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e3c72 100%);
        color: white;
        padding: 4rem 2rem;
        margin: -1rem -1rem 3rem -1rem;
        border-radius: 0 0 40px 40px;
        text-align: center;
        position: relative;
        box-shadow: 0 10px 40px rgba(30, 60, 114, 0.3);
    }
    
    .ski-title {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(45deg, #fff, #e3f2fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .ski-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 300;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        letter-spacing: 0.5px;
    }
    
    /* Continuous Conversation Styles */
    .continuous-chat {
        background: white;
        border-radius: 30px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 16px 64px rgba(0,0,0,0.08);
        border: 1px solid #f0f8ff;
        min-height: 500px;
        position: relative;
    }
    
    .chat-input-container {
        position: sticky;
        bottom: 0;
        background: white;
        border-radius: 25px;
        border: 2px solid #e3f2fd;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .chat-messages {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    
    .typing-indicator {
        background: #f8f9fa;
        padding: 1rem 1.5rem;
        border-radius: 25px 25px 25px 8px;
        margin: 1rem 0;
        max-width: 200px;
        border-left: 4px solid #1976d2;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 8px 25px;
        margin: 1.5rem 0 1.5rem auto;
        max-width: 80%;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.4s ease-out;
        word-wrap: break-word;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 25px 8px;
        margin: 1.5rem auto 1.5rem 0;
        max-width: 80%;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        border-left: 4px solid #1976d2;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        animation: slideInLeft 0.4s ease-out;
        word-wrap: break-word;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Quick Actions */
    .quick-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .quick-action-btn {
        background: #e3f2fd;
        border: 1px solid #1976d2;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        color: #1976d2;
    }
    
    .quick-action-btn:hover {
        background: #1976d2;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Fixed Spec and Retailer Styles */
    .spec-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
        padding: 1.5rem;
        background: #f8f9fa;
        border-radius: 15px;
    }
    
    .spec-item {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .spec-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    
    .spec-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1976d2;
    }
    
    .retailer-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .retailer-btn {
        display: block;
        background: linear-gradient(135deg, #00acc1, #0097a7);
        color: white;
        padding: 1rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 172, 193, 0.3);
    }
    
    .retailer-btn:hover {
        background: linear-gradient(135deg, #0097a7, #00838f);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 172, 193, 0.4);
        color: white;
        text-decoration: none;
    }
    
    /* Input styles */
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        border: 2px solid #e3f2fd !important;
        padding: 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1976d2 !important;
        box-shadow: 0 0 20px rgba(25, 118, 210, 0.2) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1976d2, #1565c0) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(25, 118, 210, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'ski_expert': SkiExpert(),
        'conversation_history': [],
        'current_recommendations': [],
        'is_typing': False,
        'message_counter': 0,
        'openai_client': None,
        'conversation_context': ""
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize OpenAI client
    if not st.session_state.openai_client:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if api_key:
            st.session_state.openai_client = openai.OpenAI(api_key=api_key)

def process_message(user_input: str):
    """Process user message and get AI response"""
    if not user_input.strip():
        return
    
    # Add user message to history
    st.session_state.conversation_history.append({
        'role': 'user', 
        'content': user_input,
        'timestamp': time.time()
    })
    
    # Show typing indicator
    st.session_state.is_typing = True
    
    try:
        # Generate AI response
        ai_response, recommendations = st.session_state.ski_expert.generate_response(
            user_input, 
            st.session_state.openai_client
        )
        
        # Add AI response to history
        st.session_state.conversation_history.append({
            'role': 'assistant', 
            'content': ai_response,
            'recommendations': recommendations,
            'timestamp': time.time()
        })
        
        # Update recommendations
        st.session_state.current_recommendations = recommendations
        
        # Update conversation context for continuous flow
        st.session_state.conversation_context = f"Last exchange: User said '{user_input}' and I responded with recommendations for {len(recommendations)} skis."
        
    except Exception as e:
        st.session_state.conversation_history.append({
            'role': 'assistant', 
            'content': f"I apologize, I encountered an error: {str(e)}. Please try rephrasing your question.",
            'timestamp': time.time()
        })
    
    finally:
        st.session_state.is_typing = False
        st.session_state.message_counter += 1

def render_chat_message(message: Dict[str, Any], key: str):
    """Render a single chat message"""
    if message['role'] == 'user':
        st.markdown(f"""
        <div class="user-message">
            {message['content']}
        </div>
        """, unsafe_allow_html=True)
    
    else:  # assistant
        st.markdown(f"""
        <div class="assistant-message">
            {message['content']}
        </div>
        """, unsafe_allow_html=True)
        
        # Show recommendations if present
        if message.get('recommendations'):
            render_inline_recommendations(message['recommendations'], key)

def render_inline_recommendations(recommendations: List[Dict[str, Any]], key: str):
    """Render recommendations inline with proper HTML"""
    if not recommendations:
        return
    
    st.markdown("### 🎿 My Recommendations:")
    
    for i, ski in enumerate(recommendations, 1):
        # Ski name and price
        st.markdown(f"**{i}. {ski['name']}** - **{ski['price_range']}**")
        
        # Description
        st.markdown(ski['description'])
        
        # Specs using Streamlit columns (fixes HTML rendering issue)
        if ski.get('specs'):
            st.markdown("**Specifications:**")
            spec_cols = st.columns(3)
            
            specs = ski['specs']
            with spec_cols[0]:
                st.metric("Length", specs.get('length', 'N/A'))
            with spec_cols[1]:
                st.metric("Waist Width", specs.get('waist', 'N/A'))
            with spec_cols[2]:
                st.metric("Turn Radius", specs.get('radius', 'N/A'))
        
        # Retailers using Streamlit columns (fixes HTML rendering issue)
        if ski.get('retailers'):
            st.markdown("**Where to Buy:**")
            retailer_cols = st.columns(len(ski['retailers']))
            
            for j, (retailer, link) in enumerate(ski['retailers'].items()):
                with retailer_cols[j]:
                    st.link_button(f"🛒 {retailer}", link, use_container_width=True)
        
        if i < len(recommendations):  # Add separator between recommendations
            st.markdown("---")

def render_continuous_chat():
    """Render the continuous chat interface"""
    st.markdown('<div class="continuous-chat">', unsafe_allow_html=True)
    
    # Chat header
    st.markdown("### 💬 Continuous Conversation")
    st.markdown("Ask follow-up questions, compare options, or get more details about any recommendations!")
    
    # Messages container
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        if st.session_state.conversation_history:
            st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
            
            for i, message in enumerate(st.session_state.conversation_history):
                render_chat_message(message, f"msg_{i}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Show typing indicator
        if st.session_state.is_typing:
            st.markdown('<div class="typing-indicator">🤔 Thinking about your perfect skis...</div>', unsafe_allow_html=True)
    
    # Quick action buttons for continuous conversation
    if st.session_state.current_recommendations:
        st.markdown("### 💡 Quick Questions:")
        
        quick_cols = st.columns(3)
        
        with quick_cols[0]:
            if st.button("🔄 Compare these options", key="compare_btn"):
                process_message("Can you compare these ski recommendations and help me choose between them?")
                st.rerun()
        
        with quick_cols[1]:
            if st.button("📏 Help with sizing", key="sizing_btn"):
                process_message("What ski length would be best for me based on my height and skiing style?")
                st.rerun()
        
        with quick_cols[2]:
            if st.button("💰 Show alternatives", key="alternatives_btn"):
                process_message("Can you show me similar skis in different price ranges?")
                st.rerun()
        
        # More specific follow-ups
        follow_up_cols = st.columns(2)
        
        with follow_up_cols[0]:
            if st.button("❓ What makes these different?", key="differences_btn"):
                process_message("What are the key differences between these ski recommendations?")
                st.rerun()
        
        with follow_up_cols[1]:
            if st.button("🎿 Any other options?", key="more_options_btn"):
                process_message("Are there any other skis you'd recommend that we haven't discussed?")
                st.rerun()
    
    # Continuous input at bottom
    st.markdown("---")
    
    # Input form that stays at bottom
    with st.form(key=f"continuous_chat_{st.session_state.message_counter}", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "", 
                placeholder="Ask me anything about skis, compare options, or get more details...",
                key=f"chat_input_{st.session_state.message_counter}"
            )
        
        with col2:
            submitted = st.form_submit_button("Send", type="primary", use_container_width=True)
        
        if submitted and user_input:
            process_message(user_input)
            st.rerun()
    
    # Example prompts for continuous conversation
    if not st.session_state.conversation_history:
        st.markdown("### 🎯 Start the conversation:")
        
        starter_examples = [
            "I'm an intermediate skier looking for all-mountain skis under $600",
            "I ski powder in Utah 15+ days a year, what do you recommend?",
            "What's the difference between carving and all-mountain skis?",
            "I'm 5'8\" 165lbs, what ski length should I get?",
            "I want to progress from intermediate to advanced, what skis?",
            "Show me the best women's skis for East Coast skiing"
        ]
        
        example_cols = st.columns(2)
        
        for i, example in enumerate(starter_examples):
            col = example_cols[i % 2]
            with col:
                if st.button(f"💬 {example}", key=f"starter_{i}"):
                    process_message(example)
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_recommendations_sidebar():
    """Render current recommendations in sidebar"""
    if st.session_state.current_recommendations:
        st.markdown("## 🎿 Current Recommendations")
        
        for i, ski in enumerate(st.session_state.current_recommendations, 1):
            with st.expander(f"{i}. {ski['name']} - {ski['price_range']}"):
                st.write(ski['description'])
                
                if ski.get('specs'):
                    specs = ski['specs']
                    st.write(f"**Length:** {specs.get('length', 'N/A')}")
                    st.write(f"**Waist:** {specs.get('waist', 'N/A')}")
                    st.write(f"**Radius:** {specs.get('radius', 'N/A')}")
                
                if ski.get('retailers'):
                    st.write("**Buy from:**")
                    for retailer, link in ski['retailers'].items():
                        st.markdown(f"[{retailer}]({link})")
        
        # Quick actions for current recommendations
        st.markdown("---")
        st.markdown("### 🤔 Need Help Deciding?")
        
        if st.button("Compare All Options", key="sidebar_compare", use_container_width=True):
            process_message("Please compare all these ski options and help me decide which is best for me")
            st.rerun()
        
        if st.button("Show Similar Skis", key="sidebar_similar", use_container_width=True):
            process_message("Can you show me some similar ski options to consider?")
            st.rerun()
    
    else:
        st.info("🎿 Start a conversation to get ski recommendations!")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="ski-header">
        <h1 class="ski-title">🎿 Ski Concierge</h1>
        <p class="ski-subtitle">Continuous conversation to find your perfect skis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key check
    if not st.session_state.openai_client:
        st.error("🔑 **OpenAI API Key Required**")
        
        with st.expander("💡 Enter API Key"):
            temp_key = st.text_input("OpenAI API Key:", type="password")
            if temp_key and st.button("🔓 Set API Key", type="primary"):
                try:
                    client = openai.OpenAI(api_key=temp_key)
                    client.models.list()  # Test the key
                    
                    st.session_state.openai_client = client
                    st.success("✅ API key verified!")
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Invalid API key: {str(e)}")
        st.stop()
    
    # Main layout
    chat_col, sidebar_col = st.columns([3, 1])
    
    with chat_col:
        render_continuous_chat()
    
    with sidebar_col:
        render_recommendations_sidebar()
        
        # Profile summary
        profile = st.session_state.ski_expert.user_profile
        if profile and any(profile.values()):
            st.markdown("## 👤 Your Profile")
            
            if profile.get('skill_level'):
                st.write(f"🎿 **Skill:** {profile['skill_level'].title()}")
            if profile.get('terrain_preference'):
                st.write(f"🏔️ **Terrain:** {profile['terrain_preference'].replace('-', ' ').title()}")
            if profile.get('budget'):
                st.write(f"💰 **Budget:** {profile['budget']}")
        
        # Reset button
        st.markdown("---")
        if st.button("🔄 New Conversation", use_container_width=True):
            # Reset everything
            st.session_state.ski_expert.reset_conversation()
            st.session_state.conversation_history = []
            st.session_state.current_recommendations = []
            st.session_state.message_counter = 0
            st.session_state.conversation_context = ""
            st.rerun()

if __name__ == "__main__":
    main()