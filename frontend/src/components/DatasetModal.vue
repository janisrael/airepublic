<template>
  <div v-if="isVisible" class="dataset-modal-overlay" @click="handleOverlayClick">
    <div class="dataset-modal-container" :class="modalSize" @click.stop>
      <div class="dataset-modal-header">
        <h2 class="dataset-modal-title">
          <span class="material-icons-round dataset-modal-icon" v-if="icon">{{ icon }}</span>
          {{ title }}
        </h2>
        <button class="dataset-modal-close" @click="closeModal">
          <span class="material-icons-round">close</span>
        </button>
      </div>
      
      <div class="dataset-modal-content" :class="{ 'loading': loading }">
        <div v-if="loading" class="dataset-modal-loading">
          <Loader size="large" />
          <p>Loading dataset...</p>
        </div>
        <slot v-else></slot>
      </div>
      
      <div class="dataset-modal-footer" v-if="showFooter">
        <slot name="footer">
          <button class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" @click="confirmAction" :disabled="loading">
            <Loader v-if="loading" size="small" />
            <span v-else>{{ confirmText }}</span>
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script>
import Loader from './Loader.vue'

export default {
  name: 'DatasetModal',
  components: {
    Loader
  },
  props: {
    isVisible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Dataset Modal'
    },
    icon: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'medium', // small, medium, large, fullscreen
      validator: (value) => ['small', 'medium', 'large', 'fullscreen'].includes(value)
    },
    showFooter: {
      type: Boolean,
      default: true
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    loading: {
      type: Boolean,
      default: false
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close', 'confirm'],
  computed: {
    modalSize() {
      return `dataset-modal-${this.size}`
    }
  },
  methods: {
    closeModal() {
      this.$emit('close')
    },
    confirmAction() {
      this.$emit('confirm')
    },
    handleOverlayClick() {
      if (this.closeOnOverlay) {
        this.closeModal()
      }
    }
  },
  watch: {
    isVisible(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
  },
  beforeUnmount() {
    document.body.style.overflow = ''
  }
}
</script>

<style scoped>
.dataset-modal-overlay {
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
  backdrop-filter: blur(4px);
}

.dataset-modal-container {
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: 
    20px 20px 60px rgba(0, 0, 0, 0.1),
    -20px -20px 60px rgba(255, 255, 255, 0.1);
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  font-family: 'Roboto Slab', sans-serif;
}

.dataset-modal-small {
  width: 400px;
  max-width: 90vw;
}

.dataset-modal-medium {
  width: 600px;
  max-width: 90vw;
}

.dataset-modal-large {
  width: 800px;
  max-width: 90vw;
  background-color: #ffffff;
}

.dataset-modal-fullscreen {
  width: 95vw;
  height: 95vh;
}

.dataset-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.dataset-modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.dataset-modal-icon {
  color: var(--primary-color);
  font-size: 1.5rem;
}

.dataset-modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dataset-modal-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.dataset-modal-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  color: var(--text-primary);
  position: relative;
}

.dataset-modal-content.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.dataset-modal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  text-align: center;
}

.dataset-modal-loading p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.dataset-modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  padding: 24px 32px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

/* Responsive design */
@media (max-width: 768px) {
  .dataset-modal-container {
    margin: 16px;
    max-height: calc(100vh - 32px);
  }
  
  .dataset-modal-header,
  .dataset-modal-content,
  .dataset-modal-footer {
    padding: 16px 20px;
  }
  
  .dataset-modal-title {
    font-size: 1.25rem;
  }
}
</style>
