"""
Simple 2-up Print Layout using PyPDF2
Places two worksheet pages side-by-side on one sheet - most reliable method
"""

import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from io import BytesIO

def create_2up_print_layout(worksheet_pdf_path1, worksheet_pdf_path2=None, output_path=None):
    """
    Create 2-up print layout: Front 1 + Front 2 on page 1, Back 2 + Back 1 on page 2
    
    Uses PyPDF2 to merge pages at specific positions
    
    Args:
        worksheet_pdf_path1: Path to first worksheet PDF (front=1a, back=1b)
        worksheet_pdf_path2: Path to second worksheet PDF (front=2a, back=2b). 
                            If None, uses worksheet1 twice.
        output_path: Optional output path
        
    Returns:
        Path to generated print layout PDF
    """
    if not os.path.exists(worksheet_pdf_path1):
        raise FileNotFoundError(f"Worksheet PDF not found: {worksheet_pdf_path1}")
    
    if output_path is None:
        base_path = worksheet_pdf_path1.rsplit('.', 1)[0]
        output_path = f"{base_path}_print.pdf"
    
    # Read the first worksheet PDF
    reader1 = PdfReader(worksheet_pdf_path1)
    if len(reader1.pages) < 2:
        raise ValueError("Worksheet must have at least 2 pages (front and back)")
    
    front1_page = reader1.pages[0]  # Front 1 (will be 1a)
    back1_page = reader1.pages[1]   # Back 1 (will be 1b)
    
    # Read the second worksheet PDF (or use first if not provided)
    if worksheet_pdf_path2 is None:
        worksheet_pdf_path2 = worksheet_pdf_path1
    
    if not os.path.exists(worksheet_pdf_path2):
        raise FileNotFoundError(f"Worksheet PDF 2 not found: {worksheet_pdf_path2}")
    
    reader2 = PdfReader(worksheet_pdf_path2)
    if len(reader2.pages) < 2:
        raise ValueError("Worksheet 2 must have at least 2 pages (front and back)")
    
    front2_page = reader2.pages[0]  # Front 2 (will be 2a)
    back2_page = reader2.pages[1]   # Back 2 (will be 2b)
    
    # Create output PDF using ReportLab (simpler for positioning)
    page_width, page_height = letter  # 8.5 x 11 inches
    
    # Stack worksheets vertically (top and bottom), each rotated 90 degrees
    # Original worksheet: 8.5" x 11" (portrait)
    # After rotating 90°: 11" x 8.5" (landscape)
    # Page: 8.5" x 11"
    # Each worksheet gets exactly half the page height (5.5")
    
    half_height = page_height / 2  # 5.5" - each worksheet gets this vertical space
    
    # Scale to fit: rotated worksheet height (8.5") must fit in half page height (5.5")
    # Scale factor = 5.5 / 8.5 ≈ 0.647
    scale_factor = half_height / page_width  # 5.5 / 8.5
    
    # Rotated dimensions after scaling
    # When rotated: original 8.5" x 11" becomes 11" x 8.5"
    # Scaled: 11" * 0.647 ≈ 7.12" wide, 8.5" * 0.647 = 5.5" tall
    rotated_scaled_width = page_height * scale_factor  # 11 * 0.647 ≈ 7.12"
    rotated_scaled_height = half_height  # 5.5" - exactly half page height
    
    # Center horizontally on page
    center_x = (page_width - rotated_scaled_width) / 2
    
    # Vertical positions for top and bottom
    top_center_y = page_height - half_height / 2  # Center of top half
    bottom_center_y = half_height / 2  # Center of bottom half
    
    # Create output PDF
    can = canvas.Canvas(output_path, pagesize=letter)
    
    # Convert PDF pages to images using pdf2image (if available) or use PyPDF2
    try:
        from pdf2image import convert_from_path
        # Convert to images for ReportLab
        images1 = convert_from_path(worksheet_pdf_path1, dpi=300)
        front1_image = images1[0]
        back1_image = images1[1]
        
        images2 = convert_from_path(worksheet_pdf_path2, dpi=300)
        front2_image = images2[0]
        back2_image = images2[1]
        
        # Save as temp PNG files
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as front1_temp:
            front1_temp_path = front1_temp.name
            front1_image.save(front1_temp_path, format='PNG')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as front2_temp:
            front2_temp_path = front2_temp.name
            front2_image.save(front2_temp_path, format='PNG')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as back1_temp:
            back1_temp_path = back1_temp.name
            back1_image.save(back1_temp_path, format='PNG')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as back2_temp:
            back2_temp_path = back2_temp.name
            back2_image.save(back2_temp_path, format='PNG')
        
        try:
            # Page 1: Front 1 (top) + Front 2 (bottom), each rotated 90 degrees (landscape)
            # Top: Front page 1 (1a)
            can.saveState()
            can.translate(center_x + rotated_scaled_width/2, top_center_y)
            can.rotate(90)
            can.drawImage(front1_temp_path, -rotated_scaled_height/2, -rotated_scaled_width/2, 
                         width=rotated_scaled_height, height=rotated_scaled_width, preserveAspectRatio=True)
            can.restoreState()
            
            # Bottom: Front page 2 (2a)
            can.saveState()
            can.translate(center_x + rotated_scaled_width/2, bottom_center_y)
            can.rotate(90)
            can.drawImage(front2_temp_path, -rotated_scaled_height/2, -rotated_scaled_width/2, 
                         width=rotated_scaled_height, height=rotated_scaled_width, preserveAspectRatio=True)
            can.restoreState()
            
            can.showPage()
            
            # Page 2: Back 2 (top) + Back 1 (bottom), each rotated 90 degrees (landscape)
            # Top: Back page 2 (2b)
            can.saveState()
            can.translate(center_x + rotated_scaled_width/2, top_center_y)
            can.rotate(90)
            can.drawImage(back2_temp_path, -rotated_scaled_height/2, -rotated_scaled_width/2, 
                         width=rotated_scaled_height, height=rotated_scaled_width, preserveAspectRatio=True)
            can.restoreState()
            
            # Bottom: Back page 1 (1b)
            can.saveState()
            can.translate(center_x + rotated_scaled_width/2, bottom_center_y)
            can.rotate(90)
            can.drawImage(back1_temp_path, -rotated_scaled_height/2, -rotated_scaled_width/2, 
                         width=rotated_scaled_height, height=rotated_scaled_width, preserveAspectRatio=True)
            can.restoreState()
            
            can.save()
        finally:
            # Clean up temp files
            try:
                os.unlink(front1_temp_path)
                os.unlink(front2_temp_path)
                os.unlink(back1_temp_path)
                os.unlink(back2_temp_path)
            except:
                pass
        
        return output_path
        
    except ImportError:
        # Fallback: Use PyPDF2 page merging (less reliable but works without pdf2image)
        raise ImportError(
            "pdf2image is required for 2-up print layout. Install with:\n"
            "  pip install pdf2image\n"
            "  brew install poppler"
        )

