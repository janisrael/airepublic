"""
Amigo Dataset Service
Downloads and prepares HuggingFace datasets for Amigo training (NL→Code)
"""

import os
import json
from typing import Dict, List, Any, Optional
from datasets import load_dataset
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AmigoDatasetService:
    """Service for downloading and preparing datasets for Amigo training"""
    
    # Amigo-specific datasets (NL→Code focused)
    AMIGO_DATASETS = {
        "bigcode/humanevalpack": {
            "name": "HumanEval Pack",
            "description": "HumanEval with natural language problem descriptions → code solutions",
            "size": "~500MB",
            "splits": ["python", "javascript", "cpp", "java", "go", "rust"],
            "format": "humaneval"
        },
        "bigcode/commitpackft": {
            "name": "Commit Pack FT",
            "description": "Commit messages → code changes (perfect for Cursor-style NL→code)",
            "size": "~5-10GB",
            "splits": ["all"],
            "format": "commit"
        },
        "bigcode/python_self_instruct": {
            "name": "Python Self-Instruct",
            "description": "Self-instructed Python tasks (NL descriptions → Python code)",
            "size": "~2-5GB",
            "splits": ["all"],
            "format": "instruction"
        },
        "WizardLM/WizardCoder-Python-V1.0": {
            "name": "WizardCoder Python",
            "description": "High-quality NL→code examples",
            "size": "~2-5GB",
            "splits": ["all"],
            "format": "instruction"
        }
    }
    
    def __init__(self, data_dir: str = "training_data/amigo_datasets"):
        """Initialize the service"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def list_available_datasets(self) -> List[Dict[str, Any]]:
        """List all available Amigo datasets"""
        return [
            {
                "id": dataset_id,
                **info
            }
            for dataset_id, info in self.AMIGO_DATASETS.items()
        ]
    
    def download_dataset(self, dataset_id: str, split: Optional[str] = None, 
                        max_samples: Optional[int] = None) -> Dict[str, Any]:
        """
        Download a HuggingFace dataset for Amigo training
        
        Args:
            dataset_id: HuggingFace dataset ID (e.g., "bigcode/humanevalpack")
            split: Dataset split (e.g., "python" for humanevalpack)
            max_samples: Maximum number of samples to download (for testing)
        
        Returns:
            Dictionary with download info and file paths
        """
        try:
            logger.info(f"📥 Downloading dataset: {dataset_id}")
            
            dataset_info = self.AMIGO_DATASETS.get(dataset_id)
            if not dataset_info:
                raise ValueError(f"Unknown dataset: {dataset_id}")
            
            # Build dataset loading args
            load_kwargs = {"path": dataset_id}
            if split and split != "all":
                load_kwargs["name"] = split
            
            # Try streaming for large datasets (like commitpackft)
            # If normal load fails, try streaming
            try:
                dataset = load_dataset(**load_kwargs)
            except Exception as e:
                if "Dataset scripts are no longer supported" in str(e) or "doesn't exist" in str(e):
                    # Try with streaming and trust_remote_code for older datasets
                    logger.warning(f"⚠️  Normal load failed, trying streaming mode for {dataset_id}")
                    load_kwargs["streaming"] = False  # Don't stream, but allow trust_remote_code
                    try:
                        load_kwargs["trust_remote_code"] = True
                        dataset = load_dataset(**load_kwargs)
                    except:
                        # Last resort: try with different split handling
                        load_kwargs.pop("name", None)
                        load_kwargs.pop("trust_remote_code", None)
                        dataset = load_dataset(**load_kwargs)
                else:
                    raise
            
            # Determine which split to use
            split_name = 'test' if 'test' in dataset else 'train' if 'train' in dataset else list(dataset.keys())[0]
            dataset_split = dataset[split_name]
            
            # Limit samples if requested
            if max_samples:
                dataset_split = dataset_split.select(range(min(max_samples, len(dataset_split))))
            
            # Save to JSONL
            output_file = os.path.join(
                self.data_dir,
                f"{dataset_id.replace('/', '-')}{f'_{split}' if split and split != 'all' else ''}.jsonl"
            )
            
            dataset_split.to_json(output_file, lines=True)
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "split": split,
                "file_path": output_file,
                "samples": len(dataset_split),
                "message": f"Downloaded {len(dataset_split)} samples to {output_file}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error downloading dataset: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to download dataset: {dataset_id}"
            }
    
    def prepare_for_training(self, dataset_file: str, output_file: str, 
                           format_type: str = "auto") -> Dict[str, Any]:
        """
        Prepare dataset file for Amigo training (NL→Code format)
        
        Args:
            dataset_file: Input JSONL file
            output_file: Output JSONL file (instruction, input, output format)
            format_type: Dataset format ("humaneval", "commit", "instruction", "auto")
        
        Returns:
            Dictionary with preparation info
        """
        try:
            logger.info(f"📊 Preparing dataset: {dataset_file}")
            
            # Load dataset
            data = []
            with open(dataset_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            
            # Detect format if auto
            if format_type == "auto":
                format_type = self._detect_format(data[0] if data else {})
            
            # Format based on type
            formatted_data = []
            for i, sample in enumerate(data):
                try:
                    formatted = self._format_sample(sample, format_type)
                    if formatted:
                        formatted_data.append(formatted)
                except Exception as e:
                    logger.warning(f"⚠️  Error formatting sample {i}: {e}")
                    continue
            
            # Save formatted dataset
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                for item in formatted_data:
                    f.write(json.dumps(item) + '\n')
            
            logger.info(f"✅ Prepared {len(formatted_data)} samples")
            
            return {
                "success": True,
                "input_file": dataset_file,
                "output_file": output_file,
                "samples": len(formatted_data),
                "format_type": format_type,
                "message": f"Prepared {len(formatted_data)} samples"
            }
            
        except Exception as e:
            logger.error(f"❌ Error preparing dataset: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to prepare dataset: {dataset_file}"
            }
    
    def _detect_format(self, sample: Dict) -> str:
        """Detect dataset format from sample"""
        if 'prompt' in sample and 'canonical_solution' in sample:
            return "humaneval"
        elif 'commit_message' in sample or 'message' in sample:
            return "commit"
        elif 'instruction' in sample and 'output' in sample:
            return "instruction"
        else:
            return "instruction"  # Default
    
    def _format_sample(self, sample: Dict, format_type: str) -> Optional[Dict]:
        """Format a single sample for training"""
        if format_type == "humaneval":
            # HumanEval format: prompt → canonical_solution
            instruction = sample.get('prompt', '').strip().replace('"""', '').strip()
            code_solution = sample.get('canonical_solution', '').strip()
            
            if not instruction or not code_solution:
                return None
            
            return {
                "instruction": f"Write a Python function that {instruction}",
                "input": "",
                "output": code_solution
            }
        
        elif format_type == "commit":
            # Commit format: commit_message → code_diff
            message = sample.get('commit_message') or sample.get('message', '').strip()
            code_diff = sample.get('code_diff') or sample.get('diff', '').strip()
            
            if not message or not code_diff:
                return None
            
            return {
                "instruction": f"Implement: {message}",
                "input": "",
                "output": code_diff
            }
        
        elif format_type == "instruction":
            # Already in instruction format or needs minimal conversion
            instruction = sample.get('instruction', '').strip()
            output = sample.get('output') or sample.get('response', '').strip()
            input_text = sample.get('input', '').strip()
            
            if not instruction or not output:
                return None
            
            return {
                "instruction": instruction,
                "input": input_text,
                "output": output
            }
        
        else:
            # Default: try to extract instruction and output
            instruction = sample.get('instruction', '').strip()
            output = sample.get('output', '').strip()
            
            if not instruction or not output:
                return None
            
            return {
                "instruction": instruction,
                "input": "",
                "output": output
            }
    
    def prepare_training_data(self, dataset_ids: List[str], 
                           max_samples_per_dataset: Optional[int] = None,
                           test_split: float = 0.1) -> Dict[str, Any]:
        """
        Download and prepare multiple datasets for Amigo training
        
        Args:
            dataset_ids: List of HuggingFace dataset IDs
            max_samples_per_dataset: Max samples per dataset (for testing)
            test_split: Validation split ratio
        
        Returns:
            Dictionary with train/val file paths
        """
        try:
            all_formatted = []
            
            for dataset_id in dataset_ids:
                logger.info(f"📥 Processing dataset: {dataset_id}")
                
                # Download
                download_result = self.download_dataset(
                    dataset_id,
                    max_samples=max_samples_per_dataset
                )
                
                if not download_result["success"]:
                    logger.warning(f"⚠️  Skipping {dataset_id}: {download_result.get('error')}")
                    continue
                
                # Prepare
                prep_result = self.prepare_for_training(
                    download_result["file_path"],
                    download_result["file_path"].replace(".jsonl", "_formatted.jsonl")
                )
                
                if not prep_result["success"]:
                    logger.warning(f"⚠️  Skipping {dataset_id}: {prep_result.get('error')}")
                    continue
                
                # Load formatted data
                with open(prep_result["output_file"], 'r') as f:
                    for line in f:
                        if line.strip():
                            all_formatted.append(json.loads(line))
            
            # Split into train/val
            split_idx = int(len(all_formatted) * (1 - test_split))
            train_data = all_formatted[:split_idx]
            val_data = all_formatted[split_idx:]
            
            # Save train/val files
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            train_file = os.path.join(self.data_dir, f"amigo_train_{timestamp}.jsonl")
            val_file = os.path.join(self.data_dir, f"amigo_val_{timestamp}.jsonl")
            
            with open(train_file, 'w') as f:
                for item in train_data:
                    f.write(json.dumps(item) + '\n')
            
            with open(val_file, 'w') as f:
                for item in val_data:
                    f.write(json.dumps(item) + '\n')
            
            return {
                "success": True,
                "train_file": train_file,
                "val_file": val_file,
                "train_samples": len(train_data),
                "val_samples": len(val_data),
                "total_samples": len(all_formatted),
                "message": f"Prepared {len(train_data)} train + {len(val_data)} val samples"
            }
            
        except Exception as e:
            logger.error(f"❌ Error preparing training data: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to prepare training data"
            }


# Singleton instance
_amigo_dataset_service = None

def get_amigo_dataset_service() -> AmigoDatasetService:
    """Get singleton AmigoDatasetService instance"""
    global _amigo_dataset_service
    if _amigo_dataset_service is None:
        _amigo_dataset_service = AmigoDatasetService()
    return _amigo_dataset_service



