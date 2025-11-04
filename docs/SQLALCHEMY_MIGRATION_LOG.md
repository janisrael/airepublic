# SQLAlchemy Migration Log

## Migration Strategy: Feature-by-Feature Approach

**Goal**: Gradually migrate from raw PostgreSQL operations to SQLAlchemy ORM while maintaining system stability.

**Rule**: No dummy data fallbacks - show real errors for proper debugging.

---

## Current Migration Status

### ✅ **Completed Migrations**
- **Infrastructure**: Created new clean architecture structure (`app/` directory)
- **Structure**: Following migration_risk_analysis.md layout
- **Backward Compatibility**: Original files remain untouched
- **Models Service**: Created `app/services/model_service.py` with SQLAlchemy implementation
- **Model Routes**: Created `app/routes/model_routes.py` with new endpoints
- **New Server**: Created `app_server_new.py` running on port 5001
- **Service Files**: Moved 7 service files to `app/services/` directory
  - `chromadb_service.py` → `app/services/chromadb_service.py`
  - `external_api_service.py` → `app/services/external_api_service.py`
  - `nvidia_nim_service.py` → `app/services/nvidia_nim_service.py`
  - `dataset_loader.py` → `app/services/dataset_service.py`
  - `evaluation_executor.py` → `app/services/evaluation_service.py`
  - `rag_training_executor.py` → `app/services/rag_service.py`
  - `training_executor.py` → `app/services/training_service.py`
- **API Endpoints**: Split into feature-based route files
  - **Models**: `app/routes/model_routes.py` - 3 endpoints
  - **Datasets**: `app/routes/dataset_routes.py` - 5 endpoints
  - **Training**: `app/routes/training_routes.py` - 9 endpoints
  - **External Models**: `app/routes/external_model_routes.py` - 11 endpoints
  - **Total**: 28 new V2 endpoints alongside original endpoints

### 🆕 **NEW: Spirit System Implementation (PostgreSQL Ready)**
- **Database Schema**: Complete PostgreSQL schema with 12 tables for spirit system
  - `spirits_registry` - 18 spirit types with pricing tiers
  - `minion_spirits` - Spirit assignments to minions
  - `spirit_mastery` - Spirit level and XP tracking
  - `spirit_bundles` - 7 bundle deals with savings
  - `subscription_plans` - 4 subscription tiers
  - `user_spirit_purchases` - Purchase tracking
  - `user_spirit_subscriptions` - Subscription management
  - `user_points` - Points system for alternative currency
  - `points_transactions` - Points transaction history
  - `user_spirit_access` - Spirit access control
  - `tools_registry` - 71 tools for spirit capabilities
  - `spirit_minions` - Enhanced minions with spirit integration
- **SQLAlchemy Models**: `model/spirit_models.py` with complete ORM implementation
- **Database Connection**: `database/postgres_connection.py` with PostgreSQL fallback
- **Service Layer**: `app/services/spirit_service.py` with business logic
- **API Routes**: `app/routes/spirit_routes.py` with 12 new endpoints
  - `/api/spirits/` - Get all spirits
  - `/api/spirits/free` - Get free spirits
  - `/api/spirits/tier/<tier>` - Get spirits by pricing tier
  - `/api/spirits/<id>` - Get spirit by ID
  - `/api/spirits/name/<name>` - Get spirit by name
  - `/api/spirits/available` - Get spirits for user rank/level
  - `/api/spirits/synergy` - Calculate spirit synergies
  - `/api/spirits/bundles` - Get spirit bundles
  - `/api/spirits/subscription-plans` - Get subscription plans
  - `/api/spirits/user/<id>/access` - Get user spirit access
  - `/api/spirits/<id>/tools` - Get spirit tools
  - `/api/spirits/health` - Health check
- **Data Seeding**: Successfully populated with complete spirit system data
  - 18 Spirit types across 6 categories
  - 71 Tools with unique capabilities
  - 7 Bundle deals with up to 44% savings
  - 4 Subscription plans with tiered pricing
- **Monetization System**: Complete purchase and subscription tracking
- **Server Integration**: Updated `app_server_new.py` with spirit routes

### 🔄 **In Progress**
- **Feature**: `/api/models` endpoint
- **Status**: ✅ COMPLETED - New SQLAlchemy service working, returns 4 models
- **Files**: `api_server.py` (lines 930-1047) → `app/routes/model_routes.py`
- **New Endpoints**: 
  - `/api/models-v2` (NEW: SQLAlchemy implementation)
  - `/api/models-v2/<name>` (NEW: Model details)
  - `/api/models-v2/health` (NEW: Health check)

### ⏳ **Pending Migrations**
- All other API endpoints

### 🚀 **Next Phase: Redis Infrastructure (Enterprise Scale)**
**Goal**: Prepare for massive scale with Redis caching and real-time features

#### **Redis Setup & Configuration**
- **Install Redis Server**: Production-ready Redis installation
- **Redis Configuration**: Memory optimization, persistence settings
- **Security**: Redis authentication and network security
- **Monitoring**: Redis monitoring and alerting setup

#### **Caching Layer Implementation**
- **Model Metadata Cache**: Cache model capabilities, parameters, pricing
- **Spirit Registry Cache**: Cache spirit types, tools, synergies
- **User Data Cache**: Cache user preferences, minions, subscriptions
- **API Response Cache**: Cache frequently requested API responses
- **Database Query Cache**: Cache expensive database queries

#### **Session Management**
- **Redis Sessions**: Replace in-memory sessions with Redis
- **JWT Token Storage**: Redis-based token blacklisting
- **User State Management**: Store user preferences and context
- **Multi-device Support**: Session synchronization across devices

#### **Real-time Features**
- **WebSocket Integration**: Real-time model training updates
- **Redis Pub/Sub**: Live notifications and status updates
- **Spirit Marketplace**: Real-time pricing and availability
- **Minion Chat**: Real-time chat with minions
- **Training Progress**: Live training progress updates

#### **Performance Optimization**
- **Query Result Caching**: Cache database query results
- **API Response Caching**: Cache API responses with TTL
- **Static Asset Caching**: Cache images, avatars, static content
- **Rate Limiting**: Redis-based rate limiting per user/API
- **Background Jobs**: Redis-based job queue for heavy operations

#### **Scalability Features**
- **Redis Clustering**: Horizontal scaling with Redis Cluster
- **Load Balancing**: Redis-based session affinity
- **Cache Warming**: Proactive cache population
- **Cache Invalidation**: Smart cache invalidation strategies
- **Multi-region Support**: Redis replication across regions
- Service layer methods
- Database operations across 27 files

---

## Migration Progress Tracking

### **Phase 1: `/api/models` Endpoint Migration**

#### **Current Implementation (PostgreSQL)**
```python
# Location: api_server.py:930-1047
@app.route('/api/models', methods=['GET'])
def get_ollama_models():
    # Uses: db.get_external_api_models() (raw PostgreSQL)
    # Uses: subprocess calls to Ollama
    # Returns: Combined local + external models
```

#### **Target Implementation (SQLAlchemy)**
```python
# New location: services/models_service.py
# Uses: SQLAlchemy models + repositories
# Uses: Proper session management
# Returns: Same API contract
```

#### **Migration Plan**
1. **Create SQLAlchemy service** for models
2. **Implement repository pattern** for external models
3. **Create new endpoint** alongside old one
4. **Test thoroughly** before switching
5. **Update frontend** to use new endpoint
6. **Remove old code** after validation

#### **Files to Create/Modify**
- `services/models_service.py` (new)
- `repositories/model_repository.py` (new)
- `api_server.py` (add new endpoint)
- `frontend/src/services/models.js` (update)

#### **Risks & Mitigation**
- **Risk**: Breaking existing functionality
- **Mitigation**: Keep old endpoint until new one is validated
- **Risk**: Different data format
- **Mitigation**: Maintain same JSON response structure

---

## File Structure Analysis

### **Current Structure vs Target Structure**

#### **Current (Mixed)**
```
backend/
├── api_server.py          # All endpoints in one file
├── database.py            # Raw PostgreSQL operations
├── model/                 # SQLAlchemy models (ready)
├── repositories/          # Repository pattern (partial)
└── services/              # Service layer (partial)
```

#### **Target (Clean Architecture)**
```
backend/
├── app/
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   └── utils/            # Helpers
├── database/
│   ├── connection.py     # Database connection
│   ├── session.py        # Session management
│   └── migrations/       # Alembic migrations
└── main.py              # App entry point
```

### **Migration Risks Assessment**

#### **🔴 HIGH RISK**
1. **API Contract Changes**
   - **Risk**: Frontend breaks due to different response format
   - **Mitigation**: Maintain exact same JSON structure

2. **Database Connection Issues**
   - **Risk**: SQLAlchemy connection fails
   - **Mitigation**: Keep PostgreSQL as fallback during migration

3. **Performance Degradation**
   - **Risk**: ORM queries slower than raw SQL
   - **Mitigation**: Profile and optimize queries

#### **🟡 MEDIUM RISK**
1. **Session Management**
   - **Risk**: Memory leaks from unclosed sessions
   - **Mitigation**: Use context managers and proper cleanup

2. **Transaction Handling**
   - **Risk**: Data inconsistency during migration
   - **Mitigation**: Use proper transaction boundaries

#### **🟢 LOW RISK**
1. **Model Definition**
   - **Risk**: Schema mismatches
   - **Mitigation**: Models already defined and tested

2. **Frontend Compatibility**
   - **Risk**: API changes break frontend
   - **Mitigation**: Maintain backward compatibility

---

## Migration Checklist

### **For Each Feature Migration**

- [ ] **Analysis**: Understand current implementation
- [ ] **Design**: Plan new SQLAlchemy implementation
- [ ] **Create**: New service and repository classes
- [ ] **Implement**: New endpoint alongside old one
- [ ] **Test**: Thorough testing of new implementation
- [ ] **Validate**: Compare old vs new responses
- [ ] **Switch**: Update frontend to use new endpoint
- [ ] **Cleanup**: Remove old code after validation
- [ ] **Document**: Update this log

---

## Next Steps

1. **Fix current import issue** in `api_server.py`
2. **Create models service** for `/api/models` endpoint
3. **Implement repository pattern** for external models
4. **Test new implementation** thoroughly
5. **Update frontend** to use new endpoint
6. **Plan next feature** migration

---

## Notes

- **No dummy data**: All fallbacks show real errors
- **Gradual migration**: One feature at a time
- **Backward compatibility**: Maintain existing API contracts
- **Testing first**: Validate before switching
- **Documentation**: Keep this log updated
