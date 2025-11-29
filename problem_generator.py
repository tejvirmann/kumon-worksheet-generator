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
        # OpenRouter may require additional headers
        extra_headers = {}
        if ai_provider == 'openrouter':
            extra_headers = {
                "HTTP-Referer": os.getenv('OPENROUTER_REFERER', 'http://localhost:5000'),
                "X-Title": os.getenv('OPENROUTER_TITLE', 'Kumon Worksheet Generator')
            }
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=extra_headers if extra_headers else None
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
        # Create topic-specific prompt with detailed instructions
        prompt = self._create_topic_specific_prompt(level, topic, num_problems)
        

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating Kumon-style math problems that follow their structured, incremental approach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500
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
            error_msg = str(e)
            print(f"Error generating problems with AI: {e}")
            
            # Provide helpful error message for 401 errors
            if "401" in error_msg or "User not found" in error_msg or "authentication" in error_msg.lower():
                print("\n⚠️  OpenRouter API Authentication Error!")
                print("This usually means:")
                print("  1. Your API key is invalid or expired")
                print("  2. Your OpenRouter account needs to be verified")
                print("  3. You need to add credits to your OpenRouter account")
                print("\nTo fix:")
                print("  1. Check your API key at: https://openrouter.ai/keys")
                print("  2. Verify your account is active")
                print("  3. Make sure you have credits in your account")
                print("\nUsing fallback problem generator for now...\n")
            
            return self._generate_fallback_problems(level, topic, num_problems)
    
    def _create_topic_specific_prompt(self, level, topic, num_problems):
        """Create a detailed, topic-specific prompt for better problem generation"""
        topic_lower = topic.lower()
        
        # Topic-specific examples and instructions
        topic_instructions = {
            "multiplication tables": f"""
TOPIC-SPECIFIC REQUIREMENTS for "{topic}":
- Generate multiplication problems from the {topic} range
- Start with easier facts (like 2×3, 3×2) and gradually increase difficulty
- Mix up the order - don't just do tables sequentially
- Include problems like: 3 × 4 =, 7 × 8 =, 5 × 9 =
- Make problems interesting with variety in difficulty progression
- Use horizontal format: "3 × 4 ="
""",
            "multiplication": f"""
TOPIC-SPECIFIC REQUIREMENTS for "{topic}":
- Generate single-digit multiplication problems appropriate for Level {level}
- Progress from easier (like 2×3) to harder (like 9×8)
- Use horizontal format: "4 × 7 ="
- Make problems varied and engaging, not just sequential tables
""",
            "addition": f"""
TOPIC-SPECIFIC REQUIREMENTS for "{topic}":
- Generate addition problems appropriate for Level {level}
- For Level B: vertical addition with carrying (e.g., "  23\n+ 45\n----")
- For Level A: horizontal addition up to 20 (e.g., "7 + 9 =")
- Progress in small increments of difficulty
- Make problems interesting with number patterns
""",
            "subtraction": f"""
TOPIC-SPECIFIC REQUIREMENTS for "{topic}":
- Generate subtraction problems appropriate for Level {level}
- For Level B: vertical subtraction with borrowing
- For Level A: horizontal subtraction from numbers up to 20
- Ensure all problems have positive results (no negative numbers)
- Progress from easier to harder problems
""",
            "linear equations": f"""
TOPIC-SPECIFIC REQUIREMENTS for "{topic}":
- Generate linear equations in one variable: ax + b = c
- Start simple (e.g., "2x + 3 = 11") and progress to more complex
- Include equations with fractions: "(x - 3) / 2 = 5"
- Include equations requiring distribution: "3(x + 2) = 15"
- End with "=" (not "?" or "solve for x")
- Make problems progressively more interesting and challenging
""",
            "simultaneous equations": f"""
TOPIC-SPECIFIC REQUIREMENTS for "{topic}":
- Generate systems of two linear equations
- Format: "2x + 3y = 11\nx - y = 1"
- Start with simple integer solutions
- Progress to more complex coefficients
- Each problem should be two equations separated by newline
""",
            "fractions": f"""
TOPIC-SPECIFIC REQUIREMENTS for "{topic}":
- Generate fraction operation problems appropriate for Level {level}
- For adding: "1/3 + 2/5 ="
- For subtracting: "5/6 - 1/4 ="
- For multiplying: "2/3 × 3/4 ="
- For dividing: "3/4 ÷ 1/2 ="
- Use proper fraction notation with horizontal bars
- Progress from like denominators to unlike denominators
""",
            "quadratic": f"""
TOPIC-SPECIFIC REQUIREMENTS for "{topic}":
- Generate quadratic equations or functions
- Format equations: "x² + 5x + 6 = 0" or "x² - 4x + 3 = 0"
- Include problems requiring factoring: "(x + 2)(x + 3) ="
- Progress from simple to complex
- Use proper mathematical notation
""",
        }
        
        # Find matching instruction
        instruction = ""
        for key in topic_instructions:
            if key in topic_lower:
                instruction = topic_instructions[key]
                break
        
        base_prompt = f"""You are generating {num_problems} Kumon-style math problems for Level {level}, topic: "{topic}".

CRITICAL REQUIREMENTS:
- Generate ACTUAL, SPECIFIC math problems that directly relate to the topic "{topic}"
- Each problem must be a complete, solvable mathematical expression
- Problems must be TOPIC-SPECIFIC - they must clearly demonstrate the topic "{topic}"
- Follow Kumon's incremental difficulty approach - start easier, gradually increase
- Format problems exactly as they would appear on a Kumon worksheet
- Make problems INTERESTING and VARIED - don't just repeat the same pattern
- Return ONLY the problems, one per line, with NO numbering, NO explanations, NO labels
- Use appropriate mathematical notation for Level {level}
{instruction}
EXAMPLE OUTPUT FORMAT (adapt to your topic):
3 × 4 =
7 × 9 =
5 × 8 =
6 × 7 =

Generate {num_problems} SPECIFIC, TOPIC-RELATED, INTERESTING problems for "{topic}" now. 
Each problem must clearly relate to the topic and be progressively more challenging:"""
        
        return base_prompt
    
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

