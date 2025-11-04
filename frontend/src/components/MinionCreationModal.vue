<template>
  <div v-if="showModal" class="modal-overlay">
    <div class="modal-content neumorphic-card">
      <div class="modal-header">
        <h2>{{ editingModel ? 'Edit Model' : 'Create New Model' }}</h2>
        <button class="btn-icon" @click="closeModal">
          <span class="material-icons-round">close</span>
        </button>
      </div>

      <div class="modal-body">
        <!-- Model Type Selection -->
        <div class="form-group">
          <label>Model Type</label>
          <div class="model-type-selector">
            <label class="type-option" :class="{ active: modelForm.modelType === 'external' }">
              <input type="radio" v-model="modelForm.modelType" value="external" hidden>
              <div class="type-icon">
                <span class="material-icons-round">cloud</span>
          </div>
              <div class="type-info">
                <h4>External Model</h4>
                <p>OpenAI, Anthropic, etc.</p>
              </div>
            </label>
            <label class="type-option" :class="{ active: modelForm.modelType === 'local' }">
              <input type="radio" v-model="modelForm.modelType" value="local" hidden>
              <div class="type-icon">
                <span class="material-icons-round">computer</span>
              </div>
              <div class="type-info">
                <h4>Local Model</h4>
                <p>Ollama or local AI model</p>
            </div>
            </label>
              </div>
              </div>

        <!-- External Model Configuration -->
        <div v-if="modelForm.modelType === 'external'" class="external-api-config">
          <div class="form-group">
            <label>Reference Model</label>
            <select class="form-control" v-model="modelForm.referenceModelId" @change="loadReferenceModel">
              <option value="">Select a reference model...</option>
              <option v-for="refModel in referenceModels" :key="refModel.id" :value="refModel.id">
                {{ refModel.display_name }} ({{ refModel.provider }})
              </option>
            </select>
            </div>

            <!-- Capabilities Preview -->
            <div class="form-group">
              <label>Capabilities (from reference model)</label>
              <div class="capabilities-preview" v-if="getSelectedReferenceModel()?.capabilities?.length > 0">
                <span 
                  v-for="capability in getSelectedReferenceModel().capabilities" 
                  :key="capability"
                  class="capability-badge"
                >
                  {{ capability }}
                </span>
              </div>
              <div v-else class="no-capabilities">
                <span class="material-icons-round">info</span>
                <span>No capabilities defined for selected reference model</span>
              </div>
              <small class="form-text text-muted">
                These capabilities will be automatically assigned to your minion based on the selected reference model.
              </small>
            </div>

          <div class="form-group">
            <label>Model Name</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="modelForm.name" 
              placeholder="e.g., My Custom GPT-4"
            />
          </div>

          <div class="form-group">
            <label>Display Name</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="modelForm.displayName" 
              placeholder="e.g., My Custom GPT-4 Assistant"
            />
        </div>

          <div class="form-group">
            <label>Minion Class</label>
            <ClassSelection
              :user-rank="userRank"
              :user-level="userLevel"
              @class-selected="handleClassSelected"
            />
            <div v-if="selectedClass" class="selected-class-info">
              <div class="selected-class-badge">
                <span class="material-icons">{{ getClassIcon(selectedClass.class_name) }}</span>
                <span>{{ selectedClass.display_name }}</span>
                <span class="material-icons remove-btn" @click="clearSelectedClass">close</span>
              </div>
              <small class="selected-class-description">{{ selectedClass.description }}</small>
            </div>
          </div>

          <div class="form-group">
            <label>Personality</label>
            <textarea 
              class="form-control" 
              v-model="modelForm.personality"
              rows="2"
              placeholder="e.g., Professional and helpful, Creative and enthusiastic, Analytical and precise"
            ></textarea>
          </div>

          <div class="form-group">
            <label>Company</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="modelForm.company" 
              placeholder="e.g., AI Republic, Your Company"
            />
              </div>
              
          <div class="form-group">
            <label>Theme Color</label>
            <div class="color-picker-container">
              <input 
                type="color" 
                class="form-control color-input" 
                v-model="modelForm.theme_color"
                title="Choose theme color"
              />
              <span class="color-preview" :style="{ backgroundColor: modelForm.theme_color }"></span>
                </div>
              </div>

          <div class="form-group">
            <label>Avatar</label>
            <div class="avatar-upload">
              <div class="avatar-preview" v-if="modelForm.avatarPreview">
                <img :src="modelForm.avatarPreview" alt="Avatar preview" class="avatar-image">
                <button type="button" class="remove-avatar" @click="removeAvatar">×</button>
                </div>
              <div class="avatar-upload-area" v-else>
                <input 
                  type="file" 
                  ref="avatarInput"
                  @change="handleAvatarUpload"
                  accept="image/*,.lottie,.json"
                  style="display: none"
                />
                <div class="upload-placeholder" @click="$refs.avatarInput.click()">
                  <span class="upload-icon">📁</span>
                  <p>Click to upload avatar</p>
                  <small>Supports: JPG, PNG, GIF, Lottie (.lottie, .json)</small>
                </div>
              </div>
              </div>
            </div>

          <div class="form-group">
            <label>Description</label>
            <textarea 
              class="form-control" 
              v-model="modelForm.description"
              rows="3"
              placeholder="Describe your custom model..."
            ></textarea>
          </div>

          <div class="form-group">
            <label>Model Type</label>
            <select class="form-control" v-model="modelForm.externalModelType">
              <option value="coding">Coding</option>
              <option value="chat">Chat</option>
              <option value="math">Math</option>
              <option value="reasoning">Reasoning</option>
              <option value="vision">Vision</option>
              <option value="audio">Audio</option>
              <option value="multimodal">Multimodal</option>
            </select>
          </div>

          <div class="form-group">
            <label>Tags (comma separated)</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="modelForm.tags"
              placeholder="e.g., nlp, classification, sentiment"
            />
        </div>

          <div class="form-group">
            <label>API Key</label>
            <input 
              type="password" 
              class="form-control" 
              v-model="modelForm.apiKey" 
              placeholder="Enter your API key..."
            />
          </div>

          <div class="form-group">
            <label>Base URL (Optional)</label>
            <input 
              type="url" 
              class="form-control" 
              v-model="modelForm.baseUrl" 
              placeholder="https://api.openai.com/v1"
            />
            </div>

          <div class="form-row">
            <div class="form-group">
              <label>Temperature</label>
              <input 
                type="number" 
                class="form-control" 
                v-model="modelForm.temperature" 
                min="0" 
                max="2" 
                step="0.1"
                placeholder="0.7"
              />
                    </div>
            <div class="form-group">
              <label>Top P</label>
              <input 
                type="number" 
                class="form-control" 
                v-model="modelForm.topP" 
                min="0" 
                max="1" 
                step="0.1"
                placeholder="0.9"
              />
                  </div>
                </div>

          <div class="form-group">
            <label>Max Tokens</label>
            <input 
              type="number" 
              class="form-control" 
              v-model="modelForm.maxTokens" 
              min="1" 
              max="100000"
              placeholder="4096"
            />
            </div>

          <div class="form-group">
            <label>
              <input type="checkbox" v-model="modelForm.stream">
              Enable Streaming
            </label>
          </div>

          <div class="form-group">
            <label>System Prompt (Optional)</label>
            <textarea 
              class="form-control" 
              v-model="modelForm.systemPrompt" 
              rows="3"
              placeholder="Enter system prompt for the model..."
            ></textarea>
          </div>
        </div>

        <!-- Local Model Configuration -->
        <div v-else class="local-model-config">
              <div class="form-group">
            <label>Model Name</label>
                <input 
                  type="text" 
                  class="form-control" 
              v-model="modelForm.name" 
              placeholder="e.g., agimat-debugger"
                />
              </div>
          
              <div class="form-group">
            <label>Model Type</label>
            <select class="form-control" v-model="modelForm.type">
              <option v-for="type in modelTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Description (Optional)</label>
                <textarea 
                  class="form-control" 
              v-model="modelForm.description"
                  rows="3"
              placeholder="A brief description of your model..."
                ></textarea>
            </div>

          <div class="form-group">
            <label>Tags (comma separated)</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="modelForm.tags"
              placeholder="e.g., nlp, classification, sentiment"
            />
                </div>
              </div>
            </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeModal">
          Cancel
        </button>
        <button class="btn btn-primary" @click="saveModel" :disabled="!canSaveModel || isLoading">
          <Loader v-if="isLoading" />
          <span v-else>{{ editingModel ? 'Update Model' : 'Create Minion' }}</span>
        </button>
      </div>
    </div>
  </div>
  <!-- </div> -->
</template>

<script>
import { getApiUrl } from '@/config/api'
import toast from '@/utils/toast'
import { getSpiritIcon, getAvatarIcon, spiritIcons } from '@/utils/icons'
import Loader from './Loader.vue'
import ClassSelection from './ClassSelection.vue'

export default {
  name: 'MinionCreationModal',
  components: {
    Loader,
    ClassSelection
  },
  props: {
    showModal: {
      type: Boolean,
      default: false
    },
    editingModel: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'minion-created'],
  data() {
    return {
      selectedClass: null,
      userRank: 'Novice',
      userLevel: 1,
      referenceModels: [],
      modelTypes: ['Text', 'Image', 'Video', 'Audio', 'Multimodal', 'Code', 'Classification', 'Generation'],
      modelForm: {
        modelType: 'external',
        name: '',
        displayName: '',
        title: null, // Make title nullable
        personality: 'Professional and helpful',
        company: 'AI Republic',
        theme_color: '#4f46e5',
        type: 'Text',
        description: 'I am a helpful AI assistant ready to assist you with various tasks.',
        tags: 'reasoning,thinking',
        referenceModelId: '',
        externalModelType: 'chat',
        apiKey: '',
        baseUrl: '',
        temperature: 0.7,
        topP: 0.9,
        maxTokens: 4096,
        stream: true,
        systemPrompt: '',
        avatarPreview: null
      },
      isLoading: false,
      error: null
    }
  },
  computed: {
    canSaveModel() {
      if (this.modelForm.modelType === 'local') {
        return this.modelForm.name.trim() !== ''
      } else {
        return this.modelForm.name.trim() !== '' && 
               this.modelForm.displayName.trim() !== '' &&
               this.modelForm.apiKey.trim() !== ''
      }
    },
  },
  watch: {
    showModal(newVal) {
      if (newVal) {
        this.loadReferenceModels()
        this.resetForm()
      }
    },
    editingModel(newModel) {
      if (newModel) {
        this.loadModelForEditing(newModel)
      }
    }
  },
  methods: {
    handleClassSelected(classDef) {
      this.selectedClass = classDef
      console.log('MinionCreationModal: Received class-selected event:', classDef)
    },

    clearSelectedClass() {
      this.selectedClass = null
      console.log('MinionCreationModal: Cleared selected class')
    },

    getClassIcon(className) {
      // Map class names to Material Icons
      const classIcons = {
        'Planner': 'psychology',
        'Developer': 'code',
        'Creative Assistant': 'palette',
        'Data Scientist': 'analytics',
        'API Integration Specialist': 'api',
        'Security Specialist': 'security',
        'Swiss Army Knife': 'build'
      }
      return classIcons[className] || 'psychology'
    },

    getSelectedReferenceModel() {
      return this.referenceModels.find(model => model.id === parseInt(this.modelForm.referenceModelId));
    },

    async loadReferenceModels() {
      try {
        const response = await fetch(getApiUrl('reference-models'))
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            this.referenceModels = data.models || []
          } else {
            console.error('Failed to load reference models:', data.error)
            this.referenceModels = []
          }
        }
      } catch (error) {
        console.error('Failed to load reference models:', error)
        this.referenceModels = []
      }
    },
    
    async loadReferenceModel() {
      if (!this.modelForm.referenceModelId) return
      
      const refModel = this.referenceModels.find(m => m.id === this.modelForm.referenceModelId)
      if (refModel) {
        this.modelForm.name = refModel.name || ''
        this.modelForm.displayName = refModel.display_name || ''
        this.modelForm.description = refModel.description || 'I am a helpful AI assistant ready to assist you with various tasks.'
        this.modelForm.externalModelType = refModel.capability || 'chat'
        // Preserve the default values for minion profile fields
        this.modelForm.title = this.modelForm.title || 'AI Assistant'
        this.modelForm.personality = this.modelForm.personality || 'Professional and helpful'
        this.modelForm.company = this.modelForm.company || 'AI Republic'
        this.modelForm.theme_color = this.modelForm.theme_color || '#4f46e5'
        this.modelForm.tags = this.modelForm.tags || 'reasoning,thinking'
      }
    },
    
    async handleAvatarUpload(event) {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          this.modelForm.avatarPreview = e.target.result
        }
        reader.readAsDataURL(file)
      }
    },
    
    removeAvatar() {
      this.modelForm.avatarPreview = null
      if (this.$refs.avatarInput) {
          this.$refs.avatarInput.value = ''
        }
    },
    
    loadModelForEditing(model) {
      this.modelForm = {
        modelType: model.model_type || 'external',
        name: model.name || '',
        title: model.title || 'AI Assistant',
        displayName: model.display_name || '',
        type: model.type || 'Text',
        description: model.description || 'I am a helpful AI assistant ready to assist you with various tasks.',
        personality: model.personality || 'Professional and helpful',
        company: model.company || 'AI Republic',
        theme_color: model.theme_color || '#4f46e5',
        tags: Array.isArray(model.tags) ? model.tags.join(',') : (model.tags || 'reasoning,thinking'),
        referenceModelId: model.reference_model_id || '',
        externalModelType: model.external_model_type || 'chat',
        apiKey: model.api_key || '',
        baseUrl: model.base_url || '',
        temperature: parseFloat(model.temperature) || 0.7,
        topP: parseFloat(model.top_p) || 0.9,
        maxTokens: parseInt(model.max_tokens) || 4096,
        stream: model.stream !== false,
        systemPrompt: model.system_prompt || '',
        avatarPreview: model.avatar_url || null
      }
    },
    
    resetForm() {
      this.selectedClass = null
      console.log('MinionCreationModal: Form reset, cleared selected class')
      this.modelForm = {
        modelType: 'external',
        name: '',
        title: null,
        displayName: '',
        type: 'Text',
        description: 'I am a helpful AI assistant ready to assist you with various tasks.',
        personality: 'Professional and helpful',
        tags: 'reasoning,thinking',
        referenceModelId: '',
        externalModelType: 'chat',
        apiKey: '',
        theme_color: '#4f46e5',
        company: 'AI Republic',
        baseUrl: '',
        temperature: 0.7,
        topP: 0.9,
        maxTokens: 4096,
        stream: true,
        systemPrompt: '',
        avatarPreview: null
      }
      this.error = null
    },
    
    closeModal() {
      this.$emit('close')
    },
    
    async saveModel() {
      if (!this.canSaveModel) return
      
      this.isLoading = true
      this.error = null
      
      try {
        const referenceModel = this.getSelectedReferenceModel()
        
        const modelData = {
          // Core model fields - match backend expectations
          name: this.modelForm.name,
          display_name: this.modelForm.displayName, // Backend expects display_name
          description: this.modelForm.description,
          provider: referenceModel?.provider || 'openai', // Required field
          model_id: referenceModel?.model_id || this.modelForm.name, // Required field
          
          // Minion profile fields
          title: this.modelForm.title,
          company: this.modelForm.company,
          theme_color: this.modelForm.theme_color,
          
          // API configuration
          api_key: this.modelForm.apiKey,
          base_url: this.modelForm.baseUrl,
          
          // Model parameters - use reference model values as defaults
          temperature: parseFloat(this.modelForm.temperature) || referenceModel?.temperature || 0.7,
          top_p: parseFloat(this.modelForm.topP) || referenceModel?.top_p || 0.9,
          max_tokens: parseInt(this.modelForm.maxTokens) || referenceModel?.max_tokens || 2048,
          context_length: referenceModel?.context_length || 4096,
          system_prompt: this.modelForm.systemPrompt || referenceModel?.system_prompt || '',
          
          // Model architecture and parameters from reference model
          parameters: referenceModel?.parameters || {},
          model_type: referenceModel?.parameters?.type || 'transformer',
          
          // Tags and other fields
          tags: this.modelForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
          reference_model_id: this.modelForm.referenceModelId || null,
          external_model_type: this.modelForm.externalModelType,
          stream: this.modelForm.stream,
          
          // Add user_id for proper user association
          user_id: 2, // Default to user 2 for now
          
          // Add capabilities from reference model
          capabilities: referenceModel?.capabilities || [],
          
          // Add selected class information
          selected_class: this.selectedClass ? this.selectedClass.class_name : null
        }
        
        console.log('Sending data to backend:', modelData)
        
        if (this.editingModel) {
          // Update existing model
          const response = await fetch(getApiUrl('models') + `/${this.editingModel.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(modelData)
          })
          
          if (!response.ok) {
            throw new Error('Failed to update model')
          }
          
          const updatedModel = await response.json()
          this.$emit('minion-created', updatedModel)
        } else {
          // Create new model
          let response
          
          // Check if we have an avatar file to upload
          const avatarFile = this.$refs.avatarInput?.files?.[0]
          
          if (avatarFile) {
            // Send FormData if we have an avatar file
            const formData = new FormData()
            
            // Add all model data as JSON string
            formData.append('modelData', JSON.stringify(modelData))
            
            // Add avatar file
            formData.append('avatar', avatarFile)
            
            response = await fetch(getApiUrl('external-models'), {
              method: 'POST',
              body: formData
            })
          } else {
            // Send JSON if no avatar file
            response = await fetch(getApiUrl('external-models'), {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(modelData)
            })
          }
          
          if (!response.ok) {
            const errorData = await response.json()
            console.error('Backend error response:', errorData)
            throw new Error(errorData.error || 'Failed to create model')
          }
          
          const newModel = await response.json()
          this.$emit('minion-created', newModel)
          
          // Show success notification
          toast.success('Minion created successfully!')
        }
        
        this.closeModal()
      } catch (error) {
        this.error = error.message
        console.error('Model save error:', error)
        
        // Show error notification
        toast.error(`Failed to create minion: ${error.message}`)
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.models-container {
    padding: 1.5rem;
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  
  .page-header h1 {
    margin: 0 0 0.25rem;
    font-size: 1.8rem;
    color: var(--text-color);
  }
  
  .page-header p {
    margin: 0;
    color: var(--secondary);
  }
  
  .section-header {
    margin-bottom: 1.5rem;
  }
  
  .section-header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: var(--text-color);
  }
  
  .models-actions {
  margin-bottom: 2rem;
}

  .actions-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }
  .neumorphic-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 8px 8px 16px var(--shadow-dark), 
                -8px -8px 16px var(--shadow-light);
    transition: all 0.3s ease;
    border: 1px solid var(--border-color);
  }
    .search-box {
    position: relative;
    flex: 1;
    max-width: 400px;
    }
    
  .search-box input {
      width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    border: none;
    border-radius: 8px;
    background: var(--card-bg);
    box-shadow: inset 3px 3px 6px var(--shadow-dark), 
                inset -3px -3px 6px var(--shadow-light);
    color: var(--text-color);
  }
  
  .search-box .material-icons-round {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--secondary);
    font-size: 1.25rem;
  }
  
  .action-buttons {
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  
  .models-grid {
  display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

  .model-card {
    background: var(--card-bg);
  border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 5px 5px 10px var(--shadow-dark), 
                -5px -5px 10px var(--shadow-light);
    transition: transform 0.3s ease;
  }
  
  .model-card:hover {
    transform: translateY(-3px);
  }
  
  .model-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }
  
  .model-header h3 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--text-color);
  }
  
  .model-status {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
  }
  
  .model-status.image { background: rgba(66, 135, 245, 0.1); color: #4287f5; }
  .model-status.text { background: rgba(40, 167, 69, 0.1); color: #28a745; }
  .model-status.audio { background: rgba(111, 66, 193, 0.1); color: #6f42c1; }
  .model-status.video { background: rgba(220, 53, 69, 0.1); color: #dc3545; }
  .model-status.nlp { background: rgba(255, 193, 7, 0.1); color: #ffc107; }
  
  .model-details {
    margin-bottom: 1rem;
  }
  
  .model-details p {
    margin: 0 0 1rem;
    color: var(--secondary);
    font-size: 0.9rem;
  }
  
  .model-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: var(--secondary);
  }
  
  .model-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
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
    width: 230px;
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
  
  .btn-danger {
    background: #e74a3b;
    color: white;
    box-shadow: var(--shadow-sm);
  }
  
  .btn-danger:hover {
    background: #d52a1a;
    transform: translateY(-2px);
    box-shadow: var(--shadow);
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
    backdrop-filter: blur(3px);
  }
  
  .modal {
    background: var(--card-bg);
    border-radius: 12px;
    width: 100%;
    max-width: 800px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow);
    overflow: hidden;
  }
  .class-card {
    box-shadow: var(--shadow);
  }
  .modal-content {
    background: var(--card-bg);
    border-radius: 12px;
    width: 100%;
    max-width: 1400px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: none !important;
    overflow: hidden;
    
  }
  
  .modal-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: var(--text-color);
  }
  
  .modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    flex-grow: 1;
    max-height: calc(90vh - 140px); /* Account for header and footer */
  }
  .model-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 5px 5px 10px var(--shadow-dark), 
                -5px -5px 10px var(--shadow-light);
    transition: transform 0.3s ease;
  }
  
  .model-card:hover {
    transform: translateY(-3px);
  }
  .modal-footer {
    padding: 1.25rem 1.5rem;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }

  /* Selected Class Info */
  .selected-class-info {
    margin-top: 1rem;
    padding: 1rem;
    background: var(--success-light);
    border: 1px solid var(--success);
    border-radius: 8px;
  }

  .selected-class-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .selected-class-badge .material-icons {
    color: var(--success);
  }

  .selected-class-badge span:not(.material-icons) {
    font-weight: 600;
    color: var(--success);
  }

  .remove-btn {
    margin-left: auto;
    cursor: pointer;
    color: var(--secondary);
    transition: color 0.3s ease;
  }

  .remove-btn:hover {
    color: var(--error);
  }

  .selected-class-description {
    color: var(--text-color);
    font-size: 0.9rem;
    line-height: 1.4;
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
  
  /* Loading State */
  .loading-state {
    text-align: center;
    padding: 4rem 2rem;
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 8px 8px 16px var(--shadow-dark), 
                -8px -8px 16px var(--shadow-light);
    margin: 2rem 0;
  }
  
  .loading-spinner {
  margin-bottom: 1rem;
  }
  
  .loading-spinner .material-icons-round {
    font-size: 3rem;
  color: var(--primary);
    animation: spin 2s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .loading-state p {
    color: var(--text-secondary);
    font-size: 1.1rem;
    margin: 0;
  }
  
  /* Empty State */
  .empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3rem 1rem;
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 8px 8px 16px var(--shadow-dark), 
                -8px -8px 16px var(--shadow-light);
  }
  
  .empty-state .material-icons-round {
    font-size: 3rem;
    color: var(--text-secondary);
  margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  .empty-state h3 {
    font-size: 1.25rem;
  color: var(--text-primary);
    margin-bottom: 0.5rem;
  }
  
  .empty-state p {
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
  }
  
  /* Job Details Section */
  .job-details-section {
    margin-top: 1rem;
    padding: 1rem;
    background: rgba(78, 115, 223, 0.05);
    border-radius: var(--radius);
    border: 1px solid rgba(78, 115, 223, 0.1);
  }
  
  .job-details-section h4 {
    margin: 0 0 0.75rem 0;
    color: var(--primary);
    font-size: 1rem;
  }
  
  .job-metadata {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  }
  
  .metadata-row {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .metadata-row:last-child {
    margin-bottom: 0;
  }
  
  .metadata-label {
    font-weight: 500;
    color: var(--text-color);
    min-width: 100px;
    margin-right: 0.5rem;
  }
  
  .metadata-value {
    color: var(--text-muted);
  font-size: 0.9rem;
  }
  
  .model-file {
    font-family: 'Courier New', monospace;
    background: rgba(78, 115, 223, 0.1);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    color: var(--primary);
    font-weight: 500;
  }
  
  /* Model Details Modal */
  .model-details-modal {
    max-width: 700px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .model-details-content {
    display: flex;
    flex-direction: column;
  gap: 1.5rem;
  }
  
  .detail-section h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
  }
  
  .detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  
  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .detail-item .label {
    font-size: 0.85rem;
    color: #666;
    font-weight: 500;
  }
  
  .detail-item .value {
    font-size: 0.95rem;
    color: #333;
    font-weight: 600;
  }
  
  .capabilities-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .capability-tag.large {
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
    background: #e3f2fd;
    color: #1976d2;
  border-radius: 12px;
    font-weight: 500;
  }
  
  .system-prompt {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #4e73df;
  }
  
  .system-prompt p {
    margin: 0;
    color: #333;
    line-height: 1.5;
    white-space: pre-wrap;
  }
  
  /* Modal Actions */
  .modal-actions {
  display: flex;
  align-items: center;
    gap: 0.5rem;
  }
  
  /* Editable Prompt */
  .editable-prompt {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .prompt-textarea {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.4;
    resize: vertical;
    min-height: 200px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 1rem;
    transition: border-color 0.3s ease;
  }
  
  .prompt-textarea:focus {
    border-color: #4e73df;
    outline: none;
    box-shadow: 0 0 0 3px rgba(78, 115, 223, 0.1);
  }
  
  .prompt-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .char-count {
  font-size: 0.8rem;
    color: #666;
    font-weight: 500;
  }
  
  /* Editable Description */
  .editable-description textarea {
    resize: vertical;
    min-height: 80px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 0.75rem;
    transition: border-color 0.3s ease;
  }
  
  .editable-description textarea:focus {
    border-color: #4e73df;
    outline: none;
    box-shadow: 0 0 0 3px rgba(78, 115, 223, 0.1);
  }
  
  /* Edit Mode Styling */
  .detail-section.editing {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #e9ecef;
  }
  
  /* Chat Test Button */
  .chat-test-btn {
    position: absolute;
    top: -84px;
    left: -18px;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #4e73df;
    color: white;
    border: none;
    cursor: pointer;
  display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(78, 115, 223, 0.3);
    transition: all 0.3s ease;
    z-index: 10;
  }

  /* Override for rank-actions buttons */
  .rank-actions .chat-test-btn {
    position: static;
    top: auto;
    left: auto;
    width: 28px;
    height: 28px;
    padding: 0;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.8);
    color: #666;
    border: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: none;
    z-index: auto;
  }
  
  .chat-test-btn:hover {
    background: #3d5fc7;
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(78, 115, 223, 0.4);
  }
  
  .chat-test-btn .material-icons-round {
    font-size: 16px;
  }
  
  .rank-number {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
  gap: 0.5rem;
}

  .rank-actions {
    display: flex;
    gap: 0.25rem;
    float: right;
    margin-top: -30px;
    margin-right: -0;
  }

  .rank-actions .chat-test-btn:hover {
    background: rgba(255, 255, 255, 1);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  .rank-actions .chat-test-btn .material-icons-round {
    font-size: 14px;
    color: #666;
  }
  
  /* Chat Modal */
  .chat-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .chat-modal-content {
    width: 90%;
    max-width: 800px;
    height: 80vh;
    background: #1e1e1e;
  border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  }
  
  .chat-header {
    background: #2d2d2d;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #404040;
  }
  
  .chat-model-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .chat-model-info .material-icons-round {
    color: #4e73df;
  }
  
  .chat-model-info h3 {
    margin: 0;
    color: #fff;
    font-size: 1.1rem;
  }
  
  .model-type {
    background: #4e73df;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  font-size: 0.8rem;
    font-weight: 500;
}

  /* Terminal Styling */
  .chat-terminal {
    height: calc(100% - 80px);
  display: flex;
    flex-direction: column;
}

  .terminal-header {
    background: #333;
    padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
    gap: 1rem;
    border-bottom: 1px solid #404040;
  }
  
  .terminal-controls {
    display: flex;
  gap: 0.5rem;
  }
  
  .control-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }
  
  .control-dot.red { background: #ff5f56; }
  .control-dot.yellow { background: #ffbd2e; }
  .control-dot.green { background: #27ca3f; }
  
  .terminal-title {
    color: #ccc;
  font-size: 0.9rem;
    font-weight: 500;
  }
  
  .terminal-body {
    flex: 1;
    background: #1e1e1e;
    padding: 1rem;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
  }
  
  .terminal-output {
  display: flex;
    flex-direction: column;
  gap: 0.5rem;
  }
  
  .message {
    display: flex;
    gap: 0.5rem;
    line-height: 1.4;
  }
  
  .message-prefix {
    color: #888;
    font-weight: bold;
    min-width: 120px;
  }
  
  .message-content {
    color: #fff;
    flex: 1;
    white-space: pre-wrap;
  }
  
  .message.user .message-prefix {
    color: #4e73df;
  }
  
  .message.ai .message-prefix {
    color: #27ca3f;
  }
  
  .message.system .message-prefix {
    color: #ffbd2e;
  }
  
  .message.error .message-prefix {
    color: #ff5f56;
  }
  
  .message.error .message-content {
    color: #ff5f56;
  }
  
  /* Typing Indicator */
  .typing-indicator {
    display: flex;
    gap: 0.25rem;
    align-items: center;
  }
  
  .typing-dot {
    width: 6px;
    height: 6px;
    background: #4e73df;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
  }
  
  .typing-dot:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  .typing-dot:nth-child(3) {
    animation-delay: 0.4s;
  }
  
  @keyframes typing {
    0%, 60%, 100% {
      transform: translateY(0);
      opacity: 0.5;
    }
    30% {
      transform: translateY(-10px);
      opacity: 1;
    }
  }
  
  /* Terminal Input */
  .terminal-input {
    background: #2d2d2d;
    padding: 1rem;
    border-top: 1px solid #404040;
  }
  
  .input-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  }
  
  .prompt-symbol {
    color: #4e73df;
    font-weight: bold;
    font-family: 'Courier New', monospace;
  }
  
  .terminal-input-field {
    flex: 1;
    background: transparent;
  border: none;
    color: #fff;
    font-family: 'Courier New', monospace;
    font-size: 1rem;
    outline: none;
  }
  
  .terminal-input-field::placeholder {
    color: #666;
  }
  
  .terminal-input-field:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  /* Responsive */
  @media (max-width: 768px) {
    .actions-bar {
      flex-direction: column;
      align-items: stretch;
    }
    
    .search-box {
      max-width: 100%;
    }
    
    .action-buttons {
      width: 100%;
    }
    
    .action-buttons select,
    .action-buttons .btn {
      width: 100%;
    }
    
    .models-grid {
      grid-template-columns: 1fr;
    }
    
    .modal {
      margin: 1rem;
      max-height: calc(100vh - 2rem);
    }
    
    .summary-cards {
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    }
    
    .rankings-grid {
      grid-template-columns: 1fr;
    }
  }
  
  /* Summary Cards */
  .summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .summary-card {
    background: var(--card-bg, #ffffff);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color, #e9ecef);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  .summary-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
  
  .card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #007bff, #0056b3);
    border-radius: 12px;
    margin-bottom: 1rem;
  }
  
  .card-icon .material-icons-round {
    color: white;
    font-size: 24px;
  }
  
  .card-content h3 {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-color, #2c3e50);
    margin: 0 0 0.5rem 0;
  }
  
  .card-content p {
    color: var(--text-muted, #6c757d);
    margin: 0;
    font-size: 0.9rem;
    font-weight: 500;
  }
  
  /* Rankings Section */
  .rankings-section {
  margin-bottom: 2rem;
}

  .rankings-section .section-header {
    margin-bottom: 1.5rem;
  }
  
  .rankings-section .section-header h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0 0 0.5rem 0;
    color: var(--text-color, #2c3e50);
  }
  
  .rankings-section .section-header p {
    color: var(--text-muted, #6c757d);
    margin: 0;
    font-size: 0.9rem;
  }
  
  .rankings-grid {
  display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

  .ranking-card {
    position: relative;
    background: var(--card-bg, #ffffff);
  border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color, #e9ecef);
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    max-width: 450px;
  }
  
  .ranking-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
  
  .clickable-card {
  cursor: pointer;
}

  .clickable-card:hover {
  transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    border-color: var(--primary, #4e73df);
  }
  
  .ranking-card.top-rank {
    border: 2px solid #ffd700;
    background: linear-gradient(135deg, #fff9e6, #ffffff);
  }
  
  .rank-number {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    position: absolute;
    top: -17px;
    left: -17px;
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .rank-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 1.1rem;
    color: white;
  }
  
  .rank-gold {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    color: #8b6914;
  }
  
  .rank-silver {
    background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
    color: #666;
  }
  
  .rank-bronze {
    background: linear-gradient(135deg, #cd7f32, #daa520);
    color: white;
  }
  
  .rank-normal {
    background: linear-gradient(135deg, #6c757d, #868e96);
    color: white;
  }
  
  .model-info {
    flex: 1;
  }
  
  .model-header-with-avatar {
  display: flex;
  align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }
  
  .model-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .model-avatar-placeholder {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--primary-color, #4e73df);
    color: white;
  display: flex;
  align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .model-avatar-placeholder .material-icons-round {
    font-size: 20px;
  }
  
  .model-info h4 {
    margin: 0 0 0.5rem 0;
    color: var(--text-color, #2c3e50);
    font-size: 1.1rem;
    font-weight: 600;
  }
  
  .model-progress {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.5rem;
  padding: 0.5rem;
    background: rgba(78, 115, 223, 0.1);
  border-radius: 8px;
    border: 1px solid rgba(78, 115, 223, 0.2);
  }
  
  .progress-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.9rem;
    font-weight: 600;
    z-index: 44;
    color: var(--primary, #4e73df);
  }
  
  .progress-item .material-icons-round {
    font-size: 18px;
    color: var(--primary, #4e73df);
  }
  
  .model-stats {
    display: flex;
    gap: 1rem;
  margin-bottom: 0.5rem;
}

  .stat {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.85rem;
    color: var(--text-muted, #6c757d);
  }
  
  .stat .material-icons-round {
    font-size: 16px;
  }
  
  .model-capabilities {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  .capability-tag {
    background: #e9ecef;
    color: #495057;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
  }
  
  .capability-more {
    background: rgba(108, 117, 125, 0.1);
    color: #6c757d;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
  }
  
  .model-params {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
  
  .param {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    color: #6c757d;
  }
  
  .param .material-icons-round {
    font-size: 14px;
  }
  
  .rank-score {
    text-align: center;
    flex-shrink: 0;
    top: 9px;
    position: absolute;
    right: 20px;
  }
  
  .score {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color, #007bff);
    margin: 0;
  }
  
  .score-label {
    font-size: 0.75rem;
    color: var(--text-muted, #6c757d);
    margin: 0;
    margin-top: -7px;
  }
  
  /* Model Type Selector */
  .model-type-selector {
  display: grid;
    grid-template-columns: 1fr 1fr;
  gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .type-option {
    display: flex !important;
    align-items: center;
    gap: 1rem;
  padding: 1rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
    background: var(--card-bg);
}

  .type-option:hover {
  border-color: var(--primary);
    background: rgba(78, 115, 223, 0.05);
}

  .type-option.active {
  border-color: var(--primary);
    background: rgba(78, 115, 223, 0.1);
}

  .type-icon {
  font-size: 2rem;
    flex-shrink: 0;
  }
  
  .type-info h4 {
    margin: 0 0 0.25rem 0;
    color: var(--text-color);
    font-size: 1rem;
  }
  
  .type-info p {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.85rem;
  }
  
  /* External API Config */
  .external-api-config {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e9ecef;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  
  /* Local Model Config */
  .local-model-config {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e9ecef;
  }
  
  /* Avatar Upload Styles */
  .avatar-upload {
    margin-top: 0.5rem;
  }
  
  .avatar-preview {
    position: relative;
    display: inline-block;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    overflow: hidden;
    border: 2px solid #e9ecef;
  }
  .model-progress::before {
    width: var(--progress-width, 0%); /* default 0% */
    height: 39px;
    content: "";
    background-color: #92adff75;
    position: absolute;
    margin-top: -9px;
    margin-left: -9px;
    z-index: 9;
    border-radius: 8px;
}
  .avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .remove-avatar {
    position: absolute;
    top: -5px;
    right: -5px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #dc3545;
    color: white;
    border: none;
    cursor: pointer;
    font-size: 12px;
  display: flex;
  align-items: center;
    justify-content: center;
    line-height: 1;
  }
  
  .avatar-upload-area {
    border: 2px dashed #7d97b1;
  border-radius: 8px;
    padding: 1rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .avatar-upload-area:hover {
    border-color: var(--primary);
    background: rgba(78, 115, 223, 0.05);
  }
  
  .upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  
  .upload-icon {
    font-size: 2rem;
    opacity: 0.6;
  }
  
  .upload-placeholder p {
    margin: 0;
    color: var(--text-color);
    font-weight: 500;
  }
  
  .upload-placeholder small {
    color: var(--text-muted);
  font-size: 0.8rem;
}

  /* Color picker styles */
  .color-picker-container {
  display: flex;
  align-items: center;
    gap: 0.75rem;
  }
  
  .color-input {
    width: 60px !important;
    height: 40px;
    padding: 0;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }
  
  .color-preview {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    border: 2px solid var(--border-color);
    box-shadow: var(--shadow-sm);
  }

  /* Responsive modal adjustments */
  @media (max-width: 768px) {
    .modal-content {
      max-height: 95vh;
      margin: 0.5rem;
    }
    
    .modal-body {
      max-height: calc(95vh - 120px);
      padding: 1rem;
    }
    
    .form-row {
    grid-template-columns: 1fr;
  }
  
  .model-type-selector {
    grid-template-columns: 1fr;
  }
}

/* Minion API Section Styles */
.value-with-copy {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.value-with-copy .value {
  flex: 1;
  word-break: break-all;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  background: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.value-with-copy .value.token-value {
  color: #6c757d;
  font-size: 0.8rem;
}

.btn-copy {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
  min-width: 32px;
  height: 32px;
}

.btn-copy:hover {
  background: #0056b3;
}

.btn-copy .material-icons-round {
  font-size: 16px;
}
.material-icons-round {
  font-size: 3.5rem;
  color: #e0e5ec;
  filter: drop-shadow(3px 3px 2px #a3b1c6) drop-shadow(-3px -3px 2px #ffffff);
  margin: 1rem;
  
}
h4 {
  font-weight: 700;
  font-size: 1.2rem !important;
}

/* Capabilities Preview Styles */
.capabilities-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.capability-badge {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid #bbdefb;
}

.form-text.text-muted {
  font-size: 0.8rem;
  color: #6c757d;
  margin-top: 0.5rem;
}

.no-capabilities {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  color: #6c757d;
  font-size: 0.9rem;
}

.no-capabilities .material-icons-round {
  font-size: 18px;
}
</style>