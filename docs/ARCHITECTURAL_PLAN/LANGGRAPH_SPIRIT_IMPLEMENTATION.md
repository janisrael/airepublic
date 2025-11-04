# LangGraph Spirit System Implementation Plan

**Created:** October 5, 2025  
**Status:** Implementation Phase  
**Version:** 1.0

---

## 🎯 **Overview**

This document outlines the implementation of the Dynamic Spirit System using LangGraph for orchestration, integrating with the existing AI Republic minion system.

---

## 🏗️ **Architecture Integration**

### **Current System → Spirit System**

```
User Chatbox (Visible Minion)
         ↓
Current Minion API (/api/v2/external-models/chat)
         ↓
LangGraph Spirit Orchestrator (NEW)
         ↓
Spirit Helpers (Hidden)
         ↓
Results Aggregation
         ↓
Single Response to User
```

### **Key Integration Points:**

1. **Minion API Enhancement**: Add spirit orchestration to existing chat endpoint
2. **Database Schema**: Add spirit registry and assignment tables
3. **LangGraph Workflow**: Implement spirit delegation logic
4. **Tool Loading**: Dynamic tool assignment based on selected spirits

---

## 📊 **Database Schema Extensions**

### **1. Spirits Registry Table**
```sql
CREATE TABLE spirits_registry (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT,
    icon TEXT, -- emoji or icon name
    unlock_rank TEXT DEFAULT 'Novice',
    unlock_level INTEGER DEFAULT 1,
    max_spirit_level INTEGER DEFAULT 10,
    tools JSONB DEFAULT '[]', -- Available tools for this spirit
    synergies JSONB DEFAULT '{}', -- Compatible spirits with bonuses
    conflicts JSONB DEFAULT '{}', -- Conflicting spirits with penalties
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **2. Minion Spirits Assignment Table**
```sql
CREATE TABLE minion_spirits (
    id SERIAL PRIMARY KEY,
    minion_id INTEGER NOT NULL REFERENCES external_api_models(id),
    spirit_id INTEGER NOT NULL REFERENCES spirits_registry(id),
    spirit_level INTEGER DEFAULT 1,
    spirit_xp INTEGER DEFAULT 0,
    xp_to_next_level INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(minion_id, spirit_id)
);
```

### **3. Spirit Mastery Tracking**
```sql
CREATE TABLE spirit_mastery (
    id SERIAL PRIMARY KEY,
    minion_spirit_id INTEGER NOT NULL REFERENCES minion_spirits(id),
    tool_name TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    mastery_level INTEGER DEFAULT 1,
    xp_earned INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(minion_spirit_id, tool_name)
);
```

---

## 🔧 **LangGraph Implementation**

### **1. Spirit Workflow State**
```python
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

class SpiritWorkflowState(TypedDict):
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
```

### **2. LangGraph Workflow Definition**
```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class SpiritOrchestrator:
    def __init__(self):
        self.workflow = self._create_workflow()
        self.memory = MemorySaver()
    
    def _create_workflow(self) -> StateGraph:
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
        
        # Conditional spirit execution
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
        
        # Continue for other spirits...
        
        workflow.add_edge("checker_spirit", "result_aggregator")
        workflow.add_edge("result_aggregator", END)
        
        return workflow.compile()
    
    def _analyze_task(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Analyze user input to determine task type and requirements"""
        user_input = state["user_input"]
        
        # Simple task classification (can be enhanced with NLP)
        if any(word in user_input.lower() for word in ["write", "create", "generate", "draft"]):
            state["task_type"] = "content_creation"
        elif any(word in user_input.lower() for word in ["analyze", "data", "chart", "graph"]):
            state["task_type"] = "data_analysis"
        elif any(word in user_input.lower() for word in ["code", "build", "develop", "program"]):
            state["task_type"] = "code_generation"
        elif any(word in user_input.lower() for word in ["search", "find", "lookup"]):
            state["task_type"] = "information_retrieval"
        else:
            state["task_type"] = "general"
        
        return state
    
    def _select_spirits(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Select appropriate spirits based on task type and minion configuration"""
        minion_id = state["minion_id"]
        
        # Get minion's assigned spirits from database
        assigned_spirits = self._get_minion_spirits(minion_id)
        state["selected_spirits"] = assigned_spirits
        
        # Calculate synergies and conflicts
        state["spirit_synergies"] = self._calculate_synergies(assigned_spirits)
        state["spirit_conflicts"] = self._calculate_conflicts(assigned_spirits)
        
        return state
    
    def _retrieve_rag_context(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Retrieve relevant context from RAG knowledge base"""
        if "analyst" in state["selected_spirits"]:
            # Use existing RAG system
            from app.services.chromadb_service import ChromaDBService
            chromadb_service = ChromaDBService()
            
            # Get minion's collection
            minion = self._get_minion_by_id(state["minion_id"])
            if minion and minion.get('rag_collection_name'):
                results = chromadb_service.query_collection(
                    minion['rag_collection_name'],
                    state["user_input"],
                    n_results=3
                )
                state["rag_context"] = "\n\n".join([r.get('document', '') for r in results])
        
        return state
    
    def _writer_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Writer spirit handles content generation tasks"""
        if "writer" not in state["selected_spirits"]:
            return state
        
        # Writer spirit logic
        writer_tools = self._get_spirit_tools("writer", state["spirit_levels"].get("writer", 1))
        
        # Apply writer tools to generate content
        content = self._apply_writer_tools(state["user_input"], state["rag_context"], writer_tools)
        state["spirit_results"]["writer"] = content
        
        return state
    
    def _analyst_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Analyst spirit handles data analysis and RAG operations"""
        if "analyst" not in state["selected_spirits"]:
            return state
        
        # Analyst spirit logic
        analyst_tools = self._get_spirit_tools("analyst", state["spirit_levels"].get("analyst", 1))
        
        # Apply analyst tools for data processing
        analysis = self._apply_analyst_tools(state["user_input"], state["rag_context"], analyst_tools)
        state["spirit_results"]["analyst"] = analysis
        
        return state
    
    def _builder_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Builder spirit handles code generation and file operations"""
        if "builder" not in state["selected_spirits"]:
            return state
        
        # Builder spirit logic
        builder_tools = self._get_spirit_tools("builder", state["spirit_levels"].get("builder", 1))
        
        # Apply builder tools for code generation
        code = self._apply_builder_tools(state["user_input"], state["rag_context"], builder_tools)
        state["spirit_results"]["builder"] = code
        
        return state
    
    def _connector_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Connector spirit handles external API calls"""
        if "connector" not in state["selected_spirits"]:
            return state
        
        # Connector spirit logic
        connector_tools = self._get_spirit_tools("connector", state["spirit_levels"].get("connector", 1))
        
        # Apply connector tools for external API calls
        external_response = self._apply_connector_tools(state["user_input"], connector_tools)
        state["external_llm_response"] = external_response
        
        return state
    
    def _checker_spirit_node(self, state: SpiritWorkflowState) -> SpiritWorkflowState:
        """Checker spirit handles validation and quality assurance"""
        if "checker" not in state["selected_spirits"]:
            return state
        
        # Checker spirit logic
        checker_tools = self._get_spirit_tools("checker", state["spirit_levels"].get("checker", 1))
        
        # Apply checker tools for validation
        validation = self._apply_checker_tools(state["spirit_results"], checker_tools)
        state["spirit_results"]["checker"] = validation
        
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
    
    # Helper methods
    def _get_minion_spirits(self, minion_id: int) -> List[str]:
        """Get assigned spirits for a minion"""
        # Database query to get minion's spirits
        pass
    
    def _calculate_synergies(self, spirits: List[str]) -> Dict[str, float]:
        """Calculate synergy bonuses between spirits"""
        # Implementation based on spirit synergy matrix
        pass
    
    def _calculate_conflicts(self, spirits: List[str]) -> Dict[str, float]:
        """Calculate conflict penalties between spirits"""
        # Implementation based on spirit conflict matrix
        pass
    
    def _get_spirit_tools(self, spirit_name: str, level: int) -> List[str]:
        """Get available tools for a spirit at given level"""
        # Implementation based on spirit level progression
        pass
    
    def _apply_writer_tools(self, user_input: str, context: str, tools: List[str]) -> str:
        """Apply writer spirit tools"""
        # Implementation of writer tools
        pass
    
    def _apply_analyst_tools(self, user_input: str, context: str, tools: List[str]) -> str:
        """Apply analyst spirit tools"""
        # Implementation of analyst tools
        pass
    
    def _apply_builder_tools(self, user_input: str, context: str, tools: List[str]) -> str:
        """Apply builder spirit tools"""
        # Implementation of builder tools
        pass
    
    def _apply_connector_tools(self, user_input: str, tools: List[str]) -> str:
        """Apply connector spirit tools"""
        # Implementation of connector tools
        pass
    
    def _apply_checker_tools(self, results: Dict[str, Any], tools: List[str]) -> str:
        """Apply checker spirit tools"""
        # Implementation of checker tools
        pass
```

---

## 🔌 **Integration with Existing System**

### **1. Enhanced Minion API**
```python
# backend/app/routes/external_model_routes.py

def chat_with_model_with_spirits(model_id, message, system_prompt='', **kwargs):
    """Enhanced chat function with spirit orchestration"""
    
    # Get minion configuration
    minion = minion_service.get_minion_by_id(model_id)
    
    # Initialize spirit orchestrator
    orchestrator = SpiritOrchestrator()
    
    # Create initial state
    initial_state = SpiritWorkflowState(
        user_input=message,
        minion_id=model_id,
        user_id=minion['user_id'],
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
    
    # Execute LangGraph workflow
    final_state = orchestrator.workflow.invoke(initial_state)
    
    return {
        'success': True,
        'response': final_state['final_response'],
        'spirits_used': final_state['spirits_used'],
        'tools_used': final_state['tools_used'],
        'processing_time': final_state['processing_time'],
        'rag_used': bool(final_state.get('rag_context')),
        'used_config': {
            'spirits': final_state['selected_spirits'],
            'synergies': final_state['spirit_synergies'],
            'conflicts': final_state['spirit_conflicts']
        }
    }
```

### **2. Spirit Management API**
```python
# backend/app/routes/spirit_routes.py

@spirit_bp.route('/spirits', methods=['GET'])
def get_available_spirits():
    """Get all available spirits"""
    pass

@spirit_bp.route('/minions/<int:minion_id>/spirits', methods=['GET'])
def get_minion_spirits(minion_id):
    """Get assigned spirits for a minion"""
    pass

@spirit_bp.route('/minions/<int:minion_id>/spirits', methods=['POST'])
def assign_spirits_to_minion(minion_id):
    """Assign spirits to a minion"""
    pass

@spirit_bp.route('/spirits/<int:spirit_id>/tools', methods=['GET'])
def get_spirit_tools(spirit_id):
    """Get available tools for a spirit"""
    pass
```

---

## 🚀 **Implementation Phases**

### **Phase 1: Database Schema (2-3 hours)**
1. Create spirit registry tables
2. Seed initial spirit data
3. Create spirit assignment tables
4. Add spirit mastery tracking

### **Phase 2: LangGraph Core (3-4 hours)**
1. Implement SpiritOrchestrator class
2. Create LangGraph workflow
3. Implement spirit nodes
4. Add conditional logic

### **Phase 3: Spirit Tools (2-3 hours)**
1. Implement spirit-specific tools
2. Create tool loading system
3. Add tool execution logic
4. Implement synergy/conflict calculations

### **Phase 4: API Integration (2-3 hours)**
1. Enhance existing minion API
2. Add spirit management endpoints
3. Integrate with existing RAG system
4. Add spirit configuration UI

### **Phase 5: Frontend Integration (3-4 hours)**
1. Create spirit selection component
2. Add spirit management to minion cards
3. Show spirit levels and tools
4. Implement spirit synergy visualization

---

## 🎯 **Benefits of LangGraph Integration**

### **1. Workflow Orchestration**
- **Conditional Logic**: Spirits are called based on task type
- **Parallel Processing**: Multiple spirits can work simultaneously
- **State Management**: LangGraph handles complex state transitions
- **Error Handling**: Graceful fallback if spirits fail

### **2. Scalability**
- **Modular Design**: Easy to add new spirits
- **Dynamic Loading**: Spirits loaded based on minion configuration
- **Performance**: Only necessary spirits are activated
- **Extensibility**: New workflow patterns can be added

### **3. Integration**
- **Existing System**: Works with current minion API
- **RAG Integration**: Seamlessly uses existing RAG system
- **External APIs**: Connects to existing external LLM services
- **Database**: Uses existing PostgreSQL infrastructure

---

## 📋 **Next Steps**

1. **Install LangGraph**: `pip install langgraph`
2. **Create Database Schema**: Implement spirit registry tables
3. **Implement Core Orchestrator**: Create SpiritOrchestrator class
4. **Test Basic Workflow**: Simple spirit delegation
5. **Add Spirit Tools**: Implement tool loading system
6. **Integrate with API**: Enhance existing minion chat endpoint
7. **Create Frontend**: Spirit selection and management UI

---

**This implementation provides a solid foundation for the Dynamic Spirit System while maintaining compatibility with the existing AI Republic architecture.**
