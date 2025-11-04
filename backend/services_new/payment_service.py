"""
Payment service using SQLAlchemy models and repository pattern
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.payment_repository import PaymentRepository, PaymentHistoryRepository, UserUsageLimitRepository
from model.payment import UserSubscription, PaymentHistory, UserUsageLimit, SubscriptionStatus, PaymentStatus

class PaymentService:
    """Service for payment and subscription operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.subscription_repo = PaymentRepository(session)
        self.payment_repo = PaymentHistoryRepository(session)
        self.limit_repo = UserUsageLimitRepository(session)
    
    def get_user_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """Get user's current subscription"""
        return self.subscription_repo.get_user_subscription(user_id)
    
    def create_subscription(self, user_id: int, **kwargs) -> UserSubscription:
        """Create user subscription"""
        subscription_data = {
            'user_id': user_id,
            **kwargs
        }
        return self.subscription_repo.create(**subscription_data)
    
    def get_payment_history(self, user_id: int) -> List[PaymentHistory]:
        """Get payment history for a user"""
        return self.payment_repo.get_by_user(user_id)
    
    def create_payment(self, user_id: int, **kwargs) -> PaymentHistory:
        """Create payment record"""
        payment_data = {
            'user_id': user_id,
            **kwargs
        }
        return self.payment_repo.create(**payment_data)
    
    def get_user_usage_limits(self, user_id: int) -> List[UserUsageLimit]:
        """Get usage limits for a user"""
        return self.limit_repo.get_by_user(user_id)
    
    def create_usage_limit(self, user_id: int, **kwargs) -> UserUsageLimit:
        """Create usage limit for user"""
        limit_data = {
            'user_id': user_id,
            **kwargs
        }
        return self.limit_repo.create(**limit_data)
