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
    
    def scan_with_dialog(self) -> Optional[str]:
        """
        Show Windows scan dialog and scan image
        Easier for users - lets Windows handle all settings
        
        Returns:
            Path to saved image file, or None if cancelled
        """
        if not self.is_available():
            return None
        
        try:
            # Show scan dialog - user can adjust all settings
            image = self.wia.ShowAcquireImage(1)  # Type 1 = Scanner
            
            if image:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recipe_scan_{timestamp}.png"
                filepath = self.save_directory / filename
                
                # Save image
                image.SaveFile(str(filepath))
                
                return str(filepath)
            else:
                return None
                
        except Exception as e:
            print(f"Error in scan dialog: {e}")
            return None
    
    def scan_from_file(self, file_path: str) -> Optional[str]:
        """
        Import an existing image file (for testing or manual import)
        Copies file to scanned_images directory
        
        Args:
            file_path: Path to existing image file
        
        Returns:
            Path to copied image in scanned directory
        """
        try:
            source = Path(file_path)
            if not source.exists():
                return None
            
            # Copy to scanned images directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = source.suffix
            filename = f"recipe_import_{timestamp}{extension}"
            destination = self.save_directory / filename
            
            # Copy file
            import shutil
            shutil.copy2(source, destination)
            
            return str(destination)
            
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


# Utility function for quick scanning
def quick_scan(save_dir: str = "data/scanned_images") -> Optional[str]:
    """
    Quick scan function - shows dialog and returns scanned image path
    
    Args:
        save_dir: Directory to save scanned images
    
    Returns:
        Path to scanned image or None
    """
    scanner = ScannerInterface(save_dir)
    if not scanner.is_available():
        print("Scanner not available. Please install pywin32: pip install pywin32")
        return None
    
    return scanner.scan_with_dialog()
