"""
PostgreSQL connection configuration for Spirit System
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Optional

def get_postgres_database_url() -> str:
    """
    Get PostgreSQL database URL for Spirit System
    """
    # Environment variables for PostgreSQL connection
    host = os.getenv('POSTGRES_HOST', '127.0.0.1')  # Use IPv4 instead of localhost
    port = os.getenv('POSTGRES_PORT', '5432')
    database = os.getenv('POSTGRES_DB', 'ai_republic_spirits')
    username = os.getenv('POSTGRES_USER', 'ai_republic')
    password = os.getenv('POSTGRES_PASSWORD', 'password')
    
    # PostgreSQL URL format
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"

def create_postgres_engine(database_url: Optional[str] = None) -> Engine:
    """
    Create SQLAlchemy engine for PostgreSQL connection
    """
    if database_url is None:
        database_url = get_postgres_database_url()
    
    # PostgreSQL-specific configuration
    engine_kwargs = {
        "echo": False,  # Set to True for SQL query logging
        "pool_pre_ping": True,  # Verify connections before use
        "pool_size": 10,  # Connection pool size
        "max_overflow": 20,  # Additional connections beyond pool_size
        "pool_recycle": 3600,  # Recycle connections every hour
    }
    
    return create_engine(database_url, **engine_kwargs)

def get_spirit_database_url() -> str:
    """
    Get Spirit System database URL
    PostgreSQL ONLY - No PostgreSQL fallback
    """
    try:
        # PostgreSQL only - no fallback
        postgres_url = get_postgres_database_url()
        # Test connection
        test_engine = create_postgres_engine(postgres_url)
        test_engine.connect()
        print(f"✅ PostgreSQL connection successful: {postgres_url}")
        return postgres_url
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("🔧 Please ensure PostgreSQL is running and configured correctly")
        print("🔧 Expected connection: postgresql://ai_republic:password@127.0.0.1:5432/ai_republic_spirits")
        raise Exception(f"PostgreSQL connection required but failed: {e}")

def create_spirit_engine() -> Engine:
    """
    Create SQLAlchemy engine for Spirit System database
    """
    database_url = get_spirit_database_url()
    
    if database_url.startswith("postgresql"):
        return create_postgres_engine(database_url)
    else:
        # PostgreSQL fallback configuration
        return create_engine(database_url, echo=False, connect_args={"check_same_thread": False})

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
