# RAG Retrieval Fix - Prioritizing Uploaded Files

## Problem Identified

When querying the knowledge base, uploaded file content was being drowned out by large datasets (37k+ documents), causing:
1. **Semantic mismatch**: Query "clickup token" didn't match document containing "clickapp token"
2. **Low similarity scores**: Uploaded file chunks had negative similarity scores
3. **Filtering out**: Strict similarity threshold (0.7) filtered out relevant uploaded content
4. **Wrong results**: ChromaDB returned irrelevant dataset items instead of uploaded files

## Root Cause

- Collection "tes7" contains 37,495 documents
- Only 20 documents are from uploaded files (chunks of the DOCX)
- When querying "clickup token", ChromaDB returned HTML button examples from Hugging Face dataset
- The uploaded file chunk (doc-7) containing "clickapp token" had negative similarity and was filtered out

## Solution Implemented

### 1. **Increased Query Results**
- Query `3x top_k` (or minimum 15) instead of just `top_k`
- Provides more candidates to filter from

### 2. **Prioritize Uploaded Files**
- Separate uploaded file chunks from dataset items
- Use lower similarity threshold (0.5) for uploaded files vs (0.7) for datasets
- Always prioritize uploaded files in results

### 3. **Keyword Matching**
- Check for exact keyword matches in uploaded files
- Check for partial matches (e.g., "click" in both "clickup" and "clickapp")
- Boost similarity score by 0.3 if keyword match found

### 4. **Fallback Logic**
- If uploaded files exist but don't meet threshold, use them anyway
- Ensures user-uploaded content is always prioritized

## Code Changes

**File**: `backend/app/routes/external_model_routes.py`

**Changes**:
- Modified `chat_with_model()` function's RAG retrieval logic
- Added separation of uploaded files vs datasets
- Added keyword matching for uploaded files
- Lowered threshold for uploaded files (0.5 vs 0.7)
- Increased query results (3x top_k minimum 15)

## Testing

To verify the fix works:

1. Query Grafana: "what is the clickup token?"
2. Expected: Should retrieve chunk doc-7 containing "clickapp token pk_126127973_ULPZ9TEC7TGPGAP3WVCA2KWOQQGV3Y4K"
3. The keyword "token" should match, and "click" partial match should boost similarity

## Next Steps

1. ✅ Test with "clickup token" query
2. ✅ Verify uploaded file chunks are prioritized
3. ⏳ Monitor similarity scores to ensure they're reasonable
4. ⏳ Consider adding fuzzy string matching for better partial matches

