#!/usr/bin/env python3
"""
Migration: Add RAG and LoRA configuration fields to external_api_models table
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.postgres_connection import create_spirit_engine
from sqlalchemy import text

def run_migration():
    """Add RAG and LoRA fields to external_api_models table"""
    
    engine = create_spirit_engine()
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            print("🔄 Adding RAG configuration fields...")
            
            # Add RAG fields
            rag_fields = [
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS rag_enabled BOOLEAN DEFAULT FALSE NOT NULL",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS rag_collection_name VARCHAR(255)",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS top_k INTEGER DEFAULT 5",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS similarity_threshold FLOAT DEFAULT 0.7",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS retrieval_method VARCHAR(50) DEFAULT 'semantic'",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS enable_contextual_compression BOOLEAN DEFAULT FALSE",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS enable_source_citation BOOLEAN DEFAULT FALSE",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS enable_query_expansion BOOLEAN DEFAULT FALSE",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100) DEFAULT 'all-MiniLM-L6-v2'",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS chunk_size INTEGER DEFAULT 1000",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS chunk_overlap INTEGER DEFAULT 100"
            ]
            
            for field_sql in rag_fields:
                conn.execute(text(field_sql))
                print(f"   ✓ Added: {field_sql.split()[-1]}")
            
            print("\n🔄 Adding LoRA configuration fields...")
            
            # Add LoRA fields
            lora_fields = [
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS lora_enabled BOOLEAN DEFAULT FALSE NOT NULL",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS lora_rank INTEGER DEFAULT 16",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS lora_alpha FLOAT DEFAULT 32.0",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS lora_dropout FLOAT DEFAULT 0.1",
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS lora_target_modules JSON"
            ]
            
            for field_sql in lora_fields:
                conn.execute(text(field_sql))
                print(f"   ✓ Added: {field_sql.split()[-1]}")
            
            # Commit transaction
            trans.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    run_migration()
