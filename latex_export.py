"""
Optional LaTeX Export Module
Generates LaTeX .tex files from worksheet data for advanced users
"""

def generate_latex_template(problems, level, topic, output_path='output'):
    """
    Generate a LaTeX .tex file that can be compiled to PDF
    
    This is an optional export format for users who want:
    - Perfect mathematical typography
    - To compile locally with XeLaTeX
    - Maximum control over layout
    
    Usage: User downloads .tex file and compiles with:
    xelatex worksheet.tex
    """
    import os
    from datetime import datetime
    
    os.makedirs(output_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kumon_level_{level}_{timestamp}.tex"
    filepath = os.path.join(output_path, filename)
    
    # Escape LaTeX special characters in problems
    def escape_latex(text):
        text = text.replace('\\', r'\textbackslash{}')
        text = text.replace('{', r'\{')
        text = text.replace('}', r'\}')
        text = text.replace('&', r'\&')
        text = text.replace('%', r'\%')
        text = text.replace('$', r'\$')
        text = text.replace('#', r'\#')
        text = text.replace('^', r'\textasciicircum{}')
        text = text.replace('_', r'\_')
        text = text.replace('~', r'\textasciitilde{}')
        return text
    
    latex_content = f"""% Kumon Worksheet - Level {level}
% Topic: {topic}
% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
% Compile with: xelatex {filename}

\\documentclass[12pt]{{article}}
\\usepackage[paper=letterpaper,margin=0.75in]{{geometry}}
\\usepackage{{fontspec}}
\\usepackage{{amsmath}}
\\usepackage{{enumitem}}

% Fonts matching Kumon style
\\setmainfont{{Helvetica}}  % Body text
\\setsansfont{{Helvetica}}  % Headings

\\pagestyle{{empty}}

\\begin{{document}}

% Header
\\noindent
\\begin{{minipage}}{{0.3\\textwidth}}
{{\\sffamily\\bfseries\\large KUMON}}\\\\
{{\\sffamily\\bfseries {level} 1 a}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}{{0.4\\textwidth}}
\\centering
{{\\sffamily\\bfseries\\large {escape_latex(topic)}}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}{{0.2\\textwidth}}
\\raggedleft
{{\\sffamily {level}}}
\\end{{minipage}}

\\vspace{{0.2in}}

% Student fields
\\noindent Time: \\underline{{\\hspace{{2cm}}}} \\quad Date: \\underline{{\\hspace{{2cm}}}} \\quad Name: \\underline{{\\hspace{{3cm}}}}

\\vspace{{0.15in}}

% Performance table
\\begin{{center}}
\\fbox{{\\parbox[c][1.2em][c]{{0.15\\textwidth}}{{\\centering 100\\%\\\\\\small (mistakes) 0}}}}
\\hspace{{4pt}}
\\fbox{{\\parbox[c][1.2em][c]{{0.15\\textwidth}}{{\\centering 90\\%\\\\\\small -}}}}
\\hspace{{4pt}}
\\fbox{{\\parbox[c][1.2em][c]{{0.15\\textwidth}}{{\\centering 80\\%\\\\\\small 1}}}}
\\hspace{{4pt}}
\\fbox{{\\parbox[c][1.2em][c]{{0.15\\textwidth}}{{\\centering 70\\%\\\\\\small -}}}}
\\hspace{{4pt}}
\\fbox{{\\parbox[c][1.2em][c]{{0.15\\textwidth}}{{\\centering 69\\%\\\\\\small 2-}}}}
\\end{{center}}

\\vspace{{0.3in}}

% Problems
\\begin{{enumerate}}[label=(\\arabic*),leftmargin=*]
"""
    
    # Add problems
    for problem in problems:
        # Try to format math expressions
        problem_escaped = escape_latex(problem)
        # Convert common math notation to LaTeX
        problem_escaped = problem_escaped.replace('×', r'$\times$')
        problem_escaped = problem_escaped.replace('÷', r'$\div$')
        
        latex_content += f"    \\item {problem_escaped}\n    \\vspace{{0.4in}}\n\n"
    
    latex_content += """\\end{enumerate}

\\vfill
\\noindent\\small © 2002 Kumon Institute of Education

\\end{document}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    return filepath

