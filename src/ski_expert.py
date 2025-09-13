import json
import sys
import os
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.ski_database import get_ski_recommendations
from config.settings import Config

class SkiExpert:
    def __init__(self):
        self.user_profile = {}
        self.conversation_history = []
        
    def analyze_user_input(self, user_input: str, openai_client) -> Dict[str, Any]:
        """
        Analyze user input to extract skiing preferences and requirements
        """
        system_prompt = """
        You are an expert ski concierge. Analyze the user's input and extract key information about their skiing needs.
        
        Extract and categorize the following information:
        - skill_level: beginner, intermediate, advanced, or expert
        - terrain_preference: all-mountain, powder, carving, park, backcountry
        - budget: any mentioned price range
        - physical_stats: height, weight if mentioned
        - skiing_frequency: how often they ski
        - current_skis: what they currently use
        - specific_needs: any particular requirements or concerns
        - questions_to_ask: what additional information would be helpful
        
        Return your analysis as a JSON object with these keys. If information isn't provided, mark as "unknown".
        """
        
        try:
            response = openai_client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing user input: {e}")
            return {"error": "Failed to analyze input"}
    
    def generate_recommendations(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate ski recommendations based on user profile
        """
        skill_level = user_profile.get('skill_level', 'intermediate').lower()
        terrain_preference = user_profile.get('terrain_preference', 'all-mountain').lower()
        budget = user_profile.get('budget', 'unknown')
        
        # Get recommendations from database
        recommendations = get_ski_recommendations(
            skill_level=skill_level,
            terrain_preference=terrain_preference,
            budget_range=budget
        )
        
        return recommendations
    
    def generate_response(self, user_input: str, openai_client) -> tuple[str, List[Dict[str, Any]]]:
        """
        Generate conversational response and ski recommendations
        """
        # Analyze current input
        analysis = self.analyze_user_input(user_input, openai_client)
        
        # Update user profile with new information
        for key, value in analysis.items():
            if value != "unknown" and key != "questions_to_ask":
                self.user_profile[key] = value
        
        # Check if we have enough information for recommendations
        has_skill_level = 'skill_level' in self.user_profile and self.user_profile['skill_level'] != 'unknown'
        has_terrain_pref = 'terrain_preference' in self.user_profile and self.user_profile['terrain_preference'] != 'unknown'
        
        recommendations = []
        
        if has_skill_level and has_terrain_pref:
            recommendations = self.generate_recommendations(self.user_profile)
        
        # Generate conversational response
        conversation_context = f"""
        User Profile: {json.dumps(self.user_profile, indent=2)}
        Current Analysis: {json.dumps(analysis, indent=2)}
        Available Recommendations: {len(recommendations)} skis found
        
        Generate a friendly, expert response that:
        1. Acknowledges what the user shared
        2. If you have recommendations, introduce them enthusiastically
        3. If you need more information, ask specific follow-up questions
        4. Keep it conversational and expert-level
        5. Don't repeat information unnecessarily
        """
        
        system_prompt = """
        You are a world-class ski concierge with 20+ years of experience fitting skis to skiers.
        You're having a natural conversation to understand exactly what skis will be perfect for this person.
        
        Be enthusiastic, knowledgeable, and personable. Ask follow-up questions when needed.
        When you have enough information, confidently recommend specific skis with reasoning.
        
        Keep responses conversational and under 150 words unless providing detailed recommendations.
        """
        
        try:
            response = openai_client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User said: '{user_input}'\n\nContext: {conversation_context}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({
                "user": user_input,
                "assistant": ai_response,
                "recommendations": recommendations
            })
            
            return ai_response, recommendations
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm having trouble processing that right now. Could you try rephrasing your question?", []
    
    def reset_conversation(self):
        """Reset the conversation and user profile"""
        self.user_profile = {}
        self.conversation_history = []