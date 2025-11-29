"""
Kumon Worksheet Generator
Main Flask application for generating Kumon-style worksheets
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from worksheet_generator import WorksheetGenerator
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
        # Generate problems using AI
        problem_gen = ProblemGenerator()
        problems = problem_gen.generate_problems(
            level=level,
            topic=topic,
            num_problems=num_problems
        )
        
        # Generate worksheet
        worksheet_gen = WorksheetGenerator()
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
