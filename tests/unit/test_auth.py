"""
Unit Tests for Authentication System
"""

import pytest
import jwt
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

class TestAuthentication:
    """Test authentication functionality"""
    
    def test_jwt_token_generation(self):
        """Test JWT token generation"""
        from app.routes.auth_routes import generate_token
        
        user_id = 1
        username = "testuser"
        
        token = generate_token(user_id, username)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode token to verify payload
        decoded = jwt.decode(token, 'your-secret-key-change-in-production', algorithms=['HS256'])
        assert decoded['user_id'] == user_id
        assert decoded['username'] == username
    
    def test_jwt_token_verification(self):
        """Test JWT token verification"""
        from app.routes.auth_routes import verify_token
        
        # Valid token
        payload = {
            'user_id': 1,
            'username': 'testuser',
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, 'your-secret-key-change-in-production', algorithm='HS256')
        
        result = verify_token(token)
        assert result is not None
        assert result['user_id'] == 1
        assert result['username'] == 'testuser'
    
    def test_expired_token(self):
        """Test expired token handling"""
        from app.routes.auth_routes import verify_token
        
        # Expired token
        payload = {
            'user_id': 1,
            'username': 'testuser',
            'exp': datetime.utcnow() - timedelta(hours=1),
            'iat': datetime.utcnow() - timedelta(hours=2)
        }
        token = jwt.encode(payload, 'your-secret-key-change-in-production', algorithm='HS256')
        
        result = verify_token(token)
        assert result is None
    
    def test_invalid_token(self):
        """Test invalid token handling"""
        from app.routes.auth_routes import verify_token
        
        # Invalid token
        result = verify_token("invalid.token.here")
        assert result is None
        
        # Empty token
        result = verify_token("")
        assert result is None
        
        # None token
        result = verify_token(None)
        assert result is None
    
    @pytest.mark.unit
    def test_password_hashing(self):
        """Test password hashing and verification"""
        from werkzeug.security import generate_password_hash, check_password_hash
        
        password = "testpassword123"
        hashed = generate_password_hash(password)
        
        assert hashed != password
        assert check_password_hash(hashed, password)
        assert not check_password_hash(hashed, "wrongpassword")
    
    @pytest.mark.unit
    def test_user_creation(self, test_db, sample_user_data):
        """Test user creation in database"""
        from model.user import User
        from werkzeug.security import generate_password_hash
        
        user = User(
            username=sample_user_data['username'],
            email=sample_user_data['email'],
            password_hash=generate_password_hash(sample_user_data['password']),
            first_name=sample_user_data['first_name'],
            last_name=sample_user_data['last_name'],
            is_active=True,
            is_verified=True
        )
        
        test_db.add(user)
        test_db.commit()
        
        assert user.id is not None
        assert user.username == sample_user_data['username']
        assert user.email == sample_user_data['email']
        assert user.is_active is True
        assert user.is_verified is True
    
    @pytest.mark.unit
    def test_user_authentication(self, test_db, sample_user_data):
        """Test user authentication flow"""
        from model.user import User
        from werkzeug.security import generate_password_hash, check_password_hash
        
        # Create user
        user = User(
            username=sample_user_data['username'],
            email=sample_user_data['email'],
            password_hash=generate_password_hash(sample_user_data['password']),
            first_name=sample_user_data['first_name'],
            last_name=sample_user_data['last_name'],
            is_active=True,
            is_verified=True
        )
        
        test_db.add(user)
        test_db.commit()
        
        # Test authentication
        found_user = test_db.query(User).filter(
            User.username == sample_user_data['username'],
            User.is_active == True
        ).first()
        
        assert found_user is not None
        assert check_password_hash(found_user.password_hash, sample_user_data['password'])
        assert not check_password_hash(found_user.password_hash, "wrongpassword")
