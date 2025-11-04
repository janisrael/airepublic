<template>
  <div v-if="visible" class="modal-overlay" @click.self="closeModal">
    <div class="modal minion-history-modal">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-content">
          <h2>
            <span class="material-icons-round">history</span>
            {{ minionName }} - Training History
          </h2>
          <p class="header-subtitle">Track your minion's growth and improvements over time</p>
        </div>
        <button class="btn-icon close-btn" @click="closeModal">
          <span class="material-icons-round">close</span>
        </button>
      </div>
      
      <!-- Body -->
      <div class="modal-body">
        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading training history...</p>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="history.length === 0" class="empty-state">
          <div class="empty-icon">
            <span class="material-icons-round">timeline</span>
          </div>
          <h3>No Training History</h3>
          <p class="empty-details">This minion hasn't been trained yet. Start a training job to see the history here.</p>
        </div>
        
        <!-- Timeline Content -->
        <div v-else class="timeline-content">
          <!-- Stats Dashboard -->
          <div class="stats-dashboard">
            <div class="stat-card">
              <div class="stat-icon total">
                <span class="material-icons-round">military_tech</span>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ history.length }}</span>
                <span class="stat-label">Total Trainings</span>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon success">
                <span class="material-icons-round">check_circle</span>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ successfulTrainings }}</span>
                <span class="stat-label">Successful</span>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon error">
                <span class="material-icons-round">error</span>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ failedTrainings }}</span>
                <span class="stat-label">Failed</span>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon date">
                <span class="material-icons-round">schedule</span>
              </div>
              <div class="stat-info">
                <span class="stat-value small">{{ lastTrainingDate }}</span>
                <span class="stat-label">Last Training</span>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon level">
                <span class="material-icons-round">military_tech</span>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ minionData.level || 1 }}</span>
                <span class="stat-label">Level</span>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon rank">
                <span class="material-icons-round">emoji_events</span>
              </div>
              <div class="stat-info">
                <span class="stat-value small">{{ minionData.rank || 'Novice' }}</span>
                <span class="stat-label">Rank</span>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon xp">
                <span class="material-icons-round">star</span>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ (minionData.total_training_xp || 0) + (minionData.total_usage_xp || 0) }}</span>
                <span class="stat-label">Total XP</span>
              </div>
            </div>
          </div>

          <div class="timeline-section">
            <Timeline :value="history" align="left" class="custom-timeline">
              <template #content="slotProps">
                <div class="timeline-card full" :class="(slotProps.item.status || '').toLowerCase()">
                  <div class="row no-gutters">
                    <!-- Left: Details -->
                    <div class="col-12 col-md-4 p-3">
                      <div class="card-header">
                        <h3 class="mb-1">{{ slotProps.item.job_name || 'Training Job' }}</h3>
                        <div class="card-time-info mb-2">
                          <span class="material-icons-round">schedule</span>
                          {{ formatDate(slotProps.item.created_at) }}
                        </div>
                      </div>

                      <p v-if="slotProps.item.description" class="mb-2">{{ slotProps.item.description }}</p>

                      <div class="detail-row mb-2">
                        <span class="material-icons-round">memory</span>
                        <div class="detail-content">
                          <span class="detail-label">Provider</span>
                          <span class="detail-value">{{ slotProps.item.provider || '—' }}</span>
                        </div>
                      </div>

                      <div class="detail-row mb-2">
                        <span class="material-icons-round">model_training</span>
                        <div class="detail-content">
                          <span class="detail-label">Model</span>
                          <span class="detail-value">{{ slotProps.item.model_name || slotProps.item.model || '—' }}</span>
                        </div>
                      </div>

                      <div class="training-data-section mt-2" v-if="getDatasetNames(slotProps.item).length > 0">
                        <div class="training-data-header"><span class="material-icons-round">dataset</span> Training Data</div>
                        <div class="dataset-chips mt-2">
                          <span v-for="dataset in getDatasetNames(slotProps.item)" :key="dataset.id" class="dataset-chip">{{ dataset.name }}</span>
                        </div>
                      </div>

                      <div class="mt-3">
                        <button class="btn btn-outline" @click.prevent="viewDetails(slotProps.item)"><span class="material-icons-round">visibility</span> View Details</button>
                      </div>
                    </div>

                    <!-- Middle: Improvements / Summary -->
                    <div class="col-12 col-md-4 p-3 border-left">
                      <div class="improvements-header mb-2">
                        <span class="material-icons-round">upgrade</span>
                        <strong class="ml-2">Upgrades & Improvements</strong>
                      </div>

                      <div class="improvements-grid">
                        <div class="improvement-item" v-if="slotProps.item.improvements">
                          <div class="improvement-info">
                            <span class="improvement-label">Knowledge</span>
                            <span class="improvement-value">{{ formatImprovement(slotProps.item.improvements.knowledge) }}</span>
                          </div>
                        </div>
                        <div class="improvement-item" v-if="slotProps.item.improvements">
                          <div class="improvement-info">
                            <span class="improvement-label">Accuracy</span>
                            <span class="improvement-value">{{ formatImprovement(slotProps.item.improvements.accuracy) }}</span>
                          </div>
                        </div>
                        <div class="improvement-item" v-if="slotProps.item.improvements">
                          <div class="improvement-info">
                            <span class="improvement-label">Speed</span>
                            <span class="improvement-value">{{ formatImprovement(slotProps.item.improvements.speed) }}</span>
                          </div>
                        </div>
                        <div class="improvement-item" v-if="slotProps.item.improvements">
                          <div class="improvement-info">
                            <span class="improvement-label">Context</span>
                            <span class="improvement-value">{{ formatImprovement(slotProps.item.improvements.context_understanding) }}</span>
                          </div>
                        </div>
                      </div>

                      <div class="mt-3">
                        <div><strong>XP Gained:</strong> {{ slotProps.item.xp_gained || slotProps.item.summary?.xp_gained || 0 }}</div>
                        <div><strong>Overall:</strong> {{ slotProps.item.overall_improvement ? (slotProps.item.overall_improvement + '%') : '--' }}</div>
                      </div>
                    </div>

                    <!-- Right: Charts -->
                    <div class="col-12 col-md-4 p-3 border-left">
                      <div class="chart-header mb-2"><span class="material-icons-round">bar_chart</span> Performance Metrics</div>

                      <div class="chart-grid">
                        <div :id="'progress-chart-' + (slotProps.item.id || slotProps.item.job_id)" class="mini-chart" style="height:120px; margin-bottom:12px;"></div>
                        <div :id="'improvement-chart-' + (slotProps.item.id || slotProps.item.job_id)" class="mini-chart" style="height:120px; margin-bottom:12px;"></div>
                        <div :id="'stats-chart-' + (slotProps.item.id || slotProps.item.job_id)" class="mini-chart" style="height:120px; margin-bottom:12px;"></div>
                        <div :id="'overtime-chart-' + (slotProps.item.id || slotProps.item.job_id)" class="mini-chart" style="height:120px;"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </Timeline>
          </div>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeModal">
          <span class="material-icons-round">close</span>
          Close
        </button>
        <button class="btn btn-primary" @click="exportHistory" v-if="history.length > 0">
          <span class="material-icons-round">file_download</span>
          Export History
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { API_ENDPOINTS, getUserEndpoint } from '@/config/api'
import DetailedStatsView from './DetailedStatsView.vue';

export default {
  name: 'MinionHistory',
  components: {
    DetailedStatsView
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    minionId: {
      type: [Number, String],
      required: false,
      default: null
    },
    minionName: {
      type: String,
      default: 'Minion'
    }
  },
  data() {
    return {
      history: [],
      loading: false,
      hasFetched: false,
      selectedChartType: 'all',
      chartInstances: {},
      minionData: {}
    }
  },
  computed: {
    successfulTrainings() {
      return this.history.filter(item => item.status === 'COMPLETED').length
    },
    failedTrainings() {
      return this.history.filter(item => item.status === 'FAILED').length
    },
    lastTrainingDate() {
      if (this.history.length === 0) return 'Never'
      const lastItem = this.history[0]
      return this.formatDateShort(lastItem.started_at || lastItem.created_at)
    }
  },
  methods: {
    async fetchHistory() {
      if (!this.minionId) return
      
      this.loading = true
      console.log('🔄 Fetching history for minion:', this.minionId)
      
      try {
        // Use configured API endpoint (V2) for minion training history
        const response = await fetch(`${API_ENDPOINTS.v2.minions}/${this.minionId}/training-history`)
        const result = await response.json()

        console.log('📊 History API response:', result)

        if (result && result.success) {
          // Some endpoints return 'training_history' and 'total_training_sessions'
          const historyArray = result.training_history || result.trainingHistory || []

          // Try to populate minionData from first history item if available
          if (historyArray.length > 0) {
            this.minionData = historyArray[0].after_metrics?.minion_stats || {}
          } else {
            this.minionData = {}
          }

          // Sort by created_at DESC (newest first)
          this.history = historyArray.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

          // Initialize charts after data is loaded
          await this.$nextTick()
          this.initializeCharts()
        } else {
          console.error('Failed to fetch minion history:', result?.error || 'Unknown error')
          this.history = []
        }
      } catch (error) {
        console.error('Error fetching minion history:', error)
        this.history = []
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      const date = new Date(dateString)
      return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    formatDateShort(dateString) {
      if (!dateString) return 'Unknown'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric'
      })
    },

    calculateDuration(start, end) {
      if (!start || !end) return 'N/A'
      const startDate = new Date(start)
      const endDate = new Date(end)
      const diff = endDate - startDate
      const minutes = Math.floor(diff / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)
      return `${minutes}m ${seconds}s`
    },

    getDatasetNames(item) {
      try {
        if (!item.config) return []
        const config = typeof item.config === 'string' ? JSON.parse(item.config) : item.config
        return config.datasetNames || []
      } catch (e) {
        return []
      }
    },

    hasImprovements(item) {
      if (!item.improvements) return false
      const imp = item.improvements
      return imp.knowledge !== 0 || imp.accuracy !== 0 || imp.speed !== 0 || imp.context_understanding !== 0
    },
     
    viewDetails(item) {
      alert(`Training Details for: ${item.job_name}\nStatus: ${item.status}\nProgress: ${Math.round(item.progress * 100)}%`)
    },

    downloadLogs(item) {
      alert(`Downloading logs for: ${item.job_name}`)
    },

    exportHistory() {
      const dataStr = JSON.stringify(this.history, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${this.minionName}_training_history.json`
      link.click()
      URL.revokeObjectURL(url)
    },
    
    closeModal() {
      this.$emit('close')
      // Dispose all chart instances
      Object.values(this.chartInstances).forEach(chart => {
        if (chart) chart.dispose()
      })
      this.chartInstances = {}
    },

    async initializeCharts() {
      // Dispose all existing charts first
      Object.values(this.chartInstances).forEach(chart => {
        if (chart) chart.dispose()
      })
      this.chartInstances = {}
      
      await this.$nextTick()
      
      console.log('📊 Initializing charts, type:', this.selectedChartType)
      
      this.history.forEach(item => {
        if (item.status === 'COMPLETED' && item.improvements) {
          console.log('📈 Rendering charts for item:', item.job_name)
          this.renderCharts(item)
        }
      })
    },

    renderCharts(item) {
      if (this.selectedChartType === 'all') {
        this.renderProgressChart(item)
        this.renderImprovementChart(item)
        this.renderStatsChart(item)
        this.renderOvertimeChart(item)
      } else {
        this.renderSingleChart(item, this.selectedChartType)
      }
    },

    renderProgressChart(item) {
      const chartId = `progress-chart-${item.id}`
      const dom = document.getElementById(chartId)
      if (!dom) return
      
      const chart = echarts.init(dom)
      this.chartInstances[chartId] = chart
      
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['Start', '25%', '50%', '75%', 'Complete'] },
        yAxis: { type: 'value', max: 100 },
        series: [{
          data: [0, 25, 50, 75, 100],
          type: 'line',
          smooth: true,
          itemStyle: { color: '#667eea' },
          areaStyle: { color: 'rgba(102, 126, 234, 0.2)' }
        }]
      })
    },

    renderImprovementChart(item) {
      const chartId = `improvement-chart-${item.id}`
      const dom = document.getElementById(chartId)
      if (!dom) return
      
      const chart = echarts.init(dom)
      this.chartInstances[chartId] = chart
      
      const imp = item.improvements
      chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        xAxis: { type: 'category', data: ['Knowledge', 'Accuracy', 'Speed', 'Context'] },
        yAxis: { type: 'value' },
        series: [{
          data: [imp.knowledge, imp.accuracy, imp.speed, imp.context_understanding],
          type: 'bar',
          itemStyle: {
            color: (params) => {
              const colors = ['#667eea', '#38ef7d', '#fee140', '#4facfe']
              return colors[params.dataIndex]
            }
          }
        }]
      })
    },

    renderStatsChart(item) {
      const chartId = `stats-chart-${item.id}`
      const dom = document.getElementById(chartId)
      if (!dom) return
      
      const chart = echarts.init(dom)
      this.chartInstances[chartId] = chart
      
      chart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: [
            { value: 30, name: 'Data Loading', itemStyle: { color: '#667eea' } },
            { value: 50, name: 'Training', itemStyle: { color: '#38ef7d' } },
            { value: 15, name: 'Validation', itemStyle: { color: '#fee140' } },
            { value: 5, name: 'Finalization', itemStyle: { color: '#ff6a00' } }
          ]
        }]
      })
    },

    renderOvertimeChart(item) {
      const chartId = `overtime-chart-${item.id}`
      const dom = document.getElementById(chartId)
      if (!dom) return
      
      const chart = echarts.init(dom)
      this.chartInstances[chartId] = chart
      
      const imp = item.improvements
      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['Knowledge', 'Accuracy', 'Speed', 'Context'] },
        xAxis: { type: 'category', data: ['V1', 'V2 (Current)'] },
        yAxis: { type: 'value' },
        series: [
          { name: 'Knowledge', type: 'line', data: [0, imp.knowledge], itemStyle: { color: '#667eea' } },
          { name: 'Accuracy', type: 'line', data: [0, imp.accuracy], itemStyle: { color: '#38ef7d' } },
          { name: 'Speed', type: 'line', data: [0, imp.speed], itemStyle: { color: '#fee140' } },
          { name: 'Context', type: 'line', data: [0, imp.context_understanding], itemStyle: { color: '#4facfe' } }
        ]
      })
    },

    renderSingleChart(item, type) {
      const chartId = `chart-${type}-${item.id}`
      const dom = document.getElementById(chartId)
      if (!dom) {
        console.log('❌ Chart DOM not found:', chartId)
        return
      }
      
      // Dispose existing chart if any
      if (this.chartInstances[chartId]) {
        this.chartInstances[chartId].dispose()
      }
      
      const chart = echarts.init(dom)
      this.chartInstances[chartId] = chart
      
      const imp = item.improvements || {}
      
      if (type === 'progress') {
        chart.setOption({
          tooltip: { trigger: 'axis' },
          grid: { left: '10%', right: '10%', top: '10%', bottom: '15%' },
          xAxis: { type: 'category', data: ['Start', '25%', '50%', '75%', 'Complete'] },
          yAxis: { type: 'value', max: 100 },
          series: [{
            data: [0, 25, 50, 75, 100],
            type: 'line',
            smooth: true,
            itemStyle: { color: '#667eea' },
            areaStyle: { color: 'rgba(102, 126, 234, 0.2)' }
          }]
        })
      } else if (type === 'improvement') {
        chart.setOption({
          tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
          grid: { left: '10%', right: '10%', top: '10%', bottom: '15%' },
          xAxis: { type: 'category', data: ['Knowledge', 'Accuracy', 'Speed', 'Context'] },
          yAxis: { type: 'value' },
          series: [{
            data: [imp.knowledge, imp.accuracy, imp.speed, imp.context_understanding],
            type: 'bar',
            itemStyle: {
              color: (params) => {
                const colors = ['#667eea', '#38ef7d', '#fee140', '#4facfe']
                return colors[params.dataIndex]
              }
            }
          }]
        })
      } else if (type === 'statistics') {
        chart.setOption({
          tooltip: { trigger: 'item' },
          series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            data: [
              { value: 30, name: 'Data Loading', itemStyle: { color: '#667eea' } },
              { value: 50, name: 'Training', itemStyle: { color: '#38ef7d' } },
              { value: 15, name: 'Validation', itemStyle: { color: '#fee140' } },
              { value: 5, name: 'Finalization', itemStyle: { color: '#ff6a00' } }
            ]
          }]
        })
      } else if (type === 'overtime') {
        chart.setOption({
          tooltip: { trigger: 'axis' },
          legend: { data: ['Knowledge', 'Accuracy', 'Speed', 'Context'] },
          grid: { left: '10%', right: '10%', top: '15%', bottom: '15%' },
          xAxis: { type: 'category', data: ['V1', 'V2 (Current)'] },
          yAxis: { type: 'value' },
          series: [
            { name: 'Knowledge', type: 'line', data: [0, imp.knowledge], itemStyle: { color: '#667eea' } },
            { name: 'Accuracy', type: 'line', data: [0, imp.accuracy], itemStyle: { color: '#38ef7d' } },
            { name: 'Speed', type: 'line', data: [0, imp.speed], itemStyle: { color: '#fee140' } },
            { name: 'Context', type: 'line', data: [0, imp.context_understanding], itemStyle: { color: '#4facfe' } }
          ]
        })
      }
    }
  },
  
  watch: {
    visible(newVal) {
      console.log('👀 Visible changed:', newVal, 'minionId:', this.minionId, 'minionName:', this.minionName)
      if (newVal && this.minionId) {
        console.log('📊 Calling fetchHistory from visible watcher...')
        this.fetchHistory()
      } else {
        console.log('📊 Not calling fetchHistory - visible:', newVal, 'minionId:', this.minionId)
      }
    },
    minionId(newVal) {
      console.log('👀 MinionId changed:', newVal, 'visible:', this.visible)
      if (newVal && this.visible) {
        console.log('📊 Calling fetchHistory from minionId watcher...')
        this.fetchHistory()
      } else {
        console.log('📊 Not calling fetchHistory from minionId watcher - minionId:', newVal, 'visible:', this.visible)
      }
    },
    selectedChartType() {
      this.initializeCharts()
    }
  },
  
  mounted() {
    console.log('🎯 MinionHistory mounted!', {
      visible: this.visible,
      minionId: this.minionId,
      minionName: this.minionName
    })
    
    // If already visible and has minionId, fetch history immediately
    if (this.visible && this.minionId) {
      console.log('📊 Mounted with visible=true and minionId, calling fetchHistory...')
      this.fetchHistory()
    }
  }
}
</script>

<style scoped>

@import "../assets/modal.css";
/* Modal Base */

/* Stats Dashboard */
.stats-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.modal.minion-history-modal {
  max-width: 100% !important;  
  height: 100vh !important;
  max-height: 100% !important;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 
    8px 8px 16px var(--shadow-dark),
    -8px -8px 16px var(--shadow-light);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 
    12px 12px 24px var(--shadow-dark),
    -12px -12px 24px var(--shadow-light);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  box-shadow: 
    inset 4px 4px 8px var(--shadow-dark),
    inset -4px -4px 8px var(--shadow-light);
}

.stat-icon .material-icons-round {
  color: white;
  font-size: 20px;
}

.stat-icon.total { background: var(--primary-color); }
.stat-icon.success { background: #4CAF50; }
.stat-icon.error { background: #f44336; }
.stat-icon.date { background: #FF9800; }
.stat-icon.level { background: #4CAF50; }
.stat-icon.rank { background: #FF9800; }
.stat-icon.xp { background: #9C27B0; }

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.small {
  font-size: 1rem;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .stats-dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-dashboard {
    grid-template-columns: 1fr;
  }
}

</style>