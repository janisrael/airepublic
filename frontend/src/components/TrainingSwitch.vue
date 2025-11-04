<template>
  <div class="training-switch">
    <div class="switch-container">
      <button 
        class="switch-option" 
        :class="{ active: activeTab === 'local' }"
        @click="setActiveTab('local')"
      >
        <span class="material-icons-round">computer</span>
        <span>Local Training</span>
      </button>
      <button 
        class="switch-option" 
        :class="{ active: activeTab === 'external' }"
        @click="setActiveTab('external')"
      >
        <span class="material-icons-round">smart_toy</span>
        <span>Minion Refinement</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingSwitch',
  props: {
    modelValue: {
      type: String,
      default: 'external'
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      activeTab: this.modelValue
    }
  },
  watch: {
    modelValue(newVal) {
      this.activeTab = newVal
    }
  },
  methods: {
    setActiveTab(tab) {
      this.activeTab = tab
      this.$emit('update:modelValue', tab)
    }
  }
}
</script>

<style scoped>
.training-switch {
  margin-bottom: 2rem;
}

.switch-container {
  display: flex;
  background: var(--card-bg);
  border-radius: var(--radius);
  padding: 4px;
  box-shadow: var(--shadow);
}

.switch-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-muted);
}

.switch-option:hover {
  background: var(--card-bg);
  color: var(--text-color);
  box-shadow: var(--shadow-sm);
}

.switch-option.active {
  background: var(--primary);
  color: white;
  box-shadow: 3px 3px 6px rgba(78, 115, 223, 0.2), 
              -3px -3px 6px rgba(122, 159, 245, 0.4);
}

.switch-option .material-icons-round {
  font-size: 1.2rem;
}
</style>
