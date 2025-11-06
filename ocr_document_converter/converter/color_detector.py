"""
Color Detector Module
Detects text colors from images for preservation in Word documents

Phase 2 Implementation - November 3, 2025
"""

import cv2
import numpy as np
from PIL import Image
import logging
from pathlib import Path
from collections import Counter


class ColorDetector:
    """Detect and analyze text colors in images"""
    
    def __init__(self):
        """Initialize color detector"""
        # Common color definitions (RGB)
        self.color_map = {
            'black': (0, 0, 0),
            'dark_gray': (64, 64, 64),
            'gray': (128, 128, 128),
            'light_gray': (192, 192, 192),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'dark_red': (139, 0, 0),
            'blue': (0, 0, 255),
            'dark_blue': (0, 0, 139),
            'navy': (0, 0, 128),
            'green': (0, 128, 0),
            'dark_green': (0, 100, 0),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'brown': (139, 69, 19),
            'pink': (255, 192, 203),
        }
    
    def detect_text_color(self, image_path, text_box):
        """
        Detect the color of text in a bounding box
        
        Args:
            image_path: Path to image file
            text_box: Dictionary with 'left', 'top', 'width', 'height' keys
            
        Returns:
            tuple: RGB color (R, G, B) values 0-255
        """
        try:
            # Load image
            img = cv2.imread(str(image_path))
            if img is None:
                logging.warning(f"Could not load image: {image_path}")
                return (0, 0, 0)  # Default to black
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Extract region of interest
            x = max(0, text_box['left'])
            y = max(0, text_box['top'])
            w = text_box['width']
            h = text_box['height']
            
            # Ensure bounds are within image
            x2 = min(x + w, img_rgb.shape[1])
            y2 = min(y + h, img_rgb.shape[0])
            
            if x >= x2 or y >= y2:
                return (0, 0, 0)
            
            roi = img_rgb[y:y2, x:x2]
            
            if roi.size == 0:
                return (0, 0, 0)
            
            # Get dominant text color
            color = self.get_dominant_text_color(roi)
            
            return color
            
        except Exception as e:
            logging.error(f"Error detecting text color: {e}")
            return (0, 0, 0)
    
    def get_dominant_text_color(self, roi):
        """
        Get the dominant text color from a region of interest
        Uses k-means clustering to find dominant colors,
        then selects the darkest one (likely to be text)
        
        Args:
            roi: Image region (numpy array)
            
        Returns:
            tuple: RGB color (R, G, B)
        """
        try:
            # Reshape image to list of pixels
            pixels = roi.reshape(-1, 3)
            
            # Remove very light pixels (likely background)
            # Text is usually darker than background
            brightness = np.mean(pixels, axis=1)
            dark_pixels = pixels[brightness < 200]
            
            if len(dark_pixels) < 10:
                # Fallback to all pixels if too few dark ones
                dark_pixels = pixels
            
            # Use k-means to find dominant colors
            from sklearn.cluster import KMeans
            
            n_clusters = min(3, len(np.unique(dark_pixels, axis=0)))
            if n_clusters < 1:
                return (0, 0, 0)
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            kmeans.fit(dark_pixels)
            
            # Get cluster centers (dominant colors)
            colors = kmeans.cluster_centers_
            
            # Count pixels in each cluster
            labels = kmeans.labels_
            label_counts = Counter(labels)
            
            # Find the most common dark color
            # Sort by count, then by darkness
            color_info = []
            for i, color in enumerate(colors):
                count = label_counts[i]
                brightness = np.mean(color)
                color_info.append((color, count, brightness))
            
            # Sort by count (descending), then by brightness (ascending = darker first)
            color_info.sort(key=lambda x: (-x[1], x[2]))
            
            # Return the most common color
            best_color = color_info[0][0]
            
            return tuple(int(c) for c in best_color)
            
        except Exception as e:
            logging.error(f"Error getting dominant color: {e}")
            # Simple fallback - median color
            try:
                median_color = np.median(roi.reshape(-1, 3), axis=0)
                return tuple(int(c) for c in median_color)
            except:
                return (0, 0, 0)
    
    def get_dominant_color(self, image_region):
        """
        Get the dominant color from an image region
        
        Args:
            image_region: PIL Image or numpy array
            
        Returns:
            tuple: RGB color (R, G, B)
        """
        try:
            # Convert to numpy array if PIL Image
            if isinstance(image_region, Image.Image):
                image_region = np.array(image_region)
            
            return self.get_dominant_text_color(image_region)
            
        except Exception as e:
            logging.error(f"Error getting dominant color: {e}")
            return (0, 0, 0)
    
    def classify_color(self, rgb_color):
        """
        Classify RGB color into common color names
        
        Args:
            rgb_color: Tuple of (R, G, B)
            
        Returns:
            str: Color name (e.g., 'black', 'red', 'blue')
        """
        r, g, b = rgb_color
        
        # Calculate distances to known colors
        min_distance = float('inf')
        closest_color = 'black'
        
        for color_name, color_rgb in self.color_map.items():
            # Euclidean distance in RGB space
            distance = np.sqrt(
                (r - color_rgb[0])**2 +
                (g - color_rgb[1])**2 +
                (b - color_rgb[2])**2
            )
            
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        
        return closest_color
    
    def is_similar_color(self, color1, color2, threshold=30):
        """
        Check if two colors are similar
        
        Args:
            color1: RGB tuple
            color2: RGB tuple
            threshold: Maximum distance to consider similar
            
        Returns:
            bool: True if colors are similar
        """
        distance = np.sqrt(
            (color1[0] - color2[0])**2 +
            (color1[1] - color2[1])**2 +
            (color1[2] - color2[2])**2
        )
        return distance < threshold
    
    def detect_colors_in_document(self, image_path, word_boxes, progress_callback=None):
        """
        Detect colors for all text boxes in a document
        
        Args:
            image_path: Path to image file
            word_boxes: List of word bounding boxes from OCR
            progress_callback: Optional callback for progress updates
            
        Returns:
            list: List of tuples (word_text, rgb_color)
        """
        results = []
        total = len(word_boxes)
        
        try:
            # Load image once
            img = cv2.imread(str(image_path))
            if img is None:
                return results
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            for idx, box in enumerate(word_boxes):
                # Progress update
                if progress_callback and idx % 10 == 0:
                    progress_callback(f"Detecting colors... {idx}/{total}")
                
                # Extract text color
                color = self.detect_text_color_from_array(img_rgb, box)
                results.append((box.get('text', ''), color))
            
            if progress_callback:
                progress_callback(f"Color detection complete - {total} words")
            
            logging.info(f"Detected colors for {len(results)} words")
            return results
            
        except Exception as e:
            logging.error(f"Error detecting colors in document: {e}")
            return results
    
    def detect_text_color_from_array(self, img_array, text_box):
        """
        Detect text color from pre-loaded image array
        
        Args:
            img_array: Numpy array (RGB)
            text_box: Dictionary with 'left', 'top', 'width', 'height'
            
        Returns:
            tuple: RGB color
        """
        try:
            x = max(0, text_box.get('left', 0))
            y = max(0, text_box.get('top', 0))
            w = text_box.get('width', 0)
            h = text_box.get('height', 0)
            
            x2 = min(x + w, img_array.shape[1])
            y2 = min(y + h, img_array.shape[0])
            
            if x >= x2 or y >= y2:
                return (0, 0, 0)
            
            roi = img_array[y:y2, x:x2]
            
            if roi.size == 0:
                return (0, 0, 0)
            
            return self.get_dominant_text_color(roi)
            
        except Exception as e:
            logging.error(f"Error detecting color from array: {e}")
            return (0, 0, 0)
    
    def simplify_color_palette(self, colors, max_colors=10):
        """
        Simplify a list of colors to a smaller palette
        Useful for reducing similar colors
        
        Args:
            colors: List of RGB tuples
            max_colors: Maximum number of distinct colors
            
        Returns:
            dict: Mapping from original colors to simplified colors
        """
        try:
            if len(colors) <= max_colors:
                return {c: c for c in colors}
            
            # Use k-means to cluster similar colors
            from sklearn.cluster import KMeans
            
            colors_array = np.array(colors)
            kmeans = KMeans(n_clusters=max_colors, random_state=42, n_init=10)
            kmeans.fit(colors_array)
            
            # Map each original color to its cluster center
            mapping = {}
            for i, color in enumerate(colors):
                cluster_center = kmeans.cluster_centers_[kmeans.labels_[i]]
                simplified = tuple(int(c) for c in cluster_center)
                mapping[tuple(color)] = simplified
            
            return mapping
            
        except Exception as e:
            logging.error(f"Error simplifying palette: {e}")
            return {c: c for c in colors}


__all__ = ['ColorDetector']
