#!/usr/bin/env python3
"""
Initialize RBAC System
Creates default roles, permissions, and assigns them to users
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rbac_service import RBACService
from model.user import User
from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker

def init_rbac_system():
    """Initialize the RBAC system with default roles and permissions"""
    
    rbac_service = RBACService()
    
    print("🔐 Initializing RBAC System...")
    
    # ==================== CREATE DEFAULT ROLES ====================
    
    default_roles = [
        {
            'name': 'superuser',
            'description': 'Full system access with all permissions'
        },
        {
            'name': 'admin',
            'description': 'Administrative access to manage users and system settings'
        },
        {
            'name': 'premium',
            'description': 'Premium user with advanced features and higher limits'
        },
        {
            'name': 'user',
            'description': 'Standard user with basic access'
        },
        {
            'name': 'developer',
            'description': 'Developer access for API and training features'
        }
    ]
    
    print("\n📋 Creating default roles...")
    for role_data in default_roles:
        result = rbac_service.create_role(role_data['name'], role_data['description'])
        if result['success']:
            print(f"  ✅ Created role: {role_data['name']}")
        else:
            print(f"  ⚠️  Role {role_data['name']}: {result.get('error', 'Unknown error')}")
    
    # ==================== CREATE DEFAULT PERMISSIONS ====================
    
    default_permissions = [
        # Admin permissions
        {'name': 'admin_access', 'resource': 'admin', 'action': 'access', 'description': 'Access admin panel'},
        {'name': 'admin_read', 'resource': 'admin', 'action': 'read', 'description': 'Read admin data'},
        {'name': 'admin_create', 'resource': 'admin', 'action': 'create', 'description': 'Create admin resources'},
        {'name': 'admin_update', 'resource': 'admin', 'action': 'update', 'description': 'Update admin resources'},
        {'name': 'admin_delete', 'resource': 'admin', 'action': 'delete', 'description': 'Delete admin resources'},
        
        # User management
        {'name': 'user_read', 'resource': 'users', 'action': 'read', 'description': 'Read user data'},
        {'name': 'user_create', 'resource': 'users', 'action': 'create', 'description': 'Create users'},
        {'name': 'user_update', 'resource': 'users', 'action': 'update', 'description': 'Update users'},
        {'name': 'user_delete', 'resource': 'users', 'action': 'delete', 'description': 'Delete users'},
        
        # Model permissions
        {'name': 'models_read', 'resource': 'models', 'action': 'read', 'description': 'Read models'},
        {'name': 'models_create', 'resource': 'models', 'action': 'create', 'description': 'Create models'},
        {'name': 'models_update', 'resource': 'models', 'action': 'update', 'description': 'Update models'},
        {'name': 'models_delete', 'resource': 'models', 'action': 'delete', 'description': 'Delete models'},
        {'name': 'models_chat', 'resource': 'models', 'action': 'chat', 'description': 'Chat with models'},
        
        # Training permissions
        {'name': 'training_read', 'resource': 'training', 'action': 'read', 'description': 'Read training data'},
        {'name': 'training_create', 'resource': 'training', 'action': 'create', 'description': 'Create training jobs'},
        {'name': 'training_update', 'resource': 'training', 'action': 'update', 'description': 'Update training jobs'},
        {'name': 'training_delete', 'resource': 'training', 'action': 'delete', 'description': 'Delete training jobs'},
        
        # Dataset permissions
        {'name': 'datasets_read', 'resource': 'datasets', 'action': 'read', 'description': 'Read datasets'},
        {'name': 'datasets_create', 'resource': 'datasets', 'action': 'create', 'description': 'Create datasets'},
        {'name': 'datasets_update', 'resource': 'datasets', 'action': 'update', 'description': 'Update datasets'},
        {'name': 'datasets_delete', 'resource': 'datasets', 'action': 'delete', 'description': 'Delete datasets'},
        
        # Spirit system permissions
        {'name': 'spirits_read', 'resource': 'spirits', 'action': 'read', 'description': 'Read spirits'},
        {'name': 'spirits_create', 'resource': 'spirits', 'action': 'create', 'description': 'Create spirits'},
        {'name': 'spirits_update', 'resource': 'spirits', 'action': 'update', 'description': 'Update spirits'},
        {'name': 'spirits_delete', 'resource': 'spirits', 'action': 'delete', 'description': 'Delete spirits'},
        
        # Minion permissions
        {'name': 'minions_read', 'resource': 'minions', 'action': 'read', 'description': 'Read minions'},
        {'name': 'minions_create', 'resource': 'minions', 'action': 'create', 'description': 'Create minions'},
        {'name': 'minions_update', 'resource': 'minions', 'action': 'update', 'description': 'Update minions'},
        {'name': 'minions_delete', 'resource': 'minions', 'action': 'delete', 'description': 'Delete minions'},
        
        # API permissions
        {'name': 'api_read', 'resource': 'api', 'action': 'read', 'description': 'Read API data'},
        {'name': 'api_create', 'resource': 'api', 'action': 'create', 'description': 'Create API resources'},
        {'name': 'api_update', 'resource': 'api', 'action': 'update', 'description': 'Update API resources'},
        {'name': 'api_delete', 'resource': 'api', 'action': 'delete', 'description': 'Delete API resources'},
    ]
    
    print("\n🔑 Creating default permissions...")
    created_permissions = []
    for perm_data in default_permissions:
        result = rbac_service.create_permission(
            perm_data['name'], 
            perm_data['resource'], 
            perm_data['action'], 
            perm_data['description']
        )
        if result['success']:
            created_permissions.append(result['permission'])
            print(f"  ✅ Created permission: {perm_data['name']}")
        else:
            print(f"  ⚠️  Permission {perm_data['name']}: {result.get('error', 'Unknown error')}")
    
    # ==================== ASSIGN PERMISSIONS TO ROLES ====================
    
    print("\n🔗 Assigning permissions to roles...")
    
    # Superuser - All permissions
    for permission in created_permissions:
        result = rbac_service.assign_permission_to_role('superuser', permission['id'])
        if result['success']:
            print(f"  ✅ Assigned {permission['name']} to superuser")
    
    # Admin - Most permissions except some superuser-only
    admin_permissions = [p for p in created_permissions if not p['name'].startswith('superuser')]
    for permission in admin_permissions:
        result = rbac_service.assign_permission_to_role('admin', permission['id'])
        if result['success']:
            print(f"  ✅ Assigned {permission['name']} to admin")
    
    # Premium - Advanced user permissions
    premium_permissions = [
        p for p in created_permissions 
        if p['resource'] in ['models', 'training', 'datasets', 'spirits', 'minions'] 
        and p['action'] in ['read', 'create', 'update']
    ]
    for permission in premium_permissions:
        result = rbac_service.assign_permission_to_role('premium', permission['id'])
        if result['success']:
            print(f"  ✅ Assigned {permission['name']} to premium")
    
    # User - Basic permissions
    user_permissions = [
        p for p in created_permissions 
        if p['resource'] in ['models', 'datasets'] 
        and p['action'] in ['read', 'create']
    ]
    for permission in user_permissions:
        result = rbac_service.assign_permission_to_role('user', permission['id'])
        if result['success']:
            print(f"  ✅ Assigned {permission['name']} to user")
    
    # Developer - API and training permissions
    developer_permissions = [
        p for p in created_permissions 
        if p['resource'] in ['api', 'training', 'models'] 
        and p['action'] in ['read', 'create', 'update']
    ]
    for permission in developer_permissions:
        result = rbac_service.assign_permission_to_role('developer', permission['id'])
        if result['success']:
            print(f"  ✅ Assigned {permission['name']} to developer")
    
    # ==================== ASSIGN ROLES TO EXISTING USERS ====================
    
    print("\n👥 Assigning roles to existing users...")
    
    # Get all users and assign appropriate roles
    engine = create_spirit_engine()
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        users = session.query(User).all()
        
        for user in users:
            # Assign roles based on username patterns
            if user.username == 'superuser':
                result = rbac_service.assign_role_to_user(user.id, 'superuser')
                if result['success']:
                    print(f"  ✅ Assigned superuser role to {user.username}")
            elif user.username == 'admin':
                result = rbac_service.assign_role_to_user(user.id, 'admin')
                if result['success']:
                    print(f"  ✅ Assigned admin role to {user.username}")
            elif user.username == 'premium':
                result = rbac_service.assign_role_to_user(user.id, 'premium')
                if result['success']:
                    print(f"  ✅ Assigned premium role to {user.username}")
            elif user.username == 'developer':
                result = rbac_service.assign_role_to_user(user.id, 'developer')
                if result['success']:
                    print(f"  ✅ Assigned developer role to {user.username}")
            else:
                # Default user role
                result = rbac_service.assign_role_to_user(user.id, 'user')
                if result['success']:
                    print(f"  ✅ Assigned user role to {user.username}")
    
    print("\n🎉 RBAC system initialization complete!")
    print("\n📊 Summary:")
    print(f"  - Created {len(default_roles)} roles")
    print(f"  - Created {len(created_permissions)} permissions")
    print(f"  - Assigned permissions to roles")
    print(f"  - Assigned roles to {len(users)} users")

if __name__ == "__main__":
    init_rbac_system()
