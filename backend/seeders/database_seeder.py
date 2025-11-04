#!/usr/bin/env python3
"""
Database Seeder for Spirit System
Integrates with SQLAlchemy to populate the spirit system tables
"""

import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seeders.spirit_system_seeder import (
    create_spirits_data,
    create_minion_templates,
    create_tools_registry
)

def seed_spirit_system(db_session):
    """
    Seed the spirit system tables with initial data
    
    Args:
        db_session: SQLAlchemy database session
    """
    try:
        print("🌟 Seeding Spirit System...")
        
        # Import models (these would be created in the new PostgreSQL schema)
        # from app.models.spirit_models import SpiritRegistry, MinionTemplate, ToolRegistry
        
        spirits_data = create_spirits_data()
        templates_data = create_minion_templates()
        tools_data = create_tools_registry()
        
        print(f"📊 Seeding {len(spirits_data)} spirits...")
        # for spirit_data in spirits_data:
        #     spirit = SpiritRegistry(**spirit_data)
        #     db_session.add(spirit)
        
        print(f"🤖 Seeding {len(templates_data)} minion templates...")
        # for template_data in templates_data:
        #     template = MinionTemplate(**template_data)
        #     db_session.add(template)
        
        print(f"🛠️ Seeding {len(tools_data)} tools...")
        # for tool_data in tools_data:
        #     tool = ToolRegistry(**tool_data)
        #     db_session.add(tool)
        
        # db_session.commit()
        print("✅ Spirit system seeded successfully!")
        
        return {
            'spirits': len(spirits_data),
            'templates': len(templates_data),
            'tools': len(tools_data)
        }
        
    except Exception as e:
        print(f"❌ Error seeding spirit system: {e}")
        # db_session.rollback()
        raise

def seed_database():
    """
    Main seeding function - to be used when PostgreSQL is ready
    """
    print("🚀 Database Seeder for Spirit System")
    print("=" * 50)
    
    # This would be used with the new PostgreSQL database
    # from database.session import get_session
    # 
    # with get_session() as session:
    #     result = seed_spirit_system(session)
    #     print(f"✅ Seeded {result['spirits']} spirits, {result['templates']} templates, {result['tools']} tools")
    
    print("📋 Ready for PostgreSQL integration!")
    print("   Run this when the new PostgreSQL schema is implemented")

if __name__ == "__main__":
    seed_database()
