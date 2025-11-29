"""
Enhanced Math Renderer for ReportLab
Converts math expressions to better-formatted text/HTML for PDF rendering
"""

import re
from reportlab.lib.utils import ImageReader
import io

class MathRenderer:
    """Render mathematical expressions for ReportLab PDFs"""
    
    @staticmethod
    def format_math_expression(text):
        """
        Format mathematical expressions for better PDF rendering
        
        Converts:
        - Fractions: "3/4" → "¾" or "3/4" (styled)
        - Exponents: "x^2" → "x²"
        - Greek letters: "alpha" → "α"
        - Operators: "*" → "×"
        """
        if not text:
            return text
        
        # Replace common math operators
        text = text.replace('*', '×')
        text = text.replace('/', '÷')
        
        # Replace exponent notation
        text = re.sub(r'\^(\d+)', lambda m: MathRenderer._unicode_superscript(m.group(1)), text)
        
        # Replace fractions (simple cases)
        text = re.sub(r'(\d+)/(\d+)', MathRenderer._format_fraction, text)
        
        # Replace Greek letters
        greek_map = {
            'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
            'Alpha': 'Α', 'Beta': 'Β', 'Gamma': 'Γ', 'Delta': 'Δ'
        }
        for greek, unicode_char in greek_map.items():
            text = text.replace(greek, unicode_char)
        
        return text
    
    @staticmethod
    def _unicode_superscript(num_str):
        """Convert number to Unicode superscript"""
        superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
        }
        return ''.join(superscript_map.get(c, c) for c in num_str)
    
    @staticmethod
    def _format_fraction(match):
        """Format fraction (for now, just keep as-is with better spacing)"""
        num, den = match.groups()
        # Could use Unicode fractions: ½, ¼, ¾, etc.
        # For now, return styled fraction
        return f"{num}/{den}"
    
    @staticmethod
    def format_problem_text(problem_text):
        """
        Format entire problem text with math formatting
        
        Examples:
        - "x^2 + 3x = 0" → "x² + 3x = 0"
        - "3/4 + 1/2" → "¾ + ½" (or styled fractions)
        """
        return MathRenderer.format_math_expression(problem_text)
    
    @staticmethod
    def create_math_paragraph(expression, style):
        """Create a ReportLab Paragraph with formatted math"""
        from reportlab.platypus import Paragraph
        formatted = MathRenderer.format_problem_text(expression)
        return Paragraph(formatted, style)

