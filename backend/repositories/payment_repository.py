"""
Payment repository for payment and subscription operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from model.payment import UserSubscription, PaymentHistory, UserUsageLimit, SubscriptionStatus, PaymentStatus
from .base import BaseRepository

class PaymentRepository(BaseRepository[UserSubscription]):
    """Repository for user subscription operations"""
    
    def __init__(self, session: Session):
        super().__init__(UserSubscription, session)
    
    def get_by_user(self, user_id: int) -> List[UserSubscription]:
        """Get subscriptions for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_status(self, status: SubscriptionStatus) -> List[UserSubscription]:
        """Get subscriptions by status"""
        return self.filter_by(status=status)
    
    def get_active_subscriptions(self) -> List[UserSubscription]:
        """Get active subscriptions"""
        return self.get_by_status(SubscriptionStatus.ACTIVE)
    
    def get_user_active_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """Get user's active subscription"""
        return self.session.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == SubscriptionStatus.ACTIVE
        ).first()
    
    def get_user_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """Get user's current subscription (active or trial)"""
        return self.session.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).first()
    
    def get_expired_subscriptions(self) -> List[UserSubscription]:
        """Get expired subscriptions"""
        return self.session.query(UserSubscription).filter(
            UserSubscription.status == SubscriptionStatus.EXPIRED
        ).all()
    
    def get_trial_subscriptions(self) -> List[UserSubscription]:
        """Get trial subscriptions"""
        return self.get_by_status(SubscriptionStatus.TRIAL)
    
    def get_cancelled_subscriptions(self) -> List[UserSubscription]:
        """Get cancelled subscriptions"""
        return self.get_by_status(SubscriptionStatus.CANCELLED)
    
    def get_subscriptions_by_provider(self, payment_provider: str) -> List[UserSubscription]:
        """Get subscriptions by payment provider"""
        return self.filter_by(payment_provider=payment_provider)
    
    def get_subscriptions_by_type(self, subscription_type: str) -> List[UserSubscription]:
        """Get subscriptions by type"""
        return self.filter_by(subscription_type=subscription_type)
    
    def get_subscriptions_expiring_soon(self, days: int = 7) -> List[UserSubscription]:
        """Get subscriptions expiring within specified days"""
        from datetime import datetime, timedelta
        expiry_date = datetime.utcnow() + timedelta(days=days)
        
        return self.session.query(UserSubscription).filter(
            UserSubscription.status == SubscriptionStatus.ACTIVE,
            UserSubscription.end_date <= expiry_date
        ).all()
    
    def cancel_subscription(self, subscription_id: int, reason: str = None) -> bool:
        """Cancel a subscription"""
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = func.now()
            if reason:
                subscription.cancellation_reason = reason
            self.session.commit()
            return True
        return False
    
    def expire_subscription(self, subscription_id: int) -> bool:
        """Expire a subscription"""
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.status = SubscriptionStatus.EXPIRED
            self.session.commit()
            return True
        return False
    
    def get_subscription_statistics(self) -> Dict[str, Any]:
        """Get subscription statistics"""
        total_subscriptions = self.count()
        active_subscriptions = len(self.get_active_subscriptions())
        trial_subscriptions = len(self.get_trial_subscriptions())
        cancelled_subscriptions = len(self.get_cancelled_subscriptions())
        expired_subscriptions = len(self.get_expired_subscriptions())
        
        return {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'trial_subscriptions': trial_subscriptions,
            'cancelled_subscriptions': cancelled_subscriptions,
            'expired_subscriptions': expired_subscriptions
        }

class PaymentHistoryRepository(BaseRepository[PaymentHistory]):
    """Repository for payment history operations"""
    
    def __init__(self, session: Session):
        super().__init__(PaymentHistory, session)
    
    def get_by_user(self, user_id: int) -> List[PaymentHistory]:
        """Get payment history for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_subscription(self, subscription_id: int) -> List[PaymentHistory]:
        """Get payment history for a subscription"""
        return self.filter_by(subscription_id=subscription_id)
    
    def get_by_status(self, status: PaymentStatus) -> List[PaymentHistory]:
        """Get payments by status"""
        return self.filter_by(status=status)
    
    def get_successful_payments(self) -> List[PaymentHistory]:
        """Get successful payments"""
        return self.get_by_status(PaymentStatus.COMPLETED)
    
    def get_failed_payments(self) -> List[PaymentHistory]:
        """Get failed payments"""
        return self.get_by_status(PaymentStatus.FAILED)
    
    def get_pending_payments(self) -> List[PaymentHistory]:
        """Get pending payments"""
        return self.get_by_status(PaymentStatus.PENDING)
    
    def get_refunded_payments(self) -> List[PaymentHistory]:
        """Get refunded payments"""
        return self.get_by_status(PaymentStatus.REFUNDED)
    
    def get_payments_by_provider(self, payment_provider: str) -> List[PaymentHistory]:
        """Get payments by provider"""
        return self.filter_by(payment_provider=payment_provider)
    
    def get_payments_by_date_range(self, start_date, end_date) -> List[PaymentHistory]:
        """Get payments by date range"""
        return self.session.query(PaymentHistory).filter(
            PaymentHistory.created_at >= start_date,
            PaymentHistory.created_at <= end_date
        ).all()
    
    def get_user_payments_by_date_range(self, user_id: int, start_date, end_date) -> List[PaymentHistory]:
        """Get user payments by date range"""
        return self.session.query(PaymentHistory).filter(
            PaymentHistory.user_id == user_id,
            PaymentHistory.created_at >= start_date,
            PaymentHistory.created_at <= end_date
        ).all()
    
    def get_payment_by_provider_id(self, provider_payment_id: str) -> Optional[PaymentHistory]:
        """Get payment by provider payment ID"""
        return self.get_by_field('provider_payment_id', provider_payment_id)
    
    def get_payment_by_transaction_id(self, provider_transaction_id: str) -> Optional[PaymentHistory]:
        """Get payment by provider transaction ID"""
        return self.get_by_field('provider_transaction_id', provider_transaction_id)
    
    def update_payment_status(self, payment_id: str, status: PaymentStatus, error_message: str = None) -> bool:
        """Update payment status"""
        payment = self.get_by_field('payment_id', payment_id)
        if payment:
            payment.status = status
            if error_message:
                payment.error_message = error_message
            self.session.commit()
            return True
        return False
    
    def get_payment_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get payment statistics for a user"""
        payments = self.get_by_user(user_id)
        
        if not payments:
            return {
                'total_payments': 0,
                'successful_payments': 0,
                'failed_payments': 0,
                'total_amount': 0.0,
                'total_refunded': 0.0,
                'success_rate': 0.0
            }
        
        successful_payments = [p for p in payments if p.status == PaymentStatus.COMPLETED]
        failed_payments = [p for p in payments if p.status == PaymentStatus.FAILED]
        
        total_amount = sum(p.amount for p in successful_payments)
        total_refunded = sum(p.refunded_amount for p in payments)
        success_rate = (len(successful_payments) / len(payments)) * 100
        
        return {
            'total_payments': len(payments),
            'successful_payments': len(successful_payments),
            'failed_payments': len(failed_payments),
            'total_amount': round(total_amount, 2),
            'total_refunded': round(total_refunded, 2),
            'success_rate': round(success_rate, 2)
        }
    
    def get_revenue_statistics(self) -> Dict[str, Any]:
        """Get revenue statistics"""
        successful_payments = self.get_successful_payments()
        failed_payments = self.get_failed_payments()
        refunded_payments = self.get_refunded_payments()
        
        total_revenue = sum(p.amount for p in successful_payments)
        total_refunded = sum(p.refunded_amount for p in refunded_payments)
        net_revenue = total_revenue - total_refunded
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_refunded': round(total_refunded, 2),
            'net_revenue': round(net_revenue, 2),
            'successful_payments': len(successful_payments),
            'failed_payments': len(failed_payments),
            'refunded_payments': len(refunded_payments)
        }

class UserUsageLimitRepository(BaseRepository[UserUsageLimit]):
    """Repository for user usage limit operations"""
    
    def __init__(self, session: Session):
        super().__init__(UserUsageLimit, session)
    
    def get_by_user(self, user_id: int) -> List[UserUsageLimit]:
        """Get usage limits for a user"""
        return self.filter_by(user_id=user_id)
    
    def get_by_limit_type(self, limit_type: str) -> List[UserUsageLimit]:
        """Get usage limits by type"""
        return self.filter_by(limit_type=limit_type)
    
    def get_by_period(self, limit_period: str) -> List[UserUsageLimit]:
        """Get usage limits by period"""
        return self.filter_by(limit_period=limit_period)
    
    def get_user_limit(self, user_id: int, limit_type: str, limit_period: str) -> Optional[UserUsageLimit]:
        """Get specific usage limit for a user"""
        return self.session.query(UserUsageLimit).filter(
            UserUsageLimit.user_id == user_id,
            UserUsageLimit.limit_type == limit_type,
            UserUsageLimit.limit_period == limit_period
        ).first()
    
    def get_enforced_limits(self, user_id: int) -> List[UserUsageLimit]:
        """Get enforced usage limits for a user"""
        return self.session.query(UserUsageLimit).filter(
            UserUsageLimit.user_id == user_id,
            UserUsageLimit.is_enforced == True
        ).all()
    
    def get_hard_limits(self, user_id: int) -> List[UserUsageLimit]:
        """Get hard usage limits for a user"""
        return self.session.query(UserUsageLimit).filter(
            UserUsageLimit.user_id == user_id,
            UserUsageLimit.is_hard_limit == True
        ).all()
    
    def get_limits_exceeding_threshold(self, user_id: int, threshold: float = 80.0) -> List[UserUsageLimit]:
        """Get usage limits exceeding warning threshold"""
        return self.session.query(UserUsageLimit).filter(
            UserUsageLimit.user_id == user_id,
            UserUsageLimit.usage_percentage >= threshold
        ).all()
    
    def update_usage(self, limit_id: int, usage: int) -> bool:
        """Update usage for a limit"""
        limit = self.get_by_id(limit_id)
        if limit:
            limit.current_usage = usage
            limit.usage_percentage = (usage / limit.limit_value) * 100
            self.session.commit()
            return True
        return False
    
    def increment_usage(self, limit_id: int, increment: int = 1) -> bool:
        """Increment usage for a limit"""
        limit = self.get_by_id(limit_id)
        if limit:
            limit.current_usage += increment
            limit.usage_percentage = (limit.current_usage / limit.limit_value) * 100
            self.session.commit()
            return True
        return False
    
    def reset_usage(self, limit_id: int) -> bool:
        """Reset usage for a limit"""
        limit = self.get_by_id(limit_id)
        if limit:
            limit.current_usage = 0
            limit.usage_percentage = 0.0
            limit.last_reset = func.now()
            self.session.commit()
            return True
        return False
    
    def reset_user_limits_by_period(self, user_id: int, limit_period: str) -> int:
        """Reset all user limits for a specific period"""
        limits = self.session.query(UserUsageLimit).filter(
            UserUsageLimit.user_id == user_id,
            UserUsageLimit.limit_period == limit_period
        ).all()
        
        count = 0
        for limit in limits:
            limit.current_usage = 0
            limit.usage_percentage = 0.0
            limit.last_reset = func.now()
            count += 1
        
        self.session.commit()
        return count
    
    def get_usage_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        limits = self.get_by_user(user_id)
        
        if not limits:
            return {
                'total_limits': 0,
                'enforced_limits': 0,
                'hard_limits': 0,
                'limits_exceeding_threshold': 0,
                'average_usage': 0.0
            }
        
        enforced_limits = [l for l in limits if l.is_enforced]
        hard_limits = [l for l in limits if l.is_hard_limit]
        limits_exceeding_threshold = [l for l in limits if l.usage_percentage >= l.warning_threshold]
        average_usage = sum(l.usage_percentage for l in limits) / len(limits)
        
        return {
            'total_limits': len(limits),
            'enforced_limits': len(enforced_limits),
            'hard_limits': len(hard_limits),
            'limits_exceeding_threshold': len(limits_exceeding_threshold),
            'average_usage': round(average_usage, 2)
        }
