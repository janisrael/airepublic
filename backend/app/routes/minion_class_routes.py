"""
Minion Class Routes - API endpoints for minion class management
Extends existing route structure without modifying working code
"""

from flask import Blueprint, request, jsonify
from app.services.minion_class_service import MinionClassService
from app.repositories.minion_class_repository import MinionClassRepository
from typing import Dict, Any
import logging

# Create blueprint for minion class routes
minion_class_bp = Blueprint('minion_class', __name__, url_prefix='/api/v2')

# Initialize services
minion_class_service = MinionClassService()
minion_class_repo = MinionClassRepository()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@minion_class_bp.route('/classes', methods=['GET'])
def get_available_classes():
    """Get all available classes for the user"""
    try:
        # Get user rank and level from query parameters or headers
        user_rank = request.args.get('user_rank', 'Novice')
        user_level = int(request.args.get('user_level', 1))
        
        # Get available classes based on user's rank and level
        available_classes = minion_class_service.get_available_classes(user_rank, user_level)
        
        # Format response
        classes_data = []
        for class_def in available_classes:
            classes_data.append({
                "class_name": class_def.class_name,
                "display_name": class_def.class_name.replace('_', ' ').title(),
                "description": class_def.class_description,
                "icon": class_def.icon,
                "category": class_def.category,
                "unlock_rank": class_def.unlock_rank,
                "unlock_level": class_def.unlock_level,
                "base_spirits": class_def.base_spirits,
                "spirit_synergies": class_def.spirit_synergies,
                "spirit_conflicts": class_def.spirit_conflicts,
                "net_performance_bonus": class_def.net_performance_bonus,
                "specialization": class_def.specialization,
                "perfect_for": class_def.perfect_for,
                "tools_count": class_def.tools_count,
                "can_unlock": True  # Already filtered by available_classes
            })
        
        return jsonify({
            "success": True,
            "classes": classes_data,
            "total_classes": len(classes_data),
            "user_rank": user_rank,
            "user_level": user_level
        })
        
    except Exception as e:
        logger.error(f"Error getting available classes: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@minion_class_bp.route('/classes/<class_name>', methods=['GET'])
def get_class_details(class_name: str):
    """Get detailed information about a specific class"""
    try:
        # Get class definition
        class_def = minion_class_service.get_class_by_name(class_name)
        if not class_def:
            return jsonify({
                "success": False,
                "error": f"Class '{class_name}' not found"
            }), 404
        
        # Get detailed spirit information
        spirit_details = minion_class_service.get_class_spirit_details(class_name)
        
        # Format response
        class_data = {
            "class_name": class_def.class_name,
            "display_name": class_def.class_name.replace('_', ' ').title(),
            "description": class_def.class_description,
            "icon": class_def.icon,
            "category": class_def.category,
            "unlock_rank": class_def.unlock_rank,
            "unlock_level": class_def.unlock_level,
            "base_spirits": class_def.base_spirits,
            "spirit_details": spirit_details,
            "spirit_synergies": class_def.spirit_synergies,
            "spirit_conflicts": class_def.spirit_conflicts,
            "net_performance_bonus": class_def.net_performance_bonus,
            "specialization": class_def.specialization,
            "perfect_for": class_def.perfect_for,
            "tools_count": class_def.tools_count,
            "is_active": class_def.is_active
        }
        
        return jsonify({
            "success": True,
            "class": class_data
        })
        
    except Exception as e:
        logger.error(f"Error getting class details for {class_name}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@minion_class_bp.route('/classes/<class_name>/unlock', methods=['POST'])
def check_class_unlock(class_name: str):
    """Check if user can unlock a specific class"""
    try:
        data = request.get_json()
        user_rank = data.get('user_rank', 'Novice')
        user_level = int(data.get('user_level', 1))
        
        # Check if user can unlock the class
        can_unlock, message = minion_class_service.can_unlock_class(class_name, user_rank, user_level)
        
        # Get class definition for additional info
        class_def = minion_class_service.get_class_by_name(class_name)
        
        return jsonify({
            "success": True,
            "can_unlock": can_unlock,
            "message": message,
            "class_name": class_name,
            "required_rank": class_def.unlock_rank if class_def else "Unknown",
            "required_level": class_def.unlock_level if class_def else 0,
            "user_rank": user_rank,
            "user_level": user_level
        })
        
    except Exception as e:
        logger.error(f"Error checking class unlock for {class_name}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@minion_class_bp.route('/minions/<int:minion_id>/class', methods=['POST'])
def assign_class_to_minion(minion_id: int):
    """Assign a class to a minion"""
    try:
        data = request.get_json()
        class_name = data.get('class_name')
        user_id = data.get('user_id')
        
        if not class_name:
            return jsonify({
                "success": False,
                "error": "class_name is required"
            }), 400
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400
        
        # Assign class to minion
        result = minion_class_service.assign_class_to_minion(minion_id, class_name, user_id)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": f"Class '{class_name}' assigned to minion successfully",
                "assignment": result
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
    except Exception as e:
        logger.error(f"Error assigning class to minion {minion_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@minion_class_bp.route('/minions/<int:minion_id>/class', methods=['GET'])
def get_minion_class(minion_id: int):
    """Get the class assigned to a minion"""
    try:
        # Get minion's assigned class
        class_def = minion_class_service.get_minion_class(minion_id)
        
        if not class_def:
            return jsonify({
                "success": True,
                "has_class": False,
                "message": "No class assigned to this minion"
            })
        
        # Get minion's spirits
        minion_spirits = minion_class_service.get_minion_spirits(minion_id)
        
        # Format response
        class_data = {
            "class_name": class_def.class_name,
            "display_name": class_def.class_name.replace('_', ' ').title(),
            "description": class_def.class_description,
            "icon": class_def.icon,
            "category": class_def.category,
            "specialization": class_def.specialization,
            "net_performance_bonus": class_def.net_performance_bonus,
            "spirit_synergies": class_def.spirit_synergies,
            "spirit_conflicts": class_def.spirit_conflicts,
            "tools_count": class_def.tools_count,
            "assigned_spirits": minion_spirits
        }
        
        return jsonify({
            "success": True,
            "has_class": True,
            "class": class_data
        })
        
    except Exception as e:
        logger.error(f"Error getting minion class for {minion_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@minion_class_bp.route('/minions/<int:minion_id>/spirits', methods=['GET'])
def get_minion_spirits(minion_id: int):
    """Get all spirits assigned to a minion"""
    try:
        # Get minion's spirits
        minion_spirits = minion_class_service.get_minion_spirits(minion_id)
        
        return jsonify({
            "success": True,
            "spirits": minion_spirits,
            "total_spirits": len(minion_spirits)
        })
        
    except Exception as e:
        logger.error(f"Error getting minion spirits for {minion_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@minion_class_bp.route('/classes/categories', methods=['GET'])
def get_class_categories():
    """Get all class categories"""
    try:
        # Get all classes and group by category
        all_classes = minion_class_service.get_all_classes()
        
        categories = {}
        for class_def in all_classes:
            if class_def.category not in categories:
                categories[class_def.category] = []
            
            categories[class_def.category].append({
                "class_name": class_def.class_name,
                "display_name": class_def.class_name.replace('_', ' ').title(),
                "description": class_def.class_description,
                "icon": class_def.icon,
                "unlock_rank": class_def.unlock_rank,
                "unlock_level": class_def.unlock_level,
                "net_performance_bonus": class_def.net_performance_bonus,
                "specialization": class_def.specialization
            })
        
        return jsonify({
            "success": True,
            "categories": categories,
            "total_categories": len(categories)
        })
        
    except Exception as e:
        logger.error(f"Error getting class categories: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@minion_class_bp.route('/classes/statistics', methods=['GET'])
def get_class_statistics():
    """Get statistics about class usage"""
    try:
        # Get class statistics
        stats = minion_class_repo.get_class_statistics()
        
        return jsonify({
            "success": True,
            "statistics": stats
        })
        
    except Exception as e:
        logger.error(f"Error getting class statistics: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@minion_class_bp.route('/classes/<class_name>/spirits', methods=['GET'])
def get_class_spirits(class_name: str):
    """Get detailed information about spirits in a class"""
    try:
        # Get class spirit details
        spirit_details = minion_class_service.get_class_spirit_details(class_name)
        
        if not spirit_details:
            return jsonify({
                "success": False,
                "error": f"Class '{class_name}' not found or has no spirits"
            }), 404
        
        return jsonify({
            "success": True,
            "class_name": class_name,
            "spirits": spirit_details,
            "total_spirits": len(spirit_details)
        })
        
    except Exception as e:
        logger.error(f"Error getting class spirits for {class_name}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Error handlers
@minion_class_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@minion_class_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500
