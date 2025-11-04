#!/usr/bin/env python3
"""
Create TrainingResult table in PostgreSQL database
Pure SQLAlchemy implementation - no PostgreSQL references
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database.postgres_connection import create_spirit_engine
from model.training_results import TrainingResult
from model.base import Base

def create_training_results_table():
    """Create the training_results table using SQLAlchemy"""
    try:
        print("🔧 Creating TrainingResult table...")
        
        # Get the engine
        engine = create_spirit_engine()
        
        # Create all tables (this will create training_results if it doesn't exist)
        Base.metadata.create_all(bind=engine)
        
        print("✅ TrainingResult table created successfully!")
        
        # Verify the table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'training_results'
            """))
            
            if result.fetchone():
                print("✅ Verified: training_results table exists")
            else:
                print("❌ Error: training_results table not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating TrainingResult table: {e}")
        return False

if __name__ == "__main__":
    success = create_training_results_table()
    if success:
        print("\n🎉 TrainingResult table setup complete!")
    else:
        print("\n💥 TrainingResult table setup failed!")
        sys.exit(1)
