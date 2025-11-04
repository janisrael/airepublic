# RAG Training Modal - Knowledge Base Strategies

## Overview

The RAG (Retrieval-Augmented Generation) Training Modal provides two distinct strategies for managing knowledge bases during minion training. Each strategy offers different configuration options and use cases.

## Knowledge Base Strategies

### 1. Create New Collection 📁

**Purpose**: Create a brand new ChromaDB collection for RAG training.

**When to Use**:
- Starting fresh with a new knowledge base
- Training a minion for a specific domain/topic
- Need full control over collection configuration
- First-time RAG training

**Configuration Options**:

#### Collection Setup
- **Collection Name**: Custom name for the new ChromaDB collection
  - Example: `my-knowledge-base`, `technical-docs`, `company-policies`
- **Collection Description**: Optional description of what the collection will contain

#### Embedding Configuration
- **Embedding Model**: Choose the vector embedding model
  - `all-MiniLM-L6-v2` (Default) - Balanced performance
  - `all-mpnet-base-v2` (Higher Quality) - Better accuracy
  - `paraphrase-multilingual-MiniLM-L12-v2` - Multilingual support
  - `sentence-transformers/all-MiniLM-L12-v2` - Faster processing

#### Document Processing
- **Chunk Size**: Size of text chunks for embedding (100-2000 tokens)
- **Chunk Overlap**: Overlap between chunks for better context (0-200 tokens)
- **Top K Results**: Number of relevant chunks to retrieve (1-20)
- **Similarity Threshold**: Minimum similarity score for retrieval (0.1-1.0)

#### Retrieval Strategy
- **Semantic Search**: Pure vector similarity search
- **Hybrid Search**: Vector + keyword search combination
- **Rerank Search**: Initial retrieval + reranking for better results

#### Advanced Options
- **Contextual Compression**: Compress retrieved context to fit token limits
- **Source Citation**: Include source references in responses
- **Query Expansion**: Automatically expand queries with related terms

### 2. Use Existing Collection 📂

**Purpose**: Enhance an existing ChromaDB collection with new documents.

**When to Use**:
- Adding to an existing knowledge base
- Incremental training with new datasets
- Building upon previous RAG training
- Collaborative knowledge base development

**Configuration Options**:

#### Collection Selection
- **Existing Collection**: Choose from available ChromaDB collections
  - Shows collection name and document count
  - Example: `general-knowledge (1250 docs)`, `technical-docs (850 docs)`

#### Update Strategy
- **Append**: Add new documents to existing collection
  - Preserves all existing documents
  - Adds new documents alongside existing ones
  - Safe for incremental updates
  - ⚠️ **Warning**: May create duplicates if same documents exist

- **Replace All**: Replace entire collection with new dataset
  - ⚠️ **DESTRUCTIVE**: Permanently deletes all existing documents
  - Replaces with new dataset completely
  - Requires explicit confirmation
  - Use only when you want to completely refresh the collection

- **Smart Replace**: Intelligent document replacement
  - Compares new dataset with existing documents
  - Replaces documents with similar content/metadata
  - Adds new documents that don't exist
  - Keeps documents that don't match
  - Most intelligent option for updates

- **Replace by ID/Filter**: Selective document replacement
  - Replace specific documents by ID
  - Filter by metadata properties
  - Filter by date ranges
  - Custom filter expressions
  - Precise control over what gets replaced

#### Limited Advanced Options
- Only basic advanced options available
- Collection configuration inherited from existing collection
- Focus on document addition/update strategy

## Update Strategies Explained

### 🔄 **Append Strategy**
**What it does**: Adds new documents to the existing collection without removing anything.

**Example Scenario**:
```
Existing Collection: "company-policies" (320 docs)
New Dataset: "updated-hr-policies" (45 docs)
Result: "company-policies" (365 docs)
```

**Pros**:
- ✅ Safe - no data loss
- ✅ Preserves all existing knowledge
- ✅ Good for incremental updates

**Cons**:
- ⚠️ May create duplicates if same documents exist
- ⚠️ Collection grows indefinitely
- ⚠️ May include outdated information

**Best for**: Adding new documents, incremental updates, collaborative editing

---

### ⚠️ **Replace All Strategy**
**What it does**: Completely wipes the existing collection and replaces it with the new dataset.

**Example Scenario**:
```
Existing Collection: "technical-docs" (850 docs)
New Dataset: "updated-manual-v2" (320 docs)
Result: "technical-docs" (320 docs) - ALL PREVIOUS DATA LOST
```

**Pros**:
- ✅ Clean slate - no outdated information
- ✅ Consistent with new dataset
- ✅ No duplicates

**Cons**:
- ❌ **DESTRUCTIVE** - permanently deletes all existing data
- ❌ Cannot be undone
- ❌ Loses all previous knowledge

**Best for**: Complete collection refresh, major version updates, when you have backups

**⚠️ Safety Requirements**:
- Explicit user confirmation required
- Warning about data loss
- Backup recommendation
- Collection size display

---

### 🧠 **Smart Replace Strategy** (Recommended)
**What it does**: Intelligently compares and replaces documents based on content similarity and metadata.

**Example Scenario**:
```
Existing Collection: "product-docs" (500 docs)
New Dataset: "updated-product-docs" (450 docs)

Smart Analysis:
- 300 docs: Similar content → Replace with updated versions
- 150 docs: New content → Add to collection  
- 200 docs: No match → Keep existing
- 50 docs: Duplicates → Skip

Result: "product-docs" (650 docs)
```

**How it works**:
1. **Content Analysis**: Compare document content using embeddings
2. **Metadata Matching**: Match documents by source, date, type
3. **Similarity Scoring**: Calculate similarity scores
4. **Decision Matrix**: 
   - High similarity (>0.8) → Replace
   - Medium similarity (0.5-0.8) → User confirmation
   - Low similarity (<0.5) → Add as new
   - Exact match → Skip duplicate

**Pros**:
- ✅ Intelligent - preserves relevant data
- ✅ Updates outdated information
- ✅ Adds new content
- ✅ Prevents duplicates
- ✅ Safe - no accidental data loss

**Cons**:
- ⚠️ More complex processing
- ⚠️ Requires similarity thresholds
- ⚠️ May need user confirmation for edge cases

**Best for**: Most use cases, document updates, version control

---

### 🎯 **Replace by ID/Filter Strategy**
**What it does**: Selectively replace specific documents based on user-defined criteria (IDs, metadata, dates, custom filters).

**Example Scenario**:
```
Existing Collection: "product-docs" (500 docs)
User Filter: "source = 'old-manual' AND version < '2.0'"
System finds: 45 matching documents
Result: Replace 45 old manual docs, keep 455 others
```

**How it works**:
1. **User defines criteria**: Document IDs, metadata filters, date ranges, or custom expressions
2. **System finds matches**: Locates documents matching the criteria
3. **Selective replacement**: Only matching documents are replaced
4. **Preserve others**: All non-matching documents remain untouched

**Pros**:
- ✅ **Precise control** - replace exactly what you want
- ✅ **No AI dependency** - user controls the selection
- ✅ **Flexible filtering** - multiple filter types available
- ✅ **Predictable results** - you know what will be replaced
- ✅ **Safe** - only affects documents matching your criteria

**Cons**:
- ⚠️ Requires knowledge of document structure/metadata
- ⚠️ Manual work to define criteria
- ⚠️ May miss similar documents that don't match criteria

**Best for**: When you know exactly which documents need updating, have specific criteria, or want full control

**Filter Types Available**:
- **Document IDs**: `doc_001, doc_002, doc_003`
- **Metadata Filter**: `source = 'old-manual'`, `version contains '1.0'`
- **Date Range**: Documents created between `2023-01-01` and `2023-12-31`
- **Custom Filter**: `source == 'old-manual' AND version < '2.0'`

---

## Strategy Comparison

| Feature | Append | Replace All | Smart Replace | Replace by ID |
|---------|--------|-------------|---------------|---------------|
| **Data Safety** | ✅ Safe | ❌ Destructive | ✅ Safe | ✅ Safe |
| **User Control** | ⚠️ Low | ⚠️ Low | ⚠️ Medium | ✅ High |
| **AI Dependency** | ❌ None | ❌ None | ✅ Required | ❌ None |
| **Precision** | ⚠️ Low | ⚠️ Low | ⚠️ Medium | ✅ High |
| **Ease of Use** | ✅ Easy | ✅ Easy | ✅ Easy | ⚠️ Requires knowledge |
| **Best For** | Adding new docs | Complete refresh | Automatic updates | Precise control |

## Why Both Smart Replace AND Replace by ID?

### **Complementary Approaches**:
- **Smart Replace** = "Let AI figure it out" (automated, intelligent)
- **Replace by ID** = "I'll tell you exactly what to replace" (manual, precise)

### **Different Use Cases**:
- **Smart Replace**: When you trust AI similarity and want automation
- **Replace by ID**: When you need exact control and know your data structure

### **User Choice**:
- **Technical users** might prefer Replace by ID for precise control
- **Business users** might prefer Smart Replace for simplicity
- **Both options** give users the flexibility to choose their preferred approach

### For "Replace All" Strategy:
1. **Always backup** existing collection before replacement
2. **Verify dataset** contains all necessary documents
3. **Test on copy** before applying to production collection
4. **Document the change** for team awareness

### For "Append" Strategy:
1. **Check for duplicates** before adding
2. **Monitor collection size** to prevent bloat
3. **Regular cleanup** of outdated documents
4. **Version control** for document updates

### For "Smart Replace" Strategy:
1. **Review similarity thresholds** for your use case
2. **Test with sample data** first
3. **Monitor replacement decisions** for accuracy
4. **Adjust parameters** based on results

| Feature | Create New Collection | Use Existing Collection |
|---------|---------------------|------------------------|
| **Collection Setup** | ✅ Full configuration | ❌ Uses existing config |
| **Embedding Model** | ✅ Choose model | ❌ Inherited |
| **Document Processing** | ✅ Configure chunking | ❌ Inherited |
| **Retrieval Strategy** | ✅ Choose method | ❌ Inherited |
| **Collection Name** | ✅ Custom input | ❌ Pre-defined |
| **Update Strategy** | ❌ Not applicable | ✅ Append/Replace All/Smart Replace |
| **Advanced Options** | ✅ Full options | ⚠️ Limited options |
| **Data Safety** | ✅ No risk | ⚠️ Risk with Replace All |

## Technical Implementation

### Frontend Conditional Rendering

The modal uses Vue.js conditional rendering (`v-if`) to show different sections based on the selected strategy:

```vue
<!-- Create New Collection Configuration -->
<div v-if="newTraining.ragConfig.knowledgeBaseStrategy === 'create_new'">
  <!-- Collection name, description, embedding, processing, retrieval -->
</div>

<!-- Use Existing Collection Configuration -->
<div v-if="newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing'">
  <!-- Collection selection, update strategy -->
</div>
```

### Data Structure

```javascript
ragConfig: {
  // Knowledge Base Configuration
  knowledgeBaseStrategy: 'create_new', // 'create_new' or 'use_existing'
  existingCollection: '',
  collectionName: '',
  collectionDescription: '',
  updateStrategy: 'append', // 'append' or 'replace'
  
  // Embedding Configuration (Create New only)
  embeddingModel: 'all-MiniLM-L6-v2',
  
  // Document Processing (Create New only)
  chunkSize: 1000,
  chunkOverlap: 100,
  topK: 4,
  similarityThreshold: 0.7,
  
  // Retrieval Strategy (Create New only)
  retrievalMethod: 'semantic',
  
  // Advanced Options
  enableContextualCompression: true,
  enableSourceCitation: true,
  enableQueryExpansion: false
}
```

## User Experience Benefits

### Before (Issues)
- ❌ Both strategies showed identical configuration options
- ❌ Confusing interface - no clear distinction
- ❌ Users couldn't understand the difference
- ❌ Unnecessary configuration for existing collections

### After (Improvements)
- ✅ Clear visual distinction between strategies
- ✅ Relevant options only for each strategy
- ✅ Intuitive workflow based on user intent
- ✅ Reduced cognitive load and confusion

## Modal Behavior

### Closing Behavior
The modal has been configured to prevent accidental closure:
- ❌ **Click outside to close**: Disabled
- ❌ **Escape key to close**: Disabled
- ✅ **X button**: Enabled
- ✅ **Cancel button**: Enabled
- ✅ **Create Training button**: Enabled (after successful creation)

This ensures users don't lose their complex RAG configuration accidentally.

## Future Enhancements

### Planned Features
1. **Collection Preview**: Show sample documents from existing collections
2. **Performance Metrics**: Display collection performance statistics
3. **Batch Operations**: Support for multiple collection updates
4. **Collection Templates**: Pre-configured collection setups
5. **Migration Tools**: Convert between strategies

### Backend Integration
- ChromaDB collection management
- Vector embedding pipeline
- Document processing and chunking
- Retrieval strategy implementation
- Performance monitoring and metrics

## Related Documentation

- [RAG Training Architecture](./ARCHITECTURAL_PLAN/RAG_TRAINING_ARCHITECTURE.md)
- [ChromaDB Integration Guide](./CHROMADB_INTEGRATION.md)
- [Training Modal User Guide](./TRAINING_MODAL_GUIDE.md)
- [Minion Training Workflow](./MINION_TRAINING_WORKFLOW.md)

---

*Last Updated: December 2024*
*Version: 1.0*
