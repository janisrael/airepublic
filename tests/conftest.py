"""
Professional Test Configuration
Pytest fixtures and configuration for comprehensive testing
"""

import pytest
import os
import tempfile
import sys
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    # Create temporary PostgreSQL database
    db_fd, db_path = tempfile.mkstemp()
    
    engine = create_engine(f'PostgreSQL:///{db_path}', echo=False)
    
    # Import models and create tables
    from model import Base
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope="session")
def redis_client():
    """Mock Redis client for testing"""
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.keys.return_value = []
    
    return mock_redis

@pytest.fixture
def mock_redis(redis_client):
    """Patch Redis for individual tests"""
    with patch('cache.redis_config.redis_manager.redis_client', redis_client):
        yield redis_client

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123',
        'first_name': 'Test',
        'last_name': 'User'
    }

@pytest.fixture
def sample_model_data():
    """Sample model data for testing"""
    return {
        'name': 'test-model',
        'display_name': 'Test Model',
        'provider': 'openai',
        'model_id': 'gpt-4',
        'capabilities': ['text-generation'],
        'context_length': 4096,
        'max_tokens': 2048,
        'temperature': 0.7,
        'top_p': 0.9
    }

@pytest.fixture
def sample_training_job():
    """Sample training job data for testing"""
    return {
        'model_name': 'test-model',
        'training_type': 'lora',
        'status': 'PENDING',
        'progress': 0,
        'dataset_name': 'test-dataset',
        'epochs': 3,
        'learning_rate': 0.0002
    }

@pytest.fixture
def auth_headers():
    """Mock JWT token headers"""
    return {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token'
    }

@pytest.fixture
def client():
    """Flask test client"""
    from app_server_new import app
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Cleanup code here if needed
    pass

# Markers for different test types
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "benchmark: marks tests as benchmark tests")
