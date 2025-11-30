"""
Custom Flowable for drawing Kumon performance bar with semi-circular segments
"""

from reportlab.platypus import Flowable
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
import math

class PerformanceBar(Flowable):
    """Draw performance bar with semi-circular segments matching Kumon style"""
    
    def __init__(self, width=7*inch, height=0.8*inch):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        
        # Performance data
        self.segments = [
            {'percent': '100%', 'mistakes': '(mistakes) 0', 'color': HexColor('#F5F5F5')},
            {'percent': '~90%', 'mistakes': '1', 'color': HexColor('#E8E8E8')},
            {'percent': '~80%', 'mistakes': '2~3', 'color': HexColor('#D0D0D0')},
            {'percent': '~70%', 'mistakes': '4', 'color': HexColor('#B8B8B8')},
            {'percent': '69%~', 'mistakes': '5~', 'color': HexColor('#A0A0A0')}
        ]
    
    def draw(self):
        """Draw the performance bar with semi-circular segments"""
        canvas = self.canv
        canvas.saveState()
        
        # Calculate segment width
        num_segments = len(self.segments)
        segment_width = self.width / num_segments
        segment_height = self.height * 0.6  # Semi-circle height
        base_height = self.height * 0.4      # Rectangular base height
        radius = segment_height / 2
        
        # Draw each segment
        x_start = 0
        for i, segment in enumerate(self.segments):
            x_center = x_start + segment_width / 2
            
            # Draw rectangular base first
            canvas.setFillColor(segment['color'])
            canvas.setStrokeColor(black)
            canvas.setLineWidth(1)
            canvas.rect(
                x_start,
                0,
                segment_width,
                base_height,
                fill=1,
                stroke=1
            )
            
            # Draw semi-circular top using path
            path = canvas.beginPath()
            # Start at left edge of semi-circle
            path.moveTo(x_center - radius, base_height)
            # Arc for semi-circle (upper half)
            path.arc(
                x_center - radius,
                base_height,
                x_center + radius,
                base_height + segment_height,
                0, 180
            )
            path.close()
            canvas.drawPath(path, fill=1, stroke=1)
            
            # Draw vertical border lines between segments
            if i < num_segments - 1:
                canvas.setStrokeColor(black)
                canvas.setLineWidth(1)
                canvas.line(
                    x_start + segment_width,
                    0,
                    x_start + segment_width,
                    base_height + segment_height
                )
            
            # Add percentage text on top of semi-circle
            canvas.setFillColor(black)
            canvas.setFont('Helvetica-Bold', 10)
            percent_text = segment['percent']
            text_width = canvas.stringWidth(percent_text, 'Helvetica-Bold', 10)
            canvas.drawString(
                x_center - text_width / 2,
                base_height + radius - 3,
                percent_text
            )
            
            # Add mistake count in base
            canvas.setFont('Helvetica', 8)
            mistake_text = segment['mistakes']
            text_width = canvas.stringWidth(mistake_text, 'Helvetica', 8)
            canvas.drawString(
                x_center - text_width / 2,
                base_height * 0.3,
                mistake_text
            )
            
            x_start += segment_width
        
        canvas.restoreState()
    
    def wrap(self, availWidth, availHeight):
        """Return size of the performance bar"""
        return self.width, self.height

