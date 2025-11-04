# External Model Training Service with User RBAC - Implementation Plan

## Overview

This document outlines the complete implementation plan for integrating external model training (LoRA + RAG + External LLM) with user management and role-based access control (RBAC) into the AI Refinement Dashboard.

## Table of Contents

1. [Database Schema](#database-schema)
2. [RBAC System](#rbac-system)
3. [Service Architecture](#service-architecture)
4. [API Endpoints](#api-endpoints)
5. [Data Relationships](#data-relationships)
6. [Security Implementation](#security-implementation)
7. [Frontend Integration](#frontend-integration)
8. [Implementation Phases](#implementation-phases)

---

## 1. Database Schema

### 1.1 User Management Tables

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Roles Table
```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,  -- 'admin', 'user', 'premium_user', 'developer'
    description TEXT,
    permissions TEXT,  -- JSON array of permissions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### User Roles Junction Table
```sql
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,  -- User who assigned this role
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users (id),
    UNIQUE(user_id, role_id)
);
```

#### Permissions Table
```sql
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,  -- 'create_model', 'train_model', 'access_external_api'
    resource TEXT NOT NULL,     -- 'models', 'training', 'external_apis'
    action TEXT NOT NULL,       -- 'create', 'read', 'update', 'delete'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Role Permissions Junction Table
```sql
CREATE TABLE role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE,
    UNIQUE(role_id, permission_id)
);
```

### 1.2 External Model and Hybrid Training Tables

#### External Model Configurations Table
```sql
CREATE TABLE external_model_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,  -- 'nvidia', 'openai', 'anthropic', 'mistral'
    model_id TEXT NOT NULL,  -- 'nvidia/llama-3.3-nemotron-super-49b-v1.5'
    api_key_encrypted TEXT NOT NULL,  -- Encrypted API key
    base_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_shared BOOLEAN DEFAULT FALSE,  -- Can be shared with other users
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

#### Hybrid Training Jobs Table
```sql
CREATE TABLE hybrid_training_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    job_id INTEGER REFERENCES training_jobs(id),  -- Link to base training job
    local_lora_model TEXT,  -- Path to local LoRA model
    rag_collection_name TEXT,  -- ChromaDB collection name
    external_model_config_id INTEGER REFERENCES external_model_configs(id),
    status TEXT DEFAULT 'PENDING',  -- PENDING, RUNNING, COMPLETED, FAILED
    progress REAL DEFAULT 0.0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

#### User Model Access Table
```sql
CREATE TABLE user_model_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    access_type TEXT NOT NULL,  -- 'owner', 'shared', 'public'
    granted_by INTEGER,  -- User who granted access
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- Optional expiration
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users (id),
    UNIQUE(user_id, model_name)
);
```

### 1.3 Updates to Existing Tables

```sql
-- Add user_id to existing tables
ALTER TABLE datasets ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE training_jobs ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE model_profiles ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE evaluations ADD COLUMN user_id INTEGER REFERENCES users(id);

-- Add indexes for performance
CREATE INDEX idx_datasets_user_id ON datasets(user_id);
CREATE INDEX idx_training_jobs_user_id ON training_jobs(user_id);
CREATE INDEX idx_model_profiles_user_id ON model_profiles(user_id);
CREATE INDEX idx_hybrid_jobs_user_id ON hybrid_training_jobs(user_id);
CREATE INDEX idx_external_configs_user_id ON external_model_configs(user_id);
```

---

## 2. RBAC System

### 2.1 Default Roles and Permissions

```python
DEFAULT_ROLES = {
    'admin': {
        'description': 'Full system access and management',
        'permissions': [
            # User management
            'users.create', 'users.read', 'users.update', 'users.delete',
            # Model management
            'models.create', 'models.read', 'models.update', 'models.delete',
            # Training management
            'training.create', 'training.read', 'training.update', 'training.delete',
            # External API management
            'external_apis.create', 'external_apis.read', 'external_apis.update', 'external_apis.delete',
            # Dataset management
            'datasets.create', 'datasets.read', 'datasets.update', 'datasets.delete',
            # System administration
            'system.admin', 'system.config', 'system.logs'
        ]
    },
    'premium_user': {
        'description': 'Premium user with external API access',
        'permissions': [
            # Model management
            'models.create', 'models.read', 'models.update', 'models.delete',
            # Training management
            'training.create', 'training.read', 'training.update', 'training.delete',
            # External API access
            'external_apis.create', 'external_apis.read', 'external_apis.update',
            # Dataset management
            'datasets.create', 'datasets.read', 'datasets.update',
            # Hybrid training
            'hybrid_training.create', 'hybrid_training.read', 'hybrid_training.update'
        ]
    },
    'user': {
        'description': 'Standard user with basic access',
        'permissions': [
            # Model management (limited)
            'models.read', 'models.create',
            # Training management (limited)
            'training.create', 'training.read',
            # Dataset management (limited)
            'datasets.read'
        ]
    },
    'developer': {
        'description': 'Developer with API access',
        'permissions': [
            # Model management
            'models.create', 'models.read', 'models.update',
            # Training management
            'training.create', 'training.read', 'training.update',
            # External API access
            'external_apis.create', 'external_apis.read', 'external_apis.update',
            # Dataset management
            'datasets.create', 'datasets.read', 'datasets.update',
            # API access
            'api.access', 'api.key_management'
        ]
    }
}
```

### 2.2 Permission Structure

```python
PERMISSIONS = {
    # User permissions
    'users.create': 'Create new users',
    'users.read': 'View user information',
    'users.update': 'Update user information',
    'users.delete': 'Delete users',
    
    # Model permissions
    'models.create': 'Create new models',
    'models.read': 'View models',
    'models.update': 'Update models',
    'models.delete': 'Delete models',
    
    # Training permissions
    'training.create': 'Start training jobs',
    'training.read': 'View training jobs',
    'training.update': 'Update training jobs',
    'training.delete': 'Delete training jobs',
    
    # External API permissions
    'external_apis.create': 'Add external API configurations',
    'external_apis.read': 'View external API configurations',
    'external_apis.update': 'Update external API configurations',
    'external_apis.delete': 'Delete external API configurations',
    
    # Dataset permissions
    'datasets.create': 'Upload datasets',
    'datasets.read': 'View datasets',
    'datasets.update': 'Update datasets',
    'datasets.delete': 'Delete datasets',
    
    # Hybrid training permissions
    'hybrid_training.create': 'Create hybrid training jobs',
    'hybrid_training.read': 'View hybrid training jobs',
    'hybrid_training.update': 'Update hybrid training jobs',
    
    # System permissions
    'system.admin': 'System administration',
    'system.config': 'System configuration',
    'system.logs': 'View system logs',
    
    # API permissions
    'api.access': 'Access API endpoints',
    'api.key_management': 'Manage API keys'
}
```


---

## 3. Service Architecture

### 3.1 User Service (`backend/services/user_service.py`)

```python
class UserService:
    """
    Handles user management, authentication, and authorization
    """
    
    def __init__(self):
        self.db = Database()
        self.auth_service = AuthService()
        self.permission_cache = {}
    
    def create_user(self, user_data):
        """Create a new user with hashed password"""
        # Validate user data
        # Hash password
        # Create user in database
        # Assign default role
        # Send verification email
        # Return user object
    
    def authenticate_user(self, username, password):
        """Authenticate user and return session token"""
        # Verify credentials
        # Check if account is active
        # Update last_login
        # Generate JWT token
        # Return user session
    
    def get_user_permissions(self, user_id):
        """Get all permissions for user through roles"""
        # Check cache first
        # Query user roles
        # Aggregate permissions
        # Cache permissions
        # Return permission list
    
    def check_permission(self, user_id, resource, action):
        """Check if user has specific permission"""
        # Get user permissions
        # Check if permission exists
        # Return boolean
    
    def assign_role(self, user_id, role_name, assigned_by):
        """Assign role to user"""
        # Verify assigner has permission
        # Get role by name
        # Create user_role record
        # Clear permission cache
        # Return success
    
    def remove_role(self, user_id, role_name, removed_by):
        """Remove role from user"""
        # Verify remover has permission
        # Delete user_role record
        # Clear permission cache
        # Return success
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile information"""
        # Validate profile data
        # Update user record
        # Return updated user
    
    def deactivate_user(self, user_id, deactivated_by):
        """Deactivate user account"""
        # Verify deactivator has permission
        # Set is_active to False
        # Invalidate all user tokens
        # Return success
```

### 3.2 Authentication Service (`backend/services/auth_service.py`)

```python
import jwt
import bcrypt
from datetime import datetime, timedelta

class AuthService:
    """
    Handles authentication, token generation, and password management
    """
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')
        self.jwt_algorithm = 'HS256'
        self.token_expiry = timedelta(days=7)
    
    def generate_token(self, user_id, username, roles):
        """Generate JWT token with user info"""
        payload = {
            'user_id': user_id,
            'username': username,
            'roles': roles,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def verify_token(self, token):
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('Token has expired')
        except jwt.InvalidTokenError:
            raise Exception('Invalid token')
    
    def refresh_token(self, old_token):
        """Refresh JWT token"""
        # Verify old token
        payload = self.verify_token(old_token)
        # Generate new token with same info
        new_token = self.generate_token(
            payload['user_id'],
            payload['username'],
            payload['roles']
        )
        return new_token
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    def invalidate_token(self, token):
        """Invalidate token (add to blacklist)"""
        # Add token to Redis/database blacklist
        # Set expiry to match token expiry
        pass
```

### 3.3 External Model Service (`backend/services/external_model_service.py`)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from peft import get_peft_model, LoraConfig, TaskType

class ExternalModelService:
    """
    Handles hybrid LoRA + RAG + External LLM pipeline
    """
    
    def __init__(self):
        self.user_service = UserService()
        self.api_key_manager = APIKeyManager()
        self.local_lora_models = {}  # Cache of loaded LoRA models
        self.vector_client = chromadb_service
        self.external_clients = {}  # Cache of external API clients
    
    def train_hybrid_model(self, user_id, job_id, job_data):
        """Train hybrid model (LoRA + RAG + External config)"""
        # Check user permissions
        if not self.user_service.check_permission(user_id, 'hybrid_training', 'create'):
            raise PermissionError('User does not have permission to create hybrid training')
        
        # Step 1: Train local LoRA model
        local_model = self._train_local_lora(user_id, job_id, job_data)
        
        # Step 2: Setup RAG knowledge base
        rag_collection = self._setup_rag_knowledge_base(user_id, job_id, job_data)
        
        # Step 3: Configure external model
        external_config = self._configure_external_model(user_id, job_data)
        
        # Step 4: Create hybrid training job record
        hybrid_job_id = self._create_hybrid_job_record(
            user_id, job_id, local_model, rag_collection, external_config
        )
        
        # Step 5: Test hybrid pipeline
        self._test_hybrid_pipeline(hybrid_job_id)
        
        return hybrid_job_id
    
    def query_hybrid_model(self, user_id, model_name, user_query):
        """Execute hybrid pipeline query"""
        # Check user access to model
        if not self._check_user_model_access(user_id, model_name):
            raise PermissionError('User does not have access to this model')
        
        # Step 1: Get local LoRA output
        local_output = self._get_local_lora_output(model_name, user_query)
        
        # Step 2: Retrieve context from RAG
        retrieved_context = self._retrieve_rag_context(model_name, user_query)
        
        # Step 3: Query external LLM
        final_output = self._query_external_llm(
            model_name, user_query, local_output, retrieved_context
        )
        
        # Step 4: Log usage
        self._log_model_usage(user_id, model_name, user_query)
        
        return final_output
    
    def _train_local_lora(self, user_id, job_id, job_data):
        """Train local LoRA model"""
        # Use existing LoRA training logic from training_executor.py
        # Return model path
        pass
    
    def _setup_rag_knowledge_base(self, user_id, job_id, job_data):
        """Setup RAG knowledge base in ChromaDB"""
        # Create collection name
        collection_name = f"user_{user_id}_job_{job_id}_kb"
        
        # Get dataset samples
        dataset_samples = self._get_dataset_samples(job_data)
        
        # Create knowledge base
        self.vector_client.create_knowledge_base(job_id, dataset_samples)
        
        return collection_name
    
    def _configure_external_model(self, user_id, job_data):
        """Configure external model for user"""
        external_config = {
            'user_id': user_id,
            'name': job_data.get('external_model_name'),
            'provider': job_data.get('external_provider'),
            'model_id': job_data.get('external_model_id'),
            'api_key_encrypted': self.api_key_manager.encrypt_api_key(
                job_data.get('api_key')
            ),
            'base_url': job_data.get('base_url')
        }
        
        # Save external config to database
        config_id = db.add_external_model_config(external_config)
        
        return config_id
    
    def _get_local_lora_output(self, model_name, user_query):
        """Get output from local LoRA model"""
        # Load LoRA model if not cached
        if model_name not in self.local_lora_models:
            self.local_lora_models[model_name] = self._load_lora_model(model_name)
        
        # Generate output
        lora_pipe = self.local_lora_models[model_name]
        output = lora_pipe(user_query, max_length=512)[0]['generated_text']
        
        return output
    
    def _retrieve_rag_context(self, model_name, user_query):
        """Retrieve context from RAG knowledge base"""
        # Get collection name for model
        collection_name = self._get_collection_name(model_name)
        
        # Query ChromaDB
        results = self.vector_client.query_collection(
            collection_name, user_query, n_results=5
        )
        
        # Format context
        context = "\n".join([doc['document'] for doc in results])
        
        return context
    
    def _query_external_llm(self, model_name, user_query, local_output, context):
        """Query external LLM with local output and context"""
        # Get external config for model
        external_config = self._get_external_config(model_name)
        
        # Get or create API client
        client = self._get_external_client(external_config)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": "/think"},
            {"role": "user", "content": f"Local draft:\n{local_output}\n\nContext:\n{context}\n\nUser query:\n{user_query}"}
        ]
        
        # Call external API
        response = client.generate(
            messages=messages,
            model=external_config['model_id'],
            temperature=0.6,
            max_tokens=4096,
            stream=True
        )
        
        return response
    
    def _check_user_model_access(self, user_id, model_name):
        """Check if user has access to model"""
        # Check if user owns the model
        # Check if model is shared with user
        # Check if model is public
        access = db.get_user_model_access(user_id, model_name)
        return access is not None
    
    def get_user_models(self, user_id):
        """Get all models accessible to user"""
        # Get owned models
        owned_models = db.get_models_by_user(user_id)
        
        # Get shared models
        shared_models = db.get_shared_models(user_id)
        
        # Get public models
        public_models = db.get_public_models()
        
        return {
            'owned': owned_models,
            'shared': shared_models,
            'public': public_models
        }
```

### 3.4 External Model API Clients (`backend/services/external_model_clients.py`)

```python
from openai import OpenAI
import anthropic
import requests

class BaseExternalClient:
    """Base class for external API clients"""
    
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url
    
    def generate(self, messages, model, **kwargs):
        raise NotImplementedError()

class NVIDIAAPIClient(BaseExternalClient):
    """NVIDIA API client"""
    
    def __init__(self, api_key):
        super().__init__(api_key, "https://integrate.api.nvidia.com/v1")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
    
    def generate(self, messages, model, **kwargs):
        """Generate response from NVIDIA API"""
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.6),
            max_tokens=kwargs.get('max_tokens', 4096),
            stream=kwargs.get('stream', False)
        )
        
        if kwargs.get('stream', False):
            return self._stream_response(completion)
        else:
            return completion.choices[0].message.content
    
    def _stream_response(self, completion):
        """Stream response from API"""
        full_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_text += text
                yield text
        return full_text

class OpenAIAPIClient(BaseExternalClient):
    """OpenAI API client"""
    
    def __init__(self, api_key):
        super().__init__(api_key, "https://api.openai.com/v1")
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, messages, model, **kwargs):
        """Generate response from OpenAI API"""
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.6),
            max_tokens=kwargs.get('max_tokens', 4096),
            stream=kwargs.get('stream', False)
        )
        
        if kwargs.get('stream', False):
            return self._stream_response(completion)
        else:
            return completion.choices[0].message.content
    
    def _stream_response(self, completion):
        """Stream response from API"""
        full_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_text += text
                yield text
        return full_text

class AnthropicAPIClient(BaseExternalClient):
    """Anthropic API client"""
    
    def __init__(self, api_key):
        super().__init__(api_key, "https://api.anthropic.com")
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate(self, messages, model, **kwargs):
        """Generate response from Anthropic API"""
        # Convert messages format
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        user_messages = [m for m in messages if m['role'] != 'system']
        
        completion = self.client.messages.create(
            model=model,
            system=system_message,
            messages=user_messages,
            temperature=kwargs.get('temperature', 0.6),
            max_tokens=kwargs.get('max_tokens', 4096),
            stream=kwargs.get('stream', False)
        )
        
        if kwargs.get('stream', False):
            return self._stream_response(completion)
        else:
            return completion.content[0].text
    
    def _stream_response(self, completion):
        """Stream response from API"""
        full_text = ""
        for chunk in completion:
            if chunk.type == 'content_block_delta':
                text = chunk.delta.text
                full_text += text
                yield text
        return full_text

class MistralAPIClient(BaseExternalClient):
    """Mistral API client"""
    
    def __init__(self, api_key):
        super().__init__(api_key, "https://api.mistral.ai/v1")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
    
    def generate(self, messages, model, **kwargs):
        """Generate response from Mistral API"""
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.6),
            max_tokens=kwargs.get('max_tokens', 4096),
            stream=kwargs.get('stream', False)
        )
        
        if kwargs.get('stream', False):
            return self._stream_response(completion)
        else:
            return completion.choices[0].message.content
    
    def _stream_response(self, completion):
        """Stream response from API"""
        full_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_text += text
                yield text
        return full_text

# Client factory
class ExternalClientFactory:
    """Factory for creating external API clients"""
    
    @staticmethod
    def create_client(provider, api_key):
        """Create appropriate client based on provider"""
        clients = {
            'nvidia': NVIDIAAPIClient,
            'openai': OpenAIAPIClient,
            'anthropic': AnthropicAPIClient,
            'mistral': MistralAPIClient
        }
        
        client_class = clients.get(provider.lower())
        if not client_class:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return client_class(api_key)
```


### 3.5 API Key Management (`backend/services/api_key_manager.py`)

```python
from cryptography.fernet import Fernet
import os
import base64

class APIKeyManager:
    """
    Handles encryption and decryption of API keys
    """
    
    def __init__(self):
        # Get encryption key from environment
        encryption_key = os.getenv('API_KEY_ENCRYPTION_KEY')
        if not encryption_key:
            # Generate new key if not exists
            encryption_key = Fernet.generate_key().decode()
            print(f"Generated new encryption key: {encryption_key}")
            print("Please add this to your .env file as API_KEY_ENCRYPTION_KEY")
        
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def encrypt_api_key(self, api_key):
        """Encrypt API key using Fernet encryption"""
        if not api_key:
            return None
        
        encrypted = self.cipher.encrypt(api_key.encode())
        return encrypted.decode()
    
    def decrypt_api_key(self, encrypted_key):
        """Decrypt API key"""
        if not encrypted_key:
            return None
        
        decrypted = self.cipher.decrypt(encrypted_key.encode())
        return decrypted.decode()
    
    def rotate_encryption_key(self, new_key):
        """Rotate encryption key and re-encrypt all API keys"""
        # Get all encrypted API keys from database
        all_configs = db.get_all_external_configs()
        
        # Create new cipher
        new_cipher = Fernet(new_key.encode())
        
        # Re-encrypt all keys
        for config in all_configs:
            # Decrypt with old key
            decrypted = self.decrypt_api_key(config['api_key_encrypted'])
            # Encrypt with new key
            new_encrypted = new_cipher.encrypt(decrypted.encode()).decode()
            # Update database
            db.update_external_config(config['id'], {
                'api_key_encrypted': new_encrypted
            })
        
        # Update cipher
        self.cipher = new_cipher
        
        return True
```

### 3.6 Hybrid Training Executor (`backend/services/hybrid_training_executor.py`)

```python
import threading
from datetime import datetime

class HybridTrainingExecutor:
    """
    Orchestrates hybrid training (LoRA + RAG + External Model)
    """
    
    def __init__(self):
        self.external_service = ExternalModelService()
        self.training_executor = TrainingExecutor()  # Existing LoRA executor
        self.running_jobs = {}
    
    def start_hybrid_training(self, user_id, job_data):
        """Start hybrid training job"""
        try:
            # Validate user permissions
            if not user_service.check_permission(user_id, 'hybrid_training', 'create'):
                raise PermissionError('User does not have hybrid training permission')
            
            # Create hybrid job record
            hybrid_job_id = db.create_hybrid_training_job({
                'user_id': user_id,
                'name': job_data.get('name'),
                'description': job_data.get('description'),
                'status': 'PENDING',
                'progress': 0.0
            })
            
            # Update status to RUNNING
            db.update_hybrid_training_job(hybrid_job_id, {
                'status': 'RUNNING',
                'started_at': datetime.now().isoformat()
            })
            
            # Start training thread
            training_thread = threading.Thread(
                target=self._execute_hybrid_training,
                args=(user_id, hybrid_job_id, job_data)
            )
            training_thread.daemon = True
            training_thread.start()
            
            self.running_jobs[hybrid_job_id] = {
                'thread': training_thread,
                'status': 'RUNNING',
                'user_id': user_id
            }
            
            return hybrid_job_id
            
        except Exception as e:
            print(f"Error starting hybrid training: {e}")
            raise
    
    def _execute_hybrid_training(self, user_id, hybrid_job_id, job_data):
        """Execute the hybrid training process"""
        try:
            print(f"🚀 Starting hybrid training for user {user_id}, job {hybrid_job_id}")
            
            # Step 1: Train local LoRA model (20% progress)
            print("📚 Step 1: Training local LoRA model...")
            db.update_hybrid_training_job(hybrid_job_id, {'progress': 0.1})
            
            lora_job_id = self._train_local_lora(user_id, job_data)
            local_lora_model = self._wait_for_lora_completion(lora_job_id)
            
            db.update_hybrid_training_job(hybrid_job_id, {
                'progress': 0.2,
                'job_id': lora_job_id,
                'local_lora_model': local_lora_model
            })
            
            # Step 2: Setup RAG knowledge base (40% progress)
            print("🗄️ Step 2: Setting up RAG knowledge base...")
            db.update_hybrid_training_job(hybrid_job_id, {'progress': 0.3})
            
            rag_collection = self._setup_rag_knowledge_base(user_id, hybrid_job_id, job_data)
            
            db.update_hybrid_training_job(hybrid_job_id, {
                'progress': 0.4,
                'rag_collection_name': rag_collection
            })
            
            # Step 3: Configure external model (60% progress)
            print("🌐 Step 3: Configuring external model...")
            db.update_hybrid_training_job(hybrid_job_id, {'progress': 0.5})
            
            external_config_id = self._configure_external_model(user_id, job_data)
            
            db.update_hybrid_training_job(hybrid_job_id, {
                'progress': 0.6,
                'external_model_config_id': external_config_id
            })
            
            # Step 4: Test hybrid pipeline (80% progress)
            print("🧪 Step 4: Testing hybrid pipeline...")
            db.update_hybrid_training_job(hybrid_job_id, {'progress': 0.7})
            
            test_results = self._test_hybrid_pipeline(hybrid_job_id, job_data)
            
            db.update_hybrid_training_job(hybrid_job_id, {'progress': 0.8})
            
            # Step 5: Create model profile (90% progress)
            print("👤 Step 5: Creating model profile...")
            db.update_hybrid_training_job(hybrid_job_id, {'progress': 0.9})
            
            model_profile = self._create_hybrid_model_profile(
                user_id, hybrid_job_id, local_lora_model, job_data
            )
            
            # Mark as completed (100% progress)
            db.update_hybrid_training_job(hybrid_job_id, {
                'status': 'COMPLETED',
                'progress': 1.0,
                'completed_at': datetime.now().isoformat()
            })
            
            print(f"✅ Hybrid training completed successfully for job {hybrid_job_id}")
            
        except Exception as e:
            print(f"❌ Hybrid training failed for job {hybrid_job_id}: {e}")
            db.update_hybrid_training_job(hybrid_job_id, {
                'status': 'FAILED',
                'error_message': str(e),
                'completed_at': datetime.now().isoformat()
            })
        finally:
            # Clean up running jobs
            if hybrid_job_id in self.running_jobs:
                del self.running_jobs[hybrid_job_id]
    
    def _train_local_lora(self, user_id, job_data):
        """Train local LoRA model using existing training executor"""
        # Create training job
        lora_job_data = {
            'name': job_data.get('name') + '_lora',
            'user_id': user_id,
            'base_model': job_data.get('base_model', 'microsoft/DialoGPT-medium'),
            'training_type': 'lora',
            'config': job_data.get('lora_config', {})
        }
        
        # Start training
        job_id = self.training_executor.start_training(None, lora_job_data)
        return job_id
    
    def _wait_for_lora_completion(self, job_id):
        """Wait for LoRA training to complete"""
        import time
        
        while True:
            job = db.get_training_job(job_id)
            if job['status'] in ['COMPLETED', 'FAILED']:
                if job['status'] == 'FAILED':
                    raise Exception(f"LoRA training failed: {job.get('error_message')}")
                return job.get('actual_model_name') or job.get('model_name')
            time.sleep(5)
    
    def _setup_rag_knowledge_base(self, user_id, hybrid_job_id, job_data):
        """Setup RAG knowledge base"""
        collection_name = f"user_{user_id}_hybrid_{hybrid_job_id}_kb"
        
        # Get dataset samples
        dataset_ids = job_data.get('selectedDatasets', [])
        all_samples = []
        
        for dataset_id in dataset_ids:
            dataset = db.get_dataset(dataset_id)
            if dataset:
                samples = dataset.get('metadata', {}).get('all_samples', [])
                all_samples.extend(samples)
        
        # Create knowledge base
        chromadb_service.create_knowledge_base(hybrid_job_id, all_samples)
        
        return collection_name
    
    def _configure_external_model(self, user_id, job_data):
        """Configure external model for user"""
        external_config = {
            'user_id': user_id,
            'name': job_data.get('external_model_name'),
            'provider': job_data.get('external_provider'),
            'model_id': job_data.get('external_model_id'),
            'api_key_encrypted': api_key_manager.encrypt_api_key(
                job_data.get('api_key')
            ),
            'base_url': job_data.get('base_url')
        }
        
        config_id = db.add_external_model_config(external_config)
        return config_id
    
    def _test_hybrid_pipeline(self, hybrid_job_id, job_data):
        """Test the hybrid pipeline"""
        test_query = job_data.get('test_query', 'Test the hybrid model')
        
        # Get hybrid job details
        hybrid_job = db.get_hybrid_training_job(hybrid_job_id)
        
        # Test query
        result = self.external_service.query_hybrid_model(
            hybrid_job['user_id'],
            hybrid_job['local_lora_model'],
            test_query
        )
        
        return {
            'test_query': test_query,
            'result': result
        }
    
    def _create_hybrid_model_profile(self, user_id, hybrid_job_id, model_name, job_data):
        """Create model profile for hybrid model"""
        profile_data = {
            'model_name': model_name,
            'user_id': user_id,
            'training_job_id': hybrid_job_id,
            'avatar_path': job_data.get('avatar_path'),
            'avatar_url': job_data.get('avatar_url'),
            'metadata': {
                'type': 'hybrid',
                'has_lora': True,
                'has_rag': True,
                'external_provider': job_data.get('external_provider')
            }
        }
        
        profile_id = db.add_model_profile(profile_data)
        return profile_id
```

---

## 4. API Endpoints

### 4.1 Authentication Endpoints

```python
# Register new user
@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """
    Register a new user
    
    Request body:
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "secure_password",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    data = request.get_json()
    
    try:
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create user
        user = user_service.create_user(data)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Login user
@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """
    Login user and return JWT token
    
    Request body:
    {
        "username": "john_doe",
        "password": "secure_password"
    }
    """
    data = request.get_json()
    
    try:
        username = data.get('username')
        password = data.get('password')
        
        # Authenticate user
        session = user_service.authenticate_user(username, password)
        
        return jsonify({
            'success': True,
            'token': session['token'],
            'user': session['user']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Invalid credentials'}), 401

# Logout user
@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout_user():
    """
    Logout user and invalidate token
    """
    token = request.headers.get('Authorization').split(' ')[1]
    
    try:
        auth_service.invalidate_token(token)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Refresh token
@app.route('/api/auth/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """
    Refresh JWT token
    """
    old_token = request.headers.get('Authorization').split(' ')[1]
    
    try:
        new_token = auth_service.refresh_token(old_token)
        return jsonify({'token': new_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### 4.2 User Management Endpoints

```python
# Get user profile
@app.route('/api/users/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """Get current user profile with roles and permissions"""
    user_id = g.user['user_id']
    
    try:
        user = db.get_user(user_id)
        roles = user_service.get_user_roles(user_id)
        permissions = user_service.get_user_permissions(user_id)
        
        return jsonify({
            'success': True,
            'user': user,
            'roles': roles,
            'permissions': permissions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Update user profile
@app.route('/api/users/profile', methods=['PUT'])
@require_auth
def update_user_profile():
    """Update user profile"""
    user_id = g.user['user_id']
    data = request.get_json()
    
    try:
        updated_user = user_service.update_user_profile(user_id, data)
        return jsonify({'success': True, 'user': updated_user}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get user models
@app.route('/api/users/models', methods=['GET'])
@require_auth
def get_user_models():
    """Get all models accessible to user"""
    user_id = g.user['user_id']
    
    try:
        models = external_service.get_user_models(user_id)
        return jsonify({'success': True, 'models': models}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```


### 4.3 External Model Endpoints

```python
# Get external models
@app.route('/api/external-models', methods=['GET'])
@require_auth
@require_permission('external_apis', 'read')
def get_external_models():
    """Get user's external model configurations"""
    user_id = g.user['user_id']
    
    try:
        configs = db.get_external_model_configs_by_user(user_id)
        
        # Decrypt API keys (mask for security)
        for config in configs:
            if config.get('api_key_encrypted'):
                # Mask API key (show only last 4 characters)
                decrypted = api_key_manager.decrypt_api_key(config['api_key_encrypted'])
                config['api_key_masked'] = '***' + decrypted[-4:] if len(decrypted) > 4 else '***'
                del config['api_key_encrypted']
        
        return jsonify({'success': True, 'configs': configs}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Add external model configuration
@app.route('/api/external-models', methods=['POST'])
@require_auth
@require_permission('external_apis', 'create')
def add_external_model():
    """
    Add new external model configuration
    
    Request body:
    {
        "name": "My NVIDIA Model",
        "provider": "nvidia",
        "model_id": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
        "api_key": "nvapi-xxx",
        "base_url": "https://integrate.api.nvidia.com/v1"
    }
    """
    user_id = g.user['user_id']
    data = request.get_json()
    
    try:
        # Encrypt API key
        encrypted_key = api_key_manager.encrypt_api_key(data.get('api_key'))
        
        config_data = {
            'user_id': user_id,
            'name': data.get('name'),
            'provider': data.get('provider'),
            'model_id': data.get('model_id'),
            'api_key_encrypted': encrypted_key,
            'base_url': data.get('base_url'),
            'is_active': True
        }
        
        config_id = db.add_external_model_config(config_data)
        
        return jsonify({'success': True, 'config_id': config_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Update external model configuration
@app.route('/api/external-models/<int:config_id>', methods=['PUT'])
@require_auth
@require_permission('external_apis', 'update')
def update_external_model(config_id):
    """Update external model configuration"""
    user_id = g.user['user_id']
    data = request.get_json()
    
    try:
        # Verify ownership
        config = db.get_external_model_config(config_id)
        if config['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Encrypt API key if provided
        if data.get('api_key'):
            data['api_key_encrypted'] = api_key_manager.encrypt_api_key(data['api_key'])
            del data['api_key']
        
        db.update_external_model_config(config_id, data)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Delete external model configuration
@app.route('/api/external-models/<int:config_id>', methods=['DELETE'])
@require_auth
@require_permission('external_apis', 'delete')
def delete_external_model(config_id):
    """Delete external model configuration"""
    user_id = g.user['user_id']
    
    try:
        # Verify ownership
        config = db.get_external_model_config(config_id)
        if config['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.delete_external_model_config(config_id)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### 4.4 Hybrid Training Endpoints

```python
# Start hybrid training
@app.route('/api/hybrid-training', methods=['POST'])
@require_auth
@require_permission('hybrid_training', 'create')
def start_hybrid_training():
    """
    Start hybrid training job
    
    Request body:
    {
        "name": "My Hybrid Model",
        "description": "Custom hybrid model",
        "base_model": "microsoft/DialoGPT-medium",
        "selectedDatasets": [1, 2, 3],
        "external_model_name": "My External Model",
        "external_provider": "nvidia",
        "external_model_id": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
        "api_key": "nvapi-xxx",
        "lora_config": {
            "rank": 8,
            "alpha": 32,
            "dropout": 0.05
        },
        "test_query": "Test this model"
    }
    """
    user_id = g.user['user_id']
    data = request.get_json()
    
    try:
        # Start hybrid training
        hybrid_job_id = hybrid_executor.start_hybrid_training(user_id, data)
        
        return jsonify({
            'success': True,
            'hybrid_job_id': hybrid_job_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get hybrid training jobs
@app.route('/api/hybrid-training', methods=['GET'])
@require_auth
@require_permission('hybrid_training', 'read')
def get_hybrid_training_jobs():
    """Get user's hybrid training jobs"""
    user_id = g.user['user_id']
    
    try:
        jobs = db.get_hybrid_training_jobs_by_user(user_id)
        return jsonify({'success': True, 'jobs': jobs}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get hybrid training job status
@app.route('/api/hybrid-training/<int:job_id>', methods=['GET'])
@require_auth
@require_permission('hybrid_training', 'read')
def get_hybrid_training_job(job_id):
    """Get hybrid training job details"""
    user_id = g.user['user_id']
    
    try:
        job = db.get_hybrid_training_job(job_id)
        
        # Verify ownership
        if job['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({'success': True, 'job': job}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Stop hybrid training job
@app.route('/api/hybrid-training/<int:job_id>/stop', methods=['POST'])
@require_auth
@require_permission('hybrid_training', 'update')
def stop_hybrid_training_job(job_id):
    """Stop running hybrid training job"""
    user_id = g.user['user_id']
    
    try:
        job = db.get_hybrid_training_job(job_id)
        
        # Verify ownership
        if job['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        hybrid_executor.stop_training(job_id)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### 4.5 Hybrid Model Query Endpoints

```python
# Query hybrid model
@app.route('/api/hybrid-models/<model_name>/query', methods=['POST'])
@require_auth
@require_permission('models', 'read')
def query_hybrid_model(model_name):
    """
    Query hybrid model
    
    Request body:
    {
        "query": "Design a landing page",
        "stream": true
    }
    """
    user_id = g.user['user_id']
    data = request.get_json()
    
    try:
        # Check user access
        if not external_service._check_user_model_access(user_id, model_name):
            return jsonify({'error': 'Unauthorized access to model'}), 403
        
        query = data.get('query')
        stream = data.get('stream', False)
        
        # Execute hybrid pipeline
        result = external_service.query_hybrid_model(user_id, model_name, query)
        
        if stream:
            # Return streaming response
            def generate():
                for chunk in result:
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        else:
            return jsonify({'success': True, 'result': result}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get model usage history
@app.route('/api/hybrid-models/<model_name>/usage', methods=['GET'])
@require_auth
def get_model_usage(model_name):
    """Get model usage history for user"""
    user_id = g.user['user_id']
    
    try:
        usage = db.get_model_usage_by_user(user_id, model_name)
        return jsonify({'success': True, 'usage': usage}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### 4.6 Model Sharing Endpoints

```python
# Share model with user
@app.route('/api/models/<model_name>/share', methods=['POST'])
@require_auth
def share_model(model_name):
    """
    Share model with another user
    
    Request body:
    {
        "share_with_user_id": 5,
        "expires_at": "2024-12-31T23:59:59"
    }
    """
    user_id = g.user['user_id']
    data = request.get_json()
    
    try:
        # Verify ownership
        access = db.get_user_model_access(user_id, model_name)
        if not access or access['access_type'] != 'owner':
            return jsonify({'error': 'Only owner can share model'}), 403
        
        # Create shared access
        share_data = {
            'user_id': data.get('share_with_user_id'),
            'model_name': model_name,
            'access_type': 'shared',
            'granted_by': user_id,
            'expires_at': data.get('expires_at')
        }
        
        db.add_user_model_access(share_data)
        
        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Revoke model access
@app.route('/api/models/<model_name>/share/<int:target_user_id>', methods=['DELETE'])
@require_auth
def revoke_model_access(model_name, target_user_id):
    """Revoke shared access to model"""
    user_id = g.user['user_id']
    
    try:
        # Verify ownership
        access = db.get_user_model_access(user_id, model_name)
        if not access or access['access_type'] != 'owner':
            return jsonify({'error': 'Only owner can revoke access'}), 403
        
        db.delete_user_model_access(target_user_id, model_name)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get shared users
@app.route('/api/models/<model_name>/shares', methods=['GET'])
@require_auth
def get_model_shares(model_name):
    """Get list of users with access to model"""
    user_id = g.user['user_id']
    
    try:
        # Verify ownership
        access = db.get_user_model_access(user_id, model_name)
        if not access or access['access_type'] != 'owner':
            return jsonify({'error': 'Only owner can view shares'}), 403
        
        shares = db.get_model_shared_users(model_name)
        
        return jsonify({'success': True, 'shares': shares}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

---

## 5. Data Relationships

### 5.1 User-Centric Data Flow

```python
class UserDataRelationships:
    """
    Manages user-centric data relationships
    """
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()
    
    def get_user_datasets(self):
        """Get all datasets owned by user"""
        owned_datasets = self.db.get_datasets_by_user(self.user_id)
        
        # Also get shared datasets
        shared_datasets = self.db.get_shared_datasets(self.user_id)
        
        return {
            'owned': owned_datasets,
            'shared': shared_datasets
        }
    
    def get_user_training_jobs(self):
        """Get all training jobs by user"""
        jobs = self.db.get_training_jobs_by_user(self.user_id)
        
        # Enrich with dataset info
        for job in jobs:
            if job.get('dataset_id'):
                job['dataset'] = self.db.get_dataset(job['dataset_id'])
        
        return jobs
    
    def get_user_hybrid_jobs(self):
        """Get user's hybrid training jobs"""
        jobs = self.db.get_hybrid_training_jobs_by_user(self.user_id)
        
        # Enrich with related data
        for job in jobs:
            if job.get('job_id'):
                job['base_training_job'] = self.db.get_training_job(job['job_id'])
            if job.get('external_model_config_id'):
                config = self.db.get_external_model_config(job['external_model_config_id'])
                # Mask API key
                if config.get('api_key_encrypted'):
                    config['api_key_masked'] = '***'
                    del config['api_key_encrypted']
                job['external_config'] = config
        
        return jobs
    
    def get_user_models(self):
        """Get all models accessible to user"""
        # Get owned models
        owned_models = []
        training_jobs = self.get_user_training_jobs()
        for job in training_jobs:
            if job.get('actual_model_name'):
                owned_models.append({
                    'name': job['actual_model_name'],
                    'type': job.get('training_type'),
                    'access_type': 'owner',
                    'training_job_id': job['id']
                })
        
        # Get shared models
        shared_access = self.db.get_user_model_access_list(self.user_id, 'shared')
        shared_models = [
            {
                'name': access['model_name'],
                'access_type': 'shared',
                'granted_by': access['granted_by'],
                'expires_at': access.get('expires_at')
            }
            for access in shared_access
        ]
        
        # Get public models
        public_models = self.db.get_public_models()
        
        return {
            'owned': owned_models,
            'shared': shared_models,
            'public': public_models
        }
    
    def get_user_external_configs(self):
        """Get user's external model configurations"""
        configs = self.db.get_external_model_configs_by_user(self.user_id)
        
        # Mask API keys
        for config in configs:
            if config.get('api_key_encrypted'):
                decrypted = api_key_manager.decrypt_api_key(config['api_key_encrypted'])
                config['api_key_masked'] = '***' + decrypted[-4:] if len(decrypted) > 4 else '***'
                del config['api_key_encrypted']
        
        return configs
    
    def get_user_dashboard_data(self):
        """Get all dashboard data for user"""
        return {
            'datasets': self.get_user_datasets(),
            'training_jobs': self.get_user_training_jobs(),
            'hybrid_jobs': self.get_user_hybrid_jobs(),
            'models': self.get_user_models(),
            'external_configs': self.get_user_external_configs()
        }
```

### 5.2 Data Ownership and Access Control

```python
class DataAccessControl:
    """
    Manages data ownership and access control
    """
    
    def __init__(self):
        self.db = Database()
        self.user_service = UserService()
    
    def verify_dataset_access(self, user_id, dataset_id):
        """Verify user has access to dataset"""
        dataset = self.db.get_dataset(dataset_id)
        
        if not dataset:
            return False
        
        # Owner access
        if dataset.get('user_id') == user_id:
            return True
        
        # Public dataset access
        if dataset.get('is_public'):
            return True
        
        # Shared access (future implementation)
        # Check if dataset is shared with user
        
        return False
    
    def verify_model_access(self, user_id, model_name):
        """Verify user has access to model"""
        access = self.db.get_user_model_access(user_id, model_name)
        
        if not access:
            # Check if it's a public model
            model_profile = self.db.get_model_profile_by_name(model_name)
            if model_profile and model_profile.get('is_public'):
                return True
            return False
        
        # Check expiration
        if access.get('expires_at'):
            if datetime.now() > datetime.fromisoformat(access['expires_at']):
                return False
        
        return True
    
    def verify_training_job_access(self, user_id, job_id):
        """Verify user has access to training job"""
        job = self.db.get_training_job(job_id)
        
        if not job:
            return False
        
        # Owner access
        if job.get('user_id') == user_id:
            return True
        
        # Admin access
        if self.user_service.check_permission(user_id, 'training', 'read'):
            return True
        
        return False
    
    def verify_external_config_access(self, user_id, config_id):
        """Verify user has access to external config"""
        config = self.db.get_external_model_config(config_id)
        
        if not config:
            return False
        
        # Owner access
        if config.get('user_id') == user_id:
            return True
        
        # Shared access
        if config.get('is_shared'):
            # Additional sharing logic
            pass
        
        return False
```


---

## 6. Security Implementation

### 6.1 Authentication Middleware

```python
# backend/middleware/auth_middleware.py
from functools import wraps
from flask import request, g, jsonify

class AuthMiddleware:
    """
    JWT authentication middleware
    """
    
    def __init__(self, auth_service):
        self.auth_service = auth_service
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'error': 'No authorization header'}), 401
            
            try:
                # Extract token (format: "Bearer <token>")
                token = auth_header.split(' ')[1]
                
                # Verify token
                payload = self.auth_service.verify_token(token)
                
                # Add user info to request context
                g.user = payload
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': 'Invalid or expired token'}), 401
        
        return decorated_function
    
    def require_permission(self, resource, action):
        """Decorator to require specific permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Check if user is authenticated
                if not hasattr(g, 'user'):
                    return jsonify({'error': 'Not authenticated'}), 401
                
                user_id = g.user['user_id']
                
                # Check permission
                if not user_service.check_permission(user_id, resource, action):
                    return jsonify({'error': f'No permission for {resource}.{action}'}), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        
        return decorator
    
    def require_role(self, role_name):
        """Decorator to require specific role"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Check if user is authenticated
                if not hasattr(g, 'user'):
                    return jsonify({'error': 'Not authenticated'}), 401
                
                user_id = g.user['user_id']
                
                # Check role
                user_roles = user_service.get_user_roles(user_id)
                if role_name not in [role['name'] for role in user_roles]:
                    return jsonify({'error': f'Role {role_name} required'}), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        
        return decorator

# Create global instances
auth_middleware = AuthMiddleware(auth_service)
require_auth = auth_middleware.require_auth
require_permission = auth_middleware.require_permission
require_role = auth_middleware.require_role
```

### 6.2 API Key Encryption

```python
# backend/services/api_key_manager.py (Expanded)
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64

class APIKeyManager:
    """
    Handles encryption, decryption, and rotation of API keys
    """
    
    def __init__(self):
        # Get encryption key from environment
        encryption_key = os.getenv('API_KEY_ENCRYPTION_KEY')
        
        if not encryption_key:
            # Generate new key if not exists
            encryption_key = Fernet.generate_key().decode()
            print(f"🔑 Generated new encryption key")
            print(f"⚠️  Add this to .env: API_KEY_ENCRYPTION_KEY={encryption_key}")
        
        self.cipher = Fernet(
            encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        )
        
        # Key derivation for additional security
        self.salt = os.getenv('API_KEY_SALT', 'ai-refinement-salt').encode()
    
    def encrypt_api_key(self, api_key):
        """Encrypt API key using Fernet encryption"""
        if not api_key:
            return None
        
        try:
            encrypted = self.cipher.encrypt(api_key.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"❌ Error encrypting API key: {e}")
            raise
    
    def decrypt_api_key(self, encrypted_key):
        """Decrypt API key"""
        if not encrypted_key:
            return None
        
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"❌ Error decrypting API key: {e}")
            raise
    
    def rotate_encryption_key(self, new_key):
        """
        Rotate encryption key and re-encrypt all API keys
        This is a critical operation and should be done carefully
        """
        print("🔄 Starting encryption key rotation...")
        
        # Get all encrypted API keys from database
        all_configs = db.get_all_external_configs()
        
        # Create new cipher
        new_cipher = Fernet(new_key.encode())
        
        # Re-encrypt all keys
        rotated_count = 0
        failed_count = 0
        
        for config in all_configs:
            try:
                # Decrypt with old key
                decrypted = self.decrypt_api_key(config['api_key_encrypted'])
                
                # Encrypt with new key
                new_encrypted = new_cipher.encrypt(decrypted.encode()).decode()
                
                # Update database
                db.update_external_config(config['id'], {
                    'api_key_encrypted': new_encrypted
                })
                
                rotated_count += 1
                
            except Exception as e:
                print(f"❌ Failed to rotate key for config {config['id']}: {e}")
                failed_count += 1
        
        # Update cipher
        self.cipher = new_cipher
        
        print(f"✅ Key rotation complete: {rotated_count} rotated, {failed_count} failed")
        
        return {
            'rotated': rotated_count,
            'failed': failed_count
        }
    
    def derive_key(self, password):
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

# Global instance
api_key_manager = APIKeyManager()
```

### 6.3 Rate Limiting and Usage Tracking

```python
# backend/middleware/rate_limit_middleware.py
from functools import wraps
from flask import request, jsonify, g
import time
from collections import defaultdict

class RateLimiter:
    """
    Rate limiting for API endpoints
    """
    
    def __init__(self):
        # Simple in-memory rate limiting (use Redis for production)
        self.request_counts = defaultdict(list)
        self.limits = {
            'default': {'requests': 100, 'window': 60},  # 100 req/min
            'training': {'requests': 10, 'window': 3600},  # 10 req/hour
            'query': {'requests': 50, 'window': 60},  # 50 req/min
        }
    
    def check_rate_limit(self, user_id, limit_type='default'):
        """Check if user is within rate limit"""
        now = time.time()
        limit_config = self.limits.get(limit_type, self.limits['default'])
        
        key = f"{user_id}:{limit_type}"
        
        # Clean old requests outside window
        self.request_counts[key] = [
            req_time for req_time in self.request_counts[key]
            if now - req_time < limit_config['window']
        ]
        
        # Check if within limit
        if len(self.request_counts[key]) >= limit_config['requests']:
            return False
        
        # Add current request
        self.request_counts[key].append(now)
        
        return True
    
    def rate_limit(self, limit_type='default'):
        """Decorator for rate limiting"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(g, 'user'):
                    return jsonify({'error': 'Not authenticated'}), 401
                
                user_id = g.user['user_id']
                
                if not self.check_rate_limit(user_id, limit_type):
                    limit_config = self.limits[limit_type]
                    return jsonify({
                        'error': f'Rate limit exceeded: {limit_config["requests"]} requests per {limit_config["window"]} seconds'
                    }), 429
                
                return f(*args, **kwargs)
            
            return decorated_function
        
        return decorator

# Global rate limiter
rate_limiter = RateLimiter()
```

### 6.4 Audit Logging

```python
# backend/services/audit_service.py
from datetime import datetime
import json

class AuditService:
    """
    Audit logging for security and compliance
    """
    
    def __init__(self):
        self.db = Database()
    
    def log_event(self, user_id, event_type, resource, action, details=None):
        """Log audit event"""
        event = {
            'user_id': user_id,
            'event_type': event_type,  # 'authentication', 'authorization', 'data_access', 'model_query'
            'resource': resource,
            'action': action,
            'details': json.dumps(details) if details else None,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in database
        self.db.add_audit_log(event)
        
        # Also log to file for backup
        self._log_to_file(event)
    
    def _log_to_file(self, event):
        """Log event to file"""
        log_file = 'backend/logs/audit.log'
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def get_user_audit_log(self, user_id, limit=100):
        """Get audit log for user"""
        return self.db.get_audit_logs_by_user(user_id, limit)
    
    def get_resource_audit_log(self, resource, limit=100):
        """Get audit log for resource"""
        return self.db.get_audit_logs_by_resource(resource, limit)

# Global audit service
audit_service = AuditService()

# Audit logging decorator
def audit_log(event_type, resource, action):
    """Decorator to automatically log events"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = g.user['user_id'] if hasattr(g, 'user') else None
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Log event
            audit_service.log_event(
                user_id=user_id,
                event_type=event_type,
                resource=resource,
                action=action,
                details={'args': str(args), 'kwargs': str(kwargs)}
            )
            
            return result
        
        return decorated_function
    
    return decorator
```

---

## 7. Frontend Integration

### 7.1 Authentication Components

```javascript
// frontend/src/services/auth.js
class AuthService {
    constructor() {
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
    }
    
    async register(userData) {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.user;
        } else {
            throw new Error(data.error);
        }
    }
    
    async login(username, password) {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            this.token = data.token;
            this.user = data.user;
            
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            return data;
        } else {
            throw new Error(data.error);
        }
    }
    
    async logout() {
        await fetch('/api/auth/logout', {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${this.token}` 
            }
        });
        
        this.token = null;
        this.user = null;
        
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
    }
    
    isAuthenticated() {
        return !!this.token;
    }
    
    hasPermission(resource, action) {
        if (!this.user || !this.user.permissions) return false;
        
        const permission = `${resource}.${action}`;
        return this.user.permissions.includes(permission);
    }
    
    hasRole(roleName) {
        if (!this.user || !this.user.roles) return false;
        
        return this.user.roles.some(role => role.name === roleName);
    }
    
    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }
}

export const authService = new AuthService();
```

### 7.2 Vue Components for User Management

```vue
<!-- frontend/src/components/auth/LoginForm.vue -->
<template>
    <div class="login-form">
        <h2>Login to AI Refinement Dashboard</h2>
        
        <form @submit.prevent="handleLogin">
            <div class="form-group">
                <label for="username">Username</label>
                <input 
                    type="text" 
                    id="username" 
                    v-model="credentials.username" 
                    required 
                />
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input 
                    type="password" 
                    id="password" 
                    v-model="credentials.password" 
                    required 
                />
            </div>
            
            <div v-if="error" class="error-message">
                {{ error }}
            </div>
            
            <button type="submit" class="btn-primary">
                {{ loading ? 'Logging in...' : 'Login' }}
            </button>
        </form>
        
        <p class="register-link">
            Don't have an account? <router-link to="/register">Register</router-link>
        </p>
    </div>
</template>

<script>
import { authService } from '@/services/auth';

export default {
    name: 'LoginForm',
    data() {
        return {
            credentials: {
                username: '',
                password: ''
            },
            loading: false,
            error: null
        };
    },
    methods: {
        async handleLogin() {
            this.loading = true;
            this.error = null;
            
            try {
                await authService.login(
                    this.credentials.username, 
                    this.credentials.password
                );
                
                // Redirect to dashboard
                this.$router.push('/dashboard');
            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>
```

### 7.3 External Model Management Components

```vue
<!-- frontend/src/components/external/ExternalModelConfig.vue -->
<template>
    <div class="external-model-config">
        <h2>External Model Configurations</h2>
        
        <button @click="showAddModal = true" class="btn-primary">
            Add External Model
        </button>
        
        <div class="config-list">
            <div v-for="config in configs" :key="config.id" class="config-card">
                <h3>{{ config.name }}</h3>
                <p><strong>Provider:</strong> {{ config.provider }}</p>
                <p><strong>Model:</strong> {{ config.model_id }}</p>
                <p><strong>API Key:</strong> {{ config.api_key_masked }}</p>
                <p><strong>Status:</strong> {{ config.is_active ? 'Active' : 'Inactive' }}</p>
                
                <div class="config-actions">
                    <button @click="editConfig(config)" class="btn-secondary">Edit</button>
                    <button @click="deleteConfig(config.id)" class="btn-danger">Delete</button>
                </div>
            </div>
        </div>
        
        <!-- Add/Edit Modal -->
        <modal v-if="showAddModal" @close="showAddModal = false">
            <h3>{{ editingConfig ? 'Edit' : 'Add' }} External Model</h3>
            
            <form @submit.prevent="saveConfig">
                <div class="form-group">
                    <label>Name</label>
                    <input v-model="configForm.name" required />
                </div>
                
                <div class="form-group">
                    <label>Provider</label>
                    <select v-model="configForm.provider" required>
                        <option value="nvidia">NVIDIA</option>
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="mistral">Mistral</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Model ID</label>
                    <input v-model="configForm.model_id" required />
                </div>
                
                <div class="form-group">
                    <label>API Key</label>
                    <input type="password" v-model="configForm.api_key" required />
                </div>
                
                <div class="form-group">
                    <label>Base URL (optional)</label>
                    <input v-model="configForm.base_url" />
                </div>
                
                <button type="submit" class="btn-primary">Save</button>
            </form>
        </modal>
    </div>
</template>

<script>
import { authService } from '@/services/auth';

export default {
    name: 'ExternalModelConfig',
    data() {
        return {
            configs: [],
            showAddModal: false,
            editingConfig: null,
            configForm: {
                name: '',
                provider: 'nvidia',
                model_id: '',
                api_key: '',
                base_url: ''
            }
        };
    },
    async mounted() {
        await this.loadConfigs();
    },
    methods: {
        async loadConfigs() {
            const response = await fetch('/api/external-models', {
                headers: authService.getAuthHeaders()
            });
            
            const data = await response.json();
            if (data.success) {
                this.configs = data.configs;
            }
        },
        
        async saveConfig() {
            const method = this.editingConfig ? 'PUT' : 'POST';
            const url = this.editingConfig 
                ? `/api/external-models/${this.editingConfig.id}` 
                : '/api/external-models';
            
            const response = await fetch(url, {
                method,
                headers: authService.getAuthHeaders(),
                body: JSON.stringify(this.configForm)
            });
            
            if (response.ok) {
                await this.loadConfigs();
                this.showAddModal = false;
                this.resetForm();
            }
        },
        
        editConfig(config) {
            this.editingConfig = config;
            this.configForm = { ...config };
            this.showAddModal = true;
        },
        
        async deleteConfig(configId) {
            if (!confirm('Are you sure you want to delete this configuration?')) {
                return;
            }
            
            await fetch(`/api/external-models/${configId}`, {
                method: 'DELETE',
                headers: authService.getAuthHeaders()
            });
            
            await this.loadConfigs();
        },
        
        resetForm() {
            this.editingConfig = null;
            this.configForm = {
                name: '',
                provider: 'nvidia',
                model_id: '',
                api_key: '',
                base_url: ''
            };
        }
    }
};
</script>
```


### 7.4 Hybrid Training Components

```vue
<!-- frontend/src/components/training/HybridTrainingForm.vue -->
<template>
    <div class="hybrid-training-form">
        <h2>Create Hybrid Training Job</h2>
        
        <form @submit.prevent="startTraining">
            <!-- Basic Info -->
            <section class="form-section">
                <h3>Basic Information</h3>
                
                <div class="form-group">
                    <label>Model Name</label>
                    <input v-model="trainingData.name" required />
                </div>
                
                <div class="form-group">
                    <label>Description</label>
                    <textarea v-model="trainingData.description"></textarea>
                </div>
                
                <div class="form-group">
                    <label>Base Model</label>
                    <select v-model="trainingData.base_model">
                        <option value="microsoft/DialoGPT-medium">DialoGPT Medium</option>
                        <option value="microsoft/DialoGPT-small">DialoGPT Small</option>
                    </select>
                </div>
            </section>
            
            <!-- Dataset Selection -->
            <section class="form-section">
                <h3>Training Datasets</h3>
                
                <div class="dataset-selector">
                    <div v-for="dataset in userDatasets" :key="dataset.id" class="dataset-option">
                        <label>
                            <input 
                                type="checkbox" 
                                :value="dataset.id" 
                                v-model="trainingData.selectedDatasets" 
                            />
                            {{ dataset.name }} ({{ dataset.sample_count }} samples)
                        </label>
                    </div>
                </div>
            </section>
            
            <!-- LoRA Configuration -->
            <section class="form-section">
                <h3>LoRA Configuration</h3>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Rank</label>
                        <input type="number" v-model.number="trainingData.lora_config.rank" min="1" max="32" />
                    </div>
                    
                    <div class="form-group">
                        <label>Alpha</label>
                        <input type="number" v-model.number="trainingData.lora_config.alpha" min="1" max="64" />
                    </div>
                    
                    <div class="form-group">
                        <label>Dropout</label>
                        <input type="number" v-model.number="trainingData.lora_config.dropout" step="0.01" min="0" max="1" />
                    </div>
                </div>
            </section>
            
            <!-- External Model Configuration -->
            <section class="form-section">
                <h3>External Model</h3>
                
                <div class="form-group">
                    <label>Select External Model</label>
                    <select v-model="selectedExternalConfig" @change="updateExternalModel">
                        <option v-for="config in externalConfigs" :key="config.id" :value="config">
                            {{ config.name }} ({{ config.provider }})
                        </option>
                    </select>
                </div>
                
                <div v-if="selectedExternalConfig" class="external-model-info">
                    <p><strong>Provider:</strong> {{ selectedExternalConfig.provider }}</p>
                    <p><strong>Model:</strong> {{ selectedExternalConfig.model_id }}</p>
                    <p><strong>API Key:</strong> {{ selectedExternalConfig.api_key_masked }}</p>
                </div>
            </section>
            
            <!-- Test Query -->
            <section class="form-section">
                <h3>Test Query (Optional)</h3>
                
                <div class="form-group">
                    <label>Test Query</label>
                    <textarea 
                        v-model="trainingData.test_query" 
                        placeholder="Enter a test query to validate the hybrid model after training"
                    ></textarea>
                </div>
            </section>
            
            <div v-if="error" class="error-message">
                {{ error }}
            </div>
            
            <button type="submit" class="btn-primary" :disabled="loading">
                {{ loading ? 'Starting Training...' : 'Start Hybrid Training' }}
            </button>
        </form>
    </div>
</template>

<script>
import { authService } from '@/services/auth';

export default {
    name: 'HybridTrainingForm',
    data() {
        return {
            trainingData: {
                name: '',
                description: '',
                base_model: 'microsoft/DialoGPT-medium',
                selectedDatasets: [],
                lora_config: {
                    rank: 8,
                    alpha: 32,
                    dropout: 0.05
                },
                external_model_name: '',
                external_provider: '',
                external_model_id: '',
                api_key: '',
                test_query: ''
            },
            userDatasets: [],
            externalConfigs: [],
            selectedExternalConfig: null,
            loading: false,
            error: null
        };
    },
    async mounted() {
        await this.loadUserDatasets();
        await this.loadExternalConfigs();
    },
    methods: {
        async loadUserDatasets() {
            const response = await fetch('/api/datasets', {
                headers: authService.getAuthHeaders()
            });
            
            const data = await response.json();
            if (data.success) {
                this.userDatasets = data.datasets.filter(ds => ds.user_id === authService.user.id);
            }
        },
        
        async loadExternalConfigs() {
            const response = await fetch('/api/external-models', {
                headers: authService.getAuthHeaders()
            });
            
            const data = await response.json();
            if (data.success) {
                this.externalConfigs = data.configs;
            }
        },
        
        updateExternalModel() {
            if (this.selectedExternalConfig) {
                this.trainingData.external_model_name = this.selectedExternalConfig.name;
                this.trainingData.external_provider = this.selectedExternalConfig.provider;
                this.trainingData.external_model_id = this.selectedExternalConfig.model_id;
                this.trainingData.api_key = this.selectedExternalConfig.api_key; // Will use encrypted version
            }
        },
        
        async startTraining() {
            this.loading = true;
            this.error = null;
            
            try {
                const response = await fetch('/api/hybrid-training', {
                    method: 'POST',
                    headers: authService.getAuthHeaders(),
                    body: JSON.stringify(this.trainingData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Redirect to training job page
                    this.$router.push(`/hybrid-training/${data.hybrid_job_id}`);
                } else {
                    this.error = data.error;
                }
            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>
```

### 7.5 Permission-Based UI Components

```vue
<!-- frontend/src/components/common/PermissionGuard.vue -->
<template>
    <div v-if="hasPermission">
        <slot></slot>
    </div>
    <div v-else-if="showFallback">
        <slot name="fallback">
            <p class="permission-denied">You don't have permission to access this feature.</p>
        </slot>
    </div>
</template>

<script>
import { authService } from '@/services/auth';

export default {
    name: 'PermissionGuard',
    props: {
        resource: {
            type: String,
            required: true
        },
        action: {
            type: String,
            required: true
        },
        showFallback: {
            type: Boolean,
            default: false
        }
    },
    computed: {
        hasPermission() {
            return authService.hasPermission(this.resource, this.action);
        }
    }
};
</script>
```

```vue
<!-- frontend/src/components/common/RoleGuard.vue -->
<template>
    <div v-if="hasRole">
        <slot></slot>
    </div>
</template>

<script>
import { authService } from '@/services/auth';

export default {
    name: 'RoleGuard',
    props: {
        role: {
            type: String,
            required: true
        }
    },
    computed: {
        hasRole() {
            return authService.hasRole(this.role);
        }
    }
};
</script>
```

---

## 8. Implementation Phases

### Phase 1: User Management Foundation (Week 1-2)

**Tasks:**
1. Create user database schema and tables
2. Implement user service and authentication service
3. Create authentication middleware
4. Build registration and login API endpoints
5. Implement JWT token generation and verification
6. Create basic frontend authentication components

**Deliverables:**
- User registration and login functionality
- JWT-based authentication
- Basic user profile management

### Phase 2: RBAC Implementation (Week 3-4)

**Tasks:**
1. Create roles and permissions tables
2. Implement permission checking logic
3. Add permission decorators to existing endpoints
4. Create role and permission management API
5. Build admin panel for role management
6. Add permission-based UI components

**Deliverables:**
- Complete RBAC system
- Role and permission management
- Permission-based access control on all endpoints

### Phase 3: Data Ownership and Relationships (Week 5-6)

**Tasks:**
1. Add user_id columns to existing tables
2. Migrate existing data to include user ownership
3. Implement data access control logic
4. Update all API endpoints to filter by user
5. Create model sharing functionality
6. Build user dashboard with all owned resources

**Deliverables:**
- User-owned datasets, models, and training jobs
- Model sharing functionality
- User-centric dashboard

### Phase 4: External Model Integration (Week 7-9)

**Tasks:**
1. Create external model configuration tables
2. Implement API key encryption service
3. Build external model API clients (NVIDIA, OpenAI, Anthropic, Mistral)
4. Create external model management endpoints
5. Build frontend components for external model management
6. Implement API key rotation functionality

**Deliverables:**
- External model configuration system
- Secure API key storage
- Multiple provider support

### Phase 5: Hybrid Training System (Week 10-12)

**Tasks:**
1. Create hybrid training jobs table
2. Implement hybrid training executor
3. Integrate LoRA + RAG + External LLM pipeline
4. Build hybrid training API endpoints
5. Create hybrid training frontend components
6. Implement progress tracking and real-time updates

**Deliverables:**
- Complete hybrid training system
- LoRA + RAG + External LLM integration
- User-friendly training interface

### Phase 6: Security and Monitoring (Week 13-14)

**Tasks:**
1. Implement rate limiting
2. Add audit logging
3. Create security monitoring dashboard
4. Implement API key rotation
5. Add usage tracking and analytics
6. Perform security audit and penetration testing

**Deliverables:**
- Rate limiting and abuse prevention
- Comprehensive audit logging
- Security monitoring tools

### Phase 7: Testing and Deployment (Week 15-16)

**Tasks:**
1. Write unit tests for all services
2. Create integration tests for API endpoints
3. Perform end-to-end testing
4. Load testing and performance optimization
5. Create deployment documentation
6. Deploy to production environment

**Deliverables:**
- Comprehensive test suite
- Performance-optimized system
- Production deployment

---

## 9. Configuration and Environment Variables

```bash
# .env file configuration

# Database
DATABASE_PATH=backend/ai_dashboard.db

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7

# API Key Encryption
API_KEY_ENCRYPTION_KEY=your-fernet-encryption-key-change-this
API_KEY_SALT=ai-refinement-salt-change-this

# External API Providers (default configs)
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_BASE_URL=https://api.anthropic.com
MISTRAL_BASE_URL=https://api.mistral.ai/v1

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT_REQUESTS=100
RATE_LIMIT_DEFAULT_WINDOW=60
RATE_LIMIT_TRAINING_REQUESTS=10
RATE_LIMIT_TRAINING_WINDOW=3600

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_ENABLED=true
AUDIT_LOG_PATH=backend/logs/audit.log

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Session
SESSION_TIMEOUT=1800  # 30 minutes
```

---

## 10. Database Migrations

```python
# backend/migrations/001_add_user_management.py
def upgrade(db):
    """Add user management tables"""
    
    # Create users table
    db.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            avatar_url TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create roles table
    db.execute('''
        CREATE TABLE roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            permissions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default roles
    default_roles = [
        ('admin', 'Full system access', json.dumps(['users.*', 'models.*', 'training.*', 'external_apis.*', 'system.*'])),
        ('premium_user', 'Premium user with external API access', json.dumps(['models.*', 'training.*', 'external_apis.create', 'external_apis.read', 'external_apis.update'])),
        ('user', 'Standard user', json.dumps(['models.read', 'models.create', 'training.create', 'training.read', 'datasets.read'])),
        ('developer', 'Developer with API access', json.dumps(['models.*', 'training.*', 'external_apis.*', 'datasets.*', 'api.*']))
    ]
    
    for role in default_roles:
        db.execute('INSERT INTO roles (name, description, permissions) VALUES (?, ?, ?)', role)
    
    print("✅ User management tables created")
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

```python
# backend/tests/test_user_service.py
import unittest
from services.user_service import UserService
from services.auth_service import AuthService

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = UserService()
        self.auth_service = AuthService()
    
    def test_create_user(self):
        """Test user creation"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure_password',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        user = self.user_service.create_user(user_data)
        
        self.assertIsNotNone(user['id'])
        self.assertEqual(user['username'], 'testuser')
        self.assertTrue('password' not in user)  # Password should not be returned
    
    def test_authenticate_user(self):
        """Test user authentication"""
        # Create user first
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure_password'
        }
        self.user_service.create_user(user_data)
        
        # Authenticate
        session = self.user_service.authenticate_user('testuser', 'secure_password')
        
        self.assertIsNotNone(session['token'])
        self.assertEqual(session['user']['username'], 'testuser')
    
    def test_check_permission(self):
        """Test permission checking"""
        # Create user with specific role
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure_password'
        }
        user = self.user_service.create_user(user_data)
        
        # Assign role
        self.user_service.assign_role(user['id'], 'user', 1)  # Assigned by admin (user_id=1)
        
        # Check permissions
        self.assertTrue(self.user_service.check_permission(user['id'], 'models', 'read'))
        self.assertFalse(self.user_service.check_permission(user['id'], 'users', 'delete'))
```

### 11.2 Integration Tests

```python
# backend/tests/test_hybrid_training.py
import unittest
from services.hybrid_training_executor import HybridTrainingExecutor
from services.external_model_service import ExternalModelService

class TestHybridTraining(unittest.TestCase):
    def setUp(self):
        self.hybrid_executor = HybridTrainingExecutor()
        self.external_service = ExternalModelService()
    
    def test_start_hybrid_training(self):
        """Test starting hybrid training job"""
        job_data = {
            'name': 'Test Hybrid Model',
            'base_model': 'microsoft/DialoGPT-medium',
            'selectedDatasets': [1],
            'external_provider': 'nvidia',
            'external_model_id': 'test-model',
            'api_key': 'test-key'
        }
        
        job_id = self.hybrid_executor.start_hybrid_training(user_id=1, job_data=job_data)
        
        self.assertIsNotNone(job_id)
        
        # Check job status
        job = db.get_hybrid_training_job(job_id)
        self.assertEqual(job['status'], 'RUNNING')
```

---

## 12. Deployment Checklist

### Pre-Deployment
- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] API keys encrypted
- [ ] Default roles and permissions created
- [ ] CORS origins configured
- [ ] Rate limits configured
- [ ] Audit logging enabled

### Security
- [ ] JWT secret changed from default
- [ ] API key encryption key generated
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled

### Performance
- [ ] Database indexes created
- [ ] Redis/caching configured (if applicable)
- [ ] Rate limiting tested
- [ ] Load testing completed
- [ ] Memory usage optimized

### Monitoring
- [ ] Audit logs configured
- [ ] Error logging enabled
- [ ] Performance monitoring setup
- [ ] Alert system configured
- [ ] Backup strategy implemented

### Documentation
- [ ] API documentation updated
- [ ] User guide created
- [ ] Admin guide created
- [ ] Deployment guide finalized

---

## 13. Conclusion

This implementation plan provides a comprehensive roadmap for integrating external model training with user management and RBAC into the AI Refinement Dashboard. The system enables:

- **Multi-user support** with secure authentication and authorization
- **Role-based access control** for fine-grained permissions
- **External model integration** with secure API key management
- **Hybrid training** combining LoRA, RAG, and external LLMs
- **Data ownership** with user-specific resources and sharing
- **Security** through encryption, rate limiting, and audit logging
- **Scalability** with modular architecture and clear separation of concerns

The phased implementation approach ensures steady progress while maintaining system stability and security throughout the development process.
