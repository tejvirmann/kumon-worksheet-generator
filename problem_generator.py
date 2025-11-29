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
        prompt = f"""You are generating {num_problems} Kumon-style math problems for Level {level}, topic: {topic}.

CRITICAL REQUIREMENTS:
- Generate ACTUAL math problems, NOT placeholders like "Problem 1" or "Solve this"
- Each problem must be a complete, solvable mathematical expression
- Problems should follow Kumon's incremental difficulty approach
- Format problems exactly as they would appear on a Kumon worksheet
- Use appropriate notation for the level (e.g., vertical format for Level B multiplication like "  3\\n× 4\\n---")
- Problems should progress in small, manageable steps
- Return ONLY the problems, one per line, with NO numbering, NO explanations, NO labels
- For algebra problems, include the full equation (e.g., "(x - 3) / 2 - (x - 5) / 6 =")
- For multiplication, show the actual multiplication (e.g., "3 × 4 =")

Example output format:
3 × 4 =
5 × 7 =
(x - 3) / 2 - (x - 5) / 6 =
2x + 5 = 11

Generate {num_problems} problems now:"""

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
            
            # Clean up the problems - remove numbering, labels, etc.
            lines = problems_text.split('\n')
            problems = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Remove common prefixes like "1. ", "(1) ", "Problem 1: ", etc.
                import re
                line = re.sub(r'^(\d+[\.\)\:]|\(?\d+\)|Problem\s+\d+\:?\s*)', '', line, flags=re.IGNORECASE)
                line = line.strip()
                # Skip if it's just a placeholder or explanation
                if line and not any(word in line.lower() for word in ['problem', 'solve', 'find', 'calculate', 'example', 'note']):
                    problems.append(line)
            
            # Filter out invalid problems
            valid_problems = [p for p in problems if p and len(p) > 2 and not p.startswith('Problem')]
            
            # If we got good problems, use them; otherwise generate fallback
            if len(valid_problems) >= num_problems:
                return valid_problems[:num_problems]
            elif len(valid_problems) > 0:
                # Fill remaining with variations
                while len(valid_problems) < num_problems:
                    valid_problems.extend(valid_problems[:num_problems - len(valid_problems)])
                return valid_problems[:num_problems]
            else:
                # Fall back to generated problems
                print("Warning: AI didn't generate valid problems, using fallback generator")
                return self._generate_fallback_problems(level, topic, num_problems)
            
        except Exception as e:
            # Fallback: Generate simple problems if AI fails
            print(f"Error generating problems with AI: {e}")
            return self._generate_fallback_problems(level, topic, num_problems)
    
    def _generate_fallback_problems(self, level, topic, num_problems):
        """Generate basic problems as fallback"""
        import random
        problems = []
        
        topic_lower = topic.lower()
        
        for i in range(num_problems):
            if "multiplication" in topic_lower and level == "B":
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                problems.append(f"{a} × {b} =")
            elif "addition" in topic_lower or level == "A":
                a = random.randint(1, 15)
                b = random.randint(1, 15)
                problems.append(f"{a} + {b} =")
            elif "subtraction" in topic_lower:
                a = random.randint(10, 20)
                b = random.randint(1, a-1)
                problems.append(f"{a} - {b} =")
            elif "fraction" in topic_lower or level in ["E", "F"]:
                num1, den1 = random.randint(1, 9), random.randint(2, 9)
                num2, den2 = random.randint(1, 9), random.randint(2, 9)
                problems.append(f"{num1}/{den1} + {num2}/{den2} =")
            elif "equation" in topic_lower or level in ["G", "H", "I", "J", "K"]:
                a, b = random.randint(1, 9), random.randint(1, 9)
                c = random.randint(5, 20)
                problems.append(f"{a}x + {b} = {c}")
            else:
                # Generic problem
                a = random.randint(2, 10)
                b = random.randint(2, 10)
                problems.append(f"{a} × {b} =")
        
        return problems

