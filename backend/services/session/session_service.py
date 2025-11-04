#!/usr/bin/env python3
"""
Session Service
Session management operations including session validation and cleanup
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import secrets

from ..auth_database import auth_db

class SessionService:
    """Session management service"""
    
    def __init__(self):
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '1800'))  # 30 minutes
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None) -> Dict:
        """
        Create a new session for user
        
        Args:
            user_id: User ID
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Dict with session info
        """
        try:
            # Create session in database
            session_token = auth_db.create_session(user_id, ip_address, user_agent)
            
            # Get session details
            session = auth_db.get_session(session_token)
            
            return {
                'success': True,
                'session_token': session_token,
                'session': session,
                'message': 'Session created successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to create session: {str(e)}'}
    
    def validate_session(self, session_token: str) -> Dict:
        """
        Validate session token
        
        Args:
            session_token: Session token to validate
        
        Returns:
            Dict with validation result
        """
        try:
            if not session_token:
                return {'success': False, 'error': 'Session token required'}
            
            # Get session from database
            session = auth_db.get_session(session_token)
            if not session:
                return {'success': False, 'error': 'Invalid or expired session'}
            
            # Check if session is active
            if not session['is_active']:
                return {'success': False, 'error': 'Session is inactive'}
            
            # Check if session has expired
            if datetime.now() > datetime.fromisoformat(session['expires_at']):
                return {'success': False, 'error': 'Session has expired'}
            
            return {
                'success': True,
                'session': session,
                'message': 'Session is valid'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Session validation failed: {str(e)}'}
    
    def refresh_session(self, session_token: str) -> Dict:
        """
        Refresh session by extending expiry
        
        Args:
            session_token: Session token to refresh
        
        Returns:
            Dict with refresh status
        """
        try:
            # Validate current session
            validation = self.validate_session(session_token)
            if not validation['success']:
                return validation
            
            # Extend session expiry
            new_expires_at = datetime.now() + timedelta(seconds=self.session_timeout)
            
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sessions 
                    SET expires_at = ?, last_accessed = CURRENT_TIMESTAMP
                    WHERE session_token = ?
                ''', (new_expires_at, session_token))
                
                if cursor.rowcount == 0:
                    return {'success': False, 'error': 'Session not found'}
                
                conn.commit()
            
            # Get updated session
            updated_session = auth_db.get_session(session_token)
            
            return {
                'success': True,
                'session': updated_session,
                'message': 'Session refreshed successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Session refresh failed: {str(e)}'}
    
    def invalidate_session(self, session_token: str) -> Dict:
        """
        Invalidate session
        
        Args:
            session_token: Session token to invalidate
        
        Returns:
            Dict with invalidation status
        """
        try:
            success = auth_db.delete_session(session_token)
            
            if success:
                return {'success': True, 'message': 'Session invalidated successfully'}
            else:
                return {'success': False, 'error': 'Session not found'}
                
        except Exception as e:
            return {'success': False, 'error': f'Session invalidation failed: {str(e)}'}
    
    def invalidate_all_user_sessions(self, user_id: int) -> Dict:
        """
        Invalidate all sessions for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with invalidation status
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sessions 
                    SET is_active = FALSE
                    WHERE user_id = ?
                ''', (user_id,))
                
                affected_sessions = cursor.rowcount
                conn.commit()
            
            return {
                'success': True,
                'message': f'Invalidated {affected_sessions} sessions',
                'affected_sessions': affected_sessions
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to invalidate user sessions: {str(e)}'}
    
    def get_user_sessions(self, user_id: int) -> Dict:
        """
        Get all active sessions for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with sessions list
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, session_token, created_at, last_accessed, 
                           expires_at, ip_address, user_agent, is_active
                    FROM sessions
                    WHERE user_id = ? AND is_active = TRUE
                    ORDER BY last_accessed DESC
                ''', (user_id,))
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        'id': row[0],
                        'session_token': row[1][:8] + '...',  # Truncate for security
                        'created_at': row[2],
                        'last_accessed': row[3],
                        'expires_at': row[4],
                        'ip_address': row[5],
                        'user_agent': row[6],
                        'is_active': bool(row[7])
                    })
                
                return {
                    'success': True,
                    'sessions': sessions,
                    'total': len(sessions)
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get user sessions: {str(e)}'}
    
    def cleanup_expired_sessions(self) -> Dict:
        """
        Clean up expired sessions
        
        Returns:
            Dict with cleanup status
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sessions 
                    SET is_active = FALSE
                    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE
                ''')
                
                cleaned_sessions = cursor.rowcount
                conn.commit()
            
            return {
                'success': True,
                'message': f'Cleaned up {cleaned_sessions} expired sessions',
                'cleaned_sessions': cleaned_sessions
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Session cleanup failed: {str(e)}'}
    
    def get_session_stats(self) -> Dict:
        """
        Get session statistics
        
        Returns:
            Dict with session stats
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                
                # Total active sessions
                cursor.execute('SELECT COUNT(*) FROM sessions WHERE is_active = TRUE')
                active_sessions = cursor.fetchone()[0]
                
                # Total sessions today
                cursor.execute('''
                    SELECT COUNT(*) FROM sessions 
                    WHERE DATE(created_at) = DATE('now')
                ''')
                today_sessions = cursor.fetchone()[0]
                
                # Expired sessions
                cursor.execute('''
                    SELECT COUNT(*) FROM sessions 
                    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE
                ''')
                expired_sessions = cursor.fetchone()[0]
                
                # Unique users with active sessions
                cursor.execute('''
                    SELECT COUNT(DISTINCT user_id) FROM sessions 
                    WHERE is_active = TRUE
                ''')
                unique_users = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'stats': {
                        'active_sessions': active_sessions,
                        'today_sessions': today_sessions,
                        'expired_sessions': expired_sessions,
                        'unique_users': unique_users
                    }
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get session stats: {str(e)}'}

# Global instance
session_service = SessionService()
