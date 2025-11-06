"""
Ingredient Matcher for Recipe Scanner Pro
Finds recipes based on available ingredients
"""

from typing import List, Dict, Set
import re
from difflib import SequenceMatcher


class IngredientMatcher:
    """Matches recipes based on available ingredients"""
    
    def __init__(self, database_manager):
        """
        Initialize matcher with database connection
        
        Args:
            database_manager: DatabaseManager instance
        """
        self.db = database_manager
    
    def find_matching_recipes(self, available_ingredients: List[str], 
                             match_threshold: float = 0.5) -> List[Dict]:
        """
        Find recipes that can be made with available ingredients
        
        Args:
            available_ingredients: List of ingredients you have
            match_threshold: Minimum match percentage (0.0-1.0)
        
        Returns:
            List of recipe dictionaries with match info
        """
        if not available_ingredients:
            return []
        
        # Normalize ingredient names
        normalized_available = [self._normalize_ingredient(ing) 
                               for ing in available_ingredients]
        
        # Get all recipes
        all_recipes = self.db.get_all_recipes()
        
        matching_recipes = []
        
        for recipe in all_recipes:
            recipe_id = recipe['id']
            
            # Get recipe ingredients
            recipe_ingredients = self.db.get_ingredients(recipe_id)
            
            if not recipe_ingredients:
                continue
            
            # Calculate match
            match_info = self._calculate_match(
                normalized_available,
                recipe_ingredients
            )
            
            match_percentage = match_info['match_percentage']
            
            # Only include if meets threshold
            if match_percentage >= match_threshold:
                recipe['match_percentage'] = match_percentage
                recipe['matching_ingredients'] = match_info['matching_count']
                recipe['total_ingredients'] = match_info['total_count']
                recipe['missing_ingredients'] = match_info['missing']
                recipe['matched_ingredients'] = match_info['matched']
                matching_recipes.append(recipe)
        
        # Sort by match percentage (highest first)
        matching_recipes.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return matching_recipes
    
    def find_exact_matches(self, available_ingredients: List[str]) -> List[Dict]:
        """
        Find recipes that can be made with ONLY the available ingredients (100% match)
        
        Args:
            available_ingredients: List of ingredients you have
        
        Returns:
            List of recipes you can make completely
        """
        return self.find_matching_recipes(available_ingredients, match_threshold=1.0)
    
    def find_close_matches(self, available_ingredients: List[str], 
                          max_missing: int = 2) -> List[Dict]:
        """
        Find recipes you're close to making (missing only a few ingredients)
        
        Args:
            available_ingredients: List of ingredients you have
            max_missing: Maximum number of missing ingredients allowed
        
        Returns:
            List of recipes with match info
        """
        all_matches = self.find_matching_recipes(available_ingredients, 
                                                 match_threshold=0.0)
        
        # Filter to only recipes missing max_missing or fewer ingredients
        close_matches = [
            recipe for recipe in all_matches
            if len(recipe['missing_ingredients']) <= max_missing
        ]
        
        return close_matches
    
    def suggest_ingredients(self, available_ingredients: List[str], 
                           top_n: int = 10) -> List[Dict]:
        """
        Suggest ingredients to buy to unlock more recipes
        
        Args:
            available_ingredients: List of ingredients you have
            top_n: Number of suggestions to return
        
        Returns:
            List of ingredient suggestions with recipe counts
        """
        # Get all recipes and their ingredients
        all_recipes = self.db.get_all_recipes()
        
        # Track which ingredients would unlock which recipes
        ingredient_impact = {}
        
        normalized_available = set(self._normalize_ingredient(ing) 
                                  for ing in available_ingredients)
        
        for recipe in all_recipes:
            recipe_ingredients = self.db.get_ingredients(recipe['id'])
            
            # Find missing ingredients for this recipe
            for ing in recipe_ingredients:
                ing_text = ing['ingredient_text']
                normalized = self._normalize_ingredient(ing_text)
                
                # If we don't have this ingredient
                if normalized not in normalized_available:
                    if ing_text not in ingredient_impact:
                        ingredient_impact[ing_text] = {
                            'ingredient': ing_text,
                            'recipe_count': 0,
                            'recipes': []
                        }
                    
                    ingredient_impact[ing_text]['recipe_count'] += 1
                    ingredient_impact[ing_text]['recipes'].append(recipe['name'])
        
        # Sort by impact (most recipes unlocked)
        suggestions = sorted(
            ingredient_impact.values(),
            key=lambda x: x['recipe_count'],
            reverse=True
        )
        
        return suggestions[:top_n]
    
    def _calculate_match(self, available_ingredients: List[str], 
                        recipe_ingredients: List[Dict]) -> Dict:
        """
        Calculate how well available ingredients match recipe ingredients
        
        Args:
            available_ingredients: Normalized list of available ingredients
            recipe_ingredients: List of recipe ingredient dictionaries
        
        Returns:
            Dictionary with match statistics
        """
        total_count = len(recipe_ingredients)
        
        if total_count == 0:
            return {
                'match_percentage': 0.0,
                'matching_count': 0,
                'total_count': 0,
                'missing': [],
                'matched': []
            }
        
        matched = []
        missing = []
        
        for recipe_ing in recipe_ingredients:
            ing_text = recipe_ing['ingredient_text']
            
            # Skip empty or invalid ingredients
            if not ing_text or ing_text.strip() in ['', '...', '.', '-']:
                total_count -= 1
                continue
                
            normalized_recipe_ing = self._normalize_ingredient(ing_text)
            
            # Skip if normalized to nothing
            if not normalized_recipe_ing or len(normalized_recipe_ing) < 2:
                total_count -= 1
                continue
            
            # Check if we have this ingredient
            is_match = False
            for available_ing in available_ingredients:
                if self._is_ingredient_match(available_ing, normalized_recipe_ing):
                    is_match = True
                    matched.append(ing_text)
                    break
            
            if not is_match:
                missing.append(ing_text)
        
        matching_count = len(matched)
        match_percentage = matching_count / total_count if total_count > 0 else 0.0
        
        return {
            'match_percentage': match_percentage,
            'matching_count': matching_count,
            'total_count': total_count,
            'missing': missing,
            'matched': matched
        }
    
    def _normalize_ingredient(self, ingredient: str) -> str:
        """
        Normalize ingredient text for matching
        
        Args:
            ingredient: Raw ingredient text
        
        Returns:
            Normalized ingredient name
        """
        # Convert to lowercase
        normalized = ingredient.lower()
        
        # Remove common measurements and quantities
        patterns_to_remove = [
            r'\d+[\s]*(cup|cups|tablespoon|tablespoons|tbsp|teaspoon|teaspoons|tsp|pound|pounds|lb|lbs|ounce|ounces|oz|gram|grams|g|kg|ml|liter|liters)',
            r'\d+[\s]*/[\s]*\d+',  # Fractions like 1/2
            r'\d+\.?\d*',  # Numbers
            r'\([^)]*\)',  # Text in parentheses
        ]
        
        for pattern in patterns_to_remove:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # Remove common descriptors
        descriptors = [
            'fresh', 'dried', 'frozen', 'canned', 'chopped', 'diced', 'minced',
            'sliced', 'shredded', 'grated', 'ground', 'crushed', 'whole',
            'large', 'medium', 'small', 'optional', 'to taste'
        ]
        
        for descriptor in descriptors:
            normalized = re.sub(r'\b' + descriptor + r'\b', '', normalized, flags=re.IGNORECASE)
        
        # Remove extra whitespace and punctuation
        normalized = re.sub(r'[,.]', '', normalized)
        normalized = ' '.join(normalized.split())
        
        return normalized.strip()
    
    def _is_ingredient_match(self, ingredient1: str, ingredient2: str, 
                           threshold: float = 0.7) -> bool:
        """
        Check if two ingredient names match
        
        Args:
            ingredient1: First ingredient (normalized)
            ingredient2: Second ingredient (normalized)
            threshold: Similarity threshold (0.0-1.0)
        
        Returns:
            True if ingredients match
        """
        # Exact match
        if ingredient1 == ingredient2:
            return True
        
        # Check if one contains the other (substring match)
        if ingredient1 in ingredient2 or ingredient2 in ingredient1:
            return True
        
        # Check individual words - more lenient matching
        words1 = set(ingredient1.split())
        words2 = set(ingredient2.split())
        
        # Remove very common words that don't help matching
        common_fillers = {'and', 'or', 'with', 'of', 'the', 'a', 'an', 'for'}
        words1 = words1 - common_fillers
        words2 = words2 - common_fillers
        
        # If they share any significant words, consider it a match
        common_words = words1.intersection(words2)
        if common_words:
            # If ANY word matches (for single-word searches like "chocolate")
            if len(words1) == 1 or len(words2) == 1:
                return True
            # For multi-word ingredients, need at least half the words to match
            min_len = min(len(words1), len(words2))
            if len(common_words) >= min_len * 0.5:
                return True
        
        # Use fuzzy matching as last resort
        similarity = SequenceMatcher(None, ingredient1, ingredient2).ratio()
        return similarity >= threshold
    
    def get_recipe_match_details(self, recipe_id: int, 
                                 available_ingredients: List[str]) -> Dict:
        """
        Get detailed match information for a specific recipe
        
        Args:
            recipe_id: Recipe ID
            available_ingredients: List of available ingredients
        
        Returns:
            Detailed match information
        """
        recipe = self.db.get_recipe(recipe_id)
        if not recipe:
            return None
        
        normalized_available = [self._normalize_ingredient(ing) 
                               for ing in available_ingredients]
        
        recipe_ingredients = recipe.get('ingredients', [])
        
        match_info = self._calculate_match(normalized_available, recipe_ingredients)
        
        return {
            'recipe_name': recipe['name'],
            'recipe_id': recipe_id,
            'match_percentage': match_info['match_percentage'] * 100,
            'can_make': match_info['match_percentage'] == 1.0,
            'have': match_info['matched'],
            'need': match_info['missing'],
            'have_count': match_info['matching_count'],
            'need_count': len(match_info['missing']),
            'total_count': match_info['total_count']
        }
