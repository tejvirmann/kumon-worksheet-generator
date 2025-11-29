"""
AI-Powered Layout Generator
Uses AI to determine optimal formatting, sizing, and layout for problems on the worksheet
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LayoutGenerator:
    """Uses AI to determine optimal problem layout and formatting"""
    
    def __init__(self):
        # Determine provider
        ai_provider = os.getenv('AI_PROVIDER', 'openrouter').lower()
        
        # Get API key
        if ai_provider == 'openrouter':
            api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
            base_url = 'https://openrouter.ai/api/v1'
            default_model = 'openai/gpt-4'
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            base_url = None
            default_model = 'gpt-4'
        
        if not api_key:
            raise ValueError("API key not found. Set OPENROUTER_API_KEY or OPENAI_API_KEY")
        
        extra_headers = {}
        if ai_provider == 'openrouter':
            extra_headers = {
                "HTTP-Referer": os.getenv('OPENROUTER_REFERER', 'http://localhost:5000'),
                "X-Title": os.getenv('OPENROUTER_TITLE', 'Kumon Worksheet Generator')
            }
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=extra_headers
        )
        self.model = os.getenv('OPENAI_MODEL', default_model)
    
    def generate_layout_spec(self, problems, level, topic, num_problems):
        """
        Use AI to determine optimal layout specifications for displaying problems
        
        Returns:
            dict with layout specs: font_size, spacing, columns, problem_format
        """
        # Create prompt for AI
        problems_text = "\n".join([f"  {i+1}. {p}" for i, p in enumerate(problems[:5])])  # Show first 5
        
        prompt = f"""Analyze these {num_problems} math problems for a Kumon worksheet (Level {level}, Topic: {topic}) and determine the optimal layout specifications.

Problems (first 5 shown):
{problems_text}
... and {num_problems - 5} more similar problems

Determine the best layout specifications in JSON format:
{{
  "font_size": <10-14, based on problem complexity>,
  "spacing_between_problems": <0.3-0.7 inches>,
  "use_two_columns": <true/false>,
  "problem_format": "<formatting instructions>",
  "justification": "<brief explanation of choices>"
}}

Consider:
- Problem complexity and length
- Need for work space
- Readability
- Kumon worksheet standards (Level {level})
- Typical format for "{topic}" problems

Return ONLY valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a layout expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            import json
            result_text = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            layout_spec = json.loads(result_text)
            return layout_spec
            
        except Exception as e:
            print(f"Layout generation failed: {e}, using defaults")
            # Return sensible defaults based on level
            is_advanced = level in ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
            return {
                "font_size": 10 if is_advanced else 11,
                "spacing_between_problems": 0.4 if is_advanced else 0.6,
                "use_two_columns": is_advanced and len(problems) > 6,
                "problem_format": "standard",
                "justification": "Default layout based on level"
            }

