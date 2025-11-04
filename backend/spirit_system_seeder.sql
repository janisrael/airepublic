-- Spirit System Seeder
-- Generated on: 2025-10-02 09:15:21

-- Insert Spirits Registry
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Writer Spirit',
            'Content & Creativity',
            'Content generation, documentation, summaries',
            '✍️',
            'Novice',
            1,
            10,
            '["markdown_generator", "style_adapter", "grammar_checker", "plagiarism_detector"]',
            '{"Creative Spirit": 25, "Translator Spirit": 20, "Educator Spirit": 15}',
            '{"Mathematician Spirit": -10}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Creative Spirit',
            'Content & Creativity',
            'Artistic content, storytelling, ideation',
            '🎨',
            'Novice',
            3,
            10,
            '["story_generator", "mood_analyzer", "creative_prompts", "style_transfer"]',
            '{"Writer Spirit": 25, "Designer Spirit": 30, "Educator Spirit": 20}',
            '{"Analyst Spirit": -15, "Security Spirit": -10}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Translator Spirit',
            'Content & Creativity',
            'Multi-language translation, localization',
            '🌍',
            'Skilled',
            1,
            10,
            '["language_detector", "translation_engine", "cultural_adapter", "pronunciation_guide"]',
            '{"Writer Spirit": 20, "Communicator Spirit": 25, "Researcher Spirit": 15}',
            '{}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Analyst Spirit',
            'Data & Analysis',
            'Data analysis, RAG operations, insights',
            '📊',
            'Novice',
            1,
            10,
            '["chroma_search", "sql_connector", "data_cleaner", "chart_generator"]',
            '{"Researcher Spirit": 30, "Mathematician Spirit": 25, "Security Spirit": 15, "Checker Spirit": 20}',
            '{"Creative Spirit": -15, "Healer Spirit": -5}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Researcher Spirit',
            'Data & Analysis',
            'Web research, fact-checking, information gathering',
            '🔍',
            'Novice',
            2,
            10,
            '["web_search", "fact_checker", "source_validator", "knowledge_synthesizer"]',
            '{"Analyst Spirit": 30, "Writer Spirit": 20, "Translator Spirit": 15}',
            '{}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Mathematician Spirit',
            'Data & Analysis',
            'Mathematical computations, statistical analysis',
            '🧮',
            'Skilled',
            2,
            10,
            '["calculator_engine", "statistical_analyzer", "equation_solver", "graph_plotter"]',
            '{"Analyst Spirit": 25, "Builder Spirit": 20, "Checker Spirit": 15}',
            '{"Writer Spirit": -10, "Creative Spirit": -12}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Builder Spirit',
            'Development & Technical',
            'Code generation, infrastructure, automation',
            '🛠️',
            'Novice',
            1,
            10,
            '["file_writer", "folder_manager", "code_generator", "docker_tool"]',
            '{"Debugger Spirit": 20, "DevOps Spirit": 25, "Checker Spirit": 20, "Mathematician Spirit": 20}',
            '{"Security Spirit": -10, "Creative Spirit": -5}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Debugger Spirit',
            'Development & Technical',
            'Code debugging, error analysis, optimization',
            '🐛',
            'Skilled',
            3,
            10,
            '["error_analyzer", "performance_profiler", "code_optimizer", "security_scanner"]',
            '{"Builder Spirit": 20, "Security Spirit": 20, "Checker Spirit": 20, "Analyst Spirit": 15}',
            '{}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'DevOps Spirit',
            'Development & Technical',
            'Infrastructure, deployment, monitoring',
            '⚙️',
            'Specialist',
            2,
            10,
            '["deployment_manager", "monitoring_tool", "backup_manager", "scaling_advisor"]',
            '{"Builder Spirit": 25, "Scheduler Spirit": 20, "Security Spirit": 15, "Analyst Spirit": 15}',
            '{}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Connector Spirit',
            'Integration & Communication',
            'External API integrations, LLM providers',
            '🌐',
            'Novice',
            1,
            10,
            '["openai_adapter", "anthropic_adapter", "nvidia_adapter", "huggingface_adapter"]',
            '{"Builder Spirit": 25, "Scheduler Spirit": 15, "Analyst Spirit": 20}',
            '{}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Communicator Spirit',
            'Integration & Communication',
            'Email, messaging, social media, notifications',
            '💬',
            'Skilled',
            1,
            10,
            '["email_manager", "sms_sender", "social_media_poster", "notification_system"]',
            '{"Scheduler Spirit": 20, "Translator Spirit": 25, "Creative Spirit": 25, "Writer Spirit": 20}',
            '{}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Scheduler Spirit',
            'Integration & Communication',
            'Calendar management, task scheduling, reminders',
            '📅',
            'Skilled',
            2,
            10,
            '["calendar_manager", "task_scheduler", "reminder_system", "meeting_planner"]',
            '{"DevOps Spirit": 20, "Communicator Spirit": 20, "Builder Spirit": 15, "Analyst Spirit": 15}',
            '{}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Checker Spirit',
            'Quality & Validation',
            'Validation, quality assurance, testing',
            '✅',
            'Novice',
            1,
            10,
            '["grammar_checker", "test_runner", "consistency_checker", "report_generator"]',
            '{"Security Spirit": 25, "Builder Spirit": 20, "Analyst Spirit": 20, "Debugger Spirit": 20}',
            '{}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Security Spirit',
            'Quality & Validation',
            'Security analysis, vulnerability scanning, compliance',
            '🔒',
            'Specialist',
            1,
            10,
            '["vulnerability_scanner", "encryption_manager", "compliance_checker", "audit_logger"]',
            '{"Checker Spirit": 25, "Analyst Spirit": 15, "Debugger Spirit": 20, "DevOps Spirit": 15}',
            '{"Builder Spirit": -10, "Creative Spirit": -10}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Educator Spirit',
            'Specialized & Advanced',
            'Teaching, tutoring, learning path creation',
            '📚',
            'Expert',
            1,
            10,
            '["lesson_planner", "quiz_generator", "progress_tracker", "knowledge_assessor"]',
            '{"Writer Spirit": 15, "Creative Spirit": 20, "Designer Spirit": 20, "Communicator Spirit": 15}',
            '{"Consultant Spirit": -5}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Designer Spirit',
            'Specialized & Advanced',
            'UI/UX design, visual content, layout optimization',
            '🎨',
            'Expert',
            2,
            10,
            '["layout_generator", "color_palette_creator", "ui_mockup_tool", "accessibility_checker"]',
            '{"Creative Spirit": 30, "Educator Spirit": 20, "Builder Spirit": 15}',
            '{"Builder Spirit": -5}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Consultant Spirit',
            'Specialized & Advanced',
            'Business advice, strategy planning, decision support',
            '💼',
            'Master',
            1,
            10,
            '["business_analyzer", "strategy_planner", "risk_assessor", "market_researcher"]',
            '{"Analyst Spirit": 20, "Communicator Spirit": 15, "Scheduler Spirit": 15, "Researcher Spirit": 15}',
            '{"Educator Spirit": -5}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirits_registry (
            name, category, description, icon, unlock_rank, unlock_level, 
            max_spirit_level, tools, synergies, conflicts, is_active, 
            created_at, updated_at
        ) VALUES (
            'Healer Spirit',
            'Specialized & Advanced',
            'Health analysis, wellness advice, medical information',
            '🩺',
            'Master',
            2,
            10,
            '["symptom_analyzer", "wellness_tracker", "medication_reminder", "health_educator"]',
            '{"Educator Spirit": 20, "Communicator Spirit": 15, "Scheduler Spirit": 15}',
            '{"Analyst Spirit": -5}',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );

-- Insert Tools Registry
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'markdown_generator',
            'Content',
            'Generate clean markdown documentation',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'style_adapter',
            'Content',
            'Adapt writing style to match user preferences',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'grammar_checker',
            'Content',
            'Check grammar and language quality',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'plagiarism_detector',
            'Content',
            'Detect plagiarism and ensure originality',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'story_generator',
            'Creative',
            'Generate creative stories and narratives',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'mood_analyzer',
            'Creative',
            'Analyze emotional tone and mood',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'creative_prompts',
            'Creative',
            'Generate creative prompts and ideas',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'style_transfer',
            'Creative',
            'Transfer artistic styles to content',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'language_detector',
            'Translation',
            'Detect and identify languages',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'translation_engine',
            'Translation',
            'Multi-language translation engine',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'cultural_adapter',
            'Translation',
            'Adapt content for cultural context',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'pronunciation_guide',
            'Translation',
            'Provide pronunciation guidance',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'chroma_search',
            'Data',
            'Vector database search and retrieval',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'sql_connector',
            'Data',
            'Database connection and query execution',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'data_cleaner',
            'Data',
            'Clean and preprocess datasets',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'chart_generator',
            'Data',
            'Generate data visualizations and charts',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'web_search',
            'Research',
            'Real-time web information retrieval',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'fact_checker',
            'Research',
            'Verify facts and information accuracy',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'source_validator',
            'Research',
            'Validate source credibility',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'knowledge_synthesizer',
            'Research',
            'Synthesize and summarize information',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'calculator_engine',
            'Math',
            'Advanced mathematical computations',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'statistical_analyzer',
            'Math',
            'Statistical analysis and modeling',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'equation_solver',
            'Math',
            'Solve complex mathematical equations',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'graph_plotter',
            'Math',
            'Plot mathematical graphs and visualizations',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'file_writer',
            'Development',
            'Create and modify files',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'folder_manager',
            'Development',
            'Manage directory structures',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'code_generator',
            'Development',
            'Generate application code',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'docker_tool',
            'Development',
            'Build and manage Docker containers',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'error_analyzer',
            'Debug',
            'Analyze and identify errors',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'performance_profiler',
            'Debug',
            'Profile code performance',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'code_optimizer',
            'Debug',
            'Optimize code for better performance',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'security_scanner',
            'Debug',
            'Scan for security vulnerabilities',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'deployment_manager',
            'DevOps',
            'Manage application deployments',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'monitoring_tool',
            'DevOps',
            'Monitor system performance',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'backup_manager',
            'DevOps',
            'Manage data backups',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'scaling_advisor',
            'DevOps',
            'Provide scaling recommendations',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'openai_adapter',
            'Integration',
            'OpenAI API integration',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'anthropic_adapter',
            'Integration',
            'Anthropic API integration',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'nvidia_adapter',
            'Integration',
            'NVIDIA API integration',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'huggingface_adapter',
            'Integration',
            'Hugging Face API integration',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'email_manager',
            'Communication',
            'Manage email communications',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'sms_sender',
            'Communication',
            'Send SMS messages',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'social_media_poster',
            'Communication',
            'Post to social media platforms',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'notification_system',
            'Communication',
            'Send multi-channel notifications',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'calendar_manager',
            'Scheduling',
            'Manage calendars and events',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'task_scheduler',
            'Scheduling',
            'Schedule and manage tasks',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'reminder_system',
            'Scheduling',
            'Create and manage reminders',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'meeting_planner',
            'Scheduling',
            'Plan and coordinate meetings',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'test_runner',
            'Testing',
            'Run unit and integration tests',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'consistency_checker',
            'Testing',
            'Check output consistency',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'report_generator',
            'Testing',
            'Generate test reports',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'vulnerability_scanner',
            'Security',
            'Scan for security vulnerabilities',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'encryption_manager',
            'Security',
            'Manage data encryption',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'compliance_checker',
            'Security',
            'Check regulatory compliance',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'audit_logger',
            'Security',
            'Log security audit events',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'lesson_planner',
            'Education',
            'Plan educational lessons',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'quiz_generator',
            'Education',
            'Generate quizzes and assessments',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'progress_tracker',
            'Education',
            'Track learning progress',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'knowledge_assessor',
            'Education',
            'Assess knowledge gaps',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'layout_generator',
            'Design',
            'Generate UI layouts',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'color_palette_creator',
            'Design',
            'Create color palettes',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'ui_mockup_tool',
            'Design',
            'Create UI mockups',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'accessibility_checker',
            'Design',
            'Check accessibility compliance',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'business_analyzer',
            'Business',
            'Analyze business processes',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'strategy_planner',
            'Business',
            'Plan business strategies',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'risk_assessor',
            'Business',
            'Assess business risks',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'market_researcher',
            'Business',
            'Research market trends',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'symptom_analyzer',
            'Health',
            'Analyze health symptoms',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'wellness_tracker',
            'Health',
            'Track health and wellness',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'medication_reminder',
            'Health',
            'Manage medication reminders',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO tools_registry (
            name, category, description, is_active, created_at
        ) VALUES (
            'health_educator',
            'Health',
            'Provide health education',
            true,
            CURRENT_TIMESTAMP
        );

-- Insert Minion Templates
-- Note: These can be stored in a minion_templates table or as JSON config
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'CodeMaster Pro',
            'Development & Technical',
            '🚀',
            'Full-stack development with security focus',
            '["Builder Spirit", "Debugger Spirit", "Analyst Spirit", "Security Spirit", "Checker Spirit"]',
            25,
            -10,
            25,
            20,
            'Enterprise software development, secure coding',
            'Novice',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'DevOps Engineer',
            'Development & Technical',
            '⚙️',
            'Infrastructure automation and monitoring',
            '["DevOps Spirit", "Builder Spirit", "Analyst Spirit", "Scheduler Spirit", "Security Spirit"]',
            45,
            0,
            45,
            18,
            'CI/CD, infrastructure management, system administration',
            'Specialist',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Hybrid Developer',
            'Development & Technical',
            '🔄',
            'Full-stack development with creative problem-solving',
            '["Builder Spirit", "Creative Spirit", "Connector Spirit", "Debugger Spirit", "Checker Spirit"]',
            35,
            -5,
            30,
            22,
            'Startup development, rapid prototyping, creative coding',
            'Skilled',
            3,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Enterprise Architect',
            'Development & Technical',
            '🏗️',
            'Enterprise system architecture and strategy',
            '["DevOps Spirit", "Security Spirit", "Analyst Spirit", "Consultant Spirit", "Builder Spirit"]',
            45,
            0,
            45,
            21,
            'Enterprise architecture, system design, IT strategy',
            'Master',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Creative Assistant',
            'Content & Creative',
            '✨',
            'Content creation and education',
            '["Writer Spirit", "Creative Spirit", "Translator Spirit", "Communicator Spirit", "Educator Spirit"]',
            45,
            0,
            45,
            15,
            'Content marketing, education, storytelling',
            'Expert',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'SEO Pro',
            'Content & Creative',
            '🔍',
            'SEO optimization and content strategy',
            '["Researcher Spirit", "Writer Spirit", "Analyst Spirit", "Communicator Spirit", "Checker Spirit"]',
            50,
            0,
            50,
            16,
            'Digital marketing, SEO, content optimization',
            'Novice',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Marketing Master',
            'Content & Creative',
            '📈',
            'Multi-channel marketing and campaign management',
            '["Communicator Spirit", "Creative Spirit", "Analyst Spirit", "Scheduler Spirit", "Researcher Spirit"]',
            55,
            0,
            55,
            20,
            'Digital marketing, campaign management, brand strategy',
            'Skilled',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'UI/UX Designer',
            'Content & Creative',
            '🎨',
            'User interface and experience design',
            '["Designer Spirit", "Creative Spirit", "Builder Spirit", "Analyst Spirit", "Checker Spirit"]',
            50,
            -5,
            45,
            18,
            'Web design, mobile apps, user experience optimization',
            'Expert',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Research Analyst',
            'Data & Analysis',
            '📊',
            'Data analysis and research',
            '["Researcher Spirit", "Analyst Spirit", "Mathematician Spirit", "Checker Spirit", "Security Spirit"]',
            45,
            0,
            45,
            18,
            'Business intelligence, research, data science',
            'Skilled',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Data Scientist',
            'Data & Analysis',
            '🧮',
            'Advanced data analysis and machine learning',
            '["Mathematician Spirit", "Analyst Spirit", "Builder Spirit", "Researcher Spirit", "Checker Spirit"]',
            55,
            0,
            55,
            22,
            'Machine learning, statistical analysis, data engineering',
            'Specialist',
            3,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Monitoring Specialist',
            'Data & Analysis',
            '📊',
            'System monitoring and alerting',
            '["DevOps Spirit", "Analyst Spirit", "Scheduler Spirit", "Communicator Spirit", "Security Spirit"]',
            45,
            0,
            45,
            16,
            'System monitoring, incident management, performance tracking',
            'Specialist',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'API Integration Specialist',
            'Integration & Automation',
            '🌐',
            'API integration and system connectivity',
            '["Connector Spirit", "Builder Spirit", "Debugger Spirit", "Analyst Spirit", "Security Spirit"]',
            45,
            0,
            45,
            19,
            'System integration, API development, microservices',
            'Skilled',
            3,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Automation Expert',
            'Integration & Automation',
            '🤖',
            'Process automation and workflow optimization',
            '["Scheduler Spirit", "Builder Spirit", "Connector Spirit", "Analyst Spirit", "Checker Spirit"]',
            45,
            0,
            45,
            18,
            'Business process automation, workflow optimization',
            'Skilled',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Swiss Army Knife',
            'Integration & Automation',
            '⚡',
            'General-purpose problem solving',
            '["Builder Spirit", "Writer Spirit", "Analyst Spirit", "Connector Spirit", "Checker Spirit"]',
            35,
            0,
            35,
            20,
            'General assistance, prototyping, multi-task projects',
            'Novice',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Startup Accelerator',
            'Integration & Automation',
            '🚀',
            'Rapid development and business growth',
            '["Builder Spirit", "Communicator Spirit", "Analyst Spirit", "Creative Spirit", "Scheduler Spirit"]',
            45,
            -5,
            40,
            22,
            'Startup development, rapid prototyping, business acceleration',
            'Skilled',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Quality Assurance',
            'Quality & Security',
            '✅',
            'Comprehensive quality assurance and testing',
            '["Checker Spirit", "Security Spirit", "Analyst Spirit", "Debugger Spirit", "Communicator Spirit"]',
            45,
            0,
            45,
            17,
            'QA testing, security auditing, compliance',
            'Specialist',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Security Specialist',
            'Quality & Security',
            '🔒',
            'Cybersecurity and vulnerability assessment',
            '["Security Spirit", "Analyst Spirit", "Debugger Spirit", "Researcher Spirit", "Checker Spirit"]',
            45,
            0,
            45,
            19,
            'Cybersecurity, penetration testing, security auditing',
            'Specialist',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Business Consultant',
            'Specialized & Advanced',
            '💼',
            'Business consulting and strategy',
            '["Consultant Spirit", "Analyst Spirit", "Communicator Spirit", "Scheduler Spirit", "Educator Spirit"]',
            35,
            0,
            35,
            12,
            'Business consulting, strategic planning, decision support',
            'Master',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Educational Designer',
            'Specialized & Advanced',
            '📚',
            'Educational content design and delivery',
            '["Educator Spirit", "Designer Spirit", "Writer Spirit", "Analyst Spirit", "Communicator Spirit"]',
            45,
            0,
            45,
            15,
            'Online education, training development, instructional design',
            'Expert',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Health & Wellness Coach',
            'Specialized & Advanced',
            '🩺',
            'Health monitoring and wellness guidance',
            '["Healer Spirit", "Educator Spirit", "Communicator Spirit", "Scheduler Spirit", "Analyst Spirit"]',
            35,
            0,
            35,
            12,
            'Health coaching, wellness programs, medical information',
            'Master',
            2,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Global Communicator',
            'Multi-Language & Global',
            '🌍',
            'Multi-language communication and education',
            '["Translator Spirit", "Communicator Spirit", "Writer Spirit", "Researcher Spirit", "Educator Spirit"]',
            45,
            0,
            45,
            16,
            'International business, multilingual content, global education',
            'Expert',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Cultural Bridge',
            'Multi-Language & Global',
            '🌉',
            'Cross-cultural communication and adaptation',
            '["Translator Spirit", "Creative Spirit", "Communicator Spirit", "Researcher Spirit", "Consultant Spirit"]',
            35,
            0,
            35,
            14,
            'International relations, cultural consulting, global marketing',
            'Master',
            1,
            CURRENT_TIMESTAMP
        );
INSERT INTO minion_templates (
            name, category, icon, description, spirits, synergy_bonus, 
            conflict_penalty, net_performance, tools_count, perfect_for, 
            unlock_rank, unlock_level, created_at
        ) VALUES (
            'Brand Strategist',
            'Design & Creative',
            '🎯',
            'Brand development and strategic communication',
            '["Creative Spirit", "Communicator Spirit", "Analyst Spirit", "Researcher Spirit", "Consultant Spirit"]',
            55,
            0,
            55,
            17,
            'Brand development, marketing strategy, creative direction',
            'Master',
            1,
            CURRENT_TIMESTAMP
        );