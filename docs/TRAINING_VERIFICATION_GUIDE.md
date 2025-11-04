# Training Verification Guide

## How to Verify Training Effectiveness

After training Grafana (or any minion) with documents, follow these steps to verify the training worked:

### Method 1: Using the Test Script (Recommended)

1. **After training completes**, run the verification script:
```bash
cd backend
source venv/bin/activate
python scripts/verify_training.py 17 "What is Google Keep?" "Tell me about the document"
```

This will:
- ✅ Check if RAG is enabled on the minion
- ✅ Verify the ChromaDB collection exists
- ✅ Test the chat API with your questions
- ✅ Confirm RAG is being used in responses

### Method 2: Manual Testing via UI

1. **Go to Minion-Builder page** (`/minion-builder`)
2. **Find Grafana** in the list
3. **Click "Test Model"** button (chat icon)
4. **Chat modal opens** - Ask questions like:
   - "What is Google Keep?"
   - "Tell me about the document you were trained on"
   - "What information do you have about Google Keep?"
5. **Verify the response** - Grafana should answer using content from the uploaded document

### What to Look For

#### ✅ Success Indicators:
- Chat modal opens when clicking "Test Model"
- Minion responds with relevant information
- Response mentions content from your document
- No errors in browser console

#### ❌ Failure Indicators:
- "RAG is NOT enabled" error
- "No API key configured" error
- Generic responses that don't mention document content
- Empty or error responses

### Troubleshooting

If training doesn't work:

1. **Check Training Job Status**:
   - Go to `/training` page
   - Check if the job status is "COMPLETED"
   - Look for any error messages

2. **Check Minion Configuration**:
   ```bash
   python scripts/verify_training.py <minion_id>
   ```
   This will show if RAG is enabled

3. **Check Backend Logs**:
   ```bash
   tail -f backend.log | grep -i "rag\|training\|error"
   ```

4. **Verify ChromaDB Collection**:
   - Check if collection exists in `backend/app/services/chromadb_data/`
   - Collection name should match `rag_collection_name` in minion config

### Expected Flow

1. **Create Minion** → `/minion-builder` → Personality + Model
2. **Train Minion** → `/training` → Upload documents → RAG training
3. **Test Minion** → `/minion-builder` → Click "Test Model" → Chat uses knowledge base ✅

### Example Test Questions

After training with "google keep document.docx", try:
- "What is Google Keep?"
- "How does Google Keep work?"
- "What features does Google Keep have?"
- "Tell me about the document you were trained on"

The minion should answer using content from the uploaded document!

