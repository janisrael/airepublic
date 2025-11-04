<template>
  <div>
  <Modal 
    :visible="showModal" 
    title="Refine Minion with External Training"
    size="large"
    :showFooter="true"
    :closeOnOverlay="false"
    :closeOnEscape="false"
    @close="closeModal"
  >
        <!-- Training Job Metadata -->
        <div class="training-metadata">
          <h3>Training Job Information</h3>
          <div class="metadata-grid">
            <div class="form-group">
              <label>Job Name <span class="required">*</span></label>
              <input 
                type="text" 
                v-model="newTraining.jobName" 
                placeholder="e.g., Refine Grafana with RAG"
                class="form-control"
                required
              >
              <small>Give your training job a descriptive name</small>
            </div>
            
            <div class="form-group">
              <label>Version</label>
              <input 
                type="text" 
                v-model="newTraining.version" 
                placeholder="e.g., v1.0, 2.1.3, beta"
                class="form-control"
              >
              <small>Version tag for the refined minion</small>
            </div>
            
            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="newTraining.description" 
                placeholder="Describe what this training job will accomplish..."
                class="form-control"
                rows="2"
              ></textarea>
              <small>Optional description of the training purpose</small>
            </div>
          </div>
        </div>

        <!-- Minion Selection -->
        <div class="form-group">
          <label>Base Minion <span class="required">*</span></label>
          <select v-model="newTraining.baseMinion" class="form-control" @change="onMinionSelect">
            <option value="">Select a minion to refine</option>
            <option v-for="minion in availableMinions" :key="minion.id" :value="minion.id">
              {{ minion.display_name }} ({{ minion.provider }})
            </option>
          </select>
          <small>Select the minion you want to refine with training</small>
        </div>

        <!-- Training Type Selection -->
        <div class="form-group">
          <label>Training Type</label>
          <div class="training-types">
            <label class="training-type-card" :class="{ active: newTraining.type === 'rag' }">
              <input type="radio" v-model="newTraining.type" value="rag" hidden>
              <div class="type-icon"><span class="material-icons-round">auto_stories</span></div>
              <h4>RAG Enhancement</h4>
              <p>Add knowledge base to minion</p>
            </label>
            
            <label class="training-type-card" :class="{ active: newTraining.type === 'lora' }">
              <input type="radio" v-model="newTraining.type" value="lora" hidden>
              <div class="type-icon"><span class="material-icons-round">auto_fix_high</span></div>
              <h4>LoRA Training</h4>
              <p>Enhance personality and style</p>
            </label>
            
            <label class="training-type-card" :class="{ active: newTraining.type === 'hybrid' }">
              <input type="radio" v-model="newTraining.type" value="hybrid" hidden>
              <div class="type-icon"><span class="material-icons-round">psychology</span></div>
              <h4>Hybrid Training</h4>
              <p>LoRA + RAG + External LLM</p>
            </label>
          </div>
        </div>

        <!-- Provider Selection -->
        <div class="form-group">
          <label>External Provider <span class="required">*</span></label>
          <select v-model="newTraining.provider" class="form-control" @change="onProviderSelect">
            <option value="">Select external provider</option>
            <option v-for="provider in availableProviders" :key="provider.name" :value="provider.name">
              {{ provider.displayName }}
            </option>
          </select>
          <small>Choose the external LLM provider for training</small>
        </div>

        <!-- Model Selection -->
        <div v-if="newTraining.provider" class="form-group">
          <label>Model <span class="required">*</span></label>
          <select v-model="newTraining.model" class="form-control">
            <option value="">Select model</option>
            <option v-for="model in availableModels" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
          <small>Select the specific model from the provider</small>
        </div>

        <!-- Dataset Selection (only for RAG and Hybrid) -->
        <div v-if="newTraining.type === 'rag' || newTraining.type === 'hybrid'" class="form-group">
          <label>Training Datasets <small>(Select multiple for combined training)</small></label>
          <div class="dataset-options">
            <!-- Existing Datasets -->
            <label class="dataset-option" v-for="dataset in availableDatasets" :key="dataset.id">
              <input type="checkbox" v-model="newTraining.selectedDatasets" :value="dataset.id" hidden>
              <div class="option-card">
                <Icon name="dataset" size="sm" color="primary" />
                <div class="dataset-info">
                  <span class="dataset-name">{{ dataset.name }}</span>
                  <span class="dataset-details">{{ dataset.sampleCount.toLocaleString() }} samples • {{ dataset.type }}</span>
                </div>
              </div>
            </label>
            
            <!-- Upload JSONL -->
            <label class="dataset-option">
              <input type="checkbox" v-model="newTraining.datasetType" value="upload" hidden>
              <div class="option-card">
                <Icon name="upload" size="sm" color="success" />
                <span>Upload JSONL File</span>
              </div>
            </label>
          </div>
          
          <!-- Selected Datasets Summary -->
          <div v-if="newTraining.selectedDatasets.length > 0" class="selected-datasets">
            <h4>Selected Datasets ({{ newTraining.selectedDatasets.length }})</h4>
            <div class="selected-list">
              <div v-for="datasetId in newTraining.selectedDatasets" :key="datasetId" class="selected-item">
                <span class="dataset-name">{{ getDatasetName(datasetId) }}</span>
                <span class="dataset-samples">{{ getDatasetSamples(datasetId).toLocaleString() }} samples</span>
                <button class="btn-icon" @click="removeDataset(datasetId)">
                  <Icon name="close" size="xs" color="danger" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Role Definition -->
        <div class="form-group">
          <label>Role Definition</label>
          <textarea 
            v-model="newTraining.roleDefinition" 
            placeholder="You are an advanced AI assistant specialized in..."
            class="form-control"
            rows="4"
          ></textarea>
          <small>Define the minion's personality, role, and behavior</small>
        </div>

        <!-- RAG/Hybrid Configuration Container -->
        <div v-if="newTraining.type === 'rag' || newTraining.type === 'hybrid'" id="rag-config-container">
          
          <!-- Model Parameters -->
          <div class="model-params">
            <h3>Model Parameters</h3>
            <div class="params-grid">
              <div class="form-group">
                <label>Temperature</label>
                <input type="number" v-model="newTraining.temperature" min="0.1" max="2.0" step="0.1" class="form-control">
                <small>Controls randomness (0.1 = focused, 2.0 = creative)</small>
              </div>
              <div class="form-group">
                <label>Top P</label>
                <input type="number" v-model="newTraining.top_p" min="0.1" max="1.0" step="0.1" class="form-control">
                <small>Controls diversity (0.1 = focused, 1.0 = diverse)</small>
              </div>
              <div class="form-group">
                <label>Max Tokens</label>
                <input type="number" v-model="newTraining.max_tokens" min="100" max="4096" step="100" class="form-control">
                <small>Maximum response length</small>
              </div>
            </div>
          </div>

          <!-- RAG Configuration -->
          <div class="rag-config">
            <h3><span class="material-icons-round">auto_stories</span> RAG Enhancement Configuration</h3>
            <p class="config-description">Configure how your minion will access and use knowledge bases</p>
            
            <!-- Knowledge Base Management -->
            <div class="knowledge-base-section">
              <!-- <h4>Knowledge Base</h4> -->
              <div class="form-group">
                <label>Knowledge Base Strategy</label>
                <div class="strategy-options">
                  <label class="strategy-option" :class="{ active: newTraining.ragConfig.knowledgeBaseStrategy === 'create_new' }">
                    <input type="radio" v-model="newTraining.ragConfig.knowledgeBaseStrategy" value="create_new" hidden>
                    <div class="option-card">
                      <span class="material-icons-round">add_circle</span>
                      <div class="option-info">
                        <span class="option-title">Create New Collection</span>
                        <span class="option-desc">Create a new ChromaDB collection for this training</span>
                      </div>
                    </div>
                  </label>
                  
                  <label class="strategy-option" :class="{ active: newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing' }">
                    <input type="radio" v-model="newTraining.ragConfig.knowledgeBaseStrategy" value="use_existing" hidden>
                    <div class="option-card">
                      <span class="material-icons-round">folder_open</span>
                      <div class="option-info">
                        <span class="option-title">Use Existing Collection</span>
                        <span class="option-desc">Add to an existing knowledge base</span>
                      </div>
                    </div>
                  </label>
                </div>
              </div>
              
              <!-- Create New Collection Configuration -->
              <div v-if="newTraining.ragConfig.knowledgeBaseStrategy === 'create_new'" class="create-new-config">
                <div class="form-group">
                  <label>Collection Name <span class="required">*</span></label>
                  <input 
                    type="text" 
                    v-model="newTraining.ragConfig.collectionName" 
                    class="form-control"
                    :class="{ 'error': collectionNameError }"
                    placeholder="e.g., my-knowledge-base"
                    @input="validateCollectionName"
                    required
                  >
                  <small v-if="!collectionNameError">Name for the new ChromaDB collection (3-512 characters, alphanumeric, dots, underscores, hyphens)</small>
                  <small v-if="collectionNameError" class="error-text">{{ collectionNameError }}</small>
                </div>
                
                <div class="form-group">
                  <label>Collection Description</label>
                  <textarea v-model="newTraining.ragConfig.collectionDescription" class="form-control" rows="2" placeholder="Describe what this knowledge base will contain..."></textarea>
                  <small>Optional description for the collection</small>
                </div>
                
                <!-- File Upload Section -->
                <div class="form-group">
                  <label>Upload Documents <span class="required">*</span></label>
                  <div class="file-upload">
                    <input 
                      type="file" 
                      @change="handleFileUpload" 
                      multiple 
                      accept=".md,.txt,.pdf,.doc,.docx" 
                      id="rag-file-upload"
                      ref="ragFileInput"
                    >
                    <label for="rag-file-upload" class="upload-btn">
                      <span class="material-icons-round">upload_file</span>
                      Upload Documents (PDF, DOC, TXT, MD)
                    </label>
                    <small>Upload documents to create the knowledge base. Supported formats: PDF, DOC, DOCX, TXT, MD</small>
                    
                    <!-- Uploaded Files List -->
                    <div v-if="uploadedFiles.length > 0" class="uploaded-files">
                      <div class="uploaded-files-header">
                        <span>{{ uploadedFiles.length }} file(s) selected</span>
                      </div>
                      <div class="file-list">
                        <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
                          <span class="material-icons-round">description</span>
                          <span class="file-name">{{ file.name }}</span>
                          <span class="file-size">({{ formatFileSize(file.size) }})</span>
                          <button @click="removeFile(index)" class="btn-icon" title="Remove file">
                            <span class="material-icons-round">close</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Use Existing Collection Configuration -->
              <div v-if="newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing'" class="use-existing-config">
                <div class="form-group">
                  <label>Existing Collection</label>
                  <select v-model="newTraining.ragConfig.existingCollection" class="form-control">
                    <option value="">Select existing collection</option>
                    <option v-for="collection in availableCollections" :key="collection.id" :value="collection.name">
                      {{ collection.name }} ({{ collection.documentCount }} docs)
                    </option>
                  </select>
                  <small>Choose an existing ChromaDB collection to enhance</small>
                </div>
                
                <div class="form-group">
                  <label>Update Strategy</label>
                  <div class="update-strategy-options">
                    <label class="strategy-option" :class="{ active: newTraining.ragConfig.updateStrategy === 'append' }">
                      <input type="radio" v-model="newTraining.ragConfig.updateStrategy" value="append" hidden>
                      <div class="option-card">
                        <span class="material-icons-round">add</span>
                        <div class="option-info">
                          <span class="option-title">Append</span>
                          <span class="option-desc">Add new documents to existing collection (Safe)</span>
                        </div>
                        <div class="option-status">
                          <span class="material-icons-round">check_circle</span>
                        </div>
                      </div>
                    </label>
                    
                    <label class="strategy-option" :class="{ active: newTraining.ragConfig.updateStrategy === 'replace_all' }">
                      <input type="radio" v-model="newTraining.ragConfig.updateStrategy" value="replace_all" hidden>
                      <div class="option-card">
                        <span class="material-icons-round">refresh</span>
                        <div class="option-info">
                          <span class="option-title">Replace All</span>
                          <span class="option-desc">⚠️ Wipes entire collection - DESTRUCTIVE</span>
                        </div>
                        <div class="option-status">
                          <span class="material-icons-round">warning</span>
                        </div>
                      </div>
                    </label>
                    
                    <label class="strategy-option" :class="{ active: newTraining.ragConfig.updateStrategy === 'smart_replace' }">
                      <input type="radio" v-model="newTraining.ragConfig.updateStrategy" value="smart_replace" hidden>
                      <div class="option-card">
                        <span class="material-icons-round">psychology</span>
                        <div class="option-info">
                          <span class="option-title">Smart Replace</span>
                          <span class="option-desc">Intelligent replacement based on similarity (Recommended)</span>
                        </div>
                        <div class="option-status">
                          <span class="material-icons-round">star</span>
                        </div>
                      </div>
                    </label>
                    
                    <label class="strategy-option" :class="{ active: newTraining.ragConfig.updateStrategy === 'replace_by_id' }">
                      <input type="radio" v-model="newTraining.ragConfig.updateStrategy" value="replace_by_id" hidden>
                      <div class="option-card">
                        <span class="material-icons-round">filter_list</span>
                        <div class="option-info">
                          <span class="option-title">Replace by ID/Filter</span>
                          <span class="option-desc">Selectively replace specific documents</span>
                        </div>
                        <div class="option-status">
                          <span class="material-icons-round">tune</span>
                        </div>
                      </div>
                    </label>
                  </div>
                  
                  <!-- Strategy Details -->
                  <div class="strategy-details">
                    <div v-if="newTraining.ragConfig.updateStrategy === 'append'" class="strategy-info append-info">
                      <h5>📄 Append Strategy</h5>
                      <p>Adds new documents to the existing collection without removing anything.</p>
                      <ul>
                        <li>✅ Safe - no data loss</li>
                        <li>✅ Preserves all existing knowledge</li>
                        <li>⚠️ May create duplicates if same documents exist</li>
                      </ul>
                    </div>
                    
                    <div v-if="newTraining.ragConfig.updateStrategy === 'replace_all'" class="strategy-info replace-all-info">
                      <h5>⚠️ Replace All Strategy</h5>
                      <p><strong>DESTRUCTIVE:</strong> Completely wipes the existing collection and replaces it with the new dataset.</p>
                      <ul>
                        <li>❌ Permanently deletes all existing data</li>
                        <li>❌ Cannot be undone</li>
                        <li>✅ Clean slate - no outdated information</li>
                      </ul>
                      <div class="warning-box">
                        <span class="material-icons-round">warning</span>
                        <strong>Warning:</strong> This action will permanently delete all documents in the selected collection. Make sure you have a backup!
                      </div>
                    </div>
                    
                    <div v-if="newTraining.ragConfig.updateStrategy === 'smart_replace'" class="strategy-info smart-replace-info">
                      <h5>🧠 Smart Replace Strategy</h5>
                      <p>Intelligently compares and replaces documents based on content similarity and metadata.</p>
                      <ul>
                        <li>✅ Intelligent - preserves relevant data</li>
                        <li>✅ Updates outdated information</li>
                        <li>✅ Adds new content</li>
                        <li>✅ Prevents duplicates</li>
                      </ul>
                      <div class="info-box">
                        <span class="material-icons-round">info</span>
                        <strong>How it works:</strong> Compares documents using embeddings, replaces similar ones, adds new ones, keeps unmatched ones.
                      </div>
                    </div>
                    
                    <div v-if="newTraining.ragConfig.updateStrategy === 'replace_by_id'" class="strategy-info replace-by-id-info">
                      <h5>🎯 Replace by ID/Filter Strategy</h5>
                      <p>Selectively replace specific documents based on IDs, metadata filters, or custom criteria.</p>
                      <ul>
                        <li>✅ Precise control - replace only what you want</li>
                        <li>✅ Preserves unrelated documents</li>
                        <li>✅ Flexible filtering options</li>
                        <li>⚠️ Requires knowledge of document structure</li>
                      </ul>
                      
                      <!-- Filter Configuration -->
                      <div class="filter-config">
                        <h6>Filter Configuration</h6>
                        <div class="filter-options">
                          <div class="form-group">
                            <label>Filter Type</label>
                            <select v-model="newTraining.ragConfig.filterType" class="form-control">
                              <option value="document_ids">Document IDs</option>
                              <option value="metadata_filter">Metadata Filter</option>
                              <option value="date_range">Date Range</option>
                              <option value="custom_filter">Custom Filter</option>
                            </select>
                          </div>
                          
                          <!-- Document IDs Filter -->
                          <div v-if="newTraining.ragConfig.filterType === 'document_ids'" class="form-group">
                            <label>Document IDs (comma-separated)</label>
                            <textarea v-model="newTraining.ragConfig.documentIds" class="form-control" rows="3" placeholder="doc_001, doc_002, doc_003"></textarea>
                            <small>Enter specific document IDs to replace</small>
                          </div>
                          
                          <!-- Metadata Filter -->
                          <div v-if="newTraining.ragConfig.filterType === 'metadata_filter'" class="form-group">
                            <label>Metadata Filter</label>
                            <div class="metadata-filter-grid">
                              <input v-model="newTraining.ragConfig.metadataKey" type="text" class="form-control" placeholder="Key (e.g., source)">
                              <select v-model="newTraining.ragConfig.metadataOperator" class="form-control">
                                <option value="equals">Equals</option>
                                <option value="contains">Contains</option>
                                <option value="starts_with">Starts With</option>
                                <option value="ends_with">Ends With</option>
                              </select>
                              <input v-model="newTraining.ragConfig.metadataValue" type="text" class="form-control" placeholder="Value (e.g., old-manual)">
                            </div>
                            <small>Filter documents by metadata properties</small>
                          </div>
                          
                          <!-- Date Range Filter -->
                          <div v-if="newTraining.ragConfig.filterType === 'date_range'" class="form-group">
                            <label>Date Range</label>
                            <div class="date-range-grid">
                              <input v-model="newTraining.ragConfig.dateFrom" type="date" class="form-control">
                              <input v-model="newTraining.ragConfig.dateTo" type="date" class="form-control">
                            </div>
                            <small>Replace documents within this date range</small>
                          </div>
                          
                          <!-- Custom Filter -->
                          <div v-if="newTraining.ragConfig.filterType === 'custom_filter'" class="form-group">
                            <label>Custom Filter Expression</label>
                            <textarea v-model="newTraining.ragConfig.customFilter" class="form-control" rows="2" placeholder="e.g., source == 'old-manual' AND version < '2.0'"></textarea>
                            <small>Advanced: Use custom filter expressions (requires technical knowledge)</small>
                          </div>
                        </div>
                      </div>
                      
                      <div class="info-box">
                        <span class="material-icons-round">info</span>
                        <strong>How it works:</strong> Only documents matching your filter criteria will be replaced. All other documents remain untouched.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Embedding Configuration (only for Create New) -->
            <div v-if="newTraining.ragConfig.knowledgeBaseStrategy === 'create_new'" class="embedding-section">
              <h4>Embedding Model</h4>
              <div class="form-group">
                <select v-model="newTraining.ragConfig.embeddingModel" class="form-control">
                  <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (Default)</option>
                  <option value="all-mpnet-base-v2">all-mpnet-base-v2 (Higher Quality)</option>
                  <option value="paraphrase-multilingual-MiniLM-L12-v2">Multilingual MiniLM</option>
                  <option value="sentence-transformers/all-MiniLM-L12-v2">MiniLM L12 (Faster)</option>
                </select>
                <small>Choose the embedding model for vector generation</small>
              </div>
            </div>

            <!-- Document Processing (only for Create New) -->
            <div v-if="newTraining.ragConfig.knowledgeBaseStrategy === 'create_new'" class="document-processing-section">
              <h4>Document Processing</h4>
              <div class="params-grid">
            <div class="form-group">
              <label>Chunk Size</label>
                  <input type="number" v-model="newTraining.ragConfig.chunkSize" min="100" max="2000" step="50" class="form-control">
                  <small>Size of text chunks for embedding (100-2000 tokens)</small>
                </div>
                <div class="form-group">
                  <label>Chunk Overlap</label>
                  <input type="number" v-model="newTraining.ragConfig.chunkOverlap" min="0" max="200" step="10" class="form-control">
                  <small>Overlap between chunks for better context (0-200 tokens)</small>
            </div>
            <div class="form-group">
              <label>Top K Results</label>
                  <input type="number" v-model="newTraining.ragConfig.topK" min="1" max="20" step="1" class="form-control">
                  <small>Number of relevant chunks to retrieve (1-20)</small>
                </div>
                <div class="form-group">
                  <label>Similarity Threshold</label>
                  <input type="number" v-model="newTraining.ragConfig.similarityThreshold" min="0.1" max="1.0" step="0.05" class="form-control">
                  <small>Minimum similarity score for retrieval (0.1-1.0)</small>
                </div>
              </div>
            </div>

            <!-- Retrieval Strategy (only for Create New) -->
            <div v-if="newTraining.ragConfig.knowledgeBaseStrategy === 'create_new'" class="retrieval-strategy-section">
              <h4>Retrieval Strategy</h4>
              <div class="retrieval-options">
                <label class="retrieval-option" :class="{ active: newTraining.ragConfig.retrievalMethod === 'semantic' }">
                  <input type="radio" v-model="newTraining.ragConfig.retrievalMethod" value="semantic" hidden>
                  <div class="option-card">
                    <span class="material-icons-round">search</span>
                    <div class="option-info">
                      <span class="option-title">Semantic Search</span>
                      <span class="option-desc">Pure vector similarity search</span>
                    </div>
                  </div>
                </label>
                
                <label class="retrieval-option" :class="{ active: newTraining.ragConfig.retrievalMethod === 'hybrid' }">
                  <input type="radio" v-model="newTraining.ragConfig.retrievalMethod" value="hybrid" hidden>
                  <div class="option-card">
                    <span class="material-icons-round">merge</span>
                    <div class="option-info">
                      <span class="option-title">Hybrid Search</span>
                      <span class="option-desc">Vector + keyword search</span>
                    </div>
                  </div>
                </label>
                
                <label class="retrieval-option" :class="{ active: newTraining.ragConfig.retrievalMethod === 'rerank' }">
                  <input type="radio" v-model="newTraining.ragConfig.retrievalMethod" value="rerank" hidden>
                  <div class="option-card">
                    <span class="material-icons-round">sort</span>
                    <div class="option-info">
                      <span class="option-title">Rerank Search</span>
                      <span class="option-desc">Initial retrieval + reranking</span>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            <!-- Advanced RAG Options -->
            <div class="advanced-rag-section">
              <h4>Advanced Options</h4>
              <div class="advanced-options-grid">
                <label class="advanced-option" :class="{ active: newTraining.ragConfig.enableContextualCompression }">
                  <input type="checkbox" v-model="newTraining.ragConfig.enableContextualCompression" @change="debugCheckbox('contextualCompression')" hidden>
                  <div class="option-card">
                    <span class="material-icons-round">compress</span>
                    <div class="option-info">
                      <span class="option-title">Contextual Compression</span>
                      <span class="option-desc">Compress retrieved context to fit within token limits</span>
                    </div>
                    <div class="option-status">
                      <span class="material-icons-round">{{ newTraining.ragConfig.enableContextualCompression ? 'check_circle' : 'radio_button_unchecked' }}</span>
                    </div>
                  </div>
                </label>
                
                <label class="advanced-option" :class="{ active: newTraining.ragConfig.enableSourceCitation }">
                  <input type="checkbox" v-model="newTraining.ragConfig.enableSourceCitation" @change="debugCheckbox('sourceCitation')" hidden>
                  <div class="option-card">
                    <span class="material-icons-round">source</span>
                    <div class="option-info">
                      <span class="option-title">Source Citation</span>
                      <span class="option-desc">Include source references in responses</span>
                    </div>
                    <div class="option-status">
                      <span class="material-icons-round">{{ newTraining.ragConfig.enableSourceCitation ? 'check_circle' : 'radio_button_unchecked' }}</span>
                    </div>
                  </div>
                </label>
                
                <label class="advanced-option" :class="{ active: newTraining.ragConfig.enableQueryExpansion }">
                  <input type="checkbox" v-model="newTraining.ragConfig.enableQueryExpansion" @change="debugCheckbox('queryExpansion')" hidden>
                  <div class="option-card">
                    <span class="material-icons-round">expand_more</span>
                    <div class="option-info">
                      <span class="option-title">Query Expansion</span>
                      <span class="option-desc">Automatically expand queries with related terms</span>
                    </div>
                    <div class="option-status">
                      <span class="material-icons-round">{{ newTraining.ragConfig.enableQueryExpansion ? 'check_circle' : 'radio_button_unchecked' }}</span>
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- LoRA Configuration Container -->
        <div v-if="newTraining.type === 'lora' || newTraining.type === 'hybrid'" id="lora-config-container">
          <div class="config-header">
            <h3><span class="material-icons-round">auto_fix_high</span> LoRA Style Enhancement</h3>
            <p class="config-description">Enhance your minion's personality and communication style</p>
          </div>
          
          <!-- Style Analysis & Enhancement Controls -->
          <div class="lora-controls">
            <div class="control-group">
              <label for="styleSensitivity">Style Analysis Sensitivity</label>
              <div class="slider-group">
                <input 
                  id="styleSensitivity"
                  type="range" 
                  min="0.1" 
                  max="1.0" 
                  step="0.1" 
                  v-model="newTraining.loraConfig.styleSensitivity"
                />
                <span class="slider-value">{{ newTraining.loraConfig.styleSensitivity }}</span>
                <span class="slider-label">Sensitivity</span>
              </div>
              <p class="helper-text">Higher values create stronger personality amplification</p>
            </div>

            <div class="control-group">
              <label for="enhancementIntensity">Enhancement Intensity</label>
              <div class="slider-group">
                <input 
                  id="enhancementIntensity"
                  type="range" 
                  min="0.5" 
                  max="2.0" 
                  step="0.1" 
                  v-model="newTraining.loraConfig.enhancementIntensity"
                />
                <span class="slider-value">{{ newTraining.loraConfig.enhancementIntensity }}</span>
                <span class="slider-label">Intensity</span>
              </div>
              <p class="helper-text">Controls the intensity of LoRA-style adaptations</p>
            </div>
          </div>
          
          <!-- Personality Traits Selection -->
          <div class="traits-section">
            <label class="traits-label">
              <span class="material-icons-round">psychology</span>
              Select Personality Traits
            </label>
            <!-- Trait Slots System -->
            <div class="trait-slots-header">
              <h4><span class="material-icons-round">account_tree</span> Trait Specialization</h4>
              <div class="slot-info">
                <span class="slots-used">{{ newTraining.loraConfig.selectedTraits.length }}/{{ maxTraitSlots }} Slots Used</span>
                <span class="trait-points-info">{{ intensityPointsBalance }}/{{ userRankPoints }} Points Remaining</span>
                <span class="training-level">Level {{ minionTrainingLevel }} Minion</span>
              </div>
            </div>

            <!-- Available Trait Slots -->
            <div class="available-slots">
              <div 
                v-for="slotNumber in 5" 
                :key="slotNumber" 
                class="trait-slot"
                :class="{ 
                  'filled': slotNumber <= newTraining.loraConfig.selectedTraits.length,
                  'available': slotNumber <= maxTraitSlots && slotNumber > newTraining.loraConfig.selectedTraits.length,
                  'locked': slotNumber > maxTraitSlots
                }"
              >
                <span class="material-icons-round">
                  {{ slotNumber <= newTraining.loraConfig.selectedTraits.length ? 'check_circle' : 
                     slotNumber <= maxTraitSlots ? 'radio_button_unchecked' : 'lock' }}
                </span>
                <span class="slot-number">Trait {{ slotNumber }}</span>
              </div>
            </div>

            <!-- Compatibility Analysis Perk -->
            <div class="compatibility-perk-section">
              <div class="perk-header">
                <h4><span class="material-icons-round">analytics</span> Advanced Compatibility Analysis</h4>
                <button 
                  class="perk-toggle-btn"
                  :class="{ 'unlocked': hasCompatibilityAnalysis }"
                  :disabled="!canUnlockCompatibilityAnalysis"
                  @click="toggleCompatibilityAnalysis"
                >
                  <span class="material-icons-round">{{ hasCompatibilityAnalysis ? 'visibility' : 'visibility_off' }}</span>
                  {{ hasCompatibilityAnalysis ? 'Analysis Active' : 'Unlock Analysis (3 Points)' }}
                </button>
              </div>
              
              <div v-if="hasCompatibilityAnalysis" class="compatibility-analysis">
                <div class="analysis-section">
                  <h5>Trait Compatibility Score</h5>
                  <div class="compatibility-meter">
                    <div class="meter-fill" :style="{ width: compatibilityPercentage + '%' }"></div>
                    <span class="meter-label">{{ compatibilityScore }}% Effectiveness</span>
                  </div>
                </div>
                
                <div v-if="newTraining.loraConfig.selectedTraits.length > 0" class="detailed-analysis">
                  <h5>Detailed Analysis</h5>
                  <div class="analysis-items">
                    <div v-for="analysis in detailedCompatibilityAnalysis" :key="analysis.calculation" class="analysis-item">
                      <span class="analysis-icon" :class="analysis.type">
                        <span class="material-icons-round">{{ analysis.type === 'synergy' ? 'trending_up' : 'trending_down' }}</span>
                      </span>
                      <span class="analysis-text">{{ analysis.description }}</span>
                      <span class="analysis-impact">{{ analysis.impact > 0 ? '+' : '' }}{{ analysis.impact }}%</span>
                    </div>
                  </div>
                </div>
                
                <div class="optimization-suggestions">
                  <h5>Optimization Suggestions</h5>
                  <div class="suggestion">💡 {{ optimizationSuggestion }}</div>
                </div>
              </div>
            </div>

            <div class="traits-grid">
              <div v-for="(trait, index) in traitOptions" :key="`trait-${index}-${trait.value}`" class="trait-card">
                <label :for="`trait-${trait.value}`">
                  <input 
                    :id="`trait-${trait.value}`"
                    type="checkbox" 
                    :value="trait.value" 
                    v-model="newTraining.loraConfig.selectedTraits"
                    :disabled="!canSelectTrait(trait.value)"
                    hidden
                  >
                  <label class="trait-content" :for="`trait-${trait.value}`" :data-selected="newTraining.loraConfig.selectedTraits.includes(trait.value)">
                    <span class="trait-icon">
                      <span class="material-icons-round">{{ getTraitIcon(trait.value) }}</span>
                    </span>
                    <span class="trait-name">{{ trait.label }}</span>
                    <span class="trait-description">{{ getTraitDescription(trait.value) }}</span>
                    
                    <!-- Intensity Allocation -->
                    <div v-if="newTraining.loraConfig.selectedTraits.includes(trait.value)" class="trait-intensity">
                      <input 
                        type="range" 
                        :min="1" 
                        :max="10" 
                        step="1"
                        v-model="newTraining.loraConfig.traitIntensities[trait.value]"
                        class="trait-intensity-slider"
                        @input="updateIntensityDistribution"
                      >
                      <span class="intensity-value">{{ newTraining.loraConfig.traitIntensities[trait.value] || 5 }}</span>
                    </div>
                  </label>
                </label>
              </div>
            </div>

            <!-- Points System Display -->
            <div class="points-summary">
              <div class="points-row">
                <span class="intensity-points"><span class="material-icons-round">grade</span> Intensity Distribution: {{ totalTraitIntensity }}/10 Points</span>
                <span class="balance-info"><span class="material-icons-round">account_balance</span> Remaining: {{ intensityPointsBalance }} Points</span>
              </div>
              <div class="status-indicators">
                <span class="points-status" :class="{ 'over-capacity': totalTraitIntensity > 10 }">
                  {{ totalTraitIntensity > 10 ? 'Over Capacity!' : totalTraitIntensity === 10 ? 'Perfect Distribution' : `Allocate ${10 - totalTraitIntensity} more points` }}
                </span>
                <span class="compatibility-status" :class="compatibilityClass">
                  {{ compatibilityText }}
                </span>
              </div>
            </div>
            
            <p class="helper-text">Select traits up to your minion's level limit, then allocate intensity points (max 10 total)</p>
          </div>
        </div>

    
    <template #footer>
      <!-- Debug Info -->
      <div v-if="!canStartTraining" class="debug-info">
        <small class="text-muted">
          Missing: 
          <span v-if="!newTraining.jobName.trim()">Job Name, </span>
          <span v-if="!newTraining.baseMinion">Base Minion, </span>
          <span v-if="!newTraining.provider">Provider, </span>
          <span v-if="!newTraining.model">Model, </span>
          <!-- Only show datasets error for RAG/Hybrid training -->
          <span v-if="(newTraining.type === 'rag' || newTraining.type === 'hybrid') && newTraining.selectedDatasets.length === 0 && uploadedFiles.length === 0">Datasets or Files, </span>
          <span v-if="(newTraining.type === 'rag' || newTraining.type === 'hybrid') && newTraining.ragConfig.knowledgeBaseStrategy === 'create_new' && uploadedFiles.length === 0 && newTraining.selectedDatasets.length === 0">Upload Files, </span>
          <!-- Show RAG config error for RAG/Hybrid training -->
          <span v-if="(newTraining.type === 'rag' || newTraining.type === 'hybrid') && newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing' && !newTraining.ragConfig.existingCollection">Existing Collection, </span>
          <span v-if="(newTraining.type === 'rag' || newTraining.type === 'hybrid') && newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing' && !newTraining.ragConfig.updateStrategy">Update Strategy, </span>
          <span v-if="(newTraining.type === 'rag' || newTraining.type === 'hybrid') && newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing' && newTraining.ragConfig.updateStrategy === 'replace_by_id' && !hasValidFilterConfig()">Filter Config</span>
        </small>
      </div>
      
      <button class="btn btn-secondary" @click="closeModal">
        Cancel
      </button>
      <button class="btn btn-primary" @click="createTrainingJob" :disabled="!canStartTraining">
        Create Training
      </button>
    </template>
  </Modal>
    <!-- Duplicate Training Warning Modal (NEW) -->
    <DuplicateTrainingWarning
    :showModal="duplicateWarningVisible"
    :duplicateInfo="duplicateValidationResult?.duplicateInfo"
    :recommendation="duplicateValidationResult?.recommendation"
    :warningMessage="duplicateValidationResult?.message"
    @cancel="handleDuplicateCancel"
    @overwrite="handleDuplicateOverwrite"
    @create-new="handleDuplicateCreateNew"
    @proceed="handleDuplicateProceed"
  />
</div>
</template>

<script>
import Icon from './Icon.vue'
import Modal from './Modal.vue'
import DuplicateTrainingWarning from './DuplicateTrainingWarning.vue'
import RAGTrainingValidator from '../services/RAGTrainingValidator.js'

export default {
  name: 'ExternalTrainingModal',
  components: {
    Icon,
    Modal,
    DuplicateTrainingWarning
  },
  props: {
    showModal: {
      type: Boolean,
      default: false
    },
    availableMinions: {
      type: Array,
      default: () => []
    },
    availableDatasets: {
      type: Array,
      default: () => []
    },
    initialData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      newTraining: {
        jobName: '',
        description: '',
        version: '',
        type: 'rag',
        baseMinion: '',
        provider: '',
        model: '',
        selectedDatasets: [],
        datasetType: 'upload',
        roleDefinition: '',
        temperature: 0.7,
        top_p: 0.9,
        max_tokens: 1024,
        ragConfig: {
          // Knowledge Base Configuration
          knowledgeBaseStrategy: 'create_new', // 'create_new' or 'use_existing'
          existingCollection: '',
          collectionName: '',
          collectionDescription: '',
          updateStrategy: 'smart_replace', // 'append', 'replace_all', 'smart_replace', or 'replace_by_id'
          
          // Filter Configuration (for replace_by_id strategy)
          filterType: 'document_ids', // 'document_ids', 'metadata_filter', 'date_range', 'custom_filter'
          documentIds: '',
          metadataKey: '',
          metadataOperator: 'equals',
          metadataValue: '',
          dateFrom: '',
          dateTo: '',
          customFilter: '',
          
          // Embedding Configuration
          embeddingModel: 'all-MiniLM-L6-v2',
          
          // Document Processing
          chunkSize: 1000,
          chunkOverlap: 100,
          topK: 4,
          similarityThreshold: 0.7,
          
          // Retrieval Strategy
          retrievalMethod: 'semantic', // 'semantic', 'hybrid', 'rerank'
          
          // Advanced Options
          enableContextualCompression: true,
          enableSourceCitation: true,
          enableQueryExpansion: false
        },
        loraConfig: {
          styleSensitivity: 0.7,
          enhancementIntensity: 1.0,
          selectedTraits: [],
          traitIntensities: {},
          compatibilityAnalysisUnlocked: false
        }
      },
      availableProviders: [
        { name: 'openai', displayName: 'OpenAI' },
        { name: 'anthropic', displayName: 'Anthropic (Claude)' },
        { name: 'nvidia', displayName: 'NVIDIA (Nemotron)' }
      ],
      availableModels: [],
      availableCollections: [
        { id: 1, name: 'general-knowledge', documentCount: 1250 },
        { id: 2, name: 'technical-docs', documentCount: 850 },
        { id: 3, name: 'company-policies', documentCount: 320 },
        { id: 4, name: 'user-manuals', documentCount: 180 }
      ],
      traitOptions: [
        { value: 'professional', label: 'Professional' },
        { value: 'friendly', label: 'Friendly' },
        { value: 'technical', label: 'Technical' },
        { value: 'creative', label: 'Creative' },
        { value: 'analytical', label: 'Analytical' },
        { value: 'supportive', label: 'Supportive' }
      ],
      // Validation states
      collectionNameError: null,
      // Duplicate training validation
      duplicateWarningVisible: false,
      duplicateValidationResult: null,
      // File upload
      uploadedFiles: []
    }
  },
  computed: {
    canStartTraining() {
      const hasJobName = !!this.newTraining.jobName.trim()
      const hasBaseMinion = !!this.newTraining.baseMinion
      const hasProvider = !!this.newTraining.provider
      const hasModel = !!this.newTraining.model
      
      // LoRA training doesn't require datasets
      const hasDatasets = (this.newTraining.type === 'lora') 
        ? true // LoRA doesn't need datasets
        : (this.newTraining.selectedDatasets.length > 0 || this.uploadedFiles.length > 0) // RAG/Hybrid need datasets OR uploaded files
      
      // For RAG/Hybrid training, check if existing collection is selected when using existing strategy
      // OR if creating new collection, check for uploaded files or datasets
      const hasValidRAGConfig = (this.newTraining.type === 'rag' || this.newTraining.type === 'hybrid')
        ? (this.newTraining.ragConfig.knowledgeBaseStrategy === 'create_new' && 
           (this.uploadedFiles.length > 0 || this.newTraining.selectedDatasets.length > 0)) || // Create new: need files or datasets
          (this.newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing' && 
           !!this.newTraining.ragConfig.existingCollection &&
           !!this.newTraining.ragConfig.updateStrategy &&
           this.hasValidFilterConfig())
        : true
      
      // Validate collection name for create_new strategy
      const hasValidCollectionName = (this.newTraining.type === 'rag' || this.newTraining.type === 'hybrid')
        ? this.newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing' || 
          (this.newTraining.ragConfig.knowledgeBaseStrategy === 'create_new' && this.validateCollectionName())
        : true
      
      // Validate uploaded files for create_new strategy
      const hasUploadedFiles = (this.newTraining.type === 'rag' || this.newTraining.type === 'hybrid')
        ? this.newTraining.ragConfig.knowledgeBaseStrategy === 'use_existing' || // Use existing doesn't need files
          (this.newTraining.ragConfig.knowledgeBaseStrategy === 'create_new' && 
           (this.uploadedFiles.length > 0 || this.newTraining.selectedDatasets.length > 0)) // Create new: need files OR datasets
        : true
      
      // Additional validation for LoRA: check intensity allocation
      const validIntensity = (this.newTraining.type === 'lora') 
        ? this.totalTraitIntensity <= 10 
        : true
      
      return hasJobName && hasBaseMinion && hasProvider && hasModel && hasDatasets && hasValidRAGConfig && hasValidCollectionName && hasUploadedFiles && validIntensity
    },
    
    // Calculate minion training level (placeholder - should come from backend)
    minionTrainingLevel() {
      // TODO: This should be calculated from actual training history
      // For now, simulate based on base minion selection
      return this.initialData?.trainingLevel || 1
    },
    
    // Calculate maximum trait slots based on training level
    maxTraitSlots() {
      const level = this.minionTrainingLevel
      if (level >= 30) return 5
      if (level >= 25) return 4
      if (level >= 20) return 3
      if (level >= 15) return 2
      if (level >= 10) return 1
      return 0 // Level 1-9: No trait slots
    },
    
    // Calculate total intensity points allocated
    totalTraitIntensity() {
      const intensities = this.newTraining.loraConfig.traitIntensities || {}
      return Object.values(intensities).reduce((sum, intensity) => sum + (intensity || 0), 0)
    },
    
    // Calculate maximum trait points available (for future use)
    maxTraitPoints() {
      // This will be increased with minion XP/training progress
      return this.minionTrainingLevel * 10 + 50 // Level 1 = 60 points, Level 10 = 150 points
    },
    
    // Calculate available trait points (remaining)
    availableTraitPoints() {
      // Cost: Each trait costs points based on complexity
      const baseCostPerTrait = 10
      const usedPoints = this.newTraining.loraConfig.selectedTraits.length * baseCostPerTrait
      return this.maxTraitPoints - usedPoints
    },
    
    // Calculate trait compatibility and relationships
    compatibilityClass() {
      const traits = this.newTraining.loraConfig.selectedTraits
      if (traits.length <= 1) return 'neutral'
      
      const compatibility = this.calculateTraitCompatibility(traits)
      if (compatibility > 0) return 'compatible'
      if (compatibility < 0) return 'conflicting'
      return 'neutral'
    },
    
    // Generate compatibility text
    compatibilityText() {
      const traits = this.newTraining.loraConfig.selectedTraits
      if (traits.length <= 1) return 'Single trait selected'
      
      const compatibility = this.calculateTraitCompatibility(traits)
      const synergyBonus = Math.round(compatibility * 100)
      
      if (compatibility > 0) {
        return `Synergy Bonus: +${synergyBonus}% effectiveness!`
      } else if (compatibility < 0) {
        return `Trait Conflict: ${Math.abs(synergyBonus)}% penalty`
      }
      return 'Balanced trait combination'
    },
    
    // Calculate remaining intensity points (User rank points - total allocated)
    intensityPointsBalance() {
      return Math.max(0, this.userRankPoints - this.totalTraitIntensity)
    },
    
    // User rank-based points (simplified for testing)
    userRankPoints() {
      // TODO: This should come from actual user rank/achievement system
      return 10 // Default points for testing
    },
    
    // Compatibility Analysis Perk Properties
    hasCompatibilityAnalysisUnlocked() {
      return this.newTraining.loraConfig.compatibilityAnalysisUnlocked
    },
    
    canUnlockCompatibilityAnalysis() {
      return !this.hasCompatibilityAnalysisUnlocked && this.intensityPointsBalance >= 3
    },
    
    compatibilityPercentage() {
      if (this.newTraining.loraConfig.selectedTraits.length <= 1) return 100
      const compatibility = this.calculateTraitCompatibility(this.newTraining.loraConfig.selectedTraits)
      return Math.max(0, Math.min(100, (compatibility * 100) + 100))
    },
    
    compatibilityScore() {
      return Math.round(this.compatibilityPercentage)
    },
    
    detailedCompatibilityAnalysis() {
      const traits = this.newTraining.loraConfig.selectedTraits
      const analysis = []
      
      // Check each trait pair for synergy/conflict
      for (let i = 0; i < traits.length; i++) {
        for (let j = i + 1; j < traits.length; j++) {
          const trait1 = traits[i]
          const trait2 = traits[j]
          const synergy = this.getTraitSynergy(trait1, trait2)
          
          if (synergy !== 0) {
            analysis.push({
              calculation: `${trait1}+${trait2}`,
              description: this.getSynergyDescription(trait1, trait2),
              impact: Math.round(synergy * 100),
              type: synergy > 0 ? 'synergy' : 'conflict'
            })
          }
        }
      }
      
      return analysis
    },
    
    optimizationSuggestion() {
      const traits = this.newTraining.loraConfig.selectedTraits
      if (traits.length === 0) return "Select at least one trait to begin analysis"
      if (traits.length === 1) return "Consider adding compatible traits for synergy bonuses"
      
      const compatibility = this.calculateTraitCompatibility(traits)
      if (compatibility > 0.1) return "Excellent synergy! Your trait combination is highly effective"
      if (compatibility < -0.1) return "Consider replacing conflicting traits for better effectiveness"
      return "Balanced combination. Consider adding more traits for specialization"
    }
  },
  watch: {
    showModal(newVal) {
      console.log('📝 showModal watcher triggered:', newVal, 'initialData:', this.initialData);
      if (newVal && this.initialData && Object.keys(this.initialData).length > 0) {
        console.log('📝 Modal opened, populating with initial data:', this.initialData);
        // Use nextTick to ensure DOM is updated
        this.$nextTick(() => {
          this.populateForm(this.initialData);
        });
      }
    }
  },
  mounted() {
    console.log('📝 ExternalTrainingModal mounted, initialData:', this.initialData);
    if (this.initialData && Object.keys(this.initialData).length > 0) {
      console.log('📝 Modal mounted with initial data, populating form');
      this.populateForm(this.initialData);
    }
  },
  methods: {
    // File upload handlers
    handleFileUpload(event) {
      const files = Array.from(event.target.files || [])
      if (files.length === 0) return
      
      // Validate file types
      const allowedTypes = ['.md', '.txt', '.pdf', '.doc', '.docx']
      const validFiles = files.filter(file => {
        const ext = '.' + file.name.split('.').pop().toLowerCase()
        return allowedTypes.includes(ext)
      })
      
      if (validFiles.length !== files.length) {
        alert('Some files were skipped. Only PDF, DOC, DOCX, TXT, and MD files are supported.')
      }
      
      // Add to uploaded files list
      this.uploadedFiles = [...this.uploadedFiles, ...validFiles]
    },
    
    removeFile(index) {
      this.uploadedFiles.splice(index, 1)
      // Reset file input if all files removed
      if (this.uploadedFiles.length === 0 && this.$refs.ragFileInput) {
        this.$refs.ragFileInput.value = ''
      }
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    },
    
    // Validate filter configuration for replace_by_id strategy
    hasValidFilterConfig() {
      if (this.newTraining.ragConfig.updateStrategy !== 'replace_by_id') {
        return true // Not using replace_by_id, so no filter validation needed
      }
      
      const filterType = this.newTraining.ragConfig.filterType
      
      switch (filterType) {
        case 'document_ids':
          return !!this.newTraining.ragConfig.documentIds.trim()
        case 'metadata_filter':
          return !!this.newTraining.ragConfig.metadataKey.trim() && 
                 !!this.newTraining.ragConfig.metadataValue.trim()
        case 'date_range':
          return !!this.newTraining.ragConfig.dateFrom && 
                 !!this.newTraining.ragConfig.dateTo
        case 'custom_filter':
          return !!this.newTraining.ragConfig.customFilter.trim()
        default:
          return false
      }
    },
    
    // Validate collection name according to ChromaDB requirements
    validateCollectionName() {
      const name = this.newTraining.ragConfig.collectionName.trim()
      
      if (!name) {
        this.collectionNameError = 'Collection name is required'
        return false
      }
      
      if (name.length < 3) {
        this.collectionNameError = 'Collection name must be at least 3 characters long'
        return false
      }
      
      if (name.length > 512) {
        this.collectionNameError = 'Collection name must be 512 characters or less'
        return false
      }
      
      // ChromaDB naming rules: [a-zA-Z0-9._-], starting and ending with [a-zA-Z0-9]
      const validPattern = /^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$/
      if (!validPattern.test(name)) {
        this.collectionNameError = 'Collection name must contain only letters, numbers, dots, underscores, and hyphens. Must start and end with a letter or number.'
        return false
      }
      
      this.collectionNameError = null
      return true
    },
    
    // Validate for duplicate training (NEW - Additional validation)
    async validateForDuplicates() {
      if (this.newTraining.type !== 'rag') {
        return { isDuplicate: false, recommendation: 'proceed' }
      }
      
      try {
        const validator = new RAGTrainingValidator()
        const validationResult = await validator.validateTrainingRequest({
          minionId: this.newTraining.baseMinion,
          selectedDatasets: this.newTraining.selectedDatasets,
          ragConfig: this.newTraining.ragConfig
        })
        
        return validationResult
      } catch (error) {
        console.warn('Duplicate validation failed:', error)
        return { isDuplicate: false, recommendation: 'proceed' }
      }
    },
    
    populateForm(data) {
      console.log('📝 populateForm called with data:', data);
      
      // Populate all form fields with initial data
      if (data.jobName) {
        console.log('📝 Setting jobName:', data.jobName);
        this.newTraining.jobName = data.jobName;
      }
      if (data.description) {
        console.log('📝 Setting description:', data.description);
        this.newTraining.description = data.description;
      }
      if (data.minionId) {
        console.log('📝 Setting baseMinion:', data.minionId);
        this.newTraining.baseMinion = data.minionId;
      }
      if (data.provider) {
        console.log('📝 Setting provider:', data.provider);
        this.newTraining.provider = data.provider;
        // Update available models for the selected provider
        this.updateAvailableModels();
      }
      if (data.model) {
        console.log('📝 Setting model:', data.model);
        this.newTraining.model = data.model;
      }
      if (data.type) {
        console.log('📝 Setting type:', data.type);
        this.newTraining.type = data.type;
      }
      if (data.selectedDatasets) {
        console.log('📝 Setting selectedDatasets:', data.selectedDatasets);
        this.newTraining.selectedDatasets = [...data.selectedDatasets];
      }
      if (data.roleDefinition) {
        console.log('📝 Setting roleDefinition:', data.roleDefinition);
        this.newTraining.roleDefinition = data.roleDefinition;
      }
      if (data.temperature !== undefined) {
        console.log('📝 Setting temperature:', data.temperature);
        this.newTraining.temperature = data.temperature;
      }
      if (data.top_p !== undefined) {
        console.log('📝 Setting top_p:', data.top_p);
        this.newTraining.top_p = data.top_p;
      }
      if (data.max_tokens !== undefined) {
        console.log('📝 Setting max_tokens:', data.max_tokens);
        this.newTraining.max_tokens = data.max_tokens;
      }
      if (data.ragConfig) {
        if (data.ragConfig.chunkSize !== undefined) {
          console.log('📝 Setting chunkSize:', data.ragConfig.chunkSize);
          this.newTraining.ragConfig.chunkSize = data.ragConfig.chunkSize;
        }
        if (data.ragConfig.topK !== undefined) {
          console.log('📝 Setting topK:', data.ragConfig.topK);
          this.newTraining.ragConfig.topK = data.ragConfig.topK;
        }
      }
      
      console.log('📝 Form populated, final newTraining:', this.newTraining);
    },
    
    closeModal() {
      // Reset form when closing
      this.uploadedFiles = []
      if (this.$refs.ragFileInput) {
        this.$refs.ragFileInput.value = ''
      }
      this.$emit('close')
    },
    
    onMinionSelect() {
      const selectedMinion = this.availableMinions.find(m => m.id == this.newTraining.baseMinion)
      if (selectedMinion) {
        // Populate from selected minion
        this.newTraining.jobName = `Refine ${selectedMinion.display_name}`
        this.newTraining.description = selectedMinion.description || ''
        this.newTraining.roleDefinition = selectedMinion.system_prompt || ''
      }
    },
    
    onProviderSelect() {
      // Update available models based on provider
      this.updateAvailableModels()
      this.newTraining.model = '' // Reset model selection
    },
    
    updateAvailableModels() {
      const modelMap = {
        'openai': [
          'gpt-4o',
          'gpt-4o-mini',
          'gpt-4-turbo',
          'gpt-3.5-turbo'
        ],
        'anthropic': [
          'claude-3-5-sonnet-20241022',
          'claude-3-5-haiku-20241022',
          'claude-3-opus-20240229',
          'claude-3-sonnet-20240229'
        ],
        'nvidia': [
          'nvidia/llama-3.3-nemotron-super-49b-v1.5',
          'nvidia/llama-3.3-nemotron-large-8b-v1.5',
          'nvidia/llama-3.3-nemotron-medium-8b-v1.5'
        ]
      }
      
      this.availableModels = modelMap[this.newTraining.provider] || []
    },
    
    getDatasetName(datasetId) {
      const dataset = this.availableDatasets.find(d => d.id === datasetId)
      return dataset ? dataset.name : 'Unknown Dataset'
    },
    
    getDatasetSamples(datasetId) {
      const dataset = this.availableDatasets.find(d => d.id === datasetId)
      return dataset ? dataset.sampleCount : 0
    },
    
    removeDataset(datasetId) {
      this.newTraining.selectedDatasets = this.newTraining.selectedDatasets.filter(id => id !== datasetId)
    },
    
    getTraitIcon(traitValue) {
      const icons = {
        'professional': 'business_center',
        'friendly': 'emoji_people',
        'technical': 'build',
        'creative': 'palette',
        'analytical': 'analytics',
        'supportive': 'support_agent'
      };
      return icons[traitValue] || 'person';
    },
    
    getTraitDescription(traitValue) {
      const descriptions = {
        'professional': 'Business-focused expertise',
        'friendly': 'Warm, helpful demeanor',
        'technical': 'Precise technical knowledge',
        'creative': 'Innovative, artistic thinking',
        'analytical': 'Data-driven analysis',
        'supportive': 'Mentor-like guidance'
      };
      return descriptions[traitValue] || 'Personality trait';
    },
    
    async createTrainingJob() {
      if (!this.canStartTraining) {
        return
      }
      
      // NEW: Check for duplicate training before proceeding
      const duplicateCheck = await this.validateForDuplicates()
      
      if (duplicateCheck.isDuplicate) {
        // Show duplicate warning modal
        this.duplicateValidationResult = duplicateCheck
        this.duplicateWarningVisible = true
        return
      }
      
      // Proceed with normal training creation
      this.proceedWithTraining()
    },
    
    // Original training creation logic (renamed to avoid conflicts)
    proceedWithTraining() {
      const trainingData = {
        ...this.newTraining,
        minionId: this.newTraining.baseMinion,
        uploadedFiles: this.uploadedFiles // Include file references
      }
      
      // If there are uploaded files, we need to pass them separately
      // The parent component (Training.vue) will handle FormData creation
      if (this.uploadedFiles.length > 0) {
        // Create a FormData-compatible structure
        this.$emit('create-training', {
          trainingData: trainingData,
          files: this.uploadedFiles // Pass files array for FormData handling
        })
      } else {
        this.$emit('create-training', trainingData)
      }
      
      this.closeModal()
    },
    
    // Duplicate warning modal handlers (NEW)
    handleDuplicateCancel() {
      this.duplicateWarningVisible = false
      this.duplicateValidationResult = null
    },
    
    handleDuplicateOverwrite() {
      this.duplicateWarningVisible = false
      // Proceed with training (will overwrite existing collection)
      this.proceedWithTraining()
    },
    
    handleDuplicateCreateNew() {
      this.duplicateWarningVisible = false
      // Suggest new collection name
      const timestamp = new Date().toISOString().slice(0, 10)
      this.newTraining.ragConfig.collectionName = `${this.newTraining.ragConfig.collectionName}-${timestamp}`
      // Proceed with training
      this.proceedWithTraining()
    },
    
    handleDuplicateProceed() {
      this.duplicateWarningVisible = false
      // Proceed anyway (user override)
      this.proceedWithTraining()
    },
    
    resetForm() {
      this.newTraining = {
        jobName: '',
        description: '',
        version: '',
        type: 'rag',
        baseMinion: '',
        provider: '',
        model: '',
        selectedDatasets: [],
        datasetType: 'upload',
        roleDefinition: '',
        temperature: 0.7,
        top_p: 0.9,
        max_tokens: 1024,
        ragConfig: {
          // Knowledge Base Configuration
          knowledgeBaseStrategy: 'create_new', // 'create_new' or 'use_existing'
          existingCollection: '',
          collectionName: '',
          collectionDescription: '',
          updateStrategy: 'smart_replace', // 'append', 'replace_all', 'smart_replace', or 'replace_by_id'
          
          // Filter Configuration (for replace_by_id strategy)
          filterType: 'document_ids', // 'document_ids', 'metadata_filter', 'date_range', 'custom_filter'
          documentIds: '',
          metadataKey: '',
          metadataOperator: 'equals',
          metadataValue: '',
          dateFrom: '',
          dateTo: '',
          customFilter: '',
          
          // Embedding Configuration
          embeddingModel: 'all-MiniLM-L6-v2',
          
          // Document Processing
          chunkSize: 1000,
          chunkOverlap: 100,
          topK: 4,
          similarityThreshold: 0.7,
          
          // Retrieval Strategy
          retrievalMethod: 'semantic', // 'semantic', 'hybrid', 'rerank'
          
          // Advanced Options
          enableContextualCompression: true,
          enableSourceCitation: true,
          enableQueryExpansion: false
        },
        loraConfig: {
          styleSensitivity: 0.7,
          enhancementIntensity: 1.0,
          selectedTraits: [],
          traitIntensities: {},
          compatibilityAnalysisUnlocked: false
        }
      }
      this.availableModels = []
      this.uploadedFiles = [] // Reset uploaded files
      this.collectionNameError = null // Reset validation errors
    },
    
    debugTraitSelection(traitValue) {
      console.log('🔍 Trait clicked:', traitValue);
      console.log('🔍 Current selectedTraits:', this.newTraining.loraConfig.selectedTraits);
      console.log('🔍 All trait options:', this.traitOptions);
    },
    
    debugCheckbox(option) {
      console.log(`🔍 Checkbox clicked: ${option}`);
      console.log('🔍 Current RAG config:', this.newTraining.ragConfig);
    },
    
    // Check if user can select a trait
    canSelectTrait(traitValue) {
      // Can select if already selected, or if haven't reached slot limit
      return this.newTraining.loraConfig.selectedTraits.includes(traitValue) || 
             this.newTraining.loraConfig.selectedTraits.length < this.maxTraitSlots
    },
    
    // Update intensity distribution when sliders change
    updateIntensityDistribution() {
      // Ensure total doesn't exceed 10 points
      if (this.totalTraitIntensity > 10) {
        console.warn('⚠️ Total intensity exceeds 10 points!');
        // Could add auto-balancing here if needed
      }
      
      // Initialize default values for new traits
      this.newTraining.loraConfig.selectedTraits.forEach(trait => {
        if (!this.newTraining.loraConfig.traitIntensities[trait]) {
          this.$set(this.newTraining.loraConfig.traitIntensities, trait, 5)
        }
      })
    },
    
    // Reset intensity values when traits are deselected
    onTraitChange() {
      // Clean up intensities for deselected traits
      Object.keys(this.newTraining.loraConfig.traitIntensities).forEach(trait => {
        if (!this.newTraining.loraConfig.selectedTraits.includes(trait)) {
          this.$delete(this.newTraining.loraConfig.traitIntensities, trait)
        }
      })
      
      // Initialize intensities for new traits
      this.updateIntensityDistribution()
    },
    
    // Calculate trait compatibility and synergy bonuses
    calculateTraitCompatibility(selectedTraits) {
      const traitRelationships = {
        // Compatible pairs (positive synergy)
        'professional+technical': 0.2,      // Expert Professional (+20%)
        'friendly+supportive': 0.2,        // Mentor Helper (+20%)
        'creative+analytical': 0.15,       // Innovation Analyst (+15%)
        'technical+analytical': 0.25,      // Data Expert (+25%)
        'professional+supportive': 0.1,    // Executive Coach (+10%)
        'friendly+creative': 0.15,         // Creative Guide (+15%)
        
        // Conflicting pairs (negative synergy)
        'professional+creative': -0.15,    // Style conflict (-15%)
        'analytical+friendly': -0.1,       // Data vs emotion (-10%)
        'technical+friendly': -0.1,        // Precision vs casual (-10%)
        'supportive+technical': -0.05      // Human vs machine (-5%)
      }
      
      let totalCompatibility = 0
      let relationshipCount = 0
      
      // Check all pairs
      for (let i = 0; i < selectedTraits.length; i++) {
        for (let j = i + 1; j < selectedTraits.length; j++) {
          const pair1 = `${selectedTraits[i]}+${selectedTraits[j]}`
          const pair2 = `${selectedTraits[j]}+${selectedTraits[i]}`
          const relationship = traitRelationships[pair1] || traitRelationships[pair2]
          
          if (relationship !== undefined) {
            totalCompatibility += relationship
            relationshipCount++
          }
        }
      }
      
      // Return average compatibility score
      return relationshipCount > 0 ? totalCompatibility / relationshipCount : 0
    },
    
    // Compatibility Analysis Perk Methods
    toggleCompatibilityAnalysis() {
      if (this.hasCompatibilityAnalysisUnlocked) {
        // Cannot refund - perk is permanent
        return
      }
      
      if (this.canUnlockCompatibilityAnalysis) {
        // Deduct 3 points permanently
        this.newTraining.loraConfig.compatibilityAnalysisUnlocked = true
        console.log('🔍 Compatibility Analysis unlocked! (3 points deducted permanently)')
      }
    },
    
    getTraitSynergy(trait1, trait2) {
      const relationships = {
        'professional+technical': 0.2,
        'friendly+supportive': 0.2,
        'creative+analytical': 0.15,
        'technical+analytical': 0.25,
        'professional+supportive': 0.1,
        'friendly+creative': 0.15,
        'professional+creative': -0.15,
        'analytical+friendly': -0.1,
        'technical+friendly': -0.1,
        'supportive+technical': -0.05
      }
      
      return relationships[`${trait1}+${trait2}`] || relationships[`${trait2}+${trait1}`] || 0
    },
    
    getSynergyDescription(trait1, trait2) {
      const descriptions = {
        'professional+technical': 'Expert Professional: Business-focused technical expertise',
        'friendly+supportive': 'Mentor Helper: Warm, guiding assistance',
        'creative+analytical': 'Innovation Analyst: Data-driven creativity',
        'technical+analytical': 'Data Expert: Precision analytical thinking',
        'professional+supportive': 'Executive Coach: Business mentoring approach',
        'friendly+creative': 'Creative Guide: Inspiring artistic guidance',
        'professional+creative': 'Style Conflict: Formal vs artistic approach clash',
        'analytical+friendly': 'Logic vs Emotion: Data-driven vs warm responses',
        'technical+friendly': 'Precision vs Casual: Exact vs relaxed communication',
        'supportive+technical': 'Human vs Machine: Emotional vs logical support'
      }
      
      return descriptions[`${trait1}+${trait2}`] || descriptions[`${trait2}+${trait1}`] || 'Neutral combination'
    }
  },
  
  watch: {
    showModal(newVal) {
      if (newVal) {
        this.resetForm()
      }
    },
    
    // Watch for trait selection changes
    'newTraining.loraConfig.selectedTraits': {
      handler() {
        this.onTraitChange()
      },
      deep: true
    },
    
    // Watch for intensity changes
    'newTraining.loraConfig.traitIntensities': {
      handler() {
        this.updateIntensityDistribution()
      },
      deep: true
    }
  }
}
</script>

<style scoped>

/* Training Metadata Styling */
.training-metadata {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: var(--radius);
  border: 1px solid rgba(78, 115, 223, 0.2);
}

.training-metadata h3 {
  margin: 0 0 1rem 0;
  color: var(--primary);
  font-size: 1.1rem;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.required {
  color: var(--danger);
  font-weight: bold;
}

/* Training Type Cards */
.training-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
}

.training-type-card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  border: 2px solid transparent;
}

.training-type-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.training-type-card.active {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
}

.type-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.training-type-card h4 {
  margin: 0.5rem 0;
  color: var(--text-color);
}

.training-type-card p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--secondary);
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 0.95rem;
  background: var(--card-bg);
  color: var(--text-color);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(78, 115, 223, 0.2);
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: var(--secondary);
}

/* Configuration Sections */
.model-params,
.rag-config {
  background: rgba(78, 115, 223, 0.02);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1rem 0;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.model-params h3,
.rag-config h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1.1rem;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

/* Enhanced RAG Configuration Styles */
.rag-config .config-description {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 20px;
  line-height: 1.4;
}

.rag-config h4 {
  color: var(--text-color);
  font-size: 1rem;
  font-weight: 600;
  margin: 20px 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

/* Knowledge Base Section */
.knowledge-base-section,
.embedding-section,
.document-processing-section,
.retrieval-strategy-section,
.advanced-rag-section {
  margin-bottom: 25px;
}

.strategy-options,
.retrieval-options,
.update-strategy-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 10px;
}

/* Strategy Details */
.strategy-details {
  margin-top: 15px;
  padding: 15px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.strategy-info h5 {
  margin: 0 0 8px 0;
  color: var(--text-color);
  font-size: 1rem;
  font-weight: 600;
}

.strategy-info p {
  margin: 0 0 10px 0;
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.4;
}

.strategy-info ul {
  margin: 0 0 10px 0;
  padding-left: 20px;
}

.strategy-info li {
  margin: 4px 0;
  color: var(--text-muted);
  font-size: 0.85rem;
}

/* Strategy-specific styling */
.append-info {
  border-left: 4px solid #10b981; /* Green */
}

.replace-all-info {
  border-left: 4px solid #ef4444; /* Red */
}

.smart-replace-info {
  border-left: 4px solid #3b82f6; /* Blue */
}

.replace-by-id-info {
  border-left: 4px solid #8b5cf6; /* Purple */
}

/* Filter Configuration */
.filter-config {
  margin-top: 15px;
  padding: 15px;
  background: rgba(139, 92, 246, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.filter-config h6 {
  margin: 0 0 15px 0;
  color: var(--text-color);
  font-size: 0.9rem;
  font-weight: 600;
}

.filter-options .form-group {
  margin-bottom: 15px;
}

.metadata-filter-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 10px;
  align-items: end;
}

.date-range-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

/* Warning and Info Boxes */
.warning-box, .info-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px;
  border-radius: 6px;
  margin-top: 10px;
  font-size: 0.85rem;
}

.warning-box {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #dc2626;
}

.warning-box .material-icons-round {
  color: #ef4444;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.info-box {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #1d4ed8;
}

.info-box .material-icons-round {
  color: #3b82f6;
  font-size: 1.2rem;
  flex-shrink: 0;
}

/* Advanced Options Grid - Neumorphism Style */
.advanced-options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 10px;
}

.advanced-option {
  cursor: pointer;
  user-select: none;
}

.advanced-option .option-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--card-bg);
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 
    8px 8px 16px rgba(0, 0, 0, 0.1),
    -8px -8px 16px rgba(255, 255, 255, 0.7);
}

.advanced-option .option-card:hover {
  transform: translateY(-2px);
  box-shadow: 
    12px 12px 24px rgba(0, 0, 0, 0.15),
    -12px -12px 24px rgba(255, 255, 255, 0.8);
}

.advanced-option.active .option-card {
  background: var(--card-bg);
  box-shadow: 
    inset 4px 4px 8px rgba(0, 0, 0, 0.1),
    inset -4px -4px 8px rgba(255, 255, 255, 0.7);
  transform: translateY(1px);
}

.advanced-option .option-card .material-icons-round {
  font-size: 1.5rem;
  color: var(--primary-color);
  flex-shrink: 0;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.advanced-option .option-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.advanced-option .option-title {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.95rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.advanced-option .option-desc {
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.3;
}

.advanced-option .option-status {
  flex-shrink: 0;
}

.advanced-option .option-status .material-icons-round {
  font-size: 1.25rem;
  color: var(--text-muted);
  transition: all 0.3s ease;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.advanced-option.active .option-status .material-icons-round {
  color: var(--primary-color);
  filter: drop-shadow(0 2px 4px rgba(78, 115, 223, 0.3));
}

.strategy-option,
.retrieval-option, .advanced-option {
  cursor: pointer;
  transition: all 0.3s ease;
  padding: .75rem .85rem;
    transition: all .2s 
ease;
    box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #fff;
    border: 1px solid #d1d9e6;
    border-radius: 20px;
}

.strategy-option .option-card,
.retrieval-option .option-card {
  background: var(--input-bg);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  
}

.strategy-option.active .option-card,
.retrieval-option.active .option-card {
  border-color: var(--primary-color);
  background: rgba(79, 70, 229, 0.05);

  
}
label.strategy-option.active {
  background-color: #e6e7ee;
    border-color: #d1d9e6;
    box-shadow: inset 2px 2px 5px #b8b9be, inset -3px -3px 7px #fff;
}
.strategy-option .option-card .material-icons-round,
.retrieval-option .option-card .material-icons-round {
  color: var(--primary-color);
  font-size: 20px;
}

.option-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.option-title {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9rem;
}

.option-desc {
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.3;
}

/* Advanced Options */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  margin-bottom: 12px;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
  user-select: none;
}

.checkbox-label:hover {
  background: rgba(78, 115, 223, 0.05);
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  position: relative;
  transition: all 0.3s ease;
  background: var(--card-bg);
  flex-shrink: 0;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.checkbox-label input[type="checkbox"]:focus + .checkmark {
  box-shadow: 0 0 0 2px rgba(78, 115, 223, 0.2);
}

/* Dataset Options */
.dataset-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.dataset-option {
  cursor: pointer;
}

.dataset-option .option-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--card-bg);
  border: 2px solid transparent;
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.dataset-option:hover .option-card {
  border-color: var(--primary);
  box-shadow: var(--shadow);
}

.dataset-option input:checked + .option-card {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
  box-shadow: var(--shadow);
}

.dataset-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.dataset-name {
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.95rem;
}

.dataset-details {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.selected-datasets {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: var(--radius);
  border: 1px solid rgba(78, 115, 223, 0.2);
}

.selected-datasets h4 {
  margin: 0 0 0.75rem 0;
  color: var(--primary);
  font-size: 1rem;
}

.selected-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.selected-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: white;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.selected-item .dataset-name {
  font-weight: 500;
  color: var(--text-color);
}

.selected-item .dataset-samples {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-left: auto;
  margin-right: 0.5rem;
}

/* Button Styles */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--primary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: var(--secondary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--card-bg);
  border: none;
  color: var(--secondary);
  cursor: pointer;
  box-shadow: 3px 3px 6px var(--shadow-dark), 
              -3px -3px 6px var(--shadow-light);
  transition: all 0.2s ease;
}

.btn-icon:hover {
  color: var(--primary);
  transform: translateY(-2px);
}

.debug-info {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: rgba(231, 74, 59, 0.1);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(231, 74, 59, 0.2);
}

.debug-info small {
  color: var(--danger);
  font-weight: 500;
}

/* Enhanced LoRA Configuration Styles */
.lora-config {
  background: var(--background-color);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 
    inset 5px 5px 10px rgba(0, 0, 0, 0.1),
    inset -5px -5px 10px rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.config-header {
  margin-bottom: 2rem;
  text-align: center;
  padding: 1rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: 12px;
  box-shadow: 
    inset 3px 3px 6px rgba(0, 0, 0, 0.1),
    inset -3px -3px 6px rgba(255, 255, 255, 0.15);
}

.config-header h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 1.4rem;
  font-weight: 700;
}

.config-description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.lora-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--background-color);
  border-radius: 12px;
  align-items: start;
  box-shadow: 
    inset 4px 4px 8px rgba(0, 0, 0, 0.08),
    inset -4px -4px 8px rgba(255, 255, 255, 0.12);
}

.control-group {
  display: flex;
  flex-direction: column;
}

.control-group label {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.slider-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  width: 100%;
}

.slider-group input[type="range"] {
  flex: 1;
  height: 8px;
  background: var(--background-color);
  border-radius: 4px;
  outline: none;
  -webkit-appearance: none;
  box-shadow: 
    inset 3px 3px 6px rgba(0, 0, 0, 0.1),
    inset -3px -3px 6px rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(78, 115, 223, 0.2);
}

.slider-group input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 24px;
  height: 24px;
  background: var(--primary-color);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 
    4px 4px 8px rgba(0, 0, 0, 0.2),
    -2px -2px 4px rgba(255, 255, 255, 0.15),
    inset 1px 1px 2px rgba(255, 255, 255, 0.3);
  border: 2px solid var(--background-color);
  transition: all 0.2s ease;
}

.slider-group input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 
    6px 6px 12px rgba(0, 0, 0, 0.25),
    -6px -6px 12px rgba(255, 255, 255, 0.5);
}

/* Firefox slider support */
.slider-group input[type="range"]::-moz-range-track {
  height: 8px;
  background: var(--background-color);
  border-radius: 4px;
  box-shadow: 
    inset 2px 2px 4px rgba(0, 0, 0, 0.2),
    inset -2px -2px 4px rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.slider-group input[type="range"]::-moz-range-thumb {
  width: 24px;
  height: 24px;
  background: linear-gradient(145deg, var(--primary-color), var(--primary-dark));
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 
    4px 4px 8px rgba(0, 0, 0, 0.2),
    -4px -4px 8px rgba(255, 255, 255, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.2s ease;
}

.slider-value {
  min-width: 3.5rem;
  text-align: center;
  font-weight: 700;
  color: var(--primary-color);
  background: var(--background-color);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 1rem;
  flex-shrink: 0;
  box-shadow: 
    inset 3px 3px 6px rgba(0, 0, 0, 0.1),
    inset -3px -3px 6px rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(78, 115, 223, 0.2);
}

.slider-label {
  font-size: 0.85rem;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 600;
}

.helper-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

.traits-section {
  margin-top: 1rem;
}

.traits-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.traits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.trait-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.trait-card label {
  cursor: pointer;
  display: block;
  width: 100%;
}

.trait-card:hover .trait-content {
  transform: translateY(-2px);
  box-shadow: 
    0 4px 8px rgba(0, 0, 0, 0.1),
    0 0 20px rgba(78, 115, 223, 0.15);
}

.trait-content[data-selected="true"] {
  background: rgba(78, 115, 223, 0.15);
  border-color: var(--primary-color);
  box-shadow: 
    inset 2px 2px 4px rgba(78, 115, 223, 0.2),
    inset -2px -2px 4px rgba(255, 255, 255, 0.3);
}

.trait-content[data-selected="true"] .trait-icon {
  color: var(--primary-color);
}

.trait-content[data-selected="true"] .trait-name {
  color: var(--primary-color);
  font-weight: 700;
}

.trait-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem 1rem;
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.2s ease;
  text-align: center;
}

.trait-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(78, 115, 223, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.trait-icon .material-icons-round {
  font-size: 1.25rem;
  color: var(--primary-color);
}

.trait-name {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}
.modal-container.modal-large {
  background-color: #ffffff !important;
}
.trait-description {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.3;
}

.modal-container {
  background-color: #ffffff !important;
}

/* Trait Slots System */
.trait-slots-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 1rem 0;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 8px;
  box-shadow: 
    inset 2px 2px 4px rgba(0, 0, 0, 0.1),
    inset -2px -2px 4px rgba(255, 255, 255, 0.15);
}

.trait-slots-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color);
  font-size: 1rem;
}

.slot-info {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.slots-used, .training-level {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary-color);
  font-weight: 600;
}

.available-slots {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.trait-slot {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.trait-slot.filled {
  background: rgba(76, 175, 80, 0.2);
  color: var(--success-color);
}

.trait-slot.available {
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary-color);
}

.trait-slot.locked {
  background: rgba(158, 158, 158, 0.1);
  color: var(--text-secondary);
  opacity: 0.5;
}

.trait-intensity {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  border: 1px solid rgba(78, 115, 223, 0.2);
}

.trait-intensity-slider {
  width: 100%;
  margin: 0.25rem 0;
}

.intensity-value {
  display: block;
  text-align: center;
  font-weight: 600;
  color: var(--primary-color);
  margin-top: 0.25rem;
}

/* Points System Summary */
.points-summary {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 8px;
  box-shadow: 
    inset 2px 2px 4px rgba(0, 0, 0, 0.1),
    inset -2px -2px 4px rgba(255, 255, 255, 0.15);
}

.points-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.trait-points, .intensity-points {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.status-indicators {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
}

.points-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: rgba(76, 175, 80, 0.2);
  color: var(--success-color);
}

.points-status.over-capacity {
  background: rgba(244, 67, 54, 0.2);
  color: var(--danger-color);
}

.compatibility-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.compatibility-status.compatible {
  background: rgba(76, 175, 80, 0.2);
  color: var(--success-color);
}

.compatibility-status.conflicting {
  background: rgba(244, 67, 54, 0.2);
  color: var(--danger-color);
}

.compatibility-status.neutral {
  background: rgba(158, 158, 158, 0.2);
  color: var(--text-secondary);
}

/* Compatibility Analysis Perk */
.compatibility-perk-section {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 8px;
  box-shadow: 
    inset 2px 2px 4px rgba(0, 0, 0, 0.1),
    inset -2px -2px 4px rgba(255, 255, 255, 0.15);
}

.perk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.perk-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color);
  font-size: 1rem;
}

.perk-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary-color);
}

.perk-toggle-btn:hover:not(:disabled) {
  background: rgba(78, 115, 223, 0.2);
  transform: translateY(-1px);
}

.perk-toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.perk-toggle-btn.unlocked {
  background: rgba(76, 175, 80, 0.2);
  color: var(--success-color);
}

.compatibility-analysis {
  padding: 1rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.analysis-section {
  margin-bottom: 1rem;
}

.analysis-section h5 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 0.9rem;
  font-weight: 600;
}

.compatibility-meter {
  position: relative;
  width: 100%;
  height: 20px;
  background: var(--background-color);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: inset 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.meter-fill {
  height: 100%;
  background: linear-gradient(90deg, 
    rgba(244, 67, 54, 0.8) 0%, 
    rgba(255, 152, 0, 0.8) 50%, 
    rgba(76, 175, 80, 0.8) 100%);
  transition: width 0.3s ease;
}

.meter-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-color);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.detailed-analysis {
  margin-bottom: 1rem;
}

.analysis-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  font-size: 0.85rem;
}

.analysis-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.analysis-icon.synergy {
  background: rgba(76, 175, 80, 0.2);
  color: var(--success-color);
}

.analysis-icon.conflict {
  background: rgba(244, 67, 54, 0.2);
  color: var(--danger-color);
}

.analysis-text {
  flex: 1;
  color: var(--text-color);
}

.analysis-impact {
  font-weight: 600;
  color: var(--text-primary);
}

.optimization-suggestions {
  padding: 0.75rem;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 4px;
  border-left: 3px solid var(--warning-color);
}

.suggestion {
  font-size: 0.85rem;
  color: var(--text-color);
  line-height: 1.4;
}

/* Responsive */
@media (max-width: 768px) {
  .training-types {
    grid-template-columns: 1fr;
  }
  
  .params-grid {
    grid-template-columns: 1fr;
  }
  
  .lora-controls {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .traits-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}

/* Validation Error Styles */
.form-control.error {
  border-color: #e74c3c;
  box-shadow: 0 0 0 2px rgba(231, 76, 60, 0.2);
}

.error-text {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  display: block;
}

.required {
  color: #e74c3c;
  font-weight: bold;
}

/* File Upload Styles */
.file-upload {
  margin-top: 0.5rem;
}

#rag-file-upload {
  display: none;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--card-bg, #ffffff);
  border: 2px dashed rgba(78, 115, 223, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-color, #333);
  width: 100%;
  justify-content: center;
}

.upload-btn:hover {
  border-color: var(--primary-color, #4e73df);
  background: rgba(78, 115, 223, 0.05);
}

.upload-btn .material-icons-round {
  font-size: 1.2rem;
  color: var(--primary-color, #4e73df);
}

.uploaded-files {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(78, 115, 223, 0.03);
  border-radius: 6px;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.uploaded-files-header {
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary, #666);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.file-item .material-icons-round {
  font-size: 1.1rem;
  color: var(--primary-color, #4e73df);
}

.file-name {
  flex: 1;
  font-size: 0.9rem;
  color: var(--text-color, #333);
  word-break: break-word;
}

.file-size {
  font-size: 0.8rem;
  color: var(--text-secondary, #666);
  white-space: nowrap;
}

.file-item .btn-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: rgba(231, 76, 60, 0.1);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.file-item .btn-icon:hover {
  background: rgba(231, 76, 60, 0.2);
}

.file-item .btn-icon .material-icons-round {
  font-size: 1rem;
  color: #e74c3c;
}
</style>

