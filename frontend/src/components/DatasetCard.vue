<template>
  <div class="neumorphic-card dataset-card" :class="{ 'loading': loading }">
    <div v-if="loading" class="dataset-card-loading">
      <Loader size="medium" />
      <p>Processing...</p>
    </div>
    <div class="card-header">
      <div class="dataset-icon" :class="datasetTypeClass">
        <span class="material-icons-round">{{ datasetIcon }}</span>
      </div>
      <div class="dataset-actions">
        <button class="btn-icon" @click="viewDataset" :title="'View ' + dataset.name">
          <span class="material-icons-round">visibility</span>
        </button>
        <button class="btn-icon danger" @click="deleteDataset" :title="'Delete ' + dataset.name">
          <span class="material-icons-round">delete</span>
        </button>
      </div>
    </div>
    
    <div class="card-content">
      <h3 class="dataset-name">{{ dataset.name }}</h3>
      <p class="dataset-description">{{ dataset.description || 'No description available' }}</p>
      
      <div class="dataset-stats">
        <div class="stat-item">
          <div class="stat-icon">
            <span class="material-icons-round">data_usage</span>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatNumber(dataset.sample_count || 0) }}</span>
            <span class="stat-label">Samples</span>
          </div>
        </div>
        
        <div class="stat-item" v-if="dataset.file_size">
          <div class="stat-icon">
            <span class="material-icons-round">storage</span>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatFileSize(dataset.file_size) }}</span>
            <span class="stat-label">Size</span>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon">
            <span class="material-icons-round">schedule</span>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatDate(dataset.created_at) }}</span>
            <span class="stat-label">Created</span>
          </div>
        </div>
      </div>
      
      <div class="dataset-tags" v-if="parsedTags && parsedTags.length">
        <span 
          v-for="tag in parsedTags.slice(0, 3)" 
          :key="tag" 
          class="dataset-tag"
        >
          {{ tag }}
        </span>
        <span v-if="parsedTags.length > 3" class="dataset-tag more">
          +{{ parsedTags.length - 3 }} more
        </span>
      </div>
    </div>
    
    <div class="card-footer">
      <div class="dataset-status">
        <span class="status-indicator" :class="statusClass"></span>
        <span class="status-text">{{ statusText }}</span>
      </div>
      
      <div class="dataset-actions-footer">
        <button class="btn btn-sm btn-secondary" @click="downloadDataset" :disabled="loading">
          <span class="material-icons-round">download</span>
          Download
        </button>
        <button class="btn btn-sm btn-primary" @click="useDataset" :disabled="loading">
          <span class="material-icons-round">play_arrow</span>
          Use Dataset
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Loader from './Loader.vue'

export default {
  name: 'DatasetCard',
  components: {
    Loader
  },
  props: {
    dataset: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['view', 'edit', 'delete', 'download', 'use'],
  computed: {
    datasetIcon() {
      const type = this.dataset.type?.toLowerCase() || ''
      
      // Map dataset types to appropriate icons
      const iconMap = {
        'text': 'article',
        'image': 'image',
        'audio': 'audiotrack',
        'video': 'video_library',
        'tabular': 'table_chart',
        'multimodal': 'view_module',
        'nlp': 'translate',
        'computer_vision': 'camera_alt',
        'speech': 'record_voice_over',
        'recommendation': 'recommend',
        'time_series': 'timeline',
        'graph': 'account_tree',
        'default': 'dataset'
      }
      
      return iconMap[type] || iconMap['default']
    },
    
    datasetTypeClass() {
      const type = this.dataset.type?.toLowerCase() || 'default'
      return `type-${type}`
    },
    
    statusClass() {
      const status = this.dataset.processing_status?.toLowerCase() || 'unknown'
      return `status-${status}`
    },
    
    statusText() {
      const status = this.dataset.processing_status?.toLowerCase() || 'unknown'
      const statusMap = {
        'completed': 'Ready',
        'processing': 'Processing',
        'error': 'Error',
        'uploading': 'Uploading',
        'pending': 'Pending',
        'unknown': 'Unknown'
      }
      return statusMap[status] || 'Unknown'
    },
    
    parsedTags() {
      if (!this.dataset.tags) return []
      
      // If tags is already an array, return it
      if (Array.isArray(this.dataset.tags)) {
        return this.dataset.tags
      }
      
      // If tags is a string, try to parse it as JSON
      if (typeof this.dataset.tags === 'string') {
        try {
          const parsed = JSON.parse(this.dataset.tags)
          return Array.isArray(parsed) ? parsed : []
        } catch (e) {
          // If parsing fails, treat as a single tag
          return [this.dataset.tags]
        }
      }
      
      return []
    }
  },
  methods: {
    viewDataset() {
      this.$emit('view', this.dataset)
    },
    
    editDataset() {
      this.$emit('edit', this.dataset)
    },
    
    deleteDataset() {
      this.$emit('delete', this.dataset)
    },
    
    downloadDataset() {
      this.$emit('download', this.dataset)
    },
    
    useDataset() {
      this.$emit('use', this.dataset)
    },
    
    formatNumber(num) {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toString()
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    
    formatFileSize(bytes) {
      if (!bytes) return 'Unknown'
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
      if (bytes === 0) return '0 Bytes'
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }
  }
}
</script>

<style scoped>
@import '@/assets/scss/neumorphism.scss';

.dataset-card {
  background: var(--card-bg);
  position: relative;
}

.dataset-card.loading {
  opacity: 0.7;
  pointer-events: none;
}

.dataset-card-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  z-index: 10;
  border-radius: 16px;
}

.dataset-card-loading p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.dataset-card:hover {
  transform: translateY(-5px);
  box-shadow: 8px 8px 16px var(--shadow-dark), 
              -8px -8px 16px var(--shadow-light);
}


.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.dataset-icon {
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

.dataset-icon.type-text {
  color: #1cc88a;
}

.dataset-icon.type-image {
  color: #f6c23e;
}

.dataset-icon.type-audio {
  color: #36b9cc;
}

.dataset-icon.type-video {
  color: #e74a3b;
}

.dataset-icon.type-tabular {
  color: #4e73df;
}

.dataset-icon.type-multimodal {
  color: #5a5c69;
}

.dataset-icon.type-nlp {
  color: #795548;
}

.dataset-icon.type-computer_vision {
  color: #e74a3b;
}

.dataset-icon.type-speech {
  color: #4e73df;
}

.dataset-icon.type-recommendation {
  color: #36b9cc;
}

.dataset-icon.type-time_series {
  color: #1cc88a;
}

.dataset-icon.type-graph {
  color: #f6c23e;
}

.dataset-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 16px;
}

.btn-icon:hover {
  background: var(--primary-color);
  color: white;
  transform: scale(1.05);
}

.btn-icon.danger:hover {
  background: #F44336;
}

.card-content {
  flex: 1;
  margin-bottom: 16px;
}

.dataset-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
  line-height: 1.3;
}

.dataset-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 16px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dataset-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
}

.meta-icon {
  font-size: 16px;
  color: var(--text-secondary);
  width: 16px;
}

.meta-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.meta-value {
  color: var(--text-primary);
  font-weight: 600;
}

/* Dataset Stats */
.dataset-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: var(--bg-secondary);
  box-shadow: inset 2px 2px 4px var(--shadow-dark), 
              inset -2px -2px 4px var(--shadow-light);
}

.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, #caced3, #f0f5fd);
  box-shadow: 2px 2px 4px var(--shadow-dark), 
              -2px -2px 4px var(--shadow-light);
}

.stat-icon .material-icons-round {
  font-size: 1rem;
  color: var(--primary-color);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  line-height: 1;
}

.dataset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.dataset-tag {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.dataset-tag.more {
  background: var(--primary-color);
  color: white;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.dataset-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.status-completed {
  background: #4CAF50;
}

.status-indicator.status-processing {
  background: #FF9800;
  animation: pulse 2s infinite;
}

.status-indicator.status-error {
  background: #F44336;
}

.status-indicator.status-uploading {
  background: #2196F3;
  animation: pulse 2s infinite;
}

.status-indicator.status-pending {
  background: #9C27B0;
  animation: pulse 2s infinite;
}

.status-indicator.status-unknown {
  background: var(--text-secondary);
}

.status-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.dataset-actions-footer {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  font-family: 'Roboto', sans-serif;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}

.btn-secondary {
  background: var(--bg-tertiary);
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

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .dataset-card {
    padding: 16px;
  }
  
  .dataset-actions {
    gap: 4px;
  }
  
  .btn-icon {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
  
  .dataset-actions-footer {
    flex-direction: column;
    gap: 6px;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

