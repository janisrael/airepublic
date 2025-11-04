"""
Services package for new clean architecture
Business logic layer using repository pattern

All original service files are copied here for the new pipeline.
Original files remain in the root directory for backward compatibility.
"""

# Import new service classes
from .model_service import ModelService

# Import moved service classes (copied from root directory)
try:
    from .chromadb_service import *
    from .external_api_service import *
    from .nvidia_nim_service import *
    from .dataset_service import *
    from .evaluation_service import *
    from .rag_service import *
    from .training_service import *
    
    __all__ = [
        'ModelService',
        # Add other service classes as needed
    ]
except ImportError as e:
    # If imports fail, just include ModelService
    __all__ = ['ModelService']
