"""
API routes for Spirit System
"""

from flask import Blueprint, request, jsonify
from app.services.spirit_service import SpiritService

# Create blueprint
spirit_bp = Blueprint('spirit', __name__, url_prefix='/api/v2/spirits')

# Initialize service
spirit_service = SpiritService()

@spirit_bp.route('/', methods=['GET'])
def get_all_spirits():
    """Get all available spirits"""
    try:
        spirits = spirit_service.get_all_spirits()
        return jsonify({
            'success': True,
            'data': spirits,
            'total': len(spirits)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/free', methods=['GET'])
def get_free_spirits():
    """Get all free spirits"""
    try:
        spirits = spirit_service.get_free_spirits()
        return jsonify({
            'success': True,
            'data': spirits,
            'total': len(spirits)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/tier/<tier>', methods=['GET'])
def get_spirits_by_tier(tier):
    """Get spirits by pricing tier"""
    try:
        spirits = spirit_service.get_spirits_by_tier(tier)
        return jsonify({
            'success': True,
            'data': spirits,
            'tier': tier,
            'total': len(spirits)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/<int:spirit_id>', methods=['GET'])
def get_spirit_by_id(spirit_id):
    """Get spirit by ID"""
    try:
        spirit = spirit_service.get_spirit_by_id(spirit_id)
        if spirit:
            return jsonify({
                'success': True,
                'data': spirit
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Spirit not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/name/<spirit_name>', methods=['GET'])
def get_spirit_by_name(spirit_name):
    """Get spirit by name"""
    try:
        spirit = spirit_service.get_spirit_by_name(spirit_name)
        if spirit:
            return jsonify({
                'success': True,
                'data': spirit
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Spirit not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/available', methods=['GET'])
def get_spirits_for_user():
    """Get spirits available for user's rank and level"""
    try:
        user_rank = request.args.get('rank', 'Novice')
        user_level = int(request.args.get('level', 1))
        
        spirits = spirit_service.get_spirits_for_user_rank(user_rank, user_level)
        return jsonify({
            'success': True,
            'data': spirits,
            'user_rank': user_rank,
            'user_level': user_level,
            'total': len(spirits)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/synergy', methods=['POST'])
def calculate_spirit_synergy():
    """Calculate synergy bonuses for spirit combination"""
    try:
        data = request.get_json()
        spirit_ids = data.get('spirit_ids', [])
        
        if not spirit_ids:
            return jsonify({
                'success': False,
                'error': 'spirit_ids is required'
            }), 400
        
        synergy_data = spirit_service.calculate_spirit_synergy(spirit_ids)
        return jsonify({
            'success': True,
            'data': synergy_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/bundles', methods=['GET'])
def get_spirit_bundles():
    """Get all spirit bundles"""
    try:
        bundles = spirit_service.get_spirit_bundles()
        return jsonify({
            'success': True,
            'data': bundles,
            'total': len(bundles)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/subscription-plans', methods=['GET'])
def get_subscription_plans():
    """Get all subscription plans"""
    try:
        plans = spirit_service.get_subscription_plans()
        return jsonify({
            'success': True,
            'data': plans,
            'total': len(plans)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/user/<int:user_id>/access', methods=['GET'])
def get_user_spirit_access(user_id):
    """Get spirits user has access to"""
    try:
        access = spirit_service.get_user_spirit_access(user_id)
        return jsonify({
            'success': True,
            'data': access,
            'user_id': user_id,
            'total': len(access)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/<int:spirit_id>/tools', methods=['GET'])
def get_spirit_tools(spirit_id):
    """Get tools available for a specific spirit"""
    try:
        tools = spirit_service.get_tools_by_spirit(spirit_id)
        return jsonify({
            'success': True,
            'data': tools,
            'spirit_id': spirit_id,
            'total': len(tools)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@spirit_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        spirits = spirit_service.get_all_spirits()
        return jsonify({
            'success': True,
            'message': 'Spirit system is healthy',
            'spirits_count': len(spirits),
            'status': 'operational'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'error'
        }), 500
