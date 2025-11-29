"""
LaTeX-Based Worksheet Generator
Primary PDF generation using LaTeX with exact Kumon formatting
Based on ChatGPT's detailed font and layout recommendations
"""

import os
import subprocess
import tempfile
import shutil
from datetime import datetime
import json

# Try to ensure Tectonic is available (for serverless/Vercel)
try:
    from tectonic_setup import ensure_tectonic
    TECTONIC_AVAILABLE = True
except ImportError:
    TECTONIC_AVAILABLE = False

class LaTeXWorksheetGenerator:
    """Generate Kumon worksheets using LaTeX for perfect typography"""
    
    def __init__(self):
        self.load_design_spec()
    
    def load_design_spec(self):
        """Load design specifications"""
        try:
            with open('design_spec.json', 'r') as f:
                self.design = json.load(f)
        except:
            self.design = {
                "colors": {
                    "secondary": "#4B2E83",
                    "footer_text": "#808080"
                }
            }
    
    def escape_latex(self, text):
        """Escape LaTeX special characters"""
        if not text:
            return ""
        text = str(text)
        # Preserve math mode content (between $)
        parts = text.split('$')
        escaped_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Regular text
                part = part.replace('\\', r'\textbackslash{}')
                part = part.replace('{', r'\{')
                part = part.replace('}', r'\}')
                part = part.replace('&', r'\&')
                part = part.replace('%', r'\%')
                part = part.replace('$', r'\$')
                part = part.replace('#', r'\#')
                part = part.replace('_', r'\_')
                part = part.replace('~', r'\textasciitilde{}')
            escaped_parts.append(part)
        return '$'.join(escaped_parts)
    
    def format_math(self, problem_text):
        """Convert math notation to LaTeX math mode"""
        if not problem_text:
            return ""
        
        # Convert common math symbols
        problem_text = problem_text.replace('×', r'$\times$')
        problem_text = problem_text.replace('÷', r'$\div$')
        problem_text = problem_text.replace('≤', r'$\leq$')
        problem_text = problem_text.replace('≥', r'$\geq$')
        
        # Handle fractions like "3/4" -> "\frac{3}{4}"
        import re
        problem_text = re.sub(r'(\d+)/(\d+)', r'$\\frac{\1}{\2}$', problem_text)
        
        # Handle exponents like "x^2" -> "x^2" (LaTeX format)
        # But preserve if already in math mode
        
        return problem_text
    
    def generate_pdf(self, problems, level, topic, layout_style='medium_spaced', page_number=1, output_dir='output'):
        """
        Generate PDF worksheet using LaTeX
        
        Args:
            problems: List of problem strings
            level: Kumon level
            topic: Topic name
            layout_style: Layout style
            page_number: Page number (1, 2, etc.) - used for page identifiers (1a/1b, 2a/2b)
            output_dir: Output directory
            
        Returns:
            Path to generated PDF file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"kumon_level_{level}_{timestamp}"
        tex_filename = f"{base_filename}.tex"
        pdf_filename = f"{base_filename}.pdf"
        
        tex_path = os.path.join(output_dir, tex_filename)
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        # Determine layout settings
        is_advanced = level in ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        problem_font_size = 10 if is_advanced else 11
        problem_spacing = "0.4in" if is_advanced else "0.6in"
        use_two_columns = is_advanced
        
        # Split problems for front and back
        mid_point = len(problems) // 2
        front_problems = problems[:mid_point]
        back_problems = problems[mid_point:]
        
        # Generate LaTeX content
        latex_content = self._generate_latex_content(
            problems=problems,
            front_problems=front_problems,
            back_problems=back_problems,
            level=level,
            topic=topic,
            problem_font_size=problem_font_size,
            problem_spacing=problem_spacing,
            use_two_columns=use_two_columns,
            page_number=page_number
        )
        
        # Write LaTeX file
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Compile LaTeX to PDF
        try:
            self._compile_latex(tex_path, output_dir)
        except Exception as e:
            raise RuntimeError(f"LaTeX compilation failed: {str(e)}")
        
        if not os.path.exists(pdf_path):
            raise RuntimeError(f"PDF was not generated: {pdf_path}")
        
        return pdf_path
    
    def _generate_latex_content(self, problems, front_problems, back_problems, level, topic, 
                                problem_font_size, problem_spacing, use_two_columns, page_number=1):
        """Generate complete LaTeX document"""
        
        # Font colors
        header_color = self.design.get('colors', {}).get('secondary', '#4B2E83')
        footer_color = self.design.get('colors', {}).get('footer_text', '#808080')
        
        # Convert hex colors to LaTeX xcolor format
        def hex_to_xcolor(hex_color):
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return f"{{{r},{g},{b}}}"
        
        header_rgb = hex_to_xcolor(header_color)
        
        # Format page identifiers
        front_page_id = f"{level} {page_number} a"
        back_page_id = f"{level} {page_number} b"
        
        latex = f"""% Kumon Worksheet - Level {level}
% Topic: {topic}
% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
% Compile with: xelatex or lualatex

\\documentclass[12pt]{{article}}
\\usepackage[paper=letterpaper,top=0.15in,bottom=0.75in,left=0.75in,right=0.75in]{{geometry}}
\\setlength{{\\topskip}}{{0pt}}
\\setlength{{\\parskip}}{{0pt}}
\\setlength{{\\topmargin}}{{0pt}}
\\setlength{{\\headheight}}{{0pt}}
\\setlength{{\\headsep}}{{0pt}}
\\usepackage{{fontspec}}
\\usepackage{{amsmath}}
\\usepackage{{enumitem}}
\\usepackage{{tikz}}
\\usepackage{{xcolor}}
\\usepackage{{graphicx}}
\\usepackage{{array}}
\\usepackage{{iftex}}

% Fonts matching Kumon style (ChatGPT recommendations)
% Kumon uses Arial for most text - this matches exactly
\\setsansfont{{Arial}}[BoldFont={{Arial-Bold}}, BoldItalicFont={{Arial-BoldItalic}}]
\\setmainfont{{Times New Roman}}
\\newfontfamily{{\\kumonfont}}{{Arial}}[BoldFont={{Arial-Bold}}]

% Logo uses Futura Rounded or Avenir Next Rounded (fallback to Arial Bold)
\\newfontfamily{{\\kumonlogo}}{{Arial-Bold}}  % Futura Rounded / Avenir Next Rounded if available

% Level identifier uses Futura or Avenir (fallback to Arial Bold)
\\newfontfamily{{\\kumonlevel}}{{Arial-Bold}}  % Futura / Avenir if available

% Colors
\\definecolor{{kumonpurple}}{{{header_rgb}}}
\\definecolor{{footertext}}{{RGB}}{{128,128,128}}

\\pagestyle{{empty}}

\\begin{{document}}

% ==================== FRONT PAGE ====================

% Header: Logo and level identifier (top-left) - at very top of page
\\noindent
\\begin{{minipage}}[t]{{0.25\\textwidth}}
{{\\kumonlogo\\fontsize{{18}}{{22}}\\selectfont\\textcolor{{kumonpurple}}{{KUMON\\textregistered}}}}\\\\[0pt]
{{\\kumonlevel\\fontsize{{14}}{{18}}\\selectfont\\textcolor{{kumonpurple}}{{{self.escape_latex(front_page_id)}}}}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.50\\textwidth}}
\\centering
{{\\kumonfont\\bfseries\\fontsize{{16}}{{20}}\\selectfont\\textcolor{{kumonpurple}}{{{self.escape_latex(topic)}}}}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.18\\textwidth}}
\\raggedleft
{{\\kumonfont\\fontsize{{10}}{{12}}\\selectfont\\textcolor{{kumonpurple}}{{{level}}}}}
\\end{{minipage}}

\\vspace{{0.02in}}

% Student information fields - Arial regular weight (not bold) - moved up
\\noindent{{\\sffamily\\fontsize{{11}}{{13}}\\selectfont Time : \\underline{{\\hspace{{2cm}}}} to : \\underline{{\\hspace{{1.5cm}}}} \\quad Date: \\underline{{\\hspace{{2cm}}}} \\quad Name: \\underline{{\\hspace{{3cm}}}}}}

\\vspace{{0.06in}}

% Performance tracking table - percentages bold, mistake labels regular/small
\\begin{{center}}
{{\\sffamily\\fontsize{{10}}{{12}}\\selectfont
\\fbox{{\\parbox[c][1.5em][c]{{1.2in}}{{\\centering\\bfseries 100\\%\\\\\\normalfont\\small (mistakes) 0}}}}
\\hspace{{4pt}}
\\fbox{{\\parbox[c][1.5em][c]{{1.2in}}{{\\centering\\bfseries 90\\%\\\\\\normalfont\\small --}}}}
\\hspace{{4pt}}
\\fbox{{\\parbox[c][1.5em][c]{{1.2in}}{{\\centering\\bfseries 80\\%\\\\\\normalfont\\small 1}}}}
\\hspace{{4pt}}
\\fbox{{\\parbox[c][1.5em][c]{{1.2in}}{{\\centering\\bfseries 70\\%\\\\\\normalfont\\small --}}}}
\\hspace{{4pt}}
\\fbox{{\\parbox[c][1.5em][c]{{1.2in}}{{\\centering\\bfseries 69\\%\\sim\\\\\\normalfont\\small 2\\sim}}}}
}}
\\end{{center}}

\\vspace{{0.2in}}

% Problems section
"""
        
        # Add front page problems
        if use_two_columns:
            latex += self._generate_two_column_problems(front_problems, problem_font_size, problem_spacing, start_num=1)
        else:
            latex += self._generate_single_column_problems(front_problems, problem_font_size, problem_spacing, start_num=1)
        
        # Footer on front page
        latex += """
\\vfill
\\begin{{minipage}}{{0.3in}}
\\rotatebox{{90}}{{
\\textcolor{{footertext}}{{\\tiny © 2002 Kumon Institute of Education}}
}}
\\end{{minipage}}
\\hfill

\\newpage

% ==================== BACK PAGE ====================

% Simplified header for back page with page number (b)
\\noindent
{{\\kumonfont\\bfseries\\large\\textcolor{{kumonpurple}}{{{self.escape_latex(back_page_id)}}}}}

\\vspace{{0.2in}}

"""
        
        # Add back page problems
        if use_two_columns:
            latex += self._generate_two_column_problems(back_problems, problem_font_size, problem_spacing, start_num=len(front_problems) + 1)
        else:
            latex += self._generate_single_column_problems(back_problems, problem_font_size, problem_spacing, start_num=len(front_problems) + 1)
        
        # Footer on back page
        latex += """
\\vfill
\\begin{{minipage}}{{0.3in}}
\\rotatebox{{90}}{{
\\textcolor{{footertext}}{{\\tiny © 2002 Kumon Institute of Education}}
}}
\\end{{minipage}}
\\hfill

\\end{{document}}
"""
        
        return latex
    
    def _generate_single_column_problems(self, problems, font_size, spacing, start_num=1):
        """Generate single-column problem list with proper formatting"""
        latex = "\\begin{enumerate}[label=(\\arabic*),leftmargin=*,itemsep=" + spacing + ",topsep=0pt,labelsep=0.3em]\n"
        
        for i, problem in enumerate(problems):
            problem_num = start_num + i
            # Format math in problem
            formatted_problem = self.format_math(problem)
            escaped_problem = self.escape_latex(formatted_problem)
            # Use Arial font (sans-serif) for problems, with proper spacing
            latex += f"    \\item{{\\sffamily\\fontsize{{{font_size}}}{{{int(font_size*1.15)}}}\\selectfont {escaped_problem}}}\n"
        
        latex += "\\end{enumerate}\n"
        return latex
    
    def _generate_two_column_problems(self, problems, font_size, spacing, start_num=1):
        """Generate two-column problem layout"""
        mid = (len(problems) + 1) // 2
        left_problems = problems[:mid]
        right_problems = problems[mid:]
        
        # Two-column layout - simpler approach with manual positioning
        latex = "\\noindent\n"
        latex += "\\begin{minipage}[t]{0.48\\textwidth}\n"
        latex += "\\begin{enumerate}[label=(\\arabic*),leftmargin=*,itemsep=" + spacing + ",topsep=0pt,start=" + str(start_num) + "]\n"
        
        # Left column problems
        for i, problem in enumerate(left_problems):
            formatted_problem = self.format_math(problem)
            escaped_problem = self.escape_latex(formatted_problem)
            # Use Arial font (sans-serif) for problems
            latex += f"    \\item{{\\sffamily\\fontsize{{{font_size}}}{{{int(font_size*1.15)}}}\\selectfont {escaped_problem}}}\n"
        
        latex += "\\end{enumerate}\n"
        latex += "\\end{minipage}\n"
        latex += "\\hfill\n"
        latex += "\\begin{minipage}[t]{0.48\\textwidth}\n"
        latex += "\\begin{enumerate}[label=(\\arabic*),leftmargin=*,itemsep=" + spacing + ",topsep=0pt,labelsep=0.3em,start=" + str(start_num + len(left_problems)) + "]\n"
        
        # Right column problems  
        for i, problem in enumerate(right_problems):
            formatted_problem = self.format_math(problem)
            escaped_problem = self.escape_latex(formatted_problem)
            problem_num = start_num + len(left_problems) + i
            # Use Arial font (sans-serif) for problems
            latex += f"    \\item{{\\sffamily\\fontsize{{{font_size}}}{{{int(font_size*1.15)}}}\\selectfont {escaped_problem}}}\n"
        
        latex += "\\end{enumerate}\n"
        latex += "\\end{minipage}\n"
        
        return latex
    
    def _compile_latex(self, tex_path, output_dir):
        """Compile LaTeX file to PDF"""
        # Try Tectonic first (for Vercel/serverless), then xelatex, then pdflatex
        tex_dir = os.path.dirname(tex_path)
        tex_basename = os.path.basename(tex_path)
        tex_name = os.path.splitext(tex_basename)[0]
        
        # Change to tex directory for compilation
        original_dir = os.getcwd()
        try:
            os.chdir(tex_dir)
            
            # Try Tectonic first (best for serverless/Vercel)
            if TECTONIC_AVAILABLE:
                try:
                    tectonic_cmd = ensure_tectonic()
                    result = subprocess.run(
                        [tectonic_cmd, '-X', 'compile', tex_basename, '--outdir', '.'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        return
                except Exception as e:
                    # Silently fail and try next compiler
                    pass
            
            # Also try 'tectonic' directly in PATH
            try:
                result = subprocess.run(
                    ['tectonic', '-X', 'compile', tex_basename, '--outdir', '.'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            # Try XeLaTeX (better for custom fonts, local development)
            try:
                result = subprocess.run(
                    ['xelatex', '-interaction=nonstopmode', '-output-directory=.', tex_basename],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            # Fallback to pdflatex
            try:
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-output-directory=.', tex_basename],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    raise RuntimeError(f"LaTeX compilation failed: {result.stderr}")
            except FileNotFoundError:
                raise RuntimeError(
                    "No LaTeX compiler found. Install one of:\n"
                    "- Tectonic (recommended for serverless): https://tectonic-typesetting.github.io/\n"
                    "- XeLaTeX (local): brew install --cask mactex\n"
                    "- pdflatex (local): brew install --cask mactex"
                )
        finally:
            os.chdir(original_dir)

