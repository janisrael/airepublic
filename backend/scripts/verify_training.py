#!/usr/bin/env python3
"""
End-to-End Training Verification Script
Tests that RAG training works correctly and minion can answer questions about uploaded documents

Usage:
    python scripts/verify_training.py <minion_id> [test_questions...]

Example:
    python scripts/verify_training.py 17 "What is Google Keep?" "Tell me about the document"
"""

import sys
import os
import json
import requests
from typing import List, Dict, Any

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.postgres_connection import create_spirit_engine
from model.minion import ExternalAPIModel
from sqlalchemy.orm import sessionmaker

# Backend API URL
API_BASE_URL = "http://localhost:5001/api/v2"

def get_minion_from_db(minion_id: int) -> Dict[str, Any]:
    """Get minion details from database"""
    engine = create_spirit_engine()
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        minion = session.query(ExternalAPIModel).filter_by(id=minion_id).first()
        if not minion:
            return None
        
        return {
            'id': minion.id,
            'display_name': minion.display_name,
            'rag_enabled': getattr(minion, 'rag_enabled', False),
            'rag_collection_name': getattr(minion, 'rag_collection_name', None),
            'top_k': getattr(minion, 'top_k', 3),
            'similarity_threshold': getattr(minion, 'similarity_threshold', 0.7),
            'provider': minion.provider,
            'model_id': minion.model_id,
            'api_key': minion.api_key,
            'base_url': minion.base_url
        }

def test_chat_api(minion_id: int, question: str) -> Dict[str, Any]:
    """Test the chat API endpoint"""
    url = f"{API_BASE_URL}/external-models/chat"
    
    payload = {
        'model_id': minion_id,
        'message': question,
        'temperature': 0.7,
        'max_tokens': 1000
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e)
        }

def verify_training_effectiveness(minion_id: int, test_questions: List[str]):
    """Verify that training was effective by testing chat responses"""
    print(f"\n{'='*70}")
    print(f"🧪 VERIFYING TRAINING EFFECTIVENESS FOR MINION #{minion_id}")
    print(f"{'='*70}\n")
    
    # Step 1: Check minion configuration
    print("📋 Step 1: Checking Minion Configuration")
    print("-" * 70)
    minion = get_minion_from_db(minion_id)
    
    if not minion:
        print(f"❌ Minion #{minion_id} not found in database!")
        return False
    
    print(f"✅ Minion Found: {minion['display_name']}")
    print(f"   Provider: {minion['provider']}")
    print(f"   Model ID: {minion['model_id']}")
    print(f"   API Key: {'✅ Configured' if minion['api_key'] else '❌ Missing'}")
    print(f"   Base URL: {minion['base_url'] or 'Not set'}")
    
    # Step 2: Check RAG Configuration
    print(f"\n📚 Step 2: Checking RAG Configuration")
    print("-" * 70)
    
    if not minion['rag_enabled']:
        print(f"❌ RAG is NOT enabled for this minion!")
        print(f"   The minion has not been trained with RAG yet.")
        return False
    
    print(f"✅ RAG Enabled: True")
    print(f"   Collection Name: {minion['rag_collection_name']}")
    print(f"   Top K: {minion['top_k']}")
    print(f"   Similarity Threshold: {minion['similarity_threshold']}")
    
    # Step 3: Test Chat API
    print(f"\n💬 Step 3: Testing Chat API with Document Questions")
    print("-" * 70)
    
    if not test_questions:
        test_questions = [
            "What is Google Keep?",
            "Tell me about the document you were trained on",
            "What information do you have about Google Keep?"
        ]
    
    all_passed = True
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}/{len(test_questions)}: {question}")
        print("-" * 70)
        
        result = test_chat_api(minion_id, question)
        
        if not result.get('success', False):
            print(f"❌ API Call Failed: {result.get('error', 'Unknown error')}")
            all_passed = False
            continue
        
        response = result.get('response', '')
        rag_used = result.get('rag_used', False)
        used_config = result.get('used_config', {})
        
        print(f"✅ Response Received:")
        print(f"   RAG Used: {'✅ Yes' if rag_used else '❌ No'}")
        print(f"   Collection: {used_config.get('collection_name', 'N/A')}")
        print(f"   Response Length: {len(response)} characters")
        print(f"\n📝 Response Preview:")
        print(f"   {response[:200]}{'...' if len(response) > 200 else ''}")
        
        # Check if response seems knowledgeable
        if rag_used:
            print(f"   ✅ Knowledge base was queried")
        else:
            print(f"   ⚠️ Warning: RAG was not used in this response")
            all_passed = False
    
    # Step 4: Summary
    print(f"\n{'='*70}")
    print(f"📊 VERIFICATION SUMMARY")
    print(f"{'='*70}\n")
    
    if all_passed:
        print(f"✅ All tests passed! Training appears to be effective.")
        print(f"   The minion can answer questions using the knowledge base.")
    else:
        print(f"⚠️ Some tests failed. Please check:")
        print(f"   1. Is the minion's API key configured correctly?")
        print(f"   2. Was the training job completed successfully?")
        print(f"   3. Does the ChromaDB collection exist?")
        print(f"   4. Are there any errors in the backend logs?")
    
    return all_passed

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_training.py <minion_id> [test_questions...]")
        print("\nExample:")
        print('  python scripts/verify_training.py 17 "What is Google Keep?"')
        sys.exit(1)
    
    try:
        minion_id = int(sys.argv[1])
        test_questions = sys.argv[2:] if len(sys.argv) > 2 else []
        
        success = verify_training_effectiveness(minion_id, test_questions)
        sys.exit(0 if success else 1)
        
    except ValueError:
        print(f"❌ Invalid minion ID: {sys.argv[1]}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

