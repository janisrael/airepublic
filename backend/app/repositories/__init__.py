"""
Repositories package for new clean architecture
Imports existing repositories and creates new ones
"""

# Import existing repositories (keeping original structure intact)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from repositories import (
        BaseRepository,
        DatasetRepository,
        MinionRepository,
        PaymentRepository,
        ProviderRepository,
        TrainingRepository,
        UserRepository
    )
    
    __all__ = [
        'BaseRepository',
        'DatasetRepository', 
        'MinionRepository',
        'PaymentRepository',
        'ProviderRepository',
        'TrainingRepository',
        'UserRepository'
    ]
except ImportError:
    # If repositories don't exist yet, we'll create them
    __all__ = []
