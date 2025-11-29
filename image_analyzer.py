"""
Image Analyzer for Kumon Worksheets
Analyzes provided Kumon worksheet images to extract styling information
"""

from PIL import Image
import os
import glob

class KumonImageAnalyzer:
    def __init__(self):
        self.analysis_results = {}
    
    def analyze_worksheet_image(self, image_path, level=None, page_type='front'):
        """
        Analyze a Kumon worksheet image to extract design elements
        
        Args:
            image_path: Path to the worksheet image
            level: Kumon level (e.g., 'B', 'H') - optional, can be auto-detected
            page_type: 'front' or 'back' - optional
            
        Returns:
            Dictionary with styling information
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Handle HEIC files - Pillow can open them directly on macOS
        try:
            img = Image.open(image_path)
            # Convert to RGB if needed for processing
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                else:
                    img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
        except Exception as e:
            raise ValueError(f"Could not open image {image_path}: {e}")
        
        width, height = img.size
        
        analysis = {
            'level': level,
            'page_type': page_type,
            'dimensions': {'width': width, 'height': height},
            'typography': {},
            'spacing': {},
            'layout': {},
            'colors': {}
        }
        
        # TODO: Implement image analysis
        # - Extract font information
        # - Measure spacing between problems
        # - Identify layout structure (columns, rows)
        # - Extract colors (background, text)
        # - Measure margins and padding
        
        return analysis
    
    def extract_typography(self, image):
        """Extract typography information from image"""
        # This will use OCR or image processing to determine:
        # - Font family
        # - Font size
        # - Line height
        # - Character spacing
        pass
    
    def extract_spacing(self, image):
        """Extract spacing information"""
        # Determine:
        # - Margins (top, bottom, left, right)
        # - Space between problems
        # - Space between problem number and problem
        # - Leading (line spacing)
        pass
    
    def extract_layout(self, image):
        """Extract layout structure"""
        # Determine:
        # - Number of columns
        # - Number of problems per page
        # - Problem alignment
        # - Header/footer structure
        pass
    
    def compare_levels(self, level_b_image, level_h_image):
        """Compare styling differences between Level B and Level H"""
        b_analysis = self.analyze_worksheet_image(level_b_image, 'B')
        h_analysis = self.analyze_worksheet_image(level_h_image, 'H')
        
        comparison = {
            'font_size_diff': None,
            'spacing_diff': None,
            'layout_diff': None
        }
        
        # TODO: Compare and identify differences
        
        return comparison
    
    def analyze_batch(self, image_paths_or_directory, level_info=None):
        """
        Analyze multiple Kumon worksheet images at once
        
        Args:
            image_paths_or_directory: List of image paths or directory path
            level_info: Optional dict mapping image paths to (level, page_type)
            
        Returns:
            Dictionary mapping image paths to analysis results
        """
        if isinstance(image_paths_or_directory, str) and os.path.isdir(image_paths_or_directory):
            # Find all image files in directory (including HEIC)
            image_paths = []
            for ext in ['*.heic', '*.HEIC', '*.jpg', '*.jpeg', '*.JPG', '*.JPEG', 
                       '*.png', '*.PNG', '*.pdf', '*.PDF']:
                image_paths.extend(glob.glob(os.path.join(image_paths_or_directory, ext)))
        else:
            image_paths = image_paths_or_directory
        
        results = {}
        for image_path in image_paths:
            level = None
            page_type = 'front'
            
            if level_info and image_path in level_info:
                level, page_type = level_info[image_path]
            
            try:
                analysis = self.analyze_worksheet_image(image_path, level, page_type)
                results[image_path] = analysis
            except Exception as e:
                print(f"Error analyzing {image_path}: {e}")
                results[image_path] = {'error': str(e)}
        
        self.analysis_results.update(results)
        return results
    
    def save_analysis_report(self, output_path='kumon_design_spec.json'):
        """Save all analysis results to a JSON file for reference"""
        import json
        with open(output_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        return output_path

