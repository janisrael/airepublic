"""
Microservice Management Routes
Handles communication with Spirit Orchestrator microservice
"""

from flask import Blueprint, jsonify, request
import asyncio
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.spirit_orchestrator_client import spirit_orchestrator_client

microservice_bp = Blueprint('microservice', __name__, url_prefix='/api/v2')


@microservice_bp.route('/microservice/spirit-orchestrator/health', methods=['GET'])
def check_spirit_orchestrator_health():
    """Check Spirit Orchestrator microservice health"""
    try:
        health_check = asyncio.run(spirit_orchestrator_client.health_check())
        
        return jsonify({
            'success': True,
            'microservice': 'spirit-orchestrator',
            'status': health_check.get('status', 'unknown'),
            'data': health_check.get('data', {}),
            'response_time': health_check.get('response_time', 0.0)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'microservice': 'spirit-orchestrator',
            'status': 'unreachable',
            'error': str(e)
        }), 500


@microservice_bp.route('/microservice/spirit-orchestrator/minions/<minion_id>/status', methods=['GET'])
def get_minion_orchestration_status(minion_id):
    """Get minion orchestration status from microservice"""
    try:
        result = asyncio.run(spirit_orchestrator_client.get_minion_status(minion_id))
        
        if result["success"]:
            return jsonify({
                'success': True,
                'minion_id': minion_id,
                'data': result["data"]
            })
        else:
            return jsonify({
                'success': False,
                'minion_id': minion_id,
                'error': result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'minion_id': minion_id,
            'error': str(e)
        }), 500


@microservice_bp.route('/microservice/spirit-orchestrator/minions/<minion_id>/spirits', methods=['GET'])
def get_minion_spirits_from_microservice(minion_id):
    """Get minion spirits from microservice"""
    try:
        result = asyncio.run(spirit_orchestrator_client.get_minion_spirits(minion_id))
        
        if result["success"]:
            return jsonify({
                'success': True,
                'minion_id': minion_id,
                'data': result["data"]
            })
        else:
            return jsonify({
                'success': False,
                'minion_id': minion_id,
                'error': result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'minion_id': minion_id,
            'error': str(e)
        }), 500


@microservice_bp.route('/microservice/spirit-orchestrator/minions/<minion_id>/test', methods=['POST'])
def test_minion_orchestration(minion_id):
    """Test minion orchestration via microservice"""
    try:
        result = asyncio.run(spirit_orchestrator_client.test_minion_orchestration(minion_id))
        
        if result["success"]:
            return jsonify({
                'success': True,
                'minion_id': minion_id,
                'data': result["data"]
            })
        else:
            return jsonify({
                'success': False,
                'minion_id': minion_id,
                'error': result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'minion_id': minion_id,
            'error': str(e)
        }), 500


@microservice_bp.route('/microservice/spirit-orchestrator/providers', methods=['GET'])
def get_microservice_llm_providers():
    """Get LLM providers from microservice"""
    try:
        result = asyncio.run(spirit_orchestrator_client.get_llm_providers())
        
        if result["success"]:
            return jsonify({
                'success': True,
                'data': result["data"]
            })
        else:
            return jsonify({
                'success': False,
                'error': result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microservice_bp.route('/microservice/spirit-orchestrator/chat', methods=['POST'])
def chat_with_microservice():
    """Chat with minion via Spirit Orchestrator microservice"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['minion_id', 'user_input', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        result = asyncio.run(spirit_orchestrator_client.chat_with_spirits(
            minion_id=data['minion_id'],
            user_input=data['user_input'],
            user_id=data['user_id'],
            model=data.get('model'),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens')
        ))
        
        if result["success"]:
            return jsonify({
                'success': True,
                'data': result["data"]
            })
        else:
            return jsonify({
                'success': False,
                'error': result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microservice_bp.route('/microservice/spirit-orchestrator/info', methods=['GET'])
def get_microservice_info():
    """Get microservice information and configuration"""
    try:
        # Get health status
        health_check = asyncio.run(spirit_orchestrator_client.health_check())
        
        # Get providers
        providers_result = asyncio.run(spirit_orchestrator_client.get_llm_providers())
        
        return jsonify({
            'success': True,
            'microservice': {
                'name': 'Spirit Orchestrator',
                'version': '1.0.0',
                'base_url': spirit_orchestrator_client.base_url,
                'status': health_check.get('status', 'unknown'),
                'health_data': health_check.get('data', {}),
                'providers': providers_result.get('data', {}).get('providers', []) if providers_result['success'] else []
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
