"""
Score Calculator Service for Minion Ranking System
Calculates and updates minion scores based on XP, rank, and technical specs
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database.postgres_connection import create_spirit_engine
from model.minion import ExternalAPIModel
from .xp_calculator import XPCalculator
import json

class ScoreCalculator:
    """Handles score calculation and updates for minions"""
    
    def __init__(self):
        self.engine = create_spirit_engine()
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=self.engine)
        self.Session = SessionLocal
    
    def calculate_minion_score(self, minion_id: int) -> Dict[str, Any]:
        """
        Calculate complete score for a minion based on current data
        
        Args:
            minion_id: The minion ID to calculate score for
            
        Returns:
            Dict with score breakdown and total
        """
        with self.Session() as session:
            try:
                minion = session.query(ExternalAPIModel).filter(
                    ExternalAPIModel.id == minion_id
                ).first()
                
                if not minion:
                    return {'success': False, 'error': 'Minion not found'}
                
                # Calculate XP and level progression
                total_xp = (minion.total_usage_xp or 0) + (minion.total_training_xp or 0)
                xp_progress = XPCalculator.get_xp_progress(total_xp)
                
                # Parse parameters from model_stats or parameters
                params = self._parse_parameters(minion)
                
                # Parse capabilities
                capabilities = self._parse_capabilities(minion)
                
                # Calculate score components
                score_breakdown = self._calculate_score_components(
                    xp_progress, params, minion.context_length, capabilities, minion.model_type
                )
                
                return {
                    'success': True,
                    'minion_id': minion_id,
                    'total_score': score_breakdown['total'],
                    'breakdown': score_breakdown,
                    'xp_progress': xp_progress
                }
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def update_minion_score(self, minion_id: int) -> Dict[str, Any]:
        """
        Calculate and update minion score in database
        
        Args:
            minion_id: The minion ID to update
            
        Returns:
            Dict with success status and score info
        """
        with self.Session() as session:
            try:
                minion = session.query(ExternalAPIModel).filter(
                    ExternalAPIModel.id == minion_id
                ).first()
                
                if not minion:
                    return {'success': False, 'error': 'Minion not found'}
                
                # Calculate new score
                score_result = self.calculate_minion_score(minion_id)
                if not score_result['success']:
                    return score_result
                
                # Update minion with new score
                minion.score = score_result['total_score']
                minion.score_breakdown = json.dumps(score_result['breakdown'])
                
                session.commit()
                
                return {
                    'success': True,
                    'minion_id': minion_id,
                    'old_score': getattr(minion, 'score', 0),
                    'new_score': score_result['total_score'],
                    'breakdown': score_result['breakdown']
                }
                
            except Exception as e:
                session.rollback()
                return {'success': False, 'error': str(e)}
    
    def add_xp_and_update_score(self, minion_id: int, xp_points: int, xp_type: str) -> Dict[str, Any]:
        """
        Add XP points to minion and recalculate score
        
        Args:
            minion_id: The minion ID
            xp_points: Points to add
            xp_type: Type of XP ('training' or 'usage')
            
        Returns:
            Dict with success status and updated info
        """
        with self.Session() as session:
            try:
                minion = session.query(ExternalAPIModel).filter(
                    ExternalAPIModel.id == minion_id
                ).first()
                
                if not minion:
                    return {'success': False, 'error': 'Minion not found'}
                
                # Add XP based on type
                if xp_type == 'training':
                    minion.total_training_xp = (minion.total_training_xp or 0) + xp_points
                elif xp_type == 'usage':
                    minion.total_usage_xp = (minion.total_usage_xp or 0) + xp_points
                else:
                    return {'success': False, 'error': 'Invalid XP type. Use "training" or "usage"'}
                
                # Recalculate level and rank
                total_xp = (minion.total_usage_xp or 0) + (minion.total_training_xp or 0)
                xp_progress = XPCalculator.get_xp_progress(total_xp)
                
                # Update level and rank
                minion.level = xp_progress['current_level']
                minion.rank = xp_progress['rank_name'].lower()
                minion.rank_level = xp_progress['rank_level']
                
                # Recalculate and update score
                score_result = self.calculate_minion_score(minion_id)
                if score_result['success']:
                    minion.score = score_result['total_score']
                    minion.score_breakdown = json.dumps(score_result['breakdown'])
                
                session.commit()
                
                return {
                    'success': True,
                    'minion_id': minion_id,
                    'xp_added': xp_points,
                    'xp_type': xp_type,
                    'new_total_xp': total_xp,
                    'new_level': xp_progress['current_level'],
                    'new_rank': xp_progress['rank_name'],
                    'new_score': score_result['total_score'],
                    'level_up': xp_progress['current_level'] > (minion.level or 1),
                    'rank_up': xp_progress['rank_name'].lower() != (minion.rank or 'novice')
                }
                
            except Exception as e:
                session.rollback()
                return {'success': False, 'error': str(e)}
    
    def _calculate_score_components(self, xp_progress: Dict, params: float, context_length: int, 
                                  capabilities: list, architecture: str) -> Dict[str, Any]:
        """Calculate individual score components"""
        
        # XP and Level Score (0-50 points) - Primary scoring factor
        level = xp_progress['current_level']
        experience = xp_progress['total_xp']
        xp_score = min(level * 5 + (experience / 100), 50)
        
        # Rank Bonus (0-25 points) - Based on rank progression
        rank = xp_progress['rank_name'].lower()
        rank_bonuses = {
            'novice': 0,
            'skilled': 10,
            'specialist': 15,
            'expert': 20,
            'master': 22,
            'grandmaster': 24,
            'autonomous': 25
        }
        rank_score = rank_bonuses.get(rank, 0)
        
        # Parameter score (0-15 points) - Technical capability
        param_score = min(params * 0.5, 15)
        
        # Context length score (0-10 points) - Technical capability
        context_score = min(context_length / 20000, 10)
        
        # Capabilities score (0-10 points) - Functional capability
        cap_score = min(len(capabilities) * 2, 10)
        
        # Architecture bonus (0-5 points) - Minor technical bonus
        arch_lower = (architecture or '').lower()
        arch_score = 1
        if 'llama' in arch_lower:
            arch_score = 5
        elif 'gemma' in arch_lower:
            arch_score = 4
        elif 'mistral' in arch_lower:
            arch_score = 3
        elif 'qwen' in arch_lower:
            arch_score = 2
        
        total_score = round(xp_score + rank_score + param_score + context_score + cap_score + arch_score)
        
        return {
            'xp_score': round(xp_score, 1),
            'rank_score': rank_score,
            'param_score': round(param_score, 1),
            'context_score': round(context_score, 1),
            'cap_score': cap_score,
            'arch_score': arch_score,
            'total': total_score
        }
    
    def _parse_parameters(self, minion: ExternalAPIModel) -> float:
        """Parse parameters from minion data"""
        # Try to get from model_stats first
        try:
            if minion.model_metadata:
                metadata = json.loads(minion.model_metadata)
                model_stats = metadata.get('model_stats', {})
                params = model_stats.get('parameters', {})
                if isinstance(params, dict) and 'size' in params:
                    size_str = params['size']
                    if 'B' in size_str:
                        return float(size_str.replace('B', ''))
        except:
            pass
        
        # Try to get from parameters field
        try:
            if minion.parameters:
                params = json.loads(minion.parameters) if isinstance(minion.parameters, str) else minion.parameters
                if isinstance(params, dict) and 'size' in params:
                    size_str = params['size']
                    if 'B' in size_str:
                        return float(size_str.replace('B', ''))
        except:
            pass
        
        return 0
    
    def _parse_capabilities(self, minion: ExternalAPIModel) -> list:
        """Parse capabilities from minion data"""
        try:
            if minion.capabilities:
                return json.loads(minion.capabilities) if isinstance(minion.capabilities, str) else minion.capabilities
        except:
            pass
        return []
    
    def get_all_minion_scores(self) -> Dict[str, Any]:
        """Get scores for all minions"""
        with self.Session() as session:
            try:
                minions = session.query(ExternalAPIModel).filter(
                    ExternalAPIModel.is_active == True
                ).all()
                
                scores = []
                for minion in minions:
                    score_result = self.calculate_minion_score(minion.id)
                    if score_result['success']:
                        scores.append({
                            'minion_id': minion.id,
                            'name': minion.display_name,
                            'score': score_result['total_score'],
                            'level': score_result['xp_progress']['current_level'],
                            'rank': score_result['xp_progress']['rank_name']
                        })
                
                return {
                    'success': True,
                    'scores': sorted(scores, key=lambda x: x['score'], reverse=True),
                    'total_minions': len(scores)
                }
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
