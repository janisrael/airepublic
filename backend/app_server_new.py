"""
New Flask Server - Clean Architecture
Uses new SQLAlchemy routes alongside original api_server.py

This is the new pipeline alongside existing code.
Original api_server.py remains untouched for backward compatibility.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import new route blueprints
from app.routes.auth_routes import auth_bp
from app.routes.model_routes import model_bp
from app.routes.dataset_routes import dataset_bp
from app.routes.training_routes_v2 import training_bp  # New V2 training routes
from app.routes.external_model_routes import external_model_bp
from app.routes.spirit_routes import spirit_bp
# from app.routes.minion_spirit_routes import minion_spirit_bp  # Temporarily disabled - needs PostgreSQL migration
from app.routes.user_minion_routes import user_minion_bp
from app.routes.training_websocket_routes import init_websocket_routes
from app.routes.minion_class_routes import minion_class_bp  # New class routes
from app.routes.microservice_routes import microservice_bp  # New microservice routes

# Initialize training websocket service
from services.training_websocket_service import init_training_websocket_service
from app.routes.reference_model_routes import reference_model_bp
from app.routes.rbac_routes import rbac_bp
from app.routes.score_routes import score_bp
from app.routes.minion_update_routes import minion_update_bp

# Note: minion_history_endpoints and external_lora_endpoints were removed
# as they were PostgreSQL-based and have PostgreSQL equivalents in the app/routes

# Create new Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize training websocket service
init_training_websocket_service(socketio)

# Initialize websocket routes
init_websocket_routes(socketio)

# Register all new route blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(model_bp)
app.register_blueprint(dataset_bp)
app.register_blueprint(training_bp)  # Register V2 training routes
app.register_blueprint(external_model_bp)
app.register_blueprint(spirit_bp)
# app.register_blueprint(minion_spirit_bp)  # Temporarily disabled - needs PostgreSQL migration
app.register_blueprint(user_minion_bp)
app.register_blueprint(reference_model_bp)
app.register_blueprint(rbac_bp)
app.register_blueprint(score_bp)
app.register_blueprint(minion_update_bp)
app.register_blueprint(minion_class_bp)  # Register class routes
app.register_blueprint(microservice_bp)  # Register microservice routes
# Note: minion_history_bp and external_lora_blueprint removed (PostgreSQL-based)

# Copy configuration from original app
# Configure Flask app
app.config['SECRET_KEY'] = 'ai-republic-secret-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Configure static file serving for uploads
from flask import send_from_directory
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

print("🚀 New Clean Architecture Server Started")
print("📊 Available endpoints:")
print("   - /api/v2/models        (NEW: Models API)")
print("   - /api/v2/datasets      (NEW: Datasets API)")
print("   - /api/v2/training-jobs (NEW: Training API)")
print("   - /api/v2/external-models (NEW: External Models API)")
print("   - /api/v2/spirits       (NEW: Spirit System API)")
print("   - /api/v2/minions       (NEW: Minion-Spirit Integration)")
print("   - /api/v2/classes       (NEW: Minion Class System)")
print("   - /api/v2/microservice  (NEW: Spirit Orchestrator Microservice)")
print("   - /api/minions/<id>/history (NEW: Minion History Timeline)")
print("   - /api/users/<id>/external-lora-training (NEW: External LoRA Training)")
print("   - /api/status           (NEW: Server status)")
print("")
print("🔗 Original endpoints still available via original api_server.py")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'architecture': 'PostgreSQL + SQLAlchemy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/status', methods=['GET'])
def server_status():
    """Server status endpoint"""
    return {
        'success': True,
        'message': 'New Clean Architecture Server is running',
        'version': '2.0.0',
                'endpoints': {
                    'new': [
                        '/api/auth/login',  # NEW V2 Authentication
                        '/api/auth/register',
                        '/api/auth/logout',
                        '/api/auth/verify',
                        '/api/auth/refresh',
                        '/api/auth/forgot-password',
                        '/api/auth/reset-password',
                        '/api/auth/profile',
                        '/api/auth/change-password',
                        '/api/v2/models',
                        '/api/v2/datasets',
                        '/api/v2/training-jobs',
                        '/api/v2/external-models',
                        '/api/v2/spirits',
                        '/api/v2/minions',
                        '/api/v2/users/<user_id>/minions',  # NEW V2 User Minions
                        '/api/v2/reference-models',  # NEW V2 Reference Models
                        '/api/minions/<id>/history',  # NEW Minion History Timeline
                        '/api/users/<id>/external-lora-training',  # NEW External LoRA Training
                        '/api/status'
                    ],
                    'original': 'Available via original api_server.py'
                }
    }


if __name__ == '__main__':
    print("🌟 Starting New Clean Architecture Server on port 5001")
    print("📝 V2 server running on port 5001")
    print("🔄 Both servers can run simultaneously for testing")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
