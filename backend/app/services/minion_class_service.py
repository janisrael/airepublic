"""
Minion Class Service - Extension for Class-Based Spirit Management
Handles minion class assignments, spirit loading, and class-based operations
"""

from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class MinionClass:
    """Data class for minion class definition"""
    id: int
    class_name: str
    class_description: str
    icon: str
    category: str
    unlock_rank: str
    unlock_level: int
    base_spirits: List[int]  # Array of spirit IDs
    spirit_synergies: Dict[str, float]  # JSONB field
    spirit_conflicts: Dict[str, float]  # JSONB field
    net_performance_bonus: float
    specialization: str
    perfect_for: List[str]  # Array of use cases
    tools_count: int
    is_active: bool = True

class MinionClassService:
    """Service for managing minion class operations"""
    
    def __init__(self):
        # Use existing PostgreSQL database connection
        from database.postgres_connection import create_spirit_engine
        self.engine = create_spirit_engine()
        self.Session = sessionmaker(bind=self.engine)
        print("✅ MinionClassService initialized with PostgreSQL connection")
    
    def get_all_classes(self) -> List[MinionClass]:
        """Get all available minion classes"""
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
                
                classes = []
                for row in result:
                    # Handle JSON fields (already parsed by PostgreSQL)
                    spirit_synergies = row[8] if row[8] else {}
                    spirit_conflicts = row[9] if row[9] else {}
                    perfect_for = row[12] if row[12] else []
                    
                    class_def = MinionClass(
                        id=row[0],
                        class_name=row[1],
                        class_description=row[2],
                        icon=row[3],
                        category=row[4],
                        unlock_rank=row[5],
                        unlock_level=row[6],
                        base_spirits=row[7],  # Already an array
                        spirit_synergies=spirit_synergies,
                        spirit_conflicts=spirit_conflicts,
                        net_performance_bonus=float(row[10]),
                        specialization=row[11],
                        perfect_for=perfect_for,
                        tools_count=row[13],
                        is_active=row[14]
                    )
                    classes.append(class_def)
                
                return classes
                
            except Exception as e:
                print(f"❌ Error getting all classes: {e}")
                return []
    
    def get_class_by_name(self, class_name: str) -> Optional[MinionClass]:
        """Get a specific class by name"""
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
                
                # Handle JSON fields (already parsed by PostgreSQL)
                spirit_synergies = row[8] if row[8] else {}
                spirit_conflicts = row[9] if row[9] else {}
                perfect_for = row[12] if row[12] else []
                
                return MinionClass(
                    id=row[0],
                    class_name=row[1],
                    class_description=row[2],
                    icon=row[3],
                    category=row[4],
                    unlock_rank=row[5],
                    unlock_level=row[6],
                    base_spirits=row[7],
                    spirit_synergies=spirit_synergies,
                    spirit_conflicts=spirit_conflicts,
                    net_performance_bonus=float(row[10]),
                    specialization=row[11],
                    perfect_for=perfect_for,
                    tools_count=row[13],
                    is_active=row[14]
                )
                
            except Exception as e:
                print(f"❌ Error getting class {class_name}: {e}")
                return None
    
    def get_available_classes(self, user_rank: str, user_level: int) -> List[MinionClass]:
        """Get classes available for user's rank and level"""
        # Define rank hierarchy for comparison
        rank_hierarchy = {
            "Novice": 1, "Skilled": 2, "Specialist": 3, 
            "Expert": 4, "Master": 5, "Grandmaster": 6, "Autonomous": 7
        }
        
        user_rank_value = rank_hierarchy.get(user_rank, 1)
        
        available_classes = []
        all_classes = self.get_all_classes()
        
        for class_def in all_classes:
            class_rank_value = rank_hierarchy.get(class_def.unlock_rank, 1)
            
            # Check if user meets unlock requirements
            if (class_rank_value <= user_rank_value and 
                class_def.unlock_level <= user_level):
                available_classes.append(class_def)
        
        return available_classes
    
    def can_unlock_class(self, class_name: str, user_rank: str, user_level: int) -> Tuple[bool, str]:
        """Check if user can unlock a specific class"""
        class_def = self.get_class_by_name(class_name)
        if not class_def:
            return False, "Class not found"
        
        # Define rank hierarchy
        rank_hierarchy = {
            "Novice": 1, "Skilled": 2, "Specialist": 3, 
            "Expert": 4, "Master": 5, "Grandmaster": 6, "Autonomous": 7
        }
        
        user_rank_value = rank_hierarchy.get(user_rank, 1)
        class_rank_value = rank_hierarchy.get(class_def.unlock_rank, 1)
        
        if class_rank_value > user_rank_value:
            return False, f"Requires {class_def.unlock_rank} rank (current: {user_rank})"
        
        if class_def.unlock_level > user_level:
            return False, f"Requires level {class_def.unlock_level} (current: {user_level})"
        
        return True, "Class can be unlocked"
    
    def assign_class_to_minion(self, minion_id: int, class_name: str, user_id: int) -> Dict[str, Any]:
        """Assign a class's default spirits to a minion"""
        try:
            # Get class definition
            class_def = self.get_class_by_name(class_name)
            if not class_def:
                return {
                    "success": False,
                    "error": f"Class '{class_name}' not found"
                }
            
            # Check if minion exists and belongs to user
            minion_exists = self._check_minion_exists(minion_id, user_id)
            if not minion_exists:
                return {
                    "success": False,
                    "error": "Minion not found or access denied"
                }
            
            # Check if minion already has a class assigned
            existing_class = self.get_minion_class(minion_id)
            if existing_class:
                return {
                    "success": False,
                    "error": f"Minion already has class '{existing_class.class_name}' assigned"
                }
            
            # Assign spirits to minion
            assigned_spirits = self._assign_spirits_to_minion(minion_id, class_def.base_spirits)
            
            # Update minion with class information
            self._update_minion_class_info(minion_id, class_name)
            
            return {
                "success": True,
                "class": class_name,
                "spirits_assigned": assigned_spirits,
                "synergies": class_def.spirit_synergies,
                "conflicts": class_def.spirit_conflicts,
                "net_performance_bonus": class_def.net_performance_bonus,
                "specialization": class_def.specialization,
                "tools_count": class_def.tools_count
            }
            
        except Exception as e:
            print(f"❌ Error assigning class to minion: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_minion_class(self, minion_id: int) -> Optional[MinionClass]:
        """Get the class assigned to a minion"""
        with self.Session() as session:
            try:
                # Check if minion has a class assigned (we'll add this field to minion table)
                result = session.execute(text("""
                    SELECT class_name FROM external_api_models 
                    WHERE id = :minion_id AND class_name IS NOT NULL
                """), {"minion_id": minion_id})
                
                row = result.fetchone()
                if not row:
                    return None
                
                return self.get_class_by_name(row[0])
                
            except Exception as e:
                print(f"❌ Error getting minion class: {e}")
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
                        sr.name as spirit_name,
                        sr.description as spirit_description,
                        sr.category as spirit_category,
                        sr.tools as spirit_tools
                    FROM minion_spirits ms
                    JOIN spirits_registry sr ON ms.spirit_id = sr.id
                    WHERE ms.minion_id = :minion_id
                    ORDER BY ms.spirit_level DESC, sr.name
                """), {"minion_id": minion_id})
                
                spirits = []
                for row in result:
                    spirits.append({
                        "spirit_id": row[0],
                        "spirit_name": row[3],
                        "spirit_description": row[4],
                        "spirit_category": row[5],
                        "spirit_level": row[1],
                        "spirit_xp": row[2],
                        "spirit_tools": row[6] if row[6] else []
                    })
                
                return spirits
                
            except Exception as e:
                print(f"❌ Error getting minion spirits: {e}")
                return []
    
    def calculate_class_performance_bonus(self, class_name: str) -> float:
        """Calculate the net performance bonus for a class"""
        class_def = self.get_class_by_name(class_name)
        if not class_def:
            return 0.0
        
        return class_def.net_performance_bonus
    
    def get_class_spirit_details(self, class_name: str) -> List[Dict[str, Any]]:
        """Get detailed information about spirits in a class"""
        class_def = self.get_class_by_name(class_name)
        if not class_def:
            return []
        
        with self.Session() as session:
            try:
                # Convert spirit IDs to string for SQL IN clause
                spirit_ids = [str(spirit_id) for spirit_id in class_def.base_spirits]
                spirit_ids_str = ','.join(spirit_ids)
                
                result = session.execute(text(f"""
                    SELECT 
                        id, name, description, category, tools, unlock_rank, unlock_level
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
                        "unlock_rank": row[5],
                        "unlock_level": row[6]
                    })
                
                return spirits
                
            except Exception as e:
                print(f"❌ Error getting class spirit details: {e}")
                return []
    
    # Private helper methods
    def _check_minion_exists(self, minion_id: int, user_id: int) -> bool:
        """Check if minion exists and belongs to user"""
        with self.Session() as session:
            try:
                result = session.execute(text("""
                    SELECT COUNT(*) FROM external_api_models 
                    WHERE id = :minion_id AND user_id = :user_id AND is_active = true
                """), {"minion_id": minion_id, "user_id": user_id})
                
                return result.fetchone()[0] > 0
                
            except Exception as e:
                print(f"❌ Error checking minion existence: {e}")
                return False
    
    def _assign_spirits_to_minion(self, minion_id: int, spirit_ids: List[int]) -> List[Dict[str, Any]]:
        """Assign spirits to minion in minion_spirits table"""
        with self.Session() as session:
            try:
                assigned_spirits = []
                
                for spirit_id in spirit_ids:
                    # Check if spirit is already assigned
                    existing = session.execute(text("""
                        SELECT COUNT(*) FROM minion_spirits 
                        WHERE minion_id = :minion_id AND spirit_id = :spirit_id
                    """), {"minion_id": minion_id, "spirit_id": spirit_id})
                    
                    if existing.fetchone()[0] == 0:
                        # Assign spirit with initial level 1
                        session.execute(text("""
                            INSERT INTO minion_spirits (minion_id, spirit_id, spirit_level, spirit_xp, created_at, updated_at)
                            VALUES (:minion_id, :spirit_id, 1, 0, :created_at, :updated_at)
                        """), {
                            "minion_id": minion_id,
                            "spirit_id": spirit_id,
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        })
                        
                        assigned_spirits.append({
                            "spirit_id": spirit_id,
                            "spirit_level": 1,
                            "spirit_xp": 0
                        })
                
                session.commit()
                return assigned_spirits
                
            except Exception as e:
                session.rollback()
                print(f"❌ Error assigning spirits to minion: {e}")
                return []
    
    def _update_minion_class_info(self, minion_id: int, class_name: str) -> bool:
        """Update minion with class information"""
        with self.Session() as session:
            try:
                # First, check if class_name column exists, if not, we'll add it later
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
                print(f"❌ Error updating minion class info: {e}")
                # If column doesn't exist, we'll handle it in the migration
                return False
