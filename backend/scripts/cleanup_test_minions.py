#!/usr/bin/env python3
"""
Cleanup script to remove test/non-working minions from the database.
Retains only working minions (User 2: Agimat, Grafana, Grafana (2), Grafana (3))
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

def cleanup_test_minions():
    """Remove test/non-working minions from database"""
    
    engine = create_spirit_engine()
    Session = sessionmaker(bind=engine)
    
    # IDs of test/non-working minions to remove
    test_minion_ids = [1, 2, 3, 4, 5, 20, 21]
    
    # Working minions to retain (User 2)
    working_minion_ids = [17, 18, 19, 22]  # Grafana, Grafana (2), Grafana (3), Agimat
    
    with Session() as session:
        try:
            # First, check what we're about to delete
            result = session.execute(text("""
                SELECT id, display_name, user_id, is_active
                FROM external_api_models
                WHERE id IN :ids
            """), {'ids': tuple(test_minion_ids)})
            
            minions_to_delete = result.fetchall()
            
            print("=" * 80)
            print("CLEANUP: Removing Test/Non-Working Minions")
            print("=" * 80)
            print(f"\nMinions to be deleted ({len(minions_to_delete)}):")
            for row in minions_to_delete:
                print(f"  ID {row[0]}: {row[1]} (User {row[2]}, Active: {row[3]})")
            
            # Verify working minions exist
            result = session.execute(text("""
                SELECT id, display_name, user_id
                FROM external_api_models
                WHERE id IN :ids
            """), {'ids': tuple(working_minion_ids)})
            
            working_minions = result.fetchall()
            print(f"\nWorking minions to retain ({len(working_minions)}):")
            for row in working_minions:
                print(f"  ID {row[0]}: {row[1]} (User {row[2]})")
            
            # Confirm deletion
            print("\n" + "=" * 80)
            response = input(f"\nDelete {len(minions_to_delete)} test minions? (yes/no): ").strip().lower()
            
            if response != 'yes':
                print("❌ Cleanup cancelled.")
                return
            
            # Delete test minions (CASCADE will handle related records)
            deleted_count = session.execute(text("""
                DELETE FROM external_api_models
                WHERE id IN :ids
            """), {'ids': tuple(test_minion_ids)})
            
            session.commit()
            
            print(f"\n✅ Successfully deleted {deleted_count.rowcount} test minions.")
            print(f"✅ Retained {len(working_minions)} working minions.")
            
            # Show remaining minions
            result = session.execute(text("""
                SELECT id, display_name, user_id, provider
                FROM external_api_models
                ORDER BY id
            """))
            
            remaining = result.fetchall()
            print(f"\nRemaining minions in database ({len(remaining)}):")
            for row in remaining:
                print(f"  ID {row[0]}: {row[1]} (User {row[2]}, Provider: {row[3]})")
            
        except Exception as e:
            session.rollback()
            print(f"\n❌ Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            session.close()

if __name__ == '__main__':
    cleanup_test_minions()
