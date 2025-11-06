"""
OCR Document Converter
Main application - Convert PDF and images to Word documents with OCR

Created: November 3, 2025
Author: AI Assistant
Purpose: Genealogy document conversion with color preservation
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import logging
import threading
from datetime import datetime

from converter import PDFHandler, OCRProcessor, DocxGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_converter.log'),
        logging.StreamHandler()
    ]
)


class OCRConverterApp(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("OCR Document Converter")
        self.geometry("900x700")
        
        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Color scheme
        self.colors = {
            'primary': '#2196F3',      # Blue
            'secondary': '#1976D2',    # Dark Blue
            'success': '#4CAF50',      # Green
            'warning': '#FF9800',      # Orange
            'error': '#F44336',        # Red
            'bg_light': '#F5F5F5',     # Light Gray
            'bg_dark': '#263238',      # Dark Blue-Gray
            'text_dark': '#212121',    # Dark text
            'text_light': '#FFFFFF',   # Light text
            'card_bg': '#FFFFFF',      # White
        }
        
        # Initialize converters
        self.pdf_handler = PDFHandler()
        self.ocr_processor = OCRProcessor()
        self.docx_generator = DocxGenerator()
        
        # Check if Tesseract is available
        if not self.ocr_processor.is_tesseract_available():
            messagebox.showerror(
                "Tesseract Not Found",
                "Tesseract OCR is not available.\n\n"
                "Please ensure Tesseract is installed or bundled with this application."
            )
        
        # File queue
        self.file_queue = []
        self.processing = False
        
        # Settings
        self.preserve_colors = ctk.BooleanVar(value=True)
        self.extract_images = ctk.BooleanVar(value=True)
        self.detect_formatting = ctk.BooleanVar(value=True)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Create UI
        self.create_header()
        self.create_main_area()
        self.create_status_bar()
        
        logging.info("OCR Document Converter started")
    
    def create_header(self):
        """Create application header"""
        header = ctk.CTkFrame(self, fg_color=self.colors['primary'], height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="📄 OCR Document Converter",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors['text_light']
        )
        title.pack(side="left", padx=30, pady=20)
        
        subtitle = ctk.CTkLabel(
            header,
            text="Convert PDF & Images to Word Documents",
            font=("Helvetica", 14),
            text_color=self.colors['text_light']
        )
        subtitle.pack(side="left", padx=(0, 20))
    
    def create_main_area(self):
        """Create main content area"""
        main_frame = ctk.CTkFrame(self, fg_color=self.colors['bg_light'])
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Left panel - File selection and queue
        left_panel = ctk.CTkFrame(main_frame, fg_color=self.colors['card_bg'], width=500)
        left_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # File selection area
        file_label = ctk.CTkLabel(
            left_panel,
            text="📁 Select Files",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors['text_dark']
        )
        file_label.pack(pady=(20, 10))
        
        # Drop zone (simulated)
        drop_frame = ctk.CTkFrame(left_panel, fg_color=self.colors['bg_light'], height=150)
        drop_frame.pack(fill="x", padx=20, pady=(0, 10))
        drop_frame.pack_propagate(False)
        
        drop_label = ctk.CTkLabel(
            drop_frame,
            text="Drag & Drop Files Here\n(Feature coming soon)\n\nOR",
            font=("Helvetica", 14),
            text_color=self.colors['text_dark']
        )
        drop_label.pack(expand=True)
        
        # Browse button
        browse_btn = ctk.CTkButton(
            left_panel,
            text="📂 Browse Files...",
            font=("Helvetica", 14, "bold"),
            width=200,
            height=40,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            command=self.browse_files
        )
        browse_btn.pack(pady=10)
        
        # File queue
        queue_label = ctk.CTkLabel(
            left_panel,
            text="📋 File Queue",
            font=("Helvetica", 16, "bold"),
            text_color=self.colors['text_dark']
        )
        queue_label.pack(pady=(20, 10))
        
        # Queue list
        self.queue_frame = ctk.CTkScrollableFrame(left_panel, fg_color=self.colors['bg_light'])
        self.queue_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Right panel - Options and controls
        right_panel = ctk.CTkFrame(main_frame, fg_color=self.colors['card_bg'], width=320)
        right_panel.pack(side="right", fill="y", padx=(0, 20), pady=20)
        right_panel.pack_propagate(False)
        
        # Options
        options_label = ctk.CTkLabel(
            right_panel,
            text="⚙️ Options",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors['text_dark']
        )
        options_label.pack(pady=(20, 15))
        
        # Color preservation
        color_check = ctk.CTkCheckBox(
            right_panel,
            text="Preserve Text Colors",
            variable=self.preserve_colors,
            font=("Helvetica", 13),
            text_color=self.colors['text_dark']
        )
        color_check.pack(pady=8, padx=20, anchor="w")
        
        # Image extraction
        image_check = ctk.CTkCheckBox(
            right_panel,
            text="Extract Images",
            variable=self.extract_images,
            font=("Helvetica", 13),
            text_color=self.colors['text_dark']
        )
        image_check.pack(pady=8, padx=20, anchor="w")
        
        # Formatting detection
        format_check = ctk.CTkCheckBox(
            right_panel,
            text="Detect Formatting",
            variable=self.detect_formatting,
            font=("Helvetica", 13),
            text_color=self.colors['text_dark']
        )
        format_check.pack(pady=8, padx=20, anchor="w")
        
        # Output directory
        output_label = ctk.CTkLabel(
            right_panel,
            text="Output Directory:",
            font=("Helvetica", 13, "bold"),
            text_color=self.colors['text_dark']
        )
        output_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        output_display = ctk.CTkLabel(
            right_panel,
            text=str(self.output_dir),
            font=("Helvetica", 11),
            text_color=self.colors['text_dark']
        )
        output_display.pack(pady=(0, 5), padx=20, anchor="w")
        
        output_btn = ctk.CTkButton(
            right_panel,
            text="Change...",
            width=100,
            height=30,
            font=("Helvetica", 11),
            fg_color=self.colors['secondary'],
            command=self.change_output_dir
        )
        output_btn.pack(pady=5, padx=20, anchor="w")
        
        # Progress section
        progress_label = ctk.CTkLabel(
            right_panel,
            text="📊 Progress",
            font=("Helvetica", 16, "bold"),
            text_color=self.colors['text_dark']
        )
        progress_label.pack(pady=(30, 10))
        
        self.progress_bar = ctk.CTkProgressBar(
            right_panel,
            width=260,
            height=20,
            fg_color=self.colors['bg_light'],
            progress_color=self.colors['success']
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            right_panel,
            text="Ready",
            font=("Helvetica", 11),
            text_color=self.colors['text_dark']
        )
        self.progress_label.pack(pady=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        button_frame.pack(side="bottom", pady=20)
        
        self.convert_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Convert All",
            font=("Helvetica", 15, "bold"),
            width=260,
            height=50,
            fg_color=self.colors['success'],
            hover_color="#45a049",
            command=self.start_conversion
        )
        self.convert_btn.pack(pady=5)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Queue",
            font=("Helvetica", 13),
            width=260,
            height=35,
            fg_color=self.colors['warning'],
            command=self.clear_queue
        )
        clear_btn.pack(pady=5)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ctk.CTkFrame(self, fg_color=self.colors['bg_dark'], height=30)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready - No files in queue",
            font=("Helvetica", 11),
            text_color=self.colors['text_light']
        )
        self.status_label.pack(side="left", padx=20)
    
    def browse_files(self):
        """Open file browser to select files"""
        file_paths = filedialog.askopenfilenames(
            title="Select PDF or Image Files",
            filetypes=[
                ("All supported", "*.pdf *.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            for file_path in file_paths:
                self.add_file_to_queue(file_path)
    
    def add_file_to_queue(self, file_path):
        """Add a file to the conversion queue"""
        file_path = Path(file_path)
        
        # Check if already in queue
        if any(item['path'] == file_path for item in self.file_queue):
            return
        
        # Add to queue
        file_info = {
            'path': file_path,
            'status': 'Ready',
            'output_path': None
        }
        self.file_queue.append(file_info)
        
        # Update UI
        self.update_queue_display()
        self.update_status()
        logging.info(f"Added to queue: {file_path.name}")
    
    def update_queue_display(self):
        """Update the file queue display"""
        # Clear current display
        for widget in self.queue_frame.winfo_children():
            widget.destroy()
        
        if not self.file_queue:
            empty_label = ctk.CTkLabel(
                self.queue_frame,
                text="No files in queue",
                font=("Helvetica", 12),
                text_color=self.colors['text_dark']
            )
            empty_label.pack(pady=20)
            return
        
        # Display each file
        for idx, file_info in enumerate(self.file_queue):
            file_frame = ctk.CTkFrame(self.queue_frame, fg_color=self.colors['card_bg'])
            file_frame.pack(fill="x", padx=5, pady=5)
            
            # File name
            name_label = ctk.CTkLabel(
                file_frame,
                text=f"• {file_info['path'].name}",
                font=("Helvetica", 12),
                text_color=self.colors['text_dark'],
                anchor="w"
            )
            name_label.pack(side="left", padx=10, pady=8)
            
            # Status
            status_color = self.colors['text_dark']
            if file_info['status'] == 'Done':
                status_color = self.colors['success']
            elif file_info['status'] == 'Error':
                status_color = self.colors['error']
            elif file_info['status'] == 'Processing':
                status_color = self.colors['warning']
            
            status_label = ctk.CTkLabel(
                file_frame,
                text=f"[{file_info['status']}]",
                font=("Helvetica", 11, "bold"),
                text_color=status_color
            )
            status_label.pack(side="right", padx=10, pady=8)
    
    def update_status(self):
        """Update status bar text"""
        count = len(self.file_queue)
        ready = sum(1 for f in self.file_queue if f['status'] == 'Ready')
        done = sum(1 for f in self.file_queue if f['status'] == 'Done')
        
        if self.processing:
            self.status_label.configure(text=f"Processing - {done}/{count} completed")
        elif count == 0:
            self.status_label.configure(text="Ready - No files in queue")
        else:
            self.status_label.configure(text=f"Ready - {count} files in queue ({done} completed)")
    
    def change_output_dir(self):
        """Change output directory"""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir = Path(dir_path)
            logging.info(f"Output directory changed to: {self.output_dir}")
    
    def clear_queue(self):
        """Clear the file queue"""
        if self.file_queue and not self.processing:
            result = messagebox.askyesno(
                "Clear Queue",
                f"Remove all {len(self.file_queue)} files from queue?"
            )
            if result:
                self.file_queue.clear()
                self.update_queue_display()
                self.update_status()
                logging.info("Queue cleared")
    
    def start_conversion(self):
        """Start converting all files in queue"""
        if not self.file_queue:
            messagebox.showwarning("No Files", "Please add files to the queue first!")
            return
        
        if self.processing:
            messagebox.showinfo("Processing", "Conversion already in progress!")
            return
        
        # Start conversion in background thread
        self.processing = True
        self.convert_btn.configure(state="disabled", text="Processing...")
        
        thread = threading.Thread(target=self.process_queue, daemon=True)
        thread.start()
    
    def process_queue(self):
        """Process all files in the queue (runs in background thread)"""
        total = len(self.file_queue)
        
        for idx, file_info in enumerate(self.file_queue, 1):
            if file_info['status'] != 'Ready':
                continue  # Skip already processed files
            
            try:
                # Update UI
                file_info['status'] = 'Processing'
                self.after(0, self.update_queue_display)
                self.after(0, self.update_status)
                self.after(0, lambda i=idx, t=total: self.progress_label.configure(
                    text=f"Processing file {i} of {t}..."
                ))
                
                # Process file
                output_path = self.convert_file(file_info['path'], idx, total)
                
                # Update success
                file_info['status'] = 'Done'
                file_info['output_path'] = output_path
                
                logging.info(f"Completed: {file_info['path'].name} -> {output_path}")
                
            except Exception as e:
                file_info['status'] = 'Error'
                logging.error(f"Error processing {file_info['path'].name}: {e}")
                messagebox.showerror("Conversion Error", f"Failed to convert:\n{file_info['path'].name}\n\nError: {str(e)}")
            
            finally:
                # Update UI
                self.after(0, self.update_queue_display)
                self.after(0, self.update_status)
        
        # Conversion complete
        self.processing = False
        self.after(0, lambda: self.convert_btn.configure(state="normal", text="🚀 Convert All"))
        self.after(0, lambda: self.progress_bar.set(1))
        self.after(0, lambda: self.progress_label.configure(text=f"Completed {total} files!"))
        
        self.after(0, lambda: messagebox.showinfo(
            "Conversion Complete",
            f"Successfully converted {total} files!\n\nOutput directory: {self.output_dir}"
        ))
    
    def convert_file(self, file_path, current_num, total_num):
        """
        Convert a single file to Word document
        
        Args:
            file_path: Path to input file
            current_num: Current file number
            total_num: Total number of files
            
        Returns:
            str: Path to output file
        """
        file_path = Path(file_path)
        
        # Determine output filename
        output_filename = f"{file_path.stem}.docx"
        output_path = self.output_dir / output_filename
        
        # Handle PDF vs image
        if self.pdf_handler.is_pdf(file_path):
            # Convert PDF to images
            self.after(0, lambda: self.progress_label.configure(text=f"Converting PDF pages..."))
            
            def pdf_progress(page, total):
                self.after(0, lambda p=page, t=total: self.progress_bar.set(p / t * 0.3))
            
            image_paths = self.pdf_handler.convert_pdf_to_images(file_path, progress_callback=pdf_progress)
            
            # OCR each page
            page_results = []
            for page_num, image_path in enumerate(image_paths, 1):
                self.after(0, lambda p=page_num, t=len(image_paths): self.progress_label.configure(
                    text=f"OCR page {p} of {t}..."
                ))
                
                progress_val = 0.3 + (page_num / len(image_paths)) * 0.6
                self.after(0, lambda v=progress_val: self.progress_bar.set(v))
                
                # Extract formatting and colors if requested
                ocr_result = self.ocr_processor.process_image(
                    image_path,
                    extract_formatting=self.detect_formatting.get(),
                    extract_colors=self.preserve_colors.get()
                )
                page_results.append(ocr_result)
            
            # Create Word document
            self.after(0, lambda: self.progress_label.configure(text="Creating Word document..."))
            self.after(0, lambda: self.progress_bar.set(0.95))
            
            self.docx_generator.create_multi_page_document(page_results, output_path, preserve_colors=self.preserve_colors.get())
            
            # Cleanup
            self.pdf_handler.cleanup_temp_files()
            
        else:
            # Single image file
            self.after(0, lambda: self.progress_label.configure(text="Processing image..."))
            self.after(0, lambda: self.progress_bar.set(0.5))
            
            # Extract formatting and colors if requested
            ocr_result = self.ocr_processor.process_image(
                file_path,
                extract_formatting=self.detect_formatting.get(),
                extract_colors=self.preserve_colors.get()
            )
            
            self.after(0, lambda: self.progress_label.configure(text="Creating Word document..."))
            self.after(0, lambda: self.progress_bar.set(0.9))
            
            self.docx_generator.create_formatted_document(ocr_result, output_path, preserve_colors=self.preserve_colors.get())
        
        self.after(0, lambda: self.progress_bar.set(1))
        return str(output_path)


def main():
    """Main entry point"""
    app = OCRConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
