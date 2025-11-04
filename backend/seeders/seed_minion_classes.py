#!/usr/bin/env python3
"""
Seeder: Populate Minion Classes
Seeds the minion_classes table with pre-configured spirit pathways
"""

import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.postgres_connection import create_spirit_engine
from sqlalchemy import text

def seed_minion_classes():
    """Seed minion classes with spirit assignments"""
    try:
        print("🌱 Seeding minion classes...")
        
        # Create engine
        engine = create_spirit_engine()
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Get spirit IDs from spirits_registry
                spirit_ids = {}
                result = conn.execute(text("SELECT id, name FROM spirits_registry"))
                for row in result:
                    spirit_ids[row[1]] = row[0]
                
                print(f"Found {len(spirit_ids)} spirits in registry")
                
                # Define minion classes
                classes = [
                    {
                        "class_name": "Planner",
                        "class_description": "Strategic planning specialist focused on breaking down complex challenges and delivering actionable solutions",
                        "category": "Development & Technical",
                        "icon": "🧠",
                        "unlock_rank": "Novice",
                        "unlock_level": 1,
                        "base_spirits": [spirit_ids.get("Analyst Spirit", 4), spirit_ids.get("Writer Spirit", 1), spirit_ids.get("Researcher Spirit", 5)],
                        "spirit_synergies": json.dumps({"analyst_researcher": 0.30, "writer_analyst": 0.15}),
                        "spirit_conflicts": json.dumps({}),
                        "net_performance_bonus": 0.45,
                        "specialization": "Strategic planning and problem-solving",
                        "perfect_for": ["Project planning", "Strategic analysis", "Research projects"],
                        "tools_count": 15
                    },
                    {
                        "class_name": "Developer",
                        "class_description": "Full-stack development specialist with security focus and code quality assurance",
                        "category": "Development & Technical",
                        "icon": "💻",
                        "unlock_rank": "Novice",
                        "unlock_level": 1,
                        "base_spirits": [spirit_ids.get("Builder Spirit", 7), spirit_ids.get("Debugger Spirit", 8), spirit_ids.get("Checker Spirit", 13)],
                        "spirit_synergies": json.dumps({"builder_debugger": 0.20, "debugger_checker": 0.20}),
                        "spirit_conflicts": json.dumps({}),
                        "net_performance_bonus": 0.40,
                        "specialization": "Full-stack development with security focus",
                        "perfect_for": ["Software development", "Code generation", "Debugging"],
                        "tools_count": 18
                    },
                    {
                        "class_name": "Creative Assistant",
                        "class_description": "Content creation and storytelling specialist with artistic capabilities",
                        "category": "Content & Creative",
                        "icon": "🎨",
                        "unlock_rank": "Novice",
                        "unlock_level": 1,
                        "base_spirits": [spirit_ids.get("Writer Spirit", 1), spirit_ids.get("Creative Spirit", 2), spirit_ids.get("Designer Spirit", 16)],
                        "spirit_synergies": json.dumps({"writer_creative": 0.25, "creative_designer": 0.30}),
                        "spirit_conflicts": json.dumps({}),
                        "net_performance_bonus": 0.55,
                        "specialization": "Content creation and artistic design",
                        "perfect_for": ["Content marketing", "Creative writing", "Visual design"],
                        "tools_count": 14
                    },
                    {
                        "class_name": "Data Scientist",
                        "class_description": "Advanced data analysis and machine learning specialist",
                        "category": "Data & Analysis",
                        "icon": "📊",
                        "unlock_rank": "Skilled",
                        "unlock_level": 3,
                        "base_spirits": [spirit_ids.get("Mathematician Spirit", 6), spirit_ids.get("Analyst Spirit", 4), spirit_ids.get("Researcher Spirit", 5)],
                        "spirit_synergies": json.dumps({"mathematician_analyst": 0.35, "analyst_researcher": 0.30}),
                        "spirit_conflicts": json.dumps({}),
                        "net_performance_bonus": 0.65,
                        "specialization": "Advanced data analysis and machine learning",
                        "perfect_for": ["Machine learning", "Statistical analysis", "Data engineering"],
                        "tools_count": 20
                    },
                    {
                        "class_name": "API Integration Specialist",
                        "class_description": "System integration and API connectivity specialist",
                        "category": "Integration & Automation",
                        "icon": "🌐",
                        "unlock_rank": "Skilled",
                        "unlock_level": 2,
                        "base_spirits": [spirit_ids.get("Connector Spirit", 10), spirit_ids.get("Builder Spirit", 7), spirit_ids.get("Debugger Spirit", 8)],
                        "spirit_synergies": json.dumps({"connector_builder": 0.25, "builder_debugger": 0.20}),
                        "spirit_conflicts": json.dumps({}),
                        "net_performance_bonus": 0.45,
                        "specialization": "System integration and API connectivity",
                        "perfect_for": ["System integration", "API development", "Microservices"],
                        "tools_count": 17
                    },
                    {
                        "class_name": "Security Specialist",
                        "class_description": "Cybersecurity and vulnerability assessment specialist",
                        "category": "Quality & Security",
                        "icon": "🔒",
                        "unlock_rank": "Specialist",
                        "unlock_level": 2,
                        "base_spirits": [spirit_ids.get("Security Spirit", 14), spirit_ids.get("Analyst Spirit", 4), spirit_ids.get("Debugger Spirit", 8)],
                        "spirit_synergies": json.dumps({"security_analyst": 0.25, "debugger_security": 0.20}),
                        "spirit_conflicts": json.dumps({}),
                        "net_performance_bonus": 0.45,
                        "specialization": "Cybersecurity and vulnerability assessment",
                        "perfect_for": ["Cybersecurity", "Penetration testing", "Security auditing"],
                        "tools_count": 19
                    },
                    {
                        "class_name": "Swiss Army Knife",
                        "class_description": "General-purpose problem solving with diverse capabilities",
                        "category": "Hybrid & Versatile",
                        "icon": "🔧",
                        "unlock_rank": "Novice",
                        "unlock_level": 1,
                        "base_spirits": [spirit_ids.get("Builder Spirit", 7), spirit_ids.get("Writer Spirit", 1), spirit_ids.get("Analyst Spirit", 4)],
                        "spirit_synergies": json.dumps({"builder_analyst": 0.20, "writer_analyst": 0.15}),
                        "spirit_conflicts": json.dumps({}),
                        "net_performance_bonus": 0.35,
                        "specialization": "General-purpose problem solving",
                        "perfect_for": ["General assistance", "Prototyping", "Multi-task projects"],
                        "tools_count": 20
                    }
                ]
                
                # Insert classes
                for cls in classes:
                    conn.execute(text("""
                        INSERT INTO minion_classes (
                            class_name, class_description, category, icon, unlock_rank, unlock_level,
                            base_spirits, spirit_synergies, spirit_conflicts, net_performance_bonus,
                            specialization, perfect_for, tools_count
                        ) VALUES (
                            :class_name, :class_description, :category, :icon, :unlock_rank, :unlock_level,
                            :base_spirits, :spirit_synergies, :spirit_conflicts, :net_performance_bonus,
                            :specialization, :perfect_for, :tools_count
                        ) ON CONFLICT (class_name) DO NOTHING
                    """), cls)
                
                # Commit transaction
                trans.commit()
                
                print(f"✅ Seeded {len(classes)} minion classes!")
                
                # Verify insertion
                result = conn.execute(text("SELECT COUNT(*) FROM minion_classes"))
                count = result.fetchone()[0]
                print(f"Total classes in database: {count}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        print(f"❌ Error seeding minion classes: {e}")
        return False

if __name__ == "__main__":
    success = seed_minion_classes()
    if success:
        print("\n🎉 Minion Classes Seeded Successfully!")
    else:
        print("\n❌ Failed to seed minion classes")
        sys.exit(1)
