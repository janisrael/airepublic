<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1>Base Model Providers</h1>
      <p>Manage dynamic LLM providers and configurations for external model access.</p>
    </div>

    <!-- Stats Cards -->
    <div class="dashboard-grid">
      <div class="neumorphic-card stats-card">
        <div class="stats-icon">
          <span class="material-icons-round">smart_toy</span>
        </div>
        <div class="stats-info">
          <h3>{{ stats.availableProviders }}</h3>
          <p>Available Providers</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon config">
          <span class="material-icons-round">settings</span>
        </div>
        <div class="stats-info">
          <h3>{{ stats.userConfigs }}</h3>
          <p>Your Configurations</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon usage">
          <span class="material-icons-round">analytics</span>
        </div>
        <div class="stats-info">
          <h3>{{ stats.totalRequests }}</h3>
          <p>Total Requests</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon cost">
          <span class="material-icons-round">attach_money</span>
        </div>
        <div class="stats-info">
          <h3>${{ stats.totalCost.toFixed(2) }}</h3>
          <p>Total Cost</p>
        </div>
      </div>
    </div>

    <!-- Provider Cards -->
    <div class="providers-section">
      <div class="section-header">
        <h2>Available Providers</h2>
        <button class="btn btn-sm btn-secondary" @click="refreshProviders">
          <span class="material-icons-round">refresh</span>
          Refresh
        </button>
      </div>
      
      <div class="providers-grid">
        <div 
          v-for="provider in providers" 
          :key="provider.name"
          class="provider-card"
          :class="{ 'selected': selectedProvider?.name === provider.name }"
          @click="selectProvider(provider)"
        >
          <div class="card-header">
            <div class="provider-icon">
              <span class="material-icons-round">{{ getProviderIcon(provider.name) }}</span>
            </div>
            <div class="provider-status">
              <span class="status-indicator" :class="{ 'active': provider.is_available }"></span>
            </div>
          </div>
          
          <div class="card-content">
            <h3 class="provider-name">{{ provider.display_name || provider.name }}</h3>
            <p class="provider-description">{{ provider.description || 'External LLM provider' }}</p>
            
            <div class="provider-features">
              <div class="feature-item" v-if="provider.supports_streaming">
                <span class="material-icons-round">stream</span>
                <span>Streaming</span>
              </div>
              <div class="feature-item" v-if="provider.requires_api_key">
                <span class="material-icons-round">key</span>
                <span>API Key Required</span>
              </div>
              <div class="feature-item" v-if="!provider.requires_api_key">
                <span class="material-icons-round">free_breakfast</span>
                <span>Free Tier</span>
              </div>
            </div>
            
            <div class="provider-models" v-if="provider.default_models && provider.default_models.length > 0">
              <h4>Models ({{ provider.default_models.length }})</h4>
              <div class="models-list">
                <div 
                  v-for="model in provider.default_models" 
                  :key="model" 
                  class="model-item"
                >
                  <span class="material-icons-round model-icon">smart_toy</span>
                  <span class="model-name">{{ model }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <button 
              class="btn btn-sm btn-primary" 
              @click.stop="selectProvider(provider)"
            >
              <span class="material-icons-round">settings</span>
              Configure
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Provider Configuration Modal -->
    <TabbedModal
      :visible="!!selectedProvider"
      :title="selectedProvider ? `Configure ${selectedProvider.display_name || selectedProvider.name}` : ''"
      size="large"
      :tabs="providerTabs"
      :default-tab="'configs'"
      @close="closeConfigModal"
      @tab-change="activeTab = $event"
    >

          <!-- Configurations Tab -->
          <div v-if="activeTab === 'configs'" class="tab-content">
            <div v-if="userConfigs.length > 0" class="configs-list">
              <div v-for="config in userConfigs" :key="config.id" class="config-item">
                <div class="config-details">
                  <h4>{{ config.config_name }}</h4>
                  <p>Model: {{ config.model_id }} | Created: {{ formatDate(config.created_at) }}</p>
                </div>
                <div class="config-actions">
                  <button class="btn btn-sm btn-secondary" @click="testProviderConfig(config.id)">
                    <span class="material-icons-round">play_arrow</span>
                    Test
                  </button>
                  <button class="btn btn-sm btn-primary" @click="setDefaultConfig(config.id)">
                    <span class="material-icons-round">star</span>
                    Set Default
                  </button>
                  <button class="btn btn-sm btn-danger" @click="deleteConfig(config.id)">
                    <span class="material-icons-round">delete</span>
                    Delete
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <span class="material-icons-round">settings</span>
              <p>No configurations found. Create a new configuration to get started.</p>
            </div>
          </div>

          <!-- New Config Tab -->
          <div v-if="activeTab === 'new'" class="tab-content">
            <div class="config-form">
        <div class="form-row">
          <div class="form-group">
            <label>Configuration Name</label>
            <input 
              v-model="configForm.name" 
              class="form-control" 
              placeholder="e.g., My OpenAI Config"
              required 
            />
          </div>
          <div class="form-group">
            <label>Model</label>
            <select v-model="configForm.model_id" class="form-control" required>
              <option value="">Select a model...</option>
              <option v-for="model in selectedProvider.default_models" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
          </div>
        </div>
        
        <div v-if="selectedProvider.requires_api_key" class="form-group">
          <label>API Key</label>
          <input 
            type="password" 
            v-model="configForm.api_key" 
            class="form-control" 
            placeholder="Enter your API key"
            required 
          />
        </div>
        
        <div v-if="selectedProvider.requires_base_url" class="form-group">
          <label>Base URL</label>
          <input 
            v-model="configForm.base_url" 
            class="form-control" 
            :placeholder="getDefaultBaseUrl(selectedProvider.name)"
          />
        </div>
        
              <div class="form-actions">
                <button class="btn btn-secondary" @click="cancelConfigForm">Cancel</button>
                <button class="btn btn-primary" @click="saveProviderConfig" :disabled="!isConfigValid">
                  <span class="material-icons-round">save</span>
                  Save Configuration
                </button>
              </div>
            </div>
          </div>

          <!-- Test Query Tab -->
          <div v-if="activeTab === 'test'" class="tab-content">
            <div class="query-form">
              <div class="query-controls">
                <div class="form-group">
                  <label>Model</label>
                  <select v-model="queryForm.model_id" class="form-control">
                    <option v-for="config in userConfigs" :key="config.id" :value="config.model_id">
                      {{ config.model_id }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Temperature</label>
                  <input 
                    v-model.number="queryForm.temperature" 
                    type="range" 
                    min="0" 
                    max="2" 
                    step="0.1" 
                    class="form-control"
                  />
                  <span class="range-value">{{ queryForm.temperature }}</span>
                </div>
              </div>
              
              <div class="form-group">
                <label>Query</label>
                <textarea 
                  v-model="queryForm.query" 
                  class="form-control" 
                  placeholder="Enter your query here..."
                  rows="4"
                ></textarea>
              </div>
              
              <div class="form-actions">
                <button class="btn btn-primary" @click="submitQuery" :disabled="!queryForm.query || loading">
                  <span class="material-icons-round">send</span>
                  {{ loading ? 'Querying...' : 'Send Query' }}
                </button>
              </div>
            </div>
            
            <div v-if="queryResponse" class="query-response">
              <h4>Response</h4>
              <div class="response-content">
                {{ queryResponse }}
              </div>
            </div>
          </div>
    </TabbedModal>

    <!-- Usage Statistics -->
    <div v-if="usageStats.total_requests > 0" class="usage-stats">
      <h3>Usage Statistics</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ usageStats.total_requests }}</div>
          <div class="stat-label">Total Requests</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ usageStats.total_tokens.toLocaleString() }}</div>
          <div class="stat-label">Total Tokens</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${{ usageStats.total_cost.toFixed(2) }}</div>
          <div class="stat-label">Total Cost</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ usageStats.avg_response_time.toFixed(0) }}ms</div>
          <div class="stat-label">Avg Response Time</div>
        </div>
      </div>
    </div>

    <!-- Query Interface -->
    <div v-if="selectedProvider && userConfigs.length > 0" class="query-interface">
      <h3>Test Query</h3>
      <div class="query-form">
        <div class="query-controls">
          <div class="form-group">
            <label>Model</label>
            <select v-model="queryForm.model_id" class="form-control">
              <option v-for="config in userConfigs" :key="config.id" :value="config.model_id">
                {{ config.model_id }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Temperature</label>
            <input 
              type="range" 
              v-model.number="queryForm.temperature" 
              min="0" 
              max="2" 
              step="0.1" 
              class="form-control"
            />
            <span>{{ queryForm.temperature }}</span>
          </div>
          <div class="form-group">
            <label>Max Tokens</label>
            <input 
              type="number" 
              v-model.number="queryForm.max_tokens" 
              min="1" 
              max="4096" 
              class="form-control"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label>Query</label>
          <textarea 
            v-model="queryForm.query" 
            class="query-textarea" 
            placeholder="Enter your query here..."
            rows="4"
          ></textarea>
        </div>
        
        <div class="form-actions">
          <button class="btn btn-primary" @click="submitQuery" :disabled="!queryForm.query || loading">
            <span class="material-icons-round">send</span>
            {{ loading ? 'Querying...' : 'Send Query' }}
          </button>
        </div>
      </div>
      
      <div v-if="queryResponse" class="query-response">
        <h4>Response</h4>
        <div class="response-content">{{ queryResponse }}</div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import TabbedModal from '@/components/TabbedModal.vue'
import { getApiUrl } from '@/config/api'

export default {
  name: 'BaseModelProviders',
  components: {
    TabbedModal
  },
  data() {
    return {
      providers: [],
      selectedProvider: null,
      userConfigs: [],
      testResults: [],
      usageStats: {
        total_requests: 0,
        total_tokens: 0,
        total_cost: 0.0,
        avg_response_time: 0.0
      },
      showConfigForm: false,
      activeTab: 'configs',
      configForm: {
        name: '',
        model_id: '',
        api_key: '',
        base_url: ''
      },
      queryForm: {
        model_id: '',
        query: '',
        temperature: 0.7,
        max_tokens: 1024
      },
      queryResponse: '',
      loading: false
    }
  },
  computed: {
    authStore() {
      return useAuthStore()
    },
    stats() {
      return {
        availableProviders: this.providers.length,
        userConfigs: this.userConfigs.length,
        totalRequests: this.usageStats.total_requests,
        totalCost: this.usageStats.total_cost
      }
    },
    isConfigValid() {
      return this.configForm.name && 
             this.configForm.model_id && 
             (!this.selectedProvider?.requires_api_key || this.configForm.api_key)
    },
    providerTabs() {
      return [
        {
          id: 'configs',
          label: 'Configurations',
          icon: 'list'
        },
        {
          id: 'new',
          label: 'New Config',
          icon: 'add'
        },
        {
          id: 'test',
          label: 'Test Query',
          icon: 'play_arrow',
          disabled: this.userConfigs.length === 0
        }
      ]
    }
  },
  async mounted() {
    await this.loadProviders()
    await this.loadUsageStats()
  },
  methods: {
    async loadProviders() {
      try {
        this.loading = true
        const response = await fetch(getApiUrl('providers/'), {
          headers: this.getAuthHeaders()
        })
        
        const data = await response.json()
        if (data.success) {
          this.providers = data.providers
        } else {
          console.error('Failed to load providers:', data.error)
        }
      } catch (error) {
        console.error('Error loading providers:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadUsageStats() {
      try {
        const response = await fetch(getApiUrl('providers/usage'), {
          headers: this.getAuthHeaders()
        })
        
        const data = await response.json()
        if (data.success) {
          this.usageStats = data.stats
        }
      } catch (error) {
        console.error('Error loading usage stats:', error)
      }
    },
    
    selectProvider(provider) {
      this.selectedProvider = provider
      this.showConfigForm = false
      this.activeTab = 'configs'
      this.loadUserConfigs()
    },
    
    closeConfigModal() {
      this.selectedProvider = null
      this.activeTab = 'configs'
      this.showConfigForm = false
      this.cancelConfigForm()
    },
    
    async loadUserConfigs() {
      if (!this.selectedProvider) return
      
      try {
        const response = await fetch(getApiUrl(`providers/configs?provider=${this.selectedProvider.name}`), {
          headers: this.getAuthHeaders()
        })
        
        const data = await response.json()
        if (data.success) {
          this.userConfigs = data.configs
        }
      } catch (error) {
        console.error('Error loading user configs:', error)
      }
    },
    
    async saveProviderConfig() {
      try {
        this.loading = true
        
        const configData = {
          provider_name: this.selectedProvider.name,
          config_name: this.configForm.name,
          model_id: this.configForm.model_id,
          api_key: this.configForm.api_key,
          base_url: this.configForm.base_url
        }
        
        const response = await fetch(getApiUrl('providers/configs'), {
          method: 'POST',
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(configData)
        })
        
        const data = await response.json()
        if (data.success) {
          this.cancelConfigForm()
          await this.loadUserConfigs()
          this.$toast.success('Configuration saved successfully')
        } else {
          this.$toast.error(data.error || 'Failed to save configuration')
        }
      } catch (error) {
        console.error('Error saving config:', error)
        this.$toast.error('Error saving configuration')
      } finally {
        this.loading = false
      }
    },
    
    async testProviderConfig(configId) {
      try {
        this.loading = true
        
        const response = await fetch(getApiUrl('providers/test'), {
          method: 'POST',
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ config_id: configId })
        })
        
        const data = await response.json()
        if (data.success) {
          this.testResults.unshift({
            id: Date.now(),
            provider: data.provider,
            success: true,
            response: data.response,
            response_time: data.response_time
          })
          this.$toast.success('Connection test successful')
        } else {
          this.testResults.unshift({
            id: Date.now(),
            provider: data.provider,
            success: false,
            error: data.error,
            response_time: 0
          })
          this.$toast.error('Connection test failed')
        }
      } catch (error) {
        console.error('Error testing config:', error)
        this.$toast.error('Error testing configuration')
      } finally {
        this.loading = false
      }
    },
    
    async setDefaultConfig(configId) {
      try {
        const response = await fetch(getApiUrl(`providers/configs/${configId}`), {
          method: 'PUT',
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ is_default: true })
        })
        
        const data = await response.json()
        if (data.success) {
          await this.loadUserConfigs()
          this.$toast.success('Default configuration updated')
        } else {
          this.$toast.error(data.error || 'Failed to update default configuration')
        }
      } catch (error) {
        console.error('Error setting default config:', error)
        this.$toast.error('Error updating default configuration')
      }
    },
    
    async deleteConfig(configId) {
      if (!confirm('Are you sure you want to delete this configuration?')) return
      
      try {
        const response = await fetch(getApiUrl(`providers/configs/${configId}`), {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        const data = await response.json()
        if (data.success) {
          await this.loadUserConfigs()
          this.$toast.success('Configuration deleted')
        } else {
          this.$toast.error(data.error || 'Failed to delete configuration')
        }
      } catch (error) {
        console.error('Error deleting config:', error)
        this.$toast.error('Error deleting configuration')
      }
    },
    
    async submitQuery() {
      if (!this.queryForm.query || !this.queryForm.model_id) return
      
      try {
        this.loading = true
        this.queryResponse = ''
        
        const response = await fetch(getApiUrl(`providers/query/${this.selectedProvider.name}/${this.queryForm.model_id}`), {
          method: 'POST',
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            messages: [
              { role: 'user', content: this.queryForm.query }
            ],
            temperature: this.queryForm.temperature,
            max_tokens: this.queryForm.max_tokens
          })
        })
        
        const data = await response.json()
        if (data.success) {
          this.queryResponse = data.response
          await this.loadUsageStats()
        } else {
          this.$toast.error(data.error || 'Query failed')
        }
      } catch (error) {
        console.error('Error submitting query:', error)
        this.$toast.error('Error submitting query')
      } finally {
        this.loading = false
      }
    },
    
    cancelConfigForm() {
      this.showConfigForm = false
      this.configForm = {
        name: '',
        model_id: '',
        api_key: '',
        base_url: ''
      }
    },
    
    async refreshProviders() {
      await this.loadProviders()
      this.$toast.success('Providers refreshed')
    },
    
    getProviderIcon(providerName) {
      const icons = {
        'openai': 'smart_toy',
        'anthropic': 'psychology',
        'nvidia': 'memory',
        'huggingface': 'favorite',
        'ollama': 'dns',
        'cohere': 'psychology_alt',
        'mistral': 'auto_awesome',
        'google': 'search'
      }
      return icons[providerName] || 'extension'
    },
    
    getDefaultBaseUrl(providerName) {
      const urls = {
        'openai': 'https://api.openai.com/v1',
        'anthropic': 'https://api.anthropic.com',
        'nvidia': 'https://integrate.api.nvidia.com/v1',
        'huggingface': 'https://api-inference.huggingface.co/models',
        'cohere': 'https://api.cohere.ai'
      }
      return urls[providerName] || ''
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    
    getAuthHeaders() {
      return {
        'Authorization': `Bearer ${this.authStore.token}`
      }
    }
  }
}
</script>

<style scoped>
@import '@/assets/base_model.css';

/* Additional component-specific styles */
.dashboard-container {
  padding: 2rem;

  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.page-header p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stats-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  background: var(--neumorphic-bg);
  box-shadow: 
    inset 4px 4px 8px var(--neumorphic-shadow-dark),
    inset -4px -4px 8px var(--neumorphic-shadow-light);
}

.stats-icon i {
  font-size: 28px;
  color: var(--primary-color);
}

.stats-info h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.stats-info p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0.25rem 0 0 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  box-shadow: 
    4px 4px 8px var(--neumorphic-shadow-dark),
    -4px -4px 8px var(--neumorphic-shadow-light);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 
    6px 6px 12px var(--neumorphic-shadow-dark),
    -6px -6px 12px var(--neumorphic-shadow-light);
}

.btn-secondary {
  background: var(--neumorphic-bg);
  color: var(--text-primary);
  box-shadow: 
    4px 4px 8px var(--neumorphic-shadow-dark),
    -4px -4px 8px var(--neumorphic-shadow-light);
}

.btn-secondary:hover {
  transform: translateY(-1px);
  box-shadow: 
    6px 6px 12px var(--neumorphic-shadow-dark),
    -6px -6px 12px var(--neumorphic-shadow-light);
}

.btn-danger {
  background: var(--error-color);
  color: white;
  box-shadow: 
    4px 4px 8px var(--neumorphic-shadow-dark),
    -4px -4px 8px var(--neumorphic-shadow-light);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn:disabled:hover {
  transform: none;
  box-shadow: 
    4px 4px 8px var(--neumorphic-shadow-dark),
    -4px -4px 8px var(--neumorphic-shadow-light);
}
</style>
