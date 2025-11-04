#!/usr/bin/env python3
"""
Complete PostgreSQL Spirit System Setup
Initializes database, creates tables, and seeds data
"""

import sys
import os
import subprocess
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

def run_script(script_path: str, description: str) -> bool:
    """Run a Python script and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=backend_dir)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def check_postgres_connection():
    """Check if PostgreSQL is available"""
    print("🔍 Checking PostgreSQL connection...")
    
    try:
        from database.postgres_connection import test_connection
        if test_connection():
            print("✅ PostgreSQL connection successful")
            return True
        else:
            print("❌ PostgreSQL connection failed")
            return False
    except Exception as e:
        print(f"❌ PostgreSQL not available: {e}")
        print("💡 Falling back to PostgreSQL for development")
        return False

def main():
    """Main setup function"""
    print("🚀 PostgreSQL Spirit System Setup")
    print("=" * 50)
    
    # Check PostgreSQL availability
    postgres_available = check_postgres_connection()
    
    if postgres_available:
        # Run PostgreSQL setup
        steps = [
            ("scripts/init_postgres_spirits.py", "Initialize PostgreSQL database"),
            ("seeders/postgres_spirit_seeder.py", "Seed spirit system data")
        ]
        
        for script_path, description in steps:
            if not run_script(script_path, description):
                print(f"\n❌ Setup failed at: {description}")
                return False
        
        print("\n🎉 PostgreSQL Spirit System Setup Complete!")
        print("📊 Database Features:")
        print("   - 18 Spirit types with pricing tiers")
        print("   - 23 Pre-built minion templates")
        print("   - 71 Tools with unique capabilities")
        print("   - 7 Spirit bundles with savings")
        print("   - 4 Subscription plans")
        print("   - Complete purchase tracking system")
        
    else:
        print("\n💡 PostgreSQL not available - using PostgreSQL fallback")
        print("🔧 To use PostgreSQL:")
        print("   1. Install PostgreSQL")
        print("   2. Set environment variables:")
        print("      - POSTGRES_HOST=localhost")
        print("      - POSTGRES_PORT=5432")
        print("      - POSTGRES_DB=ai_republic_spirits")
        print("      - POSTGRES_USER=ai_republic")
        print("      - POSTGRES_PASSWORD=password")
        print("   3. Run this setup script again")
        
        # Still create the models and services for PostgreSQL
        print("\n🔄 Creating PostgreSQL fallback setup...")
        
        # Create a simple PostgreSQL version
        try:
            from database.connection import create_engine
            from model.spirit_models import Base
            
            engine = create_engine()
            Base.metadata.create_all(engine)
            print("✅ PostgreSQL tables created")
            
        except Exception as e:
            print(f"❌ PostgreSQL setup failed: {e}")
            return False
    
    print("\n🔧 Next Steps:")
    print("   1. Test API endpoints:")
    print("      - GET /api/spirits/")
    print("      - GET /api/spirits/free")
    print("      - GET /api/spirits/bundles")
    print("      - GET /api/spirits/subscription-plans")
    print("   2. Start the new server: python app_server_new.py")
    print("   3. Test spirit system integration")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
