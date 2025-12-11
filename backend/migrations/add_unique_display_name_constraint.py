#!/usr/bin/env python3
"""
Migration: Add unique constraint for display_name per user
Ensures display_name is unique per user_id in external_api_models table
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database.postgres_connection import create_spirit_engine

def add_unique_constraint():
    """Add unique constraint for (user_id, display_name)"""
    engine = create_spirit_engine()
    
    with engine.connect() as conn:
        try:
            # Check if constraint already exists
            check_result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'external_api_models' 
                AND constraint_name = 'uq_user_display_name'
            """))
            
            if check_result.fetchone():
                print("✅ Unique constraint already exists!")
                return
            
            # First, ensure no duplicates exist (should have been fixed by script)
            print("📊 Checking for existing duplicates...")
            dup_result = conn.execute(text("""
                SELECT user_id, display_name, COUNT(*) as count
                FROM external_api_models
                WHERE is_active = true
                GROUP BY user_id, display_name
                HAVING COUNT(*) > 1
            """))
            
            duplicates = dup_result.fetchall()
            if duplicates:
                print("⚠️  WARNING: Duplicates found! Please run fix_duplicate_display_names.py first:")
                for dup in duplicates:
                    print(f"   User {dup[0]}: '{dup[1]}' ({dup[2]} duplicates)")
                return
            
            # Add unique constraint
            print("🔧 Adding unique constraint...")
            conn.execute(text("""
                ALTER TABLE external_api_models
                ADD CONSTRAINT uq_user_display_name 
                UNIQUE (user_id, display_name)
            """))
            conn.commit()
            
            print("✅ Unique constraint added successfully!")
            
        except Exception as e:
            conn.rollback()
            if 'already exists' in str(e).lower():
                print("✅ Unique constraint already exists!")
            else:
                print(f"❌ Error adding constraint: {e}")
                raise

def remove_constraint():
    """Remove unique constraint (for rollback)"""
    engine = create_spirit_engine()
    
    with engine.connect() as conn:
        try:
            print("🔧 Removing unique constraint...")
            conn.execute(text("""
                ALTER TABLE external_api_models
                DROP CONSTRAINT IF EXISTS uq_user_display_name
            """))
            conn.commit()
            print("✅ Unique constraint removed!")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error removing constraint: {e}")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Add or remove unique constraint for display_name')
    parser.add_argument('--add', action='store_true', help='Add unique constraint')
    parser.add_argument('--remove', action='store_true', help='Remove unique constraint')
    
    args = parser.parse_args()
    
    if args.add:
        add_unique_constraint()
    elif args.remove:
        remove_constraint()
    else:
        print("Usage:")
        print("  python add_unique_display_name_constraint.py --add     # Add constraint")
        print("  python add_unique_display_name_constraint.py --remove  # Remove constraint")


