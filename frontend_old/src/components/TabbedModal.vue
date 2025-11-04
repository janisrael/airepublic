<template>
  <Modal
    :visible="visible"
    :title="title"
    :size="size"
    :show-header="showHeader"
    :show-footer="showFooter"
    :show-close-button="showCloseButton"
    :close-on-overlay="closeOnOverlay"
    :close-on-escape="closeOnEscape"
    @close="$emit('close')"
  >
    <template #header v-if="showHeader">
      <slot name="header"></slot>
    </template>
    
    <!-- Tabs Navigation -->
    <div class="tabbed-modal-tabs" v-if="tabs.length > 0">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-button"
        :class="{ 'active': activeTab === tab.id, 'disabled': tab.disabled }"
        @click="selectTab(tab.id)"
        :disabled="tab.disabled"
      >
        <span v-if="tab.icon" class="material-icons-round">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>
    
    <!-- Tab Content -->
    <div class="tabbed-modal-content">
      <slot :activeTab="activeTab"></slot>
    </div>
    
    <template #footer v-if="showFooter">
      <slot name="footer"></slot>
    </template>
  </Modal>
</template>

<script>
import Modal from './Modal.vue'

export default {
  name: 'TabbedModal',
  components: {
    Modal
  },
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
      default: 'large'
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
    },
    tabs: {
      type: Array,
      default: () => []
    },
    defaultTab: {
      type: String,
      default: ''
    }
  },
  emits: ['close', 'tab-change'],
  data() {
    return {
      activeTab: this.defaultTab || (this.tabs.length > 0 ? this.tabs[0].id : '')
    }
  },
  watch: {
    tabs: {
      handler(newTabs) {
        if (newTabs.length > 0 && !this.activeTab) {
          this.activeTab = newTabs[0].id
        }
      },
      immediate: true
    },
    defaultTab(newTab) {
      if (newTab) {
        this.activeTab = newTab
      }
    }
  },
  methods: {
    selectTab(tabId) {
      if (this.activeTab !== tabId) {
        this.activeTab = tabId
        this.$emit('tab-change', tabId)
      }
    }
  }
}
</script>

<style scoped>
.tabbed-modal-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
  padding: 0 2rem;
  margin: 0 -2rem 2rem -2rem;
  padding-left: 2rem;
  padding-right: 2rem;
}

.tab-button {
  background: none;
  border: none;
  padding: 1rem 1.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  position: relative;
}

.tab-button:hover:not(.disabled) {
  background: var(--neumorphic-bg);
  color: var(--text-primary);
}

.tab-button.active {
  background: var(--primary-color);
  /* color: white; */
  box-shadow: rgba(50, 50, 93, 0.25) 0px 30px 50px -12px inset, rgba(0, 0, 0, 0.3) 0px 18px 26px -18px inset;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary-color);
}

.tab-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.form-control {
    box-shadow: var(--shadow-sm);
    background-color: light-dark(rgb(232, 240, 254), rgba(70, 90, 126, 0.4)) !important;
}
.tabbed-modal-content {
  min-height: 300px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .tabbed-modal-tabs {
    flex-wrap: wrap;
    gap: 0.25rem;
    padding: 0 1.5rem;
    margin: 0 -1.5rem 1.5rem -1.5rem;
  }
  
  .tab-button {
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
  }
}
</style>
