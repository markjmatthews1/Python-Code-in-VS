"""
PDF Handler Module
Handles PDF to image conversion for OCR processing
"""

from pathlib import Path
from PIL import Image
import logging
import os

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logging.warning("pdf2image not installed. PDF conversion will not work.")


class PDFHandler:
    """Handle PDF file operations and conversions"""
    
    def __init__(self, temp_dir="temp/pdf_pages"):
        """
        Initialize PDF handler
        
        Args:
            temp_dir: Directory for temporary PDF page images
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Set path to bundled Poppler
        self.poppler_path = self._get_poppler_path()
        if self.poppler_path:
            logging.info(f"Using bundled Poppler at: {self.poppler_path}")
    
    def _get_poppler_path(self):
        """Get path to bundled Poppler binaries"""
        # Get the directory where this script is located
        current_dir = Path(__file__).parent.parent
        poppler_bin = current_dir / "poppler-24.08.0" / "Library" / "bin"
        
        if poppler_bin.exists():
            return str(poppler_bin)
        
        logging.warning("Bundled Poppler not found, will try system Poppler")
        return None
        
    def is_pdf(self, file_path):
        """
        Check if file is a PDF
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if PDF, False otherwise
        """
        return Path(file_path).suffix.lower() == '.pdf'
    
    def get_page_count(self, pdf_path):
        """
        Get number of pages in PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            int: Number of pages, or 0 if error
        """
        if not PDF2IMAGE_AVAILABLE:
            return 0
            
        try:
            # Quick check using pdf2image
            images = convert_from_path(
                pdf_path,
                dpi=72,  # Low DPI just for counting
                first_page=1,
                last_page=1,
                poppler_path=self.poppler_path
            )
            
            # Try converting all pages to get count
            images = convert_from_path(pdf_path, dpi=72, poppler_path=self.poppler_path)
            return len(images)
            
        except Exception as e:
            logging.error(f"Error getting page count: {e}")
            return 0
    
    def convert_pdf_to_images(self, pdf_path, dpi=300, progress_callback=None):
        """
        Convert PDF pages to images
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for conversion (default 300 for good quality)
            progress_callback: Optional callback function(current_page, total_pages)
            
        Returns:
            list: Paths to generated image files
        """
        if not PDF2IMAGE_AVAILABLE:
            raise ImportError("pdf2image is required for PDF conversion. Install with: pip install pdf2image")
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Convert PDF to images
            logging.info(f"Converting PDF: {pdf_path.name} at {dpi} DPI")
            images = convert_from_path(str(pdf_path), dpi=dpi, poppler_path=self.poppler_path)
            
            # Save each page as an image
            image_paths = []
            total_pages = len(images)
            
            for i, image in enumerate(images, 1):
                # Create filename
                page_filename = f"{pdf_path.stem}_page_{i:03d}.png"
                page_path = self.temp_dir / page_filename
                
                # Save image
                image.save(page_path, "PNG")
                image_paths.append(str(page_path))
                
                logging.info(f"Saved page {i}/{total_pages}: {page_filename}")
                
                # Progress callback
                if progress_callback:
                    progress_callback(i, total_pages)
            
            logging.info(f"Successfully converted {total_pages} pages")
            return image_paths
            
        except Exception as e:
            logging.error(f"Error converting PDF to images: {e}")
            raise
    
    def convert_single_page(self, pdf_path, page_number, dpi=300):
        """
        Convert a single PDF page to image
        
        Args:
            pdf_path: Path to PDF file
            page_number: Page number (1-indexed)
            dpi: Resolution for conversion
            
        Returns:
            str: Path to generated image file
        """
        if not PDF2IMAGE_AVAILABLE:
            raise ImportError("pdf2image is required")
        
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=dpi,
                first_page=page_number,
                last_page=page_number,
                poppler_path=self.poppler_path
            )
            
            if images:
                page_filename = f"{Path(pdf_path).stem}_page_{page_number:03d}.png"
                page_path = self.temp_dir / page_filename
                images[0].save(page_path, "PNG")
                return str(page_path)
            
        except Exception as e:
            logging.error(f"Error converting page {page_number}: {e}")
            raise
    
    def cleanup_temp_files(self):
        """Remove temporary PDF page images"""
        try:
            for file in self.temp_dir.glob("*.png"):
                file.unlink()
            logging.info("Cleaned up temporary PDF images")
        except Exception as e:
            logging.error(f"Error cleaning up temp files: {e}")
    
    def validate_image(self, image_path):
        """
        Validate that image file is readable
        
        Args:
            image_path: Path to image file
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            logging.error(f"Invalid image {image_path}: {e}")
            return False
