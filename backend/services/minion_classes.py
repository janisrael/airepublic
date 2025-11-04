"""
Minion Classes System - Pre-configured Spirit Pathways
Defines different minion classes with optimized spirit combinations
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class MinionClass:
    """Represents a minion class with pre-configured spirits"""
    name: str
    display_name: str
    description: str
    icon: str
    category: str
    unlock_rank: int  # Rank number (1=Novice, 2=Skilled, etc.)
    unlock_level: int
    default_spirits: List[str]  # Spirit names
    spirit_synergies: Dict[str, float]  # Synergy bonuses
    spirit_conflicts: Dict[str, float]  # Conflict penalties
    net_performance_bonus: float
    specialization: str
    perfect_for: List[str]
    tools_count: int

class MinionClassRegistry:
    """Registry of all available minion classes"""
    
    def __init__(self):
        self.classes = self._initialize_classes()
    
    def _initialize_classes(self) -> Dict[str, MinionClass]:
        """Initialize all minion classes"""
        return {
            # 💻 DEVELOPMENT & TECHNICAL CLASSES
            "planner": MinionClass(
                name="planner",
                display_name="Planner",
                description="Strategic planning specialist focused on breaking down complex challenges and delivering actionable solutions",
                icon="🧠",
                category="Development & Technical",
                unlock_rank=1,  # Novice rank
                unlock_level=1,
                default_spirits=["analyst", "writer", "researcher"],
                spirit_synergies={"analyst_researcher": 0.30, "writer_analyst": 0.15},
                spirit_conflicts={},
                net_performance_bonus=0.45,
                specialization="Strategic planning and problem-solving",
                perfect_for=["Project planning", "Strategic analysis", "Research projects"],
                tools_count=15
            ),
            
            "developer": MinionClass(
                name="developer",
                display_name="Developer",
                description="Full-stack development specialist with security focus and code quality assurance",
                icon="💻",
                category="Development & Technical", 
                unlock_rank="Novice",
                unlock_level=1,
                default_spirits=["builder", "debugger", "checker"],
                spirit_synergies={"builder_debugger": 0.20, "debugger_checker": 0.20},
                spirit_conflicts={},
                net_performance_bonus=0.40,
                specialization="Full-stack development with security focus",
                perfect_for=["Software development", "Code generation", "Debugging"],
                tools_count=18
            ),
            
            "devops": MinionClass(
                name="devops",
                display_name="DevOps Engineer",
                description="Infrastructure automation and monitoring specialist",
                icon="⚙️",
                category="Development & Technical",
                unlock_rank="Skilled",
                unlock_level=3,
                default_spirits=["devops", "builder", "analyst"],
                spirit_synergies={"devops_builder": 0.25, "devops_analyst": 0.25},
                spirit_conflicts={},
                net_performance_bonus=0.50,
                specialization="Infrastructure automation and monitoring",
                perfect_for=["CI/CD", "Infrastructure management", "System administration"],
                tools_count=16
            ),
            
            # 📝 CONTENT & CREATIVE CLASSES
            "creative": MinionClass(
                name="creative",
                display_name="Creative Assistant",
                description="Content creation and storytelling specialist with artistic capabilities",
                icon="🎨",
                category="Content & Creative",
                unlock_rank="Novice",
                unlock_level=1,
                default_spirits=["writer", "creative", "designer"],
                spirit_synergies={"writer_creative": 0.25, "creative_designer": 0.30},
                spirit_conflicts={},
                net_performance_bonus=0.55,
                specialization="Content creation and artistic design",
                perfect_for=["Content marketing", "Creative writing", "Visual design"],
                tools_count=14
            ),
            
            "content_marketer": MinionClass(
                name="content_marketer",
                display_name="Content Marketer",
                description="SEO optimization and content strategy specialist",
                icon="📈",
                category="Content & Creative",
                unlock_rank="Skilled",
                unlock_level=2,
                default_spirits=["researcher", "writer", "analyst"],
                spirit_synergies={"researcher_analyst": 0.30, "writer_analyst": 0.15},
                spirit_conflicts={},
                net_performance_bonus=0.45,
                specialization="SEO optimization and content strategy",
                perfect_for=["Digital marketing", "SEO", "Content optimization"],
                tools_count=16
            ),
            
            # 📊 DATA & ANALYSIS CLASSES
            "data_scientist": MinionClass(
                name="data_scientist",
                display_name="Data Scientist",
                description="Advanced data analysis and machine learning specialist",
                icon="📊",
                category="Data & Analysis",
                unlock_rank="Skilled",
                unlock_level=3,
                default_spirits=["mathematician", "analyst", "researcher"],
                spirit_synergies={"mathematician_analyst": 0.35, "analyst_researcher": 0.30},
                spirit_conflicts={},
                net_performance_bonus=0.65,
                specialization="Advanced data analysis and machine learning",
                perfect_for=["Machine learning", "Statistical analysis", "Data engineering"],
                tools_count=20
            ),
            
            "research_analyst": MinionClass(
                name="research_analyst",
                display_name="Research Analyst",
                description="Business intelligence and research specialist",
                icon="🔍",
                category="Data & Analysis",
                unlock_rank="Novice",
                unlock_level=2,
                default_spirits=["researcher", "analyst", "checker"],
                spirit_synergies={"researcher_analyst": 0.30, "analyst_checker": 0.20},
                spirit_conflicts={},
                net_performance_bonus=0.50,
                specialization="Business intelligence and research",
                perfect_for=["Business intelligence", "Research", "Data analysis"],
                tools_count=15
            ),
            
            # 🌐 INTEGRATION & AUTOMATION CLASSES
            "api_specialist": MinionClass(
                name="api_specialist",
                display_name="API Integration Specialist",
                description="System integration and API connectivity specialist",
                icon="🌐",
                category="Integration & Automation",
                unlock_rank="Skilled",
                unlock_level=2,
                default_spirits=["connector", "builder", "debugger"],
                spirit_synergies={"connector_builder": 0.25, "builder_debugger": 0.20},
                spirit_conflicts={},
                net_performance_bonus=0.45,
                specialization="System integration and API connectivity",
                perfect_for=["System integration", "API development", "Microservices"],
                tools_count=17
            ),
            
            "automation_expert": MinionClass(
                name="automation_expert",
                display_name="Automation Expert",
                description="Process automation and workflow optimization specialist",
                icon="🤖",
                category="Integration & Automation",
                unlock_rank="Skilled",
                unlock_level=3,
                default_spirits=["scheduler", "builder", "connector"],
                spirit_synergies={"scheduler_builder": 0.25, "connector_scheduler": 0.20},
                spirit_conflicts={},
                net_performance_bonus=0.45,
                specialization="Process automation and workflow optimization",
                perfect_for=["Business process automation", "Workflow optimization"],
                tools_count=16
            ),
            
            # ✅ QUALITY & SECURITY CLASSES
            "security_specialist": MinionClass(
                name="security_specialist",
                display_name="Security Specialist",
                description="Cybersecurity and vulnerability assessment specialist",
                icon="🔒",
                category="Quality & Security",
                unlock_rank="Specialist",
                unlock_level=2,
                default_spirits=["security", "analyst", "debugger"],
                spirit_synergies={"security_analyst": 0.25, "debugger_security": 0.20},
                spirit_conflicts={},
                net_performance_bonus=0.45,
                specialization="Cybersecurity and vulnerability assessment",
                perfect_for=["Cybersecurity", "Penetration testing", "Security auditing"],
                tools_count=19
            ),
            
            "quality_assurance": MinionClass(
                name="quality_assurance",
                display_name="Quality Assurance",
                description="Comprehensive quality assurance and testing specialist",
                icon="✅",
                category="Quality & Security",
                unlock_rank="Novice",
                unlock_level=1,
                default_spirits=["checker", "security", "analyst"],
                spirit_synergies={"checker_security": 0.25, "analyst_checker": 0.20},
                spirit_conflicts={},
                net_performance_bonus=0.45,
                specialization="Comprehensive quality assurance and testing",
                perfect_for=["QA testing", "Security auditing", "Compliance"],
                tools_count=17
            ),
            
            # 🎯 SPECIALIZED & ADVANCED CLASSES
            "business_consultant": MinionClass(
                name="business_consultant",
                display_name="Business Consultant",
                description="Business consulting and strategic planning specialist",
                icon="💼",
                category="Specialized & Advanced",
                unlock_rank="Expert",
                unlock_level=1,
                default_spirits=["consultant", "analyst", "communicator"],
                spirit_synergies={"consultant_analyst": 0.20, "consultant_communicator": 0.15},
                spirit_conflicts={},
                net_performance_bonus=0.35,
                specialization="Business consulting and strategic planning",
                perfect_for=["Business consulting", "Strategic planning", "Decision support"],
                tools_count=12
            ),
            
            "educator": MinionClass(
                name="educator",
                display_name="Educational Designer",
                description="Educational content design and delivery specialist",
                icon="📚",
                category="Specialized & Advanced",
                unlock_rank="Expert",
                unlock_level=2,
                default_spirits=["educator", "designer", "writer"],
                spirit_synergies={"educator_designer": 0.20, "writer_educator": 0.20},
                spirit_conflicts={},
                net_performance_bonus=0.40,
                specialization="Educational content design and delivery",
                perfect_for=["Online education", "Training development", "Instructional design"],
                tools_count=15
            ),
            
            # 🌍 MULTI-LANGUAGE & GLOBAL CLASSES
            "global_communicator": MinionClass(
                name="global_communicator",
                display_name="Global Communicator",
                description="Multi-language communication and cultural adaptation specialist",
                icon="🌍",
                category="Multi-Language & Global",
                unlock_rank="Skilled",
                unlock_level=2,
                default_spirits=["translator", "communicator", "researcher"],
                spirit_synergies={"translator_communicator": 0.25, "communicator_researcher": 0.15},
                spirit_conflicts={},
                net_performance_bonus=0.40,
                specialization="Multi-language communication and cultural adaptation",
                perfect_for=["International business", "Multilingual content", "Global education"],
                tools_count=16
            ),
            
            # ⚡ HYBRID & VERSATILE CLASSES
            "swiss_army_knife": MinionClass(
                name="swiss_army_knife",
                display_name="Swiss Army Knife",
                description="General-purpose problem solving with diverse capabilities",
                icon="🔧",
                category="Hybrid & Versatile",
                unlock_rank="Novice",
                unlock_level=1,
                default_spirits=["builder", "writer", "analyst"],
                spirit_synergies={"builder_analyst": 0.20, "writer_analyst": 0.15},
                spirit_conflicts={},
                net_performance_bonus=0.35,
                specialization="General-purpose problem solving",
                perfect_for=["General assistance", "Prototyping", "Multi-task projects"],
                tools_count=20
            ),
            
            "startup_accelerator": MinionClass(
                name="startup_accelerator",
                display_name="Startup Accelerator",
                description="Rapid development and business growth specialist",
                icon="🚀",
                category="Hybrid & Versatile",
                unlock_rank="Skilled",
                unlock_level=2,
                default_spirits=["builder", "communicator", "analyst"],
                spirit_synergies={"builder_analyst": 0.20, "communicator_analyst": 0.15},
                spirit_conflicts={},
                net_performance_bonus=0.35,
                specialization="Rapid development and business growth",
                perfect_for=["Startup development", "Rapid prototyping", "Business acceleration"],
                tools_count=22
            )
        }
    
    def get_class(self, class_name: str) -> MinionClass:
        """Get a specific minion class"""
        return self.classes.get(class_name)
    
    def get_classes_by_category(self, category: str) -> List[MinionClass]:
        """Get all classes in a specific category"""
        return [cls for cls in self.classes.values() if cls.category == category]
    
    def get_available_classes(self, user_rank: str, user_level: int) -> List[MinionClass]:
        """Get classes available for user's rank and level"""
        available = []
        
        for cls in self.classes.values():
            # Check if user meets unlock requirements
            if self._can_unlock_class(cls, user_rank, user_level):
                available.append(cls)
        
        return available
    
    def _can_unlock_class(self, minion_class: MinionClass, user_rank: str, user_level: int) -> bool:
        """Check if user can unlock a specific class"""
        # Define rank hierarchy
        rank_hierarchy = {
            "Novice": 1,
            "Skilled": 2, 
            "Specialist": 3,
            "Expert": 4,
            "Master": 5,
            "Grandmaster": 6,
            "Legend": 7
        }
        
        user_rank_level = rank_hierarchy.get(user_rank, 1)
        required_rank_level = rank_hierarchy.get(minion_class.unlock_rank, 1)
        
        # Check rank and level requirements
        if user_rank_level < required_rank_level:
            return False
        
        if user_level < minion_class.unlock_level:
            return False
        
        return True
    
    def get_class_recommendations(self, user_interests: List[str]) -> List[MinionClass]:
        """Get class recommendations based on user interests"""
        recommendations = []
        
        # Simple keyword matching (can be enhanced with ML)
        interest_keywords = {
            "development": ["developer", "devops", "api_specialist"],
            "design": ["creative", "educator"],
            "data": ["data_scientist", "research_analyst"],
            "business": ["business_consultant", "startup_accelerator"],
            "security": ["security_specialist", "quality_assurance"],
            "content": ["content_marketer", "creative"],
            "automation": ["automation_expert", "api_specialist"],
            "education": ["educator", "global_communicator"]
        }
        
        for interest in user_interests:
            if interest.lower() in interest_keywords:
                for class_name in interest_keywords[interest.lower()]:
                    cls = self.get_class(class_name)
                    if cls:
                        recommendations.append(cls)
        
        # Remove duplicates and return
        return list({cls.name: cls for cls in recommendations}.values())
    
    def assign_class_spirits_to_minion(self, minion_id: int, class_name: str) -> Dict[str, Any]:
        """Assign a class's default spirits to a minion"""
        minion_class = self.get_class(class_name)
        if not minion_class:
            return {"success": False, "error": f"Class '{class_name}' not found"}
        
        # TODO: Implement database assignment
        # This would create minion_spirits records for each spirit in the class
        
        return {
            "success": True,
            "class": minion_class.name,
            "spirits_assigned": minion_class.default_spirits,
            "synergies": minion_class.spirit_synergies,
            "net_performance_bonus": minion_class.net_performance_bonus
        }

# Global registry instance
minion_class_registry = MinionClassRegistry()
