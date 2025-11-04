# Minion Token System Implementation

## Overview

The Minion Token System enables minion clients to authenticate and communicate with the AI Republic platform without requiring user login credentials. Each minion has its own unique token that provides access to its specific API endpoints.

## Architecture

```
Minion Client → Minion Token → User-Scoped Minion API → External API
```

## Token Specifications

### Format
- **Prefix**: `minion_`
- **Length**: 32 characters (hexadecimal)
- **Example**: `minion_2CC93B0A983494ABA2A65577A150305A`

### Generation
- **Auto-generated** when minion is created
- **Cryptographically secure** using PostgreSQL's `randomblob()` function
- **Unique** across all minions

### Expiration
- **No expiration** by default
- **Invalidated** when:
  - User account is closed/suspended
  - Minion is deleted
  - User manually regenerates token

## Database Schema

### `external_api_models` Table
```sql
ALTER TABLE external_api_models ADD COLUMN minion_token TEXT;
```

### Token Generation
```sql
UPDATE external_api_models 
SET minion_token = 'minion_' || substr(hex(randomblob(16)), 1, 32) 
WHERE minion_token IS NULL;
```

## Authentication Flow

### 1. Minion Token Authentication
```python
def verify_minion_token(token):
    """Verify minion token and return minion info"""
    if not token.startswith('minion_'):
        return None
    
    cursor.execute("""
        SELECT eam.*, u.id as user_id
        FROM external_api_models eam
        JOIN users u ON eam.user_id = u.id
        WHERE eam.minion_token = ? AND eam.is_active = TRUE AND u.is_active = 1
    """, (token,))
    
    return cursor.fetchone()
```

### 2. Minion Token Decorator
```python
def require_minion_token(f):
    """Authentication decorator for minion token endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Minion token required'}), 401
        
        token = auth_header.split(' ')[1]
        minion = verify_minion_token(token)
        
        if not minion:
            return jsonify({'error': 'Invalid minion token'}), 401
        
        g.minion = minion
        return f(*args, **kwargs)
    
    return decorated_function
```

## API Endpoints

### Minion-Scoped Endpoints
All endpoints use the pattern: `/api/minions/{minion_id}/...`

#### 1. Minion Details
```
GET /api/minions/{minion_id}
Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A
```

**Response**:
```json
{
    "success": true,
    "minion": {
        "id": 1,
        "name": "nvidia-llama-nemotron-super",
        "display_name": "Grafana",
        "provider": "nvidia",
        "model_id": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
        "capabilities": ["chat", "reasoning", "coding"],
        "system_prompt": "I am Grafana, the planner Minion...",
        "temperature": 0.6,
        "top_p": 0.95,
        "max_tokens": 65536
    }
}
```

#### 2. Chat with Minion
```
POST /api/minions/{minion_id}/chat
Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A
Content-Type: application/json

{
    "message": "Hello, Grafana!",
    "stream": false
}
```

**Response**:
```json
{
    "success": true,
    "response": "Hello! I'm Grafana. You said: Hello, Grafana!",
    "minion_id": 1,
    "minion_name": "Grafana"
}
```

**Streaming Chat**:
```json
{
    "message": "Hello, Grafana!",
    "stream": true
}
```

#### 3. Minion Capabilities
```
GET /api/minions/{minion_id}/capabilities
Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A
```

**Response**:
```json
{
    "success": true,
    "capabilities": ["chat", "reasoning", "coding"],
    "minion_id": 1,
    "minion_name": "Grafana"
}
```

#### 4. Minion Statistics
```
GET /api/minions/{minion_id}/stats
Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A
```

**Response**:
```json
{
    "success": true,
    "stats": {
        "total_queries": 0,
        "total_tokens_used": 0,
        "average_response_time": 0,
        "last_used": null,
        "status": "active"
    },
    "minion_id": 1,
    "minion_name": "Grafana"
}
```

#### 5. Update Minion Experience Points
```
POST /api/minions/{minion_id}/xp
Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A
Content-Type: application/json

{
    "xp_gain": 10
}
```

**Response**:
```json
{
    "success": true,
    "message": "XP updated by 10",
    "minion_id": 1,
    "minion_name": "Grafana"
}
```

#### 6. Minion Sync (Configuration)
```
GET /api/minions/{minion_id}/sync
Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A
```

**Response**:
```json
{
    "success": true,
    "sync_data": {
        "minion_id": 1,
        "model": {
            "id": 1,
            "name": "nvidia-llama-nemotron-super",
            "display_name": "Grafana",
            "description": "I am Grafana, the planner Minion...",
            "provider": "nvidia",
            "model_id": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
            "api_key": "nvapi-...",
            "base_url": "https://integrate.api.nvidia.com/v1",
            "capabilities": ["chat", "reasoning", "coding"],
            "parameters": "49B",
            "context_length": 131072,
            "max_tokens": 65536,
            "temperature": 0.6,
            "top_p": 0.95,
            "system_prompt": "I am Grafana, the planner Minion...",
            "tags": ["nvidia", "llama", "chat", "math", "reasoning"],
            "avatar_url": "uploads/avatars/959a575f-44ac-47b2-bb71-7e565a14c5b3.png",
            "level": "4",
            "experience": 60,
            "republic_id": "grafana-d7a1494e",
            "republic_key": "rep_TnrW-UrbjRb6XklzRRVQy_-5P3xVXKOmcpANP9SN7dA"
        },
        "sync_timestamp": 1759218506.1728916
    }
}
```

#### 7. Health Check
```
GET /api/minions/health
```

**Response**:
```json
{
    "success": true,
    "message": "Minion API is healthy",
    "version": "1.0.0"
}
```

## Token Permissions

### Allowed Operations
- ✅ Access minion details
- ✅ Chat with minion (including streaming)
- ✅ Get minion capabilities
- ✅ Get minion statistics
- ✅ Update minion experience points
- ✅ Sync minion configuration
- ✅ Health check

### Restricted Operations
- ❌ Access other users' minions
- ❌ Access user account information
- ❌ Admin functions
- ❌ Create/delete minions
- ❌ Modify minion configuration

## Frontend Integration

### Minion Creation Flow
1. User creates minion in AI Republic
2. System generates minion token
3. Success modal displays:
   - Minion API URL: `/api/minions/{minion_id}/chat`
   - Minion Token: `minion_2CC93B0A983494ABA2A65577A150305A`

### Minion Details Modal
- Display minion token
- Show API endpoints
- Regenerate token button
- Copy token functionality

## Token Regeneration

### User-Initiated Regeneration
```python
@user_minion_bp.route('/<int:minion_id>/regenerate-token', methods=['POST'])
@require_auth
def regenerate_minion_token(minion_id):
    """Regenerate minion token"""
    # Verify user owns minion
    # Generate new token
    # Update database
    # Return new token
```

### Security Considerations
- Old token immediately invalidated
- User notified of token change
- Audit log of token regeneration

## Minion Client Integration

### Example Minion Client Code
```python
import requests

class MinionClient:
    def __init__(self, minion_id, minion_token, base_url="http://localhost:5000"):
        self.minion_id = minion_id
        self.minion_token = minion_token
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {minion_token}',
            'Content-Type': 'application/json'
        }
    
    def chat(self, message, stream=False):
        """Chat with minion"""
        response = requests.post(
            f"{self.base_url}/api/minions/{self.minion_id}/chat",
            json={'message': message, 'stream': stream},
            headers=self.headers
        )
        return response.json()
    
    def get_details(self):
        """Get minion details"""
        response = requests.get(
            f"{self.base_url}/api/minions/{self.minion_id}",
            headers=self.headers
        )
        return response.json()
    
    def sync_config(self):
        """Sync minion configuration"""
        response = requests.get(
            f"{self.base_url}/api/minions/{self.minion_id}/sync",
            headers=self.headers
        )
        return response.json()
    
    def get_capabilities(self):
        """Get minion capabilities"""
        response = requests.get(
            f"{self.base_url}/api/minions/{self.minion_id}/capabilities",
            headers=self.headers
        )
        return response.json()
    
    def get_stats(self):
        """Get minion statistics"""
        response = requests.get(
            f"{self.base_url}/api/minions/{self.minion_id}/stats",
            headers=self.headers
        )
        return response.json()
    
    def update_xp(self, xp_gain):
        """Update minion experience points"""
        response = requests.post(
            f"{self.base_url}/api/minions/{self.minion_id}/xp",
            json={'xp_gain': xp_gain},
            headers=self.headers
        )
        return response.json()
    
    def health_check(self):
        """Check minion API health"""
        response = requests.get(
            f"{self.base_url}/api/minions/health"
        )
        return response.json()
```

## Security Features

### Token Validation
- Format validation (`minion_` prefix)
- Database lookup
- Active status check
- User account status check

### Rate Limiting
- Per-minion rate limits
- Abuse detection
- Automatic blocking

### Audit Logging
- Token usage tracking
- Failed authentication attempts
- Token regeneration events

## Error Handling

### Common Error Responses
```json
{
    "error": "Minion token required",
    "success": false
}
```

```json
{
    "error": "Invalid minion token",
    "success": false
}
```

```json
{
    "error": "Minion not found or inactive",
    "success": false
}
```

## Implementation Status

### ✅ Completed
- Database schema updated
- Token generation implemented
- Minion token authentication decorator
- Minion-scoped API endpoints
- Minion sync endpoint
- Cross-database token verification
- Minion client example code

### 🔄 In Progress
- Frontend token display
- Token regeneration

### ⏳ Pending
- Rate limiting
- Audit logging
- Minion client SDK
- Real chat integration

## Testing

### Test Cases
1. **Valid Token**: Minion client with valid token can access endpoints
2. **Invalid Token**: Invalid token returns 401 error
3. **Expired Account**: Inactive user account blocks token access
4. **Deleted Minion**: Deleted minion invalidates token
5. **Token Regeneration**: Old token invalidated after regeneration

### Test Commands
```bash
# Test minion details
curl -H "Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A" \
     http://localhost:5000/api/minions/1

# Test minion chat
curl -X POST \
     -H "Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, Grafana!"}' \
     http://localhost:5000/api/minions/1/chat

# Test minion sync
curl -H "Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A" \
     http://localhost:5000/api/minions/1/sync

# Test minion capabilities
curl -H "Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A" \
     http://localhost:5000/api/minions/1/capabilities

# Test minion statistics
curl -H "Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A" \
     http://localhost:5000/api/minions/1/stats

# Test minion XP update
curl -X POST \
     -H "Authorization: Bearer minion_2CC93B0A983494ABA2A65577A150305A" \
     -H "Content-Type: application/json" \
     -d '{"xp_gain": 10}' \
     http://localhost:5000/api/minions/1/xp

# Test health check
curl http://localhost:5000/api/minions/health
```

## Future Enhancements

### Planned Features
- **Token Scoping**: Different permission levels per token
- **Token Expiration**: Optional expiration for security
- **Webhook Support**: Minion-to-minion communication
- **Analytics**: Token usage analytics and insights
- **SDK**: Official minion client SDKs for multiple languages

### Integration Opportunities
- **Skills System**: Token-based skill activation
- **Workflow Automation**: Token-driven minion workflows
- **Third-party Integrations**: External service connections
- **Monitoring**: Real-time minion health monitoring

## Conclusion

The Minion Token System provides a secure, scalable way for minion clients to authenticate and interact with the AI Republic platform. By using unique, non-expiring tokens with proper validation and permissions, the system ensures both security and ease of use for minion developers and users.

---

**Last Updated**: 2025-09-30  
**Version**: 1.1.0  
**Status**: Core Implementation Complete
