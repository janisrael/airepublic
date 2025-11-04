#!/usr/bin/env python3
"""
Initialize PostgreSQL database for Spirit System
"""

import sys
import os
from sqlalchemy import create_engine, text

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.postgres_connection import create_spirit_engine, get_postgres_database_url
from model.spirit_models import Base
from model.base import Base as BaseModel

def create_database():
    """Create the PostgreSQL database if it doesn't exist"""
    try:
        # Get database URL without the database name
        db_url = get_postgres_database_url()
        
        # Extract database name
        db_name = db_url.split('/')[-1]
        base_url = '/'.join(db_url.split('/')[:-1])
        
        # Connect to PostgreSQL server (without specific database)
        server_engine = create_engine(base_url + '/postgres')
        
        with server_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Created database: {db_name}")
            else:
                print(f"✅ Database already exists: {db_name}")
                
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise

def create_tables():
    """Create all spirit system tables"""
    try:
        engine = create_spirit_engine()
        
        # Import all models to ensure they're registered
        from model.spirit_models import (
            SpiritRegistry, MinionSpirit, SpiritMastery, SpiritBundle,
            SubscriptionPlan, UserSpiritPurchase, UserSpiritSubscription,
            UserPoints, PointsTransaction, UserSpiritAccess, ToolRegistry, SpiritMinion
        )
        
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ Created all spirit system tables")
        
        return engine
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

def test_connection():
    """Test database connection"""
    try:
        engine = create_spirit_engine()
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Initializing PostgreSQL Spirit System Database")
    print("=" * 60)
    
    try:
        # Test connection first
        if not test_connection():
            print("❌ Database connection failed. Please check PostgreSQL configuration.")
            return False
        
        # Create database if needed
        create_database()
        
        # Create tables
        engine = create_tables()
        
        print("\n🎉 PostgreSQL Spirit System Database Initialized Successfully!")
        print("📊 Created Tables:")
        print("   - spirits_registry")
        print("   - minion_spirits") 
        print("   - spirit_mastery")
        print("   - spirit_bundles")
        print("   - subscription_plans")
        print("   - user_spirit_purchases")
        print("   - user_subscriptions")
        print("   - user_points")
        print("   - points_transactions")
        print("   - user_spirit_access")
        print("   - tools_registry")
        print("   - minions")
        
        print("\n🔧 Next Steps:")
        print("   1. Run spirit system seeders to populate data")
        print("   2. Test API endpoints with PostgreSQL")
        print("   3. Configure environment variables for production")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
