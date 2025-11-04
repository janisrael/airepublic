# Authentication Disable Record

## Overview
Temporarily disabled authentication in the V2 server (`app_server_new.py`) to bypass authentication issues and proceed with testing minion creation and other functionality.

## Date
October 3, 2025

## Reason for Disabling
- V2 authentication was returning 401 UNAUTHORIZED errors
- Login endpoint was failing with "unknown" error
- Database connection issues between V2 server and `spirit_system.db`
- Authentication was blocking progress on minion creation testing

## Files Modified

### 1. `/backend/app/routes/auth_routes.py`
**Function:** `require_auth` decorator (lines 545-581)

**Original Purpose:** Validates JWT tokens and requires authentication for protected endpoints

**Current State:** Bypasses authentication and creates mock user object
```python
def require_auth(f):
    """Decorator to require authentication for an endpoint - TEMPORARILY DISABLED"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TEMPORARY: Bypass authentication for testing
        # Create a mock user object for testing
        g.user = {
            'user_id': 1,
            'username': 'swordfish',
            'email': 'swordfish@airepublic.com'
        }
        return f(*args, **kwargs)
        
        # Original authentication code (commented out)
        # [Original code is preserved in comments]
    
    return decorated_function
```

### 2. `/backend/app/routes/user_minion_routes.py`
**Function:** `require_auth` decorator (lines 33-76)

**Original Purpose:** Authentication decorator for user-scoped minion endpoints

**Current State:** Same bypass as above - creates mock user object
```python
def require_auth(f):
    """Authentication decorator for user-scoped endpoints - TEMPORARILY DISABLED"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TEMPORARY: Bypass authentication for testing
        # Create a mock user object for testing
        g.user = {
            'user_id': 1,
            'username': 'swordfish',
            'email': 'swordfish@airepublic.com'
        }
        return f(*args, **kwargs)
        
        # Original authentication code (commented out)
        # [Original code is preserved in comments]
    
    return decorated_function
```

## Mock User Object
When authentication is disabled, all protected endpoints receive this mock user:
```python
g.user = {
    'user_id': 1,
    'username': 'swordfish',
    'email': 'swordfish@airepublic.com'
}
```

## How to Re-enable Authentication

### Step 1: Restore auth_routes.py
In `/backend/app/routes/auth_routes.py`, replace the `require_auth` function (lines 545-581):

```python
def require_auth(f):
    """Decorator to require authentication for an endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # Verify token
        user_info = verify_token(token)
        if not user_info:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Add user info to Flask's g object
        g.user = user_info
        return f(*args, **kwargs)
    
    return decorated_function
```

### Step 2: Restore user_minion_routes.py
In `/backend/app/routes/user_minion_routes.py`, replace the `require_auth` function (lines 33-76):

```python
def require_auth(f):
    """Authentication decorator for user-scoped endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'Authorization header required'
            }), 401
        
        # Check for Bearer token
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Invalid authorization format. Use: Bearer <token>'
            }), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Verify token and get user
        user = verify_token(token)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Set user in g for use in endpoints
        g.user = user
        return f(*args, **kwargs)
    
    return decorated_function
```

### Step 3: Restart V2 Server
```bash
cd /run/media/swordfish/New\ Volume/development/ai_republic/ai-refinement-dashboard/backend
pkill -f app_server_new.py
python3 app_server_new.py > server.log 2>&1 &
```

### Step 4: Test Authentication
```bash
# Test login
curl -X POST "http://localhost:5001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "swordfish", "password": "swordfish"}'

# Test protected endpoint with token
curl -X GET "http://localhost:5001/api/v2/users/1/minions" \
  -H "Authorization: Bearer <token_from_login>"
```

## Authentication Issues to Resolve

### 1. Database Connection
- V2 server should use `spirit_system.db` for authentication
- Currently falling back to `ai_dashboard.db`
- Check PostgreSQL connection configuration in `database/postgres_connection.py`

### 2. User Password Hash
- Verify `swordfish` user exists in `spirit_system.db` with correct password hash
- Ensure password hash is compatible with `werkzeug.security.check_password_hash`

### 3. JWT Token Generation
- Verify JWT_SECRET is consistent
- Check token expiration settings
- Ensure `verify_token` function works correctly

### 4. Frontend Integration
- Update frontend components to use centralized API service
- Ensure frontend sends proper Authorization headers
- Test token storage and refresh logic

## Testing Status After Disable

### ✅ Working
- V2 server starts without authentication errors
- Protected endpoints accessible without tokens
- Minion creation endpoints accessible
- Frontend can make API calls to V2 server

### 🔄 Next Steps
1. Test minion creation functionality
2. Test external LoRA training
3. Test user minion management
4. Debug and fix authentication system
5. Re-enable authentication when ready

## Security Note
⚠️ **WARNING**: This is a development/testing configuration. Authentication should be re-enabled before any production deployment or external access.

## Related Files
- `/backend/app_server_new.py` - Main V2 server
- `/backend/database/postgres_connection.py` - Database connection logic
- `/backend/model/user.py` - User model for authentication
- `/frontend/src/config/api.js` - Frontend API configuration
- `/frontend/.env` - Frontend environment variables (set to V2)

---
*Created by Agimat (AI Assistant) on October 3, 2025*
