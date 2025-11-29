"""
Worksheet Generator
Creates Kumon-style worksheets with proper formatting and layout matching actual Kumon worksheets
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import black, HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json
from datetime import datetime

class WorksheetGenerator:
    def __init__(self):
        self.page_width, self.page_height = letter
        self.load_design_spec()
        self.setup_styles()
    
    def load_design_spec(self):
        """Load design specifications from JSON file"""
        try:
            with open('design_spec.json', 'r') as f:
                self.design = json.load(f)
        except:
            # Default design specs
            self.design = {
                "colors": {
                    "primary": "#000000",
                    "secondary": "#4B2E83",
                    "background": "#FFFFFF",
                    "table_bg": "#E0E0E0",
                    "footer_text": "#808080"
                }
            }
    
    def setup_styles(self):
        """Setup text styles based on Kumon worksheet design"""
        self.styles = getSampleStyleSheet()
        
        # Header styles
        self.styles.add(ParagraphStyle(
            name='KumonLogo',
            parent=self.styles['Normal'],
            fontSize=18,
            fontName='Helvetica-Bold',
            textColor=HexColor(self.design.get('colors', {}).get('secondary', '#4B2E83')),
            leading=22
        ))
        
        self.styles.add(ParagraphStyle(
            name='LevelIdentifier',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=HexColor(self.design.get('colors', {}).get('secondary', '#4B2E83')),
            leading=18
        ))
        
        self.styles.add(ParagraphStyle(
            name='WorksheetTitle',
            parent=self.styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=HexColor(self.design.get('colors', {}).get('secondary', '#4B2E83')),
            alignment=TA_CENTER,
            leading=20,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='StudentField',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            leading=14
        ))
        
        # Problem styles
        self.styles.add(ParagraphStyle(
            name='Problem',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            alignment=TA_LEFT,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='ProblemNumber',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='Instruction',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica',
            alignment=TA_LEFT,
            leading=16
        ))
    
    def generate_pdf(self, problems, level, topic, layout_style='medium_spaced', output_dir='output'):
        """
        Generate a PDF worksheet with front and back pages matching Kumon style
        
        Args:
            problems: List of problem strings
            level: Kumon level (e.g., 'B', 'H', 'K')
            topic: Topic name
            layout_style: Layout style from kumon_levels.json
            output_dir: Directory to save PDF
            
        Returns:
            Path to generated PDF file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kumon_level_{level}_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Determine layout type based on level
        is_advanced_level = level in ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        use_two_columns = is_advanced_level
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title=f"Kumon Level {level} - {topic}"
        )
        
        story = []
        
        # Split problems for front and back
        mid_point = len(problems) // 2
        front_problems = problems[:mid_point]
        back_problems = problems[mid_point:]
        
        # Front page
        story.extend(self._create_header(level, topic, page_num=1))
        story.extend(self._create_problems_section(
            front_problems,
            use_two_columns=use_two_columns,
            level=level
        ))
        
        story.append(PageBreak())
        
        # Back page (simpler, no full header)
        story.extend(self._create_back_page_header(level))
        story.extend(self._create_problems_section(
            back_problems,
            use_two_columns=use_two_columns,
            level=level,
            start_number=len(front_problems) + 1
        ))
        
        # Build PDF with custom footer
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        return filepath
    
    def _add_footer(self, canvas, doc):
        """Add footer with copyright notice on each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 6)
        canvas.setFillColor(HexColor(self.design.get('colors', {}).get('footer_text', '#808080')))
        
        # Add copyright notice on left margin (vertical text)
        canvas.translate(0.3*inch, 4*inch)
        canvas.rotate(90)
        canvas.drawString(0, 0, "© 2002 Kumon Institute of Education")
        
        canvas.restoreState()
    
    def _create_header(self, level, topic, page_num=1):
        """Create the header section matching Kumon style"""
        content = []
        
        # KUMON logo and level identifier (top left)
        logo_text = f"<b>KUMON</b>®"
        content.append(Paragraph(logo_text, self.styles['KumonLogo']))
        content.append(Spacer(1, 0.1*inch))
        
        # Level identifier (e.g., "K 91 a")
        level_id = f"<b>{level} {page_num} a</b>" if page_num > 0 else f"<b>{level}</b>"
        content.append(Paragraph(level_id, self.styles['LevelIdentifier']))
        content.append(Spacer(1, 0.15*inch))
        
        # Title (centered)
        title_text = f"<b>{topic}</b>"
        content.append(Paragraph(title_text, self.styles['WorksheetTitle']))
        content.append(Spacer(1, 0.1*inch))
        
        # Student information fields
        student_table_data = [
            ['Time : to :', 'Date', 'Name']
        ]
        student_table = Table(student_table_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        student_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        content.append(student_table)
        content.append(Spacer(1, 0.15*inch))
        
        # Performance tracking table
        perf_table_data = [
            ['100%', '90%', '80%', '70%', '69%~'],
            ['(mistakes) 0', '—', '1', '—', '2~']
        ]
        perf_table = Table(perf_table_data, colWidths=[1.5*inch]*5)
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(self.design.get('colors', {}).get('table_bg', '#E0E0E0'))),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#F5F5F5'), white]),
        ]))
        content.append(perf_table)
        content.append(Spacer(1, 0.3*inch))
        
        return content
    
    def _create_back_page_header(self, level):
        """Create simplified header for back page"""
        content = []
        level_id = f"<b>{level}</b>"
        content.append(Paragraph(level_id, self.styles['LevelIdentifier']))
        content.append(Spacer(1, 0.2*inch))
        return content
    
    def _create_problems_section(self, problems, use_two_columns=False, level='', start_number=1):
        """Create the problems section"""
        content = []
        
        if use_two_columns and len(problems) > 3:
            # Two column layout for advanced levels
            mid = (len(problems) + 1) // 2
            left_problems = problems[:mid]
            right_problems = problems[mid:]
            
            # Create tables for two columns
            max_problems = max(len(left_problems), len(right_problems))
            table_data = []
            
            for i in range(max_problems):
                left_cell = ""
                right_cell = ""
                
                if i < len(left_problems):
                    left_para = Paragraph(
                        self._format_problem(left_problems[i], start_number + i),
                        self.styles['Problem']
                    )
                    left_cell = left_para
                
                if i < len(right_problems):
                    right_para = Paragraph(
                        self._format_problem(right_problems[i], start_number + len(left_problems) + i),
                        self.styles['Problem']
                    )
                    right_cell = right_para
                
                table_data.append([left_cell, right_cell])
            
            problems_table = Table(table_data, colWidths=[3.5*inch, 3.5*inch])
            problems_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 0.2*inch),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0.4*inch),
            ]))
            content.append(problems_table)
        else:
            # Single column layout
            for i, problem in enumerate(problems):
                problem_para = Paragraph(
                    self._format_problem(problem, start_number + i),
                    self.styles['Problem']
                )
                content.append(problem_para)
                content.append(Spacer(1, 0.6*inch))
        
        return content
    
    def _format_problem(self, problem_text, problem_number):
        """Format a single problem with Kumon-style numbering"""
        # Import math renderer for better math formatting
        try:
            from math_renderer import MathRenderer
            formatted_text = MathRenderer.format_problem_text(problem_text)
        except:
            formatted_text = problem_text
        
        return f"<b>({problem_number})</b> {formatted_text}"



