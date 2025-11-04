"""
SQLAlchemy Models for AI Refinement Dashboard
Hybrid SQLAlchemy + PostgreSQL architecture
"""

from .base import Base
from .user import User, Role, Permission, UserRole, RolePermission, Session
from .minion import ExternalAPIModel, Minion, Profile
from .training import ExternalTrainingJob, UserTrainingDataset, TrainingJobDataset
from .training_results import TrainingResult
from .provider import ProviderCapability, UserProviderConfig, ProviderUsageLog, ProviderTestResult, ProviderGroup, UserAPIKey
from .payment import UserSubscription, PaymentHistory, UserUsageLimit
from .dataset import Dataset, Evaluation
from .legacy import TrainingJob, ModelProfile, Model
from .reference_models import ReferenceModel
from .spirit_models import SpiritRegistry, MinionSpirit, SpiritMastery, SpiritBundle, SubscriptionPlan, UserSpiritPurchase, UserSpiritSubscription, UserPoints, PointsTransaction, UserSpiritAccess, ToolRegistry, SpiritMinion

__all__ = [
    # Base
    'Base',
    
    # User Management
    'User', 'Role', 'Permission', 'UserRole', 'RolePermission', 'Session',
    
    # Minion System
    'ExternalAPIModel', 'Minion', 'Profile',
    
    # Training System
    'ExternalTrainingJob', 'UserTrainingDataset', 'TrainingJobDataset', 'TrainingResult',
    
    # Provider Management
    'ProviderCapability', 'UserProviderConfig', 'ProviderUsageLog', 
    'ProviderTestResult', 'ProviderGroup', 'UserAPIKey',
    
    # Payment System
    'UserSubscription', 'PaymentHistory', 'UserUsageLimit',
    
    # Dataset Management
    'Dataset', 'Evaluation',
    
    # Legacy Models
    'TrainingJob', 'ModelProfile', 'ReferenceModel', 'Model'
]
