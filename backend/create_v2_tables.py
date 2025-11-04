#!/usr/bin/env python3
"""
Create V2 Database Tables
Creates all SQLAlchemy tables for the V2 system
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from model.base import Base
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker

def create_all_tables():
    """Create all V2 database tables"""
    try:
        print("🔧 Creating V2 database tables...")
        
        # Create engine
        engine = create_spirit_engine()
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        print("✅ All V2 tables created successfully!")
        
        # List created tables
        print("\n📊 Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        print("\n🌱 Creating sample data...")
        
        # Create engine and session
        engine = create_spirit_engine()
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            from model.user import User
            from model.reference_models import ReferenceModel
            from model.spirit_models import SpiritRegistry
            from werkzeug.security import generate_password_hash
            
            # Check if sample user exists
            existing_user = session.query(User).filter(User.username == 'testuser').first()
            if not existing_user:
                # Create sample user
                user = User(
                    username='testuser',
                    email='test@example.com',
                    password_hash=generate_password_hash('password123'),
                    first_name='Test',
                    last_name='User',
                    is_active=True,
                    is_verified=True,
                    subscription_status='no_subscription'
                )
                session.add(user)
                session.commit()
                print("✅ Sample user created: testuser / password123")
            else:
                print("ℹ️  Sample user already exists")
            
            # Check if reference models exist
            existing_models = session.query(ReferenceModel).count()
            if existing_models == 0:
                # Create sample reference models
                reference_models = [
                    {
                        'name': 'gpt-4',
                        'display_name': 'GPT-4',
                        'description': 'OpenAI GPT-4 model',
                        'model_type': 'chat',
                        'provider': 'openai',
                        'model_id': 'gpt-4',
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'max_tokens': 4096,
                        'stream': True,
                        'capabilities': ['chat', 'reasoning', 'code'],
                        'is_active': True,
                        'is_favorite': True,
                        'tags': ['openai', 'gpt-4', 'chat']
                    },
                    {
                        'name': 'claude-3-sonnet',
                        'display_name': 'Claude 3 Sonnet',
                        'description': 'Anthropic Claude 3 Sonnet model',
                        'model_type': 'chat',
                        'provider': 'anthropic',
                        'model_id': 'claude-3-sonnet-20240229',
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'max_tokens': 4096,
                        'stream': True,
                        'capabilities': ['chat', 'reasoning', 'code', 'analysis'],
                        'is_active': True,
                        'is_favorite': True,
                        'tags': ['anthropic', 'claude', 'chat']
                    },
                    {
                        'name': 'llama-3-8b',
                        'display_name': 'Llama 3 8B',
                        'description': 'Meta Llama 3 8B model',
                        'model_type': 'chat',
                        'provider': 'meta',
                        'model_id': 'llama-3-8b',
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'max_tokens': 8192,
                        'stream': True,
                        'capabilities': ['chat', 'reasoning', 'code'],
                        'is_active': True,
                        'is_favorite': False,
                        'tags': ['meta', 'llama', 'chat', 'open-source']
                    }
                ]
                
                for model_data in reference_models:
                    model = ReferenceModel(**model_data)
                    session.add(model)
                
                session.commit()
                print(f"✅ Created {len(reference_models)} reference models")
            else:
                print(f"ℹ️  {existing_models} reference models already exist")
            
            # Check if spirits exist
            existing_spirits = session.query(SpiritRegistry).count()
            if existing_spirits == 0:
                # Create sample spirits
                spirits = [
                    {
                        'name': 'Writer',
                        'category': 'Creative',
                        'description': 'Helps with writing, editing, and content creation',
                        'icon': '✍️',
                        'unlock_rank': 'Novice',
                        'unlock_level': 1,
                        'max_spirit_level': 10,
                        'tools': ['text_generator', 'grammar_checker', 'style_analyzer'],
                        'price_usd': 0.00,
                        'price_points': 0,
                        'is_purchaseable': True,
                        'is_premium': False,
                        'free_with_subscription': True,
                        'tier': 'Basic',
                        'is_active': True
                    },
                    {
                        'name': 'Analyst',
                        'category': 'Analytical',
                        'description': 'Provides data analysis and insights',
                        'icon': '📊',
                        'unlock_rank': 'Novice',
                        'unlock_level': 1,
                        'max_spirit_level': 10,
                        'tools': ['data_analyzer', 'chart_generator', 'insight_extractor'],
                        'price_usd': 0.00,
                        'price_points': 0,
                        'is_purchaseable': True,
                        'is_premium': False,
                        'free_with_subscription': True,
                        'tier': 'Basic',
                        'is_active': True
                    },
                    {
                        'name': 'Builder',
                        'category': 'Technical',
                        'description': 'Assists with coding and technical tasks',
                        'icon': '🔧',
                        'unlock_rank': 'Apprentice',
                        'unlock_level': 2,
                        'max_spirit_level': 10,
                        'tools': ['code_generator', 'debugger', 'architecture_designer'],
                        'price_usd': 9.99,
                        'price_points': 100,
                        'is_purchaseable': True,
                        'is_premium': True,
                        'free_with_subscription': False,
                        'tier': 'Professional',
                        'is_active': True
                    }
                ]
                
                for spirit_data in spirits:
                    spirit = SpiritRegistry(**spirit_data)
                    session.add(spirit)
                
                session.commit()
                print(f"✅ Created {len(spirits)} spirits")
            else:
                print(f"ℹ️  {existing_spirits} spirits already exist")
        
        print("✅ Sample data creation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

if __name__ == '__main__':
    print("🚀 V2 Database Setup")
    print("=" * 50)
    
    # Create tables
    if create_all_tables():
        # Create sample data
        create_sample_data()
        print("\n🎉 V2 database setup completed successfully!")
        print("\n📋 Next steps:")
        print("  1. Start V2 server: ./start_services.sh v2")
        print("  2. Test login with: testuser / password123")
        print("  3. Access frontend: http://localhost:5173")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
