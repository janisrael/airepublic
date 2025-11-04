#!/usr/bin/env python3
"""
Payment Service
Payment integration service for handling subscriptions and billing
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from ..auth_database import auth_db

class PaymentService:
    """Payment integration service"""
    
    def __init__(self):
        # Payment provider configuration
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
        self.stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        self.paypal_client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.paypal_client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        
        # Subscription plans
        self.subscription_plans = {
            'free': {
                'name': 'Free',
                'price': 0,
                'currency': 'usd',
                'interval': 'month',
                'features': ['Basic training', 'Limited API calls', 'Community support']
            },
            'premium': {
                'name': 'Premium',
                'price': 2999,  # $29.99 in cents
                'currency': 'usd',
                'interval': 'month',
                'features': ['Advanced training', 'Unlimited API calls', 'Priority support', 'Custom models']
            },
            'enterprise': {
                'name': 'Enterprise',
                'price': 9999,  # $99.99 in cents
                'currency': 'usd',
                'interval': 'month',
                'features': ['All Premium features', 'Dedicated support', 'Custom integrations', 'SLA']
            }
        }
    
    def get_subscription_plans(self) -> Dict:
        """
        Get available subscription plans
        
        Returns:
            Dict with subscription plans
        """
        try:
            return {
                'success': True,
                'plans': self.subscription_plans
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get subscription plans: {str(e)}'}
    
    def create_subscription(self, user_id: int, plan_name: str, payment_method: str = 'stripe') -> Dict:
        """
        Create a new subscription for user
        
        Args:
            user_id: User ID
            plan_name: Plan name (free, premium, enterprise)
            payment_method: Payment method (stripe, paypal)
        
        Returns:
            Dict with subscription creation status
        """
        try:
            # Validate plan
            if plan_name not in self.subscription_plans:
                return {'success': False, 'error': 'Invalid subscription plan'}
            
            plan = self.subscription_plans[plan_name]
            
            # Check if user already has an active subscription
            existing_subscription = self.get_user_subscription(user_id)
            if existing_subscription['success'] and existing_subscription['subscription']:
                return {'success': False, 'error': 'User already has an active subscription'}
            
            # Create subscription in database
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                
                # Generate subscription ID
                subscription_id = f"sub_{user_id}_{int(datetime.now().timestamp())}"
                
                # Calculate dates
                now = datetime.now()
                if plan_name == 'free':
                    # Free plan - no expiration
                    current_period_start = now
                    current_period_end = None
                    status = 'active'
                else:
                    # Paid plan - monthly billing
                    current_period_start = now
                    current_period_end = now + timedelta(days=30)
                    status = 'pending'  # Will be updated when payment is confirmed
                
                # Insert subscription
                cursor.execute('''
                    INSERT INTO user_subscriptions (
                        user_id, subscription_id, plan_name, plan_type, status,
                        current_period_start, current_period_end, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, subscription_id, plan_name, 'monthly', status,
                    current_period_start, current_period_end, now, now
                ))
                
                # Update user subscription status
                cursor.execute('''
                    UPDATE users 
                    SET subscription_status = ?, updated_at = ?
                    WHERE id = ?
                ''', (status, now, user_id))
                
                # Update usage limits based on plan
                self._update_usage_limits_for_plan(user_id, plan_name, cursor)
                
                conn.commit()
            
            # If free plan, activate immediately
            if plan_name == 'free':
                return {
                    'success': True,
                    'subscription_id': subscription_id,
                    'message': 'Free subscription activated successfully'
                }
            
            # For paid plans, create payment intent
            if payment_method == 'stripe':
                return self._create_stripe_payment_intent(user_id, subscription_id, plan)
            elif payment_method == 'paypal':
                return self._create_paypal_payment(user_id, subscription_id, plan)
            else:
                return {'success': False, 'error': 'Unsupported payment method'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to create subscription: {str(e)}'}
    
    def get_user_subscription(self, user_id: int) -> Dict:
        """
        Get user's current subscription
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with subscription info
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT subscription_id, plan_name, plan_type, status,
                           current_period_start, current_period_end,
                           trial_start, trial_end, created_at, updated_at
                    FROM user_subscriptions
                    WHERE user_id = ? AND status IN ('active', 'trialing')
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return {'success': True, 'subscription': None}
                
                subscription = {
                    'subscription_id': result[0],
                    'plan_name': result[1],
                    'plan_type': result[2],
                    'status': result[3],
                    'current_period_start': result[4],
                    'current_period_end': result[5],
                    'trial_start': result[6],
                    'trial_end': result[7],
                    'created_at': result[8],
                    'updated_at': result[9]
                }
                
                return {'success': True, 'subscription': subscription}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get user subscription: {str(e)}'}
    
    def cancel_subscription(self, user_id: int, subscription_id: str) -> Dict:
        """
        Cancel user subscription
        
        Args:
            user_id: User ID
            subscription_id: Subscription ID
        
        Returns:
            Dict with cancellation status
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                
                # Update subscription status
                cursor.execute('''
                    UPDATE user_subscriptions 
                    SET status = 'cancelled', cancelled_at = ?, updated_at = ?
                    WHERE user_id = ? AND subscription_id = ?
                ''', (datetime.now(), datetime.now(), user_id, subscription_id))
                
                if cursor.rowcount == 0:
                    return {'success': False, 'error': 'Subscription not found'}
                
                # Update user subscription status
                cursor.execute('''
                    UPDATE users 
                    SET subscription_status = 'cancelled', updated_at = ?
                    WHERE id = ?
                ''', (datetime.now(), user_id))
                
                # Reset usage limits to free plan
                self._update_usage_limits_for_plan(user_id, 'free', cursor)
                
                conn.commit()
            
            return {
                'success': True,
                'message': 'Subscription cancelled successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to cancel subscription: {str(e)}'}
    
    def get_payment_history(self, user_id: int, limit: int = 50, offset: int = 0) -> Dict:
        """
        Get user's payment history
        
        Args:
            user_id: User ID
            limit: Number of records to return
            offset: Offset for pagination
        
        Returns:
            Dict with payment history
        """
        try:
            with auth_dbPostgreSQL_path as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ph.id, ph.payment_intent_id, ph.amount, ph.currency,
                           ph.status, ph.payment_method, ph.created_at,
                           us.plan_name, us.plan_type
                    FROM payment_history ph
                    LEFT JOIN user_subscriptions us ON ph.subscription_id = us.id
                    WHERE ph.user_id = ?
                    ORDER BY ph.created_at DESC
                    LIMIT ? OFFSET ?
                ''', (user_id, limit, offset))
                
                payments = []
                for row in cursor.fetchall():
                    payments.append({
                        'id': row[0],
                        'payment_intent_id': row[1],
                        'amount': row[2],
                        'currency': row[3],
                        'status': row[4],
                        'payment_method': row[5],
                        'created_at': row[6],
                        'plan_name': row[7],
                        'plan_type': row[8]
                    })
                
                # Get total count
                cursor.execute('SELECT COUNT(*) FROM payment_history WHERE user_id = ?', (user_id,))
                total = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'payments': payments,
                    'total': total,
                    'limit': limit,
                    'offset': offset
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get payment history: {str(e)}'}
    
    def handle_webhook(self, webhook_data: Dict, provider: str) -> Dict:
        """
        Handle payment provider webhook
        
        Args:
            webhook_data: Webhook payload
            provider: Payment provider (stripe, paypal)
        
        Returns:
            Dict with webhook handling status
        """
        try:
            if provider == 'stripe':
                return self._handle_stripe_webhook(webhook_data)
            elif provider == 'paypal':
                return self._handle_paypal_webhook(webhook_data)
            else:
                return {'success': False, 'error': 'Unsupported payment provider'}
                
        except Exception as e:
            return {'success': False, 'error': f'Webhook handling failed: {str(e)}'}
    
    def _update_usage_limits_for_plan(self, user_id: int, plan_name: str, cursor):
        """Update user usage limits based on subscription plan"""
        plan_limits = {
            'free': {
                'training_jobs': 5,
                'api_calls': 1000,
                'storage': 1024  # 1GB in MB
            },
            'premium': {
                'training_jobs': 50,
                'api_calls': 10000,
                'storage': 10240  # 10GB in MB
            },
            'enterprise': {
                'training_jobs': -1,  # Unlimited
                'api_calls': -1,  # Unlimited
                'storage': 102400  # 100GB in MB
            }
        }
        
        limits = plan_limits.get(plan_name, plan_limits['free'])
        
        for resource_type, limit_value in limits.items():
            cursor.execute('''
                INSERT OR REPLACE INTO user_usage_limits 
                (user_id, resource_type, limit_value, used_value, reset_period, updated_at)
                VALUES (?, ?, ?, 0, 'monthly', ?)
            ''', (user_id, resource_type, limit_value, datetime.now()))
    
    def _create_stripe_payment_intent(self, user_id: int, subscription_id: str, plan: Dict) -> Dict:
        """Create Stripe payment intent"""
        # This would integrate with Stripe API
        # For now, return a placeholder response
        return {
            'success': True,
            'payment_intent_id': f'pi_{subscription_id}',
            'client_secret': f'pi_{subscription_id}_secret',
            'message': 'Stripe payment intent created'
        }
    
    def _create_paypal_payment(self, user_id: int, subscription_id: str, plan: Dict) -> Dict:
        """Create PayPal payment"""
        # This would integrate with PayPal API
        # For now, return a placeholder response
        return {
            'success': True,
            'payment_id': f'paypal_{subscription_id}',
            'approval_url': f'https://paypal.com/approve/{subscription_id}',
            'message': 'PayPal payment created'
        }
    
    def _handle_stripe_webhook(self, webhook_data: Dict) -> Dict:
        """Handle Stripe webhook events"""
        # This would handle Stripe webhook events
        # For now, return a placeholder response
        return {
            'success': True,
            'message': 'Stripe webhook handled'
        }
    
    def _handle_paypal_webhook(self, webhook_data: Dict) -> Dict:
        """Handle PayPal webhook events"""
        # This would handle PayPal webhook events
        # For now, return a placeholder response
        return {
            'success': True,
            'message': 'PayPal webhook handled'
        }

# Global instance
payment_service = PaymentService()
