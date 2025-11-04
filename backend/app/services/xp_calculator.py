"""
XP Calculator Service for Minion Leveling System
Based on MINION_XP_RANKING_SYSTEM_PLAN.md
"""

import math
from typing import Dict, Tuple, List

class XPCalculator:
    """Handles XP calculations and level progression for minions"""
    
    # Rank definitions (from the plan)
    RANKS = [
        {"name": "Novice", "level_range": (1, 5), "total_xp_required": 1000, "tools_unlocked": 1},
        {"name": "Skilled", "level_range": (6, 10), "total_xp_required": 5000, "tools_unlocked": 3},
        {"name": "Specialist", "level_range": (11, 15), "total_xp_required": 15000, "tools_unlocked": 5},
        {"name": "Expert", "level_range": (16, 20), "total_xp_required": 35000, "tools_unlocked": 7},
        {"name": "Master", "level_range": (21, 25), "total_xp_required": 70000, "tools_unlocked": 9},
        {"name": "Grandmaster", "level_range": (26, 30), "total_xp_required": 120000, "tools_unlocked": 11},
        {"name": "Autonomous", "level_range": (31, 35), "total_xp_required": 120000, "tools_unlocked": 12}
    ]
    
    @classmethod
    def calculate_level_from_xp(cls, total_xp: int) -> int:
        """Calculate current level based on total XP"""
        if total_xp <= 0:
            return 1
        
        # Use the formula: XP for next level = base_xp * (1.5 ^ current_level)
        # We need to reverse this to find level from XP
        level = 1
        xp_needed = 0
        
        while xp_needed <= total_xp and level <= 35:
            xp_for_next = cls.get_xp_for_level(level)
            if xp_needed + xp_for_next > total_xp:
                break
            xp_needed += xp_for_next
            level += 1
            
        return min(level, 35)
    
    @classmethod
    def get_xp_for_level(cls, level: int) -> int:
        """Get XP required to reach the next level from current level"""
        if level <= 0:
            return 100  # Base XP for level 1
        
        # Formula: base_xp * (1.5 ^ current_level)
        base_xp = 100
        return int(base_xp * (1.5 ** (level - 1)))
    
    @classmethod
    def get_rank_from_level(cls, level: int) -> Dict[str, any]:
        """Get rank information from level"""
        for rank in cls.RANKS:
            min_level, max_level = rank["level_range"]
            if min_level <= level <= max_level:
                return rank
        
        # If level exceeds max, return highest rank
        return cls.RANKS[-1]
    
    @classmethod
    def get_xp_progress(cls, total_xp: int) -> Dict[str, any]:
        """Calculate XP progress information"""
        current_level = cls.calculate_level_from_xp(total_xp)
        rank_info = cls.get_rank_from_level(current_level)
        
        # Calculate XP needed for current level
        xp_for_current_level = cls.get_total_xp_for_level(current_level)
        xp_for_next_level = cls.get_total_xp_for_level(current_level + 1)
        
        # Calculate progress within current level
        xp_in_current_level = total_xp - xp_for_current_level
        xp_needed_for_next = xp_for_next_level - xp_for_current_level
        
        progress_percentage = (xp_in_current_level / xp_needed_for_next * 100) if xp_needed_for_next > 0 else 100
        
        return {
            "current_level": current_level,
            "rank_name": rank_info["name"],
            "rank_level": current_level - rank_info["level_range"][0] + 1,
            "total_xp": total_xp,
            "xp_in_current_level": xp_in_current_level,
            "xp_needed_for_next": xp_needed_for_next,
            "progress_percentage": round(progress_percentage, 1),
            "xp_to_next_level": xp_needed_for_next - xp_in_current_level
        }
    
    @classmethod
    def get_total_xp_for_level(cls, level: int) -> int:
        """Get total XP required to reach a specific level"""
        if level <= 1:
            return 0
        
        total_xp = 0
        for lvl in range(1, level):
            total_xp += cls.get_xp_for_level(lvl)
        
        return total_xp
    
    @classmethod
    def calculate_training_xp(cls, refined_items: int, quality_score: float, validation_score: float) -> int:
        """Calculate XP from RAG training based on the plan"""
        # Dataset size XP using piecewise linear interpolation
        base_xp = cls.dataset_lines_to_xp(refined_items)
        
        # Quality bonus (10-20% of base)
        quality_bonus = int(base_xp * (quality_score / 100) * 0.2)
        
        # Validation bonus
        if validation_score == 100:
            validation_bonus = 200
        elif validation_score >= 90:
            validation_bonus = 150
        elif validation_score >= 80:
            validation_bonus = 100
        elif validation_score >= 70:
            validation_bonus = 50
        else:
            validation_bonus = 0
        
        return base_xp + quality_bonus + validation_bonus
    
    @classmethod
    def dataset_lines_to_xp(cls, lines: int) -> int:
        """Convert dataset size to XP using piecewise-linear interpolation"""
        if lines <= 0:
            return 0
        
        # Breakpoints from the plan
        breakpoints = [
            (0, 0),
            (10, 20),
            (100, 200),
            (500, 750),
            (4800, 1400),
            (20000, 2600)
        ]
        
        xs = [p[0] for p in breakpoints]
        ys = [p[1] for p in breakpoints]
        
        if lines >= xs[-1]:
            return ys[-1]
        
        # Find the right interval
        for i in range(len(xs) - 1):
            if xs[i] <= lines < xs[i + 1]:
                x0, y0 = xs[i], ys[i]
                x1, y1 = xs[i + 1], ys[i + 1]
                
                # Linear interpolation
                t = (lines - x0) / (x1 - x0)
                xp = y0 + t * (y1 - y0)
                return int(round(xp))
        
        return 0
    
    @classmethod
    def calculate_usage_xp(cls, api_calls: int, successful_rate: float = 1.0) -> int:
        """Calculate XP from API usage"""
        # Base XP per call
        base_xp_per_call = 5
        
        # Apply success rate multiplier
        total_xp = int(api_calls * base_xp_per_call * successful_rate)
        
        # Daily cap of 500 XP
        return min(total_xp, 500)
    
    @classmethod
    def get_unlocked_tools(cls, level: int) -> List[str]:
        """Get list of unlocked tools based on level"""
        tools_by_level = {
            3: ["Web Search"],
            6: ["File Operations"],
            8: ["Code Execution"],
            11: ["API Integration"],
            13: ["Database Query"],
            16: ["Image Processing"],
            18: ["Email Operations"],
            21: ["Calendar Management"],
            23: ["Advanced Analytics"],
            26: ["Multi-Agent Orchestration"],
            28: ["Self-Improvement"],
            31: ["Autonomous Decision Making"]
        }
        
        unlocked = []
        for unlock_level, tool_list in tools_by_level.items():
            if level >= unlock_level:
                unlocked.extend(tool_list)
        
        return unlocked
