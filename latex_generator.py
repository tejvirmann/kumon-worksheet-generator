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
import re

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
        """Convert math notation to LaTeX math mode with enhanced support for complex expressions"""
        if not problem_text:
            return ""
        
        # Check if problem already contains LaTeX math (indicated by $)
        has_math_mode = '$' in problem_text
        
        # Convert common math symbols
        problem_text = problem_text.replace('×', r'$\times$')
        problem_text = problem_text.replace('÷', r'$\div$')
        problem_text = problem_text.replace('≤', r'$\leq$')
        problem_text = problem_text.replace('≥', r'$\geq$')
        problem_text = problem_text.replace('±', r'$\pm$')
        problem_text = problem_text.replace('≠', r'$\neq$')
        
        # Handle quadratic equations: x², x^2 -> x^{2}
        problem_text = re.sub(r'([a-zA-Z])\^(\d+)', r'\1^{\2}', problem_text)
        problem_text = re.sub(r'([a-zA-Z])²', r'\1^{2}', problem_text)
        problem_text = re.sub(r'([a-zA-Z])³', r'\1^{3}', problem_text)
        
        # Handle fractions like "3/4" -> "\frac{3}{4}" (but not if already in math mode)
        if not has_math_mode:
            # Match fractions in context: (num)/(den) or num/den
            problem_text = re.sub(r'\((\d+)/(\d+)\)', r'($\\frac{\1}{\2}$)', problem_text)
            problem_text = re.sub(r'\b(\d+)/(\d+)\b', r'$\\frac{\1}{\2}$', problem_text)
        
        # Handle square roots: sqrt(x) -> \sqrt{x}
        problem_text = re.sub(r'sqrt\(([^)]+)\)', r'$\\sqrt{\1}$', problem_text)
        
        # Handle quadratic formula patterns: ax² + bx + c = 0
        # Wrap entire equations in math mode if they contain mathematical operations
        if not has_math_mode and (re.search(r'[+\-×÷=<>≤≥]', problem_text) or re.search(r'[a-zA-Z]\d+|[a-zA-Z]²', problem_text)):
            # Don't double-wrap, but ensure complex expressions are in math mode
            pass  # Will be handled by problem-specific detection
        
        # Handle complex fractions and nested expressions
        # (x - 3) / 2 -> \frac{x-3}{2}
        problem_text = re.sub(r'\(([^)]+)\)\s*/\s*(\d+)', r'$\\frac{\1}{\2}$', problem_text)
        
        # Handle word problems - leave them as text
        # If problem contains substantial text (not just math), don't wrap entirely in math mode
        word_count = len([w for w in problem_text.split() if w.isalpha() and len(w) > 2])
        if word_count > 3:
            # Word problem - keep as text with inline math for expressions
            return problem_text
        
        # Wrap entire equation in math mode if it's a pure math expression
        # This ensures clean, professional math rendering
        if not has_math_mode and word_count <= 3:
            # Check if it's a mathematical equation or expression
            if re.search(r'[=<>≤≥]', problem_text) or re.search(r'[+\-×÷/]', problem_text) or re.search(r'\d+\s*[×÷]', problem_text):
                # Wrap entire problem in math mode for clean rendering
                if not problem_text.strip().startswith('$'):
                    problem_text = f"${problem_text}$"
        
        return problem_text
    
    def needs_graph(self, problem_text, topic):
        """Determine if a problem needs a graph"""
        problem_lower = problem_text.lower()
        topic_lower = topic.lower()
        
        # Check topic keywords
        graph_topics = ['graph', 'graphing', 'function', 'parabola', 'quadratic function', 'linear equation graph']
        if any(keyword in topic_lower for keyword in graph_topics):
            return True
        
        # Check problem text keywords
        graph_keywords = ['graph', 'plot', 'sketch', 'draw', 'parabola', 'coordinate', 'axis', 'axes']
        if any(keyword in problem_lower for keyword in graph_keywords):
            return True
        
        # Check for function notation that suggests graphing
        if re.search(r'y\s*=\s*[^=]+', problem_text) and ('quadratic' in topic_lower or 'function' in topic_lower):
            return True
        
        return False
    
    def generate_graph_latex(self, problem_text, topic):
        """Generate TikZ graph LaTeX code for a problem"""
        
        # Try to extract function from problem
        # Look for y = ... patterns
        func_match = re.search(r'y\s*=\s*([^=]+)', problem_text, re.IGNORECASE)
        
        if not func_match:
            # Generate a simple coordinate plane if no function found
            return self._generate_coordinate_plane()
        
        function_expr = func_match.group(1).strip()
        
        # Check if it's a quadratic function (contains x² or x^2)
        if re.search(r'x\s*[\^²]\s*2|quadratic', function_expr, re.IGNORECASE):
            return self._generate_quadratic_graph(function_expr)
        else:
            # Assume linear function
            return self._generate_linear_graph(function_expr)
    
    def _generate_coordinate_plane(self):
        """Generate a professional coordinate plane"""
        return """\\begin{tikzpicture}[scale=0.9, baseline]
    % Axes with arrows
    \\draw[->, thick] (-3.5,0) -- (3.5,0) node[right] {\\small $x$};
    \\draw[->, thick] (0,-3.5) -- (0,3.5) node[above] {\\small $y$};
    
    % Grid (light gray for reference)
    \\draw[gray!30] (-3,-3) grid (3,3);
    
    % Tick marks and labels
    \\foreach \\x in {-3,-2,-1,1,2,3}
        \\draw (\\x,0.1) -- (\\x,-0.1) node[below] {\\footnotesize $\\x$};
    \\foreach \\y in {-3,-2,-1,1,2,3}
        \\draw (0.1,\\y) -- (-0.1,\\y) node[left] {\\footnotesize $\\y$};
    
    % Origin label
    \\node[below left] at (0,0) {\\tiny $O$};
\\end{tikzpicture}"""
    
    def _generate_linear_graph(self, expression):
        """Generate professional TikZ code for a linear graph"""
        return """\\begin{tikzpicture}[scale=0.9, baseline]
    % Axes
    \\draw[->, thick] (-3.5,0) -- (3.5,0) node[right] {\\small $x$};
    \\draw[->, thick] (0,-3.5) -- (0,3.5) node[above] {\\small $y$};
    
    % Grid (light gray)
    \\draw[gray!30] (-3,-3) grid (3,3);
    
    % Tick marks and labels
    \\foreach \\x in {-3,-2,-1,1,2,3}
        \\draw (\\x,0.1) -- (\\x,-0.1) node[below] {\\footnotesize $\\x$};
    \\foreach \\y in {-3,-2,-1,1,2,3}
        \\draw (0.1,\\y) -- (-0.1,\\y) node[left] {\\footnotesize $\\y$};
    
    % Origin label
    \\node[below left] at (0,0) {\\tiny $O$};
    
    % Draw sample line: y = x (example - user should complete)
    \\draw[thick, color=blue!70!black, domain=-3:3] plot (\\x, {\\x});
\\end{tikzpicture}"""
    
    def _generate_quadratic_graph(self, expression):
        """Generate professional TikZ code for a quadratic graph (parabola)"""
        return """\\begin{tikzpicture}[scale=0.9, baseline]
    % Axes
    \\draw[->, thick] (-3.5,0) -- (3.5,0) node[right] {\\small $x$};
    \\draw[->, thick] (0,-1.5) -- (0,4.5) node[above] {\\small $y$};
    
    % Grid (light gray)
    \\draw[gray!30] (-3,-1) grid (3,4);
    
    % Tick marks and labels
    \\foreach \\x in {-3,-2,-1,1,2,3}
        \\draw (\\x,0.1) -- (\\x,-0.1) node[below] {\\footnotesize $\\x$};
    \\foreach \\y in {-1,1,2,3,4}
        \\draw (0.1,\\y) -- (-0.1,\\y) node[left] {\\footnotesize $\\y$};
    
    % Origin label
    \\node[below left] at (0,0) {\\tiny $O$};
    
    % Draw parabola: y = x² (example - user should adjust)
    \\draw[thick, color=blue!70!black, domain=-2.5:2.5, samples=100] plot (\\x, {\\x*\\x});
    
    % Mark vertex
    \\filldraw[blue!70!black] (0,0) circle (2pt);
    \\node[above right] at (0,0) {\\tiny $(0,0)$};
\\end{tikzpicture}"""
    
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

% Header: All elements on one horizontal line
\\noindent
\\begin{{minipage}}[t]{{0.18\\textwidth}}
{{\\kumonlogo\\fontsize{{18}}{{22}}\\selectfont\\textcolor{{kumonpurple}}{{KUMON\\textregistered}}}} \\quad
{{\\kumonlevel\\fontsize{{14}}{{18}}\\selectfont\\textcolor{{kumonpurple}}{{{self.escape_latex(front_page_id)}}}}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.45\\textwidth}}
\\centering
{{\\kumonfont\\bfseries\\fontsize{{16}}{{20}}\\selectfont\\textcolor{{kumonpurple}}{{{self.escape_latex(topic)}}}}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.32\\textwidth}}
\\raggedleft
{{\\sffamily\\fontsize{{11}}{{13}}\\selectfont Time : \\underline{{\\hspace{{1.5cm}}}} to : \\underline{{\\hspace{{1.2cm}}}} \\quad Date: \\underline{{\\hspace{{1.5cm}}}} \\quad Name: \\underline{{\\hspace{{2cm}}}}}}
\\end{{minipage}}

\\vspace{{0.1in}}

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
            latex += self._generate_two_column_problems(front_problems, problem_font_size, problem_spacing, start_num=1, topic=topic)
        else:
            latex += self._generate_single_column_problems(front_problems, problem_font_size, problem_spacing, start_num=1, topic=topic)
        
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
            latex += self._generate_two_column_problems(back_problems, problem_font_size, problem_spacing, start_num=len(front_problems) + 1, topic=topic)
        else:
            latex += self._generate_single_column_problems(back_problems, problem_font_size, problem_spacing, start_num=len(front_problems) + 1, topic=topic)
        
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
    
    def _generate_single_column_problems(self, problems, font_size, spacing, start_num=1, topic=""):
        """Generate single-column problem list with proper formatting"""
        latex = "\\begin{enumerate}[label=(\\arabic*),leftmargin=*,itemsep=" + spacing + ",topsep=0pt,labelsep=0.3em]\n"
        
        for i, problem in enumerate(problems):
            problem_num = start_num + i
            # Format math in problem with better typography
            formatted_problem = self.format_math(problem)
            escaped_problem = self.escape_latex(formatted_problem)
            
            # Better formatting: use bold for math equations, professional font sizing
            if any(char in escaped_problem for char in ['=', '+', '-', '×', '÷', '/', '²', '^', '(', ')']):
                # It's a math problem - use bold, larger font for clarity
                item_content = f"\\sffamily\\bfseries\\fontsize{{{font_size + 1}}}{{{int((font_size + 1)*1.2)}}}\\selectfont {escaped_problem}"
            else:
                item_content = f"\\sffamily\\fontsize{{{font_size}}}{{{int(font_size*1.15)}}}\\selectfont {escaped_problem}"
            
            if self.needs_graph(problem, topic):
                # Add professional graph below problem with proper spacing
                graph_code = self.generate_graph_latex(problem, topic)
                item_content += f"\\\\[0.15in]\n        \\centering\n        {graph_code}"
            
            latex += f"    \\item{{{item_content}}}\n"
        
        latex += "\\end{enumerate}\n"
        return latex
    
    def _generate_two_column_problems(self, problems, font_size, spacing, start_num=1, topic=""):
        """Generate two-column problem layout with graph support"""
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
            
            # Better formatting: bold for math equations, professional font
            if any(char in escaped_problem for char in ['=', '+', '-', '×', '÷', '/', '²', '^', '(', ')']):
                item_content = f"\\sffamily\\bfseries\\fontsize{{{font_size + 1}}}{{{int((font_size + 1)*1.2)}}}\\selectfont {escaped_problem}"
            else:
                item_content = f"\\sffamily\\fontsize{{{font_size}}}{{{int(font_size*1.15)}}}\\selectfont {escaped_problem}"
            
            if self.needs_graph(problem, topic):
                # Add professional graph below problem
                graph_code = self.generate_graph_latex(problem, topic)
                item_content += f"\\\\[0.15in]\n        \\centering\n        {graph_code}"
            
            latex += f"    \\item{{{item_content}}}\n"
        
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
            
            # Better formatting: bold for math equations, professional font
            if any(char in escaped_problem for char in ['=', '+', '-', '×', '÷', '/', '²', '^', '(', ')']):
                item_content = f"\\sffamily\\bfseries\\fontsize{{{font_size + 1}}}{{{int((font_size + 1)*1.2)}}}\\selectfont {escaped_problem}"
            else:
                item_content = f"\\sffamily\\fontsize{{{font_size}}}{{{int(font_size*1.15)}}}\\selectfont {escaped_problem}"
            
            if self.needs_graph(problem, topic):
                # Add professional graph below problem
                graph_code = self.generate_graph_latex(problem, topic)
                item_content += f"\\\\[0.15in]\n        \\centering\n        {graph_code}"
            
            latex += f"    \\item{{{item_content}}}\n"
        
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

