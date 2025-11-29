"""
Vercel serverless function: /api/generate
Generates Kumon worksheet with AI problems
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worksheet_generator import WorksheetGenerator
from problem_generator import ProblemGenerator

# Load Kumon levels
with open('kumon_levels.json', 'r') as f:
    KUMON_LEVELS = json.load(f)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            level = data.get('level')
            topic = data.get('topic')
            num_problems = data.get('num_problems', 10)
            
            if not level or not topic:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Level and topic are required"}).encode())
                return
            
            # Generate problems
            problem_gen = ProblemGenerator()
            problems = problem_gen.generate_problems(level, topic, num_problems)
            
            # Generate PDF
            worksheet_gen = WorksheetGenerator()
            layout_style = KUMON_LEVELS[level]["layout_style"]
            
            # Use /tmp for Vercel
            output_dir = '/tmp'
            os.makedirs(output_dir, exist_ok=True)
            
            pdf_path = worksheet_gen.generate_pdf(
                problems=problems,
                level=level,
                topic=topic,
                layout_style=layout_style,
                output_dir=output_dir
            )
            
            # Read PDF as base64
            import base64
            with open(pdf_path, 'rb') as f:
                pdf_data = base64.b64encode(f.read()).decode('utf-8')
            
            pdf_filename = os.path.basename(pdf_path)
            
            # Return response
            response = {
                "success": True,
                "pdf_filename": pdf_filename,
                "pdf_data": pdf_data,
                "problems": problems
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

