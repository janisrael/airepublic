<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="lora-modal">
      <!-- Modal Header -->
      <div class="modal-header">
        <h2>Refine Minion with External LoRA Training</h2>
        <button class="close-btn" @click="closeModal">
          <span class="material-icons-round">close</span>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Training Configuration -->
        <div class="config-section">
          <h3>LoRA-Style Training Configuration</h3>
          
          <!-- Job Information -->
          <div class="input-group">
            <label for="jobName">Job Name</label>
            <input 
              id="jobName"
              v-model="formData.jobName" 
              type="text" 
              placeholder="Enter training job name"
              :maxlength="100"
            />
          </div>

          <div class="input-group">
            <label for="description">Description</label>
            <textarea 
              id="description"
              v-model="formData.description" 
              placeholder="Describe this LoRA-style training session"
              rows="3"
            ></textarea>
          </div>

          <!-- Minion Selection -->
          <div class="input-group">
            <label>Minion to Enhance</label>
            <div class="minion-info">
              <div class="minion-avatar">
                <img 
                  :src="selectedMinionAvatar" 
                  :alt="selectedMinion?.display_name || 'Minion'"
                  v-if="selectedMinionAvatar"
                />
                <span v-else class="avatar-placeholder">
                  <span class="material-icons-round">android</span>
                </span>
              </div>
              <div class="minion-details">
                <h4>{{ selectedMinion?.display_name || 'Select Minion' }}</h4>
                <p>{{ selectedMinion?.description || 'LoRA-style refinement training' }}</p>
              </div>
            </div>
          </div>

          <!-- Provider Selection -->
          <div class="input-group">
            <label for="provider">LLM Provider</label>
            <select id="provider" v-model="formData.provider">
              <option value="">Select Provider</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="nvidia">NVIDIA</option>
              <option value="huggingface">Hugging Face</option>
            </select>
          </div>

          <!-- Model Selection -->
          <div class="input-group" v-if="formData.provider">
            <label for="modelName">Model</label>
            <select id="modelName" v-model="formData.modelName">
              <option value="">Select Model</option>
              <option v-for="model in availableModels" :key="model.name" :value="model.name">
                {{ model.display_name || model.name }}
              </option>
            </select>
            <p class="helper-text">
              External model that will receive LoRA-style enhancement
            </p>
          </div>

          <!-- Training Datasets -->
          <div class="input-group">
            <label>Training Datasets</label>
            <div class="dataset-selection">
              <div 
                v-for="dataset in availableDatasets" 
                :key="dataset.id"
                class="dataset-item"
                :class="{ 'selected': formData.trainingDatasets.includes(dataset.id) }"
                @click="toggleDataset(dataset.id)"
              >
                <div class="dataset-info">
                  <h5>{{ dataset.name }}</h5>
                  <p>{{ dataset.description }}</p>
                  <span class="dataset-size">Size: {{ dataset.size || 'N/A' }}</span>
                </div>
                <div class="dataset-icon">
                  <span class="material-icons-round">dataset</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Advanced LoRA Settings -->
          <div class="advanced-settings">
            <button 
              class="toggle-advanced" 
              @click="advancedSettingsOpen = !advancedSettingsOpen"
              type="button"
            >
              <span class="material-icons-round">
                {{ advancedSettingsOpen ? 'expand_less' : 'expand_more' }}
              </span>
              Advanced LoRA Settings
            </button>
            
            <div v-show="advancedSettingsOpen" class="advanced-content">
              <!-- Style Analysis Sensitivity -->
              <div class="input-group">
                <label for="styleSensitivity">Style Analysis Sensitivity</label>
                <div class="slider-group">
                  <input 
                    id="styleSensitivity"
                    type="range" 
                    min="0.1" 
                    max="1.0" 
                    step="0.1" 
                    v-model="formData.styleSensitivity"
                  />
                  <span class="slider-value">{{ formData.styleSensitivity }}</span>
                </div>
                <p class="helper-text">Higher values create stronger personality amplification.</p>
              </div>

              <!-- Enhancement Intensity -->
              <div class="input-group">
                <label for="enhancementIntensity">Enhancement Intensity</label>
                <div class="slider-group">
                  <input 
                    id="enhancementIntensity"
                    type="range" 
                    min="0.5" 
                    max="2.0" 
                    step="0.1" 
                    v-model="formData.enhancementIntensity"
                  />
                  <span class="slider-value">{{ formData.enhancementIntensity }}</span>
                </div>
                <p class="helper-text">Controls the intensity of LoRA-style adaptations.</p>
              </div>

              <!-- Personality Traits Filter -->
              <div class="input-group">
                <label>Focus Personality Traits</label>
                <div class="trait-selection">
                  <label v-for="trait in personalityTraits" :key="trait" class="checkbox-label">
                    <input type="checkbox" v-model="formData.selectedTraits" :value="trait" />
                    <span class="trait-name">{{ trait }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Information Panel -->
        <div class="info-panel">
          <div class="info-section">
            <span class="material-icons-round">info</span>
            <div>
              <h4>External LoRA Training</h4>
              <p>Enhances minion personalities using prompt engineering and style adaptation. No local model training required.</p>
            </div>
          </div>
          
          <div class="info-section">
            <span class="material-icons-round">psychology</span>
            <div>
              <h4>Style Enhancement</h4>
              <p>Analyzes existing personality patterns and amplifies them for more consistent responses.</p>
            </div>
          </div>

          <div class="info-section">
            <span class="material-icons-round">memory</span>
            <div>
              <h4>Knowledge Integration</h4>
              <p>Combines personalization with external knowledge bases for enhanced capabilities.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeModal">
          <span class="material-icons-round">cancel</span>
          Cancel
        </button>
        <button 
          class="btn btn-primary" 
          @click="startLoraTraining"
          :disabled="!isFormValid || isLoading"
        >
          <span v-if="isLoading" class="material-icons-round spin">sync</span>
          <span v-else class="material-icons-round">auto_fix</span>
          {{ isLoading ? 'Starting Training...' : 'Start LoRA Enhancement' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'pinia'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'MinionExternalLoraModal',
  props: {
    selectedMinion: {
      type: Object,
      required: true
    },
    isVisible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      formData: {
        jobName: '',
        description: '',
        provider: '',
        modelName: '',
        trainingDatasets: [],
        styleSensitivity: 0.7,
        enhancementIntensity: 1.0,
        selectedTraits: []
      },
      availableModels: [
        { name: 'gpt-4o-mini', display_name: 'GPT-4o Mini' },
        { name: 'gpt-4o', display_name: 'GPT-4o' },
        { name: 'claude-3-5-sonnet-20241022', display_name: 'Claude 3.5 Sonnet' },
        { name: 'claude-3-5-haiku-20241022', display_name: 'Claude 3.5 Haiku' },
        { name: 'nvidia/llama-3.3-nemotron-super-49b-v1.5', display_name: 'Llama 3.3 Nemotron Super' }
      ],
      availableDatasets: [
        { id: 1, name: 'Personality Enhancement', description: 'Enhance personal traits', size: '127 samples' },
        { id: 2, name: 'Communication Style', description: 'Improve response patterns', size: '89 samples' },
        { id: 3, name: 'Domain Knowledge', description: 'Add specialized knowledge', size: '256 samples' }
      ],
      personalityTraits: ['professional', 'friendly', 'technical', 'creative', 'educational'],
      advancedSettingsOpen: false,
      isLoading: false
    }
  },
  computed: {
    ...mapState(useAuthStore, ['user']),
    isFormValid() {
      return (
        this.formData.jobName.trim() &&
        this.formData.provider &&
        this.formData.modelName &&
        this.formData.trainingDatasets.length > 0
      )
    },
    selectedMinionAvatar() {
      return this.selectedMinion?.avatar || null
    }
  },
  watch: {
    selectedMinion: {
      handler(newMinion) {
        if (newMinion) {
          this.formData.jobName = `LoRA Enhancement: ${newMinion.display_name}`
          this.formData.description = `External LoRA-style training for ${newMinion.display_name}`
        }
      },
      immediate: true
    },
    'formData.provider'() {
      this.formData.modelName = ''
    }
  },
  methods: {
    closeModal() {
      this.$emit('close')
    },
    
    toggleDataset(datasetId) {
      const index = this.formData.trainingDatasets.indexOf(datasetId)
      if (index > -1) {
        this.formData.trainingDatasets.splice(index, 1)
      } else {
        this.formData.trainingDatasets.push(datasetId)
      }
    },

    async startLoraTraining() {
      if (!this.isFormValid || this.isLoading) return

      this.isLoading = true
      
      try {
        const requestData = {
          minion_id: this.selectedMinion.id,
          job_name: this.formData.jobName.trim(),
          description: this.formData.description.trim(),
          provider: this.formData.provider,
          model_name: this.formData.modelName,
          training_datasets: this.formData.trainingDatasets,
          advanced_config: {
            style_sensitivity: this.formData.styleSensitivity,
            enhancement_intensity: this.formData.enhancementIntensity,
            selected_traits: this.formData.selectedTraits
          }
        }

        const response = await fetch(`/api/users/${this.user.id}/external-lora-training/jobs`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          },
          body: JSON.stringify(requestData)
        })

        const data = await response.json()

        if (data.success) {
          alert(`LoRA Training Started!\nExternal LoRA enhancement job "${this.formData.jobName}" has been created successfully.`)

          this.$emit('training-started', {
            jobId: data.job_id,
            jobData: data.data,
            trainingType: 'external_lora'
          })

          this.closeModal()
        } else {
          throw new Error(data.error || 'Failed to start training')
        }

      } catch (error) {
        console.error('Error starting LoRA training:', error)
        
        alert(`Training Failed!\n${error.message || 'Failed to start External LoRA training. Please try again.'}`)
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
/* Import main external LoRA training styles */
@import '@/assets/external-lora-training.css';

/* Component-specific overrides */
.lora-modal {
  max-height: 90vh;
  width: 70rem;
}

.config-section h3 {
  margin-bottom: 1.5rem;
  color: #6366f1;
}

.minion-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
}

.minion-avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.minion-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #6366f1;
  color: white;
}

.minion-details h4 {
  margin: 0;
  color: #1e293b;
  font-size: 1.1rem;
}

.minion-details p {
  margin: 0.25rem 0 0;
  color: #64748b;
  font-size: 0.875rem;
}

.dataset-selection {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.dataset-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dataset-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.dataset-item.selected {
  background: #e0e7ff;
  border-color: #6366f1;
}

.dataset-info h5 {
  margin: 0 0 0.25rem;
  color: #1e293b;
  font-size: 0.95rem;
}

.dataset-info p {
  margin: 0 0 0.25rem;
  color: #64748b;
  font-size: 0.8rem;
}

.dataset-size {
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 500;
}

.dataset-icon {
  color: #6366f1;
}

.advanced-settings {
  border-top: 1px solid #e2e8f0;
  padding-top: 1.5rem;
  margin-top: 1.5rem;
}

.toggle-advanced {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #6366f1;
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem 0;
}

.trait-selection {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
}

.checkbox-label:hover {
  background: #f8fafc;
}

.trait-name {
  text-transform: capitalize;
  font-size: 0.875rem;
  color: #374151;
}

.slider-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.slider-group input[type="range"] {
  flex: 1;
}

.slider-value {
  min-width: 3rem;
  text-align: center;
  font-weight: 500;
  color: #6366f1;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
}

.info-panel {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.info-section {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-section:last-child {
  margin-bottom: 0;
}

.info-section .material-icons-round {
  margin-top: 0.25rem;
  color: #6366f1;
}

.info-section h4 {
  margin: 0 0 0.25rem;
  color: #1e293b;
  font-size: 1rem;
}

.info-section p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.5;
}

.loading .material-icons-round.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
