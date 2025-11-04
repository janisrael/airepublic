<template>
  <div class="training-container">
    <div class="page-header">
      <div>
        <h1>Model Training</h1>
        <p>Train and fine-tune your AI models</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="openExternalTrainingModal">
          <Icon name="smart_toy" size="sm" color="light" />
          Refine Minion
        </button>
        <button class="btn btn-primary" @click="startNewTraining">
          <Icon name="play_arrow" size="sm" color="light" />
          New Training
        </button>
      </div>
    </div>

    <!-- Training Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="model_training" size="lg" color="primary" />
        </div>
        <div class="card-content">
          <h3>{{ totalJobsCount }}</h3>
          <p>Total Jobs</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="play_arrow" size="lg" color="success" />
        </div>
        <div class="card-content">
          <h3>{{ runningJobsCount }}</h3>
          <p>Running</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="check_circle" size="lg" color="success" />
        </div>
        <div class="card-content">
          <h3>{{ completedJobsCount }}</h3>
          <p>Completed</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="error" size="lg" color="danger" />
        </div>
        <div class="card-content">
          <h3>{{ failedJobsCount }}</h3>
          <p>Failed</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="storage" size="lg" color="info" />
        </div>
        <div class="card-content">
          <h3>{{ chromadbCollections }}</h3>
          <p>ChromaDB Collections</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="smart_toy" size="lg" color="info" />
        </div>
        <div class="card-content">
          <h3>{{ ollamaModels.length }}</h3>
          <p>Available Models</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="dataset" size="lg" color="warning" />
        </div>
        <div class="card-content">
          <h3>{{ availableDatasets.length }}</h3>
          <p>Datasets</p>
        </div>
      </div>
    </div>

    <!-- Available Models Overview -->
    <div class="capabilities-overview">
      <div class="section-header">
        <h2>Available Models</h2>
        <p v-if="ollamaModels.length === 0" class="no-models-message">
          No Ollama models found. Install some models to get started!
        </p>
      </div>
      <div class="capabilities-grid">
        <div v-for="model in ollamaModels" :key="model.name" class="capability-card">
          <div class="capability-icon">
            <Icon :name="getModelIcon(model.capabilities)" size="lg" :color="getModelColor(model.capabilities)" />
          </div>
          <h3>{{ model.name }}</h3>
          <p>{{ getModelDescription(model.capabilities) }}</p>
          <div class="model-info">
            <span class="model-size">{{ model.size }}</span>
            <span class="model-modified">{{ model.modified }}</span>
          </div>
          <div class="capability-models">
            <span v-for="capability in getCapabilitiesArray(model.capabilities)" :key="capability" class="model-tag">
              {{ capability }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Training Switch -->
    <TrainingSwitch v-model="activeTrainingTab" />

    <!-- Local Training Section -->
    <div v-if="activeTrainingTab === 'local'" class="local-training-section">
      <div class="section-header">
        <h2>🏠 Local Training</h2>
        <p>Train models on your local Ollama instance</p>
      </div>
      
      <div class="jobs-grid">
        <!-- Local Training Jobs -->
        <div v-for="job in trainingJobs" :key="`local-${job.id}`" class="job-card">
          <div class="job-header">
            <h3>{{ getJobDisplayName(job) }}</h3>
            <div class="job-badges">
              <span class="job-badge local">Local</span>
              <span class="job-status" :class="job.status.toLowerCase()">
                {{ job.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

        <!-- Minion Refinement Section -->
        <MinionTrainingSection 
          v-else-if="activeTrainingTab === 'external'"
          ref="minionTrainingSection"
          :pending-jobs="pendingJobs"
          @view-history="handleViewHistory"
          @upgrade-minion="handleUpgradeMinion"
          @create-minion="handleCreateMinion"
          @view-pending-job="handleViewPendingJob"
          @start-pending-training="handleStartPendingTraining"
          @delete-pending-job="handleDeletePendingJob"
          @training-completed="handleTrainingCompleted"
        />


    <!-- OLD EXTERNAL TRAINING JOBS - REMOVED AND REPLACED WITH NEW COMPONENTS -->

    <!-- New Training Modal -->
    <div v-if="showTrainingModal" class="modal-overlay" @click.self="showTrainingModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Start New AI Training</h2>
          <button class="btn-icon" @click="showTrainingModal = false">✕</button>
        </div>
        
        <div class="modal-body">
          <!-- Training Job Metadata -->
          <div class="training-metadata">
            <h3>Training Job Information</h3>
            <div class="metadata-grid">
              <div class="form-group">
                <label>Model Name <span class="required">*</span></label>
                <input 
                  type="text" 
                  v-model="newTraining.jobName" 
                  placeholder="e.g., My Custom AI Assistant"
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
                <small>Version tag (will create name:version format for Ollama)</small>
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
              
              <div class="form-group">
                <label>Custom Capabilities</label>
                <input 
                  type="text" 
                  v-model="newTraining.customCapabilities" 
                  placeholder="e.g., DevOps, Kubernetes, Docker, CI/CD"
                  class="form-control"
                >
                <small>Comma-separated custom capabilities (will be added to model capabilities)</small>
              </div>
              
              <div class="form-group">
                <label>Maker/Creator</label>
                <input 
                  type="text" 
                  v-model="newTraining.maker" 
                  placeholder="e.g., swordfish, Agimat Team"
                  class="form-control"
                >
                <small>Who is creating this training job</small>
              </div>
            </div>
          </div>

          <!-- Training Type Selection -->
          <div class="form-group">
            <label>Training Type</label>
            <div class="training-types">
              <label class="training-type-card" :class="{ active: newTraining.type === 'lora' }">
                <input type="radio" v-model="newTraining.type" value="lora" hidden>
                <div class="type-icon">🎯</div>
                <h4>LoRA Fine-tuning</h4>
                <p>Train custom roles/personas with minimal resources</p>
              </label>
              
              <label class="training-type-card" :class="{ active: newTraining.type === 'rag' }">
                <input type="radio" v-model="newTraining.type" value="rag" hidden>
                <div class="type-icon">📚</div>
                <h4>RAG System</h4>
                <p>Build knowledge retrieval system</p>
              </label>
              
              <label class="training-type-card" :class="{ active: newTraining.type === 'full' }">
                <input type="radio" v-model="newTraining.type" value="full" hidden>
                <div class="type-icon">🚀</div>
                <h4>Full Fine-tuning</h4>
                <p>Complete model training (requires more resources)</p>
              </label>
            </div>
          </div>

          <!-- Dynamic Model Selection -->
          <div class="form-group">
            <label>Base Model</label>
            <select v-model="newTraining.baseModel" class="form-control">
              <option value="">Select base model</option>
              <option v-for="model in ollamaModels" :key="model.name" :value="model.name">
                {{ getModelDisplayOption(model) }}
              </option>
            </select>
          </div>

          <!-- Training Configuration -->
          <div v-if="newTraining.type === 'lora'" class="lora-config">
            <h3>LoRA Configuration</h3>
            <div class="config-grid">
              <div class="form-group">
                <label>Rank (r)</label>
                <input type="number" v-model="newTraining.loraConfig.rank" min="1" max="64" class="form-control">
                <small>Higher rank = more parameters, better performance</small>
              </div>
              <div class="form-group">
                <label>Alpha</label>
                <input type="number" v-model="newTraining.loraConfig.alpha" min="1" max="128" class="form-control">
                <small>Scaling factor for LoRA weights</small>
              </div>
              <div class="form-group">
                <label>Dropout</label>
                <input type="number" v-model="newTraining.loraConfig.dropout" min="0" max="0.5" step="0.01" class="form-control">
                <small>Prevent overfitting</small>
              </div>
            </div>
          </div>

          <!-- Dataset Selection -->
          <div class="form-group">
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
                  <div class="dataset-actions">
                    <Icon name="info" size="xs" color="muted" class="info-icon" 
                          @click.stop="showDatasetInfo(dataset)" />
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
              
              <!-- Create Knowledge Base -->
              <label class="dataset-option">
                <input type="checkbox" v-model="newTraining.datasetType" value="create" hidden>
                <div class="option-card">
                  <Icon name="add" size="sm" color="info" />
                  <span>Create Knowledge Base</span>
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
              <div class="training-strategy">
                <label>Training Strategy:</label>
                <select v-model="newTraining.trainingStrategy" class="form-control">
                  <option value="concatenate">Concatenate (Combine all datasets)</option>
                  <option value="mix">Mix (Interleave samples)</option>
                  <option value="multitask">Multi-task (Separate tasks)</option>
                </select>
                <small>
                  <span v-if="newTraining.trainingStrategy === 'concatenate'">All datasets combined into one large training set</span>
                  <span v-if="newTraining.trainingStrategy === 'mix'">Samples from different datasets mixed during training</span>
                  <span v-if="newTraining.trainingStrategy === 'multitask'">Different datasets trained as separate tasks</span>
                </small>
              </div>
            </div>
          </div>

          <!-- Role Definition -->
          <div v-if="newTraining.type === 'lora'" class="form-group">
            <label>Role Definition</label>
            <textarea 
              v-model="newTraining.roleDefinition" 
              placeholder="You are Agimat, an advanced AI assistant specialized in debugging and code analysis..."
              class="form-control"
              rows="4"
            ></textarea>
            <small>Define the AI's personality, role, and behavior</small>
          </div>

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
                <label>Context Length</label>
                <input type="number" v-model="newTraining.context_length" min="512" max="32768" step="512" class="form-control">
                <small>Maximum context window size</small>
              </div>
            </div>
          </div>

          <!-- Avatar Upload -->
          <div class="form-group">
            <label>Model Avatar <small>(Optional)</small></label>
            <div class="avatar-upload">
              <div class="avatar-preview" v-if="newTraining.avatarPreview">
                <img :src="newTraining.avatarPreview" alt="Avatar preview" class="preview-image">
                <button type="button" class="remove-avatar" @click="removeAvatar">
                  <Icon name="close" size="xs" color="danger" />
                </button>
              </div>
              <div v-else class="avatar-placeholder">
                <Icon name="image" size="lg" color="muted" />
                <p>No avatar selected</p>
              </div>
              <input 
                type="file" 
                ref="avatarInput"
                @change="handleAvatarUpload" 
                accept="image/*"
                class="avatar-input"
                id="avatar-upload"
              >
              <label for="avatar-upload" class="avatar-upload-btn">
                <Icon name="upload" size="sm" color="primary" />
                {{ newTraining.avatarPreview ? 'Change Avatar' : 'Upload Avatar' }}
              </label>
              <small>Upload an image to personalize your model (PNG, JPG, GIF, WEBP - Max 5MB)</small>
            </div>
          </div>

          <!-- Training Parameters -->
          <div class="training-params">
            <h3>Training Parameters</h3>
            <div class="params-grid">
              <div class="form-group">
                <label>Learning Rate</label>
                <input type="number" v-model="newTraining.params.learningRate" step="0.0001" class="form-control">
              </div>
              <div class="form-group">
                <label>Batch Size</label>
                <input type="number" v-model="newTraining.params.batchSize" min="1" max="32" class="form-control">
              </div>
              <div class="form-group">
                <label>Epochs</label>
                <input type="number" v-model="newTraining.params.epochs" min="1" max="100" class="form-control">
              </div>
              <div class="form-group">
                <label>Max Steps</label>
                <input type="number" v-model="newTraining.params.maxSteps" min="100" max="10000" class="form-control">
              </div>
            </div>
          </div>

          <!-- RAG Configuration -->
          <div v-if="newTraining.type === 'rag'" class="rag-config">
            <h3>RAG Configuration</h3>
            <div class="form-group">
              <label>Knowledge Base</label>
              <div class="file-upload">
                <input type="file" @change="handleFileUpload" multiple accept=".md,.txt,.pdf" id="file-upload">
                <label for="file-upload" class="upload-btn">
                  <span class="emoji">📄</span>
                  Upload Documents
                </label>
                <div v-if="uploadedFiles.length > 0" class="uploaded-files">
                  <div v-for="file in uploadedFiles" :key="file.name" class="file-item">
                    <span class="emoji">📄</span>
                    <span>{{ file.name }}</span>
                    <button @click="removeFile(file)" class="btn-icon">✕</button>
                  </div>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>Chunk Size</label>
              <input type="number" v-model="newTraining.ragConfig.chunkSize" min="100" max="2000" class="form-control">
              <small>Size of text chunks for embedding</small>
            </div>
            <div class="form-group">
              <label>Top K Results</label>
              <input type="number" v-model="newTraining.ragConfig.topK" min="1" max="20" class="form-control">
              <small>Number of relevant chunks to retrieve</small>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <!-- Debug Info -->
          <div v-if="!canStartTraining" class="debug-info">
            <small class="text-muted">
              Missing: 
              <span v-if="!newTraining.jobName.trim()">Job Name, </span>
              <span v-if="!newTraining.baseModel">Base Model, </span>
              <span v-if="newTraining.selectedDatasets.length === 0 && uploadedFiles.length === 0">Datasets or Files</span>
            </small>
          </div>
          
          <button class="btn btn-secondary" @click="showTrainingModal = false">
            Cancel
          </button>
          <button class="btn btn-primary" @click="createTrainingJob" :disabled="!canStartTraining">
            Start Training
          </button>
        </div>
      </div>
    </div>

    <!-- Real-time Training Output Component -->
    <TrainingOutput 
      :currentJob="selectedJob" 
      @status-changed="handleStatusChange"
    />

    <!-- External Training Modal -->
    <ExternalTrainingModal
      ref="externalTrainingModal"
      :showModal="showExternalTrainingModal"
      :availableMinions="availableMinions"
      :availableDatasets="availableDatasets"
      :initialData="newExternalTraining"
      @close="closeExternalTrainingModal"
      @create-training="createExternalTrainingJob"
    />

    <!-- Minion History Modal -->
    <!-- Minion History previously shown as modal; now navigate to dedicated page -->

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Confirm Delete</h2>
          <button class="btn-icon" @click="cancelDeletePendingJob">✕</button>
        </div>
        <div class="modal-body">
          <p v-if="deleteTargetJob">Are you sure you want to delete the training job
            <strong>"{{ deleteTargetJob.job_name || deleteTargetJob.jobName || 'Unnamed' }}"</strong>?</p>
          <p v-if="deleteTargetJob">This will remove the job record and associated resources (knowledge base, artifacts).</p>
          <div v-if="deleteTargetJob" class="job-metadata">
            <div class="metadata-row"><span class="metadata-label">Minion:</span><span class="metadata-value">{{ deleteTargetJob.minion_name || deleteTargetJob.minionName || deleteTargetJob.minionId }}</span></div>
            <div class="metadata-row"><span class="metadata-label">Type:</span><span class="metadata-value">{{ deleteTargetJob.training_type || deleteTargetJob.type || deleteTargetJob.jobType }}</span></div>
            <div class="metadata-row"><span class="metadata-label">Created:</span><span class="metadata-value">{{ formatDate(deleteTargetJob.created_at || deleteTargetJob.createdAt) }}</span></div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelDeletePendingJob">Cancel</button>
          <button class="btn btn-danger" @click="confirmDeletePendingJob">Confirm Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Icon from '../components/Icon.vue';
import TrainingOutput from '../components/TrainingOutput.vue';
import ExternalTrainingModal from '../components/ExternalTrainingModal.vue';
import MinionHistory from '../components/MinionHistory.vue';
import TrainingSwitch from '../components/TrainingSwitch.vue';
import MinionTrainingSection from '../components/MinionTrainingSection.vue';
import { io } from 'socket.io-client';
import { useAuthStore } from '../stores/auth';
import { API_ENDPOINTS, getUserApiUrl, getApiUrl } from '@/config/api';
import '../assets/minion_training.css';
export default {
  name: 'TrainingView',
  components: {
    Icon,
    TrainingOutput,
    ExternalTrainingModal,
    MinionHistory,
    TrainingSwitch,
    MinionTrainingSection
  },
  data() {
    return {
      activeTrainingTab: 'external', // Default to external as requested
      showTrainingModal: false,
      showExternalTrainingModal: false,
      showMinionHistory: false,
      selectedMinionForHistory: null,
      uploadedFiles: [],
      availableDatasets: [],
      availableMinions: [],
      ollamaModels: [],
      newTraining: {
        jobName: '',
        description: '',
        customCapabilities: '',
        maker: 'TheSwordfish',
        version: '',
        type: 'lora',
        baseModel: '',
        datasetType: 'upload',
        selectedDatasets: [],
        trainingStrategy: 'concatenate',
        roleDefinition: 'You are Agimat, an advanced AI assistant specialized in debugging and code analysis. You provide step-by-step guidance, identify issues, and offer practical solutions.',
        temperature: 0.7,
        top_p: 0.9,
        context_length: 4096,
        avatarFile: null,
        avatarPreview: null,
        loraConfig: {
          rank: 8,
          alpha: 32,
          dropout: 0.05
        },
        params: {
          learningRate: 0.0002,
          batchSize: 4,
          epochs: 3,
          maxSteps: 2000
        },
        ragConfig: {
          chunkSize: 1000,
          topK: 4
        }
      },
      newExternalTraining: {
        jobName: '',
        description: '',
        minionId: null,
        provider: '',
        model: '',
        type: 'rag',
        selectedDatasets: [],
        roleDefinition: '',
        temperature: 0.7,
        top_p: 0.9,
        max_tokens: 1024,
        ragConfig: {
          chunkSize: 1000,
          topK: 4
        }
      },
      trainingJobs: [],
      externalTrainingJobs: [],
      chromadbCollections: 0,
      selectedJob: null,
      authStore: useAuthStore(),
      statusPollingInterval: null
      ,showDeleteConfirmModal: false,
      deleteTargetJob: null
    };
  },
  computed: {
    canStartTraining() {
      const hasJobName = !!this.newTraining.jobName.trim();
      const hasBaseModel = !!this.newTraining.baseModel;
      const hasDatasets = this.newTraining.selectedDatasets.length > 0;
      const hasUploadedFiles = this.uploadedFiles.length > 0;
      
      // For RAG training, we need either datasets OR uploaded files (not both)
      if (this.newTraining.type === 'rag') {
        return hasJobName && hasBaseModel && (hasDatasets || hasUploadedFiles);
      }
      
      // For other training types, we need datasets OR uploaded files
      return hasJobName && hasBaseModel && (hasDatasets || hasUploadedFiles);
    },
    totalSelectedSamples() {
      return this.newTraining.selectedDatasets.reduce((total, datasetId) => {
        return total + this.getDatasetSamples(datasetId);
      }, 0);
    },
    runningJobsCount() {
      const localRunning = this.trainingJobs.filter(job => job.status === 'RUNNING').length;
      const externalRunning = this.externalTrainingJobs.filter(job => job.status === 'RUNNING').length;
      return localRunning + externalRunning;
    },
    completedJobsCount() {
      const localCompleted = this.trainingJobs.filter(job => job.status === 'COMPLETED').length;
      const externalCompleted = this.externalTrainingJobs.filter(job => job.status === 'COMPLETED').length;
      return localCompleted + externalCompleted;
    },
    failedJobsCount() {
      const localFailed = this.trainingJobs.filter(job => job.status === 'FAILED').length;
      const externalFailed = this.externalTrainingJobs.filter(job => job.status === 'FAILED').length;
      return localFailed + externalFailed;
    },
    totalJobsCount() {
      return this.trainingJobs.length + this.externalTrainingJobs.length;
    },
    pendingJobs() {
      return this.externalTrainingJobs.filter(job => job.status === 'PENDING');
    }
  },
  methods: {
    // New component event handlers
    handleViewHistory(minion) {
      console.log('📊 View history for minion:', minion);
      this.selectedMinionForHistory = {
        id: minion.id,
        name: minion.display_name
      };
      console.log('📊 selectedMinionForHistory set to:', this.selectedMinionForHistory);
      this.showMinionHistory = true;
      console.log('📊 showMinionHistory set to:', this.showMinionHistory);
    },

    handleUpgradeMinion(minion) {
      console.log('🔄 Upgrade minion:', minion);
      
      // Parse the latest training config to get previous settings
      let previousConfig = {};
      if (minion.latest_training?.config) {
        try {
          previousConfig = typeof minion.latest_training.config === 'string' 
            ? JSON.parse(minion.latest_training.config) 
            : minion.latest_training.config;
        } catch (e) {
          console.warn('Failed to parse previous config:', e);
        }
      }
      
      // Determine if this is a LoRA upgrade based on training type
      const latestTrainingType = minion.latest_training?.training_type || 'lora';
      const isLoRAUpgrade = latestTrainingType === 'lora' || latestTrainingType === 'EXTERNAL_LORA';
      
      // For LoRA upgrades: start fresh (no datasets needed for style enhancement)
      // For RAG/Hybrid upgrades: filter selectedDatasets to only include datasets that still exist
      const validDatasets = [];
      if (!isLoRAUpgrade && previousConfig.selectedDatasets) {
        validDatasets.push(...previousConfig.selectedDatasets.filter(id => 
          this.availableDatasets.some(dataset => dataset.id === id)
        ));
      }
      
      // Pre-fill the external training modal with minion data from latest training
      this.newExternalTraining = {
        jobName: isLoRAUpgrade 
          ? `${minion.display_name} Style Refinement`
          : `${minion.display_name} v${this.getNextVersion(minion)}`,
        description: isLoRAUpgrade
          ? `Enhance ${minion.display_name}'s personality and communication style`
          : (minion.latest_training?.description || `Upgrade ${minion.display_name} with additional training`),
        minionId: minion.id,
        provider: minion.provider || 'openai',
        model: minion.latest_training?.model_name || minion.name || 'gpt-4o-mini',
        type: isLoRAUpgrade ? 'lora' : (minion.latest_training?.training_type || 'rag'),
        selectedDatasets: validDatasets, // Only include valid datasets
        roleDefinition: previousConfig.roleDefinition || `I am ${minion.display_name}, an advanced AI assistant.`,
        temperature: previousConfig.temperature || 0.7,
        top_p: previousConfig.top_p || 0.9,
        max_tokens: previousConfig.max_tokens || 1024,
        ragConfig: {
          chunkSize: previousConfig.ragConfig?.chunkSize || 1000,
          topK: previousConfig.ragConfig?.topK || 4
        },
        loraConfig: {
          styleSensitivity: previousConfig.loraConfig?.styleSensitivity || 0.7,
          enhancementIntensity: previousConfig.loraConfig?.enhancementIntensity || 1.0,
          selectedTraits: previousConfig.loraConfig?.selectedTraits || []
        }
      };
      
      console.log('📝 Pre-filled training data:', this.newExternalTraining);
      this.showExternalTrainingModal = true;
      
      // Only show dataset cleanup notice for non-LoRA upgrades
      if (!isLoRAUpgrade && previousConfig.selectedDatasets && validDatasets.length !== previousConfig.selectedDatasets.length) {
        const removedCount = previousConfig.selectedDatasets.length - validDatasets.length;
        console.log(`🧹 Upgraded ${minion.display_name}: Cleared ${removedCount} unavailable datasets`);
        // alert(`Upgrade Notice: Cleared ${removedCount} unavailable dataset(s) from previous training. Please select current datasets.`);
      }
      
      // Force populate the modal after it opens
      this.$nextTick(() => {
        if (this.$refs.externalTrainingModal) {
          console.log('📝 Calling populateForm on modal ref');
          this.$refs.externalTrainingModal.populateForm(this.newExternalTraining);
        }
      });
    },

    handleCreateMinion() {
      console.log('➕ Create new minion');
      // Navigate to minion creation or open modal
      this.$router.push('/models');
    },

    handleViewPendingJob(job) {
      console.log('👁️ View pending job:', job);
      // Show job details in a modal or expand the card
      alert(`Viewing pending job: ${job.job_name}\nStatus: ${job.status}\nCreated: ${job.created_at}`);
    },

    handleStartPendingTraining(job) {
      console.log('🚀 Start pending training:', job);
      // Show the training overlay on the minion card immediately when user clicks Train
      const minionCardRef = this.$refs.minionTrainingSection?.$refs[`minionCard-${job.minionId}`];
      if (minionCardRef && minionCardRef[0]) {
        minionCardRef[0].startTrainingProgress(job.id);
      }

      // Then call API to start the training in the background
      this.startTraining(job.id, job.minionId);
    },

    handleDeletePendingJob(job) {
      // Open custom confirmation modal instead of browser confirm()
      console.log('🗑️ Prompt delete pending job (modal):', job);
      this.deleteTargetJob = job;
      this.showDeleteConfirmModal = true;
    },

    async handleTrainingCompleted(minionId) {
      console.log('🎉 Training completed for minion:', minionId);
      // Refresh external training jobs to update pendingJobs computed property
      await this.fetchExternalTrainingJobs();
      // Refresh minions to update latest_training info
      await this.refreshMinions();
    },

    cancelDeletePendingJob() {
      this.deleteTargetJob = null;
      this.showDeleteConfirmModal = false;
    },

    async confirmDeletePendingJob() {
      if (!this.deleteTargetJob) return;
      const jobId = this.deleteTargetJob.id;
      try {
        // Call delete without the built-in confirm prompt
        await this.deleteTraining(jobId, true);
        // Close modal and refresh minions/jobs to update UI (will show View History / Upgrade)
        this.showDeleteConfirmModal = false;
        this.deleteTargetJob = null;
        await this.fetchExternalTrainingJobs();
        await this.refreshMinions();
      } catch (err) {
        console.error('Error confirming delete:', err);
        this.showError('Failed to delete job: ' + (err.message || String(err)));
      }
    },

    getNextVersion(minion) {
      // Extract version from latest training job name
      const latestJobName = minion.latest_training.job_name;
      const versionMatch = latestJobName.match(/v(\d+\.\d+)/);
      if (versionMatch) {
        const currentVersion = parseFloat(versionMatch[1]);
        return (currentVersion + 0.1).toFixed(1);
      }
      return '1.1';
    },

    // Pending jobs methods
    getDatasetNames(config) {
      if (!config) return 'No datasets';
      try {
        const parsed = typeof config === 'string' ? JSON.parse(config) : config;
        if (parsed.datasetNames && Array.isArray(parsed.datasetNames)) {
          return parsed.datasetNames.map(d => d.name).join(', ');
        }
        return 'Unknown datasets';
      } catch (e) {
        return 'Invalid config';
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString();
    },

    async startTraining(jobId, minionId = null) {
      try {
        console.log('🚀 Starting training job:', jobId);

        const response = await fetch(`${API_ENDPOINTS.v2.trainingJobs}/${jobId}/start`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.authStore.token}`,
            'Content-Type': 'application/json'
          }
        });

        const result = await response.json();
        if (result.success) {
          console.log('✅ Training started successfully');

          // Start real-time progress polling for this specific job
          this.startProgressPolling(jobId);

          // If a minion card ref was provided, tell the card to show connecting state
          if (minionId && this.$refs.minionTrainingSection) {
            const minionCardRef = this.$refs.minionTrainingSection.$refs[`minionCard-${minionId}`];
            if (minionCardRef && minionCardRef[0]) {
              // Tell card to show connecting first, then overlay after confirmed by status
              minionCardRef[0].setConnecting(true);
            }
          }

          // Refresh the jobs list
          await this.fetchTrainingJobs();
          // Restart status polling since we now have a running job
          this.startStatusPolling();
        } else {
          console.error('❌ Failed to start training:', result.error);
          alert('Failed to start training: ' + result.error);
        }
      } catch (error) {
        console.error('❌ Error starting training:', error);
        alert('Error starting training: ' + (error.message || String(error)));
      }
    },

    startProgressPolling(jobId) {
      console.log('🔄 Starting progress polling for job:', jobId);
      
      // Poll every 2 seconds for progress updates
      const pollInterval = setInterval(async () => {
        try {
          const response = await fetch(getUserApiUrl(this.authStore.user.id, `external-training/jobs/${jobId}`), {
            headers: {
              'Authorization': `Bearer ${this.authStore.token}`
            }
          });
          
          if (response.ok) {
            const job = await response.json();
            console.log('📊 Job progress:', job);
            
            // Update the specific minion card with progress
            const minionCardRef = this.$refs.minionTrainingSection?.$refs[`minionCard-${job.minion_id}`];
            if (minionCardRef && minionCardRef[0]) {
              minionCardRef[0].updateTrainingProgress(job);
            }
            
            // Stop polling if job is completed or failed
            if (job.status === 'COMPLETED' || job.status === 'FAILED') {
              clearInterval(pollInterval);
              console.log('✅ Progress polling stopped - job finished');
              
              // Refresh the jobs list to show final status
              await this.fetchExternalTrainingJobs();
            }
          }
        } catch (error) {
          console.error('❌ Error polling job progress:', error);
          clearInterval(pollInterval);
        }
      }, 2000);
      
      // Store the interval ID for cleanup
      this.progressPollingIntervals = this.progressPollingIntervals || {};
      this.progressPollingIntervals[jobId] = pollInterval;
    },

    async deleteTraining(jobId, skipConfirm = false) {
      if (!skipConfirm) {
        if (!confirm('Are you sure you want to delete this training job?')) {
          return;
        }
      }

      try {
        console.log('🗑️ Deleting training job:', jobId);
        const response = await fetch(`${API_ENDPOINTS.v2.trainingJobs}/${jobId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${this.authStore.token}`,
            'Content-Type': 'application/json'
          }
        });

        const result = await response.json();
        if (result.success) {
          console.log('✅ Training job deleted successfully');
          // Refresh the jobs list
          await this.fetchExternalTrainingJobs();
          // Also refresh minions so cards update
          await this.refreshMinions();
        } else {
          console.error('❌ Failed to delete training job:', result.error);
          alert('Failed to delete training job: ' + result.error);
        }
      } catch (error) {
        console.error('❌ Error deleting training job:', error);
        alert('Error deleting training job: ' + error.message);
      }
    },

    initializeSocket() {
      // Socket.IO disabled - using simple status polling instead
      console.log('📊 Socket.IO disabled - using status polling for training jobs');
    },
    
    startStatusPolling() {
      // Stop existing polling if any
      this.stopStatusPolling();
      
      // Poll for status updates every 30 seconds (reduced frequency)
      this.statusPollingInterval = setInterval(async () => {
        const hasRunningTrainingJobs = this.trainingJobs.some(job => job.status === 'RUNNING');
        const hasRunningExternalJobs = this.externalTrainingJobs.some(job => job.status === 'RUNNING');
        
        if (hasRunningTrainingJobs || hasRunningExternalJobs) {
          console.log('🔄 Polling for training job status updates...');
          
          // Only fetch what's actually needed
          if (hasRunningTrainingJobs) {
            await this.fetchTrainingJobs();
          }
          if (hasRunningExternalJobs) {
            await this.fetchExternalTrainingJobs();
          }
        } else {
          // No running jobs, stop polling to save resources
          console.log('⏸️ No running jobs detected, stopping status polling');
          this.stopStatusPolling();
        }
      }, 30000); // Poll every 30 seconds (was 10 seconds)
      
      console.log('▶️ Status polling started');
    },
    
    stopStatusPolling() {
      if (this.statusPollingInterval) {
        clearInterval(this.statusPollingInterval);
        this.statusPollingInterval = null;
        console.log('🛑 Status polling stopped');
      }
    },
    
    updateTrainingProgress(data) {
      // Find the training job and update its progress
      const jobIndex = this.trainingJobs.findIndex(job => job.id === data.job_id);
      if (jobIndex !== -1) {
        // Update progress with real-time data
        this.trainingJobs[jobIndex].progress = data.progress;
        
        // Update step information if available
        if (data.current_step && data.total_steps) {
          this.trainingJobs[jobIndex].currentStep = data.current_step;
          this.trainingJobs[jobIndex].totalSteps = data.total_steps;
          this.trainingJobs[jobIndex].stepProgress = data.step_progress;
        }
        
        // Update epoch information if available
        if (data.epoch && data.total_epochs) {
          this.trainingJobs[jobIndex].currentEpoch = data.epoch;
          this.trainingJobs[jobIndex].totalEpochs = data.total_epochs;
        }
        
        console.log(`📈 Updated job ${data.job_id}: ${data.message}`);
      }
    },
    
    async fetchAvailableDatasets() {
      try {
        console.log('Fetching available datasets for training...');
        
        // Fetch both global and user datasets
        const [globalResponse, userResponse] = await Promise.all([
          fetch(API_ENDPOINTS.v2.datasets),
          fetch(getUserApiUrl(this.authStore.user.id, 'datasets'))
        ]);
        
        const globalResult = await globalResponse.json();
        const userResult = await userResponse.json();
        
        let allDatasets = [];
        
        // Add global datasets
        if (globalResult.success) {
          const globalDatasets = globalResult.datasets.map(dataset => ({
            id: dataset.id.toString(),
            name: dataset.name,
            description: dataset.description,
            type: dataset.type,
            sampleCount: dataset.sample_count,
            createdAt: dataset.created_at,
            tags: dataset.tags || [],
            isFavorite: Boolean(dataset.is_favorite),
            lastModified: dataset.last_modified,
            size: dataset.size,
            format: dataset.format,
            license: dataset.license,
            datasetId: dataset.dataset_id,
            source: dataset.source,
            isGlobal: true,
            category: 'Global'
          }));
          allDatasets.push(...globalDatasets);
        }
        
        // Add user datasets
        if (userResult.success) {
          const userDatasets = userResult.datasets.map(dataset => ({
            id: dataset.id.toString(),
            name: dataset.name,
            description: dataset.description,
            type: dataset.type,
            sampleCount: dataset.sample_count,
            createdAt: dataset.created_at,
            tags: dataset.tags || [],
            isFavorite: Boolean(dataset.is_favorite),
            lastModified: dataset.last_modified,
            size: dataset.size,
            format: dataset.format,
            license: dataset.license,
            datasetId: dataset.dataset_id,
            source: dataset.source,
            isGlobal: false,
            category: 'My Datasets'
          }));
          allDatasets.push(...userDatasets);
        }
        
        this.availableDatasets = allDatasets;
        console.log(`Loaded ${allDatasets.length} datasets for training (${globalResult.datasets?.length || 0} global, ${userResult.datasets?.length || 0} user)`);
        
      } catch (error) {
        console.error('Error fetching datasets:', error);
        // Don't show error to user, just log it
      }
    },
    async fetchTrainingJobs() {
      try {
        console.log('Fetching training jobs from API...');
        const response = await fetch(API_ENDPOINTS.v2.trainingJobs);
        const result = await response.json();
        
        if (result.success) {
          // Transform database format to frontend format
          this.trainingJobs = result.jobs.map(job => ({
            id: job.id.toString(),
            jobName: job.name,
            description: job.description,
            jobType: job.job_type,
            maker: job.maker,
            version: job.version,
            modelName: job.model_name || job.base_model,
            baseModel: job.base_model,
            datasetName: this.getDatasetName(job.dataset_id),
            status: job.status,
            progress: Math.round(job.progress * 100), // Convert to percentage
            currentEpoch: Math.floor(job.progress * (job.config?.params?.epochs || 10)),
            totalEpochs: job.config?.params?.epochs || 10,
            elapsedTime: this.calculateElapsedTime(job.started_at),
            type: job.training_type,
            config: job.config || {},
            errorMessage: job.error_message || null,
            isStuck: this.isJobStuck(job)
          }));
          
          console.log(`Loaded ${this.trainingJobs.length} training jobs from API`);
          
          // Check for stuck jobs and auto-detect them only if there are jobs
          if (this.trainingJobs.length > 0) {
            await this.detectStuckJobs();
          }
        } else {
          console.error('Failed to fetch training jobs:', result.error);
          this.showErrorMessage(`Failed to fetch training jobs: ${result.error}`);
        }
      } catch (error) {
        console.error('Error fetching training jobs:', error);
        this.showErrorMessage(`Error fetching training jobs: ${error.message}`);
      }
    },
    
    showErrorMessage(message) {
      console.error(message);
      // You can implement toast notifications here
      alert(`Error: ${message}`);
    },

    showSuccessMessage(message) {
      console.log(message);
      // You can implement toast notifications here
      alert(`Success: ${message}`);
    },
    
    calculateElapsedTime(startedAt) {
      if (!startedAt) return 0;
      const start = new Date(startedAt);
      const now = new Date();
      return Math.floor((now - start) / (1000 * 60)); // minutes
    },
    
    isJobStuck(job) {
      if (job.status !== 'RUNNING') return false;
      
      const elapsedMinutes = this.calculateElapsedTime(job.started_at);
      const timeoutMinutes = job.training_type === 'LoRA' ? 30 : 10;
      
      return elapsedMinutes > timeoutMinutes && job.progress < 0.5;
    },
    
    async detectStuckJobs() {
      // Only detect stuck jobs if there are running jobs
      const runningJobs = this.trainingJobs.filter(job => job.status === 'RUNNING');
      if (runningJobs.length === 0) {
        return; // No running jobs, skip detection
      }
      
      try {
        console.log(`Detecting stuck training jobs (${runningJobs.length} running jobs)...`);
        const response = await fetch(getApiUrl('detect-stuck-training'), {
          method: 'POST'
        });
        
        if (!response.ok) {
          console.warn('Stuck jobs detection endpoint not available:', response.status);
          return;
        }
        
        const result = await response.json();
        
        if (result.success && result.stuck_jobs_found > 0) {
          console.log(`Detected ${result.stuck_jobs_found} stuck training jobs`);
          // Update local state instead of refetching to avoid loop
          // The next polling cycle will refresh the data naturally
        }
      } catch (error) {
        console.error('Error detecting stuck jobs:', error);
        // Don't show error to user, just log it
      }
    },
    async fetchOllamaModels() {
      try {
        console.log('Fetching Ollama models...');
        const response = await fetch(API_ENDPOINTS.v2.models);
        const result = await response.json();
        
        if (result.success) {
          this.ollamaModels = result.models;
          console.log(`Loaded ${this.ollamaModels.length} Ollama models`);
        } else {
          console.error('Failed to fetch Ollama models:', result.error);
          this.ollamaModels = [];
        }
      } catch (error) {
        console.error('Error fetching Ollama models:', error);
        this.ollamaModels = [];
        // Don't show error to user, just log it
      }
    },
    
    handleStatusChange(event) {
      console.log('🔄 Job status changed:', event);
      
      // Find and update the job in the training jobs list
      const jobIndex = this.trainingJobs.findIndex(job => job.id === event.jobId.toString());
      if (jobIndex !== -1) {
        this.trainingJobs[jobIndex].status = event.newStatus;
        this.trainingJobs[jobIndex].errorMessage = event.jobData?.error_message || null;
        
        // Update selected job if it matches
        if (this.selectedJob && this.selectedJob.id === event.jobId.toString()) {
          this.selectedJob.status = event.newStatus;
          this.selectedJob.errorMessage = event.jobData?.error_message || null;
        }
        
        // Show notification based on status
        if (event.newStatus === 'COMPLETED') {
          this.showSuccessMessage(`✅ Training completed for "${this.trainingJobs[jobIndex].jobName}"!`);
        } else if (event.newStatus === 'FAILED') {
          this.showError(`❌ Training failed for "${this.trainingJobs[jobIndex].jobName}"`);
        }
      }
    },
    
    getDatasetName(datasetId) {
      const dataset = this.availableDatasets.find(d => d.id === datasetId);
      return dataset ? dataset.name : 'Unknown Dataset';
    },
    getModelIcon(capabilities) {
      const capsArray = this.getCapabilitiesArray(capabilities);
      if (capsArray.includes('Coding') || capsArray.includes('Code Generation')) {
        return 'code';
      } else if (capsArray.includes('Reasoning') || capsArray.includes('Mathematics')) {
        return 'psychology';
      } else if (capsArray.includes('Visual Analysis')) {
        return 'visibility';
      } else if (capsArray.includes('Planning') || capsArray.includes('Task Management')) {
        return 'assignment';
      } else if (capsArray.includes('Conversation') || capsArray.includes('Instructions')) {
        return 'chat';
      } else {
        return 'smart_toy';
      }
    },
    getModelColor(capabilities) {
      const capsArray = this.getCapabilitiesArray(capabilities);
      if (capsArray.includes('Coding') || capsArray.includes('Code Generation')) {
        return 'success';
      } else if (capsArray.includes('Reasoning') || capsArray.includes('Mathematics')) {
        return 'info';
      } else if (capsArray.includes('Visual Analysis')) {
        return 'warning';
      } else if (capsArray.includes('Planning') || capsArray.includes('Task Management')) {
        return 'primary';
      } else if (capsArray.includes('Conversation') || capsArray.includes('Instructions')) {
        return 'secondary';
      } else {
        return 'light';
      }
    },
    getJobDisplayName(job) {
      // Show job name if it exists, otherwise show the original model name
      return job.jobName || job.modelName || job.baseModel || 'Unknown Job';
    },
    getModelDisplayOption(model) {
      const icon = this.getModelIcon(model.capabilities);
      const capsArray = this.getCapabilitiesArray(model.capabilities);
      const primaryCapability = capsArray[0] || 'General';
      const size = model.size;
      
      // Map icons to emojis for better display
      const iconMap = {
        'code': '💻',
        'psychology': '🧠',
        'visibility': '👁️',
        'assignment': '📋',
        'chat': '💬',
        'smart_toy': '🤖'
      };
      
      const emoji = iconMap[icon] || '🤖';
      return `${emoji} ${model.name} (${primaryCapability}) - ${size}`;
    },
    getModelDescription(capabilities) {
      const descriptions = {
        'Coding': 'Code generation, refactoring, and multi-language programming support',
        'Code Generation': 'Advanced code generation and syntax analysis',
        'Debugging': 'Code debugging, error analysis, and problem solving',
        'Reasoning': 'Mathematical reasoning, logical analysis, and complex problem solving',
        'Mathematics': 'Mathematical calculations and formula analysis',
        'Planning': 'Project planning, task management, and strategic coordination',
        'Visual Analysis': 'Code visualization, UI design, and visual documentation',
        'Conversation': 'Natural language conversation and interaction',
        'Instructions': 'Following complex instructions and task execution'
      };
      
      const capsArray = this.getCapabilitiesArray(capabilities);
      const primaryCapability = capsArray[0];
      return descriptions[primaryCapability] || 'General purpose AI model for various tasks';
    },
    getCapabilitiesArray(capabilities) {
      // Handle both string (JSON) and array formats
      if (!capabilities) return [];
      if (Array.isArray(capabilities)) return capabilities;
      if (typeof capabilities === 'string') {
        try {
          const parsed = JSON.parse(capabilities);
          return Array.isArray(parsed) ? parsed : [];
        } catch (e) {
          // If not valid JSON, treat as comma-separated string
          return capabilities.split(',').map(c => c.trim()).filter(c => c);
        }
      }
      return [];
    },
    getDatasetSamples(datasetId) {
      const dataset = this.availableDatasets.find(d => d.id === datasetId);
      return dataset ? dataset.sampleCount : 0;
    },
    removeDataset(datasetId) {
      this.newTraining.selectedDatasets = this.newTraining.selectedDatasets.filter(id => id !== datasetId);
    },
    showDatasetInfo(dataset) {
      // Show dataset details in a modal or alert
      alert(`Dataset: ${dataset.name}\n\n` +
            `Description: ${dataset.description}\n` +
            `Samples: ${dataset.sampleCount.toLocaleString()}\n` +
            `Type: ${dataset.type}\n` +
            `Format: ${dataset.format}\n` +
            `Size: ${dataset.size}\n` +
            `Source: ${dataset.source || 'Local'}`);
    },
    showSuccessMessage(message) {
      // Simple success message (you can enhance this with a toast notification)
      alert(`✅ ${message}`);
    },
    showError(message) {
      // Simple error message (you can enhance this with a toast notification)
      alert(`❌ ${message}`);
    },
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      this.uploadedFiles = [...this.uploadedFiles, ...files];
    },
    removeFile(file) {
      this.uploadedFiles = this.uploadedFiles.filter(f => f !== file);
    },
    handleAvatarUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }
      
      // Validate file type
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please select a valid image file (PNG, JPG, GIF, WEBP)');
        return;
      }
      
      // Store file and create preview
      this.newTraining.avatarFile = file;
      
      const reader = new FileReader();
      reader.onload = (e) => {
        this.newTraining.avatarPreview = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    removeAvatar() {
      this.newTraining.avatarFile = null;
      this.newTraining.avatarPreview = null;
      if (this.$refs.avatarInput) {
        this.$refs.avatarInput.value = '';
      }
    },
    async createTrainingJob() {
      try {
        // Process custom capabilities
        const customCapabilities = this.newTraining.customCapabilities
          ? this.newTraining.customCapabilities.split(',').map(cap => cap.trim()).filter(cap => cap)
          : [];

        // Prepare training job data
        const trainingData = {
          jobName: this.newTraining.jobName,
          description: this.newTraining.description,
          customCapabilities: customCapabilities,
          maker: this.newTraining.maker,
          version: this.newTraining.version,
          baseModel: this.newTraining.baseModel,
          training_type: this.newTraining.type,
          selectedDatasets: this.newTraining.selectedDatasets,
          trainingStrategy: this.newTraining.trainingStrategy,
          roleDefinition: this.newTraining.roleDefinition,
          temperature: this.newTraining.temperature,
          top_p: this.newTraining.top_p,
          context_length: this.newTraining.context_length,
          loraConfig: this.newTraining.loraConfig,
          params: this.newTraining.params,
          ragConfig: this.newTraining.ragConfig
        };

        // Call backend API to create training job
        let response;
        if (this.newTraining.avatarFile) {
          // Use FormData for avatar upload
          const formData = new FormData();
          formData.append('trainingData', JSON.stringify(trainingData));
          formData.append('avatar', this.newTraining.avatarFile);
          
          response = await fetch(API_ENDPOINTS.v2.trainingJobs, {
            method: 'POST',
            body: formData
          });
        } else {
          // Regular JSON request
          response = await fetch(API_ENDPOINTS.v2.trainingJobs, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(trainingData)
          });
        }

        const result = await response.json();

        if (result.success) {
          // Create frontend job object with backend data
          const newJob = {
            id: result.job_id,
            jobName: this.newTraining.jobName,
            description: this.newTraining.description,
            jobType: this.newTraining.jobType,
            maker: this.newTraining.maker,
            version: this.newTraining.version,
            modelName: result.model_name, // This is the actual model name that will be created
            baseModel: this.getModelDisplayName(this.newTraining.baseModel),
            datasetName: this.getDatasetName(),
            status: 'PENDING',
            progress: 0,
            currentEpoch: 0,
            totalEpochs: this.newTraining.params.epochs,
            elapsedTime: 0,
            type: this.newTraining.type,
            config: { ...this.newTraining }
          };
          
          this.trainingJobs.unshift(newJob);
          this.showTrainingModal = false;
          
          // Show success message with model name
          this.showSuccessMessage(`Training job "${this.newTraining.jobName}" created! Starting training...`);
          
          // Actually start the training by calling the start-training endpoint
          await this.startTraining(result.job_id);
          
          // Reset form
          this.resetTrainingForm();
        } else {
          this.showError(result.error || 'Failed to start training job');
        }
      } catch (error) {
        console.error('Error starting training:', error);
        this.showError('Failed to connect to server. Make sure the API server is running.');
      }
    },
    getModelDisplayName(modelId) {
      const modelNames = {
        'agimat:latest': 'agimat:latest',
        'claude-reasoning:latest': 'claude-reasoning:latest',
        'llava:13b': 'llava:13b',
        'qwen2.5-coder:7b': 'qwen2.5-coder:7b',
        'codellama:13b': 'codellama:13b',
        'llama3.1:8b': 'llama3.1:8b'
      };
      return modelNames[modelId] || modelId;
    },
    getDatasetName() {
      if (this.newTraining.type === 'rag') {
        return `${this.uploadedFiles.length} documents (RAG)`;
      }
      return this.newTraining.datasetType === 'upload' ? 'Custom JSONL Dataset' : 'Knowledge Base Dataset';
    },
    simulateTraining(jobId) {
      const job = this.trainingJobs.find(j => j.id === jobId);
      if (!job) return;
      
      const interval = setInterval(() => {
        if (job.progress >= 100) {
          job.status = 'COMPLETED';
          clearInterval(interval);
          return;
        }
        
        job.progress += Math.random() * 5;
        job.currentEpoch = Math.floor((job.progress / 100) * job.totalEpochs);
        job.elapsedTime += 30;
        
        if (job.progress >= 100) {
          job.progress = 100;
          job.currentEpoch = job.totalEpochs;
          job.status = 'COMPLETED';
          clearInterval(interval);
        }
      }, 2000);
    },
    resetTrainingForm() {
      this.newTraining = {
        type: 'lora',
        baseModel: '',
        datasetType: 'upload',
        roleDefinition: 'You are Agimat, an advanced AI assistant specialized in debugging and code analysis. You provide step-by-step guidance, identify issues, and offer practical solutions.',
        loraConfig: {
          rank: 8,
          alpha: 32,
          dropout: 0.05
        },
        params: {
          learningRate: 0.0002,
          batchSize: 4,
          epochs: 3,
          maxSteps: 2000
        },
        ragConfig: {
          chunkSize: 1000,
          topK: 4
        }
      };
      this.uploadedFiles = [];
    },
    formatDuration(seconds) {
      if (!seconds) return '--';
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      return h > 0 ? `${h}h ${m}m` : `${m}m`;
    },
    
    getCurrentTrainingJob() {
      // Return the first running job, or the most recent job
      const runningJob = this.trainingJobs.find(job => job.status === 'RUNNING');
      if (runningJob) return runningJob;
      
      return this.trainingJobs.length > 0 ? this.trainingJobs[this.trainingJobs.length - 1] : null;
    },
    startNewTraining() {
      this.showTrainingModal = true;
    },
    
    openExternalTrainingModal() {
      this.showExternalTrainingModal = true;
    },
    
    closeExternalTrainingModal() {
      this.showExternalTrainingModal = false;
      // Reset the training data
      this.newExternalTraining = {
        jobName: '',
        description: '',
        minionId: null,
        provider: '',
        model: '',
        type: 'rag',
        selectedDatasets: [],
        roleDefinition: '',
        temperature: 0.7,
        top_p: 0.9,
        max_tokens: 1024,
        ragConfig: {
          chunkSize: 1000,
          topK: 4
        }
      };
    },
    
    async createExternalTrainingJob(data) {
      try {
        if (!this.authStore.token || !this.authStore.user) {
          alert('Please log in to create training jobs');
          return;
        }
        
        // Check if data contains files (from ExternalTrainingModal with file uploads)
        const hasFiles = data.files && Array.isArray(data.files) && data.files.length > 0;
        const trainingData = hasFiles ? data.trainingData : data;
        
        let response;
        
        if (hasFiles) {
          // Use FormData when files are present
          const formData = new FormData();
          formData.append('trainingData', JSON.stringify(trainingData));
          
          // Append each file
          data.files.forEach((file, index) => {
            formData.append(`file_${index}`, file);
          });
          formData.append('fileCount', data.files.length.toString());
          
          response = await fetch(getUserApiUrl(this.authStore.user.id, 'external-training/jobs'), {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${this.authStore.token}`
              // Don't set Content-Type header - browser will set it with boundary for FormData
            },
            body: formData
          });
        } else {
          // Regular JSON request
          response = await fetch(getUserApiUrl(this.authStore.user.id, 'external-training/jobs'), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${this.authStore.token}`
            },
            body: JSON.stringify(trainingData)
          });
        }
        
        const result = await response.json();
        
        if (result.success) {
          // this.showSuccessMessage(`External training job "${trainingData.jobName}" created!`);
          await this.fetchExternalTrainingJobs();
          // Refresh minions to show the new pending job
          await this.refreshMinions();
        } else {
          this.showError(result.error || 'Failed to create external training job');
        }
      } catch (error) {
        console.error('Error creating external training job:', error);
        this.showError('Failed to connect to server. Make sure the API server is running.');
      }
    },
    
    async refreshMinions() {
      console.log('🔄 Refreshing minions data...')
      // Call fetchMinions on the MinionTrainingSection component
      if (this.$refs.minionTrainingSection) {
        await this.$refs.minionTrainingSection.fetchMinions()
      }
    },
    
    async fetchExternalTrainingJobs() {
      try {
        if (!this.authStore.token || !this.authStore.user) {
          console.log('❌ No auth token or user found');
          return;
        }
        
        console.log('🔍 Fetching external training jobs for user ID:', this.authStore.user.id);
        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'external-training/jobs'), {
          headers: {
            'Authorization': `Bearer ${this.authStore.token}`
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          console.log('📊 External training jobs API response:', result);
          this.externalTrainingJobs = result.jobs.map(job => ({
            id: job.id.toString(),
            jobName: job.job_name,
            description: job.description,
            minionId: job.minion_id,
            minionName: job.minion_name,
            provider: job.provider,
            modelName: job.model_name,
            trainingType: job.training_type,
            status: job.status,
            progress: Math.round(job.progress * 100),
            errorMessage: job.error_message || null,
            createdAt: job.created_at,
            startedAt: job.started_at,
            completedAt: job.completed_at
          }));
          console.log('📊 Mapped external training jobs:', this.externalTrainingJobs);
        } else {
          console.error('❌ Failed to fetch external training jobs:', result.error);
        }
      } catch (error) {
        console.error('Error fetching external training jobs:', error);
      }
    },
    
    async fetchAvailableMinions() {
      try {
        if (!this.authStore.token || !this.authStore.user) {
          return;
        }
        
        console.log('🔍 Fetching available minions for user ID:', this.authStore.user.id);
        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'minions'), {
          headers: {
            'Authorization': `Bearer ${this.authStore.token}`
          }
        });
        
        if (!response.ok) {
          console.warn('Available minions endpoint not available:', response.status);
          this.availableMinions = [];
          return;
        }
        
        const result = await response.json();
        
        if (result.success) {
          this.availableMinions = result.minions.map(minion => ({
            id: minion.id,
            display_name: minion.display_name,
            provider: minion.provider,
            description: minion.description,
            system_prompt: minion.system_prompt
          }));
          console.log(`Loaded ${this.availableMinions.length} available minions`);
        } else {
          console.error('Failed to fetch available minions:', result.error);
          this.showErrorMessage(`Failed to fetch available minions: ${result.error}`);
          this.availableMinions = [];
        }
      } catch (error) {
        console.error('Error fetching available minions:', error);
        this.showErrorMessage(`Error fetching available minions: ${error.message}`);
        this.availableMinions = [];
      }
    },
    viewJobDetails(job) {
      // In a real app, this would show detailed job info
      alert(`Viewing details for job: ${job.modelName}`);
    },
    
    viewExternalJobDetails(job) {
      // In a real app, this would show detailed job info
      alert(`Viewing details for external training job: ${job.jobName}`);
    },
    
    viewMinionHistory(job) {
      this.selectedMinionForHistory = {
        id: job.minionId,
        name: job.minionName
      };
      this.showMinionHistory = true;
    },
    
    closeMinionHistory() {
      this.showMinionHistory = false;
      this.selectedMinionForHistory = null;
    },
    
    async startExternalTraining(jobId) {
      try {
        if (!this.authStore.token || !this.authStore.user) {
          alert('Please log in to start training');
          return;
        }
        
        console.log('🚀 Starting external training for job:', jobId);
        console.log('👤 User:', this.authStore.user);
        console.log('🔑 Token:', this.authStore.token ? `${this.authStore.token.substring(0, 20)}...` : 'No token');
        
        const response = await fetch(getUserApiUrl(this.authStore.user.id, `external-training/jobs/${jobId}/start`), {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.authStore.token}`
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          this.showSuccessMessage('External training started!');
          await this.fetchExternalTrainingJobs();
          // Restart status polling since we now have a running job
          this.startStatusPolling();
        } else {
          this.showError(result.error || 'Failed to start external training');
        }
      } catch (error) {
        console.error('Error starting external training:', error);
        this.showError('Failed to connect to server. Make sure the API server is running.');
      }
    },
    
    async stopExternalTraining(jobId) {
      try {
        if (!this.authStore.token || !this.authStore.user) {
          alert('Please log in to stop training');
          return;
        }
        
        const response = await fetch(`${getUserApiUrl(this.authStore.user.id, 'external-training/jobs')}/${jobId}/stop`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.authStore.token}`
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          this.showSuccessMessage('External training stopped!');
          await this.fetchExternalTrainingJobs();
        } else {
          this.showError(result.error || 'Failed to stop external training');
        }
      } catch (error) {
        console.error('Error stopping external training:', error);
        this.showError('Failed to connect to server. Make sure the API server is running.');
      }
    },
    
    async deleteExternalJob(jobId) {
      if (!confirm('Are you sure you want to delete this external training job?')) {
        return;
      }
      
      try {
        if (!this.authStore.token || !this.authStore.user) {
          alert('Please log in to delete training jobs');
          return;
        }
        
        const response = await fetch(`${getUserApiUrl(this.authStore.user.id, 'external-training/jobs')}/${jobId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${this.authStore.token}`
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          this.showSuccessMessage('External training job deleted!');
          await this.fetchExternalTrainingJobs();
        } else {
          this.showError(result.error || 'Failed to delete external training job');
        }
      } catch (error) {
        console.error('Error deleting external training job:', error);
        this.showError('Failed to connect to server. Make sure the API server is running.');
      }
    },
    
    async stopTraining(jobId) {
      try {
      if (confirm('Stop this training job?')) {
          console.log(`🛑 Stopping training for job ${jobId}`);
          
          const response = await fetch(`${API_ENDPOINTS.v2.trainingJobs}/${jobId}/stop`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          });
          
          const result = await response.json();
          
          if (result.success) {
            this.showSuccessMessage(`Training stopped for job ${jobId}`);
            
            // Update job status locally
            const job = this.trainingJobs.find(j => j.id === jobId.toString());
            if (job) {
              job.status = 'STOPPED';
            }
            
            // Stop progress polling
            this.stopProgressPolling(jobId);
            
          } else {
            this.showError(result.error || 'Failed to stop training');
          }
        }
      } catch (error) {
        console.error('Error stopping training:', error);
        this.showError('Failed to connect to server.');
      }
    },
    
    startProgressPolling(jobId) {
      // Poll for progress updates every 5 seconds
      const pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`${API_ENDPOINTS.v2.trainingJobs}/${jobId}/status`);
          const result = await response.json();
          
          if (result.success) {
            const status = result.status;
            const job = this.trainingJobs.find(j => j.id === jobId.toString());
            
            if (job && status.running) {
              // Job is still running, update progress
              job.status = 'RUNNING';
              // Note: Progress updates will come from the training executor
            } else if (job && !status.running) {
              // Job completed or stopped
              job.status = status.status;
              if (status.status === 'COMPLETED') {
                this.showSuccessMessage(`Training completed for job ${jobId}!`);
                // Refresh the jobs list to get updated data
                await this.fetchTrainingJobs();
              }
              this.stopProgressPolling(jobId);
            }
          }
        } catch (error) {
          console.error('Error polling training status:', error);
        }
      }, 5000);
      
      // Store interval ID for cleanup
      this.progressPollingIntervals = this.progressPollingIntervals || {};
      this.progressPollingIntervals[jobId] = pollInterval;
    },
    
    stopProgressPolling(jobId) {
      if (this.progressPollingIntervals && this.progressPollingIntervals[jobId]) {
        clearInterval(this.progressPollingIntervals[jobId]);
        delete this.progressPollingIntervals[jobId];
      }
    },
    
    stopJob(jobId) {
      // Legacy method - redirect to new stopTraining
      this.stopTraining(jobId);
    },
    async deleteJob(jobId) {
      // Find the job to get its details for confirmation
        const job = this.trainingJobs.find(j => j.id === jobId);
      if (!job) return;
      
      // Show confirmation modal with job details
      const confirmed = confirm(
        `Are you sure you want to delete this training job?\n\n` +
        `Job: ${job.jobName}\n` +
        `Type: ${job.type}\n` +
        `Status: ${job.status}\n` +
        `Model: ${job.modelName}\n\n` +
        `This action cannot be undone and will also delete:\n` +
        `- The training job record\n` +
        `- Associated ChromaDB collection (if RAG)\n` +
        `- Generated model files (if completed)`
      );
      
      if (!confirmed) return;
      
      try {
        // Delete from backend
        const response = await fetch(`${API_ENDPOINTS.v2.trainingJobs}/${jobId}`, {
          method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Remove from frontend array
          this.trainingJobs = this.trainingJobs.filter(j => j.id !== jobId);
          
          // Show success message with cleanup details
          console.log(`✅ Successfully deleted training job: ${job.jobName}`);
          console.log('🧹 Cleanup results:', result.cleanup_results);
          
          // Show cleanup results to user
          const cleanupMessage = result.cleanup_results && result.cleanup_results.length > 0 
            ? `\n\nCleanup completed:\n${result.cleanup_results.join('\n')}`
            : '';
          
          alert(`✅ Training job "${job.jobName}" deleted successfully!${cleanupMessage}`);
          
          // Refresh data to ensure consistency
          await this.fetchTrainingJobs();
          await this.fetchChromaDBCollections();
          
        } else {
          console.error('Failed to delete training job:', result.error);
          alert(`Failed to delete training job: ${result.error}`);
        }
        
      } catch (error) {
        console.error('Error deleting training job:', error);
        alert(`Error deleting training job: ${error.message}`);
      }
    },
    
    async fetchOllamaModels() {
      try {
        const response = await fetch(API_ENDPOINTS.v2.models);
        const result = await response.json();
        
        if (result.success) {
          // Filter to only show Ollama models (not database minions)
          this.ollamaModels = result.models
            .filter(model => model.type === 'ollama')
            .map(model => ({
              name: model.name,
              capabilities: model.capabilities || []
            }));
          console.log('Loaded Ollama models:', this.ollamaModels.length);
        } else {
          console.error('Failed to fetch Ollama models:', result.error);
          this.showErrorMessage(`Failed to fetch Ollama models: ${result.error}`);
        }
      } catch (error) {
        console.error('Error fetching Ollama models:', error);
        this.showErrorMessage(`Error fetching Ollama models: ${error.message}`);
      }
    },
    
    async fetchChromaDBCollections() {
      try {
        console.log('ChromaDB collections endpoint not implemented yet');
        this.chromadbCollections = 0;
        console.log('ChromaDB collections set to 0 (endpoint not available)');
      } catch (error) {
        console.error('Error fetching ChromaDB collections:', error);
        this.chromadbCollections = 0;
      }
    }
  },
  
  beforeUnmount() {
    // Clean up any polling intervals
    this.stopStatusPolling();
    
    // Clean up progress polling intervals
    if (this.progressPollingIntervals) {
      Object.keys(this.progressPollingIntervals).forEach(jobId => {
        if (this.progressPollingIntervals[jobId]) {
          clearInterval(this.progressPollingIntervals[jobId]);
        }
      });
      this.progressPollingIntervals = {};
    }
  },
  
  async mounted() {
    console.log('🚀 Training component mounted');
    console.log('🔍 Auth store state:', {
      user: this.authStore.user,
      token: this.authStore.token ? 'Token exists' : 'No token',
      isAuthenticated: this.authStore.isAuthenticated
    });
    
    // Load available datasets, training jobs, and Ollama models when component mounts
    await this.fetchAvailableDatasets();
    await this.fetchTrainingJobs();
    await this.fetchOllamaModels();
    await this.fetchChromaDBCollections();
    
    // Load external training data
    await this.fetchExternalTrainingJobs();
    await this.fetchAvailableMinions();
    
    // Initialize status polling instead of Socket.IO
    this.initializeSocket();
    this.startStatusPolling();
    
    console.log('✅ Training component initialization complete');
  }
};
</script>

<style scoped>
.training-container {
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
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

/* Capabilities Overview */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(var(--primary-rgb), 0.1);
}

.card-content h3 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.card-content p {
  margin: 0.25rem 0 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.capabilities-overview {
  margin-bottom: 2rem;
}

.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.capability-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
  transition: transform 0.3s ease;
}

.capability-card:hover {
  transform: translateY(-3px);
}

.capability-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.capability-card h3 {
  margin: 0 0 0.75rem;
  font-size: 1.2rem;
  color: var(--text-color);
}

.capability-card p {
  margin: 0 0 1rem;
  color: var(--secondary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.capability-models {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.model-tag {
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.model-info {
  display: flex;
  justify-content: space-between;
  margin: 0.75rem 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.model-size {
  background: rgba(var(--success-rgb), 0.1);
  color: var(--success-color);
  padding: 0.2rem 0.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

.model-modified {
  color: var(--text-secondary);
  font-style: italic;
}

.no-models-message {
  color: var(--text-secondary);
  font-style: italic;
  margin-top: 0.5rem;
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.job-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
  transition: transform 0.3s ease;
}

.job-card:hover {
  transform: translateY(-3px);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.job-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 1rem;
  border-radius: 6px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  font-size: 0.9rem;
  font-weight: 500;
}

.job-progress.error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.job-progress.success {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon, .success-icon {
  font-size: 1rem;
}

.job-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-color);
}

.job-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.job-status.running {
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary);
}

.job-status.completed {
  background: rgba(28, 200, 138, 0.1);
  color: var(--success);
}

.job-status.failed {
  background: rgba(231, 74, 59, 0.1);
  color: var(--danger);
}

.job-status.stopped {
  background: rgba(246, 194, 62, 0.1);
  color: var(--warning);
}

.job-details {
  margin-bottom: 1rem;
}

.job-description {
  margin: 0 0 0.75rem;
  color: var(--text-color);
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
}

.job-capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.capability-tag {
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dataset-info {
  margin: 0 0 1rem;
  color: var(--secondary);
  font-size: 0.85rem;
  font-style: italic;
}

.job-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(78, 115, 223, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.metric-label {
  font-size: 0.7rem;
  color: var(--secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--primary);
}


.job-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--secondary);
}

.job-actions {
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

.btn-start {
  color: #28a745;
}

.btn-start:hover {
  color: #1e7e34;
}

.btn-stop {
  color: #dc3545;
}

.btn-stop:hover {
  color: #c82333;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: var(--card-bg);
  border-radius: 12px;
  width: 100%;
  /* max-width: 800px; */
  /* max-height: 90vh; */
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow);
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
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Avatar Upload */
.avatar-upload {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  padding: 1.5rem;
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  background: var(--card-bg);
  transition: all 0.3s ease;
}

.avatar-upload:hover {
  border-color: var(--primary-color);
  background: var(--hover-bg);
}

.avatar-preview {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-avatar {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--danger-color);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
}

.avatar-input {
  display: none;
}

.avatar-upload-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.avatar-upload-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
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
.lora-config,
.training-params,
.rag-config {
  background: rgba(78, 115, 223, 0.02);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1rem 0;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.lora-config h3,
.training-params h3,
.rag-config h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1.1rem;
}

.config-grid,
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

/* Dataset Options */
.dataset-options {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.dataset-option {
  flex: 1;
}

.option-card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.dataset-option input:checked + .option-card {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
}

.option-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

/* File Upload */
.file-upload {
  margin-top: 0.5rem;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--card-bg);
  border: 2px dashed rgba(78, 115, 223, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-color);
}

.upload-btn:hover {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
}

#file-upload {
  display: none;
}

.uploaded-files {
  margin-top: 1rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.file-item .btn-icon {
  width: 24px;
  height: 24px;
  font-size: 0.8rem;
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

/* Responsive */
@media (max-width: 768px) {
  .capabilities-grid {
    grid-template-columns: 1fr;
  }
  
  .training-types {
    grid-template-columns: 1fr;
  }
  
  .config-grid,
  .params-grid {
    grid-template-columns: 1fr;
  }
  
  .dataset-options {
    flex-direction: column;
  }
  
  .modal {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
  
  .job-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Dataset Options Styling */
.dataset-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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

.dataset-actions {
  margin-left: auto;
}

.info-icon {
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.info-icon:hover {
  opacity: 1;
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

.training-strategy {
  margin-top: 1rem;
}

.training-strategy label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.training-strategy small {
  display: block;
  margin-top: 0.25rem;
  color: var(--text-muted);
  font-style: italic;
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

/* Job Metadata Display */
.job-metadata {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(78, 115, 223, 0.1);
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
  min-width: 80px;
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

/* Job Badges */
.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.job-badges {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.job-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.job-badge.local {
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary);
  border: 1px solid rgba(78, 115, 223, 0.2);
}

.job-badge.external {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
  border: 1px solid rgba(40, 167, 69, 0.2);
}
</style>
