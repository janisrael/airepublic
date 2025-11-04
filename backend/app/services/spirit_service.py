"""
Spirit Service for managing spirits, purchases, and subscriptions
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from model.spirit_models import (
    SpiritRegistry, SpiritBundle, SubscriptionPlan, UserSpiritPurchase,
    UserSpiritSubscription, UserPoints, UserSpiritAccess, ToolRegistry
)
from database.postgres_connection import create_spirit_engine, get_spirit_database_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class SpiritService:
    """Service for managing spirit operations"""
    
    def __init__(self):
        # Use PostgreSQL spirit system database
        self.engine = create_spirit_engine()
        self.Session = sessionmaker(bind=self.engine)
        print("✅ Using PostgreSQL Spirit System Database")
    
    def get_all_spirits(self) -> List[Dict]:
        """Get all available spirits"""
        with self.Session() as session:
            spirits = session.query(SpiritRegistry).filter(
                SpiritRegistry.is_active == True
            ).all()
            
            return [
                {
                    'id': spirit.id,
                    'name': spirit.name,
                    'category': spirit.category,
                    'description': spirit.description,
                    'icon': spirit.icon,
                    'unlock_rank': spirit.unlock_rank,
                    'unlock_level': spirit.unlock_level,
                    'max_spirit_level': spirit.max_spirit_level,
                    'tools': spirit.tools,
                    'synergies': spirit.synergies,
                    'conflicts': spirit.conflicts,
                    'price_usd': float(spirit.price_usd),
                    'price_points': spirit.price_points,
                    'is_premium': spirit.is_premium,
                    'free_with_subscription': spirit.free_with_subscription,
                    'tier': spirit.tier
                }
                for spirit in spirits
            ]
    
    def get_spirits_by_tier(self, tier: str) -> List[Dict]:
        """Get spirits by pricing tier"""
        with self.Session() as session:
            spirits = session.query(SpiritRegistry).filter(
                and_(
                    SpiritRegistry.is_active == True,
                    SpiritRegistry.tier == tier
                )
            ).all()
            
            return [self._spirit_to_dict(spirit) for spirit in spirits]
    
    def get_free_spirits(self) -> List[Dict]:
        """Get all free spirits"""
        return self.get_spirits_by_tier('free')
    
    def get_spirit_by_id(self, spirit_id: int) -> Optional[Dict]:
        """Get spirit by ID"""
        with self.Session() as session:
            spirit = session.query(SpiritRegistry).filter(
                SpiritRegistry.id == spirit_id
            ).first()
            
            return self._spirit_to_dict(spirit) if spirit else None
    
    def get_spirit_by_name(self, spirit_name: str) -> Optional[Dict]:
        """Get spirit by name"""
        with self.Session() as session:
            spirit = session.query(SpiritRegistry).filter(
                SpiritRegistry.name == spirit_name
            ).first()
            
            return self._spirit_to_dict(spirit) if spirit else None
    
    def get_spirits_for_user_rank(self, user_rank: str, user_level: int) -> List[Dict]:
        """Get spirits available for user's rank and level"""
        with self.Session() as session:
            spirits = session.query(SpiritRegistry).filter(
                and_(
                    SpiritRegistry.is_active == True,
                    or_(
                        SpiritRegistry.unlock_rank == 'Novice',
                        and_(
                            SpiritRegistry.unlock_rank == user_rank,
                            SpiritRegistry.unlock_level <= user_level
                        )
                    )
                )
            ).all()
            
            return [self._spirit_to_dict(spirit) for spirit in spirits]
    
    def calculate_spirit_synergy(self, spirit_ids: List[int]) -> Dict:
        """Calculate synergy bonuses for spirit combination"""
        with self.Session() as session:
            spirits = session.query(SpiritRegistry).filter(
                SpiritRegistry.id.in_(spirit_ids)
            ).all()
            
            synergy_bonus = 0
            conflict_penalty = 0
            synergies = []
            conflicts = []
            
            # Calculate synergies and conflicts
            for i, spirit1 in enumerate(spirits):
                for j, spirit2 in enumerate(spirits[i+1:], i+1):
                    # Check synergies
                    if spirit2.name in spirit1.synergies:
                        bonus = spirit1.synergies[spirit2.name]
                        synergy_bonus += bonus
                        synergies.append({
                            'spirits': [spirit1.name, spirit2.name],
                            'bonus': bonus
                        })
                    
                    # Check conflicts
                    if spirit2.name in spirit1.conflicts:
                        penalty = abs(spirit1.conflicts[spirit2.name])
                        conflict_penalty += penalty
                        conflicts.append({
                            'spirits': [spirit1.name, spirit2.name],
                            'penalty': penalty
                        })
            
            net_performance = synergy_bonus - conflict_penalty
            
            return {
                'synergy_bonus': synergy_bonus,
                'conflict_penalty': conflict_penalty,
                'net_performance': net_performance,
                'synergies': synergies,
                'conflicts': conflicts
            }
    
    def get_spirit_bundles(self) -> List[Dict]:
        """Get all spirit bundles"""
        with self.Session() as session:
            bundles = session.query(SpiritBundle).filter(
                SpiritBundle.is_active == True
            ).all()
            
            return [
                {
                    'id': bundle.id,
                    'name': bundle.name,
                    'description': bundle.description,
                    'spirits': bundle.spirits,
                    'original_price_usd': float(bundle.original_price_usd),
                    'bundle_price_usd': float(bundle.bundle_price_usd),
                    'savings_usd': float(bundle.savings_usd),
                    'savings_percentage': bundle.savings_percentage,
                    'points_cost': bundle.points_cost,
                    'category': bundle.category,
                    'icon': bundle.icon,
                    'is_popular': bundle.is_popular
                }
                for bundle in bundles
            ]
    
    def get_subscription_plans(self) -> List[Dict]:
        """Get all subscription plans"""
        with self.Session() as session:
            plans = session.query(SubscriptionPlan).filter(
                SubscriptionPlan.is_active == True
            ).all()
            
            return [
                {
                    'id': plan.id,
                    'name': plan.name,
                    'price_usd': float(plan.price_usd),
                    'billing_cycle': plan.billing_cycle,
                    'free_spirits': plan.free_spirits,
                    'discount_on_purchases': plan.discount_on_purchases,
                    'exclusive_spirits': plan.exclusive_spirits,
                    'max_minions': plan.max_minions,
                    'max_spirits_per_minion': plan.max_spirits_per_minion,
                    'features': plan.features
                }
                for plan in plans
            ]
    
    def get_user_spirit_access(self, user_id: int) -> List[Dict]:
        """Get spirits user has access to"""
        with self.Session() as session:
            access_records = session.query(UserSpiritAccess).filter(
                and_(
                    UserSpiritAccess.user_id == user_id,
                    UserSpiritAccess.is_active == True
                )
            ).all()
            
            return [
                {
                    'spirit_id': access.spirit_id,
                    'access_type': access.access_type,
                    'source': access.source,
                    'granted_at': access.granted_at.isoformat() if access.granted_at else None,
                    'expires_at': access.expires_at.isoformat() if access.expires_at else None
                }
                for access in access_records
            ]
    
    def get_tools_by_spirit(self, spirit_id: int) -> List[Dict]:
        """Get tools available for a specific spirit"""
        with self.Session() as session:
            spirit = session.query(SpiritRegistry).filter(
                SpiritRegistry.id == spirit_id
            ).first()
            
            if not spirit:
                return []
            
            # Get tools from registry
            tools = session.query(ToolRegistry).filter(
                and_(
                    ToolRegistry.name.in_(spirit.tools),
                    ToolRegistry.is_active == True
                )
            ).all()
            
            return [
                {
                    'id': tool.id,
                    'name': tool.name,
                    'category': tool.category,
                    'description': tool.description
                }
                for tool in tools
            ]
    
    def _spirit_to_dict(self, spirit: SpiritRegistry) -> Dict:
        """Convert spirit model to dictionary"""
        if not spirit:
            return None
            
        return {
            'id': spirit.id,
            'name': spirit.name,
            'category': spirit.category,
            'description': spirit.description,
            'icon': spirit.icon,
            'unlock_rank': spirit.unlock_rank,
            'unlock_level': spirit.unlock_level,
            'max_spirit_level': spirit.max_spirit_level,
            'tools': spirit.tools,
            'synergies': spirit.synergies,
            'conflicts': spirit.conflicts,
            'price_usd': float(spirit.price_usd),
            'price_points': spirit.price_points,
            'is_premium': spirit.is_premium,
            'free_with_subscription': spirit.free_with_subscription,
            'tier': spirit.tier
        }
