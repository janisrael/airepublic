"""
New database package for clean architecture
Imports existing database infrastructure
"""

# Import existing database components (keeping original structure intact)
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from database import get_database_url, create_engine, get_session, SessionLocal, Base
    __all__ = ['get_database_url', 'create_engine', 'get_session', 'SessionLocal', 'Base']
except ImportError:
    __all__ = []
