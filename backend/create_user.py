#!/usr/bin/env python3
"""
Create a user account for login testing
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from model.user import User
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

def create_default_users():
    """Create default user accounts"""
    try:
        print("🔧 Creating default user accounts...")
        
        # Create engine and session
        engine = create_spirit_engine()
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Default users to create
            default_users = [
                {
                    'username': 'admin',
                    'email': 'admin@airepublic.com',
                    'password': 'admin123',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_active': True,
                    'is_verified': True,
                    'subscription_status': 'premium'
                },
                {
                    'username': 'user',
                    'email': 'user@example.com',
                    'password': 'password',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'is_active': True,
                    'is_verified': True,
                    'subscription_status': 'no_subscription'
                },
                {
                    'username': 'developer',
                    'email': 'dev@airepublic.com',
                    'password': 'dev123',
                    'first_name': 'Developer',
                    'last_name': 'User',
                    'is_active': True,
                    'is_verified': True,
                    'subscription_status': 'premium'
                },
                {
                    'username': 'swordfish',
                    'email': 'swordfish@airepublic.com',
                    'password': 'swordfish123',
                    'first_name': 'Swordfish',
                    'last_name': 'User',
                    'is_active': True,
                    'is_verified': True,
                    'subscription_status': 'premium'
                }
            ]
            
            created_count = 0
            for user_data in default_users:
                # Check if user exists
                existing_user = session.query(User).filter(User.username == user_data['username']).first()
                if existing_user:
                    print(f"ℹ️  User '{user_data['username']}' already exists")
                    continue
                
                # Create user
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=user_data['is_active'],
                    is_verified=user_data['is_verified'],
                    subscription_status=user_data['subscription_status']
                )
                
                session.add(user)
                created_count += 1
            
            session.commit()
            
            print(f"✅ Created {created_count} new users")
            print("📋 Default Login Credentials:")
            print("   Admin:     admin / admin123")
            print("   User:      user / password")
            print("   Developer: developer / dev123")
            print("   Swordfish: swordfish / swordfish123")
            return True
            
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        return False

if __name__ == '__main__':
    create_default_users()
