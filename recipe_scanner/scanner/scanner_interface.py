"""
Scanner Interface for Recipe Scanner Pro
Handles Windows scanner integration via WIA (Windows Image Acquisition)
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
from PIL import Image
import io

# Try to import Windows scanner libraries
try:
    import win32com.client
    WIA_AVAILABLE = True
except ImportError:
    WIA_AVAILABLE = False
    print("Warning: pywin32 not available. Scanner functionality will be limited.")

# Try to import PDF libraries
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
    PDF_BACKEND = "pymupdf"
except ImportError:
    try:
        from pdf2image import convert_from_path
        PDF_AVAILABLE = True
        PDF_BACKEND = "pdf2image"
    except ImportError:
        PDF_AVAILABLE = False
        PDF_BACKEND = None
        print("Warning: No PDF library available. Install PyMuPDF with: pip install PyMuPDF")


class ScannerInterface:
    """Interface for scanning documents using Windows WIA"""
    
    def __init__(self, save_directory: str = "data/scanned_images"):
        """Initialize scanner interface"""
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.wia = None
        self.device_manager = None
        self.scanner = None
        
        if WIA_AVAILABLE:
            try:
                self.device_manager = win32com.client.Dispatch("WIA.DeviceManager")
                self.wia = win32com.client.Dispatch("WIA.CommonDialog")
            except Exception as e:
                print(f"Error initializing WIA: {e}")
    
    def is_available(self) -> bool:
        """Check if scanner functionality is available"""
        return WIA_AVAILABLE and self.device_manager is not None
    
    def get_scanners(self) -> List[str]:
        """Get list of available scanners"""
        if not self.is_available():
            return []
        
        try:
            scanners = []
            for i in range(1, self.device_manager.DeviceInfos.Count + 1):
                device_info = self.device_manager.DeviceInfos.Item(i)
                # Check if device is a scanner (Type 1 = Scanner)
                if device_info.Type == 1:
                    scanners.append(device_info.Properties("Name").Value)
            return scanners
        except Exception as e:
            print(f"Error getting scanners: {e}")
            return []
    
    def select_scanner(self) -> bool:
        """Show scanner selection dialog and select a scanner"""
        if not self.is_available():
            return False
        
        try:
            # Show device selection dialog
            self.scanner = self.wia.ShowSelectDevice(1, True, False)  # Type 1 = Scanner
            return self.scanner is not None
        except Exception as e:
            print(f"Error selecting scanner: {e}")
            return False
    
    def scan_image(self, color_mode: str = "color", resolution: int = 300, 
                   format: str = "PNG") -> Optional[str]:
        """
        Scan an image using the selected scanner
        
        Args:
            color_mode: 'color', 'grayscale', or 'bw' (black & white)
            resolution: DPI (dots per inch), typically 150-600
            format: Image format ('PNG', 'JPEG', 'BMP')
        
        Returns:
            Path to saved image file, or None if scan failed
        """
        if not self.is_available():
            return None
        
        try:
            # If no scanner selected, prompt for selection
            if not self.scanner:
                if not self.select_scanner():
                    return None
            
            # Set scan properties
            item = self.scanner.Items(1)
            
            # Color mode
            # 1 = B&W, 2 = Grayscale, 4 = Color
            color_code = {
                'bw': 1,
                'grayscale': 2,
                'color': 4
            }.get(color_mode.lower(), 4)
            
            try:
                item.Properties("6146").Value = color_code  # Current Intent (Color Mode)
            except:
                pass  # Some scanners don't support this property
            
            # Resolution (DPI)
            try:
                item.Properties("6147").Value = resolution  # Horizontal Resolution
                item.Properties("6148").Value = resolution  # Vertical Resolution
            except:
                pass  # Some scanners don't support setting resolution
            
            # Perform scan
            image = item.Transfer("{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}")  # PNG format
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recipe_scan_{timestamp}.{format.lower()}"
            filepath = self.save_directory / filename
            
            # Save image
            image.SaveFile(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            print(f"Error scanning image: {e}")
            return None
    
    def scan_with_dialog(self) -> Optional[List[str]]:
        """
        Show Windows scan dialog and scan image
        Uses the standard Windows scanning dialog which allows user to select:
        - Flatbed vs Document Feeder
        - Resolution, color mode, etc.
        
        Returns:
            List with single scanned image path, or None if cancelled
            (Returns list for consistency with multi-page workflow)
        """
        if not self.is_available():
            return None
        
        try:
            base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            print(f"DEBUG: Showing Windows scan dialog...")
            print(f"DEBUG: Save directory: {self.save_directory}")
            
            # Show the standard Windows scan dialog
            # This lets the user choose flatbed vs feeder, resolution, color, etc.
            image = self.wia.ShowAcquireImage(1)  # Type 1 = Scanner
            
            if not image:
                print("DEBUG: User cancelled scan or no image returned")
                return None
            
            # Save the scanned image
            filename = f"recipe_scan_{base_timestamp}_page1.png"
            filepath = self.save_directory / filename
            image.SaveFile(str(filepath))
            print(f"DEBUG: Saved: {filepath}")
            
            # Return as list for consistency
            return [str(filepath)]
                
        except Exception as e:
            print(f"ERROR in scan_with_dialog: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scan_multiple_pages(self, color_mode: str = "color", resolution: int = 300) -> Optional[List[str]]:
        """
        Scan multiple pages from document feeder automatically
        Continues scanning until feeder is empty
        
        Args:
            color_mode: 'color', 'grayscale', or 'bw'
            resolution: DPI (dots per inch)
        
        Returns:
            List of paths to saved image files, or None if scan failed
        """
        if not self.is_available():
            return None
        
        try:
            # If no scanner selected, prompt for selection
            if not self.scanner:
                if not self.select_scanner():
                    return None
            
            scanned_pages = []
            base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page_num = 1
            max_pages = 50  # Safety limit
            
            # Color mode setting
            color_code = {
                'bw': 1,
                'grayscale': 2,
                'color': 4
            }.get(color_mode.lower(), 4)
            
            while page_num <= max_pages:
                try:
                    item = self.scanner.Items(1)
                    
                    # Set scan properties for each page
                    try:
                        item.Properties("6146").Value = color_code
                        item.Properties("6147").Value = resolution
                        item.Properties("6148").Value = resolution
                    except:
                        pass
                    
                    # Perform scan
                    image = item.Transfer("{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}")
                    
                    if image:
                        filename = f"recipe_scan_{base_timestamp}_page{page_num}.png"
                        filepath = self.save_directory / filename
                        image.SaveFile(str(filepath))
                        scanned_pages.append(str(filepath))
                        print(f"Scanned page {page_num}: {filepath}")
                        page_num += 1
                    else:
                        break
                        
                except Exception as e:
                    # Feeder is empty or error occurred
                    print(f"Finished scanning: {e}")
                    break
            
            print(f"Total pages scanned: {len(scanned_pages)}")
            return scanned_pages if scanned_pages else None
            
        except Exception as e:
            print(f"Error scanning multiple pages: {e}")
            return None
    
    def scan_from_file(self, file_path: str) -> Optional[List[str]]:
        """
        Import an existing image or PDF file (for testing or manual import)
        Copies file to scanned_images directory, or converts PDF to images
        
        Args:
            file_path: Path to existing image or PDF file
        
        Returns:
            List of paths to copied/converted images in scanned directory
        """
        try:
            source = Path(file_path)
            if not source.exists():
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = source.suffix.lower()
            
            # Handle PDF files
            if extension == '.pdf':
                if not PDF_AVAILABLE:
                    print("Error: PDF library not installed. Cannot import PDF files.")
                    print("Install with: pip install PyMuPDF")
                    return None
                
                try:
                    # Convert PDF to images (one image per page)
                    print(f"Converting PDF to images using {PDF_BACKEND}...")
                    converted_paths = []
                    
                    if PDF_BACKEND == "pymupdf":
                        # Use PyMuPDF (faster, no external dependencies)
                        import fitz
                        pdf_document = fitz.open(str(source))
                        
                        for page_num in range(len(pdf_document)):
                            page = pdf_document[page_num]
                            # Render page to image at 300 DPI
                            mat = fitz.Matrix(300/72, 300/72)  # 72 is default DPI
                            pix = page.get_pixmap(matrix=mat)
                            
                            filename = f"recipe_import_{timestamp}_page{page_num + 1}.png"
                            destination = self.save_directory / filename
                            pix.save(destination)
                            converted_paths.append(str(destination))
                            print(f"Converted PDF page {page_num + 1} to {destination}")
                        
                        pdf_document.close()
                    
                    else:  # pdf2image backend
                        from pdf2image import convert_from_path
                        images = convert_from_path(str(source), dpi=300)
                        
                        for i, image in enumerate(images, start=1):
                            filename = f"recipe_import_{timestamp}_page{i}.png"
                            destination = self.save_directory / filename
                            image.save(destination, 'PNG')
                            converted_paths.append(str(destination))
                            print(f"Converted PDF page {i} to {destination}")
                    
                    print(f"Successfully converted {len(converted_paths)} page(s) from PDF")
                    return converted_paths
                    
                except Exception as e:
                    print(f"Error converting PDF: {e}")
                    if PDF_BACKEND == "pdf2image":
                        print("Make sure poppler is installed: https://github.com/oschwartz10612/poppler-windows/releases/")
                    return None
            
            # Handle regular image files
            else:
                filename = f"recipe_import_{timestamp}{extension}"
                destination = self.save_directory / filename
                
                # Copy file
                import shutil
                shutil.copy2(source, destination)
                
                return [str(destination)]
            
        except Exception as e:
            print(f"Error importing file: {e}")
            return None
    
    def get_image_preview(self, image_path: str, max_size: Tuple[int, int] = (400, 400)) -> Optional[Image.Image]:
        """
        Get a PIL Image preview of scanned image
        
        Args:
            image_path: Path to image file
            max_size: Maximum (width, height) for preview
        
        Returns:
            PIL Image object resized to fit max_size
        """
        try:
            img = Image.open(image_path)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"Error loading image preview: {e}")
            return None
    
    def preprocess_image(self, image_path: str, enhance: bool = True) -> str:
        """
        Preprocess scanned image for better OCR results
        
        Args:
            image_path: Path to original image
            enhance: Apply enhancement filters
        
        Returns:
            Path to processed image
        """
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            if enhance:
                from PIL import ImageEnhance, ImageFilter
                
                # Increase contrast slightly
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
                
                # Increase sharpness
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.5)
                
                # Apply slight blur to reduce noise
                img = img.filter(ImageFilter.SMOOTH)
            
            # Save processed image
            processed_path = Path(image_path).parent / f"processed_{Path(image_path).name}"
            img.save(processed_path, quality=95)
            
            return str(processed_path)
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return image_path  # Return original if processing fails
    
    def get_scanned_files(self, limit: int = 10) -> List[str]:
        """
        Get list of recently scanned files
        
        Args:
            limit: Maximum number of files to return
        
        Returns:
            List of file paths, newest first
        """
        try:
            files = sorted(
                self.save_directory.glob("recipe_*.*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            return [str(f) for f in files[:limit]]
        except Exception as e:
            print(f"Error getting scanned files: {e}")
            return []
    
    def delete_scanned_file(self, file_path: str) -> bool:
        """Delete a scanned file"""
        try:
            Path(file_path).unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


    def combine_pages_to_single_image(self, image_paths: List[str], output_path: Optional[str] = None) -> Optional[str]:
        """
        Combine multiple scanned pages into a single vertical image
        Useful for creating a single image from multi-page scans
        
        Args:
            image_paths: List of image file paths to combine
            output_path: Optional output path. If None, auto-generates filename
        
        Returns:
            Path to combined image file, or None if failed
        """
        try:
            if not image_paths:
                return None
            
            # Load all images
            images = [Image.open(path) for path in image_paths]
            
            # Calculate total height and max width
            widths = [img.width for img in images]
            heights = [img.height for img in images]
            max_width = max(widths)
            total_height = sum(heights)
            
            # Create new image with white background
            combined = Image.new('RGB', (max_width, total_height), 'white')
            
            # Paste images vertically
            y_offset = 0
            for img in images:
                combined.paste(img, (0, y_offset))
                y_offset += img.height
            
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recipe_scan_{timestamp}_combined.png"
                output_path = str(self.save_directory / filename)
            
            # Save combined image
            combined.save(output_path, quality=95)
            print(f"Combined {len(images)} pages into: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"Error combining pages: {e}")
            return None


# Utility function for quick scanning
def quick_scan(save_dir: str = "data/scanned_images") -> Optional[List[str]]:
    """
    Quick scan function - shows dialog and returns scanned image path(s)
    
    Args:
        save_dir: Directory to save scanned images
    
    Returns:
        List of paths to scanned images or None
    """
    scanner = ScannerInterface(save_dir)
    if not scanner.is_available():
        print("Scanner not available. Please install pywin32: pip install pywin32")
        return None
    
    return scanner.scan_with_dialog()
