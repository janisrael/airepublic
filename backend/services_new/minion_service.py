"""
Minion service using SQLAlchemy models and repository pattern
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.minion_repository import MinionRepository, ProfileRepository
from model.minion import ExternalAPIModel, Profile
import secrets
from datetime import datetime

class MinionService:
    """Service for minion management operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.minion_repo = MinionRepository(session)
        self.profile_repo = ProfileRepository(session)
    
    def create_minion(self, user_id: int, name: str, display_name: str, provider: str, 
                     model_name: str, **kwargs) -> ExternalAPIModel:
        """Create a new minion"""
        # Generate minion token
        minion_token = self._generate_minion_token()
        
        # Create minion
        minion_data = {
            'user_id': user_id,
            'name': name,
            'display_name': display_name,
            'provider': provider,
            'model_name': model_name,
            'minion_token': minion_token,
            **kwargs
        }
        
        return self.minion_repo.create(**minion_data)
    
    def get_minion_by_id(self, minion_id: int) -> Optional[ExternalAPIModel]:
        """Get minion by ID"""
        return self.minion_repo.get_by_id(minion_id)
    
    def get_minion_by_token(self, token: str) -> Optional[ExternalAPIModel]:
        """Get minion by token"""
        return self.minion_repo.get_by_minion_token(token)
    
    def get_user_minions(self, user_id: int) -> List[ExternalAPIModel]:
        """Get all minions for a user"""
        return self.minion_repo.get_by_user(user_id)
    
    def get_active_user_minions(self, user_id: int) -> List[ExternalAPIModel]:
        """Get active minions for a user"""
        return self.minion_repo.get_active_by_user(user_id)
    
    def get_public_minions(self) -> List[ExternalAPIModel]:
        """Get public minions"""
        return self.minion_repo.get_public_minions()
    
    def update_minion(self, minion_id: int, **kwargs) -> Optional[ExternalAPIModel]:
        """Update minion"""
        return self.minion_repo.update(minion_id, **kwargs)
    
    def delete_minion(self, minion_id: int) -> bool:
        """Delete minion"""
        return self.minion_repo.delete(minion_id)
    
    def regenerate_minion_token(self, minion_id: int) -> Optional[str]:
        """Regenerate minion token"""
        minion = self.minion_repo.get_by_id(minion_id)
        if minion:
            new_token = self._generate_minion_token()
            minion.minion_token = new_token
            minion.token_created_at = datetime.utcnow()
            self.session.commit()
            return new_token
        return None
    
    def update_minion_xp(self, minion_id: int, training_xp: int = 0, usage_xp: int = 0) -> bool:
        """Update minion XP"""
        return self.minion_repo.update_minion_xp(minion_id, training_xp, usage_xp)
    
    def level_up_minion(self, minion_id: int, new_level: int, new_rank: str, new_rank_level: int) -> bool:
        """Level up minion"""
        return self.minion_repo.level_up_minion(minion_id, new_level, new_rank, new_rank_level)
    
    def rank_up_minion(self, minion_id: int, new_rank: str, new_rank_level: int) -> bool:
        """Rank up minion"""
        return self.minion_repo.rank_up_minion(minion_id, new_rank, new_rank_level)
    
    def update_minion_usage(self, minion_id: int, requests: int = 1, tokens: int = 0) -> bool:
        """Update minion usage statistics"""
        return self.minion_repo.update_minion_usage(minion_id, requests, tokens)
    
    def get_minion_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get minion statistics for a user"""
        return self.minion_repo.get_minion_statistics(user_id)
    
    def get_top_minions_by_xp(self, limit: int = 10) -> List[ExternalAPIModel]:
        """Get top minions by XP"""
        return self.minion_repo.get_top_minions_by_xp(limit)
    
    def get_recently_used_minions(self, user_id: int, limit: int = 10) -> List[ExternalAPIModel]:
        """Get recently used minions"""
        return self.minion_repo.get_recently_used_minions(user_id, limit)
    
    def search_minions(self, search_term: str) -> List[ExternalAPIModel]:
        """Search minions"""
        return self.minion_repo.search_minions(search_term)
    
    def get_minions_by_provider(self, provider: str) -> List[ExternalAPIModel]:
        """Get minions by provider"""
        return self.minion_repo.get_by_provider(provider)
    
    def get_minions_by_level(self, min_level: int = None, max_level: int = None) -> List[ExternalAPIModel]:
        """Get minions by level range"""
        return self.minion_repo.get_minions_by_level(min_level, max_level)
    
    def get_minions_by_rank(self, rank: str) -> List[ExternalAPIModel]:
        """Get minions by rank"""
        return self.minion_repo.get_minions_by_rank(rank)
    
    def create_profile(self, minion_id: int, name: str, **kwargs) -> Profile:
        """Create minion profile"""
        profile_data = {
            'minion_id': minion_id,
            'name': name,
            **kwargs
        }
        
        return self.profile_repo.create(**profile_data)
    
    def get_minion_profiles(self, minion_id: int) -> List[Profile]:
        """Get profiles for a minion"""
        return self.profile_repo.get_by_minion(minion_id)
    
    def get_default_profile(self, minion_id: int) -> Optional[Profile]:
        """Get default profile for a minion"""
        return self.profile_repo.get_default_profile(minion_id)
    
    def set_default_profile(self, profile_id: int) -> bool:
        """Set profile as default"""
        return self.profile_repo.set_default_profile(profile_id)
    
    def update_profile(self, profile_id: int, **kwargs) -> Optional[Profile]:
        """Update profile"""
        return self.profile_repo.update(profile_id, **kwargs)
    
    def delete_profile(self, profile_id: int) -> bool:
        """Delete profile"""
        return self.profile_repo.delete(profile_id)
    
    def get_minion_with_profiles(self, minion_id: int) -> Optional[Dict[str, Any]]:
        """Get minion with its profiles"""
        minion = self.get_minion_by_id(minion_id)
        if not minion:
            return None
        
        profiles = self.get_minion_profiles(minion_id)
        default_profile = self.get_default_profile(minion_id)
        
        return {
            'minion': minion.to_dict(),
            'profiles': [profile.to_dict() for profile in profiles],
            'default_profile': default_profile.to_dict() if default_profile else None
        }
    
    def _generate_minion_token(self, prefix: str = "minion_") -> str:
        """Generate minion token"""
        random_part = secrets.token_urlsafe(16)
        return f"{prefix}{random_part}"
