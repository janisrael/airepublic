"""
Training Routes - New Clean Architecture
Handles all training-related API endpoints

Original endpoints moved from api_server.py:
- /api/training-jobs (GET, POST)
- /api/training-jobs/<int:job_id> (PUT, DELETE)
- /api/start-training (POST)
- /api/training-jobs/<int:job_id>/start (POST)
- /api/training-jobs/<int:job_id>/stop (POST)
- /api/training-jobs/<int:job_id>/status (GET)
- /api/training-jobs/<int:job_id>/progress (POST)
- /api/training-jobs/<int:job_id>/output (POST)
- /api/detect-stuck-training (POST)
- /api/training-history (GET)
- /api/training-history/<int:job_id> (GET)
"""

from flask import Blueprint, jsonify, request
import json
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import from root database.py (original file)
import importlib.util
spec = importlib.util.spec_from_file_location('root_database', 'database.py')
root_database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_database)

# Use the Database class from root database.py
Database = root_database.Database

# Import training service (moved to new structure)
from app.services.training_service import *

training_bp = Blueprint('training', __name__, url_prefix='/api/v2')

# Using SQLAlchemy service instead of direct PostgreSQL connection

@training_bp.route('/training-jobs', methods=['GET'])
def get_training_jobs_v2():
    """Get all training jobs - NEW VERSION"""
    try:
        jobs = db.get_all_training_jobs()
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': len(jobs)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training-jobs', methods=['POST'])
def create_training_job_v2():
    """Create a new training job - NEW VERSION"""
    try:
        # Handle both JSON and FormData requests
        if request.content_type and 'multipart/form-data' in request.content_type:
            # FormData request (with avatar)
            training_data_str = request.form.get('trainingData')
            if not training_data_str:
                return jsonify({
                    'success': False,
                    'error': 'Training data is required'
                }), 400
            
            data = json.loads(training_data_str)
            avatar_file = request.files.get('avatar')
        else:
            # Regular JSON request
            data = request.get_json()
            avatar_file = None
        
        # Validate required fields
        if not data.get('jobName'):
            return jsonify({
                'success': False,
                'error': 'Job name is required'
            }), 400
        
        if not data.get('baseModel'):
            return jsonify({
                'success': False,
                'error': 'Base model is required'
            }), 400
        
        # Create training job data
        job_data = {
            'job_name': data['jobName'],
            'base_model': data['baseModel'],
            'dataset_id': data.get('dataset'),
            'learning_rate': data.get('learningRate', 0.0001),
            'epochs': data.get('epochs', 3),
            'batch_size': data.get('batchSize', 1),
            'max_length': data.get('maxLength', 512),
            'status': 'PENDING',
            'description': data.get('description', ''),
            'tags': data.get('tags', []),
            'config': {
                'lora_rank': data.get('loraRank', 16),
                'lora_alpha': data.get('loraAlpha', 32),
                'lora_dropout': data.get('loraDropout', 0.1),
                'target_modules': data.get('targetModules', ['q_proj', 'v_proj']),
                'gradient_accumulation_steps': data.get('gradientAccumulationSteps', 1),
                'warmup_steps': data.get('warmupSteps', 100),
                'weight_decay': data.get('weightDecay', 0.01),
                'fp16': data.get('fp16', True),
                'dataloader_num_workers': data.get('dataloaderNumWorkers', 0),
                'save_steps': data.get('saveSteps', 500),
                'eval_steps': data.get('evalSteps', 500),
                'logging_steps': data.get('loggingSteps', 10),
                'max_grad_norm': data.get('maxGradNorm', 1.0),
                'adam_beta1': data.get('adamBeta1', 0.9),
                'adam_beta2': data.get('adamBeta2', 0.999),
                'adam_epsilon': data.get('adamEpsilon', 1e-8),
                'lr_scheduler_type': data.get('lrSchedulerType', 'linear'),
                'num_train_epochs': data.get('epochs', 3),
                'per_device_train_batch_size': data.get('batchSize', 1),
                'gradient_accumulation_steps': data.get('gradientAccumulationSteps', 1),
                'learning_rate': data.get('learningRate', 0.0001),
                'max_length': data.get('maxLength', 512)
            }
        }
        
        # Add avatar if provided
        if avatar_file:
            # Handle avatar upload (simplified for now)
            job_data['avatar_url'] = f"/avatars/training_{data['jobName']}.png"
        
        # Save to database
        job_id = db.add_training_job(job_data)
        
        return jsonify({
            'success': True,
            'message': 'Training job created successfully',
            'job_id': job_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training-jobs/<int:job_id>', methods=['PUT'])
def update_training_job_v2(job_id):
    """Update a training job - NEW VERSION"""
    try:
        data = request.get_json()
        
        # Validate job exists
        job = db.get_training_job(job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': 'Training job not found'
            }), 404
        
        # Update job data
        success = db.update_training_job(job_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Training job updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update training job'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training-jobs/<int:job_id>', methods=['DELETE'])
def delete_training_job_v2(job_id):
    """Delete a training job - NEW VERSION"""
    try:
        success = db.delete_training_job(job_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Training job deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Training job not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training-jobs/<int:job_id>/status', methods=['GET'])
def get_training_status_v2(job_id):
    """Get training job status - NEW VERSION"""
    try:
        job = db.get_training_job(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Training job not found'
            }), 404
        
        return jsonify({
            'success': True,
            'status': job.get('status', 'UNKNOWN'),
            'progress': job.get('progress', 0),
            'message': job.get('message', '')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/api/start-training-v2', methods=['POST'])
def start_training_v2():
    """Start training - NEW VERSION"""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({
                'success': False,
                'error': 'Job ID is required'
            }), 400
        
        # Use training service to start training
        # This would integrate with the moved training_service.py
        result = start_training_job(job_id)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Training started successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to start training')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/api/training-history-v2', methods=['GET'])
def get_training_history_v2():
    """Get training history - NEW VERSION"""
    try:
        history = db.get_training_history()
        return jsonify({
            'success': True,
            'history': history,
            'total': len(history)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/api/training-history-v2/<int:job_id>', methods=['GET'])
def get_training_job_history_v2(job_id):
    """Get specific training job history - NEW VERSION"""
    try:
        job_history = db.get_training_job_history(job_id)
        
        if not job_history:
            return jsonify({
                'success': False,
                'error': 'Training job history not found'
            }), 404
        
        return jsonify({
            'success': True,
            'history': job_history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/api/training-v2/health', methods=['GET'])
def health_check_v2():
    """Health check for the new training API"""
    try:
        # Attempt to get training jobs to verify database connection
        jobs = db.get_all_training_jobs()
        return jsonify({
            'success': True,
            'message': 'Training API v2 is healthy',
            'total_jobs': len(jobs)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Training API v2 health check failed: {e}"
        }), 500
