"""
LangGraph-based Spirit Orchestrator
Manages spirit delegation and workflow for minions
"""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import time
import json

# Import existing services
from app.services.minion_service import MinionService
from app.services.chromadb_service import ChromaDBService
from app.services.external_api_service import ExternalAPIService

class SpiritWorkflowState(TypedDict):
    """State for LangGraph spirit workflow"""
    # Input
    user_input: str
    minion_id: int
    user_id: int
    
    # Spirit Configuration
    selected_spirits: List[str]
    spirit_levels: Dict[str, int]
    spirit_synergies: Dict[str, float]
    spirit_conflicts: Dict[str, float]
    
    # Task Processing
    task_type: str
    context: Dict[str, Any]
    
    # Results
    spirit_results: Dict[str, Any]
    final_response: str
    rag_context: str
    external_llm_response: str
    
    # Metadata
    processing_time: float
    spirits_used: List[str]
    tools_used: List[str]

class SpiritOrchestrator:
    """
    LangGraph-based orchestrator for spirit delegation
    One orchestrator per minion instance
    """
    
    def __init__(self, minion_id: int):
        self.minion_id = minion_id
        self.minion_service = MinionService()
        self.chromadb_service = ChromaDBService()
        self.external_api_service = ExternalAPIService()
        
        # Load minion configuration
        self.minion = self.minion_service.get_minion_by_id(minion_id)
        if not self.minion:
            raise ValueError(f"Minion {minion_id} not found")
        
        # Load assigned spirits
        self.assigned_spirits = self._load_minion_spirits()
        
        # Create LangGraph workflow
        self.workflow = self._create_spirit_workflow()
        self.memory = MemorySaver()
    
    def _load_minion_spirits(self) -> List[Dict[str, Any]]:
        """Dynamically load spirits assigned to this minion from database"""
        try:
            # Import spirit service for database queries
            from app.services.spirit_service import SpiritService
            from app.services.minion_spirit_integration import MinionSpiritIntegration
            
            spirit_service = SpiritService()
            integration_service = MinionSpiritIntegration()
            
            # Get minion's assigned spirits from database
            assigned_spirits = integration_service.get_minion_spirits(self.minion_id)
            
            # Load spirit details and tools for each assigned spirit
            loaded_spirits = []
            for spirit_assignment in assigned_spirits:
                spirit_id = spirit_assignment.get('spirit_id')
                spirit_level = spirit_assignment.get('spirit_level', 1)
                
                # Get spirit details from registry
                spirit_details = spirit_service.get_spirit_by_id(spirit_id)
                if spirit_details:
                    # Get tools available at this spirit level
                    available_tools = self._get_spirit_tools_by_level(spirit_details, spirit_level)
                    
                    loaded_spirits.append({
                        "id": spirit_id,
                        "name": spirit_details.get('name', '').lower().replace(' spirit', ''),
                        "level": spirit_level,
                        "tools": available_tools,
                        "category": spirit_details.get('category', ''),
                        "synergies": spirit_details.get('synergies', {}),
                        "conflicts": spirit_details.get('conflicts', {})
                    })
            
            # If no spirits assigned, load default free spirits
            if not loaded_spirits:
                loaded_spirits = self._load_default_free_spirits()
            
            return loaded_spirits
            
        except Exception as e:
            print(f"Error loading minion spirits: {e}")
            # Fallback to default spirits
            return self._load_default_free_spirits()
    
    def _load_default_free_spirits(self) -> List[Dict[str, Any]]:
        """Load default free spirits for new minions"""
        return [
            {"id": 1, "name": "writer", "level": 1, "tools": ["markdown_generator", "style_adapter"], "category": "Content & Creativity"},
            {"id": 4, "name": "analyst", "level": 1, "tools": ["chroma_search", "data_cleaner"], "category": "Data & Analysis"},
            {"id": 7, "name": "builder", "level": 1, "tools": ["file_writer", "folder_manager"], "category": "Development & Technical"},
            {"id": 10, "name": "connector", "level": 1, "tools": ["openai_adapter", "nvidia_adapter"], "category": "Integration & Communication"},
            {"id": 13, "name": "checker", "level": 1, "tools": ["grammar_checker", "test_runner"], "category": "Quality & Validation"}
        ]
    
    def _get_spirit_tools_by_level(self, spirit_details: Dict[str, Any], level: int) -> List[str]:
        """Get tools available for a spirit at a specific level"""
        all_tools = spirit_details.get('tools', [])
        
        # Define tool unlock progression by level
        tool_unlock_map = {
            1: 0.25,  # 25% of tools at level 1
            2: 0.35,  # 35% of tools at level 2
            3: 0.50,  # 50% of tools at level 3
            4: 0.65,  # 65% of tools at level 4
            5: 0.80,  # 80% of tools at level 5
            6: 0.90,  # 90% of tools at level 6
            7: 0.95,  # 95% of tools at level 7
            8: 0.98,  # 98% of tools at level 8
            9: 0.99,  # 99% of tools at level 9
            10: 1.0   # 100% of tools at level 10
        }
        
        # Calculate how many tools to unlock
        unlock_percentage = tool_unlock_map.get(level, 0.25)
        num_tools_to_unlock = max(1, int(len(all_tools) * unlock_percentage))
        
        # Return the first N tools (can be made more sophisticated)
        return all_tools[:num_tools_to_unlock]
    
    def _create_spirit_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for spirit orchestration"""
        
        # Create workflow
        workflow = StateGraph(SpiritWorkflowState)
        
        # Add nodes
        workflow.add_node("task_analyzer", self._analyze_task)
        workflow.add_node("spirit_selector", self._select_spirits)
        workflow.add_node("rag_retrieval", self._retrieve_rag_context)
        workflow.add_node("writer_spirit", self._writer_spirit_node)
        workflow.add_node("analyst_spirit", self._analyst_spirit_node)
        workflow.add_node("builder_spirit", self._builder_spirit_node)
        workflow.add_node("connector_spirit", self._connector_spirit_node)
        workflow.add_node("checker_spirit", self._checker_spirit_node)
        workflow.add_node("result_aggregator", self._aggregate_results)
        
        # Define workflow edges
        workflow.set_entry_point("task_analyzer")
        workflow.add_edge("task_analyzer", "spirit_selector")
        workflow.add_edge("spirit_selector", "rag_retrieval")
        
        # Conditional spirit execution based on task type and available spirits
        workflow.add_conditional_edges(
            "rag_retrieval",
            self._should_use_writer_spirit,
            {
                "writer": "writer_spirit",
                "skip_writer": "analyst_check"
            }
        )
        
        workflow.add_conditional_edges(
            "writer_spirit",
            self._should_use_analyst_spirit,
            {
                "analyst": "analyst_spirit",
                "skip_analyst": "builder_check"
            }
        )
        
        workflow.add_conditional_edges(
            "analyst_spirit",
            self._should_use_builder_spirit,
            {
                "builder": "builder_spirit",
                "skip_builder": "connector_check"
            }
        )
        
        workflow.add_conditional_edges(
            "builder_spirit",
            self._should_use_connector_spirit,
            {
                "connector": "connector_spirit",
                "skip_connector": "checker_check"
            }
        )
        
        workflow.add_conditional_edges(
            "connector_spirit",
            self._should_use_checker_spirit,
            {
                "checker": "checker_spirit",
                "skip_checker": "result_aggregator"
            }
        )
        
        workflow.add_edge("checker_spirit", "result_aggregator")
        workflow.add_edge("result_aggregator", END)
        
        return workflow.compile()
    
    def _analyze_task(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Analyze user input to determine task type and requirements"""
        user_input = state["user_input"].lower()
        
        # Simple task classification (can be enhanced with NLP)
        if any(word in user_input for word in ["write", "create", "generate", "draft", "content"]):
            state["task_type"] = "content_creation"
        elif any(word in user_input for word in ["analyze", "data", "chart", "graph", "research"]):
            state["task_type"] = "data_analysis"
        elif any(word in user_input for word in ["code", "build", "develop", "program", "file"]):
            state["task_type"] = "code_generation"
        elif any(word in user_input for word in ["search", "find", "lookup", "knowledge"]):
            state["task_type"] = "information_retrieval"
        elif any(word in user_input for word in ["api", "call", "external", "model"]):
            state["task_type"] = "external_integration"
        else:
            state["task_type"] = "general"
        
        return state
    
    def _select_spirits(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Select appropriate spirits based on task type and minion configuration"""
        # Get minion's assigned spirits
        state["selected_spirits"] = [spirit["name"] for spirit in self.assigned_spirits]
        state["spirit_levels"] = {spirit["name"]: spirit["level"] for spirit in self.assigned_spirits}
        
        # Calculate synergies and conflicts
        state["spirit_synergies"] = self._calculate_synergies(state["selected_spirits"])
        state["spirit_conflicts"] = self._calculate_conflicts(state["selected_spirits"])
        
        return state
    
    def _retrieve_rag_context(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Retrieve relevant context from RAG knowledge base"""
        if "analyst" in state["selected_spirits"] and self.minion.get('rag_enabled'):
            try:
                # Use existing RAG system
                collection_name = self.minion.get('rag_collection_name')
                if collection_name:
                    results = self.chromadb_service.query_collection(
                        collection_name,
                        state["user_input"],
                        n_results=3
                    )
                    if results:
                        state["rag_context"] = "\n\n".join([r.get('document', '') for r in results])
                        state["tools_used"].append("chroma_search")
            except Exception as e:
                print(f"RAG retrieval error: {e}")
                state["rag_context"] = ""
        
        return state
    
    def _writer_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Writer spirit handles content generation tasks"""
        if "writer" not in state["selected_spirits"]:
            return state
        
        try:
            # Get writer spirit tools
            writer_spirit = next((s for s in self.assigned_spirits if s["name"] == "writer"), None)
            if not writer_spirit:
                return state
            
            # Apply writer tools
            content = self._apply_writer_tools(
                state["user_input"], 
                state.get("rag_context", ""), 
                writer_spirit["tools"]
            )
            
            state["spirit_results"]["writer"] = content
            state["spirits_used"].append("writer")
            state["tools_used"].extend(writer_spirit["tools"])
            
        except Exception as e:
            print(f"Writer spirit error: {e}")
            state["spirit_results"]["writer"] = f"Writer spirit error: {e}"
        
        return state
    
    def _analyst_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Analyst spirit handles data analysis and RAG operations"""
        if "analyst" not in state["selected_spirits"]:
            return state
        
        try:
            # Get analyst spirit tools
            analyst_spirit = next((s for s in self.assigned_spirits if s["name"] == "analyst"), None)
            if not analyst_spirit:
                return state
            
            # Apply analyst tools
            analysis = self._apply_analyst_tools(
                state["user_input"], 
                state.get("rag_context", ""), 
                analyst_spirit["tools"]
            )
            
            state["spirit_results"]["analyst"] = analysis
            state["spirits_used"].append("analyst")
            state["tools_used"].extend(analyst_spirit["tools"])
            
        except Exception as e:
            print(f"Analyst spirit error: {e}")
            state["spirit_results"]["analyst"] = f"Analyst spirit error: {e}"
        
        return state
    
    def _builder_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Builder spirit handles code generation and file operations"""
        if "builder" not in state["selected_spirits"]:
            return state
        
        try:
            # Get builder spirit tools
            builder_spirit = next((s for s in self.assigned_spirits if s["name"] == "builder"), None)
            if not builder_spirit:
                return state
            
            # Apply builder tools
            code = self._apply_builder_tools(
                state["user_input"], 
                state.get("rag_context", ""), 
                builder_spirit["tools"]
            )
            
            state["spirit_results"]["builder"] = code
            state["spirits_used"].append("builder")
            state["tools_used"].extend(builder_spirit["tools"])
            
        except Exception as e:
            print(f"Builder spirit error: {e}")
            state["spirit_results"]["builder"] = f"Builder spirit error: {e}"
        
        return state
    
    def _connector_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Connector spirit handles external API calls"""
        if "connector" not in state["selected_spirits"]:
            return state
        
        try:
            # Get connector spirit tools
            connector_spirit = next((s for s in self.assigned_spirits if s["name"] == "connector"), None)
            if not connector_spirit:
                return state
            
            # Apply connector tools
            external_response = self._apply_connector_tools(
                state["user_input"], 
                connector_spirit["tools"]
            )
            
            state["external_llm_response"] = external_response
            state["spirits_used"].append("connector")
            state["tools_used"].extend(connector_spirit["tools"])
            
        except Exception as e:
            print(f"Connector spirit error: {e}")
            state["external_llm_response"] = f"Connector spirit error: {e}"
        
        return state
    
    def _checker_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Checker spirit handles validation and quality assurance"""
        if "checker" not in state["selected_spirits"]:
            return state
        
        try:
            # Get checker spirit tools
            checker_spirit = next((s for s in self.assigned_spirits if s["name"] == "checker"), None)
            if not checker_spirit:
                return state
            
            # Apply checker tools
            validation = self._apply_checker_tools(
                state["spirit_results"], 
                checker_spirit["tools"]
            )
            
            state["spirit_results"]["checker"] = validation
            state["spirits_used"].append("checker")
            state["tools_used"].extend(checker_spirit["tools"])
            
        except Exception as e:
            print(f"Checker spirit error: {e}")
            state["spirit_results"]["checker"] = f"Checker spirit error: {e}"
        
        return state
    
    def _aggregate_results(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Aggregate results from all spirits into final response"""
        results = state["spirit_results"]
        
        # Combine all spirit outputs
        final_response_parts = []
        
        if "writer" in results:
            final_response_parts.append(f"**Content:**\n{results['writer']}")
        
        if "analyst" in results:
            final_response_parts.append(f"**Analysis:**\n{results['analyst']}")
        
        if "builder" in results:
            final_response_parts.append(f"**Code:**\n{results['builder']}")
        
        if "checker" in results:
            final_response_parts.append(f"**Validation:**\n{results['checker']}")
        
        if state.get("external_llm_response"):
            final_response_parts.append(f"**External LLM:**\n{state['external_llm_response']}")
        
        # If no spirit results, provide a fallback response
        if not final_response_parts:
            final_response_parts.append(f"I understand you want help with: {state['user_input']}")
        
        state["final_response"] = "\n\n".join(final_response_parts)
        
        return state
    
    # Conditional edge functions
    def _should_use_writer_spirit(self, state: SpiritWorkflowState) -> str:
        if "writer" in state["selected_spirits"] and state["task_type"] in ["content_creation", "general"]:
            return "writer"
        return "skip_writer"
    
    def _should_use_analyst_spirit(self, state: SpiritWorkflowState) -> str:
        if "analyst" in state["selected_spirits"] and state["task_type"] in ["data_analysis", "information_retrieval"]:
            return "analyst"
        return "skip_analyst"
    
    def _should_use_builder_spirit(self, state: SpiritWorkflowState) -> str:
        if "builder" in state["selected_spirits"] and state["task_type"] in ["code_generation"]:
            return "builder"
        return "skip_builder"
    
    def _should_use_connector_spirit(self, state: SpiritWorkflowState) -> str:
        if "connector" in state["selected_spirits"] and state["task_type"] in ["external_integration", "general"]:
            return "connector"
        return "skip_connector"
    
    def _should_use_checker_spirit(self, state: SpiritWorkflowState) -> str:
        if "checker" in state["selected_spirits"]:
            return "checker"
        return "skip_checker"
    
    # Helper methods
    def _calculate_synergies(self, spirits: List[str]) -> Dict[str, float]:
        """Calculate synergy bonuses between spirits"""
        synergies = {}
        
        # Define synergy pairs
        synergy_pairs = {
            ("writer", "creative"): 0.25,
            ("analyst", "researcher"): 0.30,
            ("builder", "debugger"): 0.20,
            ("connector", "scheduler"): 0.15,
            ("checker", "security"): 0.25,
        }
        
        for (spirit1, spirit2), bonus in synergy_pairs.items():
            if spirit1 in spirits and spirit2 in spirits:
                synergies[f"{spirit1}_{spirit2}"] = bonus
        
        return synergies
    
    def _calculate_conflicts(self, spirits: List[str]) -> Dict[str, float]:
        """Calculate conflict penalties between spirits"""
        conflicts = {}
        
        # Define conflict pairs
        conflict_pairs = {
            ("analyst", "creative"): -0.15,
            ("security", "builder"): -0.10,
            ("mathematician", "creative"): -0.12,
        }
        
        for (spirit1, spirit2), penalty in conflict_pairs.items():
            if spirit1 in spirits and spirit2 in spirits:
                conflicts[f"{spirit1}_{spirit2}"] = penalty
        
        return conflicts
    
    def _apply_writer_tools(self, user_input: str, context: str, tools: List[str]) -> str:
        """Apply writer spirit tools"""
        # Mock implementation - replace with actual tool execution
        if "markdown_generator" in tools:
            return f"Generated markdown content for: {user_input}"
        elif "style_adapter" in tools:
            return f"Applied style adaptation for: {user_input}"
        else:
            return f"Writer spirit processed: {user_input}"
    
    def _apply_analyst_tools(self, user_input: str, context: str, tools: List[str]) -> str:
        """Apply analyst spirit tools"""
        # Mock implementation - replace with actual tool execution
        if "chroma_search" in tools and context:
            return f"Analyzed data with RAG context: {context[:100]}..."
        elif "data_cleaner" in tools:
            return f"Cleaned and processed data for: {user_input}"
        else:
            return f"Analyst spirit processed: {user_input}"
    
    def _apply_builder_tools(self, user_input: str, context: str, tools: List[str]) -> str:
        """Apply builder spirit tools"""
        # Mock implementation - replace with actual tool execution
        if "file_writer" in tools:
            return f"Generated code files for: {user_input}"
        elif "folder_manager" in tools:
            return f"Created project structure for: {user_input}"
        else:
            return f"Builder spirit processed: {user_input}"
    
    def _apply_connector_tools(self, user_input: str, tools: List[str]) -> str:
        """Apply connector spirit tools"""
        # Mock implementation - replace with actual tool execution
        if "openai_adapter" in tools:
            return f"OpenAI API response for: {user_input}"
        elif "nvidia_adapter" in tools:
            return f"NVIDIA API response for: {user_input}"
        else:
            return f"Connector spirit processed: {user_input}"
    
    def _apply_checker_tools(self, results: Dict[str, Any], tools: List[str]) -> str:
        """Apply checker spirit tools"""
        # Mock implementation - replace with actual tool execution
        if "grammar_checker" in tools:
            return f"Grammar check completed for {len(results)} spirit outputs"
        elif "test_runner" in tools:
            return f"Tests executed for {len(results)} spirit outputs"
        else:
            return f"Checker spirit validated {len(results)} outputs"
    
    def process_user_input(self, user_input: str, user_id: int) -> Dict[str, Any]:
        """Main entry point for processing user input through spirit workflow"""
        start_time = time.time()
        
        # Create initial state
        initial_state = SpiritWorkflowState(
            user_input=user_input,
            minion_id=self.minion_id,
            user_id=user_id,
            selected_spirits=[],
            spirit_levels={},
            spirit_synergies={},
            spirit_conflicts={},
            task_type="",
            context={},
            spirit_results={},
            final_response="",
            rag_context="",
            external_llm_response="",
            processing_time=0.0,
            spirits_used=[],
            tools_used=[]
        )
        
        try:
            # Execute LangGraph workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Calculate processing time
            final_state["processing_time"] = time.time() - start_time
            
            return {
                'success': True,
                'response': final_state['final_response'],
                'spirits_used': final_state['spirits_used'],
                'tools_used': final_state['tools_used'],
                'processing_time': final_state['processing_time'],
                'rag_used': bool(final_state.get('rag_context')),
                'task_type': final_state['task_type'],
                'used_config': {
                    'spirits': final_state['selected_spirits'],
                    'synergies': final_state['spirit_synergies'],
                    'conflicts': final_state['spirit_conflicts']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"Spirit orchestrator error: {e}",
                'processing_time': time.time() - start_time
            }
