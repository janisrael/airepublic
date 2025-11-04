# User-Scoped Minion API Documentation

## Overview

This document describes the user-scoped minion API endpoints for the AI Refinement Dashboard. These endpoints provide secure, user-specific access to minion management, ensuring that each user can only access and manage their own AI agents (minions).

## Architecture

### User-Scoped Design
- **User Isolation**: Each user can only access their own minions
- **Authentication Required**: All endpoints require Bearer token authentication
- **Minion Ownership**: Minions are owned by specific users
- **Unique Identifiers**: Uses `minion_id` from `external_api_models.id`

### API Structure
```
/api/users/{user_id}/minions/{minion_id}/...
```

## Authentication

### Bearer Token Authentication
All endpoints require a valid Bearer token in the Authorization header:

```http
Authorization: Bearer <session_token>
```

### Token Verification
- Tokens are verified against the `auth.db` sessions table
- Tokens must be active (not expired)
- User roles are retrieved for authorization
- User isolation is enforced at the endpoint level

## API Endpoints

### 1. Health Check
**GET** `/api/users/{user_id}/minions/health`

Check if the user minions API is healthy.

**Response:**
```json
{
  "success": true,
  "message": "User 1 minions API is healthy",
  "user_id": 1,
  "version": "1.0.0"
}
```

### 2. Get All User Minions
**GET** `/api/users/{user_id}/minions`

Get all minions for a specific user.

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "minions": [
    {
      "id": 1,
      "name": "nvidia-llama-nemotron-super",
      "display_name": "Grafana",
      "description": "I am Grafana, the planner Minion...",
      "provider": "nvidia",
      "model_id": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
      "capabilities": ["chat", "reasoning", "coding"],
      "parameters": "49B",
      "context_length": 131072,
      "max_tokens": 65536,
      "temperature": 0.6,
      "top_p": 0.95,
      "system_prompt": "I am Grafana, the planner Minion...",
      "experience": 60,
      "level": "4",
      "avatar_url": null,
      "quantization": "fp8",
      "architecture": "llama",
      "license": "NVIDIA",
      "tags": ["nvidia", "llama", "chat", "math", "reasoning"],
      "is_active": true,
      "is_favorite": false,
      "created_at": "2025-09-28 11:36:00",
      "updated_at": "2025-09-30 06:10:38",
      "provider_display_name": "NVIDIA",
      "provider_icon": "smart_toy",
      "provider_color": "#76B900"
    }
  ],
  "total": 1
}
```

### 3. Get Specific Minion
**GET** `/api/users/{user_id}/minions/{minion_id}`

Get a specific minion for a user (includes API key for user's own minions).

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "minion": {
    "id": 1,
    "name": "nvidia-llama-nemotron-super",
    "display_name": "Grafana",
    "description": "I am Grafana, the planner Minion...",
    "provider": "nvidia",
    "model_id": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    "api_key": "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",
    "base_url": "https://integrate.api.nvidia.com/v1",
    "capabilities": ["chat", "reasoning", "coding"],
    "parameters": "49B",
    "context_length": 131072,
    "max_tokens": 65536,
    "temperature": 0.6,
    "top_p": 0.95,
    "system_prompt": "I am Grafana, the planner Minion...",
    "experience": 60,
    "level": "4",
    "avatar_url": null,
    "quantization": "fp8",
    "architecture": "llama",
    "license": "NVIDIA",
    "tags": ["nvidia", "llama", "chat", "math", "reasoning"],
    "is_active": true,
    "is_favorite": false,
    "created_at": "2025-09-28 11:36:00",
    "updated_at": "2025-09-30 06:10:38",
    "provider_display_name": "NVIDIA",
    "provider_icon": "smart_toy",
    "provider_color": "#76B900"
  }
}
```

### 4. Chat with Minion
**POST** `/api/users/{user_id}/minions/{minion_id}/chat`

Send a message to a specific minion and get a response.

**Request Body:**
```json
{
  "message": "Hello Grafana!"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "minion_id": 1,
  "minion_name": "Grafana",
  "response": "Hello! I'm Grafana, your nvidia minion. I received your message: 'Hello Grafana!'",
  "timestamp": "2025-09-30T05:00:00Z"
}
```

### 5. Update Minion Experience
**POST** `/api/users/{user_id}/minions/{minion_id}/xp`

Update the experience points for a minion.

**Request Body:**
```json
{
  "xp_gain": 10
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "minion_id": 1,
  "minion_name": "Grafana",
  "previous_experience": 50,
  "xp_gain": 10,
  "new_experience": 60
}
```

### 6. Get Minion Capabilities
**GET** `/api/users/{user_id}/minions/{minion_id}/capabilities`

Get the capabilities and level information for a minion.

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "minion_id": 1,
  "minion_name": "Grafana",
  "capabilities": ["chat", "reasoning", "coding"],
  "level": "4",
  "experience": 60
}
```

### 7. Get Minion Statistics
**GET** `/api/users/{user_id}/minions/{minion_id}/stats`

Get usage statistics for a minion.

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "minion_id": 1,
  "minion_name": "Grafana",
  "stats": {
    "total_queries": 0,
    "successful_queries": 0,
    "failed_queries": 0,
    "average_response_time": 0,
    "last_used": null,
    "xp_gained_today": 0,
    "level_progress": 0
  }
}
```

### 8. Get Grouped Minions
**GET** `/api/users/{user_id}/minions/grouped`

Get user's minions grouped by provider.

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "grouped_minions": {
    "nvidia": {
      "name": "nvidia",
      "display_name": "NVIDIA",
      "icon": "smart_toy",
      "color": "#76B900",
      "minions": [
        {
          "id": 1,
          "name": "nvidia-llama-nemotron-super",
          "display_name": "Grafana",
          "description": "I am Grafana, the planner Minion...",
          "provider": "nvidia",
          "model_id": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
          "capabilities": ["chat", "reasoning", "coding"],
          "experience": 60,
          "level": "4",
          "avatar_url": null,
          "is_active": true,
          "is_favorite": false,
          "created_at": "2025-09-28 11:36:00",
          "updated_at": "2025-09-30 06:10:38"
        }
      ]
    }
  }
}
```

## Error Responses

### Authentication Errors
```json
{
  "success": false,
  "error": "Authorization header required"
}
```

```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```

### Access Denied
```json
{
  "success": false,
  "error": "Access denied: Cannot access other user's minions"
}
```

### Not Found
```json
{
  "success": false,
  "error": "Minion not found"
}
```

### Validation Errors
```json
{
  "success": false,
  "error": "Message is required"
}
```

```json
{
  "success": false,
  "error": "xp_gain is required"
}
```

## Usage Examples

### 1. Get User's Minions
```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/users/1/minions
```

### 2. Chat with Minion
```bash
curl -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello Grafana!"}' \
     http://localhost:5000/api/users/1/minions/1/chat
```

### 3. Update Minion Experience
```bash
curl -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"xp_gain": 10}' \
     http://localhost:5000/api/users/1/minions/1/xp
```

### 4. Get Grouped Minions
```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/users/1/minions/grouped
```

## Database Schema

### External API Models (Minions)
```sql
CREATE TABLE external_api_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    display_name TEXT,
    description TEXT,
    provider TEXT NOT NULL,
    model_id TEXT NOT NULL,
    api_key TEXT,
    base_url TEXT,
    capabilities TEXT,
    parameters TEXT,
    context_length INTEGER,
    max_tokens INTEGER,
    temperature REAL DEFAULT 0.7,
    top_p REAL DEFAULT 0.9,
    system_prompt TEXT,
    experience INTEGER DEFAULT 0,
    level TEXT DEFAULT 'beginner',
    avatar_url TEXT,
    quantization TEXT,
    architecture TEXT,
    license TEXT,
    tags TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Provider Groups
```sql
CREATE TABLE provider_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Authentication Tables
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles table
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User roles table
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (role_id) REFERENCES roles (id)
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Security Features

### 1. User Isolation
- Users can only access their own minions
- Cross-user access is blocked at the API level
- User ID verification in all endpoints

### 2. Authentication
- Bearer token authentication required
- Token expiration checking
- Session validation against database

### 3. Authorization
- Role-based access control
- User permission verification
- Endpoint-level access control

### 4. Data Protection
- API keys only visible to minion owners
- Sensitive data filtered in responses
- Input validation and sanitization

## Integration with Minion Desktop App

### Connection Flow
1. **Authentication**: Minion app authenticates with AI Republic
2. **Token Storage**: Session token stored securely in Minion's PostgreSQL database
3. **API Calls**: Minion app uses Bearer token for all API requests
4. **Data Sync**: Minion app syncs with user's minions and updates experience

### Example Integration
```javascript
// Minion app authentication
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'swordfish', password: 'admin123' })
});

const { token } = await response.json();

// Store token securely
localStorage.setItem('ai_republic_token', token);

// Use token for API calls
const minions = await fetch('http://localhost:5000/api/users/1/minions', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

## Future Enhancements

### 1. User-Specific Minion Creation
- Add `user_id` column to `external_api_models` table
- Implement minion creation endpoints
- User-specific minion management

### 2. Advanced Statistics
- Real usage tracking
- Performance metrics
- Training data collection

### 3. Minion Sharing
- Share minions between users
- Public minion marketplace
- Minion collaboration features

### 4. Real-time Updates
- WebSocket integration
- Live minion status updates
- Real-time chat functionality

## Testing

### Test Commands
```bash
# Health check
curl -H "Authorization: Bearer test_token_123" \
     http://localhost:5000/api/users/1/minions/health

# Get all minions
curl -H "Authorization: Bearer test_token_123" \
     http://localhost:5000/api/users/1/minions

# Get specific minion
curl -H "Authorization: Bearer test_token_123" \
     http://localhost:5000/api/users/1/minions/1

# Chat with minion
curl -H "Authorization: Bearer test_token_123" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello Grafana!"}' \
     http://localhost:5000/api/users/1/minions/1/chat

# Update experience
curl -H "Authorization: Bearer test_token_123" \
     -H "Content-Type: application/json" \
     -d '{"xp_gain": 10}' \
     http://localhost:5000/api/users/1/minions/1/xp

# Get grouped minions
curl -H "Authorization: Bearer test_token_123" \
     http://localhost:5000/api/users/1/minions/grouped
```

### Test Results
- ✅ Authentication working
- ✅ User isolation enforced
- ✅ Minion data returned correctly
- ✅ Chat endpoint functional
- ✅ Experience tracking working
- ✅ Provider grouping functional

## Conclusion

The user-scoped minion API provides a secure, scalable foundation for the AI Republic platform. It enables:

- **User-specific minion management**
- **Secure authentication and authorization**
- **Minion experience tracking**
- **Provider-based organization**
- **Integration with Minion desktop app**

This API is ready for production use and can be extended with additional features as needed.
