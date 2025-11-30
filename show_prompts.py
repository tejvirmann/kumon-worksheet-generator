#!/usr/bin/env python3
"""
Show exact prompts sent to AI and token counts
"""

import os
import sys
from problem_generator import ProblemGenerator
from layout_generator import LayoutGenerator

def estimate_tokens(text):
    """
    Rough token estimation: ~4 characters per token for English text
    More accurate: tiktoken library, but this is a quick estimate
    """
    # Rough estimate: 1 token ≈ 4 characters
    # System messages add overhead
    return len(text) // 4

def show_problem_prompt(level="H", topic="Linear equations", num_problems=10):
    """Show the exact problem generation prompt"""
    print("=" * 70)
    print("1. PROBLEM GENERATION PROMPT")
    print("=" * 70)
    
    # Create generator instance to access the prompt method
    try:
        gen = ProblemGenerator()
        prompt = gen._create_topic_specific_prompt(level, topic, num_problems)
        
        system_message = "Generate math problems only. No code, explanations, or extra text. Just problems."
        
        print("\n📤 SYSTEM MESSAGE:")
        print("-" * 70)
        print(system_message)
        print()
        
        print("\n📤 USER PROMPT:")
        print("-" * 70)
        print(prompt)
        print()
        
        # Calculate tokens
        system_tokens = estimate_tokens(system_message)
        prompt_tokens = estimate_tokens(prompt)
        total_input_tokens = system_tokens + prompt_tokens
        
        # Max tokens from code
        estimated_output = (num_problems * 30) + 50
        max_tokens = min(max(estimated_output, 200), 500)
        
        print("\n💰 TOKEN COUNT:")
        print("-" * 70)
        print(f"System message:     ~{system_tokens} tokens")
        print(f"User prompt:        ~{prompt_tokens} tokens")
        print(f"Total input:        ~{total_input_tokens} tokens")
        print(f"Max output tokens:  {max_tokens} tokens")
        print(f"Total estimated:    ~{total_input_tokens + max_tokens} tokens")
        print()
        
        return total_input_tokens + max_tokens
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

def show_layout_prompt(problems, level="H", topic="Linear equations", num_problems=10):
    """Show the exact layout generation prompt"""
    print("=" * 70)
    print("2. LAYOUT GENERATION PROMPT")
    print("=" * 70)
    
    try:
        gen = LayoutGenerator()
        
        # Create the prompt (same logic as in generate_layout_spec)
        problems_text = "\n".join([f"  {i+1}. {p}" for i, p in enumerate(problems[:5])])
        
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
        
        system_message = "You are a layout expert. Return only valid JSON."
        
        print("\n📤 SYSTEM MESSAGE:")
        print("-" * 70)
        print(system_message)
        print()
        
        print("\n📤 USER PROMPT:")
        print("-" * 70)
        print(prompt)
        print()
        
        # Calculate tokens
        system_tokens = estimate_tokens(system_message)
        prompt_tokens = estimate_tokens(prompt)
        total_input_tokens = system_tokens + prompt_tokens
        max_tokens = 300  # From layout_generator.py
        
        print("\n💰 TOKEN COUNT:")
        print("-" * 70)
        print(f"System message:     ~{system_tokens} tokens")
        print(f"User prompt:        ~{prompt_tokens} tokens")
        print(f"Total input:        ~{total_input_tokens} tokens")
        print(f"Max output tokens:  {max_tokens} tokens")
        print(f"Total estimated:    ~{total_input_tokens + max_tokens} tokens")
        print()
        
        return total_input_tokens + max_tokens
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    # Example usage
    level = sys.argv[1] if len(sys.argv) > 1 else "H"
    topic = sys.argv[2] if len(sys.argv) > 2 else "Linear equations"
    num_problems = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    print("\n")
    print("🔍 ANALYZING PROMPTS AND TOKEN USAGE")
    print("=" * 70)
    print(f"Level: {level}")
    print(f"Topic: {topic}")
    print(f"Number of Problems: {num_problems}")
    print()
    
    # Show problem generation prompt
    problem_tokens = show_problem_prompt(level, topic, num_problems)
    
    # Generate some example problems for layout prompt
    print("\n" + "=" * 70)
    print("3. EXAMPLE PROBLEMS (for layout generation)")
    print("=" * 70)
    example_problems = [
        "3x + 7 = 2x - 5",
        "2(x + 3) = 4x - 1",
        "5x - 8 = 3x + 12",
        "x/2 + 5 = 3x - 7",
        "4(x - 2) = 2x + 10"
    ]
    print("\nExample problems that would be analyzed:")
    for i, p in enumerate(example_problems[:5], 1):
        print(f"  {i}. {p}")
    print()
    
    # Show layout generation prompt
    layout_tokens = show_layout_prompt(example_problems, level, topic, num_problems)
    
    # Total summary
    print("\n" + "=" * 70)
    print("📊 TOTAL TOKEN SUMMARY")
    print("=" * 70)
    print(f"Problem Generation:  ~{problem_tokens} tokens")
    print(f"Layout Generation:   ~{layout_tokens} tokens")
    print(f"TOTAL PER WORKSHEET: ~{problem_tokens + layout_tokens} tokens")
    print()
    print("💡 Note: This is a rough estimate (1 token ≈ 4 characters)")
    print("   Actual token counts may vary slightly based on the model used.")
    print()

