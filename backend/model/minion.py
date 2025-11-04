"""
Minion system models for AI Refinement Dashboard
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class ExternalAPIModel(Base):
    """External API model (Minion) - combines model configuration with user profile"""
    
    __tablename__ = "external_api_models"
    
    # User ownership
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Model configuration
    name = Column(String(255), nullable=False)  # Technical model name
    display_name = Column(String(255), nullable=False)  # User-friendly name
    provider = Column(String(255), nullable=False)  # e.g., 'openai', 'anthropic', 'nvidia'
    model_id = Column(String(255), nullable=False)  # Specific model identifier
    api_key = Column(String(500))  # Encrypted API key
    base_url = Column(String(500))  # API endpoint URL (matches database schema)
    model_type = Column(String(100))  # Model type (e.g., 'external', 'local')
    max_tokens = Column(Integer, default=4096)  # Maximum tokens
    temperature = Column(Float, default=0.7)  # Temperature setting
    top_p = Column(Float, default=0.9)  # Top-p setting
    context_length = Column(Integer)  # Context length
    capabilities = Column(String(1000))  # Model capabilities
    parameters = Column(String(1000))  # Model parameters
    model_metadata = Column('metadata', String(1000))  # Additional metadata (maps to 'metadata' column)
    
    # Minion profile
    avatar_url = Column(String(500))
    avatar_path = Column(String(500))
    description = Column(Text)
    title = Column(String(255), default='AI Assistant')  # Minion title/role
    company = Column(String(255), default='AI Republic')  # Company affiliation
    theme_color = Column(String(7), default='#4f46e5')  # Theme color (hex)
    system_prompt = Column(Text)
    tags = Column(String(1000))  # Tags as string (matches database schema)
    
    # XP and Ranking System
    level = Column(Integer, default=1, nullable=False)
    rank = Column(String(100), default='Novice', nullable=False)
    rank_level = Column(Integer, default=1, nullable=False)
    total_training_xp = Column(Integer, default=0, nullable=False)
    total_usage_xp = Column(Integer, default=0, nullable=False)
    xp_to_next_level = Column(Integer, default=100, nullable=False)
    last_training_xp = Column(Integer, default=0, nullable=False)
    level_up_count = Column(Integer, default=0, nullable=False)
    rank_up_count = Column(Integer, default=0, nullable=False)
    skillset_mastery = Column(JSON)  # Skillset mastery levels
    unlocked_tools = Column(JSON)  # Unlocked LangChain tools
    
    # Score System
    score = Column(Integer, default=0, nullable=False)
    score_breakdown = Column(Text)  # JSON string with score components
    
    # Minion token system
    minion_token = Column(String(255), unique=True, index=True)
    
    # RAG Configuration (applied after training)
    rag_enabled = Column(Boolean, default=False, nullable=False)
    rag_collection_name = Column(String(255))  # ChromaDB collection name
    top_k = Column(Integer, default=5)  # Number of documents to retrieve
    similarity_threshold = Column(Float, default=0.7)  # Similarity threshold
    retrieval_method = Column(String(50), default='semantic')  # semantic, keyword, hybrid
    enable_contextual_compression = Column(Boolean, default=False)
    enable_source_citation = Column(Boolean, default=False)
    enable_query_expansion = Column(Boolean, default=False)
    embedding_model = Column(String(100), default='all-MiniLM-L6-v2')
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=100)
    
    # LoRA Configuration (applied after training)
    lora_enabled = Column(Boolean, default=False, nullable=False)
    lora_rank = Column(Integer, default=16)
    lora_alpha = Column(Float, default=32.0)
    lora_dropout = Column(Float, default=0.1)
    lora_target_modules = Column(JSON)  # Target modules for LoRA
    
    # Spirit Orchestration Configuration
    spirits_enabled = Column(Boolean, default=False, nullable=False)  # Enable Spirit Orchestrator
    
    # Minion class
    class_name = Column(String(100))  # Minion class (e.g., 'Planner', 'Marketing', etc.)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Unique constraint: display_name must be unique per user
    __table_args__ = (
        UniqueConstraint('user_id', 'display_name', name='uq_user_display_name'),
    )
    
    # Relationships
    user = relationship("User", back_populates="minions")
    training_jobs = relationship("ExternalTrainingJob", back_populates="minion", cascade="all, delete-orphan")
    # Training results history for this minion
    training_results = relationship("TrainingResult", back_populates="minion", cascade="all, delete-orphan")
    profiles = relationship("Profile", back_populates="minion", cascade="all, delete-orphan")

class Minion(Base):
    """Legacy minion model - kept for compatibility"""
    
    __tablename__ = "minions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    avatar_url = Column(String(500))
    avatar_path = Column(String(500))
    system_prompt = Column(Text)
    capabilities = Column(JSON)
    tags = Column(JSON)
    config = Column(JSON)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # XP and Ranking System
    level = Column(Integer, default=1, nullable=False)
    rank = Column(String(100), default='Novice', nullable=False)
    rank_level = Column(Integer, default=1, nullable=False)
    total_training_xp = Column(Integer, default=0, nullable=False)
    total_usage_xp = Column(Integer, default=0, nullable=False)
    xp_to_next_level = Column(Integer, default=100, nullable=False)
    last_training_xp = Column(Integer, default=0, nullable=False)
    level_up_count = Column(Integer, default=0, nullable=False)
    rank_up_count = Column(Integer, default=0, nullable=False)
    skillset_mastery = Column(JSON)
    unlocked_tools = Column(JSON)
    
    # Minion token system
    minion_token = Column(String(255), unique=True, index=True)
    token_created_at = Column(DateTime, default=datetime.utcnow)
    token_last_used = Column(DateTime)
    
    # Usage statistics
    total_requests = Column(Integer, default=0, nullable=False)
    total_tokens_used = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    profiles = relationship("Profile", back_populates="legacy_minion", cascade="all, delete-orphan")

class Profile(Base):
    """Minion profile model for character customization"""
    
    __tablename__ = "profiles"
    
    minion_id = Column(Integer, ForeignKey("external_api_models.id", ondelete="CASCADE"), nullable=False)
    legacy_minion_id = Column(Integer, ForeignKey("minions.id", ondelete="CASCADE"))
    
    # Profile information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    avatar_url = Column(String(500))
    avatar_path = Column(String(500))
    
    # Character traits
    personality = Column(JSON)  # Personality traits and characteristics
    background = Column(Text)  # Character background story
    expertise = Column(JSON)  # Areas of expertise
    communication_style = Column(JSON)  # How the minion communicates
    
    # Customization
    custom_prompts = Column(JSON)  # Custom prompt templates
    response_filters = Column(JSON)  # Response filtering rules
    behavior_rules = Column(JSON)  # Behavioral guidelines
    
    # Profile metadata
    version = Column(String(50), default="1.0")
    is_default = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    minion = relationship("ExternalAPIModel", back_populates="profiles", foreign_keys=[minion_id])
    legacy_minion = relationship("Minion", back_populates="profiles", foreign_keys=[legacy_minion_id])


class TraitsLoadout(Base):
    """Traits loadout for minions - separate table for traits system"""
    
    __tablename__ = "traits_loadout"
    
    id = Column(Integer, primary_key=True)
    minion_id = Column(Integer, ForeignKey("external_api_models.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Traits system fields
    slots = Column(Integer, default=0)  # Available trait slots
    points_available = Column(Integer, default=10)  # Available trait points
    points_spent = Column(Integer, default=0)  # Spent trait points
    trait_intensities = Column(JSON, default=dict)  # {trait_name: intensity_value}
    compatibility_score = Column(DECIMAL(5, 2), default=0.00)  # Trait compatibility score
    effectiveness_bonus = Column(DECIMAL(5, 2), default=0.00)  # Effectiveness bonus from synergies
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    minion = relationship("ExternalAPIModel", backref="traits_loadout")
