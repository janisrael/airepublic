from flask import Blueprint, jsonify, request
from app.services.minion_service import MinionService
from app.services.score_calculator import ScoreCalculator

minion_update_bp = Blueprint('minion_update_bp', __name__, url_prefix='/api/v2/users')
minion_service = MinionService()
score_calculator = ScoreCalculator()

@minion_update_bp.route('/<int:user_id>/minions/<int:minion_id>', methods=['PUT'])
def update_minion(user_id, minion_id):
    """Update minion basic information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Validate required fields
        required_fields = []
        optional_fields = ['display_name', 'title', 'description', 'temperature', 'max_tokens', 'top_p', 'system_prompt']
        
        # Check if at least one field is provided
        if not any(field in data for field in optional_fields):
            return jsonify({
                'success': False,
                'error': 'At least one field must be provided for update'
            }), 400

        # Update minion
        result = minion_service.update_minion(minion_id, data)
        
        if result['success']:
            # Recalculate score after update
            score_result = score_calculator.update_minion_score(minion_id)
            
            return jsonify({
                'success': True,
                'message': 'Minion updated successfully',
                'minion_id': minion_id,
                'updated_fields': list(data.keys()),
                'score_updated': score_result['success']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400

    except Exception as e:
        print(f"Error updating minion: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update minion'
        }), 500

@minion_update_bp.route('/<int:user_id>/minions/<int:minion_id>/traits', methods=['PUT'])
def update_minion_traits(user_id, minion_id):
    """Update minion traits"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Update traits
        result = minion_service.update_minion_traits(minion_id, data)
        
        if result['success']:
            # Recalculate score after traits update
            score_result = score_calculator.update_minion_score(minion_id)
            
            return jsonify({
                'success': True,
                'message': 'Minion traits updated successfully',
                'minion_id': minion_id,
                'score_updated': score_result['success']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400

    except Exception as e:
        print(f"Error updating minion traits: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update minion traits'
        }), 500
