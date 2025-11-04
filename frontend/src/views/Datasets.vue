<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1>Datasets</h1>
      <p>Manage your training datasets and data sources.</p>
    </div>

    <!-- Stats Cards -->
    <div class="dashboard-grid">
      <div class="neumorphic-card stats-card">
        <div class="stats-icon">
          <span class="material-icons-round">dataset</span>
        </div>
        <div class="stats-info">
          <h3>{{ stats.totalDatasets }}</h3>
          <p>Total Datasets</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon">
          <span class="material-icons-round">storage</span>
        </div>
        <div class="stats-info">
          <h3>{{ formatFileSize(stats.totalSize) }}</h3>
          <p>Total Size</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon">
          <span class="material-icons-round">data_usage</span>
        </div>
        <div class="stats-info">
          <h3>{{ formatNumber(stats.totalSamples) }}</h3>
          <p>Total Samples</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon">
          <span class="material-icons-round">trending_up</span>
        </div>
        <div class="stats-info">
          <h3>{{ stats.recentUploads }}</h3>
          <p>Recent Uploads</p>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="neumorphic-card quick-actions">
      <h3>Quick Actions</h3>
      <div class="actions-grid">
        <button class="action-btn" @click="showUploadModal = true" :disabled="uploading || isLoadingHF">
          <span class="material-icons-round icon-success">upload</span>
          <span>Upload Dataset</span>
        </button>
        <button class="action-btn" @click="showHuggingFaceModal = true" :disabled="uploading || isLoadingHF">
          <span class="material-icons-round icon-primary">hub</span>
          <span>Load from Hugging Face</span>
        </button>
        <button class="action-btn" @click="refreshDatasets">
          <span class="material-icons-round icon-info">refresh</span>
          <span>Refresh Datasets</span>
        </button>
        <button class="action-btn" @click="exportDatasets">
          <span class="material-icons-round icon-warning">download</span>
          <span>Export Dataset List</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="dashboard-row">
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <!-- Search and Filter Bar -->
          <div class="search-filter-bar">
            <div class="search-box">
              <span class="material-icons-round search-icon">search</span>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search datasets..."
                class="form-control search-input"
              />
            </div>
            <div class="filter-controls">
              <select v-model="selectedType" class="form-control filter-select">
                <option value="">All Types</option>
                <option value="Text">Text</option>
                <option value="Image">Image</option>
                <option value="Audio">Audio</option>
                <option value="Video">Video</option>
                <option value="Tabular">Tabular</option>
                <option value="Multimodal">Multimodal</option>
              </select>
              <select v-model="sortBy" class="form-control filter-select">
                <option value="name">Sort by Name</option>
                <option value="date">Sort by Date</option>
                <option value="size">Sort by Size</option>
                <option value="samples">Sort by Samples</option>
              </select>
              <button 
                @click="sortDescending = !sortDescending" 
                class="btn btn-sm btn-secondary sort-btn"
                :class="{ active: sortDescending }"
              >
                <span class="material-icons-round">{{ sortDescending ? 'arrow_downward' : 'arrow_upward' }}</span>
              </button>
            </div>
          </div>

          <!-- Dataset Grid -->
          <div class="dataset-grid" v-if="filteredDatasets.length > 0">
            <DatasetCard
              v-for="dataset in filteredDatasets"
              :key="dataset.id"
              :dataset="dataset"
              :loading="loadingDatasets.includes(dataset.id)"
              @view="viewDataset"
              @edit="editDataset"
              @delete="deleteDataset"
              @download="downloadDataset"
              @use="useDataset"
            />
          </div>

          <!-- Empty State -->
          <div v-if="filteredDatasets.length === 0 && !isLoading" class="empty-state">
            <div class="empty-state-icon">
              <span class="material-icons-round">dataset</span>
            </div>
            <h3>No datasets found</h3>
            <p v-if="searchQuery || selectedType">
              Try adjusting your search criteria or filters.
            </p>
            <p v-else>
              Get started by uploading your first dataset or loading one from Hugging Face.
            </p>
            <div class="empty-state-actions">
              <button class="btn btn-primary" @click="showUploadModal = true" :disabled="uploading || isLoadingHF">
                <span class="material-icons-round">upload</span>
                Upload Dataset
              </button>
              <button class="btn btn-secondary" @click="showHuggingFaceModal = true" :disabled="uploading || isLoadingHF">
                <span class="material-icons-round">hub</span>
                Load from Hugging Face
              </button>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="isLoading" class="loading-state">
            <Loader size="large" />
            <p>Loading datasets...</p>
          </div>

          <!-- Uploading State -->
          <div v-if="uploading" class="loading-state">
            <Loader size="large" />
            <p>Creating dataset...</p>
          </div>

          <!-- Hugging Face Loading State -->
          <div v-if="isLoadingHF" class="loading-state">
            <Loader size="large" />
            <p>Loading dataset from Hugging Face...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Dataset Upload Modal -->
    <DatasetModal
      :isVisible="showUploadModal"
      title="Upload Dataset"
      icon="upload"
      size="large"
      :loading="uploading"
      confirmText="Upload"
      @close="showUploadModal = false"
      @confirm="handleUpload"
    >
      <div class="upload-form">
        <div class="form-group">
          <label for="datasetName">Dataset Name</label>
          <input 
            id="datasetName"
            v-model="uploadForm.name" 
            type="text" 
            class="form-control"
            placeholder="Enter dataset name"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="datasetDescription">Description</label>
          <textarea 
            id="datasetDescription"
            v-model="uploadForm.description" 
            class="form-control"
            rows="3"
            placeholder="Describe your dataset"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="datasetType">Dataset Type</label>
          <select id="datasetType" v-model="uploadForm.type" class="form-control">
            <option value="text">Text</option>
            <option value="image">Image</option>
            <option value="audio">Audio</option>
            <option value="video">Video</option>
            <option value="tabular">Tabular</option>
            <option value="multimodal">Multimodal</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="datasetFile">Dataset File</label>
          <input 
            id="datasetFile"
            type="file" 
            @change="handleFileSelect"
            class="form-control"
            accept=".json,.csv,.txt,.zip"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="datasetTags">Tags (comma-separated)</label>
          <input 
            id="datasetTags"
            v-model="uploadForm.tags" 
            type="text" 
            class="form-control"
            placeholder="tag1, tag2, tag3"
          >
        </div>
      </div>
    </DatasetModal>

    <!-- Hugging Face Modal -->
    <DatasetModal
      :isVisible="showHuggingFaceModal"
      title="Load from Hugging Face"
      icon="hub"
      size="large"
      :loading="isLoadingHF"
      :showFooter="true"
      confirmText="Load Custom Dataset"
      @close="showHuggingFaceModal = false"
      @confirm="handleHuggingFaceLoad"
    >
      <div class="huggingface-form">
        <div class="hf-intro">
          <p>Load datasets directly from Hugging Face Datasets library. You can use any public dataset by providing its ID.</p>
          <div class="code-example">
            <code>from datasets import load_dataset<br>ds = load_dataset("your-dataset-id")</code>
          </div>
        </div>
        
        <!-- Popular Datasets -->
        <div class="popular-datasets">
          <h3>Popular Datasets</h3>
          <div class="dataset-grid">
            <div class="dataset-card" @click="loadSpecificDataset('sahil2801/CodeAlpaca-20k')">
              <div class="dataset-icon">
                <span class="material-icons-round">code</span>
              </div>
              <h4>CodeAlpaca-20k</h4>
              <p>20K code instruction-following examples</p>
              <span class="dataset-id">sahil2801/CodeAlpaca-20k</span>
            </div>
            <div class="dataset-card" @click="loadSpecificDataset('HuggingFaceH4/CodeAlpaca_20K')">
              <div class="dataset-icon">
                <span class="material-icons-round">terminal</span>
              </div>
              <h4>CodeAlpaca 20K</h4>
              <p>Python code generation dataset</p>
              <span class="dataset-id">HuggingFaceH4/CodeAlpaca_20K</span>
            </div>
            <div class="dataset-card" @click="loadSpecificDataset('iamtarun/python_code_instructions_18k_alpaca')">
              <div class="dataset-icon">
                <span class="material-icons-round">build</span>
              </div>
              <h4>Python Instructions</h4>
              <p>18K Python code instructions</p>
              <span class="dataset-id">iamtarun/python_code_instructions_18k_alpaca</span>
            </div>
            <div class="dataset-card" @click="loadSpecificDataset('code_x_glue_cc_defect_detection')">
              <div class="dataset-icon">
                <span class="material-icons-round">bug_report</span>
              </div>
              <h4>Defect Detection</h4>
              <p>Code bug detection dataset</p>
              <span class="dataset-id">code_x_glue_cc_defect_detection</span>
            </div>
            <div class="dataset-card" @click="loadSpecificDataset('openai_humaneval')">
              <div class="dataset-icon">
                <span class="material-icons-round">psychology</span>
              </div>
              <h4>HumanEval</h4>
              <p>Code evaluation problems</p>
              <span class="dataset-id">openai_humaneval</span>
            </div>
            <div class="dataset-card" @click="loadSpecificDataset('flytech/python-codes-25k')">
              <div class="dataset-icon">
                <span class="material-icons-round">flash_on</span>
              </div>
              <h4>Python Codes 25K</h4>
              <p>25K Python code examples</p>
              <span class="dataset-id">flytech/python-codes-25k</span>
            </div>
          </div>
        </div>
        
        <!-- Custom Dataset Input -->
        <div class="custom-dataset">
          <h3>Custom Dataset</h3>
          <div class="form-group">
            <label for="hfDatasetName">Dataset Name <span class="required">*</span></label>
            <input 
              id="hfDatasetName"
              v-model="hfForm.datasetName" 
              type="text" 
              class="form-control dataset-input"
              placeholder="e.g., My Custom Code Dataset"
              required
            >
            <small>Give your dataset a descriptive name</small>
          </div>
          
          <div class="form-group">
            <label for="hfDescription">Description</label>
            <textarea 
              id="hfDescription"
              v-model="hfForm.description" 
              class="form-control dataset-input"
              placeholder="Describe what this dataset contains and its purpose..."
              rows="3"
            ></textarea>
            <small>Optional description of the dataset content and use case</small>
          </div>
          
          <div class="form-group">
            <label for="hfDatasetId">Hugging Face Dataset ID <span class="required">*</span></label>
            <input 
              id="hfDatasetId"
              v-model="hfForm.datasetId" 
              type="text" 
              class="form-control dataset-input"
              placeholder="e.g., sahil2801/CodeAlpaca-20k"
              required
            >
            <small>Find datasets at <a href="https://huggingface.co/datasets" target="_blank">huggingface.co/datasets</a></small>
          </div>
          
          <div class="form-group">
            <label for="hfSplit">Split</label>
            <select id="hfSplit" v-model="hfForm.split" class="form-control">
              <option value="train">Train</option>
              <option value="validation">Validation</option>
              <option value="test">Test</option>
              <option value="all">All</option>
            </select>
          </div>
        </div>
      </div>
    </DatasetModal>

    <!-- Dataset Details Modal -->
    <DatasetModal
      :isVisible="showDetailsModal"
      :title="selectedDataset?.name || 'Dataset Details'"
      icon="info"
      size="large"
      :showFooter="false"
      @close="showDetailsModal = false"
    >
      <div v-if="selectedDataset" class="dataset-details">
        <div class="details-section">
          <h4>Overview</h4>
          <div class="details-grid">
            <div class="detail-item">
              <span class="detail-label">Type:</span>
              <span class="detail-value">{{ selectedDataset.type }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Samples:</span>
              <span class="detail-value">{{ selectedDataset.sample_count?.toLocaleString() || 'Unknown' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Size:</span>
              <span class="detail-value">{{ formatFileSize(selectedDataset.file_size) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Created:</span>
              <span class="detail-value">{{ formatDate(selectedDataset.created_at) }}</span>
            </div>
          </div>
        </div>
        
        <div class="details-section" v-if="selectedDataset.description">
          <h4>Description</h4>
          <p>{{ selectedDataset.description }}</p>
        </div>
        
        <div class="details-section" v-if="selectedDatasetTags && selectedDatasetTags.length">
          <h4>Tags</h4>
          <div class="tags-list">
            <span v-for="tag in selectedDatasetTags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </DatasetModal>

    <!-- Delete Confirmation Modal -->
    <DatasetModal
      :isVisible="showDeleteModal"
      title="Delete Dataset"
      icon="delete"
      size="small"
      :loading="loadingDatasets.includes(datasetToDelete?.id)"
      :showFooter="true"
      confirmText="Delete Dataset"
      @close="showDeleteModal = false"
      @confirm="confirmDeleteDataset"
    >
      <div class="delete-confirmation">
        <div class="delete-icon">
          <span class="material-icons-round">warning</span>
        </div>
        <h3>Are you sure?</h3>
        <p>This action cannot be undone. The dataset <strong>"{{ datasetToDelete?.name }}"</strong> will be permanently deleted.</p>
        <div class="delete-details" v-if="datasetToDelete">
          <div class="detail-item">
            <span class="material-icons-round">data_usage</span>
            <span>{{ formatNumber(datasetToDelete.sample_count || 0) }} samples</span>
          </div>
          <div class="detail-item" v-if="datasetToDelete.file_size">
            <span class="material-icons-round">storage</span>
            <span>{{ formatFileSize(datasetToDelete.file_size) }}</span>
          </div>
        </div>
      </div>
    </DatasetModal>
  </div>
</template>

<script>
import DatasetCard from '../components/DatasetCard.vue'
import DatasetModal from '../components/DatasetModal.vue'
import Loader from '../components/Loader.vue'
import { API_ENDPOINTS } from '@/config/api'

export default {
  name: 'Datasets',
  components: {
    DatasetCard,
    DatasetModal,
    Loader
  },
  data() {
    return {
      // Search and filters
      searchQuery: '',
      selectedType: '',
      sortBy: 'name',
      sortDescending: false,
      
      // Modals
      showUploadModal: false,
      showHuggingFaceModal: false,
      showDetailsModal: false,
      showDeleteModal: false,
      
      // Loading states
      isLoading: false,
      isLoadingHF: false,
      uploading: false,
      loadingDatasets: [],
      
      // Forms
      uploadForm: {
        name: '',
        description: '',
        type: 'text',
        file: null,
        tags: ''
      },
      hfForm: {
        datasetName: '',
        description: '',
        datasetId: '',
        split: 'train'
      },
      
      // Data
      datasets: [],
      selectedDataset: null,
      datasetToDelete: null,
      
      // Stats
      stats: {
        totalDatasets: 0,
        totalSize: 0,
        totalSamples: 0,
        recentUploads: 0
      },
      
      // Dataset types
      datasetTypes: ['Text', 'Image', 'Audio', 'Video', 'Tabular', 'Multimodal']
    }
  },
  computed: {
    filteredDatasets() {
      // Create a copy to avoid mutating the original array
      let filtered = [...this.datasets]
      
      // Filter by search query
      if (this.searchQuery && this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase().trim()
        filtered = filtered.filter(dataset => {
          try {
            const tags = this.parseDatasetTags(dataset.tags)
            return dataset.name.toLowerCase().includes(query) ||
              (dataset.description && dataset.description.toLowerCase().includes(query)) ||
              tags.some(tag => tag.toLowerCase().includes(query))
          } catch (error) {
            console.warn('Error parsing tags for dataset:', dataset.name, error)
            return dataset.name.toLowerCase().includes(query) ||
              (dataset.description && dataset.description.toLowerCase().includes(query))
          }
        })
      }
      
      // Filter by type
      if (this.selectedType) {
        filtered = filtered.filter(dataset => dataset.type === this.selectedType)
      }
      
      // Sort
      filtered.sort((a, b) => {
        let aVal, bVal
        
        switch (this.sortBy) {
          case 'name':
            aVal = a.name.toLowerCase()
            bVal = b.name.toLowerCase()
            break
          case 'date':
            aVal = new Date(a.created_at || 0)
            bVal = new Date(b.created_at || 0)
            break
          case 'size':
            aVal = a.file_size || 0
            bVal = b.file_size || 0
            break
          case 'samples':
            aVal = a.sample_count || 0
            bVal = b.sample_count || 0
            break
          default:
            aVal = a.name.toLowerCase()
            bVal = b.name.toLowerCase()
        }
        
        if (this.sortDescending) {
          return bVal > aVal ? 1 : -1
        } else {
          return aVal > bVal ? 1 : -1
        }
      })
      
      return filtered
    },
    
    selectedDatasetTags() {
      if (!this.selectedDataset?.tags) return []
      
      // If tags is already an array, return it
      if (Array.isArray(this.selectedDataset.tags)) {
        return this.selectedDataset.tags
      }
      
      // If tags is a string, try to parse it as JSON
      if (typeof this.selectedDataset.tags === 'string') {
        try {
          const parsed = JSON.parse(this.selectedDataset.tags)
          return Array.isArray(parsed) ? parsed : []
        } catch (e) {
          // If parsing fails, treat as a single tag
          return [this.selectedDataset.tags]
        }
      }
      
      return []
    }
  },
  async mounted() {
    await this.loadDatasets()
  },
  methods: {
    async loadDatasets() {
      this.isLoading = true
      try {
        console.log('Loading datasets from API...')
        const response = await fetch(API_ENDPOINTS.v2.datasets)
        console.log('API Response status:', response.status)
        if (response.ok) {
          const result = await response.json()
          console.log('API Response data:', result)
          this.datasets = result.datasets || []
          console.log('Datasets loaded:', this.datasets.length)
          this.updateStats()
        } else {
          console.error('API Error:', response.status, response.statusText)
        }
      } catch (error) {
        console.error('Error loading datasets:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    updateStats() {
      try {
        this.stats.totalDatasets = this.datasets.length
        this.stats.totalSize = this.datasets.reduce((sum, dataset) => sum + (dataset.file_size || 0), 0)
        this.stats.totalSamples = this.datasets.reduce((sum, dataset) => sum + (dataset.sample_count || 0), 0)
        
        // Count recent uploads (last 7 days)
        const weekAgo = new Date()
        weekAgo.setDate(weekAgo.getDate() - 7)
        this.stats.recentUploads = this.datasets.filter(dataset => {
          try {
            return dataset.created_at && new Date(dataset.created_at) > weekAgo
          } catch (e) {
            return false
          }
        }).length
      } catch (error) {
        console.warn('Error updating stats:', error)
        // Set default values to prevent undefined states
        this.stats.totalDatasets = 0
        this.stats.totalSize = 0
        this.stats.totalSamples = 0
        this.stats.recentUploads = 0
      }
    },
    
    viewDataset(dataset) {
      this.selectedDataset = dataset
      this.showDetailsModal = true
    },
    
    editDataset(dataset) {
      // TODO: Implement edit functionality
      console.log('Edit dataset:', dataset)
    },
    
    deleteDataset(dataset) {
      this.datasetToDelete = dataset
      this.showDeleteModal = true
    },
    
    async confirmDeleteDataset() {
      if (!this.datasetToDelete) return
      
      const dataset = this.datasetToDelete
      this.loadingDatasets.push(dataset.id)
      
      try {
        const response = await fetch(`${API_ENDPOINTS.v2.datasets}/${dataset.id}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          // Remove from local datasets array immediately for better UX
          this.datasets = this.datasets.filter(d => d.id !== dataset.id)
          this.updateStats()
          
          // Close modal and reset
          this.showDeleteModal = false
          this.datasetToDelete = null
          
          console.log(`Dataset "${dataset.name}" deleted successfully`)
        } else {
          const errorData = await response.json().catch(() => ({}))
          console.error('Error deleting dataset:', errorData.error || 'Unknown error')
          alert(`Failed to delete dataset: ${errorData.error || 'Unknown error'}`)
        }
      } catch (error) {
        console.error('Error deleting dataset:', error)
        alert(`Failed to delete dataset: ${error.message}`)
      } finally {
        this.loadingDatasets = this.loadingDatasets.filter(id => id !== dataset.id)
      }
    },
    
    downloadDataset(dataset) {
      // TODO: Implement download functionality
      console.log('Download dataset:', dataset)
    },
    
    useDataset(dataset) {
      // TODO: Implement use functionality
      console.log('Use dataset:', dataset)
    },
    
    handleFileSelect(event) {
      this.uploadForm.file = event.target.files[0]
    },
    
    async handleUpload() {
      if (!this.uploadForm.name || !this.uploadForm.file) {
        alert('Please fill in all required fields')
        return
      }
      
      this.uploading = true
      try {
        const formData = new FormData()
        formData.append('name', this.uploadForm.name)
        formData.append('description', this.uploadForm.description)
        formData.append('type', this.uploadForm.type)
        formData.append('file', this.uploadForm.file)
        formData.append('tags', this.uploadForm.tags)
        
        const response = await fetch(API_ENDPOINTS.v2.datasets, {
          method: 'POST',
          body: formData
        })
        
        if (response.ok) {
          this.showUploadModal = false
          this.resetUploadForm()
          await this.loadDatasets()
        }
      } catch (error) {
        console.error('Error uploading dataset:', error)
      } finally {
        this.uploading = false
      }
    },
    
    async handleHuggingFaceLoad() {
      if (!this.hfForm.datasetName || !this.hfForm.datasetId) {
        alert('Please enter both dataset name and Hugging Face dataset ID')
        return
      }
      
      this.isLoadingHF = true
      try {
        const response = await fetch(API_ENDPOINTS.v2.loadDataset, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            dataset_id: this.hfForm.datasetId,
            custom_name: this.hfForm.datasetName,
            custom_description: this.hfForm.description,
            split: this.hfForm.split
          })
        })
        
        if (response.ok) {
          this.showHuggingFaceModal = false
          this.resetHuggingFaceForm()
          await this.loadDatasets()
        }
      } catch (error) {
        console.error('Error loading from Hugging Face:', error)
      } finally {
        this.isLoadingHF = false
      }
    },
    
    async loadSpecificDataset(datasetId) {
      if (!datasetId || !datasetId.trim()) {
        alert('Please provide a valid dataset ID')
        return
      }
      
      this.isLoadingHF = true
      this.showHuggingFaceModal = false
      
      try {
        console.log(`Loading dataset: ${datasetId}`)
        
        const response = await fetch(API_ENDPOINTS.v2.loadDataset, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ dataset_id: datasetId })
        })
        
        const result = await response.json()
        
        if (result.success) {
          // Show success message
          const dataset = result.dataset
          const successMessage = `Successfully loaded "${dataset.name}"!\n\n` +
            `📊 Samples: ${dataset.sample_count.toLocaleString()}\n` +
            `⭐ Quality Score: ${dataset.quality_score}%\n` +
            `📋 Format: ${dataset.format}\n` +
            `🏷️ Tags: ${dataset.tags}`
          
          alert(successMessage)
          
          // Refresh the datasets list
          await this.loadDatasets()
        } else {
          alert(`Failed to load dataset: ${result.error || 'Unknown error'}`)
        }
      } catch (error) {
        console.error('Error loading dataset:', error)
        alert('Failed to load dataset. Please check the dataset ID and try again.')
      } finally {
        this.isLoadingHF = false
      }
    },
    
    resetUploadForm() {
      this.uploadForm = {
        name: '',
        description: '',
        type: 'text',
        file: null,
        tags: ''
      }
    },
    
    resetHuggingFaceForm() {
      this.hfForm = {
        datasetName: '',
        description: '',
        datasetId: '',
        split: 'train'
      }
    },
    
    formatFileSize(bytes) {
      if (!bytes) return '0 Bytes'
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    },
    
    formatNumber(num) {
      if (!num) return '0'
      return num.toLocaleString()
    },

    refreshDatasets() {
      this.loadDatasets()
    },

    exportDatasets() {
      // Create CSV content
      const headers = ['Name', 'Type', 'Samples', 'Size', 'Created', 'Status']
      const csvContent = [
        headers.join(','),
        ...this.datasets.map(dataset => [
          `"${dataset.name}"`,
          dataset.type || 'Unknown',
          dataset.sample_count || 0,
          dataset.file_size ? this.formatFileSize(dataset.file_size) : '0 B',
          new Date(dataset.created_at).toLocaleDateString(),
          dataset.processing_status || 'Unknown'
        ].join(','))
      ].join('\n')

      // Create and download file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `datasets_export_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    
    parseDatasetTags(tags) {
      if (!tags) return []
      
      // If tags is already an array, return a copy to avoid mutations
      if (Array.isArray(tags)) {
        return [...tags]
      }
      
      // If tags is a string, try to parse it as JSON
      if (typeof tags === 'string') {
        try {
          const parsed = JSON.parse(tags)
          return Array.isArray(parsed) ? [...parsed] : [tags]
        } catch (e) {
          // If parsing fails, treat as a single tag
          return [tags]
        }
      }
      
      return []
    }
  }
}
</script>

<style scoped>
@import '@/assets/scss/neumorphism.scss';

:root {
  --primary-color: #4e73df;
  --success-color: #1cc88a;
  --info-color: #36b9cc;
  --warning-color: #f6c23e;
  --danger-color: #e74a3b;
  --light-color: #f8f9fc;
  --dark-color: #5a5c69;
}

.dashboard-container {
  padding: 1.5rem;
  margin: 0 auto;
  font-family: 'Roboto', sans-serif;
}

.material-icons-round {
  font-family: 'Material Icons Round';
  font-weight: normal;
  font-style: normal;
  font-size: 1.5rem;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  vertical-align: middle;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.page-header p {
  color: var(--secondary);
  margin: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stats-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  transition: transform 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.5rem;
  font-size: 1.8rem;
  background: linear-gradient(145deg, #caced3, #f0f5fd);
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
}

.stats-icon.training {
  color: #f6c23e;
}

.stats-icon.dataset {
  color: #1cc88a;
}

.stats-icon.accuracy {
  color: #4e73df;
}

.stats-info h3 {
  font-size: 1.8rem;
  margin: 0 0 0.25rem;
  color: var(--text-color);
}

.stats-info p {
  margin: 0;
  color: var(--secondary);
  font-size: 0.9rem;
}

.datasets-header-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.search-filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  padding: 16px;
  margin-bottom: 16px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 48px;
  border: none;
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 1rem;
  font-family: 'Roboto', sans-serif;
}

.search-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--primary-color);
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.filters,
.filter-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-btn {
  padding: 12px 16px;
  border: none;
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-family: 'Roboto', sans-serif;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 50px;
}

.sort-btn:hover {
  background: var(--primary-color);
  color: white;
}

.sort-btn.active {
  background: var(--primary-color);
  color: white;
}

.filter-select {
  padding: 12px 16px;
  border: none;
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-family: 'Roboto', sans-serif;
  cursor: pointer;
  min-width: 140px;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: var(--primary-color);
  color: white;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  font-family: 'Roboto', sans-serif;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--text-secondary);
  color: var(--bg-primary);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

.datasets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.empty-state {
  text-align: center;
  padding: 64px 32px;
  color: var(--text-secondary);
}

.empty-state-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  color: var(--text-secondary);
}

.empty-state h3 {
  font-size: 1.5rem;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.empty-state p {
  font-size: 1rem;
  margin: 0 0 24px 0;
}

.empty-state-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.loading-state {
  text-align: center;
  padding: 64px 32px;
  color: var(--text-secondary);
}

.loading-state p {
  margin-top: 16px;
  font-size: 1rem;
}

.upload-form,
.huggingface-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hf-intro {
  margin-bottom: 2rem;
}

.hf-intro p {
  margin-bottom: 1rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.code-example {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  margin-bottom: 1rem;
}

.code-example code {
  color: #d63384;
  font-size: 0.9rem;
}

.popular-datasets {
  margin-bottom: 2rem;
}

.popular-datasets h3 {
  margin-bottom: 1rem;
  color: var(--text-primary);
  font-size: 1.2rem;
}

.dataset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.dataset-grid .dataset-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
}

.dataset-grid .dataset-card:hover {
  transform: translateY(-5px);
  box-shadow: 8px 8px 16px var(--shadow-dark), 
              -8px -8px 16px var(--shadow-light);
}

.dataset-grid .dataset-card .dataset-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 15px;
  background: linear-gradient(145deg, #caced3, #f0f5fd);
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
  margin: 0 auto 1rem;
}

.dataset-grid .dataset-card .dataset-icon .material-icons-round {
  font-size: 2rem;
  color: var(--primary-color);
}

/* Delete Confirmation Modal Styles */
.delete-confirmation {
  text-align: center;
  padding: 2rem 1rem;
}

.delete-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.delete-icon .material-icons-round {
  font-size: 4rem;
  color: #f44336;
  background: linear-gradient(145deg, #ffebee, #ffcdd2);
  border-radius: 50%;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
}

.delete-confirmation h3 {
  margin: 0 0 1rem;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
}

.delete-confirmation p {
  margin: 0 0 2rem;
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.5;
}

.delete-confirmation strong {
  color: var(--text-primary);
  font-weight: 600;
}

.delete-details {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 12px;
  box-shadow: inset 2px 2px 4px var(--shadow-dark), 
              inset -2px -2px 4px var(--shadow-light);
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.detail-item .material-icons-round {
  font-size: 1.2rem;
  color: var(--primary-color);
}

/* Quick Actions Styles */
.quick-actions {
  margin-bottom: 2rem;
  padding: 1.5rem;
}

.quick-actions h3 {
  margin: 0 0 1.5rem;
  font-size: 1.25rem;
  color: var(--text-color);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 8px 8px 15px var(--shadow-dark), 
              -8px -8px 15px var(--shadow-light);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-btn .material-icons-round {
  font-size: 1.2rem;
}

.action-btn .icon-primary {
  color: var(--primary-color);
}

.action-btn .icon-success {
  color: var(--success-color);
}

.action-btn .icon-info {
  color: var(--info-color);
}

.action-btn .icon-warning {
  color: var(--warning-color);
}

.dataset-grid .dataset-card h4 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.dataset-grid .dataset-card p {
  margin: 0 0 1rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.dataset-id {
  display: inline-block;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.custom-dataset {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.custom-dataset h3 {
  margin-bottom: 1rem;
  color: var(--text-primary);
  font-size: 1.2rem;
}

.required {
  color: #e74c3c;
  font-weight: bold;
}

.dataset-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
  margin-bottom: 0.5rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.dataset-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
}

.dataset-input[required] {
  border-left: 4px solid #e74c3c;
}

.custom-dataset small {
  display: block;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.custom-dataset small a {
  color: var(--primary-color);
  text-decoration: none;
}

.custom-dataset small a:hover {
  text-decoration: underline;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: var(--text-primary);
}

.form-control {
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 1rem;
  font-family: 'Roboto', sans-serif;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.2);
}

.dataset-details {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.details-section h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-value {
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 600;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .dashboard-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .datasets-header-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    justify-content: space-between;
  }
  
  .datasets-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .empty-state-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>