#!/usr/bin/env python3
"""
Download Amigo Stage 1 Training Datasets
Downloads REAL datasets (full size) for NL→Code training
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.amigo_dataset_service import get_amigo_dataset_service
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Download all Stage 1 datasets for Amigo training"""
    
    logger.info("🚀 Starting Amigo Stage 1 Dataset Download")
    logger.info("=" * 60)
    
    # Initialize service
    service = get_amigo_dataset_service()
    
    # Stage 1 datasets (from AMIGO_REFINEMENT_PLAN.md)
    stage1_datasets = [
        {
            "id": "bigcode/commitpackft",
            "description": "Commit messages → code changes (HIGHEST PRIORITY - Cursor-style)",
            "size": "~5-10GB",
            "split": None  # All splits
        },
        {
            "id": "bigcode/humanevalpack",
            "description": "HumanEval: NL problem → code solution",
            "size": "~500MB",
            "split": "python"  # Start with Python
        },
        {
            "id": "bigcode/python_self_instruct",
            "description": "Self-instructed Python tasks (NL → Python code)",
            "size": "~2-5GB",
            "split": None
        }
    ]
    
    results = []
    
    for i, dataset_config in enumerate(stage1_datasets, 1):
        dataset_id = dataset_config["id"]
        split = dataset_config.get("split")
        
        logger.info(f"\n[{i}/{len(stage1_datasets)}] Processing: {dataset_id}")
        logger.info(f"Description: {dataset_config['description']}")
        logger.info(f"Expected size: {dataset_config['size']}")
        logger.info("-" * 60)
        
        try:
            # Download dataset (FULL - no max_samples limit)
            logger.info(f"📥 Downloading {dataset_id}...")
            download_result = service.download_dataset(
                dataset_id=dataset_id,
                split=split,
                max_samples=None  # Full dataset
            )
            
            if not download_result["success"]:
                logger.error(f"❌ Failed to download {dataset_id}: {download_result.get('error')}")
                results.append({
                    "dataset": dataset_id,
                    "status": "failed",
                    "error": download_result.get("error")
                })
                continue
            
            logger.info(f"✅ Downloaded: {download_result['samples']} samples")
            logger.info(f"📁 Saved to: {download_result['file_path']}")
            
            # Prepare for training (format NL→Code)
            logger.info(f"📊 Preparing dataset for NL→Code training...")
            prep_result = service.prepare_for_training(
                dataset_file=download_result["file_path"],
                output_file=download_result["file_path"].replace(".jsonl", "_formatted.jsonl"),
                format_type="auto"
            )
            
            if not prep_result["success"]:
                logger.error(f"❌ Failed to prepare {dataset_id}: {prep_result.get('error')}")
                results.append({
                    "dataset": dataset_id,
                    "status": "download_ok_prepare_failed",
                    "error": prep_result.get("error"),
                    "raw_file": download_result["file_path"]
                })
                continue
            
            logger.info(f"✅ Prepared: {prep_result['samples']} formatted samples")
            logger.info(f"📁 Formatted file: {prep_result['output_file']}")
            
            results.append({
                "dataset": dataset_id,
                "status": "success",
                "raw_file": download_result["file_path"],
                "formatted_file": prep_result["output_file"],
                "samples": prep_result["samples"],
                "format_type": prep_result["format_type"]
            })
            
        except Exception as e:
            logger.error(f"❌ Error processing {dataset_id}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "dataset": dataset_id,
                "status": "error",
                "error": str(e)
            })
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 DOWNLOAD SUMMARY")
    logger.info("=" * 60)
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] != "success"]
    
    logger.info(f"✅ Successfully downloaded and prepared: {len(successful)}/{len(stage1_datasets)}")
    logger.info(f"❌ Failed: {len(failed)}/{len(stage1_datasets)}")
    
    if successful:
        logger.info("\n✅ SUCCESSFUL DATASETS:")
        total_samples = 0
        for result in successful:
            logger.info(f"  • {result['dataset']}: {result['samples']} samples")
            logger.info(f"    Formatted: {result['formatted_file']}")
            total_samples += result['samples']
        
        logger.info(f"\n📈 Total samples prepared: {total_samples:,}")
        logger.info("\n💡 Next step: Combine these datasets for training!")
        logger.info("   Run: python scripts/combine_amigo_datasets.py")
    
    if failed:
        logger.info("\n❌ FAILED DATASETS:")
        for result in failed:
            logger.info(f"  • {result['dataset']}: {result.get('error', 'Unknown error')}")
    
    # Save results summary
    summary_file = os.path.join(service.data_dir, "download_summary.json")
    with open(summary_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "stage": "Stage 1 - NL→Code",
            "results": results,
            "successful": len(successful),
            "failed": len(failed)
        }, f, indent=2)
    
    logger.info(f"\n📝 Summary saved to: {summary_file}")
    
    return len(successful) == len(stage1_datasets)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

