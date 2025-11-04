"""
Routes package for new clean architecture
API endpoints split from the monolithic api_server.py

All original endpoints are copied here for the new pipeline.
Original endpoints remain in api_server.py for backward compatibility.
"""

# Import route blueprints
from .model_routes import model_bp
from .dataset_routes import dataset_bp
# from .training_routes import training_bp  # Temporarily disabled - needs PostgreSQL migration
from .external_model_routes import external_model_bp

__all__ = [
    'model_bp',
    'dataset_bp',
    # 'training_bp',  # Temporarily disabled
    'external_model_bp'
]
