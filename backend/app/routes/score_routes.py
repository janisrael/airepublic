"""
Score Management Routes
Handles score calculation and XP updates for minions
"""

from flask import Blueprint, request, jsonify
from app.services.score_calculator import ScoreCalculator
from app.services.minion_service import MinionService

score_bp = Blueprint('score', __name__, url_prefix='/api/v2')

@score_bp.route('/minions/<int:minion_id>/score', methods=['GET'])
def get_minion_score(minion_id):
    """Get current score for a minion"""
    try:
        calculator = ScoreCalculator()
        result = calculator.calculate_minion_score(minion_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'minion_id': minion_id,
                'score': result['total_score'],
                'breakdown': result['breakdown'],
                'xp_progress': result['xp_progress']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@score_bp.route('/minions/<int:minion_id>/score', methods=['POST'])
def update_minion_score(minion_id):
    """Update minion score based on current data"""
    try:
        calculator = ScoreCalculator()
        result = calculator.update_minion_score(minion_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Score updated successfully',
                'minion_id': minion_id,
                'old_score': result['old_score'],
                'new_score': result['new_score'],
                'breakdown': result['breakdown']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@score_bp.route('/minions/<int:minion_id>/xp', methods=['POST'])
def add_minion_xp(minion_id):
    """Add XP points to minion and update score"""
    try:
        data = request.get_json()
        
        if not data or 'xp_points' not in data or 'xp_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing xp_points or xp_type in request body'
            }), 400
        
        xp_points = data['xp_points']
        xp_type = data['xp_type']
        
        if not isinstance(xp_points, (int, float)) or xp_points <= 0:
            return jsonify({
                'success': False,
                'error': 'xp_points must be a positive number'
            }), 400
        
        if xp_type not in ['training', 'usage']:
            return jsonify({
                'success': False,
                'error': 'xp_type must be "training" or "usage"'
            }), 400
        
        calculator = ScoreCalculator()
        result = calculator.add_xp_and_update_score(minion_id, int(xp_points), xp_type)
        
        if result['success']:
            response = {
                'success': True,
                'message': 'XP added and score updated successfully',
                'minion_id': minion_id,
                'xp_added': result['xp_added'],
                'xp_type': result['xp_type'],
                'new_total_xp': result['new_total_xp'],
                'new_level': result['new_level'],
                'new_rank': result['new_rank'],
                'new_score': result['new_score']
            }
            
            # Add level/rank up notifications
            if result['level_up']:
                response['level_up'] = True
                response['level_up_message'] = f"Level up! Now level {result['new_level']}"
            
            if result['rank_up']:
                response['rank_up'] = True
                response['rank_up_message'] = f"Rank up! Now {result['new_rank']}"
            
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@score_bp.route('/minions/scores', methods=['GET'])
def get_all_scores():
    """Get scores for all minions"""
    try:
        calculator = ScoreCalculator()
        result = calculator.get_all_minion_scores()
        
        if result['success']:
            return jsonify({
                'success': True,
                'scores': result['scores'],
                'total_minions': result['total_minions']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@score_bp.route('/minions/<int:minion_id>/recalculate', methods=['POST'])
def recalculate_minion(minion_id):
    """Recalculate minion XP, level, rank, and score"""
    try:
        calculator = ScoreCalculator()
        
        # First update the score to recalculate everything
        result = calculator.update_minion_score(minion_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Minion recalculated successfully',
                'minion_id': minion_id,
                'new_score': result['new_score'],
                'breakdown': result['breakdown']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
