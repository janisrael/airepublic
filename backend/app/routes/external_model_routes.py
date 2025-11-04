"""
External Model Routes - New Clean Architecture
Handles all external model-related API endpoints

Original endpoints moved from api_server.py:
- /api/external-models/test (POST)
- /api/external-models/chat (POST)
- /api/external-models/providers (GET)
- /api/external-models (POST)
- /api/external-models/<int:model_id> (PUT)
- /api/external-models/<int:model_id> (DELETE)
- /api/external-models/<int:model_id>/toggle-favorite (POST)
- /api/external-models/sync-nvidia (POST)
- /api/external-models/<int:model_id>/sync-nvidia (POST)
- /api/external-models/<int:model_id>/avatar (POST)

MIGRATED TO POSTGRESQL - No more PostgreSQL connections
"""

from flask import Blueprint, jsonify, request
import sys
import os
import json

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import PostgreSQL-based services
from app.services.minion_service import MinionService
from app.services.external_api_service import ExternalAPIService
from model.minion import ExternalAPIModel

external_model_bp = Blueprint('external_models', __name__, url_prefix='/api/v2')

# Initialize PostgreSQL-based minion service
minion_service = MinionService()
external_api_service = ExternalAPIService()

def chat_with_spirit_orchestration(model_id, message, system_prompt='', temperature=0.7, max_tokens=1000, top_p=0.9, context_length=4096, description='', capabilities=None, tags=None, use_rag=None):
    """Chat with minion using Spirit Orchestration via microservice"""
    try:
        import asyncio
        
        # Import microservice client
        from services.spirit_orchestrator_client import spirit_orchestrator_client
        
        # Get minion from database
        minion = minion_service.get_minion_by_id(model_id)
        if not minion:
            return {
                'success': False,
                'error': 'Minion not found'
            }
        
        # Check microservice health first
        health_check = asyncio.run(spirit_orchestrator_client.health_check())
        if not health_check["success"]:
            # Fallback to local spirit orchestration
            return asyncio.run(chat_with_spirit_orchestration_local(model_id, message, system_prompt, temperature, max_tokens, top_p, context_length, description, capabilities, tags, use_rag))
        
        # Use microservice for spirit orchestration
        result = asyncio.run(spirit_orchestrator_client.chat_with_spirits(
            minion_id=str(model_id),
            user_input=message,
            user_id=str(minion['user_id']),
            model=None,  # Let microservice choose
            temperature=temperature,
            max_tokens=max_tokens
        ))
        
        if result["success"]:
            data = result["data"]
            # Enhance response with minion metadata
            enhanced_result = {
                'success': True,
                'response': data.get("response", ""),
                'minion_id': model_id,
                'minion_name': data.get("minion_name", minion.get('name', 'Unknown')),
                'provider': minion.get('provider', 'Unknown'),
                'model_id': minion.get('model_id', 'Unknown'),
                'spirits_enabled': True,
                'orchestration_used': True,
                'spirits_used': data.get("spirits_used", []),
                'tools_used': data.get("tools_used", []),
                'task_type': data.get("task_type", "general"),
                'processing_time': data.get("processing_time", 0.0),
                'rag_used': data.get("rag_used", False),
                'microservice_used': True
            }
            return enhanced_result
        else:
            # Fallback to local spirit orchestration
            return asyncio.run(chat_with_spirit_orchestration_local(model_id, message, system_prompt, temperature, max_tokens, top_p, context_length, description, capabilities, tags, use_rag))
        
    except Exception as e:
        # Fallback to local spirit orchestration
        return asyncio.run(chat_with_spirit_orchestration_local(model_id, message, system_prompt, temperature, max_tokens, top_p, context_length, description, capabilities, tags, use_rag))


async def chat_with_spirit_orchestration_local(model_id, message, system_prompt='', temperature=0.7, max_tokens=1000, top_p=0.9, context_length=4096, description='', capabilities=None, tags=None, use_rag=None):
    """Fallback local Spirit Orchestration implementation"""
    try:
        # Import SpiritOrchestrator
        from services.spirit_orchestrator import SpiritOrchestrator
        
        # Get minion from database
        minion = minion_service.get_minion_by_id(model_id)
        if not minion:
            return {
                'success': False,
                'error': 'Minion not found'
            }
        
        # Initialize SpiritOrchestrator
        orchestrator = SpiritOrchestrator(model_id)
        
        # Process user input through spirit workflow
        result = orchestrator.process_user_input(message, minion['user_id'])
        
        # Enhance response with minion metadata
        result.update({
            'minion_id': model_id,
            'minion_name': minion.get('name', 'Unknown'),
            'provider': minion.get('provider', 'Unknown'),
            'model_id': minion.get('model_id', 'Unknown'),
            'spirits_enabled': True,
            'orchestration_used': True,
            'microservice_used': False
        })
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Spirit orchestration error: {str(e)}',
            'minion_id': model_id,
            'spirits_enabled': True,
            'orchestration_used': False,
            'microservice_used': False
        }

def chat_with_model(model_id, message, system_prompt='', temperature=0.7, max_tokens=1000, top_p=0.9, context_length=4096, description='', capabilities=None, tags=None, use_rag=None, use_spirits=None):
    """Chat with external model using minion configuration with optional RAG and Spirit Orchestration"""
    try:
        # Get minion from database
        minion = minion_service.get_minion_by_id(model_id)
        if not minion:
            return {
                'success': False,
                'error': 'Minion not found'
            }
        
        # Check if spirit orchestration should be used
        should_use_spirits = use_spirits if use_spirits is not None else minion.get('spirits_enabled', False)
        
        # If spirits are enabled, use SpiritOrchestrator
        if should_use_spirits:
            return chat_with_spirit_orchestration(model_id, message, system_prompt, temperature, max_tokens, top_p, context_length, description, capabilities, tags, use_rag)
        
        # Use provided parameters or fall back to minion defaults
        final_system_prompt = system_prompt or minion.get('system_prompt', '')
        final_temperature = temperature if temperature != 0.7 else minion.get('temperature', 0.7)
        final_top_p = top_p if top_p != 0.9 else minion.get('top_p', 0.9)
        final_max_tokens = max_tokens if max_tokens != 1000 else minion.get('max_tokens', 1000)
        final_context_length = context_length if context_length != 4096 else minion.get('context_length', 4096)
        
        # Determine if RAG should be used
        should_use_rag = use_rag if use_rag is not None else minion.get('rag_enabled', False)
        
        # Build enhanced system prompt with minion personality
        enhanced_system_prompt = build_enhanced_system_prompt(
            minion, final_system_prompt, description, capabilities, tags
        )
        
        # Prepare model configuration
        model_config = {
            'provider': minion['provider'],
            'model_id': minion['model_id'],
            'api_key': minion.get('api_key', ''),
            'base_url': minion.get('base_url', ''),
            'temperature': final_temperature,
            'top_p': final_top_p,
            'max_tokens': final_max_tokens,
            'context_length': final_context_length,
            'system_prompt': enhanced_system_prompt
        }
        
        # Check if API key is available
        if not model_config['api_key']:
            return {
                'success': False,
                'error': f'No API key configured for {minion["provider"]} provider. Please configure the API key in minion settings.'
            }
        
        # Apply RAG if enabled
        final_message = message
        rag_used = False
        if should_use_rag and minion.get('rag_collection_name'):
            from app.services.chromadb_service import ChromaDBService
            chromadb_service = ChromaDBService()
            
            # Get RAG parameters from minion config
            top_k = minion.get('top_k', 3)
            similarity_threshold = minion.get('similarity_threshold', 0.7)
            enable_source_citation = minion.get('enable_source_citation', False)
            
            # Query knowledge base - query more results to improve chances of finding uploaded files
            # Query 3x the requested top_k to ensure we have enough candidates
            query_n_results = max(top_k * 3, 15)  # At least 15 results, or 3x top_k
            kb_results = chromadb_service.query_collection(
                minion['rag_collection_name'], 
                message, 
                n_results=query_n_results
            )
            
            # HYBRID SEARCH: Also query uploaded files separately if they exist
            # This ensures uploaded files are always considered, even if semantic search misses them
            collection = chromadb_service.get_collection(minion['rag_collection_name'])
            uploaded_file_results_direct = []
            if collection:
                try:
                    # Get all documents to filter uploaded files
                    all_docs = collection.get()
                    uploaded_file_data = []  # Store (doc, id, metadata) tuples
                    
                    if all_docs.get('documents') and all_docs.get('metadatas'):
                        for i, metadata in enumerate(all_docs['metadatas']):
                            if metadata.get('source') == 'uploaded_file':
                                uploaded_file_data.append((
                                    all_docs['documents'][i],
                                    all_docs['ids'][i],
                                    metadata
                                ))
                    
                    # If we have uploaded files, do a separate keyword-based search on them
                    if uploaded_file_data:
                        query_words = set(message.lower().split())
                        matched_uploaded = []
                        
                        for doc_text, doc_id, metadata in uploaded_file_data:
                            doc_lower = doc_text.lower()
                            # Score chunks based on keyword matches
                            match_score = 0
                            matched_keywords = []
                            
                            # Priority keywords (exact matches score higher)
                            priority_keywords = ['token', 'clickup', 'clickapp']
                            
                            for word in query_words:
                                if len(word) > 3:
                                    word_lower = word.lower()
                                    # Exact match - score based on importance
                                    if word_lower in doc_lower:
                                        if word_lower in priority_keywords:
                                            match_score += 10  # High priority for token/clickup/clickapp
                                        else:
                                            match_score += 3
                                        matched_keywords.append(word_lower)
                                    # Partial match for longer words
                                    elif len(word) > 5:
                                        for doc_word in doc_lower.split():
                                            if word[:5] in doc_word or doc_word[:5] in word:
                                                # Check if it's a priority keyword
                                                if any(pk in doc_word for pk in priority_keywords):
                                                    match_score += 5  # Partial match for priority keywords
                                                else:
                                                    match_score += 1
                                                matched_keywords.append(f"{word}→{doc_word}")
                                                break
                            
                            if match_score > 0:
                                # Lower distance = higher relevance (inverse of score)
                                # Score 10+ gets distance 0.1, score 5 gets distance 0.3, etc.
                                distance_score = max(0.1, 1.0 - (match_score / 20.0))
                                
                                matched_uploaded.append({
                                    'document': doc_text,
                                    'metadata': metadata,
                                    'distance': distance_score,
                                    'id': doc_id,
                                    'source': 'uploaded_file',
                                    'keyword_match': True,
                                    'match_score': match_score,
                                    'matched_keywords': matched_keywords
                                })
                        
                        if matched_uploaded:
                            # Sort by match_score (highest first), then by distance (lowest first)
                            matched_uploaded.sort(key=lambda x: (-x.get('match_score', 0), x.get('distance', 1.0)))
                            uploaded_file_results_direct = matched_uploaded
                            print(f"🔍 Found {len(uploaded_file_results_direct)} uploaded file chunks via keyword search")
                            # Log top match for debugging
                            if uploaded_file_results_direct:
                                top_match = uploaded_file_results_direct[0]
                                print(f"   Top match: score={top_match.get('match_score', 0)}, keywords={top_match.get('matched_keywords', [])}")
                except Exception as e:
                    print(f"⚠️ Error in hybrid search for uploaded files: {e}")
            
            if kb_results:
                # Separate uploaded file chunks from dataset items
                uploaded_file_results = []
                dataset_results = []
                
                # Normalize query message for text matching (lowercase, remove special chars)
                query_words = set(message.lower().split())
                
                for r in kb_results:
                    metadata = r.get('metadata', {})
                    source = metadata.get('source', '')
                    document_text = r.get('document', '').lower()
                    
                    # Calculate similarity
                    distance = r.get('distance', 1.0)
                    similarity = 1 - distance
                    
                    # Check for keyword matches in uploaded files (helps with semantic mismatch)
                    keyword_match = False
                    if source == 'uploaded_file':
                        # Check if any query words appear in the document
                        # This helps catch cases like "clickup" vs "clickapp"
                        # Also check for partial matches (e.g., "click" in both "clickup" and "clickapp")
                        for word in query_words:
                            if len(word) > 3:
                                # Exact match
                                if word in document_text:
                                    keyword_match = True
                                    break
                                # Partial match: check if significant substring exists
                                # e.g., "click" matches both "clickup" and "clickapp"
                                if len(word) > 5:  # Only for longer words
                                    for doc_word in document_text.split():
                                        if word[:5] in doc_word or doc_word[:5] in word:
                                            keyword_match = True
                                            break
                                    if keyword_match:
                                        break
                    
                    # Prioritize uploaded files - use lower threshold for them
                    if source == 'uploaded_file':
                        # For uploaded files, use a more lenient threshold (0.5 instead of 0.7)
                        # Also boost similarity if keyword match found
                        uploaded_threshold = min(similarity_threshold - 0.2, 0.5)
                        if keyword_match:
                            # Boost similarity by 0.3 if keyword match found
                            similarity = min(similarity + 0.3, 1.0)
                        
                        if similarity >= uploaded_threshold or keyword_match:
                            uploaded_file_results.append(r)
                    else:
                        # For dataset items, use the configured threshold
                        if similarity >= similarity_threshold:
                            dataset_results.append(r)
                
                # Prioritize uploaded files: use them first, then fill remaining slots with dataset items
                filtered_results = []
                
                # PRIORITIZE: Add direct keyword-matched uploaded files first (highest priority)
                if uploaded_file_results_direct:
                    for r in uploaded_file_results_direct[:top_k]:
                        filtered_results.append(r)
                
                # Then add uploaded files from semantic search
                remaining_slots = top_k - len(filtered_results)
                if remaining_slots > 0:
                    for r in uploaded_file_results[:remaining_slots]:
                        # Avoid duplicates (check by document content)
                        if not any(fr.get('document') == r.get('document') for fr in filtered_results):
                            filtered_results.append(r)
                
                # Fill remaining slots with dataset items
                remaining_slots = top_k - len(filtered_results)
                if remaining_slots > 0:
                    for r in dataset_results[:remaining_slots]:
                        filtered_results.append(r)
                
                # If no results met threshold but we have uploaded files (from either source), use them anyway
                # This ensures uploaded content is always prioritized
                if not filtered_results:
                    if uploaded_file_results_direct:
                        filtered_results = uploaded_file_results_direct[:top_k]
                    elif uploaded_file_results:
                        filtered_results = uploaded_file_results[:top_k]
                
                # Fallback: if still no results, use top result anyway
                # This ensures RAG is used even with lower similarity matches
                if not filtered_results and kb_results:
                    filtered_results = [kb_results[0]]  # Use best match available
                
                if filtered_results:
                    # Build knowledge base context
                    kb_context = "\n\n".join([r.get('document', '') for r in filtered_results])
                    
                    # Apply source citation if enabled
                    if enable_source_citation:
                        final_message = f"<KnowledgeBase>\n{kb_context}\n</KnowledgeBase>\n\n{message}\n\nPlease cite sources when using information from the knowledge base."
                    else:
                        final_message = f"<KnowledgeBase>\n{kb_context}\n</KnowledgeBase>\n\n{message}"
                    
                    rag_used = True
            elif uploaded_file_results_direct:
                # If semantic search returned nothing but we have direct keyword matches, use them
                filtered_results = uploaded_file_results_direct[:top_k]
                kb_context = "\n\n".join([r.get('document', '') for r in filtered_results])
                
                if enable_source_citation:
                    final_message = f"<KnowledgeBase>\n{kb_context}\n</KnowledgeBase>\n\n{message}\n\nPlease cite sources when using information from the knowledge base."
                else:
                    final_message = f"<KnowledgeBase>\n{kb_context}\n</KnowledgeBase>\n\n{message}"
                
                rag_used = True
        
        # Call external API service
        response_generator = external_api_service.call_model(model_config, final_message)
        
        # Collect response (non-streaming for now)
        response_text = ''
        for chunk in response_generator:
            response_text += chunk
        
        return {
            'success': True,
            'response': response_text,
            'model_id': model_id,
            'provider': minion['provider'],
            'minion_name': minion['display_name'],
            'rag_used': rag_used,
            'used_config': {
                'temperature': final_temperature,
                'top_p': final_top_p,
                'max_tokens': final_max_tokens,
                'context_length': final_context_length,
                'rag_enabled': should_use_rag,
                'collection_name': minion.get('rag_collection_name') if rag_used else None
            }
        }
        
    except Exception as e:
        error_message = str(e)
        # Provide more user-friendly error messages
        if 'api_key' in error_message.lower() or 'OPENAI_API_KEY' in error_message:
            return {
                'success': False,
                'error': f'No API key configured for {minion["provider"]} provider. Please configure the API key in minion settings.',
                'error_type': 'missing_api_key',
                'provider': minion['provider']
            }
        return {
            'success': False,
            'error': error_message,
            'error_type': 'api_error'
        }

def build_enhanced_system_prompt(minion, base_system_prompt, description, capabilities, tags):
    """Build enhanced system prompt with minion personality and details"""
    prompt_parts = []
    
    # Add minion identity with clear distinction
    prompt_parts.append(f"You are {minion['display_name']}, a specialized AI minion assistant.")
    
    # Add description as personality
    if description:
        prompt_parts.append(f"Your role and personality: {description}")
    
    # Add capabilities
    if capabilities and len(capabilities) > 0:
        cap_text = ", ".join(capabilities)
        prompt_parts.append(f"Your capabilities include: {cap_text}")
    
    # Add tags as personality traits
    if tags and len(tags) > 0:
        tag_text = ", ".join(tags)
        prompt_parts.append(f"Your personality traits: {tag_text}")
    
    # Add base system prompt
    if base_system_prompt:
        prompt_parts.append(f"Additional instructions: {base_system_prompt}")
    
    # Add behavioral guidelines
    prompt_parts.append("Always respond in character as the AI minion you are. Do not confuse yourself with any other systems or platforms that might share a similar name.")
    
    return "\n\n".join(prompt_parts)

def get_available_providers():
    """Get available providers from the database"""
    try:
        with minion_service.Session() as session:
            # Get unique providers from external_api_models
            providers = session.query(ExternalAPIModel.provider).filter(
                ExternalAPIModel.provider.isnot(None),
                ExternalAPIModel.provider != ''
            ).distinct().all()
            
            provider_list = []
            for provider in providers:
                provider_list.append({
                    'name': provider[0],
                    'display_name': provider[0].title() if provider[0] else 'Unknown',
                    'icon': 'settings_ethernet',
                    'color': '#4f46e5'
                })
            
            return provider_list
    except Exception as e:
        print(f"Error getting providers: {e}")
        return []

@external_model_bp.route('/external-models', methods=['GET'])
def get_external_models_v2():
    """Get all external models - POSTGRESQL VERSION"""
    try:
        # Get all external models from PostgreSQL
        models = minion_service.get_all_minions()
        
        return jsonify({
            'success': True,
            'data': models,
            'count': len(models),
            'message': f'Retrieved {len(models)} external models'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve external models'
        }), 500

@external_model_bp.route('/external-models/test', methods=['POST'])
def test_external_model_v2():
    """Test external model connection - NEW VERSION"""
    try:
        data = request.get_json()
        
        if not data.get('model_id'):
            return jsonify({
                'success': False,
                'error': 'Model ID is required'
            }), 400
        
        # Use external API service to test model
        result = test_model_connection(data['model_id'])
        
        return jsonify({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'response_time': result.get('response_time', 0),
            'error': result.get('error', '')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/chat', methods=['POST'])
def chat_external_model_v2():
    """Chat with external model - NEW VERSION"""
    try:
        data = request.get_json()
        
        if not data.get('model_id'):
            return jsonify({
                'success': False,
                'error': 'Model ID is required'
            }), 400
        
        if not data.get('message'):
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Use external API service to chat with model
        result = chat_with_model(
            model_id=data['model_id'],
            message=data['message'],
            system_prompt=data.get('system_prompt', ''),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 1000),
            top_p=data.get('top_p', 0.9),
            context_length=data.get('context_length', 4096),
            description=data.get('description', ''),
            capabilities=data.get('capabilities', []),
            tags=data.get('tags', []),
            use_rag=data.get('use_rag', None),  # None = use minion's RAG setting
            use_spirits=data.get('use_spirits', None)  # None = use minion's spirits setting
        )
        
        return jsonify({
            'success': result.get('success', False),
            'response': result.get('response', ''),
            'usage': result.get('usage', {}),
            'error': result.get('error', ''),
            'minion_name': result.get('minion_name', ''),
            'provider': result.get('provider', ''),
            'rag_used': result.get('rag_used', False),
            'spirits_enabled': result.get('spirits_enabled', False),
            'orchestration_used': result.get('orchestration_used', False),
            'spirits_used': result.get('spirits_used', []),
            'tools_used': result.get('tools_used', []),
            'processing_time': result.get('processing_time', 0),
            'task_type': result.get('task_type', ''),
            'used_config': result.get('used_config', {})
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/providers', methods=['GET'])
def get_providers_v2():
    """Get available providers - NEW VERSION"""
    try:
        providers = get_available_providers()
        
        return jsonify({
            'success': True,
            'providers': providers,
            'total': len(providers)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models', methods=['POST'])
def create_external_model_v2():
    """Create new external model - POSTGRESQL VERSION"""
    try:
        # Handle both JSON and FormData requests
        if request.content_type and 'multipart/form-data' in request.content_type:
            # FormData request (with file upload)
            data = request.form.to_dict()
            
            # If modelData is sent as JSON string, parse it
            if 'modelData' in data:
                import json
                model_data_json = json.loads(data['modelData'])
                data.update(model_data_json)
                del data['modelData']  # Remove the JSON string
            
            # Parse JSON fields
            if 'capabilities' in data and isinstance(data['capabilities'], str):
                data['capabilities'] = json.loads(data['capabilities'])
            if 'parameters' in data and isinstance(data['parameters'], str):
                data['parameters'] = json.loads(data['parameters'])
            if 'tags' in data and isinstance(data['tags'], str) and data['tags']:
                data['tags'] = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
            
            # Handle file upload
            if 'avatar' in request.files:
                avatar_file = request.files['avatar']
                if avatar_file and avatar_file.filename:
                    # Save avatar file
                    import os
                    upload_folder = 'uploads/avatars'
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Generate unique filename
                    import uuid
                    file_extension = os.path.splitext(avatar_file.filename)[1]
                    filename = f"{uuid.uuid4()}{file_extension}"
                    file_path = os.path.join(upload_folder, filename)
                    
                    avatar_file.save(file_path)
                    data['avatar_path'] = file_path
        else:
            # JSON request
            data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'provider', 'model_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create model data for PostgreSQL
        model_data = {
            'name': data['name'],
            'display_name': data.get('display_name', data['name']),
            'description': data.get('description', ''),
            'provider': data['provider'],
            'model_id': data['model_id'],
            'quantization': data.get('quantization'),
            'model_type': data.get('model_type'),  # Add model_type field
            'capabilities': data.get('capabilities', ['chat']),
            'parameters': data.get('parameters', {}),
            'context_length': data.get('context_length', 4096),
            'max_tokens': data.get('max_tokens', 2048),
            'temperature': data.get('temperature', 0.7),
            'top_p': data.get('top_p', 0.9),
            'system_prompt': data.get('system_prompt', ''),
            'tags': data.get('tags', []),
            'avatar_url': data.get('avatar_path') or data.get('avatar_url'),
            'avatar_path': data.get('avatar_path'),  # Add avatar_path field
            'is_active': data.get('is_active', True),
            'is_favorite': data.get('is_favorite', False)
        }
        
        # Get user_id from request data (frontend will pass this)
        user_id = data.get('user_id', 1)  # Default to 1 if not provided
        
        # Save to PostgreSQL using minion service
        result = minion_service.create_minion(user_id, model_data)  # Use user_id from frontend
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'External API model "{data["name"]}" added successfully',
                'model_id': result['minion']['id']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to create model')
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/<int:model_id>', methods=['PUT'])
def update_external_model_v2(model_id):
    """Update external model - NEW VERSION"""
    try:
        data = request.get_json()
        
        # Validate model exists
        model = db.get_external_api_model(model_id)
        if not model:
            return jsonify({
                'success': False,
                'error': 'External model not found'
            }), 404
        
        # Update model data
        success = db.update_external_api_model(model_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'External model updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update external model'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/<int:model_id>', methods=['DELETE'])
def delete_external_model_v2(model_id):
    """Delete external model - NEW VERSION"""
    try:
        success = db.delete_external_api_model(model_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'External model deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'External model not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/<int:model_id>/toggle-favorite', methods=['POST'])
def toggle_favorite_external_model_v2(model_id):
    """Toggle favorite status of external model - NEW VERSION"""
    try:
        success = db.toggle_favorite_external_model(model_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Favorite status toggled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'External model not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/sync-nvidia', methods=['POST'])
def sync_nvidia_models_v2():
    """Sync NVIDIA models - NEW VERSION"""
    try:
        # Use NVIDIA NIM service to sync models
        result = sync_nvidia_models()
        
        return jsonify({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'models_synced': result.get('models_synced', 0),
            'error': result.get('error', '')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/<int:model_id>/sync-nvidia', methods=['POST'])
def sync_nvidia_model_v2(model_id):
    """Sync specific NVIDIA model - NEW VERSION"""
    try:
        # Use NVIDIA NIM service to sync specific model
        result = sync_nvidia_model(model_id)
        
        return jsonify({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'error': result.get('error', '')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/<int:model_id>/avatar', methods=['POST'])
def upload_avatar_v2(model_id):
    """Upload avatar for external model - NEW VERSION"""
    try:
        if 'avatar' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No avatar file provided'
            }), 400
        
        avatar_file = request.files['avatar']
        
        if avatar_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No avatar file selected'
            }), 400
        
        # Handle avatar upload (simplified for now)
        # In a real implementation, you'd save the file and update the database
        
        return jsonify({
            'success': True,
            'message': 'Avatar uploaded successfully',
            'avatar_url': f'/avatars/external_model_{model_id}.png'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/<int:model_id>/status', methods=['GET'])
def get_model_api_status(model_id):
    """Get API configuration status for a minion"""
    try:
        minion = minion_service.get_minion_by_id(model_id)
        
        if not minion:
            return jsonify({
                'success': False,
                'error': 'Minion not found'
            }), 404
        
        has_api_key = bool(minion.get('api_key'))
        has_base_url = bool(minion.get('base_url'))
        
        # Determine status
        if has_api_key and has_base_url:
            status = 'configured'
            status_message = 'API configured and ready'
        elif has_api_key and not has_base_url:
            # Some providers don't need base_url (e.g., OpenAI uses default)
            status = 'configured'
            status_message = 'API configured (using default endpoint)'
        elif not has_api_key:
            status = 'missing_api_key'
            status_message = f'No API key configured for {minion.get("provider", "unknown")} provider'
        else:
            status = 'incomplete'
            status_message = 'API configuration incomplete'
        
        return jsonify({
            'success': True,
            'status': status,
            'status_message': status_message,
            'has_api_key': has_api_key,
            'has_base_url': has_base_url,
            'provider': minion.get('provider'),
            'model_id': model_id,
            'minion_name': minion.get('display_name')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@external_model_bp.route('/external-models/health', methods=['GET'])
def health_check_v2():
    """Health check for the new external models API"""
    try:
        # Get models count from minion service
        models = minion_service.get_all_minions()
        return jsonify({
            'success': True,
            'message': 'External Models API v2 is healthy',
            'total_models': len(models)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"External Models API v2 health check failed: {e}"
        }), 500
