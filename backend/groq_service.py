import os
from groq import Groq
from dotenv import load_dotenv, find_dotenv
import json

# Ensure we find the .env in the root project directory
load_dotenv(find_dotenv())

class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("Warning: GROQ_API_KEY not found in environment variables.")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    def get_recommendations(self, preferences, candidates):
        """
        Takes user preferences and unique candidates, returns exactly the Top 5 choices.
        """
        if not self.client:
            return {"error": "Groq API client not initialized. Please provide GROQ_API_KEY."}

        if not candidates:
            return {"recommendations": [], "message": "No restaurants found matching your criteria."}

        # Structure candidates for the prompt
        candidate_list = []
        for c in candidates:
            candidate_list.append({
                "name": c.get("name"),
                "location": c.get("location"),
                "full_address": c.get("address"),
                "cuisines": c.get("cuisines"),
                "rating": c.get("rate"),
                "price_for_two": c.get("approx_cost(for two people)")
            })

        system_prompt = """
        You are an elite Bangalore Food critic and Recommendation Expert. 
        Your task is to analyze the provided Top 15 candidates and pick exactly the Top 5 best matches for the user.
        
        Output MUST be in STRICT JSON format:
        {
            "recommendations": [
                {
                    "name": "Restaurant Name",
                    "full_address": "Complete detailed address as provided in data",
                    "rating": "User rating (e.g. 4.1/5 or 3.9)",
                    "price_for_two": "Approximate cost for two with currency symbol",
                    "recommendation_reason": "Exactly one compelling sentence explaining why this matches user preference."
                }
            ],
            "summary": "Short 2-sentence expert summary of your picks."
        }
        """

        user_prompt = f"""
        User Preferences:
        - Locality: {preferences.get('location', 'Any')}
        - Price Profile: {preferences.get('price_range', 'Any')}
        - Cuisine Tags: {preferences.get('cuisines', 'Any')}
        - Min Rating: {preferences.get('min_rating', 'Any')}
        
        Candidate Set (Unique matches from Bangalore dataset):
        {json.dumps(candidate_list, indent=2)}
        
        Expert Task: Pick the Top 5 and return the JSON.
        """

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return {"error": str(e), "message": "The AI is currently dining out. Using fallback data."}

# Singleton instance
groq_service = None

def get_groq_service():
    global groq_service
    if groq_service is None:
        groq_service = GroqService()
    return groq_service
