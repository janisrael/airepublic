"""
API routes for Minion-Spirit Integration
"""

from flask import Blueprint, request, jsonify
from app.services.minion_spirit_integration import MinionSpiritIntegration

# Create blueprint
minion_spirit_bp = Blueprint('minion_spirit', __name__, url_prefix='/api/v2/minions')

# Initialize service
integration_service = MinionSpiritIntegration()

@minion_spirit_bp.route('/<int:minion_id>/spirits', methods=['GET'])
def get_minion_spirits(minion_id):
    """Get spirits assigned to a minion"""
    try:
        spirits = integration_service.get_minion_spirits(minion_id)
        return jsonify({
            'success': True,
            'data': spirits,
            'minion_id': minion_id,
            'total': len(spirits)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@minion_spirit_bp.route('/<int:minion_id>/spirits/available', methods=['GET'])
def get_available_spirits_for_minion(minion_id):
    """Get spirits that can be assigned to a minion"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        spirits = integration_service.get_available_spirits_for_minion(minion_id, user_id)
        return jsonify({
            'success': True,
            'data': spirits,
            'minion_id': minion_id,
            'user_id': user_id,
            'total': len(spirits)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@minion_spirit_bp.route('/<int:minion_id>/spirits', methods=['POST'])
def assign_spirit_to_minion(minion_id):
    """Assign a spirit to a minion"""
    try:
        data = request.get_json()
        spirit_id = data.get('spirit_id')
        user_id = data.get('user_id', 1)
        
        if not spirit_id:
            return jsonify({
                'success': False,
                'error': 'spirit_id is required'
            }), 400
        
        result = integration_service.assign_spirit_to_minion(minion_id, spirit_id, user_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@minion_spirit_bp.route('/<int:minion_id>/spirits/<int:spirit_id>', methods=['DELETE'])
def remove_spirit_from_minion(minion_id, spirit_id):
    """Remove a spirit from a minion"""
    try:
        result = integration_service.remove_spirit_from_minion(minion_id, spirit_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@minion_spirit_bp.route('/<int:minion_id>/spirits/synergy', methods=['GET'])
def get_minion_spirit_synergy(minion_id):
    """Get synergy calculation for minion's spirits"""
    try:
        synergy_data = integration_service.get_minion_spirit_synergy(minion_id)
        return jsonify({
            'success': True,
            'data': synergy_data,
            'minion_id': minion_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@minion_spirit_bp.route('/<int:minion_id>/spirits/health', methods=['GET'])
def health_check(minion_id):
    """Health check for minion-spirit integration"""
    try:
        spirits = integration_service.get_minion_spirits(minion_id)
        synergy = integration_service.get_minion_spirit_synergy(minion_id)
        
        return jsonify({
            'success': True,
            'message': 'Minion-spirit integration is healthy',
            'minion_id': minion_id,
            'spirits_count': len(spirits),
            'synergy_performance': synergy.get('net_performance', 0),
            'status': 'operational'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'error'
        }), 500
