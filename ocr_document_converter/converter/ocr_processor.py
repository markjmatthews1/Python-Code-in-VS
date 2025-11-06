"""
OCR Processor Module
Handles text extraction with Tesseract OCR
"""

import pytesseract
from PIL import Image
from pathlib import Path
import logging
import os


class OCRProcessor:
    """Process images with OCR to extract text and formatting"""
    
    def __init__(self, tesseract_path=None):
        """
        Initialize OCR processor
        
        Args:
            tesseract_path: Optional path to Tesseract executable
        """
        # Try to find bundled Tesseract
        if tesseract_path is None:
            # Check for bundled Tesseract (same as Recipe Scanner)
            bundled_path = Path(__file__).parent.parent / "tesseract" / "tesseract.exe"
            if bundled_path.exists():
                tesseract_path = str(bundled_path)
                logging.info(f"Using bundled Tesseract at {bundled_path}")
            else:
                logging.info("Using system Tesseract")
        
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text(self, image_path):
        """
        Extract plain text from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            str: Extracted text
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            logging.info(f"Extracted {len(text)} characters from {Path(image_path).name}")
            return text
            
        except Exception as e:
            logging.error(f"Error extracting text from {image_path}: {e}")
            return ""
    
    def extract_text_with_boxes(self, image_path):
        """
        Extract text with bounding box information
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Dictionary with text and bounding box data
            Format: {
                'text': str,
                'boxes': list of {'text': str, 'left': int, 'top': int, 
                                  'width': int, 'height': int, 'conf': float}
            }
        """
        try:
            image = Image.open(image_path)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract text with bounding boxes
            boxes = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:  # Only include non-empty text
                    box = {
                        'text': text,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'conf': float(data['conf'][i])
                    }
                    boxes.append(box)
            
            full_text = pytesseract.image_to_string(image)
            
            result = {
                'text': full_text,
                'boxes': boxes,
                'image_width': image.width,
                'image_height': image.height
            }
            
            logging.info(f"Extracted {len(boxes)} text boxes from {Path(image_path).name}")
            return result
            
        except Exception as e:
            logging.error(f"Error extracting text with boxes: {e}")
            return {'text': '', 'boxes': [], 'image_width': 0, 'image_height': 0}
    
    def extract_text_with_formatting(self, image_path):
        """
        Extract text with formatting information (bold, italic, font size estimates)
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Text with formatting data
            Format: {
                'text': str,
                'words': list of {
                    'text': str,
                    'x': int, 'y': int,
                    'width': int, 'height': int,
                    'font_size_estimate': int,
                    'confidence': float
                }
            }
        """
        try:
            image = Image.open(image_path)
            
            # Get word-level data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            words = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text and data['conf'][i] > 0:  # Only confident detections
                    word = {
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'font_size_estimate': data['height'][i],  # Height approximates font size
                        'confidence': float(data['conf'][i])
                    }
                    words.append(word)
            
            full_text = pytesseract.image_to_string(image)
            
            return {
                'text': full_text,
                'words': words,
                'image_width': image.width,
                'image_height': image.height
            }
            
        except Exception as e:
            logging.error(f"Error extracting formatted text: {e}")
            return {'text': '', 'words': [], 'image_width': 0, 'image_height': 0}
    
    def get_text_orientation(self, image_path):
        """
        Detect text orientation in image
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Orientation info (angle, confidence)
        """
        try:
            image = Image.open(image_path)
            osd = pytesseract.image_to_osd(image)
            
            # Parse OSD output
            lines = osd.split('\n')
            orientation_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    orientation_data[key.strip()] = value.strip()
            
            return orientation_data
            
        except Exception as e:
            logging.error(f"Error detecting orientation: {e}")
            return {}
    
    def process_image(self, image_path, extract_formatting=True, extract_colors=False, progress_callback=None):
        """
        Main processing method - extracts all available information
        
        Args:
            image_path: Path to image file
            extract_formatting: Whether to extract detailed formatting
            extract_colors: Whether to detect text colors (Phase 2)
            progress_callback: Optional callback for progress updates
            
        Returns:
            dict: Complete OCR results with optional color data
        """
        try:
            if progress_callback:
                progress_callback("Starting OCR...")
            
            # Extract text with formatting
            if extract_formatting:
                if progress_callback:
                    progress_callback("Extracting text with formatting...")
                result = self.extract_text_with_formatting(image_path)
            else:
                if progress_callback:
                    progress_callback("Extracting text...")
                text = self.extract_text(image_path)
                result = {'text': text, 'words': []}
            
            # Add color detection if requested (Phase 2)
            if extract_colors and result.get('words'):
                if progress_callback:
                    progress_callback("Detecting text colors...")
                
                from .color_detector import ColorDetector
                color_detector = ColorDetector()
                
                # Detect colors for each word
                for word_data in result['words']:
                    text_box = {
                        'left': word_data['x'],
                        'top': word_data['y'],
                        'width': word_data['width'],
                        'height': word_data['height']
                    }
                    color = color_detector.detect_text_color(image_path, text_box)
                    word_data['color'] = color
                
                if progress_callback:
                    progress_callback("Color detection complete")
            
            if progress_callback:
                progress_callback("OCR complete")
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            return {'text': '', 'words': [], 'error': str(e)}
    
    def is_tesseract_available(self):
        """
        Check if Tesseract is available and working
        
        Returns:
            bool: True if Tesseract is available
        """
        try:
            version = pytesseract.get_tesseract_version()
            logging.info(f"Tesseract version: {version}")
            return True
        except Exception as e:
            logging.error(f"Tesseract not available: {e}")
            return False
