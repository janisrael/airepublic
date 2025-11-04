<template>
  <div v-if="isVisible" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" :class="modalClass" @click.stop>
      <div class="modal-header" v-if="showHeader">
        <h3 v-if="title">{{ title }}</h3>
        <slot name="header"></slot>
        <button v-if="showCloseButton" class="modal-close" @click="close">
          <span class="material-icons-round">close</span>
        </button>
      </div>
      
      <div class="modal-body">
        <slot></slot>
      </div>
      
      <div class="modal-footer" v-if="showFooter">
        <slot name="footer"></slot>
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
      default: ''
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
      default: false
    },
    showCloseButton: {
      type: Boolean,
      default: true
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    },
    closeOnEscape: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close', 'update:visible'],
  computed: {
    isVisible: {
      get() {
        return this.visible
      },
      set(value) {
        this.$emit('update:visible', value)
      }
    },
    modalClass() {
      return {
        [`modal-${this.size}`]: true
      }
    }
  },
  methods: {
    close() {
      this.isVisible = false
      this.$emit('close')
    },
    handleOverlayClick() {
      if (this.closeOnOverlay) {
        this.close()
      }
    },
    handleEscapeKey(event) {
      if (event.key === 'Escape' && this.closeOnEscape) {
        this.close()
      }
    }
  },
  mounted() {
    if (this.closeOnEscape) {
      document.addEventListener('keydown', this.handleEscapeKey)
    }
  },
  beforeUnmount() {
    if (this.closeOnEscape) {
      document.removeEventListener('keydown', this.handleEscapeKey)
    }
  }
}
</script>

<style scoped>
/* Modal Overlay */
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
  backdrop-filter: blur(4px);
}

/* Modal Content */
.modal-content {
  background: #efefef;
  border-radius: 20px;
  box-shadow: 
    20px 20px 40px var(--neumorphic-shadow-dark),
    -20px -20px 40px var(--neumorphic-shadow-light);
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  
  flex-direction: column;
  animation: modalSlideIn 0.3s ease-out;
}

/* Modal Sizes */
.modal-small {
  max-width: 400px;
  width: 100%;
}

.modal-medium {
  max-width: 600px;
  width: 100%;
}

.modal-large {
  max-width: 1200px;
  width: 100%;
}

.modal-fullscreen {
  max-width: 95vw;
  width: 95vw;
  max-height: 95vh;
  height: 95vh;
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: var(--neumorphic-bg);
  color: var(--text-primary);
  box-shadow: 
    inset 2px 2px 4px var(--neumorphic-shadow-dark),
    inset -2px -2px 4px var(--neumorphic-shadow-light);
}

/* Modal Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

/* Modal Footer */
.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Animation */
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 0.5rem;
  }
  
  .modal-content {
    border-radius: 16px;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 1rem 1.5rem;
  }
  
  .modal-header h3 {
    font-size: 1.25rem;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .modal-footer {
    padding: 1rem 1.5rem;
    flex-direction: column;
  }
  
  .modal-footer > * {
    width: 100%;
  }
  
  .modal-large,
  .modal-fullscreen {
    max-width: 100vw;
    width: 100vw;
    max-height: 100vh;
    height: 100vh;
    border-radius: 0;
  }
}
</style>
