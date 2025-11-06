# OCR Document Converter

Convert PDF and image files to editable Word documents with color preservation and formatting.

## Features
- ✅ Convert PDF (multi-page) and images to Word (.docx)
- ✅ Preserve text colors (important for genealogy documents)
- ✅ Extract and embed images
- ✅ Maintain layout and formatting
- ✅ Batch processing support
- ✅ Visual progress indicators

## Primary Use Case
Designed for genealogy researchers working with scanned historical documents from FamilySearch, Ancestry, and other sources.

## Installation

### Requirements
- Python 3.12+
- Tesseract OCR (bundled)

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Run Application
```bash
python app.py
```

### Basic Workflow
1. **Select Files**: Drag & drop or browse for PDF/image files
2. **Configure Options**: Set color preservation, image extraction, etc.
3. **Convert**: Click "Convert All" to process
4. **Output**: Word documents saved to `output/` directory

## Project Structure
```
ocr_document_converter/
├── app.py                      # Main application
├── converter/
│   ├── ocr_processor.py       # OCR with formatting detection
│   ├── color_detector.py      # Text color extraction
│   ├── pdf_handler.py         # PDF to image conversion
│   └── docx_generator.py      # Word document creation
├── tesseract/                  # Bundled Tesseract OCR
├── temp/                       # Temporary processing files
└── output/                     # Converted documents
```

## Building Standalone Executable

```bash
pyinstaller --onefile --windowed --add-data "tesseract;tesseract" app.py
```

## Development Status
- [x] Project structure created
- [ ] Phase 1: Core OCR (In Progress)
- [ ] Phase 2: Color detection
- [ ] Phase 3: Formatting & layout
- [ ] Phase 4: Image handling
- [ ] Phase 5: Polish & features

## Credits
Built with:
- Tesseract OCR
- CustomTkinter
- python-docx
- pdf2image
- OpenCV

---
Created: November 3, 2025
