#!/usr/bin/env python3
"""
Migration: Create Minion Classes Table
Creates the minion_classes table for pre-configured spirit pathways
"""

import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.postgres_connection import create_spirit_engine
from sqlalchemy import text

def create_minion_classes_table():
    """Create the minion_classes table"""
    try:
        print("🔧 Creating minion_classes table...")
        
        # Create engine
        engine = create_spirit_engine()
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Create minion_classes table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS minion_classes (
                        id SERIAL PRIMARY KEY,
                        class_name TEXT NOT NULL UNIQUE,
                        class_description TEXT,
                        icon TEXT,
                        category TEXT NOT NULL,
                        unlock_rank TEXT DEFAULT 'Novice',
                        unlock_level INTEGER DEFAULT 1,
                        base_spirits INTEGER[] NOT NULL, -- Array of spirit IDs
                        spirit_synergies JSONB DEFAULT '{}',
                        spirit_conflicts JSONB DEFAULT '{}',
                        net_performance_bonus DECIMAL(5,2) DEFAULT 0.00,
                        specialization TEXT,
                        perfect_for TEXT[],
                        tools_count INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create index for faster queries
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_minion_classes_category 
                    ON minion_classes(category);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_minion_classes_unlock 
                    ON minion_classes(unlock_rank, unlock_level);
                """))
                
                # Commit transaction
                trans.commit()
                
                print("✅ minion_classes table created successfully!")
                
                # Seed initial classes
                seed_minion_classes(conn)
                
                return True
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        print(f"❌ Error creating minion_classes table: {e}")
        return False

def seed_minion_classes(conn):
    """Seed initial minion classes"""
    try:
        print("🌱 Seeding minion classes...")
        
        # First, get spirit IDs from spirits_registry
        spirit_ids = {}
        result = conn.execute(text("SELECT id, name FROM spirits_registry"))
        for row in result:
            spirit_ids[row[1]] = row[0]
        
        print(f"Found {len(spirit_ids)} spirits in registry")
        
        # Define minion classes with spirit IDs
        classes = [
            {
                "class_name": "Planner",
                "class_description": "Strategic planning specialist focused on breaking down complex challenges and delivering actionable solutions",
                "icon": "🧠",
                "category": "Development & Technical",
                "unlock_rank": "Novice",
                "unlock_level": 1,
                "base_spirits": [spirit_ids.get("Analyst Spirit", 4), spirit_ids.get("Writer Spirit", 1), spirit_ids.get("Researcher Spirit", 5)],
                "spirit_synergies": {"analyst_researcher": 0.30, "writer_analyst": 0.15},
                "spirit_conflicts": {},
                "net_performance_bonus": 0.45,
                "specialization": "Strategic planning and problem-solving",
                "perfect_for": ["Project planning", "Strategic analysis", "Research projects"],
                "tools_count": 15
            },
            {
                "class_name": "Developer",
                "class_description": "Full-stack development specialist with security focus and code quality assurance",
                "icon": "💻",
                "category": "Development & Technical",
                "unlock_rank": "Novice",
                "unlock_level": 1,
                "base_spirits": [spirit_ids.get("Builder Spirit", 7), spirit_ids.get("Debugger Spirit", 8), spirit_ids.get("Checker Spirit", 13)],
                "spirit_synergies": {"builder_debugger": 0.20, "debugger_checker": 0.20},
                "spirit_conflicts": {},
                "net_performance_bonus": 0.40,
                "specialization": "Full-stack development with security focus",
                "perfect_for": ["Software development", "Code generation", "Debugging"],
                "tools_count": 18
            },
            {
                "class_name": "Creative Assistant",
                "class_description": "Content creation and storytelling specialist with artistic capabilities",
                "icon": "🎨",
                "category": "Content & Creative",
                "unlock_rank": "Novice",
                "unlock_level": 1,
                "base_spirits": [spirit_ids.get("Writer Spirit", 1), spirit_ids.get("Creative Spirit", 2), spirit_ids.get("Designer Spirit", 16)],
                "spirit_synergies": {"writer_creative": 0.25, "creative_designer": 0.30},
                "spirit_conflicts": {},
                "net_performance_bonus": 0.55,
                "specialization": "Content creation and artistic design",
                "perfect_for": ["Content marketing", "Creative writing", "Visual design"],
                "tools_count": 14
            },
            {
                "class_name": "Data Scientist",
                "class_description": "Advanced data analysis and machine learning specialist",
                "icon": "📊",
                "category": "Data & Analysis",
                "unlock_rank": "Skilled",
                "unlock_level": 3,
                "base_spirits": [spirit_ids.get("Mathematician Spirit", 6), spirit_ids.get("Analyst Spirit", 4), spirit_ids.get("Researcher Spirit", 5)],
                "spirit_synergies": {"mathematician_analyst": 0.35, "analyst_researcher": 0.30},
                "spirit_conflicts": {},
                "net_performance_bonus": 0.65,
                "specialization": "Advanced data analysis and machine learning",
                "perfect_for": ["Machine learning", "Statistical analysis", "Data engineering"],
                "tools_count": 20
            },
            {
                "class_name": "API Integration Specialist",
                "class_description": "System integration and API connectivity specialist",
                "icon": "🌐",
                "category": "Integration & Automation",
                "unlock_rank": "Skilled",
                "unlock_level": 2,
                "base_spirits": [spirit_ids.get("Connector Spirit", 10), spirit_ids.get("Builder Spirit", 7), spirit_ids.get("Debugger Spirit", 8)],
                "spirit_synergies": {"connector_builder": 0.25, "builder_debugger": 0.20},
                "spirit_conflicts": {},
                "net_performance_bonus": 0.45,
                "specialization": "System integration and API connectivity",
                "perfect_for": ["System integration", "API development", "Microservices"],
                "tools_count": 17
            },
            {
                "class_name": "Security Specialist",
                "class_description": "Cybersecurity and vulnerability assessment specialist",
                "icon": "🔒",
                "category": "Quality & Security",
                "unlock_rank": "Specialist",
                "unlock_level": 2,
                "base_spirits": [spirit_ids.get("Security Spirit", 14), spirit_ids.get("Analyst Spirit", 4), spirit_ids.get("Debugger Spirit", 8)],
                "spirit_synergies": {"security_analyst": 0.25, "debugger_security": 0.20},
                "spirit_conflicts": {},
                "net_performance_bonus": 0.45,
                "specialization": "Cybersecurity and vulnerability assessment",
                "perfect_for": ["Cybersecurity", "Penetration testing", "Security auditing"],
                "tools_count": 19
            },
            {
                "class_name": "Swiss Army Knife",
                "class_description": "General-purpose problem solving with diverse capabilities",
                "icon": "🔧",
                "category": "Hybrid & Versatile",
                "unlock_rank": "Novice",
                "unlock_level": 1,
                "base_spirits": [spirit_ids.get("Builder Spirit", 7), spirit_ids.get("Writer Spirit", 1), spirit_ids.get("Analyst Spirit", 4)],
                "spirit_synergies": {"builder_analyst": 0.20, "writer_analyst": 0.15},
                "spirit_conflicts": {},
                "net_performance_bonus": 0.35,
                "specialization": "General-purpose problem solving",
                "perfect_for": ["General assistance", "Prototyping", "Multi-task projects"],
                "tools_count": 20
            }
        ]
        
        # Insert classes
        for cls in classes:
            # Convert dicts to JSON strings for PostgreSQL
            cls_data = cls.copy()
            cls_data['spirit_synergies'] = json.dumps(cls['spirit_synergies'])
            cls_data['spirit_conflicts'] = json.dumps(cls['spirit_conflicts'])
            cls_data['perfect_for'] = cls['perfect_for']  # Already a list, PostgreSQL handles it
            
            conn.execute(text("""
                INSERT INTO minion_classes (
                    class_name, class_description, icon, category, unlock_rank, unlock_level,
                    base_spirits, spirit_synergies, spirit_conflicts, net_performance_bonus,
                    specialization, perfect_for, tools_count
                ) VALUES (
                    :class_name, :class_description, :icon, :category, :unlock_rank, :unlock_level,
                    :base_spirits, :spirit_synergies, :spirit_conflicts, :net_performance_bonus,
                    :specialization, :perfect_for, :tools_count
                ) ON CONFLICT (class_name) DO NOTHING
            """), cls_data)
        
        print(f"✅ Seeded {len(classes)} minion classes!")
        
    except Exception as e:
        print(f"❌ Error seeding minion classes: {e}")
        raise e

if __name__ == "__main__":
    success = create_minion_classes_table()
    if success:
        print("\n🎉 Minion Classes Table Created Successfully!")
        print("📊 Available Classes:")
        print("   - Planner (Development & Technical)")
        print("   - Developer (Development & Technical)")
        print("   - Creative Assistant (Content & Creative)")
        print("   - Data Scientist (Data & Analysis)")
        print("   - API Integration Specialist (Integration & Automation)")
        print("   - Security Specialist (Quality & Security)")
        print("   - Swiss Army Knife (Hybrid & Versatile)")
    else:
        print("\n❌ Failed to create minion classes table")
        sys.exit(1)
