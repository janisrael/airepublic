<template>
  <div 
    :class="['class-card', { locked: !canUnlock, selected: isSelected }]"
    @click="handleCardClick"
  >
    <!-- Selection Indicator -->
    <div v-if="isSelected" class="selection-indicator">
      <span class="material-icons">check_circle</span>
    </div>
    <!-- Class Header -->
    <div class="class-card-header">
      <div class="class-icon">
        <span class="material-icons">{{ getClassIcon(classDef.class_name) }}</span>
      </div>
      <div class="class-info">
        <h3 class="class-name">{{ classDef.display_name }}</h3>
        <p class="class-category">{{ classDef.category }}</p>
      </div>
      <div class="class-status">
        <span v-if="canUnlock" class="status-badge unlocked">
          <span class="material-icons">check_circle</span>
          Unlocked
        </span>
        <span v-else class="status-badge locked">
          <span class="material-icons">lock</span>
          {{ unlockRequirement }}
        </span>
      </div>
    </div>

    <!-- Class Description -->
    <div class="class-description">
      <p>{{ classDef.description }}</p>
    </div>

    <!-- Class Stats -->
    <div class="class-stats">
      <div class="stat-item">
        <span class="stat-label">Performance</span>
        <span class="stat-value performance">+{{ (classDef.net_performance_bonus * 100).toFixed(0) }}%</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Spirits</span>
        <span class="stat-value">{{ classDef.base_spirits.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Tools</span>
        <span class="stat-value">{{ classDef.tools_count }}+</span>
      </div>
    </div>

    <!-- Class Spirits Preview -->
    <div class="class-spirits-preview">
      <div class="spirits-label">Included Spirits:</div>
      <div class="spirits-list">
        <span 
          v-for="spirit in classDef.base_spirits.slice(0, 3)" 
          :key="spirit"
          class="spirit-tag"
        >
          {{ getSpiritName(spirit) }}
        </span>
        <span v-if="classDef.base_spirits.length > 3" class="spirit-tag more">
          +{{ classDef.base_spirits.length - 3 }} more
        </span>
      </div>
    </div>

    <!-- Class Actions -->
    <div class="class-actions">
      <button 
        v-if="canUnlock"
        @click.stop="selectClass"
        class="action-btn primary"
      >
        Install
      </button>
      <button 
        v-else
        @click.stop="viewDetails"
        class="action-btn secondary"
      >
        View Requirements
      </button>
      <button 
        @click.stop="viewDetails"
        class="action-btn secondary"
      >
        View Details
      </button>
    </div>

    <!-- Locked Overlay -->
    <div v-if="!canUnlock" class="locked-overlay">
      <span class="material-icons lock-icon">lock</span>
      <p>Requires {{ unlockRequirement }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ClassCard',
  props: {
    classDef: {
      type: Object,
      required: true
    },
    canUnlock: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      isSelected: false
    }
  },
  computed: {
    unlockRequirement() {
      if (this.classDef.unlock_rank !== 'Novice' || this.classDef.unlock_level > 1) {
        return `${this.classDef.unlock_rank} L${this.classDef.unlock_level}`
      }
      return 'Higher Rank'
    }
  },
  methods: {
    handleCardClick() {
      if (this.canUnlock) {
        this.selectClass()
      } else {
        this.viewDetails()
      }
    },

    selectClass() {
      console.log('ClassCard: Emitting select event:', this.classDef)
      this.$emit('select', this.classDef)
    },

    viewDetails() {
      this.$emit('view-details', this.classDef)
    },

    getSpiritName(spiritId) {
      // Map spirit IDs to names (this should ideally come from the API)
      const spiritNames = {
        1: 'Writer',
        2: 'Creative',
        3: 'Translator',
        4: 'Analyst',
        5: 'Researcher',
        6: 'Mathematician',
        7: 'Builder',
        8: 'Debugger',
        9: 'DevOps',
        10: 'Connector',
        11: 'Communicator',
        12: 'Scheduler',
        13: 'Checker',
        14: 'Security',
        15: 'Educator',
        16: 'Designer',
        17: 'Consultant',
        18: 'Healer'
      }
      return spiritNames[spiritId] || `Spirit ${spiritId}`
    },

    getClassIcon(className) {
      // Map class names to Material Icons
      const classIcons = {
        'Planner': 'psychology',
        'Developer': 'code',
        'Creative Assistant': 'palette',
        'Data Scientist': 'analytics',
        'API Integration Specialist': 'api',
        'Security Specialist': 'security',
        'Swiss Army Knife': 'build'
      }
      return classIcons[className] || 'psychology'
    }
  }
}
</script>

<style scoped>
.class-card {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.selection-indicator {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: var(--success);
  color: white;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.selection-indicator .material-icons {
  font-size: 1.25rem;
}

.class-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.class-card.selected {
  border-color: var(--primary);
  background: var(--primary-light);
}

.class-card.locked {
  opacity: 0.7;
  cursor: not-allowed;
}

.class-card.locked:hover {
  transform: none;
  border-color: var(--border-color);
}

.class-card-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}
.class-card {
    box-shadow: var(--shadow);
}

.class-card[is-selected="true"] {
    box-shadow: inset 2px 2px 5px #b8b9be, inset -3px -3px 7px #fff;
}
.class-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
  color: var(--primary);
}

.class-info {
  flex: 1;
}

.class-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.class-category {
  font-size: 0.9rem;
  color: var(--secondary);
  margin: 0;
}

.class-status {
  flex-shrink: 0;
  display: none;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge .material-icons {
  font-size: 1rem;
}

.status-badge.unlocked {
  background: var(--success-light);
  color: var(--success);
}

.status-badge.locked {
  background: var(--warning-light);
  color: var(--warning);
}

.class-description {
  margin-bottom: 1rem;
}

.class-description p {
  font-size: 0.95rem;
  color: var(--text-color);
  line-height: 1.5;
  margin: 0;
}

.class-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--secondary);
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
}

.stat-value.performance {
  color: var(--success);
}

.class-spirits-preview {
  margin-bottom: 1.5rem;
}

.spirits-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.spirits-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.spirit-tag {
  padding: 0.25rem 0.75rem;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.spirit-tag.more {
  background: var(--bg-secondary);
  color: var(--secondary);
}

.class-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: var(--primary);
  color: white;
}

.action-btn.primary:hover {
  background: var(--primary-dark);
}

.action-btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.action-btn.secondary:hover {
  background: var(--border-color);
}

.locked-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  border-radius: 16px;
}

.lock-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.locked-overlay p {
  margin: 0;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .class-card {
    padding: 1rem;
  }
  
  .class-card-header {
    gap: 0.75rem;
  }
  
  .class-icon {
    font-size: 2rem;
  }
  
  .class-name {
    font-size: 1.1rem;
  }
  
  .class-stats {
    gap: 0.5rem;
  }
  
  .class-actions {
    flex-direction: column;
  }
}
</style>
