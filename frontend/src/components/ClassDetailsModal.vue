<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="class-details-modal" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="class-header">
          <div class="class-icon-large">
            <span class="material-icons">{{ getClassIcon(classDef.class_name) }}</span>
          </div>
          <div class="class-title">
            <h2>{{ classDef.display_name }} Class</h2>
            <p class="class-subtitle">{{ classDef.specialization }}</p>
          </div>
        </div>
        <button @click="closeModal" class="close-btn">×</button>
      </div>

      <!-- Modal Content -->
      <div class="modal-content">
        <!-- Class Description -->
        <div class="class-description-section">
          <h3>Description</h3>
          <p>{{ classDef.description }}</p>
        </div>

        <!-- Performance Stats -->
        <div class="performance-section">
          <div class="performance-card">
            <div class="performance-icon">
              <span class="material-icons">rocket_launch</span>
            </div>
            <div class="performance-info">
              <div class="performance-label">Performance Bonus</div>
              <div class="performance-value">+{{ (classDef.net_performance_bonus * 100).toFixed(0) }}%</div>
            </div>
          </div>
        </div>

        <!-- Included Spirits -->
        <div class="spirits-section">
          <h3>
            <span class="material-icons">auto_awesome</span>
            Included Spirits ({{ classDef.base_spirits.length }})
          </h3>
          <div class="spirits-grid">
            <div 
              v-for="spirit in spiritDetails" 
              :key="spirit.spirit_id"
              class="spirit-card"
            >
              <div class="spirit-header">
                <div class="spirit-name">{{ spirit.spirit_name }}</div>
                <div class="spirit-category">{{ spirit.spirit_category }}</div>
              </div>
              <div class="spirit-description">{{ spirit.spirit_description }}</div>
              <div class="spirit-tools">
                <div class="tools-label">Tools:</div>
                <div class="tools-list">
                  <span 
                    v-for="tool in spirit.spirit_tools.slice(0, 3)" 
                    :key="tool"
                    class="tool-tag"
                  >
                    {{ tool }}
                  </span>
                  <span v-if="spirit.spirit_tools.length > 3" class="tool-tag more">
                    +{{ spirit.spirit_tools.length - 3 }} more
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Available Tools -->
        <div class="tools-section">
          <h3>
            <span class="material-icons">build</span>
            Desktop Tools ({{ totalTools }})
          </h3>
          <div class="installation-notice">
            <div class="notice-icon">
              <span class="material-icons">computer</span>
            </div>
            <div class="notice-content">
              <strong>Desktop Installation Required</strong>
              <p>These tools will be installed on your local minion application to enable computer manipulation and automation capabilities.</p>
            </div>
          </div>
          <div class="tools-grid">
            <span 
              v-for="tool in allTools" 
              :key="tool"
              class="tool-item"
            >
              {{ tool }}
            </span>
          </div>
        </div>

        <!-- Perfect For -->
        <div class="perfect-for-section">
          <h3>
            <span class="material-icons">target</span>
            Perfect For
          </h3>
          <div class="perfect-for-list">
            <span 
              v-for="useCase in classDef.perfect_for" 
              :key="useCase"
              class="use-case-tag"
            >
              {{ useCase }}
            </span>
          </div>
        </div>

        <!-- Unlock Requirements -->
        <div v-if="!canUnlock" class="unlock-section">
          <h3>
            <span class="material-icons">lock</span>
            Unlock Requirements
          </h3>
          <div class="unlock-requirements">
            <div class="requirement-item">
              <span class="requirement-label">Required Rank:</span>
              <span class="requirement-value">{{ classDef.unlock_rank }}</span>
            </div>
            <div class="requirement-item">
              <span class="requirement-label">Required Level:</span>
              <span class="requirement-value">{{ classDef.unlock_level }}</span>
            </div>
            <div class="requirement-item">
              <span class="requirement-label">Your Rank:</span>
              <span class="requirement-value current">{{ userRank }}</span>
            </div>
            <div class="requirement-item">
              <span class="requirement-label">Your Level:</span>
              <span class="requirement-value current">{{ userLevel }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Actions -->
      <div class="modal-actions">
        <button @click="closeModal" class="action-btn secondary">
          Back to Selection
        </button>
        <button 
          v-if="canUnlock"
          @click="useClass"
          class="action-btn primary"
        >
          Install
        </button>
        <button 
          v-else
          @click="closeModal"
          class="action-btn primary"
        >
          Level Up to Unlock
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import classService from '@/services/classService'

export default {
  name: 'ClassDetailsModal',
  props: {
    classDef: {
      type: Object,
      required: true
    },
    userRank: {
      type: String,
      default: 'Novice'
    },
    userLevel: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      spiritDetails: [],
      loading: false,
      error: null
    }
  },
  computed: {
    canUnlock() {
      const rankHierarchy = {
        'Novice': 1, 'Skilled': 2, 'Specialist': 3, 
        'Expert': 4, 'Master': 5, 'Grandmaster': 6, 'Autonomous': 7
      }
      
      const userRankValue = rankHierarchy[this.userRank] || 1
      const classRankValue = rankHierarchy[this.classDef.unlock_rank] || 1
      
      return classRankValue <= userRankValue && this.classDef.unlock_level <= this.userLevel
    },

    allTools() {
      const tools = new Set()
      this.spiritDetails.forEach(spirit => {
        spirit.spirit_tools.forEach(tool => tools.add(tool))
      })
      return Array.from(tools).sort()
    },

    totalTools() {
      return this.allTools.length
    }
  },
  async mounted() {
    await this.loadSpiritDetails()
  },
  methods: {
    async loadSpiritDetails() {
      this.loading = true
      this.error = null
      
      try {
        this.spiritDetails = await classService.getClassSpirits(this.classDef.class_name)
      } catch (error) {
        console.error('Error loading spirit details:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    closeModal() {
      this.$emit('close')
    },

    useClass() {
      this.$emit('use-class', this.classDef)
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
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.class-details-modal {
  background: var(--card-bg);
  border-radius: 16px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2rem 2rem 1rem 2rem;
  border-bottom: 1px solid var(--border-color);
}

.class-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.class-card {
    box-shadow: var(--shadow);
}
.class-icon-large {
  font-size: 3rem;
  color: var(--primary);
}

.class-title h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.class-subtitle {
  font-size: 1rem;
  color: var(--secondary);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--secondary);
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-color);
}

.modal-content {
  padding: 2rem;
}

.class-description-section,
.spirits-section,
.tools-section,
.perfect-for-section,
.unlock-section {
  margin-bottom: 2rem;
}

.class-description-section h3,
.spirits-section h3,
.tools-section h3,
.perfect-for-section h3,
.unlock-section h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.class-description-section h3 .material-icons,
.spirits-section h3 .material-icons,
.tools-section h3 .material-icons,
.perfect-for-section h3 .material-icons,
.unlock-section h3 .material-icons {
  font-size: 1.5rem;
  color: var(--primary);
}

.class-description-section p {
  font-size: 1rem;
  color: var(--text-color);
  line-height: 1.6;
  margin: 0;
}

.performance-section {
  margin-bottom: 2rem;
}

.performance-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--success-light);
  border-radius: 12px;
  border: 1px solid var(--success);
}

.performance-icon {
  font-size: 2rem;
  color: var(--success);
}

.performance-info {
  flex: 1;
}

.performance-label {
  font-size: 0.9rem;
  color: var(--success);
  margin-bottom: 0.25rem;
}

.performance-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--success);
}

.spirits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.spirit-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem;
}

.spirit-header {
  margin-bottom: 0.75rem;
}

.spirit-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.spirit-category {
  font-size: 0.8rem;
  color: var(--secondary);
}

.spirit-description {
  font-size: 0.9rem;
  color: var(--text-color);
  line-height: 1.4;
  margin-bottom: 0.75rem;
}

.tools-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.tools-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.tool-tag {
  padding: 0.2rem 0.5rem;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
}

.tool-tag.more {
  background: var(--bg-secondary);
  color: var(--secondary);
}

.installation-notice {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--info-light);
  border: 1px solid var(--info);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.notice-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  color: var(--info);
}

.notice-content strong {
  display: block;
  color: var(--info);
  margin-bottom: 0.5rem;
}

.notice-content p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-color);
  line-height: 1.4;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
}

.tool-item {
  padding: 0.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.9rem;
  text-align: center;
  color: var(--text-color);
}

.perfect-for-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.use-case-tag {
  padding: 0.5rem 1rem;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.unlock-requirements {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.requirement-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.requirement-label {
  font-size: 0.9rem;
  color: var(--secondary);
}

.requirement-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-color);
}

.requirement-value.current {
  color: var(--primary);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  padding: 1rem 2rem 2rem 2rem;
  border-top: 1px solid var(--border-color);
}

.action-btn {
  flex: 1;
  padding: 0.75rem 1.5rem;
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

/* Responsive Design */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 0.5rem;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-content {
    padding: 1rem;
  }
  
  .class-header {
    gap: 0.75rem;
  }
  
  .class-icon-large {
    font-size: 2.5rem;
  }
  
  .spirits-grid {
    grid-template-columns: 1fr;
  }
  
  .tools-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  
  .unlock-requirements {
    grid-template-columns: 1fr;
  }
  
  .modal-actions {
    flex-direction: column;
    padding: 1rem;
  }
}
</style>
