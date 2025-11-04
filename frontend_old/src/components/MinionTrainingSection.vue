<template>
  <div class="minion-training-section">
    <div class="section-header">
      <h2><span data-v-7a7a37b1="" class="material-icons-round">smart_toy</span> Minion Refinement</h2>
      <p>Enhance your minions with external models and training</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">
        <span class="material-icons-round">refresh</span>
      </div>
      <p>Loading minions...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">
        <span class="material-icons-round">error</span>
      </div>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="fetchMinions">
        <span class="material-icons-round">refresh</span>
        Retry
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="minions.length === 0" class="empty-state">
      <div class="empty-icon">
        <span class="material-icons-round">smart_toy</span>
      </div>
      <h3>No Minions Found</h3>
      <p>Create your first minion to start training and refinement.</p>
      <button class="btn btn-primary" @click="createMinion">
        <span class="material-icons-round">add</span>
        Create Minion
      </button>
    </div>

    <!-- Minions Grid -->
        <div v-else class="minions-grid">
        <MinionTrainingCard 
          v-for="minion in minions" 
          :key="minion.id" 
          :minion="minion"
          :pending-jobs="pendingJobs"
          :ref="`minionCard-${minion.id}`"
          @view-history="handleViewHistory"
          @upgrade-minion="handleUpgradeMinion"
          @view-pending-job="handleViewPendingJob"
          @start-pending-training="handleStartPendingTraining"
          @delete-pending-job="handleDeletePendingJob"
          @training-completed="handleTrainingCompleted"
        />
        </div>

    <!-- External LoRA Modal -->
    <MinionExternalLoraModal
      v-if="showLoraModal"
      :selected-minion="selectedMinionForLora"
      :is-visible="showLoraModal"
      @close="closeLoraModal"
      @training-started="handleLoraTrainingStarted"
    />
  </div>
</template>

<script>
import MinionTrainingCard from './MinionTrainingCard.vue'
import MinionExternalLoraModal from './MinionExternalLoraModal.vue'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'MinionTrainingSection',
  components: {
    MinionTrainingCard,
    MinionExternalLoraModal
  },
  props: {
    pendingJobs: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      minions: [],
      loading: false,
      error: null,
      authStore: useAuthStore(),
      // External LoRA Modal state
      showLoraModal: false,
      selectedMinionForLora: null
    }
  },
  async mounted() {
    // Wait for auth store to initialize
    if (!this.authStore.user && this.authStore.token) {
      await this.authStore.initialize()
    }
    this.fetchMinions()
  },
  watch: {
    'authStore.user': {
      handler(newUser) {
        if (newUser && newUser.id) {
          console.log('👤 User authenticated, fetching minions...')
          this.fetchMinions()
        }
      },
      immediate: false
    },
    pendingJobs: {
      handler(newPendingJobs) {
        console.log('📋 Pending jobs updated:', newPendingJobs)
      },
      deep: true
    }
  },
  methods: {
    async fetchMinions() {
      this.loading = true
      this.error = null
      
      try {
        // Debug auth state
        console.log('🔍 MinionTrainingSection auth state:', {
          user: this.authStore.user,
          token: this.authStore.token ? 'Token exists' : 'No token',
          isAuthenticated: this.authStore.isAuthenticated
        })
        
        // Get user from auth store
        if (!this.authStore?.user?.id) {
          throw new Error('User not authenticated')
        }

        const response = await fetch(
          `http://localhost:5000/api/users/${this.authStore.user.id}/external-training/jobs?group_by=minion&latest_only=true`,
          {
            headers: {
              'Authorization': `Bearer ${this.authStore.token}`
            }
          }
        )

        const result = await response.json()

        if (result.success) {
          this.minions = result.minions || []
          console.log('📊 Loaded minions:', this.minions)
        } else {
          throw new Error(result.error || 'Failed to fetch minions')
        }
      } catch (error) {
        console.error('Error fetching minions:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    handleViewHistory(minion) {
      console.log('📊 View history for minion:', minion)
      // Emit event to parent component to open history modal
      this.$emit('view-history', minion)
    },

    handleUpgradeMinion(minion) {
      console.log('🔄 Upgrade minion:', minion)
      // Emit event to parent component to open upgrade modal
      this.$emit('upgrade-minion', minion)
    },

    createMinion() {
      // Emit event to parent component to open minion creation
      this.$emit('create-minion')
    },

    handleViewPendingJob(job) {
      this.$emit('view-pending-job', job)
    },

    handleStartPendingTraining(job) {
      this.$emit('start-pending-training', job)
    },

        handleDeletePendingJob(job) {
          this.$emit('delete-pending-job', job)
        },

        handleTrainingCompleted(minionId) {
          console.log('🎉 Training completed for minion:', minionId)
          // Refresh the minions data to show updated training results
          this.fetchMinions()
        },

  }
}
</script>

<style scoped>
.minion-training-section {
  margin-bottom: 2rem;
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.section-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  animation: spin 1s linear infinite;
}

.loading-spinner .material-icons-round {
  font-size: 1.5rem;
  color: var(--primary-color);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-icon,
.empty-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.error-icon {
  background: var(--danger-light);
}

.error-icon .material-icons-round {
  font-size: 2rem;
  color: var(--danger-color);
}

.empty-icon {
  background: var(--info-light);
}

.empty-icon .material-icons-round {
  font-size: 2rem;
  color: var(--info-color);
}

.loading-state p,
.error-state p,
.empty-state p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.minions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-dark);
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .section-header h2 {
    color: var(--dark-text-primary);
  }
  
  .section-header p {
    color: var(--dark-text-secondary);
  }
  
  .loading-state p,
  .error-state p,
  .empty-state p {
    color: var(--dark-text-secondary);
  }
  
  .empty-state h3 {
    color: var(--dark-text-primary);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .minions-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header h2 {
    font-size: 1.3rem;
  }
}
</style>
