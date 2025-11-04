#!/usr/bin/env python3
"""
Fix duplicate display names for minions
Makes display names unique per user by appending numbers
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.postgres_connection import create_spirit_engine
from collections import Counter

def fix_duplicate_display_names():
    """Fix duplicate display names by making them unique"""
    engine = create_spirit_engine()
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        try:
            # Get all minions grouped by user_id and display_name
            result = session.execute(text("""
                SELECT user_id, display_name, COUNT(*) as count, 
                       array_agg(id ORDER BY id) as ids
                FROM external_api_models
                WHERE is_active = true
                GROUP BY user_id, display_name
                HAVING COUNT(*) > 1
                ORDER BY user_id, display_name
            """))
            
            duplicates = result.fetchall()
            
            if not duplicates:
                print("✅ No duplicate display names found!")
                return
            
            print(f"📊 Found {len(duplicates)} sets of duplicate display names\n")
            
            total_fixed = 0
            for row in duplicates:
                user_id, display_name, count, ids = row
                print(f"👤 User {user_id}: '{display_name}' ({count} duplicates, IDs: {ids})")
                
                # Keep the first one (oldest by ID), rename the rest
                ids_list = ids if isinstance(ids, list) else [ids]
                ids_list.sort()  # Ensure sorted by ID
                
                for idx, minion_id in enumerate(ids_list[1:], start=2):
                    new_name = f"{display_name} ({idx})"
                    
                    # Check if new name already exists
                    check_result = session.execute(
                        text("""
                            SELECT COUNT(*) FROM external_api_models
                            WHERE user_id = :user_id 
                            AND display_name = :new_name
                            AND is_active = true
                        """),
                        {"user_id": user_id, "new_name": new_name}
                    )
                    exists_count = check_result.scalar()
                    
                    # If new name exists, keep incrementing
                    if exists_count > 0:
                        counter = 2
                        while True:
                            test_name = f"{display_name} ({counter})"
                            check_result = session.execute(
                                text("""
                                    SELECT COUNT(*) FROM external_api_models
                                    WHERE user_id = :user_id 
                                    AND display_name = :test_name
                                    AND is_active = true
                                """),
                                {"user_id": user_id, "test_name": test_name}
                            )
                            if check_result.scalar() == 0:
                                new_name = test_name
                                break
                            counter += 1
                    
                    # Update the minion
                    session.execute(
                        text("""
                            UPDATE external_api_models
                            SET display_name = :new_name
                            WHERE id = :minion_id
                        """),
                        {"new_name": new_name, "minion_id": minion_id}
                    )
                    print(f"   ✅ ID {minion_id}: '{display_name}' → '{new_name}'")
                    total_fixed += 1
                
                print()
            
            session.commit()
            print(f"✅ Fixed {total_fixed} duplicate display names!")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error fixing duplicates: {e}")
            raise

def remove_test_minions(user_id=2, test_names=None):
    """Remove test/fallback minions"""
    if test_names is None:
        test_names = ['Grafana', 'Agimat']
    
    engine = create_spirit_engine()
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        try:
            print(f"🗑️  Removing test minions for user {user_id}...")
            
            # Find test minions
            placeholders = ','.join([f"'{name}'" for name in test_names])
            result = session.execute(text(f"""
                SELECT id, display_name, name, created_at
                FROM external_api_models
                WHERE user_id = :user_id
                AND display_name IN ({placeholders})
                AND is_active = true
                ORDER BY id
            """), {"user_id": user_id})
            
            test_minions = result.fetchall()
            
            if not test_minions:
                print("✅ No test minions found!")
                return
            
            print(f"📊 Found {len(test_minions)} test minions:\n")
            for minion in test_minions:
                print(f"   ID {minion[0]}: {minion[1]} ({minion[2]}) - Created: {minion[3]}")
            
            # Confirm deletion
            print(f"\n⚠️  This will delete {len(test_minions)} minions!")
            confirm = input("Type 'DELETE' to confirm: ")
            
            if confirm != 'DELETE':
                print("❌ Deletion cancelled")
                return
            
            # Delete test minions
            for minion in test_minions:
                session.execute(
                    text("DELETE FROM external_api_models WHERE id = :id"),
                    {"id": minion[0]}
                )
                print(f"   ✅ Deleted ID {minion[0]}: {minion[1]}")
            
            session.commit()
            print(f"\n✅ Removed {len(test_minions)} test minions!")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error removing test minions: {e}")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix duplicate display names or remove test minions')
    parser.add_argument('--fix-duplicates', action='store_true', help='Fix duplicate display names')
    parser.add_argument('--remove-test', action='store_true', help='Remove test minions')
    parser.add_argument('--user-id', type=int, default=2, help='User ID for test minion removal')
    
    args = parser.parse_args()
    
    if args.fix_duplicates:
        fix_duplicate_display_names()
    elif args.remove_test:
        remove_test_minions(user_id=args.user_id)
    else:
        print("Usage:")
        print("  python fix_duplicate_display_names.py --fix-duplicates  # Fix duplicates")
        print("  python fix_duplicate_display_names.py --remove-test      # Remove test minions")

