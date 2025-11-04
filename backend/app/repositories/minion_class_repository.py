"""
Minion Class Repository - Database operations for minion classes
Extends existing repository pattern without modifying working code
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

class MinionClassRepository:
    """Repository for minion class database operations"""
    
    def __init__(self):
        # Use existing PostgreSQL database connection
        from database.postgres_connection import create_spirit_engine
        self.engine = create_spirit_engine()
        self.Session = sessionmaker(bind=self.engine)
        print("✅ MinionClassRepository initialized with PostgreSQL connection")
    
    def get_class_by_id(self, class_id: int) -> Optional[Dict[str, Any]]:
        """Get class by ID"""
        with self.Session() as session:
            try:
                result = session.execute(text("""
                    SELECT 
                        id, class_name, class_description, icon, category,
                        unlock_rank, unlock_level, base_spirits,
                        spirit_synergies, spirit_conflicts, net_performance_bonus,
                        specialization, perfect_for, tools_count, is_active,
                        created_at, updated_at
                    FROM minion_classes 
                    WHERE id = :class_id
                """), {"class_id": class_id})
                
                row = result.fetchone()
                if not row:
                    return None
                
                return {
                    "id": row[0],
                    "class_name": row[1],
                    "class_description": row[2],
                    "icon": row[3],
                    "category": row[4],
                    "unlock_rank": row[5],
                    "unlock_level": row[6],
                    "base_spirits": row[7],
                    "spirit_synergies": json.loads(row[8]) if row[8] else {},
                    "spirit_conflicts": json.loads(row[9]) if row[9] else {},
                    "net_performance_bonus": float(row[10]),
                    "specialization": row[11],
                    "perfect_for": row[12] if row[12] else [],
                    "tools_count": row[13],
                    "is_active": row[14],
                    "created_at": row[15],
                    "updated_at": row[16]
                }
                
            except Exception as e:
                print(f"❌ Error getting class by ID {class_id}: {e}")
                return None
    
    def get_classes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get classes by category"""
        with self.Session() as session:
            try:
                result = session.execute(text("""
                    SELECT 
                        id, class_name, class_description, icon, category,
                        unlock_rank, unlock_level, base_spirits,
                        spirit_synergies, spirit_conflicts, net_performance_bonus,
                        specialization, perfect_for, tools_count, is_active
                    FROM minion_classes 
                    WHERE category = :category AND is_active = true
                    ORDER BY class_name
                """), {"category": category})
                
                classes = []
                for row in result:
                    classes.append({
                        "id": row[0],
                        "class_name": row[1],
                        "class_description": row[2],
                        "icon": row[3],
                        "category": row[4],
                        "unlock_rank": row[5],
                        "unlock_level": row[6],
                        "base_spirits": row[7],
                        "spirit_synergies": json.loads(row[8]) if row[8] else {},
                        "spirit_conflicts": json.loads(row[9]) if row[9] else {},
                        "net_performance_bonus": float(row[10]),
                        "specialization": row[11],
                        "perfect_for": row[12] if row[12] else [],
                        "tools_count": row[13],
                        "is_active": row[14]
                    })
                
                return classes
                
            except Exception as e:
                print(f"❌ Error getting classes by category {category}: {e}")
                return []
    
    def get_classes_by_unlock_requirements(self, rank: str, level: int) -> List[Dict[str, Any]]:
        """Get classes that can be unlocked by user's rank and level"""
        # Define rank hierarchy for comparison
        rank_hierarchy = {
            "Novice": 1, "Skilled": 2, "Specialist": 3, 
            "Expert": 4, "Master": 5, "Grandmaster": 6, "Autonomous": 7
        }
        
        user_rank_value = rank_hierarchy.get(rank, 1)
        
        with self.Session() as session:
            try:
                result = session.execute(text("""
                    SELECT 
                        id, class_name, class_description, icon, category,
                        unlock_rank, unlock_level, base_spirits,
                        spirit_synergies, spirit_conflicts, net_performance_bonus,
                        specialization, perfect_for, tools_count, is_active
                    FROM minion_classes 
                    WHERE is_active = true
                    ORDER BY category, class_name
                """))
                
                available_classes = []
                for row in result:
                    class_rank_value = rank_hierarchy.get(row[5], 1)
                    
                    # Check if user meets unlock requirements
                    if (class_rank_value <= user_rank_value and 
                        row[6] <= level):
                        available_classes.append({
                            "id": row[0],
                            "class_name": row[1],
                            "class_description": row[2],
                            "icon": row[3],
                            "category": row[4],
                            "unlock_rank": row[5],
                            "unlock_level": row[6],
                            "base_spirits": row[7],
                            "spirit_synergies": json.loads(row[8]) if row[8] else {},
                            "spirit_conflicts": json.loads(row[9]) if row[9] else {},
                            "net_performance_bonus": float(row[10]),
                            "specialization": row[11],
                            "perfect_for": row[12] if row[12] else [],
                            "tools_count": row[13],
                            "is_active": row[14]
                        })
                
                return available_classes
                
            except Exception as e:
                print(f"❌ Error getting classes by unlock requirements: {e}")
                return []
    
    def get_minion_class_assignment(self, minion_id: int) -> Optional[Dict[str, Any]]:
        """Get the class assigned to a minion"""
        with self.Session() as session:
            try:
                result = session.execute(text("""
                    SELECT class_name FROM external_api_models 
                    WHERE id = :minion_id AND class_name IS NOT NULL
                """), {"minion_id": minion_id})
                
                row = result.fetchone()
                if not row:
                    return None
                
                # Get full class details
                class_name = row[0]
                return self.get_class_by_name(class_name)
                
            except Exception as e:
                print(f"❌ Error getting minion class assignment: {e}")
                return None
    
    def get_class_by_name(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get class by name"""
        with self.Session() as session:
            try:
                result = session.execute(text("""
                    SELECT 
                        id, class_name, class_description, icon, category,
                        unlock_rank, unlock_level, base_spirits,
                        spirit_synergies, spirit_conflicts, net_performance_bonus,
                        specialization, perfect_for, tools_count, is_active
                    FROM minion_classes 
                    WHERE class_name = :class_name AND is_active = true
                """), {"class_name": class_name})
                
                row = result.fetchone()
                if not row:
                    return None
                
                return {
                    "id": row[0],
                    "class_name": row[1],
                    "class_description": row[2],
                    "icon": row[3],
                    "category": row[4],
                    "unlock_rank": row[5],
                    "unlock_level": row[6],
                    "base_spirits": row[7],
                    "spirit_synergies": json.loads(row[8]) if row[8] else {},
                    "spirit_conflicts": json.loads(row[9]) if row[9] else {},
                    "net_performance_bonus": float(row[10]),
                    "specialization": row[11],
                    "perfect_for": row[12] if row[12] else [],
                    "tools_count": row[13],
                    "is_active": row[14]
                }
                
            except Exception as e:
                print(f"❌ Error getting class by name {class_name}: {e}")
                return None
    
    def get_minion_spirits(self, minion_id: int) -> List[Dict[str, Any]]:
        """Get all spirits assigned to a minion"""
        with self.Session() as session:
            try:
                result = session.execute(text("""
                    SELECT 
                        ms.spirit_id,
                        ms.spirit_level,
                        ms.spirit_xp,
                        ms.created_at,
                        ms.updated_at,
                        sr.name as spirit_name,
                        sr.description as spirit_description,
                        sr.category as spirit_category,
                        sr.tools as spirit_tools,
                        sr.unlock_requirements as spirit_unlock_requirements
                    FROM minion_spirits ms
                    JOIN spirits_registry sr ON ms.spirit_id = sr.id
                    WHERE ms.minion_id = :minion_id
                    ORDER BY ms.spirit_level DESC, sr.name
                """), {"minion_id": minion_id})
                
                spirits = []
                for row in result:
                    spirits.append({
                        "spirit_id": row[0],
                        "spirit_level": row[1],
                        "spirit_xp": row[2],
                        "assigned_at": row[3],
                        "updated_at": row[4],
                        "spirit_name": row[5],
                        "spirit_description": row[6],
                        "spirit_category": row[7],
                        "spirit_tools": row[8] if row[8] else [],
                        "spirit_unlock_requirements": row[9] if row[9] else {}
                    })
                
                return spirits
                
            except Exception as e:
                print(f"❌ Error getting minion spirits: {e}")
                return []
    
    def assign_spirit_to_minion(self, minion_id: int, spirit_id: int, level: int = 1, xp: int = 0) -> bool:
        """Assign a spirit to a minion"""
        with self.Session() as session:
            try:
                # Check if spirit is already assigned
                existing = session.execute(text("""
                    SELECT COUNT(*) FROM minion_spirits 
                    WHERE minion_id = :minion_id AND spirit_id = :spirit_id
                """), {"minion_id": minion_id, "spirit_id": spirit_id})
                
                if existing.fetchone()[0] > 0:
                    # Update existing assignment
                    session.execute(text("""
                        UPDATE minion_spirits 
                        SET spirit_level = :level, spirit_xp = :xp, updated_at = :updated_at
                        WHERE minion_id = :minion_id AND spirit_id = :spirit_id
                    """), {
                        "minion_id": minion_id,
                        "spirit_id": spirit_id,
                        "level": level,
                        "xp": xp,
                        "updated_at": datetime.now()
                    })
                else:
                    # Create new assignment
                    session.execute(text("""
                        INSERT INTO minion_spirits (minion_id, spirit_id, spirit_level, spirit_xp, created_at, updated_at)
                        VALUES (:minion_id, :spirit_id, :level, :xp, :created_at, :updated_at)
                    """), {
                        "minion_id": minion_id,
                        "spirit_id": spirit_id,
                        "level": level,
                        "xp": xp,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    })
                
                session.commit()
                return True
                
            except Exception as e:
                session.rollback()
                print(f"❌ Error assigning spirit to minion: {e}")
                return False
    
    def remove_spirit_from_minion(self, minion_id: int, spirit_id: int) -> bool:
        """Remove a spirit from a minion"""
        with self.Session() as session:
            try:
                session.execute(text("""
                    DELETE FROM minion_spirits 
                    WHERE minion_id = :minion_id AND spirit_id = :spirit_id
                """), {"minion_id": minion_id, "spirit_id": spirit_id})
                
                session.commit()
                return True
                
            except Exception as e:
                session.rollback()
                print(f"❌ Error removing spirit from minion: {e}")
                return False
    
    def update_minion_class(self, minion_id: int, class_name: str) -> bool:
        """Update minion's assigned class"""
        with self.Session() as session:
            try:
                session.execute(text("""
                    UPDATE external_api_models 
                    SET class_name = :class_name, updated_at = :updated_at
                    WHERE id = :minion_id
                """), {
                    "minion_id": minion_id,
                    "class_name": class_name,
                    "updated_at": datetime.now()
                })
                
                session.commit()
                return True
                
            except Exception as e:
                session.rollback()
                print(f"❌ Error updating minion class: {e}")
                return False
    
    def get_spirit_details(self, spirit_ids: List[int]) -> List[Dict[str, Any]]:
        """Get detailed information about spirits"""
        if not spirit_ids:
            return []
        
        with self.Session() as session:
            try:
                # Convert spirit IDs to string for SQL IN clause
                spirit_ids_str = ','.join([str(spirit_id) for spirit_id in spirit_ids])
                
                result = session.execute(text(f"""
                    SELECT 
                        id, name, description, category, tools, unlock_requirements,
                        base_performance, synergy_bonuses, conflict_penalties
                    FROM spirits_registry 
                    WHERE id IN ({spirit_ids_str})
                    ORDER BY name
                """))
                
                spirits = []
                for row in result:
                    spirits.append({
                        "spirit_id": row[0],
                        "spirit_name": row[1],
                        "spirit_description": row[2],
                        "spirit_category": row[3],
                        "spirit_tools": row[4] if row[4] else [],
                        "spirit_unlock_requirements": row[5] if row[5] else {},
                        "base_performance": float(row[6]) if row[6] else 0.0,
                        "synergy_bonuses": row[7] if row[7] else {},
                        "conflict_penalties": row[8] if row[8] else {}
                    })
                
                return spirits
                
            except Exception as e:
                print(f"❌ Error getting spirit details: {e}")
                return []
    
    def get_class_statistics(self) -> Dict[str, Any]:
        """Get statistics about class usage"""
        with self.Session() as session:
            try:
                # Get total classes
                total_classes = session.execute(text("""
                    SELECT COUNT(*) FROM minion_classes WHERE is_active = true
                """)).fetchone()[0]
                
                # Get classes by category
                categories = session.execute(text("""
                    SELECT category, COUNT(*) as count
                    FROM minion_classes 
                    WHERE is_active = true
                    GROUP BY category
                    ORDER BY count DESC
                """)).fetchall()
                
                # Get classes by unlock rank
                ranks = session.execute(text("""
                    SELECT unlock_rank, COUNT(*) as count
                    FROM minion_classes 
                    WHERE is_active = true
                    GROUP BY unlock_rank
                    ORDER BY unlock_rank
                """)).fetchall()
                
                # Get minions with classes assigned
                minions_with_classes = session.execute(text("""
                    SELECT COUNT(*) FROM external_api_models 
                    WHERE class_name IS NOT NULL
                """)).fetchone()[0]
                
                return {
                    "total_classes": total_classes,
                    "categories": [{"category": row[0], "count": row[1]} for row in categories],
                    "unlock_ranks": [{"rank": row[0], "count": row[1]} for row in ranks],
                    "minions_with_classes": minions_with_classes
                }
                
            except Exception as e:
                print(f"❌ Error getting class statistics: {e}")
                return {
                    "total_classes": 0,
                    "categories": [],
                    "unlock_ranks": [],
                    "minions_with_classes": 0
                }
