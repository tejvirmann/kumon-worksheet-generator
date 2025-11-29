"""
Print Layout Generator
Creates 2-up print layout for double-sided printing and cutting

Layout:
- Print Page 1: [Worksheet Front] [Worksheet Front] (side by side)
- Print Page 2: [Worksheet Back] [Worksheet Back] (side by side)

When printed double-sided and cut, creates two identical worksheets.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image
import os
from io import BytesIO

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

class PrintLayoutGenerator:
    """Generate 2-up print layouts for worksheets"""
    
    def __init__(self):
        self.page_width, self.page_height = letter  # 8.5 x 11 inches
    
    def create_2up_print_layout(self, worksheet_pdf_path, output_path=None):
        """
        Create a 2-up print layout PDF
        
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
        
        if not PDF2IMAGE_AVAILABLE:
            raise ImportError(
                "pdf2image is required for print layout. Install with: pip install pdf2image\n"
                "Also requires poppler: brew install poppler (macOS) or apt-get install poppler-utils (Linux)"
            )
        
        # Convert PDF pages to images
        images = convert_from_path(worksheet_pdf_path, dpi=300)
        
        if len(images) < 2:
            raise ValueError("Worksheet must have at least 2 pages (front and back)")
        
        front_image = images[0]
        back_image = images[1]
        
        # Create output PDF with 2-up layout
        can = canvas.Canvas(output_path, pagesize=letter)
        page_width, page_height = self.page_width, self.page_height
        
        # Calculate dimensions for 2-up layout
        # Each worksheet page takes up exactly half the width
        # Scale to fill half width while maintaining aspect ratio
        half_width = page_width / 2
        scale_factor = half_width / page_width  # 0.5 (half width)
        scaled_width = half_width
        scaled_height = page_height * scale_factor  # Scale height proportionally
        
        # Convert PIL images to temporary buffers for ReportLab
        def pil_to_temp_file(pil_image, temp_path):
            pil_image.save(temp_path, format='PNG')
            return temp_path
        
        import tempfile
        
        # Create temporary files for images
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as front_temp:
            front_temp_path = front_temp.name
            front_image.save(front_temp_path, format='PNG')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as back_temp:
            back_temp_path = back_temp.name
            back_image.save(back_temp_path, format='PNG')
        
        try:
            # Page 1: Two front pages side by side - fill half width each
            x_left = 0
            # Center vertically
            y_top = (page_height - scaled_height) / 2
            
            # Left front - half width, proportional height
            can.drawImage(front_temp_path, x_left, y_top, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
            
            # Right front - half width, proportional height
            x_right = half_width
            can.drawImage(front_temp_path, x_right, y_top, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
            
            can.showPage()
            
            # Page 2: Two back pages side by side - fill half width each
            # Left back - half width, proportional height
            can.drawImage(back_temp_path, x_left, y_top, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
            
            # Right back - half width, proportional height
            can.drawImage(back_temp_path, x_right, y_top, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
            
            can.showPage()
            can.save()
        finally:
            # Clean up temp files
            try:
                os.unlink(front_temp_path)
                os.unlink(back_temp_path)
            except:
                pass
        
        can.showPage()
        can.save()
        
        return output_path
