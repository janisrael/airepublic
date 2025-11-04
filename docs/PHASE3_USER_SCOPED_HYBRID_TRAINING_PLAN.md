# Phase 3: User-Scoped Hybrid Training Pipeline Plan

## Overview
Create a separate external model training pipeline that integrates with the existing minion system, following the guide's dynamic LLM router architecture. This will be user-scoped and link training resources (datasets, RAG, ChromaDB) to specific minions/models per user.

## Architecture Design

### Current System Analysis
- **Local LLM Pipeline**: LoRA fine-tuning + RAG + ChromaDB (untouched)
- **Minion System**: User-scoped AI agents with external API models
- **Training Page**: Currently handles local model training only

### New External Training Pipeline
```
User Query → Local LoRA (style) → RAG (knowledge) → External LLM Router → Final Answer
```

## File Structure (Separate from existing)

### Backend Services
```
backend/services/external_training/
├── __init__.py
├── external_training_service.py          # Main service orchestrator
├── external_training_executor.py         # Training job executor
├── llm_router.py                         # Dynamic LLM provider router
├── llm_providers/
│   ├── __init__.py
│   ├── base_provider.py                  # Abstract base class
│   ├── openai_provider.py               # OpenAI adapter
│   ├── anthropic_provider.py            # Anthropic adapter
│   ├── nvidia_provider.py               # NVIDIA adapter
│   ├── huggingface_provider.py          # Hugging Face adapter
│   └── ollama_provider.py               # Ollama adapter
├── api_key_manager.py                    # Encrypted API key management
└── user_training_endpoints.py           # User-scoped API endpoints
```

### Database Extensions
```
backend/services/external_training/
├── external_training_database.py         # Training job storage
└── migrations/
    ├── add_external_training_tables.py   # New tables for external training
    └── link_training_to_minions.py       # Link training to minions
```

### Frontend Components
```
frontend/src/views/
├── ExternalTraining.vue                  # New training page for external models
└── components/
    ├── ExternalTrainingModal.vue         # Training configuration modal
    ├── ProviderSelector.vue              # Dynamic provider selection
    └── TrainingProgress.vue              # Real-time progress tracking
```

## Database Schema Extensions

### New Tables
```sql
-- External training jobs (user-scoped)
CREATE TABLE external_training_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    minion_id INTEGER,                    -- Link to external_api_models
    job_name VARCHAR(255) NOT NULL,
    description TEXT,
    provider VARCHAR(50) NOT NULL,        -- openai, anthropic, nvidia, etc.
    model_name VARCHAR(255) NOT NULL,
    training_type VARCHAR(50) DEFAULT 'hybrid', -- hybrid, rag_only, lora_only
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, RUNNING, COMPLETED, FAILED
    progress REAL DEFAULT 0.0,
    config TEXT,                          -- JSON configuration
    error_message TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (minion_id) REFERENCES external_api_models(id)
);

-- User API keys (encrypted)
CREATE TABLE user_api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL,
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, provider)
);

-- Training datasets (user-scoped)
CREATE TABLE user_training_datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    dataset_type VARCHAR(50) DEFAULT 'jsonl', -- jsonl, rag, custom
    file_path TEXT,
    sample_count INTEGER DEFAULT 0,
    metadata TEXT,                         -- JSON metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Training job datasets (many-to-many)
CREATE TABLE training_job_datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_job_id INTEGER NOT NULL,
    dataset_id INTEGER NOT NULL,
    FOREIGN KEY (training_job_id) REFERENCES external_training_jobs(id),
    FOREIGN KEY (dataset_id) REFERENCES user_training_datasets(id)
);
```

## Implementation Plan

### Phase 3A: Core Infrastructure (Week 1)
1. **Database Schema**
   - Create migration scripts
   - Add new tables
   - Link to existing minion system

2. **LLM Router Foundation**
   - Implement base provider interface
   - Create OpenAI, Anthropic, NVIDIA providers
   - Add provider factory pattern

3. **API Key Management**
   - Encrypted storage system
   - User-scoped key management
   - Secure key retrieval

### Phase 3B: Training Pipeline (Week 2)
1. **External Training Service**
   - User-scoped training job management
   - Integration with existing LoRA + RAG
   - Dynamic provider selection

2. **Training Executor**
   - Hybrid pipeline execution
   - Progress tracking
   - Error handling and recovery

3. **API Endpoints**
   - User-scoped training endpoints
   - Provider management
   - Dataset management

### Phase 3C: Frontend Integration (Week 3)
1. **External Training Page**
   - New Vue component
   - Provider selection UI
   - Training configuration

2. **Integration with Existing System**
   - Link to minion system
   - User authentication
   - Real-time progress updates

### Phase 3D: Advanced Features (Week 4)
1. **Additional Providers**
   - Hugging Face Inference API
   - Ollama local models
   - Custom API endpoints

2. **Training Analytics**
   - Performance metrics
   - Cost tracking
   - Usage statistics

## Key Features

### 1. User-Scoped Training
- Each user can only see their own training jobs
- Superusers can see all training jobs
- Training resources linked to specific minions

### 2. Dynamic Provider Support
- Plugin architecture for easy provider addition
- Unified interface across all providers
- Runtime provider selection

### 3. Hybrid Pipeline
- Local LoRA for style/behavior
- RAG for knowledge injection
- External LLM for final generation

### 4. Resource Linking
- Datasets linked to users
- Training jobs linked to minions
- ChromaDB collections per user

## API Endpoints

### User-Scoped Training
```
GET    /api/users/{user_id}/external-training/jobs
POST   /api/users/{user_id}/external-training/jobs
GET    /api/users/{user_id}/external-training/jobs/{job_id}
PUT    /api/users/{user_id}/external-training/jobs/{job_id}
DELETE /api/users/{user_id}/external-training/jobs/{job_id}
POST   /api/users/{user_id}/external-training/jobs/{job_id}/start
POST   /api/users/{user_id}/external-training/jobs/{job_id}/stop
```

### Provider Management
```
GET    /api/users/{user_id}/providers
POST   /api/users/{user_id}/providers
PUT    /api/users/{user_id}/providers/{provider}
DELETE /api/users/{user_id}/providers/{provider}
```

### Dataset Management
```
GET    /api/users/{user_id}/training-datasets
POST   /api/users/{user_id}/training-datasets
GET    /api/users/{user_id}/training-datasets/{dataset_id}
PUT    /api/users/{user_id}/training-datasets/{dataset_id}
DELETE /api/users/{user_id}/training-datasets/{dataset_id}
```

## Security Considerations

### 1. API Key Encryption
- Fernet encryption for API keys
- Environment-based encryption keys
- Secure key rotation

### 2. User Isolation
- All training resources scoped to users
- No cross-user data access
- Superuser override for administration

### 3. Input Validation
- Provider-specific validation
- Dataset format validation
- Configuration sanitization

## Integration Points

### 1. Existing Minion System
- Link training jobs to minions
- Use minion tokens for authentication
- Extend minion profile with training history

### 2. Local Training System
- Reuse LoRA training components
- Share ChromaDB service
- Common dataset formats

### 3. Authentication System
- Use existing user authentication
- Role-based access control
- Session management

## Testing Strategy

### 1. Unit Tests
- Provider implementations
- Training service logic
- Database operations

### 2. Integration Tests
- End-to-end training pipeline
- Provider switching
- User isolation

### 3. Performance Tests
- Large dataset handling
- Concurrent training jobs
- Memory usage optimization

## Deployment Considerations

### 1. Environment Variables
```
EXTERNAL_TRAINING_ENABLED=true
API_KEY_ENCRYPTION_KEY=your-encryption-key
DEFAULT_PROVIDERS=openai,anthropic,nvidia
```

### 2. Dependencies
```
openai>=1.0.0
anthropic>=0.37.0
requests>=2.31.0
cryptography>=41.0.0
```

### 3. Monitoring
- Training job status tracking
- Provider API usage monitoring
- Error rate tracking

## Success Metrics

### 1. Functionality
- ✅ User can create external training jobs
- ✅ Dynamic provider selection works
- ✅ Hybrid pipeline executes successfully
- ✅ Training resources properly linked to users

### 2. Performance
- Training job creation < 2 seconds
- Provider switching < 1 second
- Large dataset processing < 30 seconds

### 3. User Experience
- Intuitive provider selection
- Clear training progress
- Helpful error messages

## Risk Mitigation

### 1. Provider API Changes
- Abstract provider interface
- Version-specific adapters
- Fallback mechanisms

### 2. Resource Limits
- User quota management
- Rate limiting
- Cost monitoring

### 3. Data Security
- Encrypted API key storage
- Secure data transmission
- Regular security audits

## Future Enhancements

### 1. Advanced Features
- Custom provider plugins
- Training job scheduling
- Automated model evaluation

### 2. Integration
- CI/CD pipeline integration
- Model deployment automation
- Performance monitoring

### 3. Scalability
- Distributed training
- Load balancing
- Caching strategies

---

This plan provides a comprehensive roadmap for implementing user-scoped hybrid training while maintaining separation from the existing local LLM pipeline. The modular design allows for incremental implementation and easy extension with new providers.
