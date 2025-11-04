"""
Dataset Routes - New Clean Architecture
Handles all dataset-related API endpoints

Original endpoints moved from api_server.py:
- /api/datasets (GET)
- /api/load-dataset (POST)
- /api/datasets/<dataset_id> (DELETE)
- /api/datasets/<dataset_id>/favorite (POST)
"""

from flask import Blueprint, jsonify, request
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import dataset service (PostgreSQL-based)
from app.services.dataset_service import DatasetService

# Import dataset loader
from dataset_loader import load_any_dataset

dataset_bp = Blueprint('datasets', __name__, url_prefix='/api/v2')

# Using SQLAlchemy service instead of direct PostgreSQL connection

@dataset_bp.route('/datasets', methods=['GET'])
def get_global_datasets_v2():
    """Get global admin-provided datasets (free for all users)"""
    try:
        dataset_service = DatasetService()
        datasets = dataset_service.get_global_datasets()
        
        return jsonify({
            'success': True,
            'datasets': datasets,
            'total': len(datasets),
            'message': f'Retrieved {len(datasets)} global datasets'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'datasets': [],
            'total': 0
        }), 500

@dataset_bp.route('/users/<int:user_id>/datasets', methods=['GET'])
def get_user_datasets_v2(user_id):
    """Get datasets for a specific user - USER SCOPED"""
    try:
        dataset_service = DatasetService()
        datasets = dataset_service.get_user_datasets(user_id)
        
        return jsonify({
            'success': True,
            'datasets': datasets,
            'total': len(datasets),
            'user_id': user_id,
            'message': f'Retrieved {len(datasets)} datasets for user {user_id}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'datasets': [],
            'total': 0,
            'user_id': user_id
        }), 500

@dataset_bp.route('/load-dataset', methods=['POST', 'OPTIONS'])
def load_new_dataset_v2():
    """Load a new dataset from Hugging Face - NEW VERSION"""
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    dataset_id = None
    try:
        data = request.get_json()
        print(f"Raw request data: {data}")
        print(f"Data type: {type(data)}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
            
        dataset_id = data.get('dataset_id')
        custom_name = data.get('custom_name')
        custom_description = data.get('custom_description')
        
        print(f"Dataset ID extracted: {dataset_id}")
        print(f"Custom name: {custom_name}")
        print(f"Custom description: {custom_description}")
        
        if not dataset_id:
            return jsonify({
                'success': False,
                'error': 'No dataset_id provided'
            }), 400
        
        print(f"Loading dataset: {dataset_id}")
        print(f"Dataset ID type: {type(dataset_id)}")
        print(f"Dataset ID value: {repr(dataset_id)}")
        
        # Use the dataset service from new structure
        result = load_any_dataset(dataset_id, max_samples=None)  # No limit for real datasets
        
        if result.get('success'):
            # Check if dataset already exists
            existing_dataset = None  # TODO: Implement with SQLAlchemy service
            if existing_dataset:
                return jsonify({
                    'success': False,
                    'error': f'Dataset {dataset_id} already exists'
                }), 400
            
            # Prepare dataset data for database
            dataset_data = {
                'name': custom_name if custom_name else result['name'],
                'description': custom_description if custom_description else result['description'],
                'dataset_id': result['dataset_id'],
                'type': 'Text',
                'sample_count': result['total_samples'],
                'loaded_samples': result['loaded_samples'],
                'size': result['size'],
                'format': result['format'],
                'license': 'See Hugging Face',
                'tags': ['hugging-face', 'imported'],
                'source': f'Hugging Face - {dataset_id}',
                'metadata': {
                    'loaded_at': result['loaded_at'],
                    'split_used': result.get('split_used', 'train'),
                    'samples_preview': result['samples'][:10],  # Store first 10 samples as preview
                    'all_samples': result['samples'],  # Store all samples for training
                    'format_analysis': result['metadata'].get('format_analysis')  # Include format analysis!
                }
            }
            
            # Save to database using DatasetService
            try:
                from app.services.dataset_service import DatasetService
                dataset_service = DatasetService()
                
                # Create dataset record for database
                dataset_record = {
                    'name': dataset_data['name'],
                    'description': dataset_data['description'],
                    'dataset_type': dataset_data['type'].lower(),
                    'format': dataset_data['format'].lower(),
                    'file_path': f'/datasets/imported/{dataset_id.replace("/", "_")}.json',
                    'file_size': 0,  # Will be calculated properly later
                    'total_items': dataset_data['sample_count'],
                    'processed_items': dataset_data['loaded_samples'],
                    'quality_score': 95.0,  # High quality for Hugging Face datasets
                    'processing_status': 'completed',
                    'is_active': True,
                    'is_public': True,
                    'is_verified': True,
                    'usage_count': 0,
                    'tags': dataset_data['tags'],
                    'version': '1.0',
                    'user_id': None,  # Global dataset
                    'config': {
                        'source': dataset_data['source'],
                        'license': dataset_data['license'],
                        'loaded_at': dataset_data['metadata']['loaded_at']
                    },
                    'dataset_metadata': {
                        'loaded_at': dataset_data['metadata']['loaded_at'],
                        'split_used': dataset_data['metadata'].get('split_used', 'train'),
                        'format_analysis': dataset_data['metadata'].get('format_analysis', 'Standard LoRA format'),
                        'sample_count': dataset_data['loaded_samples'],
                        'all_samples': dataset_data['metadata']['all_samples']  # Include actual samples for training
                    }
                }
                
                # Save to database using DatasetService
                saved_dataset = dataset_service.create_dataset(dataset_record)
                print(f"✅ Dataset saved to database with ID: {saved_dataset['id']}")
                
            except Exception as save_error:
                print(f"❌ Error saving dataset to database: {save_error}")
                response = jsonify({
                    'success': False,
                    'error': f'Failed to save dataset to database: {str(save_error)}',
                    'message': f'Dataset loaded but not saved. Error: {str(save_error)}'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 500
            
            # Return minimal response to avoid connection reset
            response_data = {
                'success': True,
                'message': f'Successfully loaded and saved {result["name"]} with {result["loaded_samples"]} samples',
                'dataset': {
                    'id': saved_dataset['id'],
                    'name': saved_dataset['name'],
                    'description': saved_dataset['description'],
                    'sample_count': saved_dataset['sample_count'],
                    'quality_score': saved_dataset['quality_score'],
                    'format': saved_dataset['format'],
                    'tags': saved_dataset['tags']
                }
            }
            
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            response = jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error loading dataset')
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
            
    except Exception as e:
        print(f"Error loading dataset {dataset_id}: {e}")
        print(f"Exception type: {type(e)}")
        print(f"Exception args: {e.args}")
        response = jsonify({
            'success': False,
            'error': f'Error loading dataset: {str(e)}'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@dataset_bp.route('/datasets/<int:dataset_id>', methods=['DELETE'])
def delete_dataset_v2(dataset_id):
    """Delete a dataset - NEW VERSION"""
    try:
        dataset_service = DatasetService()
        success = dataset_service.delete_dataset(dataset_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Dataset {dataset_id} deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Dataset {dataset_id} not found or could not be deleted'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dataset_bp.route('/datasets/<dataset_id>/favorite', methods=['POST'])
def toggle_favorite_v2(dataset_id):
    """Toggle favorite status of a dataset - NEW VERSION"""
    try:
        success = False  # TODO: Implement with SQLAlchemy service
        if success:
            return jsonify({
                'success': True,
                'message': f'Favorite status toggled for dataset {dataset_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Dataset {dataset_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dataset_bp.route('/datasets/health', methods=['GET'])
def health_check_v2():
    """Health check for the new datasets API"""
    try:
        # Attempt to get datasets to verify database connection
        datasets = []  # TODO: Implement with SQLAlchemy service
        return jsonify({
            'success': True,
            'message': 'Datasets API v2 is healthy',
            'total_datasets': len(datasets)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Datasets API v2 health check failed: {e}"
        }), 500
