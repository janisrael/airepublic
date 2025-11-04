<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1>Model Comparison</h1>
      <p>Compare AI models side-by-side with detailed specifications and performance metrics</p>
    </div>

    <!-- Stats Cards -->
    <div class="dashboard-grid">
      <div class="neumorphic-card stats-card">
        <div class="stats-icon">
          <span class="material-icons-round">smart_toy</span>
        </div>
        <div class="stats-info">
          <h3>{{ filteredModels.length }}</h3>
          <p>{{ viewFilter === 'minions' ? 'Available Minions' : 'Base Models' }}</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon training">
          <span class="material-icons-round">compare_arrows</span>
        </div>
        <div class="stats-info">
          <h3>{{ selectedModels.length }}</h3>
          <p>Selected for Comparison</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon dataset">
          <span class="material-icons-round">table_chart</span>
        </div>
        <div class="stats-info">
          <h3>{{ comparisonData.length }}</h3>
          <p>Models Compared</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon accuracy">
          <span class="material-icons-round">analytics</span>
        </div>
        <div class="stats-info">
          <h3>{{ uniqueCapabilities.length }}</h3>
          <p>Unique Capabilities</p>
        </div>
      </div>
    </div>

    <!-- Model Selection and Comparison -->
    <div class="dashboard-row">
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Model Selection</h3>
            <div class="selection-controls">
              <div class="btn-group" role="group">
                <button 
                  @click="viewFilter = 'minions'"
                  :class="['btn', 'btn-sm', viewFilter === 'minions' ? 'btn-primary' : 'btn-outline-primary']"
                  title="View Minions"
                >
                  <span class="material-icons-round">smart_toy</span>
                  Minion
                </button>
                <button 
                  @click="viewFilter = 'baseModels'"
                  :class="['btn', 'btn-sm', viewFilter === 'baseModels' ? 'btn-primary' : 'btn-outline-primary']"
                  title="View Base Models"
                >
                  <span class="material-icons-round">storage</span>
                  Base
                </button>
              </div>
              <button 
                @click="selectAllModels" 
                class="btn btn-sm btn-outline-primary"
                :disabled="filteredModels.length === 0"
              >
                <span class="material-icons-round">select_all</span>
                Select All
              </button>
              <button 
                @click="clearSelection" 
                class="btn btn-sm btn-outline-secondary"
                :disabled="selectedModels.length === 0"
              >
                <span class="material-icons-round">clear_all</span>
                Clear All
              </button>
            </div>
          </div>
          
          <div class="model-selection-grid">
            <div 
              v-for="model in filteredModels" 
              :key="getModelKey(model)"
              class="model-selection-card"
              :class="{ 'selected': selectedModels.includes(getModelKey(model)) }"
              @click="toggleModelSelection(getModelKey(model))"
            >
              <div class="model-info">
                <div class="model-header-with-avatar">
                  <div class="model-avatar" v-if="model.avatar_url">
                    <img :src="model.avatar_url" :alt="(model.display_name || model.name) + ' avatar'" class="avatar-image">
                  </div>
                  <div class="model-avatar-placeholder" v-else>
                    <span class="material-icons-round">smart_toy</span>
                  </div>
                  <h4>{{ model.display_name || model.name }}</h4>
                  <span v-if="viewFilter === 'baseModels' && model.type === 'external_api'" class="model-count-badge">
                    ({{ model.instance_count || 1 }} minions)
                  </span>
                </div>
                <p class="model-size">{{ model.size || model.model_id || 'N/A' }}</p>
                <p v-if="viewFilter === 'baseModels' && model.type === 'external_api'" class="model-id">
                  {{ model.model_id }}
                </p>
                <div class="model-capabilities">
                  <span 
                    v-for="capability in model.capabilities" 
                    :key="capability"
                    class="capability-tag"
                  >
                    {{ capability }}
                  </span>
                </div>
              </div>
              <div class="selection-indicator">
                <span class="material-icons-round">{{ selectedModels.includes(getModelKey(model)) ? 'check_circle' : 'radio_button_unchecked' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Comparison Actions</h3>
            <div class="action-controls">
              <button 
                @click="loadComparisonData" 
                class="btn btn-sm btn-primary"
                :disabled="selectedModels.length === 0 || loading"
              >
                <span class="material-icons-round">compare_arrows</span>
                {{ loading ? 'Loading...' : 'Compare Models' }}
              </button>
              <button 
                @click="exportComparison" 
                class="btn btn-sm btn-outline-success"
                :disabled="comparisonData.length === 0"
              >
                <span class="material-icons-round">download</span>
                Export CSV
              </button>
            </div>
          </div>
          
          <div v-if="loading" class="loading-state">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading model details...</p>
          </div>

          <div v-else-if="comparisonData.length > 0" class="comparison-summary">
            <h4>Comparison Summary</h4>
            <div class="summary-stats">
              <div class="summary-item">
                <span class="label">Models Compared:</span>
                <span class="value">{{ comparisonData.length }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Total Parameters:</span>
                <span class="value">{{ getTotalParameters() }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Avg Context Length:</span>
                <span class="value">{{ getAvgContextLength() }}</span>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <span class="material-icons-round">compare_arrows</span>
            <p>Select models to compare their specifications and performance</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Table -->
    <div v-if="comparisonData.length > 0" class="neumorphic-card comparison-table-card">
      <div class="card-header">
        <h3>Detailed Comparison</h3>
        <div class="table-controls">
          <button 
            @click="refreshComparison" 
            class="btn btn-sm btn-outline-primary"
            :disabled="loading"
          >
            <span class="material-icons-round">refresh</span>
            Refresh
          </button>
        </div>
      </div>

      <div class="table-container">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>Base Model</th>
              <th>Level / Rank</th>
              <th>Experience</th>
              <th>Capabilities</th>
              <th>Parameters</th>
              <th>Context Length</th>
              <th>Temperature</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="model in comparisonData" :key="model.name">
              <td class="model-name-cell">
                <div class="model-name">
                  <div class="model-name-with-avatar">
                    <div class="model-avatar-small" v-if="model.minion_specific?.avatar_url || model.details.avatar_url">
                      <img :src="model.minion_specific?.avatar_url || model.details.avatar_url" :alt="model.name + ' avatar'" class="avatar-image-small">
                    </div>
                    <div class="model-avatar-placeholder-small" v-else>
                      <span class="material-icons-round">smart_toy</span>
                    </div>
                    <div class="model-name-text">
                      <strong>{{ model.name }}</strong>
                      <small v-if="model.minion_specific?.description" class="model-description-small">
                        {{ model.minion_specific.description.substring(0, 50) }}{{ model.minion_specific.description.length > 50 ? '...' : '' }}
                      </small>
                    </div>
                  </div>
                </div>
              </td>
              <td>
                <div class="base-model-info">
                  <span class="base-model-id">{{ model.base_model?.model_id || model.details.model_id || 'Unknown' }}</span>
                  <span class="base-model-provider" v-if="model.base_model?.provider">
                    ({{ model.base_model.provider }})
                  </span>
                </div>
              </td>
              <td>
                <div class="minion-stats">
                  <span class="stat-badge level">{{ model.minion_specific?.level || model.details.level || 1 }}</span>
                  <span class="stat-badge rank">{{ model.minion_specific?.rank || model.details.rank || 'Novice' }}</span>
                  <span v-if="model.minion_specific?.rank_level" class="stat-badge rank-level">
                    ({{ model.minion_specific.rank_level }}/5)
                  </span>
                </div>
              </td>
              <td>
                <div class="experience-info">
                  <span class="xp-value">{{ (model.minion_specific?.experience || model.details.experience || 0).toLocaleString() }} XP</span>
                  <div class="xp-breakdown" v-if="model.minion_specific">
                    <small>Training: {{ (model.minion_specific.total_training_xp || 0).toLocaleString() }}</small>
                    <small>Usage: {{ (model.minion_specific.total_usage_xp || 0).toLocaleString() }}</small>
                  </div>
                </div>
              </td>
              <td>
                <div class="capabilities-list">
                  <span 
                    v-for="capability in (model.minion_specific?.capabilities || model.details.capabilities || [])" 
                    :key="capability"
                    class="capability-badge"
                  >
                    {{ capability }}
                  </span>
                  <span v-if="(model.minion_specific?.capabilities || model.details.capabilities || []).length === 0" class="text-muted">
                    None
                  </span>
                </div>
              </td>
              <td>{{ model.base_model?.parameters || model.details.parameters || 'Unknown' }}</td>
              <td>{{ model.base_model?.context_length || model.details.context_length || 'Unknown' }}</td>
              <td>{{ model.base_model?.temperature || model.details.temperature || 'Unknown' }}</td>
              <td>
                <button 
                  @click="viewModelDetails(model)"
                  class="btn btn-sm btn-outline-primary"
                >
                  <span class="material-icons-round">visibility</span>
                  Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Performance Charts - Upgrade Metrics -->
    <div v-if="comparisonData.length > 1 && viewFilter === 'minions'" class="dashboard-row">
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Experience & Level Comparison</h3>
          </div>
          <div class="chart-container">
            <canvas ref="experienceChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>XP Breakdown (Training vs Usage)</h3>
          </div>
          <div class="chart-container">
            <canvas ref="xpBreakdownChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <div v-if="comparisonData.length > 1 && viewFilter === 'minions'" class="dashboard-row">
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Rank & Score Comparison</h3>
          </div>
          <div class="chart-container">
            <canvas ref="rankScoreChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Capabilities Count</h3>
          </div>
          <div class="chart-container">
            <canvas ref="capabilitiesCountChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Base Model Charts (for base models view) -->
    <div v-if="comparisonData.length > 1 && viewFilter === 'baseModels'" class="dashboard-row">
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Technical Specs Comparison</h3>
          </div>
          <div class="chart-container">
            <canvas ref="performanceChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Capabilities Overview</h3>
          </div>
          <div class="chart-container">
            <canvas ref="capabilitiesChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Details Modal -->
    <div v-if="selectedModelDetails" class="modal-overlay" @click.self="selectedModelDetails = null">
      <div class="modal model-details-modal">
        <div class="modal-header">
          <h2>Model Details</h2>
          <button class="btn-icon" @click="selectedModelDetails = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="model-details-content">
            <div class="detail-section">
              <h4>Basic Information</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="label">Name:</span>
                  <span class="value">{{ selectedModelDetails.name }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Architecture:</span>
                  <span class="value">{{ selectedModelDetails.details.architecture || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Parameters:</span>
                  <span class="value">{{ selectedModelDetails.details.parameters || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Context Length:</span>
                  <span class="value">{{ selectedModelDetails.details.context_length || 'Unknown' }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Configuration</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="label">Temperature:</span>
                  <span class="value">{{ selectedModelDetails.details.temperature || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Top P:</span>
                  <span class="value">{{ selectedModelDetails.details.top_p || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Quantization:</span>
                  <span class="value">{{ selectedModelDetails.details.quantization || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Embedding Length:</span>
                  <span class="value">{{ selectedModelDetails.details.embedding_length || 'Unknown' }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Capabilities</h4>
              <div class="capabilities-grid">
                <span 
                  v-for="capability in selectedModelDetails.details.capabilities" 
                  :key="capability"
                  class="capability-tag large"
                >
                  {{ capability }}
                </span>
              </div>
            </div>

            <div v-if="selectedModelDetails.details.system_prompt" class="detail-section">
              <h4>System Prompt</h4>
              <div class="system-prompt">
                <p>{{ selectedModelDetails.details.system_prompt }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { API_ENDPOINTS } from '@/config/api';

export default {
  name: 'ModelComparisonView',
  data() {
    return {
      availableModels: [],
      selectedModels: [],
      comparisonData: [],
      loading: false,
      selectedModelDetails: null,
      chartInstances: [],
      viewFilter: 'minions' // 'minions' or 'baseModels'
    };
  },
  computed: {
    uniqueCapabilities() {
      const capabilities = new Set();
      this.comparisonData.forEach(model => {
        model.details.capabilities?.forEach(capability => {
          capabilities.add(capability);
        });
      });
      return Array.from(capabilities);
    },
    
    filteredModels() {
      if (this.viewFilter === 'minions') {
        // Show all minions (external_api models)
        return this.availableModels.filter(model => model.type === 'external_api');
      } else {
        // Show base models (deduplicated by model_id)
        const baseModelMap = new Map();
        
        this.availableModels.forEach(model => {
          let key;
          if (model.type === 'ollama') {
            // Ollama models use name as key
            key = model.name || model.ollama_name;
            if (!baseModelMap.has(key)) {
              baseModelMap.set(key, {
                ...model,
                instance_count: 1,
                display_name: model.name
              });
            }
          } else if (model.type === 'external_api') {
            // External API models use model_id as key
            key = model.model_id || model.name;
            if (!baseModelMap.has(key)) {
              baseModelMap.set(key, {
                ...model,
                instance_count: 1,
                // Use the most used/experienced instance as the representative
                display_name: model.model_id || model.name
              });
            } else {
              // Increment instance count
              const existing = baseModelMap.get(key);
              existing.instance_count++;
              // Update if this instance has more XP/usage
              if ((model.total_usage_xp || 0) + (model.total_training_xp || 0) > 
                  (existing.total_usage_xp || 0) + (existing.total_training_xp || 0)) {
                baseModelMap.set(key, {
                  ...existing,
                  ...model,
                  instance_count: existing.instance_count,
                  display_name: model.model_id || model.name
                });
              }
            }
          }
        });
        
        return Array.from(baseModelMap.values());
      }
    }
  },
  watch: {
    viewFilter() {
      // Clear selection when filter changes since we're showing different models
      this.selectedModels = [];
      this.comparisonData = [];
    }
  },
  async mounted() {
    await this.loadAvailableModels();
  },
  beforeUnmount() {
    // Cleanup chart instances
    this.chartInstances.forEach(chart => {
      if (chart && typeof chart.dispose === 'function') {
        chart.dispose();
      }
    });
    this.chartInstances = [];
  },
  methods: {
    async loadAvailableModels() {
      try {
        const response = await fetch(API_ENDPOINTS.v2.models);
        const data = await response.json();
        
        if (data.success) {
          // Parse capabilities from JSON string to array if needed
          this.availableModels = data.models.map(model => ({
            ...model,
            capabilities: this.getCapabilitiesArray(model.capabilities || [])
          }));
        } else {
          console.error('Failed to load models:', data.error);
        }
      } catch (error) {
        console.error('Error loading models:', error);
      }
    },
    
    toggleModelSelection(modelName) {
      const index = this.selectedModels.indexOf(modelName);
      if (index > -1) {
        this.selectedModels.splice(index, 1);
      } else {
        this.selectedModels.push(modelName);
      }
      // Clear comparison data when selection changes
      this.comparisonData = [];
    },
    
    selectAllModels() {
      this.selectedModels = this.filteredModels.map(model => this.getModelKey(model));
    },
    
    clearSelection() {
      this.selectedModels = [];
      this.comparisonData = [];
    },
    
    async loadComparisonData() {
      if (this.selectedModels.length === 0) return;
      
      this.loading = true;
      this.comparisonData = [];
      
      try {
        // Fetch all models first
        const response = await fetch(API_ENDPOINTS.v2.models);
        const data = await response.json();
        
        if (data.success) {
          // Filter to only selected models and get their details
          // Match based on the key used for selection
          this.comparisonData = data.models
            .filter(model => {
              if (this.viewFilter === 'minions') {
                // In minions view, match by display_name or id
                return this.selectedModels.includes(model.display_name) || 
                       this.selectedModels.includes(`minion-${model.id}`);
              } else {
                // In base models view, match by name (Ollama) or model_id (external API)
                if (model.type === 'ollama') {
                  return this.selectedModels.includes(model.name || model.ollama_name);
                } else {
                  return this.selectedModels.includes(model.model_id || model.name);
                }
              }
            })
            .map(model => ({
              name: model.display_name || model.name,
              // Minion-specific data (varies per minion)
              minion_specific: {
                display_name: model.display_name,
                description: model.description || '',
                system_prompt: model.system_prompt || '',
                experience: model.experience || 0,
                level: model.level || 1,
                rank: model.rank || 'Novice',
                rank_level: model.rank_level || 1,
                total_training_xp: model.total_training_xp || 0,
                total_usage_xp: model.total_usage_xp || 0,
                score: model.score || 0,
                capabilities: this.getCapabilitiesArray(model.capabilities || []), // Can be customized per minion
                avatar_url: model.avatar_url,
                tags: model.tags || []
              },
              // Base model data (shared if same base model)
              base_model: {
                model_id: model.model_id || model.name,
                architecture: model.architecture || 'Unknown',
                parameters: model.parameters || 'Unknown',
                context_length: model.context_length || 'Unknown',
                embedding_length: model.embedding_length || 'Unknown',
                quantization: model.quantization || 'Unknown',
                temperature: model.temperature || 'Unknown',
                top_p: model.top_p || 'Unknown',
                license: model.license || 'Unknown',
                modified: model.modified || 'Unknown',
                size: model.size || 'Unknown',
                provider: model.provider || 'Unknown',
                type: model.type || 'Unknown'
              },
              // For backward compatibility, also include in details
              details: {
                architecture: model.architecture || 'Unknown',
                parameters: model.parameters || 'Unknown',
                context_length: model.context_length || 'Unknown',
                embedding_length: model.embedding_length || 'Unknown',
                quantization: model.quantization || 'Unknown',
                temperature: model.temperature || 'Unknown',
                top_p: model.top_p || 'Unknown',
                capabilities: this.getCapabilitiesArray(model.capabilities || []),
                system_prompt: model.system_prompt || '',
                license: model.license || 'Unknown',
                modified: model.modified || 'Unknown',
                size: model.size || model.model_id || 'Unknown',
                model_id: model.model_id,
                provider: model.provider,
                type: model.type,
                // Add minion-specific fields
                experience: model.experience || 0,
                level: model.level || 1,
                rank: model.rank || 'Novice',
                description: model.description || ''
              }
            }));
          
          console.log('📊 Loaded comparison data:', this.comparisonData);
          
          // Initialize charts after data is loaded
          this.$nextTick(() => {
            this.initCharts();
          });
        } else {
          console.error('Failed to load models:', data.error);
        }
        
      } catch (error) {
        console.error('Error loading comparison data:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async refreshComparison() {
      await this.loadComparisonData();
    },
    
    exportComparison() {
      if (this.comparisonData.length === 0) return;
      
      const csvContent = this.generateCSV();
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `model-comparison-${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    },
    
    generateCSV() {
      const headers = [
        'Model', 'Parameters', 'Context Length', 'Embedding Length', 'Quantization',
        'Temperature', 'Top P', 'Architecture', 'Capabilities'
      ];
      
      const rows = this.comparisonData.map(model => [
        model.name,
        model.details.parameters || 'Unknown',
        model.details.context_length || 'Unknown',
        model.details.embedding_length || 'Unknown',
        model.details.quantization || 'Unknown',
        model.details.temperature || 'Unknown',
        model.details.top_p || 'Unknown',
        model.details.architecture || 'Unknown',
        (model.details.capabilities || []).join('; ')
      ]);
      
      const csvContent = [headers, ...rows]
        .map(row => row.map(cell => `"${cell}"`).join(','))
        .join('\n');
      
      return csvContent;
    },
    
    getCapabilitiesArray(capabilities) {
      // Handle both string (JSON) and array formats
      if (!capabilities) return [];
      if (Array.isArray(capabilities)) return capabilities;
      if (typeof capabilities === 'string') {
        try {
          const parsed = JSON.parse(capabilities);
          return Array.isArray(parsed) ? parsed : [];
        } catch (e) {
          // If not valid JSON, treat as comma-separated string
          return capabilities.split(',').map(c => c.trim()).filter(c => c);
        }
      }
      return [];
    },
    
    getModelKey(model) {
      // For minions view, use display_name (unique per minion) or id as key
      // For base models view, use name (for Ollama) or model_id (for external API)
      if (this.viewFilter === 'minions') {
        // In minions view, use display_name or id to ensure uniqueness
        return model.display_name || `minion-${model.id}` || model.name;
      } else {
        // In base models view, use name for Ollama or model_id for external API
        if (model.type === 'ollama') {
          return model.name || model.ollama_name;
        } else {
          return model.model_id || model.name;
        }
      }
    },
    
    viewModelDetails(model) {
      this.selectedModelDetails = model;
      console.log('📋 Viewing model details:', model);
    },
    
    getTotalParameters() {
      return this.comparisonData.reduce((total, model) => {
        const params = model.details.parameters;
        if (params && params.includes('B')) {
          const num = parseFloat(params);
          return total + (num * 1000000000); // Convert B to actual number
        }
        return total;
      }, 0);
    },
    
    getAvgContextLength() {
      const validLengths = this.comparisonData
        .map(model => parseInt(model.details.context_length))
        .filter(length => !isNaN(length));
      
      if (validLengths.length === 0) return 'Unknown';
      return Math.round(validLengths.reduce((a, b) => a + b, 0) / validLengths.length).toLocaleString();
    },
    
    initCharts() {
      // Dispose existing charts first
      this.chartInstances.forEach(chart => {
        if (chart && typeof chart.dispose === 'function') {
          chart.dispose();
        }
      });
      this.chartInstances = [];
      
      if (this.viewFilter === 'minions') {
        // Show upgrade-based performance charts for minions
        this.$nextTick(() => {
          this.createExperienceChart();
          this.createXPBreakdownChart();
          this.createRankScoreChart();
          this.createCapabilitiesCountChart();
        });
      } else {
        // Show base model specs for base models view
        this.$nextTick(() => {
          this.createPerformanceChart();
          this.createCapabilitiesChart();
        });
      }
    },
    
    createPerformanceChart() {
      const canvas = this.$refs.performanceChart;
      if (!canvas || this.comparisonData.length < 2) return;
      
      // Set high DPI canvas
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        useDirtyRect: false
      });
      
      const modelNames = this.comparisonData.map(model => model.name);
      const contextLengths = this.comparisonData.map(model => {
        const length = parseInt(model.details.context_length);
        return isNaN(length) ? 0 : length;
      });
      
      const option = {
        title: {
          text: 'Context Length Comparison',
          left: 'center',
          textStyle: {
            color: '#333',
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: modelNames,
          axisLabel: {
            rotate: 45,
            fontSize: 10
          }
        },
        yAxis: {
          type: 'value',
          name: 'Context Length'
        },
        series: [{
          name: 'Context Length',
          type: 'bar',
          data: contextLengths,
          itemStyle: {
            color: '#4e73df'
          }
        }]
      };
      
      chart.setOption(option);
      this.chartInstances.push(chart);
    },
    
    createExperienceChart() {
      const canvas = this.$refs.experienceChart;
      if (!canvas || this.comparisonData.length < 2) return;
      
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        useDirtyRect: false
      });
      
      const modelNames = this.comparisonData.map(model => model.name);
      const experiences = this.comparisonData.map(model => 
        model.minion_specific?.experience || model.details.experience || 0
      );
      const levels = this.comparisonData.map(model => 
        model.minion_specific?.level || model.details.level || 1
      );
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        legend: {
          data: ['Experience (XP)', 'Level'],
          top: 10
        },
        xAxis: {
          type: 'category',
          data: modelNames,
          axisLabel: { rotate: 45, fontSize: 10 }
        },
        yAxis: [
          {
            type: 'value',
            name: 'Experience (XP)',
            position: 'left',
            axisLabel: { formatter: '{value}' }
          },
          {
            type: 'value',
            name: 'Level',
            position: 'right',
            max: 35
          }
        ],
        series: [
          {
            name: 'Experience (XP)',
            type: 'bar',
            yAxisIndex: 0,
            data: experiences,
            itemStyle: { color: '#4e73df' },
            label: {
              show: true,
              formatter: (params) => params.value.toLocaleString()
            }
          },
          {
            name: 'Level',
            type: 'line',
            yAxisIndex: 1,
            data: levels,
            itemStyle: { color: '#1cc88a' },
            lineStyle: { width: 3 },
            symbol: 'circle',
            symbolSize: 8,
            label: {
              show: true,
              formatter: 'Lv.{value}'
            }
          }
        ]
      };
      
      chart.setOption(option);
      this.chartInstances.push(chart);
    },
    
    createXPBreakdownChart() {
      const canvas = this.$refs.xpBreakdownChart;
      if (!canvas || this.comparisonData.length < 2) return;
      
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        useDirtyRect: false
      });
      
      const modelNames = this.comparisonData.map(model => model.name);
      const trainingXP = this.comparisonData.map(model => 
        model.minion_specific?.total_training_xp || 0
      );
      const usageXP = this.comparisonData.map(model => 
        model.minion_specific?.total_usage_xp || 0
      );
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: {
          data: ['Training XP', 'Usage XP'],
          top: 10
        },
        xAxis: {
          type: 'category',
          data: modelNames,
          axisLabel: { rotate: 45, fontSize: 10 }
        },
        yAxis: {
          type: 'value',
          name: 'Experience Points'
        },
        series: [
          {
            name: 'Training XP',
            type: 'bar',
            stack: 'XP',
            data: trainingXP,
            itemStyle: { color: '#f39c12' }
          },
          {
            name: 'Usage XP',
            type: 'bar',
            stack: 'XP',
            data: usageXP,
            itemStyle: { color: '#e74c3c' }
          }
        ]
      };
      
      chart.setOption(option);
      this.chartInstances.push(chart);
    },
    
    createRankScoreChart() {
      const canvas = this.$refs.rankScoreChart;
      if (!canvas || this.comparisonData.length < 2) return;
      
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        useDirtyRect: false
      });
      
      const modelNames = this.comparisonData.map(model => model.name);
      const scores = this.comparisonData.map(model => 
        model.minion_specific?.score || 0
      );
      
      // Rank to numeric for visualization
      const rankValues = this.comparisonData.map(model => {
        const rank = model.minion_specific?.rank || model.details.rank || 'Novice';
        const rankMap = {
          'Novice': 1, 'Skilled': 2, 'Expert': 3, 'Master': 4, 'Grandmaster': 5, 'Legendary': 6
        };
        return rankMap[rank] || 1;
      });
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        legend: {
          data: ['Score', 'Rank (numeric)'],
          top: 10
        },
        xAxis: {
          type: 'category',
          data: modelNames,
          axisLabel: { rotate: 45, fontSize: 10 }
        },
        yAxis: [
          {
            type: 'value',
            name: 'Score',
            position: 'left'
          },
          {
            type: 'value',
            name: 'Rank',
            position: 'right',
            min: 0,
            max: 6
          }
        ],
        series: [
          {
            name: 'Score',
            type: 'bar',
            yAxisIndex: 0,
            data: scores,
            itemStyle: { color: '#9b59b6' },
            label: {
              show: true,
              formatter: '{value}'
            }
          },
          {
            name: 'Rank (numeric)',
            type: 'line',
            yAxisIndex: 1,
            data: rankValues,
            itemStyle: { color: '#e67e22' },
            lineStyle: { width: 3 },
            symbol: 'diamond',
            symbolSize: 10,
            label: {
              show: true,
              formatter: (params) => {
                const rankMap = ['', 'Novice', 'Skilled', 'Expert', 'Master', 'Grandmaster', 'Legendary'];
                return rankMap[params.value] || '';
              }
            }
          }
        ]
      };
      
      chart.setOption(option);
      this.chartInstances.push(chart);
    },
    
    createCapabilitiesCountChart() {
      const canvas = this.$refs.capabilitiesCountChart;
      if (!canvas || this.comparisonData.length < 2) return;
      
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        useDirtyRect: false
      });
      
      const modelNames = this.comparisonData.map(model => model.name);
      const capabilityCounts = this.comparisonData.map(model => {
        const caps = model.minion_specific?.capabilities || model.details.capabilities || [];
        return caps.length;
      });
      
      // Store reference for tooltip formatter
      const comparisonDataRef = this.comparisonData;
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params) => {
            if (!params || !params[0]) return '';
            const dataIndex = params[0].dataIndex;
            const model = comparisonDataRef[dataIndex];
            const caps = model?.minion_specific?.capabilities || model?.details?.capabilities || [];
            return `${params[0].name}<br/>${params[0].marker} Capabilities: ${params[0].value}<br/>${caps.join(', ') || 'None'}`;
          }
        },
        xAxis: {
          type: 'category',
          data: modelNames,
          axisLabel: { rotate: 45, fontSize: 10 }
        },
        yAxis: {
          type: 'value',
          name: 'Number of Capabilities',
          minInterval: 1
        },
        series: [{
          name: 'Capabilities',
          type: 'bar',
          data: capabilityCounts,
          itemStyle: {
            color: (params) => {
              // Color based on count: more capabilities = better color
              const colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6'];
              return colors[Math.min(params.value - 1, colors.length - 1)] || '#95a5a6';
            }
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{value}'
          }
        }]
      };
      
      chart.setOption(option);
      this.chartInstances.push(chart);
    },
    
    createCapabilitiesChart() {
      const canvas = this.$refs.capabilitiesChart;
      if (!canvas || this.comparisonData.length < 2) return;
      
      // Set high DPI canvas
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        useDirtyRect: false
      });
      
      // Count capabilities across all models
      const capabilityCount = {};
      this.comparisonData.forEach(model => {
        model.details.capabilities?.forEach(capability => {
          capabilityCount[capability] = (capabilityCount[capability] || 0) + 1;
        });
      });
      
      const data = Object.entries(capabilityCount).map(([capability, count]) => ({
        name: capability,
        value: count
      }));
      
      const option = {
        title: {
          text: 'Capabilities Distribution',
          left: 'center',
          textStyle: {
            color: '#333',
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [{
          name: 'Capabilities',
          type: 'pie',
          radius: '60%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      };
      
      chart.setOption(option);
      this.chartInstances.push(chart);
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.page-header p {
  color: #666;
  margin: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dashboard-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dashboard-col {
  display: flex;
  flex-direction: column;
}

.neumorphic-card {
  background: #f0f0f3;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 
    20px 20px 60px #bebebe,
    -20px -20px 60px #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex: 1;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1.5rem;
}

.stats-icon.training {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.dataset {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.accuracy {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-info h3 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.stats-info p {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.card-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.selection-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.btn-group {
  display: flex;
  gap: 0;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #dee2e6;
}

.btn-group .btn {
  border-radius: 0;
  border-left: none;
  border-right: none;
  white-space: nowrap;
}

.btn-group .btn:first-child {
  border-left: 1px solid #dee2e6;
  border-top-left-radius: 6px;
  border-bottom-left-radius: 6px;
}

.btn-group .btn:last-child {
  border-right: 1px solid #dee2e6;
  border-top-right-radius: 6px;
  border-bottom-right-radius: 6px;
}

.action-controls,
.table-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.model-count-badge {
  font-size: 0.75rem;
  color: #666;
  font-weight: normal;
  margin-left: 0.5rem;
}

.model-id {
  font-size: 0.75rem;
  color: #888;
  font-family: monospace;
  margin-top: 0.25rem;
}

.model-selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.model-selection-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-selection-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.model-selection-card.selected {
  border-color: #4e73df;
  background: linear-gradient(135deg, rgba(78, 115, 223, 0.1) 0%, rgba(78, 115, 223, 0.05) 100%);
}

.model-header-with-avatar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.model-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.model-avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-color, #4e73df);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.model-avatar-placeholder .material-icons-round {
  font-size: 20px;
}

.model-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.model-size {
  font-size: 0.85rem;
  color: #666;
  margin: 0 0 0.5rem 0;
}

.model-capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.capability-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.capability-tag.large {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
}

.selection-indicator {
  color: #4e73df;
  font-size: 1.25rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
  border: 0.25rem solid #f3f3f3;
  border-top: 0.25rem solid #4e73df;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.comparison-summary {
  padding: 1rem;
}

.comparison-summary h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-item .label {
  color: #666;
  font-size: 0.9rem;
}

.summary-item .value {
  color: #333;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.empty-state .material-icons-round {
  font-size: 3rem;
  color: #ccc;
  margin-bottom: 1rem;
}

.comparison-table-card {
  margin-top: 1.5rem;
}

.table-container {
  overflow-x: auto;
  border-radius: 12px;
  background: white;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.comparison-table th {
  background: #f8f9fa;
  padding: 1rem 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
}

.comparison-table td {
  padding: 1rem 0.75rem;
  border-bottom: 1px solid #dee2e6;
  vertical-align: top;
}

.comparison-table tr:hover {
  background: #f8f9fa;
}

.model-name-cell {
  min-width: 150px;
}

.model-name-with-avatar {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.model-name-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.model-description-small {
  font-size: 0.75rem;
  color: #666;
  font-weight: normal;
  display: block;
  line-height: 1.3;
}

.base-model-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.base-model-id {
  font-family: monospace;
  font-size: 0.875rem;
  color: #333;
  font-weight: 500;
}

.base-model-provider {
  font-size: 0.75rem;
  color: #666;
}

.minion-stats {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-start;
}

.stat-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-badge.level {
  background-color: #e3f2fd;
  color: #1976d2;
}

.stat-badge.rank {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.stat-badge.rank-level {
  background-color: #fff3e0;
  color: #e65100;
  font-size: 0.7rem;
}

.experience-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.xp-value {
  font-weight: 600;
  color: #2e7d32;
  font-size: 0.9rem;
}

.xp-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  font-size: 0.7rem;
  color: #666;
}

.xp-breakdown small {
  display: block;
}

.model-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.avatar-image-small {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.model-avatar-placeholder-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary-color, #4e73df);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.model-avatar-placeholder-small .material-icons-round {
  font-size: 12px;
}

.model-name-text {
  flex: 1;
}

.model-name strong {
  color: #333;
  font-size: 0.95rem;
}

.model-name small {
  color: #666;
  display: block;
  margin-top: 0.25rem;
}

.capabilities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.capability-badge {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
}

.chart-container {
  height: 300px;
  position: relative;
  margin: 0 -1rem -1rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  border-radius: 12px;
  padding: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
  border-radius: 8px;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}

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

.model-details-modal {
  background: white;
  border-radius: 20px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #666;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.model-details-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item .label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.detail-item .value {
  font-size: 0.95rem;
  color: #333;
  font-weight: 600;
}

.capabilities-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.system-prompt {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #4e73df;
}

.system-prompt p {
  margin: 0;
  color: #333;
  line-height: 1.5;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

.btn-primary {
  background: #4e73df;
  color: white;
}

.btn-primary:hover {
  background: #3c5bd1;
}

.btn-outline-primary {
  background: transparent;
  color: #4e73df;
  border: 1px solid #4e73df;
}

.btn-outline-primary:hover {
  background: #4e73df;
  color: white;
}

.btn-outline-secondary {
  background: transparent;
  color: #666;
  border: 1px solid #ddd;
}

.btn-outline-secondary:hover {
  background: #666;
  color: white;
}

.btn-outline-success {
  background: transparent;
  color: #28a745;
  border: 1px solid #28a745;
}

.btn-outline-success:hover {
  background: #28a745;
  color: white;
}

.material-icons-round {
  font-family: 'Material Icons Round';
  font-weight: normal;
  font-style: normal;
  font-size: 1rem;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
}
</style>