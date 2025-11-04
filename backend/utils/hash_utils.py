"""
Hash utilities for training configuration deduplication
Generates consistent hashes for RAG config + dataset combinations
"""

import json
import hashlib
from typing import Dict, List, Any

def generate_training_hash(rag_config: Dict[str, Any], datasets: List[str]) -> str:
    """
    Generate a consistent hash key for a training setup (rag_config + datasets).
    Sorting ensures the hash is identical even if dataset order changes.
    
    Args:
        rag_config: RAG configuration dictionary
        datasets: List of dataset identifiers
        
    Returns:
        SHA-256 hash string (64 characters)
    """
    # Normalize the configuration
    normalized = {
        "rag_config": rag_config,
        "datasets": sorted(datasets)  # Sort to ensure consistent ordering
    }
    
    # Serialize to JSON with sorted keys for consistency
    serialized = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
    
    # Generate SHA-256 hash
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def get_config_fingerprint(config_hash: str, length: int = 8) -> str:
    """
    Get a short fingerprint of the configuration hash for display purposes.
    
    Args:
        config_hash: Full SHA-256 hash
        length: Number of characters to return (default: 8)
        
    Returns:
        Short fingerprint string
    """
    return config_hash[:length] if config_hash else "unknown"

def compare_configs(config1: Dict[str, Any], datasets1: List[str], 
                   config2: Dict[str, Any], datasets2: List[str]) -> bool:
    """
    Compare two training configurations to see if they're identical.
    
    Args:
        config1, config2: RAG configuration dictionaries
        datasets1, datasets2: Dataset identifier lists
        
    Returns:
        True if configurations are identical, False otherwise
    """
    hash1 = generate_training_hash(config1, datasets1)
    hash2 = generate_training_hash(config2, datasets2)
    return hash1 == hash2

# Example usage and testing
if __name__ == "__main__":
    # Test hash consistency
    config1 = {"chunk_size": 512, "similarity_threshold": 0.7}
    datasets1 = ["dataset1.json", "dataset2.csv"]
    
    config2 = {"chunk_size": 512, "similarity_threshold": 0.7}
    datasets2 = ["dataset2.csv", "dataset1.json"]  # Different order
    
    hash1 = generate_training_hash(config1, datasets1)
    hash2 = generate_training_hash(config2, datasets2)
    
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    print(f"Identical: {hash1 == hash2}")
    print(f"Fingerprint: {get_config_fingerprint(hash1)}")
