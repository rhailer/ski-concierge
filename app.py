import streamlit as st
import openai
import sys
import os
import time
from typing import Dict, List, Any

# Setup imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.ski_expert import SkiExpert
    from src.text_interface import EnhancedTextInterface, SmartFollowUp
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

# Production-ready CSS with Austrian aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main > div {
        padding-top: 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Header */
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
    
    .ski-header::before {
        content: '⛷️';
        position: absolute;
        top: 1rem;
        left: 2rem;
        font-size: 3rem;
        opacity: 0.1;
        animation: float 3s ease-in-out infinite;
    }
    
    .ski-header::after {
        content: '🎿';
        position: absolute;
        top: 1rem;
        right: 2rem;
        font-size: 3rem;
        opacity: 0.1;
        animation: float 3s ease-in-out infinite reverse;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
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
    
    /* Quick Selectors */
    .selectors-container {
        background: white;
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 12px 48px rgba(0,0,0,0.08);
        border: 1px solid #e8f4f8;
    }
    
    .selector-section {
        margin: 2rem 0;
    }
    
    .selector-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e3c72;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .selector-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
    }
    
    .quick-button {
        padding: 1.25rem 1.5rem;
        border: 2px solid #e1f5fe;
        border-radius: 18px;
        background: linear-gradient(135deg, #f8fffe, #e8f8ff);
        color: #1e3c72;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .quick-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .quick-button:hover {
        border-color: #2196f3;
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.25);
    }
    
    .quick-button:hover::before {
        left: 100%;
    }
    
    .quick-button.selected {
        background: linear-gradient(135deg, #1976d2, #1565c0);
        color: white;
        border-color: #1565c0;
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(21, 101, 192, 0.4);
    }
    
    .quick-button.selected::after {
        content: '✓';
        position: absolute;
        top: 0.75rem;
        right: 1rem;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    /* Conversation Interface */
    .conversation-card {
        background: white;
        border-radius: 30px;
        padding: 3rem;
        margin: 2rem 0;
        box-shadow: 0 16px 64px rgba(0,0,0,0.08);
        border: 1px solid #f0f8ff;
        position: relative;
    }
    
    .conversation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1976d2, #42a5f5, #1976d2);
        border-radius: 30px 30px 0 0;
    }
    
    .message-thread {
        margin: 2rem 0;
        max-height: 500px;
        overflow-y: auto;
        padding-right: 1rem;
    }
    
    .message-thread::-webkit-scrollbar {
        width: 6px;
    }
    
    .message-thread::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .message-thread::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #1976d2, #42a5f5);
        border-radius: 10px;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 8px 25px;
        margin: 1.5rem 0 1.5rem auto;
        max-width: 85%;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        word-wrap: break-word;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 25px 8px;
        margin: 1.5rem auto 1.5rem 0;
        max-width: 85%;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        border-left: 4px solid #1976d2;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        animation: slideInLeft 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
    
    /* Follow-up Questions */
    .follow-ups {
        margin: 2rem 0;
        padding: 1.5rem;
        background: linear-gradient(135deg, #e8f5e8, #f3e5f5);
        border-radius: 20px;
        border-left: 4px solid #4caf50;
    }
    
    .follow-up-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2e7d32;
        margin-bottom: 1rem;
    }
    
    .follow-up-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 0.75rem;
    }
    
    .follow-up-button {
        background: white;
        border: 1px solid #c8e6c9;
        border-radius: 15px;
        padding: 0.75rem 1rem;
        color: #2e7d32;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        text-align: left;
    }
    
    .follow-up-button:hover {
        background: #e8f5e8;
        border-color: #4caf50;
        transform: translateX(5px);
    }
    
    /* Recommendations */
    .recommendations-section {
        background: white;
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 12px 48px rgba(0,0,0,0.08);
        border: 1px solid #f0f8ff;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 2px solid #e3f2fd;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #4caf50, #66bb6a, #4caf50);
    }
    
    .recommendation-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        border-color: #1976d2;
    }
    
    .ski-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: #1e3c72;
        margin: 0 0 1.5rem 0;
        line-height: 1.3;
    }
    
    .ski-price {
        display: inline-block;
        background: linear-gradient(135deg, #ff5722, #d84315);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(255, 87, 34, 0.3);
        letter-spacing: 0.5px;
    }
    
    .ski-description {
        color: #37474f;
        line-height: 1.8;
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
    }
    
    .specs-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f5f5, #eeeeee);
        border-radius: 20px;
    }
    
    .spec-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    
    .spec-card:hover {
        transform: translateY(-3px);
    }
    
    .spec-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #607d8b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
    }
    
    .spec-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e3c72;
        font-family: 'Inter', sans-serif;
    }
    
    .retailers-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .retailer-link {
        display: block;
        background: linear-gradient(135deg, #00acc1, #0097a7);
        color: white !important;
        padding: 1rem 1.5rem;
        border-radius: 25px;
        text-decoration: none !important;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 20px rgba(0, 172, 193, 0.3);
        letter-spacing: 0.5px;
    }
    
    .retailer-link:hover {
        background: linear-gradient(135deg, #0097a7, #00838f);
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0, 172, 193, 0.4);
        text-decoration: none !important;
        color: white !important;
    }
    
    /* Profile Card */
    .profile-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
    }
    
    .profile-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .profile-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1.25rem 0;
        font-weight: 500;
        font-size: 1.05rem;
        padding: 0.75rem;
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1976d2, #1565c0) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 25px rgba(25, 118, 210, 0.3) !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.5px !important;
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1565c0, #0d47a1) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 40px rgba(25, 118, 210, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-2px) !important;
    }
    
    /* Form Elements */
    .stTextArea > div > div > textarea {
        border-radius: 20px !important;
        border: 2px solid #e3f2fd !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1.5rem !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #1976d2 !important;
        box-shadow: 0 0 25px rgba(25, 118, 210, 0.2) !important;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .ski-title {
            font-size: 2.5rem;
        }
        
        .ski-subtitle {
            font-size: 1.1rem;
        }
        
        .selector-grid {
            grid-template-columns: 1fr;
        }
        
        .specs-grid {
            grid-template-columns: 1fr;
        }
        
        .user-message, .assistant-message {
            max-width: 95%;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'ski_expert': SkiExpert(),
        'text_interface': None,
        'quick_selections': {
            'skill_level': None,
            'terrain_preference': None,
            'budget_range': None,
            'skiing_frequency': None
        },
        'current_recommendations': [],
        'conversation_started': False,
        'last_ai_response': "",
        'follow_up_questions': [],
        'openai_client': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize OpenAI client and text interface
    if not st.session_state.openai_client:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if api_key:
            st.session_state.openai_client = openai.OpenAI(api_key=api_key)
            st.session_state.text_interface = EnhancedTextInterface(st.session_state.openai_client)

def process_user_input(user_input: str) -> tuple[str, List[Dict[str, Any]]]:
    """Process user input and return AI response and recommendations"""
    if not user_input.strip():
        return "", []
    
    try:
        # Update profile with quick selections
        for key, value in st.session_state.quick_selections.items():
            if value and value != st.session_state.ski_expert.user_profile.get(key):
                st.session_state.ski_expert.user_profile[key] = value
        
        # Generate AI response
        ai_response, recommendations = st.session_state.ski_expert.generate_response(
            user_input, 
            st.session_state.openai_client
        )
        
        # Update session state
        st.session_state.current_recommendations = recommendations
        st.session_state.conversation_started = True
        st.session_state.last_ai_response = ai_response
        
        # Generate smart follow-up questions
        st.session_state.follow_up_questions = SmartFollowUp.generate_follow_ups(
            st.session_state.ski_expert.user_profile,
            ai_response
        )
        
        return ai_response, recommendations
        
    except Exception as e:
        st.error(f"❌ Error processing input: {str(e)}")
        return "I'm sorry, I encountered an error. Please try rephrasing your question.", []

def render_quick_selectors():
    """Render enhanced quick selector interface"""
    st.markdown('<div class="selectors-container">', unsafe_allow_html=True)
    
    # Skill Level Section
    st.markdown('<div class="selector-section">', unsafe_allow_html=True)
    st.markdown('<div class="selector-title">🎿 What\'s your skiing level?</div>', unsafe_allow_html=True)
    
    skill_cols = st.columns(4)
    skills = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    
    for i, skill in enumerate(skills):
        with skill_cols[i]:
            selected = st.session_state.quick_selections['skill_level'] == skill.lower()
            button_type = "primary" if selected else "secondary"
            
            if st.button(
                f"{'✓ ' if selected else ''}{skill}",
                key=f"skill_{skill}",
                type=button_type,
                help=f"Select if you're a {skill.lower()} skier",
                use_container_width=True
            ):
                st.session_state.quick_selections['skill_level'] = skill.lower()
                ai_response, recommendations = process_user_input(f"I'm a {skill.lower()} skier")
                if ai_response:
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Terrain Preference Section
    st.markdown('<div class="selector-section">', unsafe_allow_html=True)
    st.markdown('<div class="selector-title">🏔️ What terrain do you prefer?</div>', unsafe_allow_html=True)
    
    terrain_cols = st.columns(4)
    terrains = [
        ('All-Mountain', 'all-mountain'),
        ('Powder', 'powder'),
        ('Carving/Groomers', 'carving'),
        ('Park/Freestyle', 'park')
    ]
    
    for i, (display, value) in enumerate(terrains):
        with terrain_cols[i]:
            selected = st.session_state.quick_selections['terrain_preference'] == value
            button_type = "primary" if selected else "secondary"
            
            if st.button(
                f"{'✓ ' if selected else ''}{display}",
                key=f"terrain_{value}",
                type=button_type,
                help=f"Select if you prefer {display.lower()} skiing",
                use_container_width=True
            ):
                st.session_state.quick_selections['terrain_preference'] = value
                ai_response, recommendations = process_user_input(f"I prefer {display.lower()} skiing")
                if ai_response:
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Budget and Frequency in one row
    budget_freq_cols = st.columns(2)
    
    with budget_freq_cols[0]:
        st.markdown('<div class="selector-title">💰 Budget Range</div>', unsafe_allow_html=True)
        budgets = ['Under $400', '$400-600', '$600-800', '$800+']
        
        for budget in budgets:
            selected = st.session_state.quick_selections['budget_range'] == budget
            button_type = "primary" if selected else "secondary"
            
            if st.button(
                f"{'✓ ' if selected else ''}{budget}",
                key=f"budget_{budget}",
                type=button_type,
                help=f"Select if your budget is {budget}",
                use_container_width=True
            ):
                st.session_state.quick_selections['budget_range'] = budget
                ai_response, recommendations = process_user_input(f"My budget is {budget}")
                if ai_response:
                    st.rerun()
    
    with budget_freq_cols[1]:
        st.markdown('<div class="selector-title">⏰ How often do you ski?</div>', unsafe_allow_html=True)
        frequencies = ['Rarely (1-5 days)', 'Occasionally (5-15 days)', 'Frequently (15-30 days)', 'Very Often (30+ days)']
        
        for freq in frequencies:
            selected = st.session_state.quick_selections['skiing_frequency'] == freq
            button_type = "primary" if selected else "secondary"
            
            if st.button(
                f"{'✓ ' if selected else ''}{freq}",
                key=f"freq_{freq}",
                type=button_type,
                help=f"Select if you ski {freq.lower()}",
                use_container_width=True
            ):
                st.session_state.quick_selections['skiing_frequency'] = freq
                ai_response, recommendations = process_user_input(f"I ski {freq.lower()}")
                if ai_response:
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_conversation_interface():
    """Render the main conversation interface"""
    st.markdown('<div class="conversation-card">', unsafe_allow_html=True)
    
    if st.session_state.text_interface:
        # Get user input
        user_input = st.session_state.text_interface.render_conversation_interface()
        
        if user_input:
            # Process the input
            ai_response, recommendations = process_user_input(user_input)
            if ai_response:
                st.rerun()
    
    # Display conversation history
    if st.session_state.ski_expert.conversation_history:
        st.markdown("### 💬 Our Conversation")
        st.markdown('<div class="message-thread">', unsafe_allow_html=True)
        
        for exchange in st.session_state.ski_expert.conversation_history:
            # User message
            st.markdown(f"""
            <div class="user-message">
                {exchange['user']}
            </div>
            """, unsafe_allow_html=True)
            
            # Assistant message
            st.markdown(f"""
            <div class="assistant-message">
                {exchange['assistant']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Audio response option for last message
        if st.session_state.last_ai_response and st.session_state.text_interface:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.session_state.text_interface.offer_audio_response(st.session_state.last_ai_response)
    
    # Smart follow-up questions
    if st.session_state.follow_up_questions and st.session_state.conversation_started:
        st.markdown('<div class="follow-ups">', unsafe_allow_html=True)
        st.markdown('<div class="follow-up-title">💡 Questions I can help with:</div>', unsafe_allow_html=True)
        
        follow_up_cols = st.columns(2)
        for i, question in enumerate(st.session_state.follow_up_questions[:4]):  # Show top 4
            col = follow_up_cols[i % 2]
            with col:
                if st.button(f"❓ {question}", key=f"followup_{i}"):
                    ai_response, recommendations = process_user_input(question)
                    if ai_response:
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_recommendations():
    """Render ski recommendations with enhanced styling"""
    st.markdown('<div class="recommendations-section">', unsafe_allow_html=True)
    
    if st.session_state.current_recommendations:
        st.markdown("## 🎿 Your Perfect Ski Matches")
        
        for i, ski in enumerate(st.session_state.current_recommendations, 1):
            st.markdown(f"""
            <div class="recommendation-card">
                <div class="ski-name">{i}. {ski['name']}</div>
                <div class="ski-price">{ski['price_range']}</div>
                <div class="ski-description">{ski['description']}</div>
                
                <div class="specs-grid">
                    <div class="spec-card">
                        <div class="spec-label">Length Range</div>
                        <div class="spec-value">{ski.get('specs', {}).get('length', 'Various')}</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">Waist Width</div>
                        <div class="spec-value">{ski.get('specs', {}).get('waist', 'N/A')}</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">Turn Radius</div>
                        <div class="spec-value">{ski.get('specs', {}).get('radius', 'N/A')}</div>
                    </div>
                </div>
                
                <div class="retailers-grid">
                    {"".join([
                        f'<a href="{link}" target="_blank" class="retailer-link">Shop at {retailer}</a>' 
                        for retailer, link in ski.get('retailers', {}).items()
                    ])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional help section
        st.markdown("---")
        st.markdown("### 🤔 Need more help deciding?")
        
        help_cols = st.columns(3)
        with help_cols[0]:
            if st.button("📊 Compare these options", use_container_width=True):
                ai_response, _ = process_user_input("Can you compare these ski recommendations and help me choose between them?")
                if ai_response:
                    st.rerun()
        
        with help_cols[1]:
            if st.button("📏 Help with sizing", use_container_width=True):
                ai_response, _ = process_user_input("Can you help me determine the right ski length for my height and weight?")
                if ai_response:
                    st.rerun()
        
        with help_cols[2]:
            if st.button("🔍 Show similar options", use_container_width=True):
                ai_response, _ = process_user_input("Can you show me some similar ski options in different price ranges?")
                if ai_response:
                    st.rerun()
    
    else:
        # Empty state with clear call to action
        st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem; color: #607d8b;'>
            <div style='font-size: 4rem; margin-bottom: 2rem;'>🎿</div>
            <h2 style='color: #1e3c72; margin-bottom: 1.5rem; font-family: "Playfair Display", serif;'>
                Ready to find your perfect skis?
            </h2>
            <p style='font-size: 1.3rem; line-height: 1.6; margin-bottom: 2rem;'>
                Use the quick selectors above or start a conversation below!<br>
                I'll analyze your needs and recommend the ideal skis for you.
            </p>
            <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;'>
                <div style='padding: 1rem; background: #e8f5e8; border-radius: 15px; color: #2e7d32;'>
                    <strong>🎯 Personalized</strong><br>Based on your exact needs
                </div>
                <div style='padding: 1rem; background: #e3f2fd; border-radius: 15px; color: #1565c0;'>
                    <strong>💰 Current Pricing</strong><br>Real prices from top retailers
                </div>
                <div style='padding: 1rem; background: #fff3e0; border-radius: 15px; color: #ef6c00;'>
                    <strong>🔗 Direct Links</strong><br>Buy immediately when ready
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_user_profile():
    """Render user profile with enhanced styling"""
    profile = st.session_state.ski_expert.user_profile
    
    if profile and any(profile.values()):
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown('<div class="profile-title">👤 Your Skiing Profile</div>', unsafe_allow_html=True)
        
        if profile.get('skill_level'):
            st.markdown(f'<div class="profile-item">🎿 <strong>Skill Level:</strong> {profile["skill_level"].title()}</div>', unsafe_allow_html=True)
        
        if profile.get('terrain_preference'):
            terrain = profile['terrain_preference'].replace('-', ' ').title()
            st.markdown(f'<div class="profile-item">🏔️ <strong>Preferred Terrain:</strong> {terrain}</div>', unsafe_allow_html=True)
        
        if profile.get('budget_range'):
            st.markdown(f'<div class="profile-item">💰 <strong>Budget:</strong> {profile["budget_range"]}</div>', unsafe_allow_html=True)
        
        if profile.get('skiing_frequency'):
            st.markdown(f'<div class="profile-item">⏰ <strong>Frequency:</strong> {profile["skiing_frequency"]}</div>', unsafe_allow_html=True)
        
        # Additional profile details
        additional_info = []
        for key, value in profile.items():
            if key not in ['skill_level', 'terrain_preference', 'budget_range', 'skiing_frequency'] and value and value != 'unknown':
                if key == 'physical_stats':
                    additional_info.append(f"📏 <strong>Physical:</strong> {value}")
                elif key == 'current_skis':
                    additional_info.append(f"⛷️ <strong>Current Skis:</strong> {value}")
                elif key == 'specific_needs':
                    additional_info.append(f"🎯 <strong>Needs:</strong> {value}")
        
        for info in additional_info:
            st.markdown(f'<div class="profile-item">{info}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="ski-header">
        <h1 class="ski-title">🎿 Ski Concierge</h1>
        <p class="ski-subtitle">Expert guidance to find your perfect skis through natural conversation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key check
    if not st.session_state.openai_client:
        st.error("🔑 **OpenAI API Key Required**")
        st.markdown("""
        To use the Ski Concierge, you need an OpenAI API key for the AI conversation features.
        
        **How to set it up:**
        1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
        2. Set it as an environment variable: `OPENAI_API_KEY=your_key_here`
        3. Or add it to your Streamlit secrets
        """)
        
        with st.expander("💡 Enter API Key Temporarily (for testing)"):
            temp_key = st.text_input("OpenAI API Key:", type="password", help="This will only be stored for this session")
            if temp_key and st.button("🔓 Set API Key", type="primary"):
                try:
                    client = openai.OpenAI(api_key=temp_key)
                    # Test the key
                    client.models.list()
                    
                    st.session_state.openai_client = client
                    st.session_state.text_interface = EnhancedTextInterface(client)
                    st.success("✅ API key verified! You can now use the Ski Concierge.")
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Invalid API key: {str(e)}")
        
        st.stop()
    
    # Quick Selectors
    render_quick_selectors()
    
    # Main Layout
    conversation_col, recommendations_col = st.columns([3, 2], gap="large")
    
    with conversation_col:
        render_conversation_interface()
    
    with recommendations_col:
        render_recommendations()
        render_user_profile()
        
        # Reset Button
        st.markdown("---")
        if st.button("🔄 Start Fresh Conversation", type="secondary", use_container_width=True):
            # Reset everything
            st.session_state.ski_expert.reset_conversation()
            st.session_state.quick_selections = {k: None for k in st.session_state.quick_selections}
            st.session_state.current_recommendations = []
            st.session_state.conversation_started = False
            st.session_state.last_ai_response = ""
            st.session_state.follow_up_questions = []
            st.success("✨ Fresh start! Ready for a new conversation.")
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()