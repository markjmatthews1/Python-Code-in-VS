# OCR Document Converter - Project Plan

## Project Overview
Desktop application to convert PDF and image files to editable Word documents (.docx) with OCR, preserving formatting, colors, and images.

## Target Use Case
**Primary User**: Genealogy researchers working with historical documents
- Scanned documents (PDF/JPG) from ancestry websites
- Personal documents that were printed and re-scanned
- Need to preserve text colors (important for annotations/highlights)
- Want to match original layout as closely as possible

## Core Features (Version 1.0)

### Input Handling
- ✅ Accept PDF files (single or multi-page)
- ✅ Accept image files (JPG, PNG, TIFF, BMP)
- ⏳ Drag-and-drop file import (Phase 5)
- ✅ Browse file dialog
- ✅ Batch processing (multiple files with queue)
- ✅ Multi-page PDF processing (each page → Word page)

### OCR Processing
- ✅ Tesseract OCR engine integration (bundled)
- ✅ Extract all text from documents
- ✅ Preserve text positioning (word-level bounding boxes)
- ✅ Detect text regions and bounding boxes
- ✅ Progress indicator for long documents
- ✅ Background threading (non-blocking UI)

### Text Formatting Preservation
- ✅ **Text Color Detection** (HIGH PRIORITY - COMPLETE)
  - ✅ Sample pixel colors from text regions using OpenCV
  - ✅ K-means clustering for dominant color detection
  - ✅ Preserve red, blue, green, black, and other colors
  - ✅ Apply RGB colors to text in Word document
- ✅ **Font Size Detection** (COMPLETE)
  - ✅ Estimate font sizes from character heights
  - ✅ Apply appropriate sizes in Word (pt)
- ⏳ **Font Style Detection** (Phase 3)
  - [ ] Detect bold text
  - [ ] Detect italic text
  - [ ] Apply styles in Word
- ⏳ **Font Family** (Phase 3)
  - [ ] Use sensible defaults (Times New Roman for serif, Arial for sans-serif)
  - [ ] Detect serif vs sans-serif if possible
  - [ ] Manual font override option in settings

### Image Handling
- ⏳ Extract images from PDFs (Phase 4)
- ⏳ Extract images from scanned documents (detect photo regions) (Phase 4)
- ⏳ Embed images in Word document (Phase 4)
- ⏳ Maintain approximate image positions (Phase 4)
- ⏳ Preserve image quality/resolution (Phase 4)

### Output
- ✅ Generate .docx files (Microsoft Word format)
- ✅ Maintain page breaks for multi-page documents
- ✅ Preserve paragraph spacing (line grouping)
- ✅ Save to user-selected location
- ✅ Auto-name based on source filename

### User Interface
- ✅ Modern, clean interface (CustomTkinter)
- ✅ File selection area (browse button)
- ⏳ Preview pane showing original document (Phase 5)
- ✅ Options panel:
  - ✅ Preserve colors (on/off toggle)
  - ⏳ Detect formatting (on/off) - Phase 3
  - ⏳ Image extraction (on/off) - Phase 4
  - ⏳ Output quality settings - Phase 5
- ✅ Progress bar during conversion
- ✅ Success/error notifications (status bar)
- ✅ Batch processing queue with status

## Technical Architecture

### Technology Stack
- **Language**: Python 3.12
- **GUI**: CustomTkinter (modern UI)
- **OCR**: Tesseract 5.x (same as Recipe Scanner)
- **PDF Processing**: pdf2image, PyPDF2
- **Word Generation**: python-docx
- **Image Processing**: Pillow (PIL), OpenCV (color detection)
- **Color Detection**: numpy, opencv-python

### File Structure
```
ocr_document_converter/
├── ocr_app.py                      # Main application (renamed from app.py)
├── converter/
│   ├── __init__.py                # ✅ Module initialization
│   ├── ocr_processor.py           # ✅ OCR with color extraction
│   ├── color_detector.py          # ✅ K-means color detection
│   ├── pdf_handler.py             # ✅ PDF to image conversion
│   └── docx_generator.py          # ✅ Word document creation with RGB colors
├── tesseract/                      # ✅ Bundled Tesseract 5.x (134 files)
├── poppler-24.08.0/                # ✅ Bundled Poppler for PDF support
│   └── Library/bin/               # PDF conversion utilities
├── temp/                           # Temporary processing files
│   └── pdf_pages/                 # Extracted PDF pages
├── output/                         # Default output directory
├── requirements.txt                # ✅ Python dependencies
└── INSTALLATION_COMPLETE.md        # ✅ Setup documentation
```

### Key Libraries Required
```python
# Core functionality - ✅ ALL INSTALLED
pytesseract==0.3.13          # OCR engine - ✅ INSTALLED
pdf2image==1.17.0            # PDF to image conversion - ✅ INSTALLED
python-docx==1.2.0           # Word document creation - ✅ INSTALLED
Pillow==11.2.1               # Image processing - ✅ INSTALLED

# Color and layout detection - ✅ ALL INSTALLED
opencv-python==4.12.0.88     # Advanced image processing - ✅ INSTALLED
numpy==2.2.6                 # Color analysis - ✅ INSTALLED
scikit-learn==1.7.0          # K-means clustering - ✅ INSTALLED

# PDF handling - ✅ ALL INSTALLED
PyPDF2==3.0.1                # PDF manipulation - ✅ INSTALLED
# poppler-24.08.0 bundled (no separate install needed) - ✅ BUNDLED

# UI - ✅ INSTALLED
customtkinter==5.2.2         # Modern GUI - ✅ INSTALLED
```

## Development Phases

### Phase 1: Core OCR ✅ COMPLETE
- ✅ Project setup and structure
- ✅ Basic UI layout (file queue, progress bar)
- ✅ File import (browse button)
- ✅ PDF to image conversion (with bundled Poppler)
- ✅ Basic OCR text extraction
- ✅ Simple Word document generation (plain text)
- ✅ Background processing with threading
- ✅ Progress indicators

### Phase 2: Color Detection ✅ COMPLETE
- ✅ Text region identification (word bounding boxes)
- ✅ Color sampling from text areas (OpenCV)
- ✅ Color classification using k-means clustering
- ✅ Apply colors to Word document text (RGB)
- ✅ Dominant color detection per word
- ✅ Line grouping for better formatting
- ✅ Font size estimation from pixel height

### Phase 3: Advanced Formatting ⏳ NEXT
- [ ] Bold/italic detection (font weight analysis)
- [ ] Underline/strikethrough detection
- [ ] Better font family matching (serif vs sans-serif)
- [ ] Line spacing analysis
- [ ] Paragraph detection improvements
- [ ] Better layout preservation

### Phase 4: Image Handling 📅 PLANNED
- [ ] Image region detection in documents
- [ ] Image extraction from PDFs
- [ ] Image extraction from scanned docs
- [ ] Image embedding in Word documents
- [ ] Position images in document

### Phase 5: Polish & Features 📅 PLANNED
- [ ] Drag-and-drop file import
- [ ] Multi-page handling refinement
- [ ] Better error handling and recovery
- [ ] Settings/preferences storage
- [ ] Help documentation
- [ ] Output directory selection improvements

### Phase 6: Testing & Optimization 📅 PLANNED
- [ ] Test with genealogy documents
- [ ] Test with various PDF formats
- [ ] Performance optimization
- [ ] Bug fixes
- [ ] User feedback incorporation
- [ ] Create standalone .exe with PyInstaller

## Technical Challenges & Solutions

### Challenge 1: Exact Font Matching
**Problem**: Tesseract doesn't identify original fonts
**Solution**: 
- Use heuristics (serif detection via character analysis)
- Provide manual font override
- Default to common fonts (Times New Roman, Arial, Calibri)
- Focus on size and style rather than exact family

### Challenge 2: Color Detection Accuracy
**Problem**: Text colors may vary slightly due to scanning artifacts
**Solution**:
- Sample multiple pixels per character
- Use color clustering to identify dominant colors
- Threshold similar colors (e.g., #000000 and #0A0A0A both → black)
- Provide color adjustment settings

### Challenge 3: Layout Preservation
**Problem**: Word documents handle layout differently than PDFs
**Solution**:
- Use bounding boxes to approximate positions
- Accept "close enough" rather than pixel-perfect
- Focus on reading order and spacing
- Handle single-column layouts well, multi-column as best effort

### Challenge 4: Image Quality
**Problem**: Re-scanning can degrade quality
**Solution**:
- Extract images at original resolution when possible
- Offer quality settings (low/medium/high)
- Don't upscale images unnecessarily
- Preserve aspect ratios

## Success Criteria

### Must Have (v1.0)
✓ Convert PDF/images to Word documents
✓ Preserve text colors accurately (90%+ accuracy)
✓ Extract and include images
✓ Readable text output (95%+ OCR accuracy)
✓ Multi-page support
✓ Batch processing

### Nice to Have (v1.0)
✓ Font size preservation (approximate)
✓ Bold/italic detection
✓ Basic layout preservation
✓ Progress indicators

### Future Versions
- Table detection and recreation
- Better multi-column handling
- Font family matching improvements
- Header/footer preservation
- Metadata preservation (dates, authors)

## Testing Plan

### Test Documents
1. **Simple text documents** (letters, certificates)
2. **Colored text documents** (highlighted genealogy forms)
3. **Documents with images** (family photos with captions)
4. **Multi-page PDFs** (full record sets)
5. **Scanned documents** (various quality levels)
6. **Mixed layouts** (text + images + tables)

### Test Criteria
- OCR accuracy > 95%
- Color preservation > 90%
- Image extraction > 95%
- Layout "looks similar" (subjective)
- Processing time < 30 seconds per page

## User Interface Mockup

```
┌─────────────────────────────────────────────────────┐
│  OCR Document Converter                    [_][□][X]│
├─────────────────────────────────────────────────────┤
│  📁 Select Files                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  Drag & Drop PDF or Image Files Here         │  │
│  │                 OR                            │  │
│  │          [Browse Files...]                    │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  📋 File Queue                     ⚙️ Options        │
│  ┌─────────────────────────┐  ┌──────────────────┐ │
│  │ • document1.pdf [Ready] │  │☑ Preserve Colors │ │
│  │ • scan_page2.jpg [Done] │  │☑ Extract Images  │ │
│  │                         │  │☑ Detect Bold     │ │
│  │                         │  │☐ Advanced Layout │ │
│  │                         │  │                  │ │
│  └─────────────────────────┘  │ Font: [Arial  ▼] │ │
│                                │ Quality: [High▼] │ │
│  📊 Progress                    └──────────────────┘ │
│  ┌───────────────────────────────────────────────┐  │
│  │ Converting: document1.pdf - Page 2/5          │  │
│  │ ████████████████████░░░░░░░░░ 65%            │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  [Convert All]  [Clear Queue]    Output: [Browse..] │
├─────────────────────────────────────────────────────┤
│  Status: Ready - 2 files in queue                   │
└─────────────────────────────────────────────────────┘
```

## Timeline Estimate
- **Phase 1**: ✅ 3 days (Nov 3, 2025) - Core functionality COMPLETE
- **Phase 2**: ✅ Same day (Nov 3, 2025) - Color detection COMPLETE
- **Phase 3**: 📅 3-4 days - Advanced formatting (bold/italic)
- **Phase 4**: 📅 3-4 days - Image extraction and embedding
- **Phase 5**: 📅 2-3 days - Polish and UI improvements
- **Testing**: 📅 2-3 days - Real-world document testing

**Completed**: Phases 1-2 (Core OCR + Color Detection)
**Current Status**: READY TO TEST - Can convert PDFs/images to Word with color preservation
**Next**: Test with real documents, then continue to Phase 3 if needed

## Installation Status

### ✅ COMPLETE - Ready to Use
1. **Tesseract OCR**: ✅ Bundled (134 files, ~200 MB)
   - Location: `ocr_document_converter/tesseract/`
   - Includes English language data
   - No external installation required

2. **Poppler**: ✅ Bundled (v24.08.0)
   - Location: `ocr_document_converter/poppler-24.08.0/Library/bin/`
   - PDF to image conversion utilities
   - Automatically detected by pdf_handler.py

3. **Python Dependencies**: ✅ All installed
   - pytesseract, pdf2image, python-docx, Pillow
   - opencv-python, numpy, scikit-learn
   - customtkinter, PyPDF2

### Launch Command
```cmd
cd "c:\Users\mjmat\Python Code in VS\ocr_document_converter"
python ocr_app.py
```

## Current Capabilities (Phases 1-2)

### ✅ What Works Now:
- Convert PDFs (any page count) to Word documents
- Convert images (JPG, PNG, TIFF, BMP) to Word documents
- Extract text using Tesseract OCR
- **Preserve text colors** (red, blue, green, black, etc.)
- Apply approximate font sizes based on text height
- Group words into lines for better formatting
- Process multiple files in batch mode
- Show progress during conversion
- Multi-page PDF support with page breaks

### ⏳ What's Coming Next (Phase 3+):
- Bold/italic text detection
- Better font family matching
- Image extraction from documents
- Drag-and-drop file import
- Preview pane
- More advanced layout preservation

## Next Steps

### Immediate (Testing Phase)
1. ✅ Installation complete - All dependencies ready
2. 🔄 **Test with simple image** - Screenshot with colored text
3. 🔄 **Test with real genealogy document** - FamilySearch PDF with annotations
4. 🔄 **Verify color preservation** - Check red/blue text in Word output
5. 🔄 **Test multi-page PDF** - Ensure page breaks work correctly
6. 🔄 **Collect user feedback** - Identify priority improvements

### Next Development Phase (If Needed)
**Phase 3: Advanced Formatting**
- Implement bold/italic detection using font weight analysis
- Add serif vs sans-serif font detection
- Improve paragraph spacing and line grouping
- Add underline/strikethrough support

**Phase 4: Image Handling**
- Detect image regions in documents
- Extract embedded images from PDFs
- Position images in Word output
- Maintain image quality

### Future Enhancements
- Create standalone .exe with PyInstaller
- Add drag-and-drop file import
- Implement preview pane
- Add settings persistence
- Create help documentation

---

**User Requirements (Confirmed Nov 3, 2025):**
1. **Document sizes**: Typically 1-10 pages per document
2. **PDF sources**: 
   - Primary: FamilySearch.org
   - Secondary: Ancestry.com (handle eventually, not initially critical)
3. **Output naming**: `original_filename.docx` with option to rename
4. **Priorities**: 
   - Layout matching (HIGH) - ✅ Basic implementation complete
   - Color accuracy (HIGH) - ✅ COMPLETE with k-means clustering
   - Speed (LOW) - ✅ Progress indicators implemented
5. **Deployment**: Must be standalone executable with embedded OCR engine (like Recipe Scanner) - 📅 Future phase

**Progress Indicators (Implemented):**
- ✅ Visual progress bar
- ✅ Current file being processed displayed
- ✅ Status updates in status bar
- ✅ Background threading keeps UI responsive

**Standalone Executable Requirements (Future):**
- Bundle Tesseract OCR engine (already bundled ✅)
- Bundle Poppler (already bundled ✅)
- Include all dependencies (all installed ✅)
- No external installations required
- PyInstaller for .exe creation (Phase 6)

---
Created: November 3, 2025
Updated: November 3, 2025 - 4:45 PM
Status: **Phases 1-2 Complete - Ready for Testing**

**Last Updated**: Tesseract and Poppler bundled, all dependencies installed and verified working
