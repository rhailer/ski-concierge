import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Any

def render_ski_recommendations(recommendations: List[Dict[str, Any]]):
    """
    Render ski recommendations in an attractive format
    """
    if not recommendations:
        return
    
    st.markdown("### 🎿 My Recommendations for You")
    
    for i, ski in enumerate(recommendations, 1):
        with st.container():
            # Create columns for layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{i}. {ski['name']}**")
                st.markdown(f"💰 **Price:** {ski['price_range']}")
                st.markdown(f"📝 **Why I recommend this:** {ski['description']}")
                
                # Specs if available
                if 'specs' in ski:
                    specs = ski['specs']
                    st.markdown(f"📏 **Specs:** Length: {specs.get('length', 'N/A')}, Waist: {specs.get('waist', 'N/A')}, Radius: {specs.get('radius', 'N/A')}")
            
            with col2:
                st.markdown("**🛒 Where to Buy:**")
                for retailer, link in ski['retailers'].items():
                    st.markdown(f"[{retailer}]({link})")
            
            st.divider()

def render_conversation_history(conversation_history: List[Dict[str, Any]]):
    """
    Render conversation history in chat format
    """
    st.markdown("### 💬 Our Conversation")
    
    for exchange in conversation_history:
        # User message
        with st.chat_message("user"):
            st.write(exchange['user'])
        
        # Assistant message
        with st.chat_message("assistant"):
            st.write(exchange['assistant'])
            
            # Show recommendations if any
            if exchange.get('recommendations'):
                render_ski_recommendations(exchange['recommendations'])

def render_user_profile(user_profile: Dict[str, Any]):
    """
    Render user profile information
    """
    if not user_profile:
        return
    
    st.markdown("### 👤 Your Skiing Profile")
    
    cols = st.columns(3)
    
    with cols[0]:
        if 'skill_level' in user_profile:
            st.metric("Skill Level", user_profile['skill_level'].title())
    
    with cols[1]:
        if 'terrain_preference' in user_profile:
            st.metric("Preferred Terrain", user_profile['terrain_preference'].title())
    
    with cols[2]:
        if 'budget' in user_profile and user_profile['budget'] != 'unknown':
            st.metric("Budget", user_profile['budget'])
    
    # Additional profile info
    profile_details = []
    if 'skiing_frequency' in user_profile and user_profile['skiing_frequency'] != 'unknown':
        profile_details.append(f"**Frequency:** {user_profile['skiing_frequency']}")
    
    if 'physical_stats' in user_profile and user_profile['physical_stats'] != 'unknown':
        profile_details.append(f"**Physical Stats:** {user_profile['physical_stats']}")
    
    if 'current_skis' in user_profile and user_profile['current_skis'] != 'unknown':
        profile_details.append(f"**Current Skis:** {user_profile['current_skis']}")
    
    if profile_details:
        st.markdown(" | ".join(profile_details))

def create_skiing_terrain_chart():
    """
    Create an informative chart about different ski terrains
    """
    terrains = ['All-Mountain', 'Powder', 'Carving', 'Park', 'Backcountry']
    versatility = [95, 60, 40, 30, 70]
    difficulty = [50, 70, 30, 80, 90]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=versatility,
        theta=terrains,
        fill='toself',
        name='Versatility',
        line_color='#1f77b4'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=difficulty,
        theta=terrains,
        fill='toself',
        name='Difficulty Level',
        line_color='#ff7f0e'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Ski Terrain Characteristics",
        height=400
    )
    
    return fig