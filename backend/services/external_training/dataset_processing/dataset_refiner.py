"""
Dataset Refiner
Cleans, validates, and refines datasets before RAG training
Ensures high-quality training data for optimal minion performance
"""

import re
import json
from typing import List, Dict, Any, Tuple
from collections import Counter


class DatasetRefiner:
    """
    Professional dataset cleaning and refinement service
    Ensures training data is high-quality and properly formatted
    """
    
    def __init__(self):
        self.stats = {
            'original_count': 0,
            'removed_duplicates': 0,
            'removed_empty': 0,
            'removed_low_quality': 0,
            'removed_malformed': 0,
            'final_count': 0
        }
    
    def refine_dataset(self, raw_data: List[Dict[str, Any]], 
                      min_text_length: int = 10,
                      max_text_length: int = 10000) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Refine dataset with comprehensive cleaning
        
        Args:
            raw_data: Raw dataset items
            min_text_length: Minimum text length to keep
            max_text_length: Maximum text length to keep
            
        Returns:
            Tuple of (refined_data, statistics)
        """
        print(f"\n{'='*60}")
        print(f"🧹 Starting Dataset Refinement")
        print(f"{'='*60}\n")
        
        self.stats['original_count'] = len(raw_data)
        print(f"📊 Original dataset size: {len(raw_data)} items")
        
        # Step 1: Remove completely empty items
        data = self._remove_empty_items(raw_data)
        print(f"   ✓ Removed {self.stats['removed_empty']} empty items")
        
        # Step 2: Remove duplicates
        data = self._remove_duplicates(data)
        print(f"   ✓ Removed {self.stats['removed_duplicates']} duplicate items")
        
        # Step 3: Filter by length
        data = self._filter_by_length(data, min_text_length, max_text_length)
        print(f"   ✓ Removed {self.stats['removed_low_quality']} items (length filter)")
        
        # Step 4: Remove malformed items
        data = self._remove_malformed(data)
        print(f"   ✓ Removed {self.stats['removed_malformed']} malformed items")
        
        # Step 5: Normalize text
        data = self._normalize_text(data)
        print(f"   ✓ Normalized text in all items")
        
        # Step 6: Validate structure
        data = self._validate_structure(data)
        print(f"   ✓ Validated data structure")
        
        self.stats['final_count'] = len(data)
        
        print(f"\n{'='*60}")
        print(f"✅ Dataset Refinement Complete")
        print(f"   Original: {self.stats['original_count']} items")
        print(f"   Final: {self.stats['final_count']} items")
        print(f"   Quality: {self._calculate_quality_score()}%")
        print(f"{'='*60}\n")
        
        return data, self.stats
    
    def _remove_empty_items(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove items with no meaningful content"""
        filtered = []
        
        for item in data:
            # Check if item has any non-empty text content
            has_content = False
            
            for key in ['instruction', 'output', 'input', 'context', 'text', 'code']:
                if key in item and item[key] and str(item[key]).strip():
                    has_content = True
                    break
            
            if has_content:
                filtered.append(item)
            else:
                self.stats['removed_empty'] += 1
        
        return filtered
    
    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate items based on content hash"""
        seen_hashes = set()
        filtered = []
        
        for item in data:
            # Create content hash
            content = self._extract_main_content(item)
            content_hash = hash(content.lower().strip())
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                filtered.append(item)
            else:
                self.stats['removed_duplicates'] += 1
        
        return filtered
    
    def _filter_by_length(self, data: List[Dict[str, Any]], 
                         min_length: int, max_length: int) -> List[Dict[str, Any]]:
        """Filter items by text length"""
        filtered = []
        
        for item in data:
            content = self._extract_main_content(item)
            length = len(content)
            
            if min_length <= length <= max_length:
                filtered.append(item)
            else:
                self.stats['removed_low_quality'] += 1
        
        return filtered
    
    def _remove_malformed(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove malformed items (invalid JSON, corrupted data, etc.)"""
        filtered = []
        
        for item in data:
            is_valid = True
            
            # Check for common corruption patterns
            content = self._extract_main_content(item)
            
            # Check for excessive special characters
            special_char_ratio = len(re.findall(r'[^\w\s]', content)) / max(len(content), 1)
            if special_char_ratio > 0.5:  # More than 50% special chars
                is_valid = False
            
            # Check for binary/non-text content
            if any(ord(c) > 127 for c in content[:100]):  # Check first 100 chars
                non_ascii_ratio = sum(1 for c in content if ord(c) > 127) / max(len(content), 1)
                if non_ascii_ratio > 0.3:  # More than 30% non-ASCII
                    is_valid = False
            
            # Check for repeated patterns (likely corrupted)
            if len(set(content.split())) / max(len(content.split()), 1) < 0.1:  # Less than 10% unique words
                is_valid = False
            
            if is_valid:
                filtered.append(item)
            else:
                self.stats['removed_malformed'] += 1
        
        return filtered
    
    def _normalize_text(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize text content"""
        normalized = []
        
        for item in data:
            normalized_item = {}
            
            for key, value in item.items():
                if isinstance(value, str):
                    # Remove excessive whitespace
                    value = re.sub(r'\s+', ' ', value).strip()
                    
                    # Normalize quotes
                    value = value.replace('"', '"').replace('"', '"')
                    value = value.replace(''', "'").replace(''', "'")
                    
                    # Remove null bytes
                    value = value.replace('\x00', '')
                
                normalized_item[key] = value
            
            normalized.append(normalized_item)
        
        return normalized
    
    def _validate_structure(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate that each item has required structure"""
        # For now, just ensure each item is a dict with at least one text field
        return [item for item in data if isinstance(item, dict) and len(item) > 0]
    
    def _extract_main_content(self, item: Dict[str, Any]) -> str:
        """Extract main text content from an item"""
        # Priority order for content extraction
        priority_keys = ['output', 'context', 'instruction', 'text', 'code', 'input']
        
        for key in priority_keys:
            if key in item and item[key]:
                return str(item[key])
        
        # Fallback: concatenate all string values
        return ' '.join(str(v) for v in item.values() if v)
    
    def _calculate_quality_score(self) -> int:
        """Calculate quality score based on refinement stats"""
        if self.stats['original_count'] == 0:
            return 0
        
        retention_rate = self.stats['final_count'] / self.stats['original_count']
        
        # Quality score based on what was removed
        quality = 100
        quality -= (self.stats['removed_duplicates'] / max(self.stats['original_count'], 1)) * 20
        quality -= (self.stats['removed_empty'] / max(self.stats['original_count'], 1)) * 30
        quality -= (self.stats['removed_malformed'] / max(self.stats['original_count'], 1)) * 25
        
        return max(0, int(quality))  # Remove artificial cap for large-scale usage
    
    def get_refinement_report(self) -> Dict[str, Any]:
        """Get detailed refinement report"""
        return {
            'statistics': self.stats.copy(),
            'quality_score': self._calculate_quality_score(),
            'retention_rate': self.stats['final_count'] / max(self.stats['original_count'], 1),
            'improvements': {
                'duplicates_removed': self.stats['removed_duplicates'],
                'empty_removed': self.stats['removed_empty'],
                'low_quality_removed': self.stats['removed_low_quality'],
                'malformed_removed': self.stats['removed_malformed']
            }
        }


# Singleton instance
_dataset_refiner = None

def get_dataset_refiner() -> DatasetRefiner:
    """Get or create DatasetRefiner singleton"""
    global _dataset_refiner
    if _dataset_refiner is None:
        _dataset_refiner = DatasetRefiner()
    return _dataset_refiner

