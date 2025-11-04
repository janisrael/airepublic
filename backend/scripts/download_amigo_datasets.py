#!/usr/bin/env python3
"""
Download Full Amigo Stage 1 Datasets
Downloads the complete datasets (no size limits) for Amigo training:
- bigcode/commitpackft (Primary) - ~5-10GB
- bigcode/humanevalpack (Primary) - ~500MB  
- bigcode/python_self_instruct (Secondary) - ~2-5GB
"""

import sys
import os
import logging
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.amigo_dataset_service import get_amigo_dataset_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_full_datasets():
    """Download full Stage 1 datasets for Amigo"""
    
    logger.info("🚀 Starting Amigo Stage 1 Dataset Download (FULL datasets)")
    logger.info("=" * 70)
    
    service = get_amigo_dataset_service()
    
    # Stage 1 Primary Datasets (Tier 1)
    stage1_datasets = [
        {
            "id": "bigcode/humanevalpack",
            "split": "python",  # Start with Python, can add other languages later
            "description": "HumanEval: NL problem → code solution (PRIMARY - ~500MB)"
        },
        {
            "id": "WizardLM/WizardCoder-Python-V1.0",
            "split": "all",
            "description": "WizardCoder Python: High-quality NL→code examples (PRIMARY - ~2-5GB)"
        },
        {
            "id": "bigcode/commitpackft",
            "split": None,  # Try without split first
            "description": "Commit messages → code changes (PRIMARY - ~5-10GB) - May need streaming"
        }
    ]
    
    logger.info(f"📋 Will download {len(stage1_datasets)} datasets:")
    for i, ds in enumerate(stage1_datasets, 1):
        logger.info(f"  {i}. {ds['id']} ({ds['split']}) - {ds['description']}")
    
    logger.info("")
    logger.info("⚠️  This will download FULL datasets (no size limits)")
    logger.info("⚠️  Total estimated size: ~8-16GB")
    logger.info("")
    
    # Download each dataset
    downloaded_files = []
    
    for ds_info in stage1_datasets:
        dataset_id = ds_info["id"]
        split = ds_info["split"]
        
        logger.info("")
        logger.info(f"📥 Downloading: {dataset_id} (split: {split})")
        logger.info(f"   {ds_info['description']}")
        logger.info("-" * 70)
        
        # Download FULL dataset (no max_samples limit)
        split_arg = None if not split or split == "all" else split
        result = service.download_dataset(
            dataset_id=dataset_id,
            split=split_arg,
            max_samples=None  # FULL dataset, no limits
        )
        
        if result["success"]:
            logger.info(f"✅ Downloaded: {result['file_path']}")
            logger.info(f"   Samples: {result['samples']:,}")
            downloaded_files.append(result["file_path"])
        else:
            logger.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            logger.warning(f"⚠️  Continuing with other datasets...")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("📊 Download Summary")
    logger.info(f"   Successfully downloaded: {len(downloaded_files)} datasets")
    
    if downloaded_files:
        logger.info("")
        logger.info("📁 Downloaded files:")
        for f in downloaded_files:
            file_size = os.path.getsize(f) / (1024**3)  # GB
            logger.info(f"   {f} ({file_size:.2f} GB)")
        
        logger.info("")
        logger.info("🔄 Next step: Prepare datasets for training format")
        logger.info("   Run: python prepare_amigo_datasets.py")
    else:
        logger.error("❌ No datasets were downloaded successfully")
    
    logger.info("")
    logger.info("✅ Dataset download complete!")


if __name__ == "__main__":
    try:
        download_full_datasets()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

