<template>
  <div class="spirit-marketplace">
    <!-- Header -->
    <div class="page-header">
      <h1>Spirit Marketplace</h1>
      <p>Enhance your minions with specialized spirits</p>
      
      <!-- Filter Controls -->
      <div class="neumorphic-card filter-card">
        <div class="filter-controls">
          <div class="filter-group">
            <label>Tier:</label>
            <select v-model="selectedTier" @change="filterSpirits" class="form-control">
              <option value="">All Tiers</option>
              <option value="free">Free</option>
              <option value="basic">Basic</option>
              <option value="professional">Professional</option>
              <option value="premium">Premium</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Category:</label>
            <select v-model="selectedCategory" @change="filterSpirits" class="form-control">
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Search:</label>
            <input 
              type="text" 
              v-model="searchQuery" 
              @input="filterSpirits"
              placeholder="Search spirits..."
              class="form-control"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading spirits...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <span class="material-icons-round">error</span>
      <p>{{ error }}</p>
      <button @click="loadSpirits" class="retry-btn">Retry</button>
    </div>

    <!-- Spirits Grid -->
    <div v-else class="spirits-grid">
      <div 
        v-for="spirit in filteredSpirits" 
        :key="spirit.id" 
        class="neumorphic-card spirit-card"
        :class="{
          'free-tier': spirit.tier === 'free',
          'basic-tier': spirit.tier === 'basic',
          'professional-tier': spirit.tier === 'professional',
          'premium-tier': spirit.tier === 'premium'
        }"
      >
        <!-- Spirit Icon -->
        <div class="spirit-icon">
          <span class="spirit-emoji">{{ spirit.icon }}</span>
        </div>

        <!-- Spirit Info -->
        <div class="spirit-info">
          <h3>{{ spirit.name }}</h3>
          <p class="spirit-category">{{ spirit.category }}</p>
          <p class="spirit-description">{{ spirit.description }}</p>
          
          <!-- Pricing -->
          <div class="spirit-pricing">
            <span class="price" v-if="spirit.price_usd > 0">
              ${{ spirit.price_usd }}
            </span>
            <span class="price free" v-else>FREE</span>
            <span class="tier-badge">{{ spirit.tier }}</span>
          </div>

          <!-- Tools -->
          <div class="spirit-tools" v-if="spirit.tools && spirit.tools.length">
            <span class="tools-label">Tools:</span>
            <div class="tools-list">
              <span 
                v-for="tool in spirit.tools.slice(0, 3)" 
                :key="tool" 
                class="tool-tag"
              >
                {{ tool.replace(/_/g, ' ') }}
              </span>
              <span v-if="spirit.tools.length > 3" class="more-tools">
                +{{ spirit.tools.length - 3 }} more
              </span>
            </div>
          </div>

          <!-- Unlock Requirements -->
          <div class="unlock-requirements">
            <span class="requirement">
              Rank: {{ spirit.unlock_rank }} (Level {{ spirit.unlock_level }})
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="spirit-actions">
          <button 
            @click="viewSpiritDetails(spirit)" 
            class="btn btn-secondary"
          >
            <span class="material-icons-round">info</span>
            Details
          </button>
          
          <button 
            @click="assignSpirit(spirit)" 
            class="btn btn-primary"
            :disabled="!canAssignSpirit(spirit)"
          >
            <span class="material-icons-round">add</span>
            Assign
          </button>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="!loading && !error && filteredSpirits.length === 0" class="no-results">
      <span class="material-icons-round">search_off</span>
      <p>No spirits found matching your criteria</p>
    </div>

    <!-- Spirit Details Modal -->
    <div v-if="selectedSpirit" class="modal-overlay" @click="closeSpiritDetails">
      <div class="neumorphic-card modal-content spirit-details-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedSpirit.name }}</h3>
          <button @click="closeSpiritDetails" class="close-btn">
            <span class="material-icons-round">close</span>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="spirit-detail-section">
            <div class="spirit-icon-large">
              <span class="spirit-emoji">{{ selectedSpirit.icon }}</span>
            </div>
            <div class="spirit-detail-info">
              <p class="spirit-description">{{ selectedSpirit.description }}</p>
              
              <div class="detail-row">
                <strong>Category:</strong> {{ selectedSpirit.category }}
              </div>
              <div class="detail-row">
                <strong>Price:</strong> 
                <span v-if="selectedSpirit.price_usd > 0">${{ selectedSpirit.price_usd }}</span>
                <span v-else>FREE</span>
              </div>
              <div class="detail-row">
                <strong>Tier:</strong> {{ selectedSpirit.tier }}
              </div>
              <div class="detail-row">
                <strong>Unlock:</strong> {{ selectedSpirit.unlock_rank }} (Level {{ selectedSpirit.unlock_level }})
              </div>
            </div>
          </div>

          <!-- Tools Section -->
          <div class="tools-section" v-if="selectedSpirit.tools && selectedSpirit.tools.length">
            <h4>Available Tools</h4>
            <div class="tools-grid">
              <div 
                v-for="tool in selectedSpirit.tools" 
                :key="tool" 
                class="tool-item"
              >
                {{ tool.replace(/_/g, ' ') }}
              </div>
            </div>
          </div>

          <!-- Synergies Section -->
          <div class="synergies-section" v-if="selectedSpirit.synergies && Object.keys(selectedSpirit.synergies).length">
            <h4>Spirit Synergies</h4>
            <div class="synergy-list">
              <div 
                v-for="(bonus, spiritName) in selectedSpirit.synergies" 
                :key="spiritName"
                class="synergy-item positive"
              >
                <span class="material-icons-round">add</span>
                <span>{{ spiritName }}: +{{ bonus }}%</span>
              </div>
            </div>
          </div>

          <!-- Conflicts Section -->
          <div class="conflicts-section" v-if="selectedSpirit.conflicts && Object.keys(selectedSpirit.conflicts).length">
            <h4>Spirit Conflicts</h4>
            <div class="conflict-list">
              <div 
                v-for="(penalty, spiritName) in selectedSpirit.conflicts" 
                :key="spiritName"
                class="synergy-item negative"
              >
                <span class="material-icons-round">remove</span>
                <span>{{ spiritName }}: {{ penalty }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeSpiritDetails" class="btn btn-secondary">Close</button>
          <button 
            @click="assignSpirit(selectedSpirit)" 
            class="btn btn-primary"
            :disabled="!canAssignSpirit(selectedSpirit)"
          >
            <span class="material-icons-round">add</span>
            Assign Spirit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import spiritService from '@/services/spiritService.js'

export default {
  name: 'SpiritMarketplace',
  props: {
    minionId: {
      type: Number,
      default: null
    },
    userId: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      spirits: [],
      filteredSpirits: [],
      loading: false,
      error: null,
      selectedTier: '',
      selectedCategory: '',
      searchQuery: '',
      categories: [],
      selectedSpirit: null
    }
  },
  mounted() {
    this.loadSpirits()
  },
  methods: {
    async loadSpirits() {
      this.loading = true
      this.error = null
      
      try {
        const spirits = await spiritService.getAllSpirits()
        this.spirits = spirits
        this.filteredSpirits = spirits
        
        // Extract unique categories
        this.categories = [...new Set(spirits.map(s => s.category))]
        
        console.log(`Loaded ${spirits.length} spirits`)
      } catch (error) {
        this.error = 'Failed to load spirits. Please check if the spirit server is running on port 5001.'
        console.error('Error loading spirits:', error)
      } finally {
        this.loading = false
      }
    },

    filterSpirits() {
      let filtered = this.spirits

      // Filter by tier
      if (this.selectedTier) {
        filtered = filtered.filter(spirit => spirit.tier === this.selectedTier)
      }

      // Filter by category
      if (this.selectedCategory) {
        filtered = filtered.filter(spirit => spirit.category === this.selectedCategory)
      }

      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(spirit => 
          spirit.name.toLowerCase().includes(query) ||
          spirit.description.toLowerCase().includes(query) ||
          spirit.category.toLowerCase().includes(query)
        )
      }

      this.filteredSpirits = filtered
    },

    viewSpiritDetails(spirit) {
      this.selectedSpirit = spirit
    },

    closeSpiritDetails() {
      this.selectedSpirit = null
    },

    canAssignSpirit(spirit) {
      // Basic validation - can be enhanced with user permissions
      return spirit.tier === 'free' || spirit.tier === 'basic'
    },

    async assignSpirit(spirit) {
      if (!this.minionId) {
        this.$emit('assign-spirit', spirit)
        return
      }

      try {
        const result = await spiritService.assignSpiritToMinion(
          this.minionId, 
          spirit.id, 
          this.userId
        )
        
        if (result.success) {
          this.$emit('spirit-assigned', { spirit, result })
          this.$emit('show-message', {
            type: 'success',
            text: `${spirit.name} assigned successfully!`
          })
        } else {
          this.$emit('show-message', {
            type: 'error',
            text: result.error || 'Failed to assign spirit'
          })
        }
      } catch (error) {
        this.$emit('show-message', {
          type: 'error',
          text: 'Failed to assign spirit'
        })
        console.error('Error assigning spirit:', error)
      }
    }
  }
}
</script>

<style scoped>
.spirit-marketplace {
  padding: var(--spacer-lg);
  /* max-width: 1200px; */
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacer-xl);
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: var(--spacer-sm);
  color: var(--text-color);
  font-weight: 600;
}

.page-header p {
  color: var(--text-muted);
  font-size: 1.1rem;
  margin-bottom: var(--spacer-lg);
}

.filter-card {
  margin-bottom: var(--spacer-lg);
}

.filter-controls {
  display: flex;
  gap: var(--spacer-lg);
  justify-content: center;
  flex-wrap: wrap;
  padding: var(--spacer-md);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-sm);
}

.filter-group label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9rem;
}

.filter-group .form-control {
  min-width: 150px;
}

.spirits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--spacer-lg);
  margin-bottom: var(--spacer-xl);
}

.spirit-card {
  padding: var(--spacer-lg);
  transition: var(--transition);
  border-left: 4px solid var(--secondary);
}

.spirit-card:hover {
  transform: translateY(-2px);
}

.spirit-card.free-tier {
  border-left-color: var(--success);
}

.spirit-card.basic-tier {
  border-left-color: var(--info);
}

.spirit-card.professional-tier {
  border-left-color: var(--warning);
}

.spirit-card.premium-tier {
  border-left-color: var(--primary);
}

.spirit-icon {
  text-align: center;
  margin-bottom: 15px;
}

.spirit-emoji {
  font-size: 3rem;
}

.spirit-info h3 {
  font-size: 1.4rem;
  margin-bottom: 8px;
  color: #333;
}

.spirit-category {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 10px;
  font-weight: 600;
}

.spirit-description {
  color: #555;
  line-height: 1.5;
  margin-bottom: 15px;
}

.spirit-pricing {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.price.free {
  color: #4CAF50;
}

.tier-badge {
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.spirit-tools {
  margin-bottom: 15px;
}

.tools-label {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

.tools-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 5px;
}

.tool-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 0.8rem;
}

.more-tools {
  color: #666;
  font-size: 0.8rem;
  font-style: italic;
}

.unlock-requirements {
  margin-bottom: 15px;
}

.requirement {
  font-size: 0.9rem;
  color: #666;
}

.spirit-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: all 0.2s;
}

.btn-primary {
  background: #2196F3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976D2;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.loading-state,
.error-state,
.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2196F3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 15px;
}

/* Modal Styles */
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
}

.spirit-details-modal {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.spirit-detail-section {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.spirit-icon-large .spirit-emoji {
  font-size: 4rem;
}

.spirit-detail-info {
  flex: 1;
}

.detail-row {
  margin-bottom: 10px;
  color: #555;
}

.tools-section,
.synergies-section,
.conflicts-section {
  margin-bottom: 25px;
}

.tools-section h4,
.synergies-section h4,
.conflicts-section h4 {
  margin-bottom: 15px;
  color: #333;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.tool-item {
  background: #e3f2fd;
  color: #1976d2;
  padding: 8px 12px;
  border-radius: 8px;
  text-align: center;
  font-size: 0.9rem;
}

.synergy-list,
.conflict-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.synergy-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
}

.synergy-item.positive {
  background: #e8f5e8;
  color: #2e7d32;
}

.synergy-item.negative {
  background: #ffebee;
  color: #c62828;
}

.modal-footer {
  display: flex;
  gap: 15px;
  padding: 20px;
  border-top: 1px solid #eee;
  justify-content: flex-end;
}

/* Responsive Design */
@media (max-width: 768px) {
  .spirits-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .spirit-detail-section {
    flex-direction: column;
    text-align: center;
  }
  
  .modal-footer {
    flex-direction: column;
  }
}
</style>
