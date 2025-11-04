"""
Reference Models SQLAlchemy Model
Defines the database schema for reference models (public templates)
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, DECIMAL, JSON
from sqlalchemy.sql import func
from .base import Base

class ReferenceModel(Base):
    """Reference Models table - public models anyone can use for minion creation"""
    __tablename__ = 'reference_models'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255))
    description = Column(Text)
    title = Column(String(255), default='AI Assistant')  # Minion title/role
    company = Column(String(255), default='AI Republic')  # Company affiliation
    theme_color = Column(String(7), default='#4f46e5')  # Theme color (hex)
    model_type = Column(String(50), nullable=False)  # coding, chat, etc.
    provider = Column(String(100), nullable=False)  # nvidia, openai, anthropic, etc.
    model_id = Column(String(255), nullable=False)  # moonshotai/kimi-k2-instruct-0905, gpt-4, etc.
    api_key = Column(Text)  # encrypted or reference to key management
    base_url = Column(String(500))  # custom API endpoint
    temperature = Column(DECIMAL(3, 2), default=0.6)
    top_p = Column(DECIMAL(3, 2), default=0.9)
    max_tokens = Column(Integer, default=4096)
    stream = Column(Boolean, default=True)
    capabilities = Column(JSON, default=[])  # JSON array
    parameters = Column(JSON, default={})  # JSON object with model specs
    context_length = Column(Integer)
    system_prompt = Column(Text)
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)
    tags = Column(JSON, default=[])  # JSON array
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
