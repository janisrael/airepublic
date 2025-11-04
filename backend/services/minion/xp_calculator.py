"""
Minion XP Calculator Service
Handles XP calculation, level progression, and rank determination for minions
"""

from bisect import bisect_right
from typing import Dict, Tuple, List
import json

# XP Breakpoints for dataset size (from ranking system docs)
DATASET_XP_BREAKPOINTS = [
    (0, 0),
    (10, 20),
    (100, 200),
    (500, 750),
    (4800, 1400),
    (20000, 2600)
]

# Rank definitions (from ranking system docs)
RANK_DEFINITIONS = [
    {"rank": 1, "name": "Novice", "title": "Apprentice", "level_range": (1, 5), "xp_required": 0},
    {"rank": 2, "name": "Skilled", "title": "Journeyman", "level_range": (6, 10), "xp_required": 1000},
    {"rank": 3, "name": "Specialist", "title": "Craftsman", "level_range": (11, 15), "xp_required": 5000},
    {"rank": 4, "name": "Expert", "title": "Strategist", "level_range": (16, 20), "xp_required": 15000},
    {"rank": 5, "name": "Master", "title": "Architect", "level_range": (21, 25), "xp_required": 35000},
    {"rank": 6, "name": "Grandmaster", "title": "Sentinel", "level_range": (26, 30), "xp_required": 70000},
    {"rank": 7, "name": "Autonomous", "title": "Sovereign", "level_range": (31, 35), "xp_required": 120000}
]

# Skillset unlock requirements (rank-based)
SKILLSET_UNLOCKS = {
    1: ["Web Search"],  # Novice
    2: ["File Operations", "Code Execution"],  # Skilled
    3: ["API Integration", "Database Query"],  # Specialist
    4: ["Image Processing", "Email Operations"],  # Expert
    5: ["Calendar Management", "Advanced Analytics"],  # Master
    6: ["Multi-Agent Orchestration", "Self-Improvement"],  # Grandmaster
    7: ["Autonomous Decision Making"]  # Autonomous
}


class XPCalculator:
    """Handles XP calculations and progression for minions"""
    
    @staticmethod
    def dataset_lines_to_xp(lines: int) -> int:
        """
        Convert dataset size to XP using piecewise-linear interpolation
        Based on the ranking system documentation
        """
        if lines <= 0:
            return 0
        
        xs = [p[0] for p in DATASET_XP_BREAKPOINTS]
        ys = [p[1] for p in DATASET_XP_BREAKPOINTS]
        
        # If beyond last breakpoint, return last XP
        if lines >= xs[-1]:
            return ys[-1]
        
        idx = bisect_right(xs, lines) - 1
        x0, y0 = xs[idx], ys[idx]
        x1, y1 = xs[idx+1], ys[idx+1]
        
        # Linear interpolation
        t = (lines - x0) / (x1 - x0)
        xp = y0 + t * (y1 - y0)
        return int(round(xp))
    
    @staticmethod
    def calculate_training_xp(refined_items: int, quality_score: float, validation_score: float, training_type: str = "rag") -> int:
        """
        Calculate total XP gained from training
        Formula: Dataset Size XP + Quality Bonus + Validation Bonus
        """
        # 1. Base XP from dataset size
        base_xp = XPCalculator.dataset_lines_to_xp(refined_items)
        
        # 2. Quality bonus (10-20% of base)
        quality_bonus = int(base_xp * (quality_score / 100) * 0.2)
        
        # 3. Validation bonus
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
        
        total_xp = base_xp + quality_bonus + validation_bonus
        
        print(f"📊 XP Calculation:")
        print(f"   Dataset Size: {refined_items} items → {base_xp} XP")
        print(f"   Quality Bonus: {quality_score}% → +{quality_bonus} XP")
        print(f"   Validation Bonus: {validation_score}% → +{validation_bonus} XP")
        print(f"   Total XP Gained: {total_xp} XP")
        
        return total_xp
    
    @staticmethod
    def calculate_usage_xp(api_calls: int, successful_rate: float = 1.0) -> int:
        """
        Calculate XP from usage (API calls, chat interactions)
        Daily cap: 500 XP
        """
        base_xp = api_calls * 5  # 5 XP per API call
        success_multiplier = successful_rate
        total_xp = int(base_xp * success_multiplier)
        
        # Apply daily cap
        return min(total_xp, 500)
    
    @staticmethod
    def calculate_level_from_xp(total_xp: int) -> Tuple[int, int, int]:
        """
        Calculate current level, rank, and rank level from total XP
        Returns: (level, rank, rank_level)
        """
        # Find current rank based on XP
        current_rank = 1
        for rank_def in RANK_DEFINITIONS:
            if total_xp >= rank_def["xp_required"]:
                current_rank = rank_def["rank"]
            else:
                break
        
        # Calculate level within rank
        rank_def = RANK_DEFINITIONS[current_rank - 1]
        rank_start_level = rank_def["level_range"][0]
        rank_end_level = rank_def["level_range"][1]
        
        # XP required for current rank
        current_rank_xp = rank_def["xp_required"]
        
        # XP required for next rank
        next_rank_xp = RANK_DEFINITIONS[current_rank]["xp_required"] if current_rank < len(RANK_DEFINITIONS) else float('inf')
        
        # Calculate level within rank (1-5 levels per rank)
        if current_rank == 7:  # Autonomous rank (no cap)
            # For autonomous rank, continue leveling beyond 35
            level = 35 + ((total_xp - current_rank_xp) // 1000)
            rank_level = min(5, ((total_xp - current_rank_xp) // 1000) % 5 + 1)
        else:
            # Calculate level based on XP progress within rank
            rank_xp_range = next_rank_xp - current_rank_xp
            xp_in_rank = total_xp - current_rank_xp
            level_progress = xp_in_rank / rank_xp_range if rank_xp_range > 0 else 0
            
            # Map to level within rank (1-5)
            rank_level = min(5, max(1, int(level_progress * 5) + 1))
            level = rank_start_level + rank_level - 1
        
        return level, current_rank, rank_level
    
    @staticmethod
    def get_rank_info(rank: int) -> Dict:
        """Get rank information by rank number"""
        if 1 <= rank <= len(RANK_DEFINITIONS):
            return RANK_DEFINITIONS[rank - 1]
        return RANK_DEFINITIONS[0]  # Default to Novice
    
    @staticmethod
    def get_next_level_xp_requirement(current_level: int, current_xp: int) -> Tuple[int, int]:
        """
        Get XP required for next level and progress percentage
        Returns: (xp_needed, progress_percentage)
        """
        level, rank, rank_level = XPCalculator.calculate_level_from_xp(current_xp)
        
        if rank == 7:  # Autonomous rank
            # Every 1000 XP = 1 level
            xp_needed = 1000 - (current_xp % 1000)
            progress = (current_xp % 1000) / 1000 * 100
        else:
            # Calculate XP needed for next level within rank
            rank_def = RANK_DEFINITIONS[rank - 1]
            next_rank_def = RANK_DEFINITIONS[rank] if rank < len(RANK_DEFINITIONS) else None
            
            if next_rank_def:
                rank_xp_range = next_rank_def["xp_required"] - rank_def["xp_required"]
                xp_per_level = rank_xp_range / 5
                xp_in_rank = current_xp - rank_def["xp_required"]
                xp_needed = int(xp_per_level - (xp_in_rank % xp_per_level))
                progress = (xp_in_rank % xp_per_level) / xp_per_level * 100
            else:
                xp_needed = 0
                progress = 100
        
        return xp_needed, progress
    
    @staticmethod
    def get_unlocked_skillsets(rank: int) -> List[str]:
        """Get list of unlocked skillsets for a given rank"""
        unlocked = []
        for r in range(1, rank + 1):
            if r in SKILLSET_UNLOCKS:
                unlocked.extend(SKILLSET_UNLOCKS[r])
        return unlocked
    
    @staticmethod
    def check_level_up(old_xp: int, new_xp: int) -> Dict:
        """
        Check if minion leveled up and return level up information
        Returns: {
            'leveled_up': bool,
            'old_level': int,
            'new_level': int,
            'old_rank': int,
            'new_rank': int,
            'ranked_up': bool,
            'unlocked_skillsets': List[str]
        }
        """
        old_level, old_rank, old_rank_level = XPCalculator.calculate_level_from_xp(old_xp)
        new_level, new_rank, new_rank_level = XPCalculator.calculate_level_from_xp(new_xp)
        
        leveled_up = new_level > old_level
        ranked_up = new_rank > old_rank
        
        # Get newly unlocked skillsets
        old_skillsets = XPCalculator.get_unlocked_skillsets(old_rank)
        new_skillsets = XPCalculator.get_unlocked_skillsets(new_rank)
        unlocked_skillsets = [s for s in new_skillsets if s not in old_skillsets]
        
        return {
            'leveled_up': leveled_up,
            'old_level': old_level,
            'new_level': new_level,
            'old_rank': old_rank,
            'new_rank': new_rank,
            'ranked_up': ranked_up,
            'unlocked_skillsets': unlocked_skillsets
        }
    
    @staticmethod
    def calculate_rank_up_bonus(new_rank: int) -> int:
        """Calculate bonus XP for ranking up"""
        rank_bonuses = {
            2: 500,   # Skilled
            3: 800,   # Specialist
            4: 1200,  # Expert
            5: 2000,  # Master
            6: 3000,  # Grandmaster
            7: 5000   # Autonomous
        }
        return rank_bonuses.get(new_rank, 0)


# Example usage and testing
if __name__ == "__main__":
    # Test with today's training data
    print("🧪 Testing XP Calculator with Grafana's training:")
    print("=" * 50)
    
    # Today's training: 4,800 items, 99% quality, 100% validation
    xp_gained = XPCalculator.calculate_training_xp(4800, 99, 100)
    print(f"\n📈 XP Gained: {xp_gained}")
    
    # Calculate new level/rank
    old_xp = 0
    new_xp = xp_gained
    level, rank, rank_level = XPCalculator.calculate_level_from_xp(new_xp)
    rank_info = XPCalculator.get_rank_info(rank)
    
    print(f"\n🎯 New Stats:")
    print(f"   Level: {level}")
    print(f"   Rank: {rank} ({rank_info['name']} - {rank_info['title']})")
    print(f"   Rank Level: {rank_level}/5")
    print(f"   Total XP: {new_xp}")
    
    # Check for level up
    level_up_info = XPCalculator.check_level_up(old_xp, new_xp)
    print(f"\n🎉 Level Up Info:")
    print(f"   Leveled Up: {level_up_info['leveled_up']}")
    print(f"   Ranked Up: {level_up_info['ranked_up']}")
    print(f"   Unlocked Skillsets: {level_up_info['unlocked_skillsets']}")
    
    # Next level requirements
    xp_needed, progress = XPCalculator.get_next_level_xp_requirement(level, new_xp)
    print(f"\n📊 Next Level:")
    print(f"   XP Needed: {xp_needed}")
    print(f"   Progress: {progress:.1f}%")
