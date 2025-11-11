"""
OCR Engine for Recipe Scanner Pro
Extracts text from scanned recipe images using Tesseract OCR
"""

from pathlib import Path
from typing import Optional, Dict, List
import re
import os

# Import PIL components first
try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available")

# Try to import Tesseract
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not available. OCR functionality will be limited.")


class OCREngine:
    """Engine for extracting text from images using Tesseract OCR"""
    
    def __init__(self, tesseract_cmd: str = None):
        """
        Initialize OCR engine
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional)
                          If None, will try to find automatically
        """
        self.tesseract_available = TESSERACT_AVAILABLE
        
        # Set Tesseract path - prioritize bundled version
        if self.tesseract_available:
            if tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            else:
                # Try bundled version first (for portability)
                bundled_path = Path(__file__).parent.parent / "tesseract" / "tesseract.exe"
                if bundled_path.exists():
                    pytesseract.pytesseract.tesseract_cmd = str(bundled_path)
                    # Set TESSDATA_PREFIX for bundled version
                    os.environ['TESSDATA_PREFIX'] = str(bundled_path.parent / "tessdata")
                    print(f"OCR: Using bundled Tesseract at {bundled_path}")
                else:
                    # Fall back to default Windows installation path
                    default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                    try:
                        if Path(default_path).exists():
                            pytesseract.pytesseract.tesseract_cmd = default_path
                            print(f"OCR: Tesseract found at {default_path}")
                    except:
                        pass
    
    def is_available(self) -> bool:
        """Check if OCR is available"""
        if not self.tesseract_available or not PIL_AVAILABLE:
            return False
        
        try:
            # Test if tesseract is actually working
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            print(f"Tesseract not properly configured: {e}")
            return False
    
    def extract_text(self, image_path: str, preprocess: bool = True, 
                     lang: str = 'eng') -> str:
        """
        Extract text from image
        
        Args:
            image_path: Path to image file
            preprocess: Apply image preprocessing for better results
            lang: Language for OCR (default: 'eng' for English)
        
        Returns:
            Extracted text
        """
        if not self.is_available():
            return ""
        
        try:
            # Load image
            img = Image.open(image_path)
            
            # Preprocess if requested
            if preprocess:
                img = self._preprocess_image(img)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(img, lang=lang)
            
            return text.strip()
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def extract_text_with_confidence(self, image_path: str, 
                                    preprocess: bool = True) -> Dict:
        """
        Extract text with confidence scores
        
        Returns:
            Dictionary with 'text' and 'confidence' keys
        """
        if not self.is_available():
            return {'text': '', 'confidence': 0}
        
        try:
            img = Image.open(image_path)
            
            if preprocess:
                img = self._preprocess_image(img)
            
            # Get detailed data
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            # Extract text and calculate average confidence
            texts = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if conf > 0:  # Only include recognized text
                    text = data['text'][i].strip()
                    if text:
                        texts.append(text)
                        confidences.append(int(conf))
            
            full_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': full_text,
                'confidence': avg_confidence
            }
            
        except Exception as e:
            print(f"Error extracting text with confidence: {e}")
            return {'text': '', 'confidence': 0}
    
    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results
        Enhanced to handle difficult images (low quality JPGs, poor lighting, etc.)
        
        Args:
            img: PIL Image object
        
        Returns:
            Preprocessed image
        """
        try:
            print(f"DEBUG OCR: Original image size: {img.size}, mode: {img.mode}")
            
            # Convert to RGB if needed
            if img.mode not in ('RGB', 'L'):
                print(f"DEBUG OCR: Converting from {img.mode} to RGB")
                img = img.convert('RGB')
            
            # Resize if too small or too large (improves OCR)
            width, height = img.size
            
            # If image is very small, scale it up significantly
            if width < 1500 or height < 1500:
                target_width = 2000
                scale = target_width / width
                new_size = (int(width * scale), int(height * scale))
                print(f"DEBUG OCR: Upscaling image from {img.size} to {new_size}")
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # If image is huge, scale it down
            elif width > 4000 or height > 4000:
                target_width = 3000
                scale = target_width / width
                new_size = (int(width * scale), int(height * scale))
                print(f"DEBUG OCR: Downscaling image from {img.size} to {new_size}")
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to grayscale first for better processing
            print(f"DEBUG OCR: Converting to grayscale")
            img = img.convert('L')
            
            # Apply aggressive contrast enhancement
            print(f"DEBUG OCR: Enhancing contrast")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # Increased from 1.5
            
            # Apply brightness adjustment if image is too dark
            print(f"DEBUG OCR: Adjusting brightness")
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)
            
            # Apply strong sharpening
            print(f"DEBUG OCR: Sharpening image")
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.5)  # Increased from 2.0
            
            # Auto-contrast to normalize levels
            print(f"DEBUG OCR: Applying auto-contrast")
            img = ImageOps.autocontrast(img, cutoff=2)
            
            # Apply adaptive thresholding for text extraction
            # This helps separate text from background
            print(f"DEBUG OCR: Applying threshold")
            from PIL import ImageFilter
            img = img.filter(ImageFilter.SHARPEN)
            
            # Try to binarize the image (black text on white background)
            threshold = 128
            img = img.point(lambda x: 255 if x > threshold else 0)
            
            print(f"DEBUG OCR: Final preprocessed image size: {img.size}, mode: {img.mode}")
            
            # Save preprocessed image for debugging
            debug_path = Path(self.tesseract_available and pytesseract.pytesseract.tesseract_cmd).parent.parent / "data" / "last_preprocessed.png" if hasattr(self, 'tesseract_available') else Path("last_preprocessed.png")
            try:
                img.save(debug_path)
                print(f"DEBUG OCR: Saved preprocessed image to {debug_path}")
            except:
                pass
            
            return img
            
        except Exception as e:
            print(f"ERROR preprocessing image: {e}")
            import traceback
            traceback.print_exc()
            return img
    
    def extract_structured_data(self, text: str) -> Dict:
        """
        Extract structured recipe data from raw text
        Handles both line-by-line and continuous paragraph formats
        
        Args:
            text: Raw OCR text
        
        Returns:
            Dictionary with recipe components
        """
        result = {
            'title': '',
            'ingredients': [],
            'instructions': [],
            'variations': '',
            'notes': '',
            'servings': '',
            'prep_time': '',
            'cook_time': '',
            'raw_text': text
        }
        
        if not text:
            return result
        
        # First, try to find section markers in the continuous text
        text_lower = text.lower()
        
        # Find section positions
        ingredients_pos = -1
        directions_pos = -1
        variations_pos = -1
        notes_pos = -1
        
        # Look for "Ingredients" or "Ingredients:"
        for pattern in ['ingredients:', 'ingredients']:
            pos = text_lower.find(pattern)
            if pos != -1:
                ingredients_pos = pos + len(pattern)
                print(f"DEBUG OCR: Found 'Ingredients' at position {pos}")
                break
        
        # Look for "Directions" or "Directions:"
        for pattern in ['directions:', 'directions', 'instructions:', 'instructions']:
            pos = text_lower.find(pattern)
            if pos != -1:
                directions_pos = pos + len(pattern)
                print(f"DEBUG OCR: Found directions at position {pos}")
                break
        
        # Look for "Variations" or "Variations:"
        for pattern in ['variations:', 'variations', 'variation:', 'variation']:
            pos = text_lower.find(pattern)
            if pos != -1:
                variations_pos = pos + len(pattern)
                print(f"DEBUG OCR: Found 'Variations' at position {pos}")
                break
        
        # Look for "Notes" or "Notes:"
        for pattern in ['notes:', 'notes', 'cook\'s note:', 'cook\'s notes:', 'tips:']:
            pos = text_lower.find(pattern)
            if pos != -1:
                notes_pos = pos + len(pattern)
                print(f"DEBUG OCR: Found 'Notes' at position {pos}")
                break
        
        # Extract title - look for first line or text before ingredients
        title_text = text[:ingredients_pos if ingredients_pos > 0 else 200].strip()
        
        print(f"DEBUG OCR: Title search area (first 200 chars): '{title_text[:200]}'")
        
        # Split by lines and take the first substantial line as title
        title_lines = [line.strip() for line in title_text.split('\n') if line.strip()]
        print(f"DEBUG OCR: Found {len(title_lines)} non-empty lines in title area")
        
        if title_lines:
            # Use the first line that's not too short and doesn't look like metadata
            for i, line in enumerate(title_lines):
                line_clean = line.replace('—', '').replace('–', '').strip()
                print(f"DEBUG OCR: Checking line {i+1}: '{line_clean[:100]}...' (length: {len(line_clean)})")
                if (len(line_clean) > 5 and 
                    not line_clean.lower().startswith(('prep:', 'cook:', 'yield:', 'total:', 'servings:')) and
                    'ingredient' not in line_clean.lower()):
                    result['title'] = line_clean
                    print(f"DEBUG OCR: Selected title from line {i+1}: '{line_clean}'")
                    break
        
        # If no title found yet, try everything before common markers
        if not result['title']:
            print("DEBUG OCR: No title found in first pass, trying marker-based search")
            title_end = len(text)
            for marker in ['TOTAL TIME:', 'YIELD:', 'Prep:', 'PREP TIME:', 'ingredients']:
                pos = text.lower().find(marker.lower())
                if pos > 0 and pos < title_end:
                    title_end = pos
                    print(f"DEBUG OCR: Found marker '{marker}' at position {pos}")
            
            potential_title = text[:title_end].strip().split('\n')[0].strip()
            potential_title = potential_title.replace('—', '').replace('–', '').strip()
            print(f"DEBUG OCR: Potential title from markers: '{potential_title[:100]}...' (length: {len(potential_title)})")
            if len(potential_title) < 100 and len(potential_title) > 5:
                result['title'] = potential_title
                print(f"DEBUG OCR: Accepted marker-based title")
        
        # FALLBACK: If still no title, use the very first line of text
        # This handles recipes where the title is at the top but no other markers are found
        if not result['title']:
            print("DEBUG OCR: No title found yet, using first line fallback")
            all_lines = [line.strip() for line in text.split('\n') if line.strip()]
            print(f"DEBUG OCR: Total non-empty lines in document: {len(all_lines)}")
            if all_lines:
                first_line = all_lines[0].replace('—', '').replace('–', '').strip()
                print(f"DEBUG OCR: First line of document: '{first_line[:100]}...' (length: {len(first_line)})")
                
                # If the first line is too long (continuous text block), extract just the beginning
                if len(first_line) > 100:
                    print("DEBUG OCR: First line is too long, extracting title from beginning")
                    # Try to find title at the very start - look for common patterns
                    # Title usually ends at first sentence, "Author:", "{", or descriptive text
                    title_end_markers = [' {', ' Author:', ' Make this', ' This ', ' A ', ' The ']
                    best_end = len(first_line)
                    for marker in title_end_markers:
                        pos = first_line.find(marker)
                        if pos > 0 and pos < best_end:
                            best_end = pos
                            print(f"DEBUG OCR: Found title end marker '{marker}' at position {pos}")
                    
                    # Extract up to the marker
                    extracted_title = first_line[:best_end].strip()
                    
                    # Also limit by word count - titles are usually 2-10 words
                    words = extracted_title.split()
                    if len(words) > 12:
                        extracted_title = ' '.join(words[:12])
                        print(f"DEBUG OCR: Title too many words, truncated to first 12 words")
                    
                    if 3 <= len(extracted_title) <= 100:
                        result['title'] = extracted_title
                        print(f"DEBUG OCR: Extracted title from long line: '{extracted_title}'")
                    else:
                        print(f"DEBUG OCR: Extracted title rejected (length {len(extracted_title)} outside 3-100 range)")
                elif 3 <= len(first_line) <= 100:
                    result['title'] = first_line
                    print(f"DEBUG OCR: Using first line as fallback title: '{first_line}'")
                else:
                    print(f"DEBUG OCR: First line rejected (length {len(first_line)} outside 3-100 range)")
        
        if result['title']:
            print(f"DEBUG OCR: ✓ Final title selected: '{result['title']}'")
        else:
            print(f"DEBUG OCR: ✗ No title found in document!")
        
        # Find servings (YIELD:)
        yield_match = re.search(r'YIELD:\s*(\d+)\s*servings?', text, re.IGNORECASE)
        if yield_match:
            result['servings'] = yield_match.group(1)
        
        # Find times
        prep_match = re.search(r'Prep:\s*(\d+\s*min)', text, re.IGNORECASE)
        if prep_match:
            result['prep_time'] = prep_match.group(1)
        
        cook_match = re.search(r'Cook:\s*(\d+\s*min)', text, re.IGNORECASE)
        if cook_match:
            result['cook_time'] = cook_match.group(1)
        
        # Extract ingredients section
        if ingredients_pos > 0 and directions_pos > 0:
            ingredients_text = text[ingredients_pos:directions_pos].strip()
            print(f"DEBUG OCR: Ingredients text length: {len(ingredients_text)} chars")
            print(f"DEBUG OCR: Ingredients text preview: '{ingredients_text[:150]}...'")
            
            # IMPROVED: First check if bullet points exist in the text
            has_bullets = bool(re.search(r'[•◦▪▫○●]', ingredients_text))
            print(f"DEBUG OCR: Bullet points detected: {has_bullets}")
            
            # Try multiple extraction methods in order of reliability
            extraction_methods = []
            
            # Method 1: Split by bullet points (if present)
            if has_bullets:
                print("DEBUG OCR: Method 1 - Bullet point extraction")
                bullet_parts = re.split(r'[•◦▪▫○●]', ingredients_text)
                temp_ingredients = []
                for part in bullet_parts:
                    part = part.strip().lstrip('—-* ')
                    # Clean up any remaining bullet artifacts
                    part = re.sub(r'^[\s\-•◦▪▫○●]+', '', part).strip()
                    if 3 < len(part) < 250 and not part.lower().startswith(('direction', 'instruction', 'preparation')):
                        temp_ingredients.append(part)
                if temp_ingredients:
                    extraction_methods.append(('bullet_points', temp_ingredients))
                    print(f"DEBUG OCR: Bullet extraction found {len(temp_ingredients)} ingredients")
            
            # Method 2: Split by newlines
            print("DEBUG OCR: Method 2 - Newline extraction")
            lines = ingredients_text.split('\n')
            valid_lines = []
            for line in lines:
                line = line.strip()
                # Remove leading bullets, dashes, or numbers
                line = re.sub(r'^[—\-•◦▪▫○●*\d]+\.?\s*', '', line).strip()
                # Skip empty lines and section headers
                if (len(line) > 3 and 
                    not line.lower().startswith(('direction', 'instruction', 'preparation', 'method')) and
                    'ingredient' not in line.lower()):
                    if line:
                        valid_lines.append(line)
            if valid_lines:
                extraction_methods.append(('newlines', valid_lines))
                print(f"DEBUG OCR: Newline extraction found {len(valid_lines)} ingredients")
            
            # Method 3: Pattern-based splitting (measurements)
            print("DEBUG OCR: Method 3 - Pattern-based extraction")
            ingredient_pattern = r'(?:^|\s)(\d+(?:/\d+)?(?:\s*-\s*\d+(?:/\d+)?)?\s+(?:cups?|tablespoons?|tbsp?|teaspoons?|tsp?|ounces?|oz|pounds?|lbs?|grams?|g|milliliters?|ml|liters?|l|large|medium|small|whole|cloves?|pinch(?:es)?|cans?|packages?|lbs?))'
            parts = re.split(ingredient_pattern, ingredients_text, flags=re.IGNORECASE)
            pattern_ingredients = []
            for i in range(1, len(parts), 2):
                if i < len(parts):
                    ingredient = parts[i]
                    if i + 1 < len(parts):
                        ingredient += parts[i + 1]
                    ingredient = ingredient.strip().lstrip('—-•◦▪▫○●* ').strip()
                    next_measure = re.search(ingredient_pattern, ingredient[10:], re.IGNORECASE)
                    if next_measure:
                        ingredient = ingredient[:10 + next_measure.start()].strip()
                    if 5 < len(ingredient) < 250:
                        pattern_ingredients.append(ingredient)
            if pattern_ingredients:
                extraction_methods.append(('patterns', pattern_ingredients))
                print(f"DEBUG OCR: Pattern extraction found {len(pattern_ingredients)} ingredients")
            
            # Method 4: Smart splitting by measurement detection (IMPROVED)
            # This handles cases where ingredients run together in a paragraph
            print("DEBUG OCR: Method 4 - Smart measurement detection")
            # Match patterns like: "1 cup flour 2 tbsp sugar 3 eggs"
            measurement_starts = list(re.finditer(r'\b(\d+(?:/\d+)?(?:\s*-\s*\d+(?:/\d+)?)?\s+(?:cups?|tablespoons?|tbsp?|teaspoons?|tsp?|ounces?|oz|pounds?|lbs?|grams?|g|milliliters?|ml|liters?|l|large|medium|small|whole|cloves?|pinch(?:es)?|cans?|packages?|lbs?))', ingredients_text, re.IGNORECASE))
            smart_ingredients = []
            for idx, match in enumerate(measurement_starts):
                start = match.start()
                # Find end: either next measurement or end of text
                if idx + 1 < len(measurement_starts):
                    end = measurement_starts[idx + 1].start()
                else:
                    end = len(ingredients_text)
                ingredient = ingredients_text[start:end].strip()
                # Clean up
                ingredient = re.sub(r'^[—\-•◦▪▫○●*]+', '', ingredient).strip()
                if 5 < len(ingredient) < 250:
                    smart_ingredients.append(ingredient)
            if smart_ingredients:
                extraction_methods.append(('smart_measurement', smart_ingredients))
                print(f"DEBUG OCR: Smart measurement detection found {len(smart_ingredients)} ingredients")
            
            # Choose the best extraction method
            # Prefer bullet points if detected, then newlines, then patterns
            if extraction_methods:
                # Score each method: bullet points = 3, newlines = 2, others = 1
                scored_methods = []
                for method_name, ingredients in extraction_methods:
                    score = len(ingredients)
                    if method_name == 'bullet_points':
                        score *= 3  # Highest priority
                    elif method_name == 'newlines':
                        score *= 2  # Second priority
                    scored_methods.append((score, method_name, ingredients))
                
                # Sort by score and pick the best
                scored_methods.sort(reverse=True, key=lambda x: x[0])
                best_method = scored_methods[0]
                result['ingredients'] = best_method[2]
                print(f"DEBUG OCR: Selected method '{best_method[1]}' with {len(best_method[2])} ingredients (score: {best_method[0]})")
            else:
                print("DEBUG OCR: No extraction methods succeeded")
            
            # Final fallback: just split by periods or semicolons if we still have nothing
            if not result['ingredients'] and len(ingredients_text) > 10:
                print("DEBUG OCR: Final fallback - splitting by punctuation")
                fallback_parts = re.split(r'[.;]', ingredients_text)
                for part in fallback_parts:
                    part = part.strip().lstrip('—-•◦▪▫○●* ')
                    if 5 < len(part) < 250:
                        result['ingredients'].append(part)
                print(f"DEBUG OCR: Fallback found {len(result['ingredients'])} ingredients")
            
            # CLEANUP: Remove bullet points and filter out unwanted words
            if result['ingredients']:
                cleaned_ingredients = []
                for ingredient in result['ingredients']:
                    # Remove all bullet point characters from the ingredient text
                    ingredient = re.sub(r'[•◦▪▫○●]', '', ingredient).strip()
                    # Remove any leading/trailing dashes, asterisks, etc.
                    ingredient = ingredient.strip('—-•◦▪▫○●* ').strip()
                    # Skip if the ingredient is just the word "ingredients" or "ingredient"
                    if ingredient.lower() not in ['ingredient', 'ingredients']:
                        # Skip if it's too short or empty after cleaning
                        if len(ingredient) > 2:
                            cleaned_ingredients.append(ingredient)
                
                result['ingredients'] = cleaned_ingredients
                print(f"DEBUG OCR: After cleanup: {len(result['ingredients'])} ingredients remain")
        
        # Extract directions section
        if directions_pos > 0:
            # Find the end of directions (start of variations or notes, or end of text)
            directions_end = len(text)
            if variations_pos > directions_pos:
                directions_end = variations_pos - 10  # Subtract length of "variations:" marker
            elif notes_pos > directions_pos:
                directions_end = notes_pos - 6  # Subtract length of "notes:" marker
            
            directions_text = text[directions_pos:directions_end].strip()
            print(f"DEBUG OCR: Directions text length: {len(directions_text)} chars")
            print(f"DEBUG OCR: Directions text preview: '{directions_text[:150]}...'")
            
            # Split by numbered steps
            steps = re.split(r'(?=\d+\.\s+)', directions_text)
            for step in steps:
                step = step.strip()
                if len(step) > 10 and not step.lower().startswith(('ingredient', 'yield', 'prep', 'cook', 'variation', 'note')):
                    # Clean up step
                    step = re.sub(r'^\d+\.\s*', '', step)  # Remove step number
                    step = step.strip()
                    if step:
                        result['instructions'].append(step)
            
            print(f"DEBUG OCR: Numbered step extraction found {len(result['instructions'])} steps")
            
            # If no numbered steps found, try splitting by sentences or paragraphs
            if not result['instructions']:
                print("DEBUG OCR: No numbered steps, trying sentence-based extraction")
                # Split by periods followed by capital letters (new sentences)
                sentences = re.split(r'\.\s+(?=[A-Z])', directions_text)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 15 and not sentence.lower().startswith(('ingredient', 'yield', 'prep', 'cook')):
                        # Add back the period if it was removed
                        if not sentence.endswith('.'):
                            sentence += '.'
                        result['instructions'].append(sentence)
                print(f"DEBUG OCR: Sentence extraction found {len(result['instructions'])} instructions")
        
        # Extract variations section
        if variations_pos > 0:
            variations_end = len(text)
            if notes_pos > variations_pos:
                variations_end = notes_pos - 6  # Subtract length of "notes:" marker
            
            variations_text = text[variations_pos:variations_end].strip()
            result['variations'] = variations_text
        
        # Extract notes section
        if notes_pos > 0:
            notes_text = text[notes_pos:].strip()
            result['notes'] = notes_text
        
        print(f"DEBUG OCR: Extracted {len(result['ingredients'])} ingredients, {len(result['instructions'])} instructions")
        if result['variations']:
            print(f"DEBUG OCR: Found variations section")
        if result['notes']:
            print(f"DEBUG OCR: Found notes section")
        
        return result
    
    def save_text(self, text: str, output_path: str):
        """Save extracted text to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(f"Error saving text: {e}")
    
    def get_tesseract_version(self) -> str:
        """Get Tesseract version"""
        if not self.is_available():
            return "Not available"
        
        try:
            return pytesseract.get_tesseract_version().strftime("%Y%m%d")
        except:
            return "Unknown"


def quick_extract(image_path: str, preprocess: bool = True) -> str:
    """
    Quick text extraction utility function
    
    Args:
        image_path: Path to image
        preprocess: Apply preprocessing
    
    Returns:
        Extracted text
    """
    ocr = OCREngine()
    if not ocr.is_available():
        return ""
    
    return ocr.extract_text(image_path, preprocess=preprocess)
