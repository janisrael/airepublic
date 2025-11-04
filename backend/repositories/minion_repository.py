"""
Minion repository for minion management operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from model.minion import ExternalAPIModel, Minion, Profile
from .base import BaseRepository

class MinionRepository(BaseRepository[ExternalAPIModel]):
    """Repository for minion (ExternalAPIModel) operations"""
    
    def __init__(self, session: Session):
        super().__init__(ExternalAPIModel, session)
    
    def get_by_user(self, user_id: int) -> List[ExternalAPIModel]:
        """Get all minions for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_active_by_user(self, user_id: int) -> List[ExternalAPIModel]:
        """Get active minions for a user"""
        return self.session.query(ExternalAPIModel).filter(
            ExternalAPIModel.user_id == user_id,
            ExternalAPIModel.is_active == True
        ).all()
    
    def get_by_provider(self, provider: str) -> List[ExternalAPIModel]:
        """Get minions by provider"""
        return self.filter_by(provider=provider)
    
    def get_by_display_name(self, display_name: str) -> Optional[ExternalAPIModel]:
        """Get minion by display name"""
        return self.get_by_field('display_name', display_name)
    
    def get_by_minion_token(self, token: str) -> Optional[ExternalAPIModel]:
        """Get minion by token"""
        return self.get_by_field('minion_token', token)
    
    def get_public_minions(self) -> List[ExternalAPIModel]:
        """Get public minions"""
        return self.filter_by(is_public=True, is_active=True)
    
    def search_minions(self, search_term: str) -> List[ExternalAPIModel]:
        """Search minions by name, description, or tags"""
        return self.search(search_term, ['name', 'display_name', 'description'])
    
    def get_minions_by_level(self, min_level: int = None, max_level: int = None) -> List[ExternalAPIModel]:
        """Get minions by level range"""
        query = self.session.query(ExternalAPIModel)
        
        if min_level is not None:
            query = query.filter(ExternalAPIModel.level >= min_level)
        if max_level is not None:
            query = query.filter(ExternalAPIModel.level <= max_level)
        
        return query.all()
    
    def get_minions_by_rank(self, rank: str) -> List[ExternalAPIModel]:
        """Get minions by rank"""
        return self.filter_by(rank=rank)
    
    def get_top_minions_by_xp(self, limit: int = 10) -> List[ExternalAPIModel]:
        """Get top minions by total XP"""
        return self.session.query(ExternalAPIModel).order_by(
            desc(ExternalAPIModel.total_training_xp + ExternalAPIModel.total_usage_xp)
        ).limit(limit).all()
    
    def get_recently_used_minions(self, user_id: int, limit: int = 10) -> List[ExternalAPIModel]:
        """Get recently used minions for a user"""
        return self.session.query(ExternalAPIModel).filter(
            ExternalAPIModel.user_id == user_id,
            ExternalAPIModel.last_used.isnot(None)
        ).order_by(desc(ExternalAPIModel.last_used)).limit(limit).all()
    
    def update_minion_xp(self, minion_id: int, training_xp: int = 0, usage_xp: int = 0) -> bool:
        """Update minion XP"""
        minion = self.get_by_id(minion_id)
        if minion:
            minion.total_training_xp += training_xp
            minion.total_usage_xp += usage_xp
            self.session.commit()
            return True
        return False
    
    def level_up_minion(self, minion_id: int, new_level: int, new_rank: str, new_rank_level: int) -> bool:
        """Level up minion"""
        minion = self.get_by_id(minion_id)
        if minion:
            minion.level = new_level
            minion.rank = new_rank
            minion.rank_level = new_rank_level
            minion.level_up_count += 1
            self.session.commit()
            return True
        return False
    
    def rank_up_minion(self, minion_id: int, new_rank: str, new_rank_level: int) -> bool:
        """Rank up minion"""
        minion = self.get_by_id(minion_id)
        if minion:
            minion.rank = new_rank
            minion.rank_level = new_rank_level
            minion.rank_up_count += 1
            self.session.commit()
            return True
        return False
    
    def update_minion_usage(self, minion_id: int, requests: int = 1, tokens: int = 0) -> bool:
        """Update minion usage statistics"""
        minion = self.get_by_id(minion_id)
        if minion:
            minion.total_requests += requests
            minion.total_tokens_used += tokens
            self.session.commit()
            return True
        return False
    
    def get_minion_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get minion statistics for a user"""
        minions = self.get_by_user(user_id)
        
        if not minions:
            return {
                'total_minions': 0,
                'active_minions': 0,
                'total_xp': 0,
                'average_level': 0,
                'rank_distribution': {}
            }
        
        active_minions = [m for m in minions if m.is_active]
        total_xp = sum(m.total_training_xp + m.total_usage_xp for m in minions)
        average_level = sum(m.level for m in minions) / len(minions)
        
        rank_distribution = {}
        for minion in minions:
            rank = minion.rank
            rank_distribution[rank] = rank_distribution.get(rank, 0) + 1
        
        return {
            'total_minions': len(minions),
            'active_minions': len(active_minions),
            'total_xp': total_xp,
            'average_level': round(average_level, 2),
            'rank_distribution': rank_distribution
        }

class ProfileRepository(BaseRepository[Profile]):
    """Repository for profile operations"""
    
    def __init__(self, session: Session):
        super().__init__(Profile, session)
    
    def get_by_minion(self, minion_id: int) -> List[Profile]:
        """Get profiles for a minion"""
        return self.filter_by(minion_id=minion_id)
    
    def get_default_profile(self, minion_id: int) -> Optional[Profile]:
        """Get default profile for a minion"""
        return self.session.query(Profile).filter(
            Profile.minion_id == minion_id,
            Profile.is_default == True
        ).first()
    
    def get_active_profiles(self, minion_id: int) -> List[Profile]:
        """Get active profiles for a minion"""
        return self.session.query(Profile).filter(
            Profile.minion_id == minion_id,
            Profile.is_active == True
        ).all()
    
    def set_default_profile(self, profile_id: int) -> bool:
        """Set profile as default"""
        profile = self.get_by_id(profile_id)
        if profile:
            # Remove default from other profiles of the same minion
            self.session.query(Profile).filter(
                Profile.minion_id == profile.minion_id,
                Profile.id != profile_id
            ).update({'is_default': False})
            
            # Set this profile as default
            profile.is_default = True
            self.session.commit()
            return True
        return False
    
    def get_profiles_by_personality(self, personality_trait: str) -> List[Profile]:
        """Get profiles by personality trait"""
        # This would require JSON querying - simplified for now
        return self.session.query(Profile).filter(
            Profile.personality.contains(personality_trait)
        ).all()
    
    def get_profiles_by_expertise(self, expertise_area: str) -> List[Profile]:
        """Get profiles by expertise area"""
        # This would require JSON querying - simplified for now
        return self.session.query(Profile).filter(
            Profile.expertise.contains(expertise_area)
        ).all()
