# Training Verification Guide

**Created:** January 2025  
**Purpose:** How to verify that training/refinement actually applies to minion responses

---

## 📊 **Grafana Training Sessions Overview**

**Minion:** Grafana (ID: 17)  
**Total Training Sessions:** 6

### **Completed Trainings (3):**
1. **Grafana v1.3** (Job ID: 39) - RAG Training
   - Created: 2025-10-05 22:37:31
   - Type: RAG
   - Status: COMPLETED
   - **Collection Created:** `sasdasdas`
   - **Purpose:** "Enhance Grafana's personality and communication style"

2. **Grafana v1.1** (Job ID: ~38) - RAG Training
   - Created: 2025-10-05 19:36:01
   - Status: COMPLETED

3. **Grafana Style Refinement** (Job ID: ~37) - RAG Training
   - Created: 2025-10-05 19:20:07
   - Status: COMPLETED

### **Other Sessions:**
- **Grafana v1.2** - Status: RUNNING
- **Polling Test** - Status: FAILED
- **Real Dataset Test** - Status: FAILED

---

## 🔍 **Training Details: Grafana v1.3**

**Job ID:** 39  
**Type:** RAG Training  
**Model:** nvidia/llama-3.3-nemotron-super-49b-v1.5

### **RAG Configuration:**
```json
{
  "collectionName": "sasdasdas",
  "collectionDescription": "dasdasd",
  "chunkSize": 1000,
  "chunkOverlap": 100,
  "embeddingModel": "all-MiniLM-L6-v2",
  "retrievalMethod": "semantic",
  "topK": 4,
  "similarityThreshold": 0.7,
  "enableContextualCompression": true,
  "enableQueryExpansion": false,
  "enableSourceCitation": true,
  "knowledgeBaseStrategy": "create_new",
  "updateStrategy": "smart_replace"
}
```

**Key Settings:**
- **Top K:** 4 (retrieves 4 most relevant chunks)
- **Similarity Threshold:** 0.7 (only includes chunks with 70%+ similarity)
- **Contextual Compression:** Enabled (compresses retrieved context)
- **Source Citation:** Enabled (model will cite sources)

---

## 🧪 **How Training Applies to Chat**

### **Current Flow:**

1. **User clicks "Test Model" on `/minion-builder`**
   - Opens chat modal (`openChatModal()`)
   - Calls `/api/v2/external-models/chat` endpoint

2. **Backend Process** (`external_model_routes.py` → `chat_with_model()`):
   ```python
   # Check if RAG should be used
   should_use_rag = use_rag if use_rag is not None else minion.get('rag_enabled', False)
   
   # If RAG enabled and collection exists
   if should_use_rag and minion.get('rag_collection_name'):
       # Query ChromaDB collection
       kb_results = chromadb_service.query_collection(
           minion['rag_collection_name'], 
           message, 
           n_results=top_k
       )
       
       # Filter by similarity threshold
       filtered_results = [r for r in kb_results 
                          if r.get('distance', 1.0) <= (1 - similarity_threshold)]
       
       # Build knowledge base context
       kb_context = "\n\n".join([r.get('document', '') for r in filtered_results])
       
       # Add to message
       final_message = f"<KnowledgeBase>\n{kb_context}\n</KnowledgeBase>\n\n{message}"
   ```

3. **Model Receives:**
   - Original user message
   - **Plus:** Relevant knowledge from RAG training collection
   - **Plus:** System prompt with minion personality

---

## ✅ **How to Verify Training is Applied**

### **Method 1: Check Minion Configuration**

Verify that Grafana has RAG enabled and collection name set:

```sql
SELECT 
    display_name,
    rag_enabled,
    rag_collection_name,
    top_k,
    similarity_threshold
FROM external_api_models
WHERE display_name = 'Grafana';
```

**Expected:**
- `rag_enabled = true`
- `rag_collection_name = 'sasdasdas'` (or similar)
- `top_k = 3` or `4`
- `similarity_threshold = 0.7`

### **Method 2: Test with Specific Query**

1. **Go to `/minion-builder`**
2. **Click "Test Model" (chat icon) on Grafana**
3. **Ask a question that SHOULD be in the training data:**
   ```
   "What is my personality like?"
   "How should I communicate?"
   "Tell me about my style"
   ```

4. **Check Response:**
   - ✅ **If RAG is working:** Response should include information from the training dataset
   - ✅ **If source citation enabled:** Response should cite sources
   - ❌ **If RAG is NOT working:** Response will be generic, not using trained knowledge

### **Method 3: Check Backend Logs**

When chat endpoint is called, check backend logs for:
```
RAG collection queried: sasdasdas
Retrieved X chunks
Knowledge base context added to prompt
```

### **Method 4: Enable Debug Mode**

**Frontend:** Add `use_rag: true` to the chat request:
```javascript
// In MinionBuilder.vue, line ~2219
const requestBody = {
  model_id: this.selectedChatModel.id,
  message: userMessage,
  use_rag: true,  // ← Force RAG usage
  // ... other params
};
```

**Backend:** Check response includes:
```json
{
  "success": true,
  "response": "...",
  "rag_used": true,  // ← Should be true
  "used_config": {
    "rag_enabled": true,
    "rag_collection": "sasdasdas"
  }
}
```

---

## 🔧 **Current Issues & Solutions**

### **Issue 1: RAG Not Enabled by Default**

**Problem:** The chat endpoint uses `minion.get('rag_enabled', False)`, so if the minion doesn't have `rag_enabled = true` in the database, RAG won't be used.

**Solution:**
1. Update Grafana's database record:
   ```sql
   UPDATE external_api_models
   SET 
       rag_enabled = true,
       rag_collection_name = 'sasdasdas',
       top_k = 4,
       similarity_threshold = 0.7,
       enable_source_citation = true,
       enable_contextual_compression = true
   WHERE display_name = 'Grafana';
   ```

2. Or force RAG in frontend (temporary):
   ```javascript
   use_rag: true  // Force RAG usage
   ```

### **Issue 2: Collection Name Mismatch**

**Problem:** Training created collection `sasdasdas`, but minion might not be configured to use it.

**Solution:** Ensure `rag_collection_name` matches the collection created during training.

### **Issue 3: No Verification UI**

**Problem:** There's no way to see if RAG was used in the response.

**Solution:** Enhance chat response to show:
- ✅ "RAG: Active" indicator
- ✅ Number of knowledge chunks retrieved
- ✅ Sources cited (if enabled)

---

## 📝 **Testing Checklist**

### **Pre-Testing:**
- [ ] Grafana has `rag_enabled = true` in database
- [ ] Grafana has `rag_collection_name = 'sasdasdas'` set
- [ ] ChromaDB collection `sasdasdas` exists and has documents
- [ ] Collection has relevant documents for testing

### **During Testing:**
- [ ] Open `/minion-builder`
- [ ] Click "Test Model" (chat icon) on Grafana
- [ ] Send a test message related to training data
- [ ] Check if response includes trained knowledge
- [ ] Check browser console for API response metadata
- [ ] Check backend logs for RAG query confirmation

### **Verification:**
- [ ] Response quality improved (uses trained knowledge)
- [ ] Source citations appear (if enabled)
- [ ] Response is contextually relevant to training data
- [ ] API response includes `rag_used: true`

---

## 🎯 **Expected Behavior**

### **Without RAG:**
```
User: "What is my personality?"
Grafana: [Generic response, not using trained data]
```

### **With RAG (Training Applied):**
```
User: "What is my personality?"
Grafana: [Response includes information from training dataset]
         [If source citation enabled: Cites sources]
         [Contextually aware of training data]
```

---

## 🔍 **Debug Commands**

### **Check ChromaDB Collection:**
```python
from app.services.chromadb_service import ChromaDBService

chromadb_service = ChromaDBService()
results = chromadb_service.query_collection(
    'sasdasdas', 
    'What is my personality?', 
    n_results=3
)
print(f"Retrieved {len(results)} chunks")
for r in results:
    print(f"Distance: {r.get('distance')}")
    print(f"Content: {r.get('document')[:100]}...")
```

### **Check Minion Config:**
```python
from app.services.minion_service import MinionService

minion_service = MinionService()
grafana = minion_service.get_minion_by_id(17)
print(f"RAG Enabled: {grafana.get('rag_enabled')}")
print(f"Collection: {grafana.get('rag_collection_name')}")
```

---

## 📚 **Next Steps**

1. **Verify Grafana's RAG configuration in database**
2. **Test chat with RAG-enabled query**
3. **Add RAG status indicator to chat UI**
4. **Add debug mode to show retrieved chunks**
5. **Create automated test for training verification**

---

**Last Updated:** January 2025  
**Related Files:**
- `backend/app/routes/external_model_routes.py` - Chat endpoint
- `frontend/src/components/MinionBuilder.vue` - Chat modal
- `backend/app/services/chromadb_service.py` - RAG service
- `backend/services/external_training/rag/rag_service.py` - RAG training

