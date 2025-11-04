<template>
  <Modal 
    :visible="showModal" 
    title="⚠️ Duplicate Training Detected"
    size="medium"
    :showFooter="true"
    :closeOnOverlay="false"
    :closeOnEscape="false"
    @close="handleCancel"
  >
    <div class="duplicate-warning">
      <div class="warning-icon">
        <span class="material-icons-round">warning</span>
      </div>
      
      <div class="warning-content">
        <h3>{{ warningMessage }}</h3>
        
        <div v-if="duplicateInfo" class="duplicate-details">
          <div class="detail-item">
            <strong>Previous Training:</strong>
            <span>{{ formatDate(duplicateInfo.created_at) }}</span>
          </div>
          <div class="detail-item">
            <strong>Collection:</strong>
            <span>{{ duplicateInfo.collection_name }}</span>
          </div>
          <div class="detail-item">
            <strong>XP Gained:</strong>
            <span>{{ duplicateInfo.xp_gained || 0 }}</span>
          </div>
          <div class="detail-item">
            <strong>Status:</strong>
            <span class="status-badge" :class="duplicateInfo.summary?.training_type?.toLowerCase()">
              {{ duplicateInfo.summary?.training_type || 'RAG' }}
            </span>
          </div>
        </div>
        
        <div class="recommendation">
          <h4>Recommended Action:</h4>
          <p>{{ getRecommendationText() }}</p>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="modal-footer-actions">
        <button 
          class="btn btn-secondary" 
          @click="handleCancel"
        >
          Cancel Training
        </button>
        
        <button 
          v-if="recommendation === 'overwrite'"
          class="btn btn-warning" 
          @click="handleOverwrite"
        >
          Overwrite Collection
        </button>
        
        <button 
          v-if="recommendation === 'create_new'"
          class="btn btn-primary" 
          @click="handleCreateNew"
        >
          Create New Collection
        </button>
        
        <button 
          class="btn btn-success" 
          @click="handleProceed"
        >
          Proceed Anyway
        </button>
      </div>
    </template>
  </Modal>
</template>

<script>
import Modal from './Modal.vue'

export default {
  name: 'DuplicateTrainingWarning',
  components: {
    Modal
  },
  props: {
    showModal: {
      type: Boolean,
      default: false
    },
    duplicateInfo: {
      type: Object,
      default: null
    },
    recommendation: {
      type: String,
      default: 'proceed'
    },
    warningMessage: {
      type: String,
      default: 'Duplicate training detected'
    }
  },
  emits: ['cancel', 'overwrite', 'create-new', 'proceed'],
  methods: {
    handleCancel() {
      this.$emit('cancel')
    },
    
    handleOverwrite() {
      this.$emit('overwrite')
    },
    
    handleCreateNew() {
      this.$emit('create-new')
    },
    
    handleProceed() {
      this.$emit('proceed')
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getRecommendationText() {
      switch (this.recommendation) {
        case 'overwrite':
          return 'Overwrite the existing collection with new data. This will replace all previous embeddings.'
        case 'create_new':
          return 'Create a new collection with a different name to avoid conflicts.'
        case 'proceed':
          return 'Proceed with training as this appears to be a legitimate update.'
        default:
          return 'Choose an action below to continue.'
      }
    }
  }
}
</script>

<style scoped>
.duplicate-warning {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.warning-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffc107;
}

.warning-icon .material-icons-round {
  font-size: 24px;
}

.warning-content {
  flex: 1;
}

.warning-content h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.duplicate-details {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item strong {
  color: #555;
  font-weight: 600;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.rag {
  background: rgba(78, 115, 223, 0.1);
  color: #4e73df;
}

.status-badge.lora {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.recommendation {
  background: rgba(78, 115, 223, 0.05);
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.recommendation h4 {
  margin: 0 0 0.5rem 0;
  color: #4e73df;
  font-size: 1rem;
}

.recommendation p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.modal-footer-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-warning:hover {
  background: #e0a800;
}

.btn-primary {
  background: #4e73df;
  color: white;
}

.btn-primary:hover {
  background: #375a7f;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

@media (max-width: 768px) {
  .duplicate-warning {
    flex-direction: column;
    text-align: center;
  }
  
  .modal-footer-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
