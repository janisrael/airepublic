#!/usr/bin/env python3
"""
Prepare Amigo Datasets for Training
Converts downloaded datasets to NL→Code training format and combines them
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


def prepare_all_datasets():
    """Prepare all downloaded datasets for training"""
    
    logger.info("🔧 Preparing Amigo Stage 1 Datasets for Training")
    logger.info("=" * 70)
    
    service = get_amigo_dataset_service()
    data_dir = service.data_dir
    
    # Find all downloaded JSONL files (not already formatted)
    downloaded_files = []
    for file in os.listdir(data_dir):
        if file.endswith('.jsonl') and not file.endswith('_formatted.jsonl') and not file.startswith('amigo_train_') and not file.startswith('amigo_val_'):
            downloaded_files.append(os.path.join(data_dir, file))
    
    if not downloaded_files:
        logger.error("❌ No downloaded datasets found!")
        logger.info(f"   Looking in: {data_dir}")
        logger.info("   Please run download_amigo_datasets.py first")
        return
    
    logger.info(f"📋 Found {len(downloaded_files)} datasets to prepare:")
    for f in downloaded_files:
        logger.info(f"   - {os.path.basename(f)}")
    
    logger.info("")
    
    # Prepare each dataset
    prepared_files = []
    
    for dataset_file in downloaded_files:
        logger.info(f"🔧 Preparing: {os.path.basename(dataset_file)}")
        logger.info("-" * 70)
        
        output_file = dataset_file.replace('.jsonl', '_formatted.jsonl')
        
        result = service.prepare_for_training(
            dataset_file=dataset_file,
            output_file=output_file,
            format_type="auto"  # Auto-detect format
        )
        
        if result["success"]:
            logger.info(f"✅ Prepared: {result['output_file']}")
            logger.info(f"   Samples: {result['samples']:,}")
            logger.info(f"   Format: {result['format_type']}")
            prepared_files.append(result["output_file"])
        else:
            logger.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    logger.info("")
    logger.info("=" * 70)
    
    if prepared_files:
        logger.info("🔄 Combining all datasets into train/val splits...")
        logger.info("")
        
        # Manual combination from prepared files
        import json
        all_data = []
        for prep_file in prepared_files:
            logger.info(f"   Loading: {os.path.basename(prep_file)}")
            with open(prep_file, 'r') as f:
                for line in f:
                    if line.strip():
                        all_data.append(json.loads(line))
        
        # Split into train/val
        from datetime import datetime
        split_idx = int(len(all_data) * 0.9)
        train_data = all_data[:split_idx]
        val_data = all_data[split_idx:]
        
        # Save train/val files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        train_file = os.path.join(data_dir, f"amigo_train_{timestamp}.jsonl")
        val_file = os.path.join(data_dir, f"amigo_val_{timestamp}.jsonl")
        
        logger.info(f"   Writing train: {len(train_data):,} samples")
        with open(train_file, 'w') as f:
            for item in train_data:
                f.write(json.dumps(item) + '\n')
        
        logger.info(f"   Writing val: {len(val_data):,} samples")
        with open(val_file, 'w') as f:
            for item in val_data:
                f.write(json.dumps(item) + '\n')
        
        logger.info("")
        logger.info("✅ Training datasets ready!")
        logger.info(f"   Train: {train_file}")
        logger.info(f"   Val: {val_file}")
        logger.info(f"   Total samples: {len(all_data):,} ({len(train_data):,} train, {len(val_data):,} val)")
    else:
        logger.error("❌ No datasets were prepared successfully")
    
    logger.info("")
    logger.info("✅ Dataset preparation complete!")


if __name__ == "__main__":
    try:
        prepare_all_datasets()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Preparation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

