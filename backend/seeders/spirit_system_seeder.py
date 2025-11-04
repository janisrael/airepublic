#!/usr/bin/env python3
"""
Spirit System Seeder
Populates the spirits registry and pre-built minion templates

This seeder creates:
1. All 18 spirit types with their tools and unlock requirements
2. Spirit synergy and conflict matrices
3. Pre-built minion templates for easy selection
4. Tool registry entries for each spirit

Usage: python seeders/spirit_system_seeder.py
"""

import sys
import os
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_spirits_data():
    """Create comprehensive spirits registry data"""
    
    spirits_data = [
        # CONTENT & CREATIVITY SPIRITS
        {
            "name": "Writer Spirit",
            "category": "Content & Creativity",
            "description": "Content generation, documentation, summaries",
            "icon": "✍️",
            "unlock_rank": "Novice",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["markdown_generator", "style_adapter", "grammar_checker", "plagiarism_detector"],
            "synergies": {
                "Creative Spirit": 25,
                "Translator Spirit": 20,
                "Educator Spirit": 15
            },
            "conflicts": {
                "Mathematician Spirit": -10
            },
            "is_active": True,
            "purchaseable": True,
            "price_usd": 4.99,
            "price_points": 50,
            "is_premium": False,
            "free_with_subscription": True
        },
        {
            "name": "Creative Spirit",
            "category": "Content & Creativity",
            "description": "Artistic content, storytelling, ideation",
            "icon": "🎨",
            "unlock_rank": "Novice",
            "unlock_level": 3,
            "max_spirit_level": 10,
            "tools": ["story_generator", "mood_analyzer", "creative_prompts", "style_transfer"],
            "synergies": {
                "Writer Spirit": 25,
                "Designer Spirit": 30,
                "Educator Spirit": 20
            },
            "conflicts": {
                "Analyst Spirit": -15,
                "Security Spirit": -10
            },
            "is_active": True
        },
        {
            "name": "Translator Spirit",
            "category": "Content & Creativity",
            "description": "Multi-language translation, localization",
            "icon": "🌍",
            "unlock_rank": "Skilled",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["language_detector", "translation_engine", "cultural_adapter", "pronunciation_guide"],
            "synergies": {
                "Writer Spirit": 20,
                "Communicator Spirit": 25,
                "Researcher Spirit": 15
            },
            "conflicts": {},
            "is_active": True
        },
        
        # DATA & ANALYSIS SPIRITS
        {
            "name": "Analyst Spirit",
            "category": "Data & Analysis",
            "description": "Data analysis, RAG operations, insights",
            "icon": "📊",
            "unlock_rank": "Novice",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["chroma_search", "sql_connector", "data_cleaner", "chart_generator"],
            "synergies": {
                "Researcher Spirit": 30,
                "Mathematician Spirit": 25,
                "Security Spirit": 15,
                "Checker Spirit": 20
            },
            "conflicts": {
                "Creative Spirit": -15,
                "Healer Spirit": -5
            },
            "is_active": True
        },
        {
            "name": "Researcher Spirit",
            "category": "Data & Analysis",
            "description": "Web research, fact-checking, information gathering",
            "icon": "🔍",
            "unlock_rank": "Novice",
            "unlock_level": 2,
            "max_spirit_level": 10,
            "tools": ["web_search", "fact_checker", "source_validator", "knowledge_synthesizer"],
            "synergies": {
                "Analyst Spirit": 30,
                "Writer Spirit": 20,
                "Translator Spirit": 15
            },
            "conflicts": {},
            "is_active": True
        },
        {
            "name": "Mathematician Spirit",
            "category": "Data & Analysis",
            "description": "Mathematical computations, statistical analysis",
            "icon": "🧮",
            "unlock_rank": "Skilled",
            "unlock_level": 2,
            "max_spirit_level": 10,
            "tools": ["calculator_engine", "statistical_analyzer", "equation_solver", "graph_plotter"],
            "synergies": {
                "Analyst Spirit": 25,
                "Builder Spirit": 20,
                "Checker Spirit": 15
            },
            "conflicts": {
                "Writer Spirit": -10,
                "Creative Spirit": -12
            },
            "is_active": True
        },
        
        # DEVELOPMENT & TECHNICAL SPIRITS
        {
            "name": "Builder Spirit",
            "category": "Development & Technical",
            "description": "Code generation, infrastructure, automation",
            "icon": "🛠️",
            "unlock_rank": "Novice",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["file_writer", "folder_manager", "code_generator", "docker_tool"],
            "synergies": {
                "Debugger Spirit": 20,
                "DevOps Spirit": 25,
                "Checker Spirit": 20,
                "Mathematician Spirit": 20
            },
            "conflicts": {
                "Security Spirit": -10,
                "Creative Spirit": -5
            },
            "is_active": True
        },
        {
            "name": "Debugger Spirit",
            "category": "Development & Technical",
            "description": "Code debugging, error analysis, optimization",
            "icon": "🐛",
            "unlock_rank": "Skilled",
            "unlock_level": 3,
            "max_spirit_level": 10,
            "tools": ["error_analyzer", "performance_profiler", "code_optimizer", "security_scanner"],
            "synergies": {
                "Builder Spirit": 20,
                "Security Spirit": 20,
                "Checker Spirit": 20,
                "Analyst Spirit": 15
            },
            "conflicts": {},
            "is_active": True
        },
        {
            "name": "DevOps Spirit",
            "category": "Development & Technical",
            "description": "Infrastructure, deployment, monitoring",
            "icon": "⚙️",
            "unlock_rank": "Specialist",
            "unlock_level": 2,
            "max_spirit_level": 10,
            "tools": ["deployment_manager", "monitoring_tool", "backup_manager", "scaling_advisor"],
            "synergies": {
                "Builder Spirit": 25,
                "Scheduler Spirit": 20,
                "Security Spirit": 15,
                "Analyst Spirit": 15
            },
            "conflicts": {},
            "is_active": True
        },
        
        # INTEGRATION & COMMUNICATION SPIRITS
        {
            "name": "Connector Spirit",
            "category": "Integration & Communication",
            "description": "External API integrations, LLM providers",
            "icon": "🌐",
            "unlock_rank": "Novice",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["openai_adapter", "anthropic_adapter", "nvidia_adapter", "huggingface_adapter"],
            "synergies": {
                "Builder Spirit": 25,
                "Scheduler Spirit": 15,
                "Analyst Spirit": 20
            },
            "conflicts": {},
            "is_active": True
        },
        {
            "name": "Communicator Spirit",
            "category": "Integration & Communication",
            "description": "Email, messaging, social media, notifications",
            "icon": "💬",
            "unlock_rank": "Skilled",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["email_manager", "sms_sender", "social_media_poster", "notification_system"],
            "synergies": {
                "Scheduler Spirit": 20,
                "Translator Spirit": 25,
                "Creative Spirit": 25,
                "Writer Spirit": 20
            },
            "conflicts": {},
            "is_active": True
        },
        {
            "name": "Scheduler Spirit",
            "category": "Integration & Communication",
            "description": "Calendar management, task scheduling, reminders",
            "icon": "📅",
            "unlock_rank": "Skilled",
            "unlock_level": 2,
            "max_spirit_level": 10,
            "tools": ["calendar_manager", "task_scheduler", "reminder_system", "meeting_planner"],
            "synergies": {
                "DevOps Spirit": 20,
                "Communicator Spirit": 20,
                "Builder Spirit": 15,
                "Analyst Spirit": 15
            },
            "conflicts": {},
            "is_active": True
        },
        
        # QUALITY & VALIDATION SPIRITS
        {
            "name": "Checker Spirit",
            "category": "Quality & Validation",
            "description": "Validation, quality assurance, testing",
            "icon": "✅",
            "unlock_rank": "Novice",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["grammar_checker", "test_runner", "consistency_checker", "report_generator"],
            "synergies": {
                "Security Spirit": 25,
                "Builder Spirit": 20,
                "Analyst Spirit": 20,
                "Debugger Spirit": 20
            },
            "conflicts": {},
            "is_active": True
        },
        {
            "name": "Security Spirit",
            "category": "Quality & Validation",
            "description": "Security analysis, vulnerability scanning, compliance",
            "icon": "🔒",
            "unlock_rank": "Specialist",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["vulnerability_scanner", "encryption_manager", "compliance_checker", "audit_logger"],
            "synergies": {
                "Checker Spirit": 25,
                "Analyst Spirit": 15,
                "Debugger Spirit": 20,
                "DevOps Spirit": 15
            },
            "conflicts": {
                "Builder Spirit": -10,
                "Creative Spirit": -10
            },
            "is_active": True
        },
        
        # SPECIALIZED & ADVANCED SPIRITS
        {
            "name": "Educator Spirit",
            "category": "Specialized & Advanced",
            "description": "Teaching, tutoring, learning path creation",
            "icon": "📚",
            "unlock_rank": "Expert",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["lesson_planner", "quiz_generator", "progress_tracker", "knowledge_assessor"],
            "synergies": {
                "Writer Spirit": 15,
                "Creative Spirit": 20,
                "Designer Spirit": 20,
                "Communicator Spirit": 15
            },
            "conflicts": {
                "Consultant Spirit": -5
            },
            "is_active": True
        },
        {
            "name": "Designer Spirit",
            "category": "Specialized & Advanced",
            "description": "UI/UX design, visual content, layout optimization",
            "icon": "🎨",
            "unlock_rank": "Expert",
            "unlock_level": 2,
            "max_spirit_level": 10,
            "tools": ["layout_generator", "color_palette_creator", "ui_mockup_tool", "accessibility_checker"],
            "synergies": {
                "Creative Spirit": 30,
                "Educator Spirit": 20,
                "Builder Spirit": 15
            },
            "conflicts": {
                "Builder Spirit": -5
            },
            "is_active": True
        },
        {
            "name": "Consultant Spirit",
            "category": "Specialized & Advanced",
            "description": "Business advice, strategy planning, decision support",
            "icon": "💼",
            "unlock_rank": "Master",
            "unlock_level": 1,
            "max_spirit_level": 10,
            "tools": ["business_analyzer", "strategy_planner", "risk_assessor", "market_researcher"],
            "synergies": {
                "Analyst Spirit": 20,
                "Communicator Spirit": 15,
                "Scheduler Spirit": 15,
                "Researcher Spirit": 15
            },
            "conflicts": {
                "Educator Spirit": -5
            },
            "is_active": True
        },
        {
            "name": "Healer Spirit",
            "category": "Specialized & Advanced",
            "description": "Health analysis, wellness advice, medical information",
            "icon": "🩺",
            "unlock_rank": "Master",
            "unlock_level": 2,
            "max_spirit_level": 10,
            "tools": ["symptom_analyzer", "wellness_tracker", "medication_reminder", "health_educator"],
            "synergies": {
                "Educator Spirit": 20,
                "Communicator Spirit": 15,
                "Scheduler Spirit": 15
            },
            "conflicts": {
                "Analyst Spirit": -5
            },
            "is_active": True
        }
    ]
    
    return spirits_data

def create_minion_templates():
    """Create pre-built minion templates"""
    
    templates = [
        # DEVELOPMENT & TECHNICAL MINIONS
        {
            "name": "CodeMaster Pro",
            "category": "Development & Technical",
            "icon": "🚀",
            "description": "Full-stack development with security focus",
            "spirits": ["Builder Spirit", "Debugger Spirit", "Analyst Spirit", "Security Spirit", "Checker Spirit"],
            "synergy_bonus": 25,
            "conflict_penalty": -10,
            "net_performance": 25,
            "tools_count": 20,
            "perfect_for": "Enterprise software development, secure coding",
            "unlock_rank": "Novice",
            "unlock_level": 1
        },
        {
            "name": "DevOps Engineer",
            "category": "Development & Technical",
            "icon": "⚙️",
            "description": "Infrastructure automation and monitoring",
            "spirits": ["DevOps Spirit", "Builder Spirit", "Analyst Spirit", "Scheduler Spirit", "Security Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 18,
            "perfect_for": "CI/CD, infrastructure management, system administration",
            "unlock_rank": "Specialist",
            "unlock_level": 2
        },
        {
            "name": "Hybrid Developer",
            "category": "Development & Technical",
            "icon": "🔄",
            "description": "Full-stack development with creative problem-solving",
            "spirits": ["Builder Spirit", "Creative Spirit", "Connector Spirit", "Debugger Spirit", "Checker Spirit"],
            "synergy_bonus": 35,
            "conflict_penalty": -5,
            "net_performance": 30,
            "tools_count": 22,
            "perfect_for": "Startup development, rapid prototyping, creative coding",
            "unlock_rank": "Skilled",
            "unlock_level": 3
        },
        {
            "name": "Enterprise Architect",
            "category": "Development & Technical",
            "icon": "🏗️",
            "description": "Enterprise system architecture and strategy",
            "spirits": ["DevOps Spirit", "Security Spirit", "Analyst Spirit", "Consultant Spirit", "Builder Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 21,
            "perfect_for": "Enterprise architecture, system design, IT strategy",
            "unlock_rank": "Master",
            "unlock_level": 1
        },
        
        # CONTENT & CREATIVE MINIONS
        {
            "name": "Creative Assistant",
            "category": "Content & Creative",
            "icon": "✨",
            "description": "Content creation and education",
            "spirits": ["Writer Spirit", "Creative Spirit", "Translator Spirit", "Communicator Spirit", "Educator Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 15,
            "perfect_for": "Content marketing, education, storytelling",
            "unlock_rank": "Expert",
            "unlock_level": 1
        },
        {
            "name": "SEO Pro",
            "category": "Content & Creative",
            "icon": "🔍",
            "description": "SEO optimization and content strategy",
            "spirits": ["Researcher Spirit", "Writer Spirit", "Analyst Spirit", "Communicator Spirit", "Checker Spirit"],
            "synergy_bonus": 50,
            "conflict_penalty": 0,
            "net_performance": 50,
            "tools_count": 16,
            "perfect_for": "Digital marketing, SEO, content optimization",
            "unlock_rank": "Novice",
            "unlock_level": 2
        },
        {
            "name": "Marketing Master",
            "category": "Content & Creative",
            "icon": "📈",
            "description": "Multi-channel marketing and campaign management",
            "spirits": ["Communicator Spirit", "Creative Spirit", "Analyst Spirit", "Scheduler Spirit", "Researcher Spirit"],
            "synergy_bonus": 55,
            "conflict_penalty": 0,
            "net_performance": 55,
            "tools_count": 20,
            "perfect_for": "Digital marketing, campaign management, brand strategy",
            "unlock_rank": "Skilled",
            "unlock_level": 2
        },
        {
            "name": "UI/UX Designer",
            "category": "Content & Creative",
            "icon": "🎨",
            "description": "User interface and experience design",
            "spirits": ["Designer Spirit", "Creative Spirit", "Builder Spirit", "Analyst Spirit", "Checker Spirit"],
            "synergy_bonus": 50,
            "conflict_penalty": -5,
            "net_performance": 45,
            "tools_count": 18,
            "perfect_for": "Web design, mobile apps, user experience optimization",
            "unlock_rank": "Expert",
            "unlock_level": 2
        },
        
        # DATA & ANALYSIS MINIONS
        {
            "name": "Research Analyst",
            "category": "Data & Analysis",
            "icon": "📊",
            "description": "Data analysis and research",
            "spirits": ["Researcher Spirit", "Analyst Spirit", "Mathematician Spirit", "Checker Spirit", "Security Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 18,
            "perfect_for": "Business intelligence, research, data science",
            "unlock_rank": "Skilled",
            "unlock_level": 2
        },
        {
            "name": "Data Scientist",
            "category": "Data & Analysis",
            "icon": "🧮",
            "description": "Advanced data analysis and machine learning",
            "spirits": ["Mathematician Spirit", "Analyst Spirit", "Builder Spirit", "Researcher Spirit", "Checker Spirit"],
            "synergy_bonus": 55,
            "conflict_penalty": 0,
            "net_performance": 55,
            "tools_count": 22,
            "perfect_for": "Machine learning, statistical analysis, data engineering",
            "unlock_rank": "Specialist",
            "unlock_level": 3
        },
        {
            "name": "Monitoring Specialist",
            "category": "Data & Analysis",
            "icon": "📊",
            "description": "System monitoring and alerting",
            "spirits": ["DevOps Spirit", "Analyst Spirit", "Scheduler Spirit", "Communicator Spirit", "Security Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 16,
            "perfect_for": "System monitoring, incident management, performance tracking",
            "unlock_rank": "Specialist",
            "unlock_level": 2
        },
        
        # INTEGRATION & AUTOMATION MINIONS
        {
            "name": "API Integration Specialist",
            "category": "Integration & Automation",
            "icon": "🌐",
            "description": "API integration and system connectivity",
            "spirits": ["Connector Spirit", "Builder Spirit", "Debugger Spirit", "Analyst Spirit", "Security Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 19,
            "perfect_for": "System integration, API development, microservices",
            "unlock_rank": "Skilled",
            "unlock_level": 3
        },
        {
            "name": "Automation Expert",
            "category": "Integration & Automation",
            "icon": "🤖",
            "description": "Process automation and workflow optimization",
            "spirits": ["Scheduler Spirit", "Builder Spirit", "Connector Spirit", "Analyst Spirit", "Checker Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 18,
            "perfect_for": "Business process automation, workflow optimization",
            "unlock_rank": "Skilled",
            "unlock_level": 2
        },
        {
            "name": "Swiss Army Knife",
            "category": "Integration & Automation",
            "icon": "⚡",
            "description": "General-purpose problem solving",
            "spirits": ["Builder Spirit", "Writer Spirit", "Analyst Spirit", "Connector Spirit", "Checker Spirit"],
            "synergy_bonus": 35,
            "conflict_penalty": 0,
            "net_performance": 35,
            "tools_count": 20,
            "perfect_for": "General assistance, prototyping, multi-task projects",
            "unlock_rank": "Novice",
            "unlock_level": 1
        },
        {
            "name": "Startup Accelerator",
            "category": "Integration & Automation",
            "icon": "🚀",
            "description": "Rapid development and business growth",
            "spirits": ["Builder Spirit", "Communicator Spirit", "Analyst Spirit", "Creative Spirit", "Scheduler Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": -5,
            "net_performance": 40,
            "tools_count": 22,
            "perfect_for": "Startup development, rapid prototyping, business acceleration",
            "unlock_rank": "Skilled",
            "unlock_level": 2
        },
        
        # QUALITY & SECURITY MINIONS
        {
            "name": "Quality Assurance",
            "category": "Quality & Security",
            "icon": "✅",
            "description": "Comprehensive quality assurance and testing",
            "spirits": ["Checker Spirit", "Security Spirit", "Analyst Spirit", "Debugger Spirit", "Communicator Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 17,
            "perfect_for": "QA testing, security auditing, compliance",
            "unlock_rank": "Specialist",
            "unlock_level": 1
        },
        {
            "name": "Security Specialist",
            "category": "Quality & Security",
            "icon": "🔒",
            "description": "Cybersecurity and vulnerability assessment",
            "spirits": ["Security Spirit", "Analyst Spirit", "Debugger Spirit", "Researcher Spirit", "Checker Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 19,
            "perfect_for": "Cybersecurity, penetration testing, security auditing",
            "unlock_rank": "Specialist",
            "unlock_level": 1
        },
        
        # SPECIALIZED & ADVANCED MINIONS
        {
            "name": "Business Consultant",
            "category": "Specialized & Advanced",
            "icon": "💼",
            "description": "Business consulting and strategy",
            "spirits": ["Consultant Spirit", "Analyst Spirit", "Communicator Spirit", "Scheduler Spirit", "Educator Spirit"],
            "synergy_bonus": 35,
            "conflict_penalty": 0,
            "net_performance": 35,
            "tools_count": 12,
            "perfect_for": "Business consulting, strategic planning, decision support",
            "unlock_rank": "Master",
            "unlock_level": 1
        },
        {
            "name": "Educational Designer",
            "category": "Specialized & Advanced",
            "icon": "📚",
            "description": "Educational content design and delivery",
            "spirits": ["Educator Spirit", "Designer Spirit", "Writer Spirit", "Analyst Spirit", "Communicator Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 15,
            "perfect_for": "Online education, training development, instructional design",
            "unlock_rank": "Expert",
            "unlock_level": 2
        },
        {
            "name": "Health & Wellness Coach",
            "category": "Specialized & Advanced",
            "icon": "🩺",
            "description": "Health monitoring and wellness guidance",
            "spirits": ["Healer Spirit", "Educator Spirit", "Communicator Spirit", "Scheduler Spirit", "Analyst Spirit"],
            "synergy_bonus": 35,
            "conflict_penalty": 0,
            "net_performance": 35,
            "tools_count": 12,
            "perfect_for": "Health coaching, wellness programs, medical information",
            "unlock_rank": "Master",
            "unlock_level": 2
        },
        
        # MULTI-LANGUAGE & GLOBAL MINIONS
        {
            "name": "Global Communicator",
            "category": "Multi-Language & Global",
            "icon": "🌍",
            "description": "Multi-language communication and education",
            "spirits": ["Translator Spirit", "Communicator Spirit", "Writer Spirit", "Researcher Spirit", "Educator Spirit"],
            "synergy_bonus": 45,
            "conflict_penalty": 0,
            "net_performance": 45,
            "tools_count": 16,
            "perfect_for": "International business, multilingual content, global education",
            "unlock_rank": "Expert",
            "unlock_level": 1
        },
        {
            "name": "Cultural Bridge",
            "category": "Multi-Language & Global",
            "icon": "🌉",
            "description": "Cross-cultural communication and adaptation",
            "spirits": ["Translator Spirit", "Creative Spirit", "Communicator Spirit", "Researcher Spirit", "Consultant Spirit"],
            "synergy_bonus": 35,
            "conflict_penalty": 0,
            "net_performance": 35,
            "tools_count": 14,
            "perfect_for": "International relations, cultural consulting, global marketing",
            "unlock_rank": "Master",
            "unlock_level": 1
        },
        
        # DESIGN & CREATIVE MINIONS
        {
            "name": "Brand Strategist",
            "category": "Design & Creative",
            "icon": "🎯",
            "description": "Brand development and strategic communication",
            "spirits": ["Creative Spirit", "Communicator Spirit", "Analyst Spirit", "Researcher Spirit", "Consultant Spirit"],
            "synergy_bonus": 55,
            "conflict_penalty": 0,
            "net_performance": 55,
            "tools_count": 17,
            "perfect_for": "Brand development, marketing strategy, creative direction",
            "unlock_rank": "Master",
            "unlock_level": 1
        }
    ]
    
    return templates

def create_tools_registry():
    """Create comprehensive tools registry"""
    
    tools_data = [
        # Writer Spirit Tools
        {"name": "markdown_generator", "category": "Content", "description": "Generate clean markdown documentation"},
        {"name": "style_adapter", "category": "Content", "description": "Adapt writing style to match user preferences"},
        {"name": "grammar_checker", "category": "Content", "description": "Check grammar and language quality"},
        {"name": "plagiarism_detector", "category": "Content", "description": "Detect plagiarism and ensure originality"},
        
        # Creative Spirit Tools
        {"name": "story_generator", "category": "Creative", "description": "Generate creative stories and narratives"},
        {"name": "mood_analyzer", "category": "Creative", "description": "Analyze emotional tone and mood"},
        {"name": "creative_prompts", "category": "Creative", "description": "Generate creative prompts and ideas"},
        {"name": "style_transfer", "category": "Creative", "description": "Transfer artistic styles to content"},
        
        # Translator Spirit Tools
        {"name": "language_detector", "category": "Translation", "description": "Detect and identify languages"},
        {"name": "translation_engine", "category": "Translation", "description": "Multi-language translation engine"},
        {"name": "cultural_adapter", "category": "Translation", "description": "Adapt content for cultural context"},
        {"name": "pronunciation_guide", "category": "Translation", "description": "Provide pronunciation guidance"},
        
        # Analyst Spirit Tools
        {"name": "chroma_search", "category": "Data", "description": "Vector database search and retrieval"},
        {"name": "sql_connector", "category": "Data", "description": "Database connection and query execution"},
        {"name": "data_cleaner", "category": "Data", "description": "Clean and preprocess datasets"},
        {"name": "chart_generator", "category": "Data", "description": "Generate data visualizations and charts"},
        
        # Researcher Spirit Tools
        {"name": "web_search", "category": "Research", "description": "Real-time web information retrieval"},
        {"name": "fact_checker", "category": "Research", "description": "Verify facts and information accuracy"},
        {"name": "source_validator", "category": "Research", "description": "Validate source credibility"},
        {"name": "knowledge_synthesizer", "category": "Research", "description": "Synthesize and summarize information"},
        
        # Mathematician Spirit Tools
        {"name": "calculator_engine", "category": "Math", "description": "Advanced mathematical computations"},
        {"name": "statistical_analyzer", "category": "Math", "description": "Statistical analysis and modeling"},
        {"name": "equation_solver", "category": "Math", "description": "Solve complex mathematical equations"},
        {"name": "graph_plotter", "category": "Math", "description": "Plot mathematical graphs and visualizations"},
        
        # Builder Spirit Tools
        {"name": "file_writer", "category": "Development", "description": "Create and modify files"},
        {"name": "folder_manager", "category": "Development", "description": "Manage directory structures"},
        {"name": "code_generator", "category": "Development", "description": "Generate application code"},
        {"name": "docker_tool", "category": "Development", "description": "Build and manage Docker containers"},
        
        # Debugger Spirit Tools
        {"name": "error_analyzer", "category": "Debug", "description": "Analyze and identify errors"},
        {"name": "performance_profiler", "category": "Debug", "description": "Profile code performance"},
        {"name": "code_optimizer", "category": "Debug", "description": "Optimize code for better performance"},
        {"name": "security_scanner", "category": "Debug", "description": "Scan for security vulnerabilities"},
        
        # DevOps Spirit Tools
        {"name": "deployment_manager", "category": "DevOps", "description": "Manage application deployments"},
        {"name": "monitoring_tool", "category": "DevOps", "description": "Monitor system performance"},
        {"name": "backup_manager", "category": "DevOps", "description": "Manage data backups"},
        {"name": "scaling_advisor", "category": "DevOps", "description": "Provide scaling recommendations"},
        
        # Connector Spirit Tools
        {"name": "openai_adapter", "category": "Integration", "description": "OpenAI API integration"},
        {"name": "anthropic_adapter", "category": "Integration", "description": "Anthropic API integration"},
        {"name": "nvidia_adapter", "category": "Integration", "description": "NVIDIA API integration"},
        {"name": "huggingface_adapter", "category": "Integration", "description": "Hugging Face API integration"},
        
        # Communicator Spirit Tools
        {"name": "email_manager", "category": "Communication", "description": "Manage email communications"},
        {"name": "sms_sender", "category": "Communication", "description": "Send SMS messages"},
        {"name": "social_media_poster", "category": "Communication", "description": "Post to social media platforms"},
        {"name": "notification_system", "category": "Communication", "description": "Send multi-channel notifications"},
        
        # Scheduler Spirit Tools
        {"name": "calendar_manager", "category": "Scheduling", "description": "Manage calendars and events"},
        {"name": "task_scheduler", "category": "Scheduling", "description": "Schedule and manage tasks"},
        {"name": "reminder_system", "category": "Scheduling", "description": "Create and manage reminders"},
        {"name": "meeting_planner", "category": "Scheduling", "description": "Plan and coordinate meetings"},
        
        # Checker Spirit Tools
        {"name": "test_runner", "category": "Testing", "description": "Run unit and integration tests"},
        {"name": "consistency_checker", "category": "Testing", "description": "Check output consistency"},
        {"name": "report_generator", "category": "Testing", "description": "Generate test reports"},
        
        # Security Spirit Tools
        {"name": "vulnerability_scanner", "category": "Security", "description": "Scan for security vulnerabilities"},
        {"name": "encryption_manager", "category": "Security", "description": "Manage data encryption"},
        {"name": "compliance_checker", "category": "Security", "description": "Check regulatory compliance"},
        {"name": "audit_logger", "category": "Security", "description": "Log security audit events"},
        
        # Educator Spirit Tools
        {"name": "lesson_planner", "category": "Education", "description": "Plan educational lessons"},
        {"name": "quiz_generator", "category": "Education", "description": "Generate quizzes and assessments"},
        {"name": "progress_tracker", "category": "Education", "description": "Track learning progress"},
        {"name": "knowledge_assessor", "category": "Education", "description": "Assess knowledge gaps"},
        
        # Designer Spirit Tools
        {"name": "layout_generator", "category": "Design", "description": "Generate UI layouts"},
        {"name": "color_palette_creator", "category": "Design", "description": "Create color palettes"},
        {"name": "ui_mockup_tool", "category": "Design", "description": "Create UI mockups"},
        {"name": "accessibility_checker", "category": "Design", "description": "Check accessibility compliance"},
        
        # Consultant Spirit Tools
        {"name": "business_analyzer", "category": "Business", "description": "Analyze business processes"},
        {"name": "strategy_planner", "category": "Business", "description": "Plan business strategies"},
        {"name": "risk_assessor", "category": "Business", "description": "Assess business risks"},
        {"name": "market_researcher", "category": "Business", "description": "Research market trends"},
        
        # Healer Spirit Tools
        {"name": "symptom_analyzer", "category": "Health", "description": "Analyze health symptoms"},
        {"name": "wellness_tracker", "category": "Health", "description": "Track health and wellness"},
        {"name": "medication_reminder", "category": "Health", "description": "Manage medication reminders"},
        {"name": "health_educator", "category": "Health", "description": "Provide health education"}
    ]
    
    return tools_data

def generate_sql_seeder():
    """Generate SQL INSERT statements for the seeder"""
    
    spirits_data = create_spirits_data()
    templates_data = create_minion_templates()
    tools_data = create_tools_registry()
    
    sql_statements = []
    
    # Add header comment
    sql_statements.append("-- Spirit System Seeder")
    sql_statements.append("-- Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sql_statements.append("")
    
    # Insert spirits registry
    sql_statements.append("-- Insert Spirits Registry")
    for spirit in spirits_data:
        sql = f"""INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            '{spirit['name']}',
            '{spirit['category']}',
            '{spirit['description']}',
            '{spirit['icon']}',
            '{spirit['unlock_rank']}',
            {spirit['unlock_level']},
            {spirit['max_spirit_level']},
            '{json.dumps(spirit['tools'])}',
            '{json.dumps(spirit['synergies'])}',
            '{json.dumps(spirit['conflicts'])}',
            {str(spirit['is_active']).lower()},
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );"""
        sql_statements.append(sql)
    
    sql_statements.append("")
    
    # Insert tools registry
    sql_statements.append("-- Insert Tools Registry")
    for tool in tools_data:
        sql = f"""INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            '{tool['name']}',
            '{tool['category']}',
            '{tool['description']}',
            true,
            CURRENT_TIMESTAMP
        );"""
        sql_statements.append(sql)
    
    sql_statements.append("")
    
    # Insert minion templates (as a separate table or JSON config)
    sql_statements.append("-- Insert Minion Templates")
    sql_statements.append("-- Note: These can be stored in a minion_templates table or as JSON config")
    
    for template in templates_data:
        sql = f"""INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            '{template['name']}',
            '{template['category']}',
            '{template['icon']}',
            '{template['description']}',
            '{json.dumps(template['spirits'])}',
            {template['synergy_bonus']},
            {template['conflict_penalty']},
            {template['net_performance']},
            {template['tools_count']},
            '{template['perfect_for']}',
            '{template['unlock_rank']}',
            {template['unlock_level']},
            CURRENT_TIMESTAMP
        );"""
        sql_statements.append(sql)
    
    return sql_statements

def main():
    """Main seeder function"""
    print("🌟 Spirit System Seeder")
    print("=" * 50)
    
    # Generate data
    spirits_data = create_spirits_data()
    templates_data = create_minion_templates()
    tools_data = create_tools_registry()
    
    print(f"✅ Generated {len(spirits_data)} spirits")
    print(f"✅ Generated {len(templates_data)} minion templates")
    print(f"✅ Generated {len(tools_data)} tools")
    
    # Generate SQL
    sql_statements = generate_sql_seeder()
    
    # Write to file
    output_file = "spirit_system_seeder.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"✅ SQL seeder written to: {output_file}")
    
    # Write JSON data files for easy import
    with open("spirits_registry.json", 'w', encoding='utf-8') as f:
        json.dump(spirits_data, f, indent=2, ensure_ascii=False)
    
    with open("minion_templates.json", 'w', encoding='utf-8') as f:
        json.dump(templates_data, f, indent=2, ensure_ascii=False)
    
    with open("tools_registry.json", 'w', encoding='utf-8') as f:
        json.dump(tools_data, f, indent=2, ensure_ascii=False)
    
    print("✅ JSON data files created:")
    print("   - spirits_registry.json")
    print("   - minion_templates.json")
    print("   - tools_registry.json")
    
    print("\n🎯 Summary:")
    print(f"   📊 {len(spirits_data)} Spirit Types")
    print(f"   🤖 {len(templates_data)} Pre-Built Minion Templates")
    print(f"   🛠️ {len(tools_data)} Tools Available")
    print(f"   🔄 {len([s for s in spirits_data if s['synergies']])} Spirit Synergies")
    print(f"   ⚠️ {len([s for s in spirits_data if s['conflicts']])} Spirit Conflicts")
    
    print("\n🚀 Ready for PostgreSQL implementation!")

if __name__ == "__main__":
    main()
