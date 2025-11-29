"""
AI Problem Generator
Generates math problems based on Kumon level and topic
Supports both OpenAI and OpenRouter.io
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ProblemGenerator:
    def __init__(self, model=None):
        # Determine provider
        ai_provider = os.getenv('AI_PROVIDER', 'openrouter').lower()
        
        # Get API key
        if ai_provider == 'openrouter':
            api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
            base_url = 'https://openrouter.ai/api/v1'
            default_model = 'openai/gpt-4'
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            base_url = None  # Use default OpenAI URL
            default_model = 'gpt-4'
        
        if not api_key:
            raise ValueError(
                f"{ai_provider.upper()}_API_KEY environment variable is not set. "
                "Please set OPENAI_API_KEY or OPENROUTER_API_KEY in your .env file"
            )
        
        # Initialize OpenAI client (OpenRouter is OpenAI-compatible)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Set model - use provided, env variable, or default
        self.model = model or os.getenv('OPENAI_MODEL') or default_model
        self.provider = ai_provider
    
    def generate_problems(self, level, topic, num_problems=10):
        """
        Generate math problems using AI based on Kumon level and topic
        
        Args:
            level: Kumon level (e.g., 'B', 'H')
            topic: Topic within that level (e.g., 'Multiplication tables (1-10)')
            num_problems: Number of problems to generate
            
        Returns:
            List of problem strings
        """
        prompt = f"""Generate {num_problems} Kumon-style math problems for Level {level}, topic: {topic}.

Requirements:
- Problems should follow Kumon's incremental difficulty approach
- Each problem should be on a separate line
- Format problems exactly as they would appear on a Kumon worksheet
- Use appropriate notation for the level (e.g., vertical format for Level B multiplication)
- Problems should progress in small, manageable steps
- Return ONLY the problems, one per line, no explanations

Generate the problems now:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating Kumon-style math problems that follow their structured, incremental approach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            problems_text = response.choices[0].message.content.strip()
            problems = [p.strip() for p in problems_text.split('\n') if p.strip()]
            
            # Ensure we have the right number of problems
            while len(problems) < num_problems:
                problems.extend(problems[:num_problems - len(problems)])
            
            return problems[:num_problems]
            
        except Exception as e:
            # Fallback: Generate simple problems if AI fails
            print(f"Error generating problems with AI: {e}")
            return self._generate_fallback_problems(level, topic, num_problems)
    
    def _generate_fallback_problems(self, level, topic, num_problems):
        """Generate basic problems as fallback"""
        problems = []
        for i in range(num_problems):
            if "multiplication" in topic.lower() and level == "B":
                # Simple multiplication problems
                import random
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                problems.append(f"{a} × {b} =")
            else:
                problems.append(f"Problem {i+1}")
        return problems

