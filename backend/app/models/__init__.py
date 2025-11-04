"""
Models package for new clean architecture
Imports existing SQLAlchemy models from the legacy model/ directory
"""

# Import existing models (keeping original structure intact)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from model import (
    # User Management
    User, Role, Permission, UserRole, RolePermission, Session,
    
    # Minion System  
    ExternalAPIModel, Minion, Profile,
    
    # Training System
    ExternalTrainingJob, UserTrainingDataset, TrainingJobDataset,
    
    # Provider Management
    ProviderCapability, UserProviderConfig, ProviderUsageLog,
    ProviderTestResult, ProviderGroup, UserAPIKey,
    
    # Payment System
    UserSubscription, PaymentHistory, UserUsageLimit,
    
    # Dataset Management
    Dataset, Evaluation,
    
    # Legacy Models
    TrainingJob, ModelProfile, ReferenceModel, Model,
    
    # Base
    Base
)

__all__ = [
    # Base
    'Base',
    
    # User Management
    'User', 'Role', 'Permission', 'UserRole', 'RolePermission', 'Session',
    
    # Minion System
    'ExternalAPIModel', 'Minion', 'Profile',
    
    # Training System
    'ExternalTrainingJob', 'UserTrainingDataset', 'TrainingJobDataset',
    
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
