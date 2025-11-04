"""
Training Routes - V2 Clean Architecture with SQLAlchemy
Handles training-related API endpoints

Endpoints:
- /api/v2/training-jobs (GET) - Get all training jobs
- /api/v2/training-jobs (POST) - Create new training job
- /api/v2/training-jobs/<int:job_id> (GET, PUT, DELETE) - Manage specific job
"""

from flask import Blueprint, jsonify, request
import json
from sqlalchemy.orm import sessionmaker
from database.postgres_connection import create_spirit_engine
from services_new.training_service import TrainingService
from app.services.minion_service import MinionService
from model.training import ExternalTrainingJob
from model.training_results import TrainingResult

training_bp = Blueprint('training', __name__, url_prefix='/api/v2')

# SQLAlchemy session factory for training services
_engine = create_spirit_engine()
_SessionLocal = sessionmaker(bind=_engine)

def _job_to_dict(job: ExternalTrainingJob):
    return {
        'id': job.id,
        'user_id': job.user_id,
        'minion_id': job.minion_id,
        'job_name': job.job_name,
        'description': job.description,
        'training_type': job.training_type.value if getattr(job, 'training_type', None) else None,
        'provider': job.provider,
        'model_name': job.model_name,
        'status': job.status.value if getattr(job, 'status', None) else None,
        'progress': job.progress,
        'xp_gained': job.xp_gained,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        'created_at': job.created_at.isoformat() if getattr(job, 'created_at', None) else None,
        'updated_at': job.updated_at.isoformat() if getattr(job, 'updated_at', None) else None,
    }

@training_bp.route('/training-jobs', methods=['GET'])
def get_training_jobs_v2():
    """Get all training jobs - V2 PostgreSQL version"""
    try:
        # Return empty list for now - training functionality not yet migrated
        return jsonify({
            'success': True,
            'jobs': [],
            'total': 0,
            'database': 'SQLAlchemy + PostgreSQL',
            'version': '2.0.0',
            'message': 'Training jobs endpoint - not yet fully migrated to PostgreSQL'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error fetching training jobs'
        }), 500


@training_bp.route('/users/<int:user_id>/external-training/jobs', methods=['GET', 'POST', 'OPTIONS'])
def get_user_external_training_jobs(user_id: int):
    """Return external training jobs for a user.

    Supports query params:
      - group_by=minion → groups jobs by minion_id
      - latest_only=true → returns latest job per minion
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return ('', 200)

    try:
        # Support POST to create a new external training job scoped to the user
        if request.method == 'POST':
            # Handle both JSON and FormData requests (for file uploads)
            import json
            
            if request.content_type and 'multipart/form-data' in request.content_type:
                # FormData request (with file uploads)
                training_data_str = request.form.get('trainingData')
                if not training_data_str:
                    return jsonify({
                        'success': False,
                        'error': 'Training data is required',
                        'message': 'Invalid training job data'
                    }), 400
                
                data = json.loads(training_data_str)
                
                # Handle file uploads (store files for processing)
                uploaded_files = []
                if 'fileCount' in request.form:
                    file_count = int(request.form.get('fileCount', 0))
                    for i in range(file_count):
                        file_key = f'file_{i}'
                        if file_key in request.files:
                            uploaded_files.append(request.files[file_key])
                
                # Store files in data for later processing
                data['uploaded_files'] = uploaded_files
            else:
                # Regular JSON request
                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'Request body is required',
                        'message': 'Invalid training job data'
                    }), 400

            # Validate required fields
            required_fields = ['jobName', 'minionId', 'provider', 'model', 'type']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}',
                        'message': 'Invalid training job data'
                    }), 400

            # Use services to create job
            from app.services.training_service import TrainingService as AppTrainingService
            from app.services.minion_service import MinionService as AppMinionService

            training_service = AppTrainingService()
            minion_service = AppMinionService()
            
            # Check for duplicate training jobs (same config + datasets)
            rag_config = data.get('ragConfig', {})
            selected_datasets = data.get('datasets', [])
            force_retrain = data.get('forceRetrain', False)
            
            if not force_retrain and rag_config and selected_datasets:
                existing_job = training_service.exists_similar_job(
                    user_id=user_id,  # Use URL parameter, not request body
                    minion_id=data['minionId'],
                    rag_config=rag_config,
                    selected_datasets=selected_datasets
                )
                
                if existing_job:
                    config_info = training_service.get_job_config_info(existing_job)
                    return jsonify({
                        'success': False,
                        'status': 'duplicate',
                        'message': 'A similar training job was already created recently.',
                        'duplicate_info': {
                            'existing_job_id': existing_job.id,
                            'existing_job_name': existing_job.job_name,
                            'config_fingerprint': config_info['config_fingerprint'],
                            'created_at': config_info['created_at'],
                            'status': config_info['status'],
                            'xp_gained': config_info['xp_gained']
                        },
                        'retrain_allowed': True,
                        'suggestion': 'Use forceRetrain: true to override this check'
                    }), 409

            minion = minion_service.get_minion_by_id(data['minionId'])
            if not minion:
                return jsonify({
                    'success': False,
                    'error': f'Minion {data["minionId"]} not found',
                    'message': 'Invalid minion ID'
                }), 404

            # Handle file uploads - save files temporarily if present
            uploaded_file_paths = []
            if 'uploaded_files' in data and data['uploaded_files']:
                import os
                import uuid
                upload_dir = 'uploads/training_files'
                os.makedirs(upload_dir, exist_ok=True)
                
                for file_obj in data['uploaded_files']:
                    if file_obj and file_obj.filename:
                        # Generate unique filename
                        file_ext = os.path.splitext(file_obj.filename)[1]
                        unique_filename = f"{uuid.uuid4()}{file_ext}"
                        file_path = os.path.join(upload_dir, unique_filename)
                        
                        # Save file
                        file_obj.save(file_path)
                        uploaded_file_paths.append(file_path)
                
                # Store file paths in rag_config for later processing
                if 'ragConfig' not in data:
                    data['ragConfig'] = {}
                data['ragConfig']['uploaded_file_paths'] = uploaded_file_paths

            job_data = {
                'job_name': data['jobName'],
                'description': data.get('description', ''),
                'minion_id': data['minionId'],
                'user_id': user_id,  # Use URL parameter, not request body
                'provider': data['provider'],
                'model': data['model'],
                'training_type': data['type'],
                'status': 'pending',
                'config': {
                    'rag_config': data.get('ragConfig', {}),
                    'selected_datasets': data.get('selectedDatasets', []),
                    'minion_config': minion
                }
            }
            
            # Create job with configuration hash for duplicate detection
            job = training_service.create_training_job_with_hash(
                job_data, 
                rag_config, 
                selected_datasets
            )

            # Create a history record (best-effort)
            try:
                with _SessionLocal() as session:
                    minion_details = minion_service.get_minion_by_id(data['minionId'])
                    training_result = TrainingResult(
                        job_id=job.id,
                        minion_id=data['minionId'],
                        user_id=user_id,
                        training_type=data['type'].upper(),
                        collection_name=data.get('ragConfig', {}).get('collectionName'),
                        before_metrics={
                            'minion_stats': {
                                'level': minion_details.get('level', 1),
                                'xp': minion_details.get('total_training_xp', 0) + minion_details.get('total_usage_xp', 0),
                                'rank': minion_details.get('rank', 'Novice'),
                                'score': minion_details.get('score', 0),
                                'capabilities': minion_details.get('capabilities', []),
                                'parameters': minion_details.get('parameters', {})
                            },
                            'timestamp': job.created_at.isoformat() if job.created_at else None
                        },
                        rag_config=data.get('ragConfig', {}),
                        minion_config=minion,
                        xp_gained=0,
                        accuracy_improvement=0.0,
                        speed_improvement=0.0,
                        knowledge_improvement=0.0,
                        overall_improvement=0.0
                    )
                    session.add(training_result)
                    session.commit()
            except Exception as history_error:
                # Warning: Could not create history record: {history_error}
                pass

            return jsonify({
                'success': True,
                'job': {
                    'id': job.id,
                    'job_name': job.job_name,
                    'status': job.status.value if hasattr(job.status, 'value') else str(job.status),
                    'minion_id': job.minion_id,
                    'user_id': job.user_id,
                    'created_at': job.created_at.isoformat() if job.created_at else None
                },
                'message': f'Training job "{job.job_name}" created successfully'
            }), 201
        group_by = request.args.get('group_by')
        latest_only = (request.args.get('latest_only', 'false').lower() == 'true')

        with _SessionLocal() as session:
            service = TrainingService(session)
            minion_service = MinionService()
            if group_by == 'minion' or latest_only:
                grouped = service.get_grouped_training_jobs(user_id)
                latest_jobs = grouped.get('latest_jobs', {})
                result = {
                    'success': True,
                    'group_by': 'minion' if group_by == 'minion' else None,
                    'latest_only': latest_only,
                }
                if group_by == 'minion':
                    grouped_serialized = {
                        str(minion_id): [_job_to_dict(j) for j in jobs]
                        for minion_id, jobs in (grouped.get('grouped_jobs') or {}).items()
                    }
                    result['grouped_jobs'] = grouped_serialized
                if latest_only:
                    latest_list = [_job_to_dict(j) for j in (latest_jobs or {}).values()]
                    result['latest_jobs'] = latest_list
                # Compose minions list with latest training snapshot
                user_minions = minion_service.get_user_minions(user_id)
                minions_out = []
                for m in user_minions:
                    latest = None
                    if latest_jobs:
                        # latest_jobs keys are minion_id; values are job objects
                        lj = latest_jobs.get(m['id']) if isinstance(latest_jobs, dict) else None
                        if lj:
                            latest = _job_to_dict(lj)
                    # training count
                    training_count = 0
                    gj = (grouped.get('grouped_jobs') or {}).get(m['id']) if grouped else None
                    if gj:
                        training_count = len(gj)
                    # attach
                    minion_entry = {
                        **m,
                        'latest_training': latest,
                        'training_count': training_count
                    }
                    minions_out.append(minion_entry)
                result['minions'] = minions_out
                result['total'] = len(minions_out)
                return jsonify(result)
            else:
                jobs = service.get_user_training_jobs(user_id)
                return jsonify({
                    'success': True,
                    'jobs': [_job_to_dict(j) for j in jobs],
                    'total': len(jobs)
                })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error fetching user external training jobs'
        }), 500

@training_bp.route('/training-jobs/check-duplicate', methods=['POST'])
def check_duplicate_training():
    """Check if a similar training job already exists without creating one"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['minionId', 'ragConfig', 'datasets']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}',
                    'message': 'Invalid request data'
                }), 400
        
        # Use services to check for duplicates
        from app.services.training_service import TrainingService as AppTrainingService
        training_service = AppTrainingService()
        
        rag_config = data.get('ragConfig', {})
        selected_datasets = data.get('datasets', [])
        
        # For check-duplicate endpoint, we need user_id from request body
        user_id = data.get('userId')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing required field: userId',
                'message': 'Invalid request data'
            }), 400
        
        existing_job = training_service.exists_similar_job(
            user_id=user_id,
            minion_id=data['minionId'],
            rag_config=rag_config,
            selected_datasets=selected_datasets
        )
        
        if existing_job:
            config_info = training_service.get_job_config_info(existing_job)
            return jsonify({
                'success': True,
                'is_duplicate': True,
                'duplicate_info': {
                    'existing_job_id': existing_job.id,
                    'existing_job_name': existing_job.job_name,
                    'config_fingerprint': config_info['config_fingerprint'],
                    'created_at': config_info['created_at'],
                    'status': config_info['status'],
                    'xp_gained': config_info['xp_gained']
                },
                'message': 'Similar training job found',
                'retrain_allowed': True
            }), 200
        else:
            return jsonify({
                'success': True,
                'is_duplicate': False,
                'message': 'No similar training job found - safe to proceed'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error checking for duplicate training jobs'
        }), 500

@training_bp.route('/training-jobs', methods=['POST'])
def create_training_job_v2():
    """Create new training job - V2 PostgreSQL version"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['jobName', 'minionId', 'provider', 'model', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}',
                    'message': 'Invalid training job data'
                }), 400
        
        # Import services
        from app.services.training_service import TrainingService
        from app.services.minion_service import MinionService
        
        training_service = TrainingService()
        minion_service = MinionService()
        
        # Get user ID from request (for now, use user_id from URL or default to 2)
        user_id = request.view_args.get('user_id', 2)
        
        # Get minion details
        minion = minion_service.get_minion_by_id(data['minionId'])
        if not minion:
            return jsonify({
                'success': False,
                'error': f'Minion {data["minionId"]} not found',
                'message': 'Invalid minion ID'
            }), 404

        # Enforce single pending/running job per minion per user
        try:
            user_pending = training_service.training_repo.get_user_pending_jobs(user_id)
            user_running = training_service.training_repo.get_user_running_jobs(user_id)

            for pj in (user_pending or []) + (user_running or []):
                if pj.minion_id == data['minionId']:
                    return jsonify({
                        'success': False,
                        'error': 'A pending or running training job already exists for this minion. Please delete/cancel or start that job before creating a new one.',
                        'existing_job_id': pj.id,
                        'message': 'Minion already has a pending or running job'
                    }), 409
        except Exception as check_err:
            # If repo check fails, log and continue (do not block creation)
            # Warning: could not verify existing pending jobs: {check_err}
            pass
        
        # Create training job
        job_data = {
            'job_name': data['jobName'],
            'description': data.get('description', ''),
            'minion_id': data['minionId'],
            'user_id': user_id,
            'provider': data['provider'],
            'model': data['model'],
            'training_type': data['type'],
            'status': 'pending',
            'config': {
                'rag_config': data.get('ragConfig', {}),
                'selected_datasets': data.get('selectedDatasets', []),
                'minion_config': minion
            }
        }
        
        # Create job in database
        job = training_service.create_training_job(job_data)
        
        # Create history record for tracking
        try:
            with _SessionLocal() as session:
                # Get minion stats snapshot for history
                minion_service = MinionService()
                minion_details = minion_service.get_minion_by_id(data['minionId'])
                
                # Create training result record
                training_result = TrainingResult(
                    job_id=job.id,
                    minion_id=data['minionId'],
                    user_id=user_id,
                    training_type=data['type'].upper(),
                    collection_name=data.get('ragConfig', {}).get('collectionName'),
                    before_metrics={
                        'minion_stats': {
                            'level': minion_details.get('level', 1),
                            'xp': minion_details.get('total_training_xp', 0) + minion_details.get('total_usage_xp', 0),
                            'rank': minion_details.get('rank', 'Novice'),
                            'score': minion_details.get('score', 0),
                            'capabilities': minion_details.get('capabilities', []),
                            'parameters': minion_details.get('parameters', {})
                        },
                        'timestamp': job.created_at.isoformat() if job.created_at else None
                    },
                    rag_config=data.get('ragConfig', {}),
                    minion_config=minion,
                    xp_gained=0,  # Will be updated after training
                    accuracy_improvement=0.0,
                    speed_improvement=0.0,
                    knowledge_improvement=0.0,
                    overall_improvement=0.0
                )
                
                session.add(training_result)
                session.commit()
                
                # History record created for job {job.id}
                
        except Exception as history_error:
            # Warning: Could not create history record: {history_error}
            # Don't fail the job creation if history fails
            pass
        
        return jsonify({
            'success': True,
            'job': {
                'id': job.id,
                'job_name': job.job_name,
                'status': job.status.value if hasattr(job.status, 'value') else str(job.status),
                'minion_id': job.minion_id,
                'user_id': job.user_id,
                'created_at': job.created_at.isoformat() if job.created_at else None
            },
            'message': f'Training job "{job.job_name}" created successfully'
        }), 201
        
    except Exception as e:
        # Error creating training job: {e}
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error creating training job'
        }), 500

@training_bp.route('/training-jobs/<int:job_id>', methods=['GET'])
def get_training_job_v2(job_id):
    """Get specific training job - V2 PostgreSQL version"""
    try:
        from app.services.training_service import TrainingService
        
        training_service = TrainingService()
        job = training_service.get_training_job(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'message': f'Training job {job_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'job': _job_to_dict(job)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error fetching training job'
        }), 500


@training_bp.route('/training-jobs/<int:job_id>', methods=['DELETE'])
def delete_training_job_v2(job_id):
    """Delete a training job - V2 PostgreSQL version"""
    try:
        from app.services.training_service import TrainingService

        service = TrainingService()

        # Ensure job exists
        job = service.get_training_job(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Training job not found'}), 404

        # Only allow delete if not RUNNING
        status_value = job.status.value if hasattr(job.status, 'value') else str(job.status)
        if status_value == 'RUNNING':
            return jsonify({'success': False, 'error': 'Cannot delete a running job'}), 400

        # Delete via repository
        deleted = service.training_repo.delete(job_id)
        if deleted:
            return jsonify({'success': True, 'message': f'Training job {job_id} deleted'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to delete training job'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'message': 'Error deleting training job'}), 500

def _run_training_in_background(job_id: int):
    """Run training in a background thread to avoid blocking HTTP requests"""
    import threading
    import json
    from app.services.training_service import TrainingService
    from app.services.minion_service import MinionService
    from app.services.dataset_service import DatasetService
    from services.external_training.rag.rag_service import RAGTrainingService
    
    try:
        training_service = TrainingService()
        minion_service = MinionService()
        dataset_service = DatasetService()
        
        # Get the training job
        job = training_service.get_training_job(job_id)
        if not job:
            print(f"❌ Training job {job_id} not found in background thread")
            return
        
        # Get minion details
        minion = minion_service.get_minion_by_id(job.minion_id)
        if not minion:
            training_service.update_training_job_status(job_id, 'FAILED')
            print(f"❌ Minion {job.minion_id} not found for job {job_id}")
            return
        
        # Get datasets
        config = json.loads(job.config) if job.config else {}
        selected_datasets = config.get('selected_datasets', [])
        datasets = []
        
        for dataset_id in selected_datasets:
            dataset = dataset_service.get_dataset_data(dataset_id)
            if dataset:
                datasets.append(dataset)
        
        # Get RAG config
        rag_config = config.get('rag_config', {})
        
        # Start RAG training
        try:
            print(f"🚀 Starting RAG training for job {job_id} in background thread")
            rag_service = RAGTrainingService()
            result = rag_service.train_minion_with_rag(
                job_id=job_id,
                minion_id=job.minion_id,
                user_id=job.user_id,
                datasets=datasets,
                rag_config=rag_config,
                minion_config=minion
            )
            
            # Check if training was successful
            if result.get('success', False):
                # Update job status to COMPLETED only after successful training
                training_service.update_training_job_status(job_id, 'COMPLETED')
                print(f"✅ Training job {job_id} completed successfully")
            else:
                # Training failed
                training_service.update_training_job_status(job_id, 'FAILED')
                print(f"❌ Training job {job_id} failed: {result.get('error', 'Unknown error')}")
                return
            
            # Update history record with after metrics
            try:
                with _SessionLocal() as session:
                    # Get updated minion stats
                    updated_minion = minion_service.get_minion_by_id(job.minion_id)
                    
                    # Find the training result record - prefer the one with matching minion_id
                    training_result = session.query(TrainingResult).filter_by(
                        job_id=job_id,
                        minion_id=job.minion_id
                    ).first()
                    
                    # If not found, try without minion_id filter (backward compatibility)
                    if not training_result:
                        training_result = session.query(TrainingResult).filter_by(job_id=job_id).first()
                    
                    if training_result:
                        # Update with after metrics
                        training_result.after_metrics = {
                            'minion_stats': {
                                'level': updated_minion.get('level', 1),
                                'xp': updated_minion.get('total_training_xp', 0) + updated_minion.get('total_usage_xp', 0),
                                'rank': updated_minion.get('rank', 'Novice'),
                                'score': updated_minion.get('score', 0),
                                'capabilities': updated_minion.get('capabilities', []),
                                'parameters': updated_minion.get('parameters', {})
                            },
                            'timestamp': job.completed_at.isoformat() if job.completed_at else None
                        }
                        
                        # Use real improvements from RAG training
                        improvements = result.get('improvements', {})
                        training_result.accuracy_improvement = improvements.get('accuracy', 0)
                        training_result.speed_improvement = improvements.get('speed', 0)
                        training_result.knowledge_improvement = improvements.get('knowledge', 0)
                        training_result.overall_improvement = improvements.get('overall', 0)
                        training_result.xp_gained = result.get('xp_gained', 0)  # Real XP from training
                        
                        # Update improvements JSON with real data
                        training_result.improvements = {
                            'accuracy': f"+{training_result.accuracy_improvement:.1f}%",
                            'speed': f"+{training_result.speed_improvement:.1f}%",
                            'knowledge': f"+{training_result.knowledge_improvement:.1f}%",
                            'overall': f"+{training_result.overall_improvement:.1f}%"
                        }
                        
                        session.commit()
                        print(f"✅ History record updated for job {job_id}")
                        
            except Exception as history_error:
                print(f"⚠️ Could not update history record: {history_error}")
                
        except Exception as training_error:
            # Update job status to FAILED
            training_service.update_training_job_status(job_id, 'FAILED')
            print(f"❌ Training job {job_id} failed with error: {training_error}")
            
    except Exception as e:
        print(f"❌ Error in background training thread for job {job_id}: {e}")
        try:
            training_service = TrainingService()
            training_service.update_training_job_status(job_id, 'FAILED')
        except:
            pass


@training_bp.route('/training-jobs/<int:job_id>/start', methods=['POST'])
def start_training_job_v2(job_id):
    """Start training job - V2 PostgreSQL version (non-blocking)"""
    try:
        import threading
        # Import services
        from app.services.training_service import TrainingService
        from app.services.minion_service import MinionService
        
        training_service = TrainingService()
        
        # Get the training job
        job = training_service.get_training_job(job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': f'Training job {job_id} not found',
                'message': 'Invalid job ID'
            }), 404
        
        # Check if job is already running
        if job.status.value == 'RUNNING':
            return jsonify({
                'success': False,
                'error': 'Job is already running',
                'message': 'Cannot start a job that is already in progress'
            }), 400
        
        # Update job status to RUNNING immediately
        training_service.update_training_job_status(job_id, 'RUNNING')
        
        # Start training in a background thread (non-blocking)
        training_thread = threading.Thread(
            target=_run_training_in_background,
            args=(job_id,),
            daemon=True  # Daemon thread will terminate when main process exits
        )
        training_thread.start()
        
        print(f"✅ Training job {job_id} started in background thread")
        
        # Return immediately - training runs in background
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'RUNNING',
            'message': f'Training job "{job.job_name}" started successfully. Training is running in the background.'
        }), 200
        
    except Exception as e:
        print(f"❌ Error starting training job: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error starting training job'
        }), 500

@training_bp.route('/training-jobs/<int:job_id>/stop', methods=['POST'])
def stop_training_job_v2(job_id):
    """Stop training job - V2 PostgreSQL version"""
    try:
        return jsonify({
            'success': False,
            'message': 'Training job stop not yet implemented in V2',
            'database': 'SQLAlchemy + PostgreSQL',
            'version': '2.0.0'
        }), 501  # Not Implemented
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error stopping training job'
        }), 500

@training_bp.route('/training-jobs/<int:job_id>/status', methods=['GET'])
def get_training_job_status_v2(job_id):
    """Get training job status - V2 PostgreSQL version

    Returns a lightweight status object with: success, running(boolean), status, progress, message
    """
    try:
        from app.services.training_service import TrainingService

        service = TrainingService()
        job = service.get_training_job(job_id)

        if not job:
            return jsonify({
                'success': False,
                'message': f'Training job {job_id} not found'
            }), 404

        # Normalize fields
        status_value = job.status.value if hasattr(job.status, 'value') else str(job.status)
        progress = float(job.progress or 0.0)

        return jsonify({
            'success': True,
            'running': status_value == 'RUNNING',
            'status': status_value,
            'progress': progress,
            'message': job.error_message or ''
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error fetching training job status'
        }), 500


@training_bp.route('/detect-stuck-training', methods=['POST'])
def detect_stuck_training_v2():
    """Lightweight endpoint to detect stuck training jobs.

    Returns zero stuck jobs by default. Frontend polls this endpoint; providing
    a stable 200 response avoids 404 noise while a full detector is implemented.
    """
    try:
        # Placeholder implementation: no stuck jobs detected
        return jsonify({
            'success': True,
            'stuck_jobs_found': 0,
            'stuck_jobs': []
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/minions/<int:minion_id>/training-history', methods=['GET'])
def get_minion_training_history(minion_id):
    """Get training history for a specific minion (deduplicated and accurate)"""
    try:
        with _SessionLocal() as session:
            # Get all training results for this minion, ordered by creation date
            all_results = session.query(TrainingResult).filter_by(minion_id=minion_id).order_by(TrainingResult.created_at.desc()).all()
            
            # Deduplicate by job_id - keep only the most recent/complete record per job
            # Use a dict to track the best result for each job_id
            best_results = {}
            
            for result in all_results:
                job_id = result.job_id
                
                # If no job_id, use result.id as key (orphaned records)
                if not job_id:
                    key = f"orphan_{result.id}"
                    if key not in best_results:
                        best_results[key] = result
                    continue
                
                # For records with job_id, prefer:
                # 1. Records with after_metrics (completed training)
                # 2. Most recent record if both have or don't have after_metrics
                if job_id not in best_results:
                    best_results[job_id] = result
                else:
                    existing = best_results[job_id]
                    
                    # Prefer record with after_metrics (completed training)
                    existing_has_after = existing.after_metrics is not None and existing.after_metrics != {}
                    current_has_after = result.after_metrics is not None and result.after_metrics != {}
                    
                    if current_has_after and not existing_has_after:
                        best_results[job_id] = result  # Current has after_metrics, existing doesn't
                    elif not current_has_after and existing_has_after:
                        pass  # Keep existing (has after_metrics)
                    elif result.created_at and existing.created_at:
                        # Both have or don't have after_metrics, prefer most recent
                        if result.created_at > existing.created_at:
                            best_results[job_id] = result
            
            # Build history data from deduplicated results
            history_data = []
            for result in best_results.values():
                # Get job details from ExternalTrainingJob table
                job_details = None
                if result.job_id:
                    job = session.query(ExternalTrainingJob).filter_by(id=result.job_id).first()
                    if job:
                        job_details = {
                            'job_name': job.job_name,
                            'description': job.description,
                            'provider': job.provider,
                            'model_name': job.model_name,
                            'status': job.status.value if hasattr(job.status, 'value') else str(job.status),
                            'created_at': job.created_at.isoformat() if job.created_at else None,
                            'started_at': job.started_at.isoformat() if job.started_at else None,
                            'completed_at': job.completed_at.isoformat() if job.completed_at else None
                        }
                
                # Only include records that have a valid job_id (skip orphaned records)
                if result.job_id and job_details:
                    history_data.append({
                        'id': result.id,
                        'job_id': result.job_id,
                        'job_details': job_details,
                        'training_type': result.training_type,
                        'collection_name': result.collection_name,
                        'before_metrics': result.before_metrics,
                        'after_metrics': result.after_metrics,
                        'improvements': result.improvements,
                        'accuracy_improvement': result.accuracy_improvement or 0.0,
                        'speed_improvement': result.speed_improvement or 0.0,
                        'knowledge_improvement': result.knowledge_improvement or 0.0,
                        'overall_improvement': result.overall_improvement or 0.0,
                        'xp_gained': result.xp_gained or 0,
                        'level_up': result.level_up or False,
                        'rank_up': result.rank_up or False,
                        'created_at': result.created_at.isoformat() if result.created_at else None,
                        'rag_config': result.rag_config,
                        'minion_config': result.minion_config,
                        'summary': result.get_summary() if hasattr(result, 'get_summary') else None
                    })
            
            # Sort by job creation date (most recent first)
            history_data.sort(key=lambda x: x['job_details']['created_at'] if x['job_details'] and x['job_details'].get('created_at') else '', reverse=True)
            
            return jsonify({
                'success': True,
                'minion_id': minion_id,
                'training_history': history_data,
                'total_training_sessions': len(history_data)
            }), 200
            
    except Exception as e:
        print(f"❌ Error fetching training history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error fetching training history'
        }), 500
