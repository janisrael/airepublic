#!/usr/bin/env python3
"""
Migration: Add Minion Profile Fields
Adds title, company, and theme_color fields to minion tables
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import create_database_engine
from sqlalchemy import text

def migrate():
    """Add missing minion profile fields to database tables"""
    try:
        print("🔄 Adding minion profile fields (title, company, theme_color)...")
        
        # Create engine
        engine = create_database_engine()
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Add fields to minions table
                print("  📝 Adding fields to minions table...")
                conn.execute(text("""
                    ALTER TABLE minions ADD COLUMN title TEXT DEFAULT '';
                """))
                conn.execute(text("""
                    ALTER TABLE minions ADD COLUMN company TEXT DEFAULT '';
                """))
                conn.execute(text("""
                    ALTER TABLE minions ADD COLUMN theme_color TEXT DEFAULT '#4f46e5';
                """))
                
                # Add fields to external_api_models table
                print("  📝 Adding fields to external_api_models table...")
                conn.execute(text("""
                    ALTER TABLE external_api_models ADD COLUMN title TEXT DEFAULT '';
                """))
                conn.execute(text("""
                    ALTER TABLE external_api_models ADD COLUMN company TEXT DEFAULT '';
                """))
                conn.execute(text("""
                    ALTER TABLE external_api_models ADD COLUMN theme_color TEXT DEFAULT '#4f46e5';
                """))
                
                # Add fields to reference_models table
                print("  📝 Adding fields to reference_models table...")
                conn.execute(text("""
                    ALTER TABLE reference_models ADD COLUMN title TEXT DEFAULT '';
                """))
                conn.execute(text("""
                    ALTER TABLE reference_models ADD COLUMN company TEXT DEFAULT '';
                """))
                conn.execute(text("""
                    ALTER TABLE reference_models ADD COLUMN theme_color TEXT DEFAULT '#4f46e5';
                """))
                
                # Commit transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                
                # Verify the changes
                print("\n🔍 Verifying changes...")
                result = conn.execute(text("PRAGMA table_info(minions)"))
                columns = [row[1] for row in result.fetchall()]
                
                new_fields = ['title', 'company', 'theme_color']
                for field in new_fields:
                    if field in columns:
                        print(f"  ✅ {field} field added to minions table")
                    else:
                        print(f"  ❌ {field} field missing from minions table")
                
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def rollback():
    """Rollback the migration (remove the added fields)"""
    try:
        print("🔄 Rolling back minion profile fields migration...")
        
        # Create engine
        engine = create_database_engine()
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Note: PostgreSQL doesn't support DROP COLUMN directly
                # This would require recreating the tables, which is complex
                print("⚠️  Rollback not implemented - PostgreSQL doesn't support DROP COLUMN")
                print("   To rollback, you would need to recreate the tables")
                trans.commit()
                return False
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Rollback failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error during rollback: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        success = rollback()
    else:
        success = migrate()
    
    sys.exit(0 if success else 1)
