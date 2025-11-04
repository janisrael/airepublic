#!/usr/bin/env python3
"""
Cleanup script to remove all training data for Grafana (minion_id 17)
This will:
1. Delete all training jobs for minion_id 17
2. Delete all training history records (TrainingResult)
3. Optionally clean up ChromaDB collections
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.postgres_connection import create_spirit_engine
from model.training import ExternalTrainingJob
from model.training_results import TrainingResult
from sqlalchemy.orm import sessionmaker
import json

MINION_ID = 17  # Grafana

def cleanup_grafana_training():
    """Remove all training data for Grafana"""
    print(f"\n{'='*60}")
    print(f"🧹 Cleaning up all training data for Minion {MINION_ID} (Grafana)")
    print(f"{'='*60}\n")
    
    # Create session factory
    engine = create_spirit_engine()
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        try:
            # 1. Get all training jobs for Grafana
            training_jobs = session.query(ExternalTrainingJob).filter_by(minion_id=MINION_ID).all()
            print(f"📋 Found {len(training_jobs)} training jobs for Grafana")
            
            if not training_jobs:
                print("✅ No training jobs found. Nothing to clean.")
                return
            
            # Show jobs before deletion
            print("\n📝 Training jobs to be deleted:")
            for job in training_jobs:
                status = job.status.value if hasattr(job.status, 'value') else str(job.status)
                print(f"   - Job #{job.id}: {job.job_name} ({status})")
            
            # 2. Get all training history records
            training_results = session.query(TrainingResult).filter_by(minion_id=MINION_ID).all()
            print(f"\n📋 Found {len(training_results)} training history records")
            
            # Show history records
            if training_results:
                print("\n📝 Training history records to be deleted:")
                for result in training_results:
                    print(f"   - History #{result.id}: Job #{result.job_id}, Type: {result.training_type}")
            
            # 3. Get collection names from RAG configs
            collections_to_clean = set()
            for job in training_jobs:
                if job.config:
                    try:
                        config = json.loads(job.config) if isinstance(job.config, str) else job.config
                        rag_config = config.get('rag_config', {})
                        collection_name = rag_config.get('collectionName')
                        if collection_name:
                            collections_to_clean.add(collection_name)
                    except:
                        pass
            
            if collections_to_clean:
                print(f"\n🗄️  ChromaDB collections that may need cleanup:")
                for coll in collections_to_clean:
                    print(f"   - {coll}")
                print("   ⚠️  Note: Collections will need manual cleanup from ChromaDB")
            
            # Confirm deletion
            print(f"\n⚠️  WARNING: This will permanently delete:")
            print(f"   - {len(training_jobs)} training jobs")
            print(f"   - {len(training_results)} training history records")
            
            response = input("\n❓ Continue? (yes/no): ").strip().lower()
            if response != 'yes':
                print("❌ Cleanup cancelled.")
                return
            
            # 4. Delete training history records first (due to foreign key constraints)
            deleted_history = 0
            for result in training_results:
                session.delete(result)
                deleted_history += 1
            
            print(f"\n🗑️  Deleted {deleted_history} training history records")
            
            # 5. Delete training jobs (this will cascade delete related records)
            deleted_jobs = 0
            for job in training_jobs:
                session.delete(job)
                deleted_jobs += 1
            
            print(f"🗑️  Deleted {deleted_jobs} training jobs")
            
            # 6. Commit changes
            session.commit()
            
            print(f"\n✅ Cleanup completed successfully!")
            print(f"   - Deleted {deleted_jobs} training jobs")
            print(f"   - Deleted {deleted_history} training history records")
            
            if collections_to_clean:
                print(f"\n⚠️  Manual cleanup needed:")
                print(f"   - ChromaDB collections: {', '.join(collections_to_clean)}")
                print(f"   - These can be removed from: backend/app/services/chromadb_data/")
            
        except Exception as e:
            session.rollback()
            print(f"\n❌ Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    cleanup_grafana_training()

