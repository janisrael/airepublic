#!/usr/bin/env python3
"""
Migration: Add class_name column to external_api_models table
This allows minions to have an assigned class
"""

import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def add_class_name_column():
    """Add class_name column to external_api_models table"""
    try:
        from database.postgres_connection import create_spirit_engine
        from sqlalchemy import text
        
        engine = create_spirit_engine()
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'external_api_models' 
                AND column_name = 'class_name'
            """))
            
            if result.fetchone():
                print("✅ class_name column already exists in external_api_models table")
                return True
            
            # Add class_name column
            conn.execute(text("""
                ALTER TABLE external_api_models 
                ADD COLUMN class_name VARCHAR(100)
            """))
            
            # Add index for performance
            conn.execute(text("""
                CREATE INDEX idx_external_api_models_class_name 
                ON external_api_models(class_name)
            """))
            
            conn.commit()
            print("✅ Successfully added class_name column to external_api_models table")
            return True
            
    except Exception as e:
        print(f"❌ Error adding class_name column: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Adding class_name column to external_api_models table...")
    success = add_class_name_column()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)
