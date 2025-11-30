"""
Worksheet Generator
Creates Kumon-style worksheets with proper formatting and layout matching actual Kumon worksheets
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage, BaseDocTemplate, PageTemplate, Frame, Flowable
from reportlab.lib.geomutils import *
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
        
        # Try to register Comic Sans or use fallback
        self.comic_sans_font = 'Helvetica'  # Default fallback
        try:
            # Common Comic Sans locations
            comic_sans_paths = [
                '/System/Library/Fonts/Supplemental/Comic Sans MS.ttf',
                '/Library/Fonts/Comic Sans MS.ttf',
                '/usr/share/fonts/truetype/comicsansms.ttf',
                'C:/Windows/Fonts/comicsans.ttf',
                'C:/Windows/Fonts/comic.ttf',
            ]
            for path in comic_sans_paths:
                if os.path.exists(path):
                    pdfmetrics.registerFont(TTFont('ComicSans', path))
                    self.comic_sans_font = 'ComicSans'
                    break
        except:
            pass  # Use fallback
        
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
        
        # Level/Page number style with Comic Sans (top right)
        self.styles.add(ParagraphStyle(
            name='LevelPageNumber',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName=self.comic_sans_font,  # Comic Sans or fallback
            textColor=HexColor(self.design.get('colors', {}).get('secondary', '#4B2E83')),
            alignment=TA_RIGHT,
            leading=16
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
            name='WorksheetTitleInTable',
            parent=self.styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=HexColor(self.design.get('colors', {}).get('secondary', '#4B2E83')),
            alignment=TA_CENTER,
            leading=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='StudentField',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='StudentFields',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            alignment=TA_RIGHT,
            leading=14
        ))
        
        # Problem styles - Times New Roman Italic, larger size
        self.styles.add(ParagraphStyle(
            name='Problem',
            parent=self.styles['Normal'],
            fontSize=14,  # Larger size
            fontName='Times-Italic',  # Italicized Times New Roman
            alignment=TA_LEFT,
            leading=18
        ))
        
        self.styles.add(ParagraphStyle(
            name='ProblemAdvanced',
            parent=self.styles['Normal'],
            fontSize=13,  # Slightly smaller for advanced, but still larger than before
            fontName='Times-Italic',  # Italicized Times New Roman
            alignment=TA_LEFT,
            leading=17
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
    
    def generate_pdf(self, problems, level, topic, layout_style='medium_spaced', page_number=1, output_dir='output', layout_spec=None):
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
        
        # Determine layout type based on level or AI layout spec
        if layout_spec:
            # Use AI-generated layout specifications
            use_two_columns = layout_spec.get('use_two_columns', False)
            problem_font_size = layout_spec.get('font_size', 11)
            problem_spacing = layout_spec.get('spacing_between_problems', 0.6)
        else:
            # Default based on level
            is_advanced_level = level in ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
            use_two_columns = is_advanced_level
            problem_font_size = 10 if is_advanced_level else 11
            problem_spacing = 0.4 if is_advanced_level else 0.6
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.15*inch,  # Reduced from 0.75 to move content higher
            bottomMargin=0.75*inch,
            title=f"Kumon Level {level} - {topic}"
        )
        
        story = []
        
        # Split problems for front and back
        mid_point = len(problems) // 2
        front_problems = problems[:mid_point]
        back_problems = problems[mid_point:]
        
        # Store page_number for use in headers
        self._page_number = page_number
        
        # Front page
        story.extend(self._create_header(level, topic, page_num=1))
        story.extend(self._create_problems_section(
            front_problems,
            use_two_columns=use_two_columns,
            level=level,
            problem_font_size=problem_font_size if layout_spec else None,
            problem_spacing=problem_spacing if layout_spec else None
        ))
        
        story.append(PageBreak())
        
        # Back page (simpler, no full header)
        story.extend(self._create_back_page_header(level))
        story.extend(self._create_problems_section(
            back_problems,
            use_two_columns=use_two_columns,
            level=level,
            start_number=len(front_problems) + 1,
            problem_font_size=problem_font_size if layout_spec else None,
            problem_spacing=problem_spacing if layout_spec else None
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
        """Create the header section matching exact Kumon style - hardcoded for efficiency"""
        content = []
        
        # Sheet identifier (e.g., "C108a") - below logo
        if page_num > 0 and hasattr(self, '_page_number'):
            page_identifier = f"{self._page_number}a"
        elif page_num > 0:
            page_identifier = "1a"
        else:
            page_identifier = ""
        sheet_id = f"{level}{page_identifier}" if page_identifier else level
        
        # Level identifier for top right (e.g., "C108")
        level_ref = level
        
        # Hardcoded header layout - efficient, matches image exactly
        # Row 1: KUMON logo (left) | Level reference (right)
        logo_para = Paragraph(f"<b>KUMON</b>®", self.styles['KumonLogo'])
        level_ref_para = Paragraph(level_ref, self.styles['LevelPageNumber'])
        
        header_row1 = Table([[logo_para, "", level_ref_para]], 
                           colWidths=[2.2*inch, 3.8*inch, 2.5*inch])
        header_row1.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        content.append(header_row1)
        
        # Sheet ID below logo (on its own line)
        sheet_id_para = Paragraph(f"<b>{sheet_id}</b>", self.styles['LevelIdentifier'])
        content.append(sheet_id_para)
        content.append(Spacer(1, 0.06*inch))
        
        # Title (centered) - large, bold
        title_text = f"<b>{topic}</b>"
        content.append(Paragraph(title_text, self.styles['WorksheetTitle']))
        content.append(Spacer(1, 0.06*inch))
        
        # Student fields (Time, Date, Name) - hardcoded format, left-aligned
        student_text = "Time : <u>________</u> to : <u>________</u>  Date: <u>________</u>  Name: <u>________</u>"
        student_style = ParagraphStyle(
            name='StudentFieldsFixed',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            alignment=TA_LEFT,  # Left-aligned, not right
            leading=14
        )
        content.append(Paragraph(student_text, student_style))
        content.append(Spacer(1, 0.12*inch))
        
        # Performance bar - hardcoded, efficient table
        perf_bar_data = [
            ['100%', '~90%', '~80%', '~70%', '69%~'],
            ['(mistakes) 0', '1', '2~3', '4', '5~']
        ]
        perf_bar_table = Table(perf_bar_data, colWidths=[1.4*inch]*5, rowHeights=[0.35*inch, 0.25*inch])
        
        # Hardcoded colors (static, won't change)
        perf_colors = [
            HexColor('#F5F5F5'), HexColor('#E8E8E8'), HexColor('#D0D0D0'),
            HexColor('#B8B8B8'), HexColor('#A0A0A0')
        ]
        
        # Hardcoded table style (static)
        perf_bar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), perf_colors[0]),
            ('BACKGROUND', (1, 0), (1, 0), perf_colors[1]),
            ('BACKGROUND', (2, 0), (2, 0), perf_colors[2]),
            ('BACKGROUND', (3, 0), (3, 0), perf_colors[3]),
            ('BACKGROUND', (4, 0), (4, 0), perf_colors[4]),
            ('BACKGROUND', (0, 1), (0, 1), perf_colors[0]),
            ('BACKGROUND', (1, 1), (1, 1), perf_colors[1]),
            ('BACKGROUND', (2, 1), (2, 1), perf_colors[2]),
            ('BACKGROUND', (3, 1), (3, 1), perf_colors[3]),
            ('BACKGROUND', (4, 1), (4, 1), perf_colors[4]),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, black),
        ]))
        content.append(perf_bar_table)
        content.append(Spacer(1, 0.3*inch))
        
        return content
    
    def _create_back_page_header(self, level):
        """Create simplified header for back page with page number (b)"""
        content = []
        # Add page number with 'b' suffix if available
        if hasattr(self, '_page_number'):
            level_id = f"<b>{level} {self._page_number} b</b>"
        else:
            level_id = f"<b>{level}</b>"
        content.append(Paragraph(level_id, self.styles['LevelIdentifier']))
        content.append(Spacer(1, 0.2*inch))
        return content
    
    def _create_problems_section(self, problems, use_two_columns=False, level='', start_number=1, problem_font_size=None, problem_spacing=None):
        """Create the problems section - uses AI layout spec if provided"""
        content = []
        
        # Determine font size and spacing from AI layout spec or defaults
        # Always use Times-Italic for problems (matching Kumon style)
        if problem_font_size:
            # Create custom style with AI-specified font size, but use Times-Italic
            from reportlab.lib.styles import ParagraphStyle
            custom_problem_style = ParagraphStyle(
                name='CustomProblem',
                parent=self.styles['Normal'],
                fontSize=problem_font_size,
                fontName='Times-Italic',  # Always Times-Italic
                alignment=TA_LEFT,
                leading=int(problem_font_size * 1.2)
            )
            problem_style = custom_problem_style
        else:
            problem_style = self.styles['ProblemAdvanced'] if use_two_columns else self.styles['Problem']
        
        if use_two_columns and len(problems) > 3:
            # Two column layout for advanced levels
            mid = (len(problems) + 1) // 2
            left_problems = problems[:mid]
            right_problems = problems[mid:]
            
            # Create tables for two columns
            max_problems = max(len(left_problems), len(right_problems))
            table_data = []
            
            # Use AI-specified spacing or default for two-column
            spacing = (problem_spacing * inch) if problem_spacing else 0.4*inch
            
            for i in range(max_problems):
                left_cell = ""
                right_cell = ""
                
                if i < len(left_problems):
                    left_para = Paragraph(
                        self._format_problem(left_problems[i], start_number + i),
                        problem_style
                    )
                    left_cell = left_para
                
                if i < len(right_problems):
                    right_para = Paragraph(
                        self._format_problem(right_problems[i], start_number + len(left_problems) + i),
                        problem_style
                    )
                    right_cell = right_para
                
                table_data.append([left_cell, right_cell])
            
            problems_table = Table(table_data, colWidths=[3.5*inch, 3.5*inch])
            problems_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 0.2*inch),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0.4*inch),  # Proper spacing for two-column
            ]))
            content.append(problems_table)
        else:
            # Single column layout - use AI-generated spacing or default
            spacing_value = problem_spacing if problem_spacing else (0.4 if use_two_columns else 0.6)
            spacing = spacing_value * inch if isinstance(spacing_value, (int, float)) else spacing_value
            
            for i, problem in enumerate(problems):
                problem_para = Paragraph(
                    self._format_problem(problem, start_number + i),
                    problem_style
                )
                content.append(problem_para)
                content.append(Spacer(1, spacing))
        
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



