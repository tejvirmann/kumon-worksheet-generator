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
        # Reload environment variables to pick up any changes
        load_dotenv(override=True)
        
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
        
        # Debug: Print API key status (first 10 chars only for security)
        if api_key:
            print(f"✓ API key loaded (starts with: {api_key[:10]}...)")
        else:
            print("✗ API key not found!")
        
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
        

        # Calculate max_tokens dynamically based on number of problems needed
        # Estimate: ~30 tokens per problem (conservative estimate)
        # Add 50 tokens buffer for formatting/response overhead
        estimated_tokens = (num_problems * 30) + 50
        # Cap at 500 to stay within credit limits, minimum 200 for small requests
        max_tokens = min(max(estimated_tokens, 200), 500)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Generate math problems only. No code, explanations, or extra text. Just problems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            problems_text = response.choices[0].message.content.strip()
            
            # Debug: show what AI returned (first 500 chars)
            print(f"📝 AI returned ({len(problems_text)} chars): {problems_text[:500]}...")
            
            # Clean up the problems - remove numbering, labels, etc.
            lines = problems_text.split('\n')
            problems = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Remove common prefixes like "1. ", "(1) ", "Problem 1: ", etc.
                import re
                line = re.sub(r'^(\d+[\.\)\:]\s*|\(?\d+\)\s*|Problem\s+\d+\:?\s*)', '', line, flags=re.IGNORECASE)
                line = line.strip()
                
                # Skip empty lines or lines that are clearly not problems
                if not line or len(line) < 2:
                    continue
                
                # Skip code patterns
                if line.strip().startswith(('#', '//', '/*', 'def ', 'import ', 'function ', 'print(')):
                    continue
                
                # Skip lines that are clearly explanations (but allow math problems with equations)
                # Only skip if it's clearly an instruction/explanation, not a math expression
                skip_patterns = [r'^problem\s+\d+', r'^example\s+\d+', r'^note:', r'^hint:']
                if any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
                    continue
                
                # Accept if it looks like a math problem (has numbers, operators, or = sign)
                has_math = bool(re.search(r'[\d=+\-×÷/²^()]', line))
                # Or if it's a reasonable length word problem
                is_reasonable_length = 5 <= len(line) <= 200
                
                if has_math or is_reasonable_length:
                    problems.append(line)
            
            # Filter out invalid problems - be more lenient
            valid_problems = []
            for p in problems:
                if not p or len(p) < 2:
                    continue
                # Skip if it's clearly code
                if any(word in p.lower() for word in ['def ', 'function(', 'return ', 'import ', 'print(', 'def ']):
                    continue
                # Accept if it has math content or reasonable length
                if re.search(r'[\d=+\-×÷/²^()]', p) or (len(p) >= 5 and len(p) <= 200):
                    valid_problems.append(p)
            
            print(f"✅ Parsed {len(valid_problems)} valid problems from AI response")
            
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
            import traceback
            
            # Log full error details
            print(f"\n❌ Error generating problems with AI:")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {error_msg}")
            print(f"\n   Full traceback:")
            traceback.print_exc()
            
            # Provide helpful error message for specific error types
            if "401" in error_msg or "User not found" in error_msg or "authentication" in error_msg.lower() or "Unauthorized" in error_msg:
                print("\n⚠️  OpenRouter API Authentication Error!")
                print("This usually means:")
                print("  1. Your API key is invalid or expired")
                print("  2. Your OpenRouter account needs to be verified")
                print("  3. You need to add credits to your OpenRouter account")
                print("\nTo fix:")
                print("  1. Check your API key at: https://openrouter.ai/keys")
                print("  2. Verify your account is active")
                print("  3. Make sure you have credits in your account")
                print(f"  4. Current API key starts with: {os.getenv('OPENROUTER_API_KEY', 'NOT SET')[:10]}...")
            elif "402" in error_msg or "credits" in error_msg.lower() or "afford" in error_msg.lower():
                print("\n⚠️  OpenRouter API Credit Limit Error!")
                print("You don't have enough credits for this request.")
                
                # Try to extract the affordable token amount from error message
                import re
                afford_match = re.search(r'can only afford (\d+)', error_msg)
                if afford_match:
                    affordable_tokens = int(afford_match.group(1))
                    print(f"   Your account can afford up to {affordable_tokens} tokens.")
                    print(f"   Requested: {max_tokens} tokens")
                    print("   Tip: Try requesting fewer problems to use fewer tokens.")
                
                print("\nOptions:")
                print("  1. Add credits at: https://openrouter.ai/settings/credits")
                print("  2. Use fallback problem generator (works without API)")
                print("  3. Request fewer problems to use fewer tokens")
                print("\nUsing fallback problem generator for now...")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                print("\n⚠️  OpenRouter API Rate Limit Error!")
                print("You've exceeded the rate limit. Please wait a moment and try again.")
            elif "500" in error_msg or "502" in error_msg or "503" in error_msg:
                print("\n⚠️  OpenRouter API Server Error!")
                print("OpenRouter's servers are experiencing issues. Please try again later.")
            else:
                print(f"\n⚠️  Unknown API Error: {error_msg}")
            
            print("\nUsing fallback problem generator for now...\n")
            
            return self._generate_fallback_problems(level, topic, num_problems)
    
    def _create_topic_specific_prompt(self, level, topic, num_problems):
        """Create a detailed, topic-specific prompt for better problem generation - emphasizing difficulty"""
        topic_lower = topic.lower()
        
        # Topic-specific examples and instructions - MAKE PROBLEMS DIFFICULT
        topic_instructions = {
            "multiplication tables": f"- Challenging multiplication 1-10. Increase difficulty. Format: 7 × 8 = (one per line)\n",
            "multiplication": f"- Difficult multi-digit multiplication. Format: 47 × 39 = or more complex\n",
            "addition": f"- Complex addition with carrying. Level {level}. Format: 347 + 289 = or vertical if Level B\n",
            "subtraction": f"- Challenging subtraction with borrowing. Level {level}. Format: 534 - 267 =\n",
            "linear equations": f"- Complex linear equations: 3x + 7 = 2x - 5 or 2(x + 3) = 4x - 1. Increase difficulty progressively. End with =\n",
            "simultaneous equations": f"- Challenging systems. Format: 3x + 2y = 11\\n2x - y = 3\n",
            "fractions": f"- Complex fraction operations. Format: 2/3 + 5/6 = or 3/4 × 8/9 =\n",
            "quadratic": f"- Advanced quadratic equations: x² - 7x + 10 = 0 or y = 2(x - 3)² + 5. Increase complexity.\n",
            "word problem": f"- Challenging word problems. Multi-step, realistic scenarios. Level {level}.\n",
            "graph": f"- Advanced graph problems: Graph y = -x² + 4x - 3 or Graph y = 3x + 2. Graphs auto-generated.\n",
        }
        
        # Find matching instruction
        instruction = ""
        for key in topic_instructions:
            if key in topic_lower:
                instruction = topic_instructions[key]
                break
        
        # Streamlined prompt - no code, just problems - MAKE THEM DIFFICULT
        base_prompt = f"""Generate {num_problems} CHALLENGING math problems for Level {level}, topic: {topic}.

CRITICAL: Make these problems DIFFICULT and appropriately challenging for Level {level}.

Rules:
- Output ONLY problems, one per line, no numbering/explanations
- Problems should be CHALLENGING and require thought
- Start moderately difficult, then increase to very difficult
- Topic: {topic}
{instruction}
Format examples:
47 × 39 =
347 + 289 =
3x + 7 = 2x - 5

Generate {num_problems} CHALLENGING problems now:"""
        
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

