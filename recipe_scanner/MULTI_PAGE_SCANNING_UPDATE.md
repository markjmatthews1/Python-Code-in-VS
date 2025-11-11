# Multi-Page Scanning Enhancement

## Date: November 9, 2025

## Overview
Enhanced the Recipe Scanner app to automatically detect and handle multiple pages from the document feeder when scanning recipes.

## Changes Made

### 1. Scanner Interface (`scanner_interface.py`)

#### Updated `scan_with_dialog()` method:
- **Now returns**: `List[str]` instead of `Optional[str]`
- **Behavior**: 
  - Automatically detects multiple pages in document feeder
  - Scans all available pages in one operation
  - Each page saved with sequential numbering: `recipe_scan_TIMESTAMP_page1.png`, `_page2.png`, etc.
  - Returns list of all scanned image paths
  - Safety limit of 50 pages to prevent infinite loops

#### New `scan_multiple_pages()` method:
- Dedicated method for programmatic multi-page scanning
- Doesn't show dialog - uses specified settings
- Scans all pages from feeder until empty
- Parameters: `color_mode`, `resolution`
- Returns list of scanned page paths

#### New `combine_pages_to_single_image()` method:
- Combines multiple page images into single vertical image
- Useful for creating consolidated view of multi-page recipes
- Maintains image quality
- Auto-generates output filename with timestamp

### 2. Main Application (`app.py`)

#### Updated `scan_image()` method:
- Handles both single-page and multi-page scanning
- Detects number of pages returned
- Shows appropriate messages:
  - Single page: "Recipe scanned successfully!"
  - Multiple pages: "X pages scanned successfully from document feeder!"
- Properly populates `self.scanned_pages` list

#### Updated `scan_next_page()` method:
- Now handles multiple pages if document feeder used
- Updates total page count correctly
- Shows appropriate feedback for single vs. multiple additional pages

#### `process_scanned_image()` - Already Compatible:
- Already had logic to process multiple pages
- Combines text from all pages with `=== PAGE BREAK ===` marker
- Shows average confidence across all pages
- No changes needed - works perfectly with new multi-page scanning

## User Experience

### Single Page Scan:
1. User clicks "Scan Recipe"
2. Scanner dialog opens
3. User scans one page
4. App receives 1 page, processes normally
5. "Recipe scanned successfully!" message

### Multi-Page Scan (Document Feeder):
1. User clicks "Scan Recipe"
2. Scanner dialog opens
3. User places multiple pages in document feeder
4. User starts scan
5. App automatically detects and scans all pages
6. Each page saved with sequential numbering
7. "X pages scanned successfully from document feeder!" message
8. User can process all pages with OCR in one click

### OCR Processing:
- Single or multiple pages processed seamlessly
- Text extracted from each page
- Combined with page break markers
- Recipe structured data extracted from combined text
- Average OCR confidence shown across all pages

## Technical Details

### Page Detection:
- Uses Windows WIA (Windows Image Acquisition) API
- After initial scan dialog, attempts to transfer additional images
- Continues until `Transfer()` fails (no more pages)
- Each page saved immediately to prevent memory issues

### File Naming Convention:
```
recipe_scan_20251109_143052_page1.png
recipe_scan_20251109_143052_page2.png
recipe_scan_20251109_143052_page3.png
```
- Same base timestamp for all pages in one scan
- Sequential page numbers
- Easy to identify which pages belong together

### Safety Features:
- Maximum 50 pages per scan (prevents infinite loops)
- Each page saved immediately (prevents memory overflow)
- Graceful error handling if feeder jams or empties
- Debug output shows page count and file paths

## Backward Compatibility

### Return Type Change:
- `scan_with_dialog()` now returns `List[str]` instead of `Optional[str]`
- Single page scan returns list with one item: `['path.png']`
- Multi-page scan returns list: `['page1.png', 'page2.png', ...]`
- Existing code updated to handle list return type

### No Breaking Changes:
- All existing scan workflows continue to work
- Single page scanning works exactly as before
- Additional functionality added, nothing removed

## Future Enhancements (Optional)

1. **Manual Page Ordering**: Allow user to reorder pages before OCR
2. **Page Preview Grid**: Show thumbnails of all scanned pages
3. **Delete Individual Pages**: Remove specific pages from multi-page scan
4. **Auto-Combine Option**: Setting to automatically combine pages into single image
5. **Page Rotation**: Detect and auto-rotate pages if scanned upside-down
6. **Duplex Scanning**: Support for double-sided document scanning

## Testing Recommendations

1. Test single page scan (flatbed)
2. Test multi-page scan (document feeder with 2-3 pages)
3. Test OCR on multi-page scans
4. Test "Scan Next Page" button with both flatbed and feeder
5. Verify file naming is sequential
6. Check that all pages are processed by OCR
7. Verify page break markers in combined text

## Notes

- Requires Windows with WIA support
- Document feeder must be supported by scanner hardware
- If scanner doesn't have feeder, works normally as single-page scan
- Error messages are informative if feeder is empty or jams
