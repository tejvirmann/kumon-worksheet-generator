"""
LaTeX-Based Print Layout Generator
Creates 2-up print layout using LaTeX (no pdf2image dependency)

Layout:
- Print Page 1: [Worksheet Front] [Worksheet Front] (side by side)
- Print Page 2: [Worksheet Back] [Worksheet Back] (side by side)

When printed double-sided and cut, creates two identical worksheets.
"""

import os
import subprocess
import tempfile
from datetime import datetime
from latex_generator import LaTeXWorksheetGenerator

class LaTeXPrintLayoutGenerator:
    """Generate 2-up print layouts using LaTeX"""
    
    def __init__(self):
        self.worksheet_gen = LaTeXWorksheetGenerator()
    
    def create_2up_print_layout(self, worksheet_pdf_path, output_path=None):
        """
        Create a 2-up print layout PDF using LaTeX
        
        Args:
            worksheet_pdf_path: Path to the original worksheet PDF (should have front and back)
            output_path: Optional output path (default: adds _print.pdf suffix)
            
        Returns:
            Path to the generated print layout PDF
        """
        if not os.path.exists(worksheet_pdf_path):
            raise FileNotFoundError(f"Worksheet PDF not found: {worksheet_pdf_path}")
        
        if output_path is None:
            base_path = worksheet_pdf_path.rsplit('.', 1)[0]
            output_path = f"{base_path}_print.pdf"
        
        # Get absolute path for LaTeX inclusion
        abs_worksheet_path = os.path.abspath(worksheet_pdf_path)
        
        # Extract pages from PDF and create LaTeX document
        latex_content = self._generate_print_layout_latex(abs_worksheet_path)
        
        # Write LaTeX file
        tex_path = output_path.replace('.pdf', '.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Compile LaTeX to PDF
        try:
            self._compile_latex(tex_path, os.path.dirname(output_path))
        except Exception as e:
            raise RuntimeError(f"LaTeX compilation failed: {str(e)}")
        
        if not os.path.exists(output_path):
            raise RuntimeError(f"PDF was not generated: {output_path}")
        
        # Clean up LaTeX aux files
        try:
            base_name = os.path.splitext(tex_path)[0]
            for ext in ['.aux', '.log', '.tex']:
                aux_file = base_name + ext
                if os.path.exists(aux_file):
                    os.remove(aux_file)
        except:
            pass
        
        return output_path
    
    def _generate_print_layout_latex(self, worksheet_pdf_path):
        """Generate LaTeX code that includes two copies of the worksheet side-by-side"""
        
        # Escape path for LaTeX (replace backslashes, escape special chars)
        escaped_path = worksheet_pdf_path.replace('\\', '/').replace('_', '\\_')
        
        # Use pdfpages package to include PDFs
        latex = f"""\\documentclass[12pt]{{article}}
\\usepackage[paper=letterpaper,margin=0in]{{geometry}}
\\usepackage{{pdfpages}}
\\usepackage{{graphicx}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

\\begin{{document}}

% Page 1: Two front pages side by side
\\begin{{minipage}}[t]{{0.5\\textwidth}}
\\includepdf[pages=1,scale=0.48,offset=0 0,noautoscale]{{{escaped_path}}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.5\\textwidth}}
\\includepdf[pages=1,scale=0.48,offset=0 0,noautoscale]{{{escaped_path}}}
\\end{{minipage}}

\\newpage

% Page 2: Two back pages side by side
\\begin{{minipage}}[t]{{0.5\\textwidth}}
\\includepdf[pages=2,scale=0.48,offset=0 0,noautoscale]{{{escaped_path}}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.5\\textwidth}}
\\includepdf[pages=2,scale=0.48,offset=0 0,noautoscale]{{{escaped_path}}}
\\end{{minipage}}

\\end{{document}}
"""
        return latex
    
    def _compile_latex(self, tex_path, output_dir):
        """Compile LaTeX file to PDF"""
        tex_dir = os.path.dirname(tex_path)
        tex_basename = os.path.basename(tex_path)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tex_dir)
            
            # Try Tectonic first (best for serverless/Vercel)
            try:
                result = subprocess.run(
                    ['tectonic', '-X', 'compile', tex_basename, '--outdir', '.'],
                    capture_output=True,
                    text=True,
                    timeout=60  # Increased timeout for first-time package downloads
                )
                if result.returncode == 0:
                    return
                else:
                    # Tectonic failed - log the error for debugging
                    error_msg = f"Tectonic compilation failed: {result.stderr}"
                    if result.stdout:
                        error_msg += f"\nStdout: {result.stdout[:500]}"
                    raise RuntimeError(error_msg)
            except FileNotFoundError:
                pass
            except subprocess.TimeoutExpired:
                raise RuntimeError("Tectonic compilation timed out (may be downloading packages)")
            except Exception as e:
                # Re-raise with more context
                raise RuntimeError(f"Tectonic error: {str(e)}")
            
            # Try pdflatex (pdfpages works with pdflatex)
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
                    "- pdflatex (local): brew install --cask mactex"
                )
        finally:
            os.chdir(original_dir)

