"""
Kumon Worksheet Generator
Main Flask application for generating Kumon-style worksheets
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from worksheet_generator import WorksheetGenerator
from latex_generator import LaTeXWorksheetGenerator
from problem_generator import ProblemGenerator
from config import config

app = Flask(__name__)

# Load configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Load Kumon levels data
with open('kumon_levels.json', 'r') as f:
    KUMON_LEVELS = json.load(f)

@app.route('/')
def index():
    """Main page with dropdowns for level and topic selection"""
    return render_template('index.html', levels=KUMON_LEVELS)

@app.route('/api/levels')
def get_levels():
    """API endpoint to get all available levels"""
    levels_list = [{"id": key, **value} for key, value in KUMON_LEVELS.items()]
    return jsonify(levels_list)

@app.route('/api/topics/<level>')
def get_topics(level):
    """API endpoint to get topics for a specific level"""
    if level in KUMON_LEVELS:
        return jsonify({
            "topics": KUMON_LEVELS[level]["topics"],
            "layout_style": KUMON_LEVELS[level]["layout_style"]
        })
    return jsonify({"error": "Level not found"}), 404

@app.route('/api/generate', methods=['POST'])
def generate_worksheet():
    """Generate worksheet with AI-generated problems"""
    data = request.json
    level = data.get('level')
    topic = data.get('topic')
    num_problems = data.get('num_problems', 10)
    
    if not level or not topic:
        return jsonify({"error": "Level and topic are required"}), 400
    
    try:
        # Generate problems using AI (make them difficult)
        problem_gen = ProblemGenerator()
        problems = problem_gen.generate_problems(
            level=level,
            topic=topic,
            num_problems=num_problems
        )
        
        # Use AI to determine optimal layout for these problems
        try:
            from layout_generator import LayoutGenerator
            layout_gen = LayoutGenerator()
            layout_spec = layout_gen.generate_layout_spec(problems, level, topic, num_problems)
            print(f"✅ AI Layout Spec: {layout_spec.get('justification', 'N/A')}")
        except Exception as layout_error:
            print(f"⚠️  Layout generation failed: {layout_error}, using defaults")
            layout_spec = None
        
        # Generate worksheet using ReportLab (efficient, fast)
        try:
            worksheet_gen = WorksheetGenerator()
            layout_style = KUMON_LEVELS[level]["layout_style"]
            pdf_path = worksheet_gen.generate_pdf(
                problems=problems,
                level=level,
                topic=topic,
                layout_style=layout_style,
                layout_spec=layout_spec  # Pass AI-generated layout spec
            )
        except Exception as reportlab_error:
            # Fallback to LaTeX if ReportLab fails
            print(f"ReportLab generation failed: {reportlab_error}, falling back to LaTeX")
            worksheet_gen = LaTeXWorksheetGenerator()
            layout_style = KUMON_LEVELS[level]["layout_style"]
            pdf_path = worksheet_gen.generate_pdf(
                problems=problems,
                level=level,
                topic=topic,
                layout_style=layout_style
            )
        
        # Read PDF as base64 for embedding
        import base64
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        
        pdf_filename = os.path.basename(pdf_path)
        
        return jsonify({
            "success": True,
            "pdf_path": pdf_path,
            "pdf_filename": pdf_filename,
            "pdf_data": pdf_data,  # Base64 encoded PDF for embedding
            "problems": problems
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-print-layout', methods=['POST'])
def generate_print_layout():
    """Generate 2-up print layout PDF - generates 2 worksheets and combines them"""
    data = request.json
    level = data.get('level')
    topic = data.get('topic')
    num_problems = data.get('num_problems', 10)
    
    if not level or not topic:
        return jsonify({"error": "Level and topic are required"}), 400
    
    try:
        # Generate two worksheets with different problems
        problem_gen = ProblemGenerator()
        
        # Generate first worksheet
        problems1 = problem_gen.generate_problems(level=level, topic=topic, num_problems=num_problems)
        # Generate second worksheet (with different problems)
        problems2 = problem_gen.generate_problems(level=level, topic=topic, num_problems=num_problems)
        
        # Generate both worksheets
        from latex_generator import LaTeXWorksheetGenerator
        from worksheet_generator import WorksheetGenerator
        
        worksheet_gen_latex = LaTeXWorksheetGenerator()
        worksheet_gen_reportlab = WorksheetGenerator()
        layout_style = KUMON_LEVELS[level]["layout_style"]
        
        # Generate worksheet 1 (pages 1a and 1b)
        try:
            pdf_path1 = worksheet_gen_latex.generate_pdf(
                problems=problems1,
                level=level,
                topic=topic,
                layout_style=layout_style,
                page_number=1,
                output_dir=app.config['OUTPUT_DIR']
            )
        except Exception:
            pdf_path1 = worksheet_gen_reportlab.generate_pdf(
                problems=problems1,
                level=level,
                topic=topic,
                layout_style=layout_style,
                page_number=1,
                output_dir=app.config['OUTPUT_DIR']
            )
        
        # Generate worksheet 2 (pages 2a and 2b)
        try:
            pdf_path2 = worksheet_gen_latex.generate_pdf(
                problems=problems2,
                level=level,
                topic=topic,
                layout_style=layout_style,
                page_number=2,
                output_dir=app.config['OUTPUT_DIR']
            )
        except Exception:
            pdf_path2 = worksheet_gen_reportlab.generate_pdf(
                problems=problems2,
                level=level,
                topic=topic,
                layout_style=layout_style,
                page_number=2,
                output_dir=app.config['OUTPUT_DIR']
            )
        
        # Create 2-up print layout with both worksheets
        print_path = None
        last_error = None
        
        # Try simple PDF layout first (uses pdf2image + ReportLab, most reliable)
        try:
            from pdf_2up_layout import create_2up_print_layout
            print_path = create_2up_print_layout(pdf_path1, pdf_path2)
        except Exception as simple_error:
            last_error = simple_error
            print(f"Simple 2-up layout failed: {simple_error}, trying LaTeX...")
            # Try LaTeX
            try:
                from latex_print_layout import LaTeXPrintLayoutGenerator
                layout_gen = LaTeXPrintLayoutGenerator()
                print_path = layout_gen.create_2up_print_layout(worksheet_path)
            except Exception as latex_error:
                last_error = latex_error
                # Fallback to ReportLab-based print layout (requires pdf2image)
                print(f"LaTeX print layout failed: {latex_error}, trying ReportLab fallback...")
                try:
                    from print_layout import PrintLayoutGenerator
                    layout_gen = PrintLayoutGenerator()
                    print_path = layout_gen.create_2up_print_layout(worksheet_path)
                except Exception as reportlab_error:
                    last_error = reportlab_error
                    error_str = str(reportlab_error)
                
                    # Provide helpful error message
                    if "pdf2image" in error_str or "poppler" in error_str.lower():
                        error_msg = (
                            "Print layout generation failed. The ReportLab fallback requires pdf2image.\n\n"
                            "To fix, choose one:\n\n"
                            "Option 1 (Recommended): Install LaTeX for best quality:\n"
                            "  brew install --cask mactex\n\n"
                            "Option 2: Install pdf2image for ReportLab fallback:\n"
                            "  pip install pdf2image\n"
                            "  brew install poppler\n\n"
                            f"Original error: {error_str}"
                        )
                    else:
                        error_msg = (
                            f"Print layout generation failed.\n\n"
                            f"Error: {error_str}\n\n"
                            f"Try installing LaTeX: brew install --cask mactex"
                        )
                    raise RuntimeError(error_msg)
        
        if print_path is None:
            raise RuntimeError("Failed to generate print layout")
        
        # Read PDF as base64
        import base64
        with open(print_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        
        print_filename = os.path.basename(print_path)
        
        return jsonify({
            "success": True,
            "pdf_filename": print_filename,
            "pdf_data": pdf_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/view/<filename>')
def view_worksheet(filename):
    """View generated worksheet PDF (for embedding)"""
    file_path = os.path.join('output', filename)
    if os.path.exists(file_path):
        from flask import Response
        with open(file_path, 'rb') as f:
            pdf_data = f.read()
        return Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="{filename}"',
                'X-Content-Type-Options': 'nosniff'
            }
        )
    return jsonify({"error": "File not found"}), 404

@app.route('/api/download/<filename>')
def download_worksheet(filename):
    """Download generated worksheet PDF"""
    file_path = os.path.join('output', filename)
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            mimetype='application/pdf',
            download_name=filename
        )
    return jsonify({"error": "File not found"}), 404

@app.route('/health')
def health():
    """Health check endpoint for deployment"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
