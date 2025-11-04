#!/usr/bin/env python3
"""
Add sample datasets to test the dual dataset system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker
from model.dataset import Dataset
from datetime import datetime

def add_sample_datasets():
    """Add sample global and user datasets"""
    
    # Create database connection
    engine = create_spirit_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Sample global datasets (admin-provided, free for all)
        global_datasets = [
            {
                'name': 'General Knowledge Base',
                'description': 'Comprehensive general knowledge dataset for RAG training',
                'dataset_type': 'text',
                'format': 'json',
                'file_path': '/datasets/global/general_knowledge.json',
                'file_size': 52428800,  # 50MB
                'total_items': 10000,
                'processed_items': 10000,
                'quality_score': 95.0,
                'processing_status': 'completed',
                'is_active': True,
                'is_public': True,
                'is_verified': True,
                'usage_count': 150,
                'tags': ['general', 'knowledge', 'rag', 'free'],
                'version': '1.0',
                'user_id': None  # Global dataset
            },
            {
                'name': 'Code Examples Dataset',
                'description': 'Programming code examples and documentation',
                'dataset_type': 'code',
                'format': 'json',
                'file_path': '/datasets/global/code_examples.json',
                'file_size': 31457280,  # 30MB
                'total_items': 5000,
                'processed_items': 5000,
                'quality_score': 88.0,
                'processing_status': 'completed',
                'is_active': True,
                'is_public': True,
                'is_verified': True,
                'usage_count': 75,
                'tags': ['programming', 'code', 'examples', 'free'],
                'version': '1.0',
                'user_id': None  # Global dataset
            },
            {
                'name': 'Technical Documentation',
                'description': 'Technical documentation and API references',
                'dataset_type': 'text',
                'format': 'json',
                'file_path': '/datasets/global/tech_docs.json',
                'file_size': 41943040,  # 40MB
                'total_items': 8000,
                'processed_items': 8000,
                'quality_score': 92.0,
                'processing_status': 'completed',
                'is_active': True,
                'is_public': True,
                'is_verified': True,
                'usage_count': 120,
                'tags': ['technical', 'documentation', 'api', 'free'],
                'version': '1.0',
                'user_id': None  # Global dataset
            }
        ]
        
        # Sample user datasets (user-specific)
        user_datasets = [
            {
                'name': 'My Personal Notes',
                'description': 'Personal notes and observations for custom training',
                'dataset_type': 'text',
                'format': 'json',
                'file_path': '/datasets/user/2/personal_notes.json',
                'file_size': 1048576,  # 1MB
                'total_items': 500,
                'processed_items': 500,
                'quality_score': 75.0,
                'processing_status': 'completed',
                'is_active': True,
                'is_public': False,
                'is_verified': False,
                'usage_count': 5,
                'tags': ['personal', 'notes', 'private'],
                'version': '1.0',
                'user_id': 2  # User-specific dataset
            },
            {
                'name': 'Project Documentation',
                'description': 'Documentation for my specific project',
                'dataset_type': 'text',
                'format': 'json',
                'file_path': '/datasets/user/2/project_docs.json',
                'file_size': 2097152,  # 2MB
                'total_items': 1000,
                'processed_items': 1000,
                'quality_score': 80.0,
                'processing_status': 'completed',
                'is_active': True,
                'is_public': False,
                'is_verified': False,
                'usage_count': 3,
                'tags': ['project', 'documentation', 'private'],
                'version': '1.0',
                'user_id': 2  # User-specific dataset
            }
        ]
        
        # Add global datasets
        print("Adding global datasets...")
        for dataset_data in global_datasets:
            dataset = Dataset(**dataset_data)
            session.add(dataset)
            print(f"  ✅ Added global dataset: {dataset_data['name']}")
        
        # Add user datasets
        print("Adding user datasets...")
        for dataset_data in user_datasets:
            dataset = Dataset(**dataset_data)
            session.add(dataset)
            print(f"  ✅ Added user dataset: {dataset_data['name']}")
        
        # Commit all changes
        session.commit()
        print(f"\n🎉 Successfully added {len(global_datasets)} global datasets and {len(user_datasets)} user datasets!")
        
    except Exception as e:
        print(f"❌ Error adding datasets: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    add_sample_datasets()
