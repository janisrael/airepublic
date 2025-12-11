#!/usr/bin/env python3
"""
Migration: Add spirits_enabled column to external_api_models table
Phase 4 - Chat Endpoint Unification
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.postgres_connection import create_spirit_engine
from sqlalchemy import text

def run_migration():
    """Add spirits_enabled column to external_api_models table"""
    
    engine = create_spirit_engine()
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            print("🔄 Adding Spirit Orchestration configuration field...")
            
            # Add spirits_enabled field
            conn.execute(text(
                "ALTER TABLE external_api_models ADD COLUMN IF NOT EXISTS spirits_enabled BOOLEAN DEFAULT FALSE NOT NULL"
            ))
            print("   ✓ Added: spirits_enabled")
            
            # Commit transaction
            trans.commit()
            print("\n✅ Migration completed successfully!")
            print("   All minions now have spirits_enabled column (default: False)")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    run_migration()








