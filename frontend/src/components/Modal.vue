<template>
  <div v-if="visible" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" :class="modalSize" @click.stop>
      <div class="modal-header" v-if="showHeader">
        <h2 class="modal-title">{{ title }}</h2>
        <button class="modal-close" @click="closeModal" v-if="showCloseButton">
          <span class="material-icons-round">close</span>
        </button>
      </div>
      
      <div class="modal-content">
        <slot></slot>
      </div>
      
      <div class="modal-footer" v-if="showFooter">
        <slot name="footer">
          <button class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" @click="confirmAction" :disabled="loading">
            {{ confirmText }}
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Modal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Modal'
    },
    size: {
      type: String,
      default: 'medium', // small, medium, large, fullscreen
      validator: (value) => ['small', 'medium', 'large', 'fullscreen'].includes(value)
    },
    showHeader: {
      type: Boolean,
      default: true
    },
    showFooter: {
      type: Boolean,
      default: true
    },
    showCloseButton: {
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
    closeOnEscape: {
      type: Boolean,
      default: true
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close', 'confirm'],
  computed: {
    modalSize() {
      return `modal-${this.size}`
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
    },
    handleEscapeKey(event) {
      if (event.key === 'Escape' && this.visible) {
        this.closeModal()
      }
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
  },
  mounted() {
    if (this.closeOnEscape) {
      document.addEventListener('keydown', this.handleEscapeKey)
    }
  },
  beforeUnmount() {
    document.body.style.overflow = ''
    document.removeEventListener('keydown', this.handleEscapeKey)
  }
}
</script>

<style scoped>
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
  backdrop-filter: blur(4px);
}

.modal-container {
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

.modal-small {
  width: 400px;
  max-width: 90vw;
}

.modal-medium {
  width: 600px;
  max-width: 90vw;
}

.modal-large {
  width: 800px;
  max-width: 90vw;
}

.modal-fullscreen {
  width: 95vw;
  height: 95vh;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.modal-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
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

.modal-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.modal-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  color: var(--text-primary);
}

.modal-footer {
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
  .modal-container {
    margin: 16px;
    max-height: calc(100vh - 32px);
  }
  
  .modal-header,
  .modal-content,
  .modal-footer {
    padding: 16px 20px;
  }
  
  .modal-title {
    font-size: 1.25rem;
  }
}
</style>