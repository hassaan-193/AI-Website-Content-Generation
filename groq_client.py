import requests
import json
from typing import Dict, List

class GroqClient:
    """
    Handles all interactions with Groq API
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Send a chat request to Groq API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Response text from Groq
        """
        payload = {
            "model": "llama-3.3-70b-versatile",  # Fast and powerful Groq model
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"Groq API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    def analyze_business(self, description: str) -> Dict:
        """
        Analyze business description and extract key information
        """
        messages = [
            {
                "role": "system",
                "content": "You are a business analyst. Extract structured information from business descriptions."
            },
            {
                "role": "user",
                "content": f"""Analyze this business description and extract key information:

"{description}"

Return ONLY a valid JSON object with this exact structure (no markdown, no backticks, no extra text):
{{
  "business_type": "specific type of business",
  "industry": "industry category",
  "content_goal": "what content they need",
  "target_audience": "who they serve"
}}"""
            }
        ]
        
        response = self.chat(messages, temperature=0.3)
        # Clean response and parse JSON
        clean_response = response.strip()
        if clean_response.startswith("```"):
            # Remove markdown code blocks if present
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response.strip())
    
    def generate_questions(self, business_analysis: Dict) -> List[Dict]:
        """
        Generate smart questions based on business analysis
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert interviewer who asks insightful questions to understand businesses."
            },
            {
                "role": "user",
                "content": f"""Based on this business analysis:
Business Type: {business_analysis['business_type']}
Industry: {business_analysis['industry']}
Goal: {business_analysis['content_goal']}
Target Audience: {business_analysis.get('target_audience', 'General')}

Generate 6 essential questions to gather information for creating excellent website content.

Return ONLY a valid JSON array (no markdown, no backticks):
[
  {{
    "id": "q1",
    "question": "What specific products/services do you offer?",
    "purpose": "To understand the core offerings"
  }},
  {{
    "id": "q2",
    "question": "Who is your target audience?",
    "purpose": "To tailor the content appropriately"
  }},
  {{
    "id": "q3",
    "question": "What makes your business unique?",
    "purpose": "To highlight your competitive advantages"
  }},
  {{
    "id": "q4",
    "question": "What tone should the website have?",
    "purpose": "To match your brand personality"
  }},
  {{
    "id": "q5",
    "question": "What are your main business goals?",
    "purpose": "To align content with objectives"
  }},
  {{
    "id": "q6",
    "question": "What actions do you want visitors to take?",
    "purpose": "To create effective calls-to-action"
  }}
]"""
            }
        ]
        
        response = self.chat(messages, temperature=0.5)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response.strip())
    
    def generate_page_content(self, page_type: str, knowledge_base: Dict) -> str:
        """
        Generate content for a specific page type
        """
        messages = [
            {
                "role": "system",
                "content": f"You are a professional copywriter specializing in {page_type} page content for websites."
            },
            {
                "role": "user",
                "content": f"""Create compelling, professional content for a {page_type} page.

Business Information:
{json.dumps(knowledge_base, indent=2)}

Requirements:
- Write in a clear, engaging style
- Structure with section headings
- NO HTML or code, just plain text
- Make it human-friendly and persuasive
- Length: 300-500 words
- Match the business tone and audience

Write the {page_type} page content now:"""
            }
        ]
        
        return self.chat(messages, temperature=0.7, max_tokens=2000)