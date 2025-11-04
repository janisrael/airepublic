<template>
  <div class="dashboard-container">
    <div class="page-header">
      <div class="minion-header">
        <div class="minion-info">
          <div v-if="loadingMinion" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading minion details...</p>
          </div>
          <div v-else-if="minionError" class="error-state">
            <span class="material-icons-round">error</span>
            <h1>Error Loading Minion</h1>
            <p>{{ minionError }}</p>
          </div>
          <div v-else>
            <h1>{{ minionName }}</h1>
            <p v-if="minionDescription">{{ minionDescription }}</p>
            <p v-else class="no-description">No description available</p>
          </div>
        </div>
        <div class="minion-avatar" v-if="minionAvatar && !loadingMinion && !minionError">
          <img :src="minionAvatar" :alt="minionName" />
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="dashboard-grid">
      <div class="neumorphic-card stats-card">
        <div class="stats-icon total">
          <span class="material-icons-round">military_tech</span>
        </div>
        <div class="stats-info">
          <h3>{{ totalTrainings }}</h3>
          <p>Total Trainings</p>
        </div>
      </div>
      
      <div class="neumorphic-card stats-card">
        <div class="stats-icon xp">
          <span class="material-icons-round">star</span>
        </div>
        <div class="stats-info">
          <h3>{{ totalXPGained }}</h3>
          <p>Total XP Gained</p>
        </div>
      </div>
      
      <div class="neumorphic-card stats-card">
        <div class="stats-icon level">
          <span class="material-icons-round">trending_up</span>
        </div>
        <div class="stats-info">
          <h3>{{ currentLevel }}</h3>
          <p>Current Level</p>
        </div>
      </div>
      
      <div class="neumorphic-card stats-card">
        <div class="stats-icon rank">
          <span class="material-icons-round">emoji_events</span>
        </div>
        <div class="stats-info">
          <h3>{{ currentRank }}</h3>
          <p>Current Rank</p>
        </div>
      </div>
    </div>

    <!-- Recent Activity and Model Performance -->
    <div class="dashboard-row">

      <div class="timeline timeline-three px-3 px-sm-0">
            <div v-for="(h, i) in history" :key="h.id || i" class="row no-gutters">
              
              <component 
                :is="(i + 1) % 2 !== 0 ? 'RightContent' : 'LeftContent'"
                :item="h"
                :prefix="h.id || i"
                :index="i"
              ></component>
            </div>
      </div>
      <!-- <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Recent Activity</h3>
            <button class="btn btn-sm btn-secondary">View All</button>
          </div>
          <ul class="activity-list">
            <li v-for="(activity, index) in recentActivities" :key="index" class="activity-item">
              <div class="activity-icon" :class="activity.type">
                <span class="material-icons-round">{{ activity.icon }}</span>
              </div>
              <div class="activity-details">
                <p class="activity-text">{{ activity.text }}</p>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
            </li>
          </ul>
        </div>
      </div> -->

      <!-- <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Model Performance</h3>
            <select class="form-control form-control-sm" style="width: auto;">
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Last 90 days</option>
            </select>
          </div>
          <div class="chart-container">
            <LineChart :chart-data="chartData" :options="chartOptions" />
          </div>
        </div>
      </div> -->
    </div>

    <!-- Quick Actions -->
    <!-- <div class="neumorphic-card quick-actions">
      <h3>Quick Actions</h3>
      <div class="actions-grid">
        <button class="action-btn" @click="startNewTraining">
          <span class="material-icons-round icon-primary">play_arrow</span>
          <span>Start New Training</span>
        </button>
        <button class="action-btn" @click="uploadDataset">
          <span class="material-icons-round icon-success">upload</span>
          <span>Upload Dataset</span>
        </button>
        <button class="action-btn" @click="evaluateModel">
          <span class="material-icons-round icon-info">assessment</span>
          <span>Evaluate Model</span>
        </button>
        <button class="action-btn" @click="deployModel">
          <span class="material-icons-round icon-warning">rocket_launch</span>
          <span>Deploy Model</span>
        </button>
      </div>
    </div> -->
  </div>
</template>

<script>
import { Line } from 'vue-chartjs';
import { API_ENDPOINTS } from '@/config/api'
import LeftContent from '@/components/timeline-content/LeftContent.vue'
import RightContent from '@/components/timeline-content/RightContent.vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale
} from 'chart.js';

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale);

const LineChart = {
  name: 'LineChart',
  extends: Line,
  props: {
    chartData: { type: Object, required: true },
    options: { type: Object, default: () => ({}) }
  },
  mounted() {
    // this.renderChart(this.chartData, this.options);
  },
  watch: {
    chartData: {
      handler(newData) {
        this.renderChart(newData, this.options);
      },
      deep: true
    },
    options: {
      handler(newOptions) {
        this.renderChart(this.chartData, newOptions);
      },
      deep: true
    }
  }
};

export default {
  name: 'MinionTrainingHistory',
  components: { LineChart, LeftContent, RightContent },
  props: {
    minionId: {
      type: [String, Number],
      required: false,
      default: null
    }
    ,
    minionhistory: {
      type: Array,
      required: false,
      default: () => []
    }
  },
  data() {
    return {
      minionName: '',
      minionDescription: '',
      minionAvatar: '',
      minionError: null,
      loadingMinion: false,
      statsCards: [
        { icon: 'smart_toy', value: '5', label: 'Active Models' },
        { icon: 'bolt', value: '2', label: 'Training Jobs', class: 'training' },
        { icon: 'dataset', value: '12', label: 'Datasets', class: 'dataset' },
        { icon: 'track_changes', value: '92.5%', label: 'Avg. Accuracy', class: 'accuracy' }
      ],
      recentActivities: [
        {
          type: 'training',
          icon: 'bolt',
          text: 'Training job "Image Classifier v2.1" completed successfully',
          time: '10 minutes ago'
        },
        {
          type: 'model',
          icon: 'smart_toy',
          text: 'New model version 3.2.0 deployed to production',
          time: '2 hours ago'
        },
        {
          type: 'dataset',
          icon: 'dataset',
          text: 'New dataset "Street View Images Q3-2023" uploaded',
          time: '1 day ago'
        },
        {
          type: 'evaluation',
          icon: 'trending_up',
          text: 'Model accuracy improved to 94.2% on test set',
          time: '2 days ago'
        },
        {
          type: 'alert',
          icon: 'warning',
          text: 'Training job #1245 failed - Insufficient GPU memory',
          time: '3 days ago'
        }
      ],
      chartData: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [
          {
            label: 'Accuracy',
            data: [85, 82, 88, 87, 90, 91, 92.5],
            borderColor: '#4e73df',
            backgroundColor: 'rgba(78, 115, 223, 0.1)',
            tension: 0.4,
            fill: true,
            borderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5
          },
          {
            label: 'Loss',
            data: [1.2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.45],
            borderColor: '#e74a3b',
            borderDash: [5, 5],
            backgroundColor: 'transparent',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5
          }
        ]
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { usePointStyle: true, padding: 20 } },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { size: 14, weight: 'bold' },
            bodyFont: { size: 13 },
            padding: 12,
            cornerRadius: 8
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            ticks: { padding: 10 }
          },
          x: {
            grid: { display: false },
            ticks: { padding: 10 }
          }
        }
      },

      history: [],
      loadingHistory: false,
      openPanel: null,
      openSubPanels: {}
    };
  },
  computed: {
    totalTrainings() {
      return this.history.length;
    },
    totalXPGained() {
      return this.history.reduce((total, h) => total + (parseInt(h.xp_gained) || 0), 0);
    },
    currentLevel() {
      if (this.history.length === 0) return 1;
      // Get the latest training record's after_metrics for current level
      const latestRecord = this.history[0]; // Most recent is first
      if (latestRecord.after_metrics && latestRecord.after_metrics.minion_stats) {
        return latestRecord.after_metrics.minion_stats.level || 1;
      }
      // Fallback: calculate from before_metrics + XP gained
      const beforeLevel = latestRecord.before_metrics?.minion_stats?.level || 1;
      const totalXP = this.totalXPGained;
      // Simple level calculation: every 100 XP = 1 level
      return Math.max(beforeLevel, Math.floor(totalXP / 100) + 1);
    },
    currentRank() {
      if (this.history.length === 0) return 'Novice';
      // Get the latest training record's after_metrics for current rank
      const latestRecord = this.history[0]; // Most recent is first
      if (latestRecord.after_metrics && latestRecord.after_metrics.minion_stats) {
        return latestRecord.after_metrics.minion_stats.rank || 'Novice';
      }
      // Fallback: calculate rank based on level
      const level = this.currentLevel;
      if (level >= 50) return 'Master';
      if (level >= 30) return 'Expert';
      if (level >= 20) return 'Advanced';
      if (level >= 10) return 'Intermediate';
      return 'Novice';
    },
    successfulTrainings() {
      return this.history.filter(h => h.status === 'COMPLETED' || h.status === 'completed').length;
    },
    failedTrainings() {
      return this.history.filter(h => h.status === 'FAILED' || h.status === 'failed').length;
    },
    averageImprovement() {
      if (this.history.length === 0) return 0;
      const improvements = this.history
        .filter(h => h.overall_improvement !== undefined && h.overall_improvement !== null)
        .map(h => parseFloat(h.overall_improvement) || 0);
      
      if (improvements.length === 0) return 0;
      const average = improvements.reduce((sum, val) => sum + val, 0) / improvements.length;
      return Math.round(average * 10) / 10; // Round to 1 decimal place
    }
  },
  watch: {
    minionId(newVal) {
      if (newVal) this.fetchHistory()
    }
  },
  async mounted() {
    if (this.minionId) await this.fetchHistory()
  },
  methods: {
    async fetchHistory() {
      if (!this.minionId) return
      this.loadingHistory = true
      try {
        // First, fetch minion details
        await this.fetchMinionDetails()
        
        // Then fetch training history
        const res = await fetch(`${API_ENDPOINTS.v2.minions}/${this.minionId}/training-history`)
        const result = await res.json()
        if (result && result.success) {
          this.history = result.training_history || []
        } else {
          console.warn('Failed to fetch history', result)
          this.history = []
        }
      } catch (err) {
        console.error('Error fetching history:', err)
        this.history = []
      } finally {
        this.loadingHistory = false
      }
    },

    async fetchMinionDetails() {
      if (!this.minionId) return
      this.loadingMinion = true
      this.minionError = null
      
      try {
        const res = await fetch(`${API_ENDPOINTS.v2.minions}/${this.minionId}`)
        
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`)
        }
        
        const result = await res.json()
        console.log('Minion API response:', result) // Debug log
        
        if (!result.success) {
          throw new Error(result.error || result.message || 'Failed to fetch minion details')
        }
        
        const minion = result.minion || result.data || result
        console.log('Minion data:', minion) // Debug log
        
        if (!minion) {
          throw new Error('No minion data received')
        }
        
        // Extract real minion data - prioritize display_name over name
        this.minionName = minion.display_name || minion.name || minion.title
        this.minionDescription = minion.description || minion.roleDefinition || ''
        this.minionAvatar = minion.avatar || minion.image
        
        // Validate required fields
        if (!this.minionName) {
          throw new Error('Minion name is missing from API response')
        }
        
        console.log('Successfully loaded minion:', {
          name: this.minionName,
          description: this.minionDescription,
          avatar: this.minionAvatar
        })
        
      } catch (err) {
        console.error('Error fetching minion details:', err)
        this.minionError = err.message || 'Failed to load minion details'
        this.minionName = ''
        this.minionDescription = ''
        this.minionAvatar = ''
      } finally {
        this.loadingMinion = false
      }
    },

    togglePanel(id) {
      this.openPanel = this.openPanel === id ? null : id
      if (this.openPanel) {
        this.openSubPanels = { ...this.openSubPanels, [this.openPanel]: this.openSubPanels[this.openPanel] || 1 }
      }
    },

    toggleSub(itemId, idx) {
      const cur = this.openSubPanels[itemId]
      this.openSubPanels = { ...this.openSubPanels, [itemId]: cur === idx ? null : idx }
    },

    startNewTraining() {
      this.$router.push('/training');
    },
    uploadDataset() {
      this.$router.push('/datasets?action=upload');
    },
    evaluateModel() {
      this.$router.push('/evaluation');
    },
    deployModel() {
      alert('Deployment dialog would open here');
    }
  }
};
</script>
<style lang="scss" scoped>
@import '@/assets/scss/neumorphism.scss';
</style>
<style scoped>
:root {
  --primary-color: #4e73df;
  --success-color: #1cc88a;
  --info-color: #36b9cc;
  --warning-color: #f6c23e;
  --danger-color: #e74a3b;
  --light-color: #f8f9fc;
  --dark-color: #5a5c69;
}

.dashboard-container {
  padding: 1.5rem;
  /* max-width: 1400px; */
  margin: 0 auto;
  font-family: 'Roboto', sans-serif;
}

.material-icons-round {
  font-family: 'Material Icons Round';
  font-weight: normal;
  font-style: normal;
  font-size: 1.5rem;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  vertical-align: middle;
}

.page-header {
  margin-bottom: 2rem;
}

.minion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.minion-info h1 {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-size: 2rem;
  font-weight: 700;
}

.minion-info p {
  color: var(--text-secondary);
  font-size: 1rem;
  margin: 0;
}

.minion-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid var(--primary);
  box-shadow: 0 4px 12px rgba(78, 115, 223, 0.2);
}

.minion-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #dc3545;
}

.error-state .material-icons-round {
  font-size: 24px;
}

.error-state h1 {
  color: #dc3545;
  font-size: 1.5rem;
  margin: 0;
}

.error-state p {
  color: #dc3545;
  margin: 0;
  font-size: 0.9rem;
}

.no-description {
  color: var(--text-secondary);
  font-style: italic;
  opacity: 0.7;
}

.stats-icon.total,
.stats-icon.xp,
.stats-icon.level,
.stats-icon.rank,
.stats-icon.success,
.stats-icon.failed,
.stats-icon.accuracy {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.page-header h1 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.page-header p {
  color: var(--secondary);
  margin: 0;
}

.stats-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  transition: transform 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.5rem;
  font-size: 1.8rem;
  background: linear-gradient(145deg, #caced3, #f0f5fd);
  box-shadow: 5px 5px 10px var(--shadow-dark),
    -5px -5px 10px var(--shadow-light);
}

.stats-icon i {
  font-style: normal;
}

.stats-icon.training {
  color: #f6c23e;
}

.stats-icon.dataset {
  color: #1cc88a;
}

.stats-icon.accuracy {
  color: #4e73df;
}

.stats-info h3 {
  font-size: 1.8rem;
  margin: 0 0 0.25rem;
  color: var(--text-color);
}

.stats-info p {
  margin: 0;
  color: var(--secondary);
  font-size: 0.9rem;
}

.dashboard-row {
  /* display: flex; */
  flex-wrap: wrap;
  margin: 0 -0.75rem 1.5rem;
}
.card-body {
  padding: 0;
}
.dashboard-col {
  flex: 1 0 0%;
  padding: 0 0.75rem;
  min-width: 300px;
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text-color);
}

.activity-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.stats-icon-timeline {
  width: 100px;
  height: 100px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.5rem;
  font-size: 1.8rem;
  background: linear-gradient(145deg, #caced3, #f0f5fd);
  box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light);
}

.stats-icon-timeline span.material-icons-round {
  font-size: 3rem;
}

.col-2.col-md-1.text-center.flex-column.d-none.d-md-flex {
  padding-left: 10px;
  padding-right: 10px;
}

.activity-item {
  display: flex;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-size: 1.2rem;
  background: var(--card-bg);
  box-shadow: 3px 3px 6px var(--shadow-dark),
    -3px -3px 6px var(--shadow-light);
}

.activity-icon.training {
  color: #f6c23e;
}

.activity-icon.evaluation {
  color: #36b9cc;
}

.activity-icon.deployment {
  color: #1cc88a;
}

.activity-icon.dataset {
  color: #4e73df;
}

.activity-icon.model {
  color: #e74a3b;
}

.activity-details {
  flex: 1;
}

.activity-text {
  margin: 0 0 0.25rem;
  color: var(--text-color);
  font-size: 0.9rem;
  line-height: 1.4;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--secondary);
}

.chart-container {
  height: 300px;
  position: relative;
  margin: 0 -1rem -1rem;
}

.quick-actions {
  margin-top: 1.5rem;
}

.quick-actions h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  color: var(--text-color);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.timeline.timeline-three .row .col.middle-line:after {
  content: "";
  position: absolute;
  bottom: 0;
  height: 100%;
  width: 6px;
  margin-top: 1.875rem;
  margin-left: -3px;
  border: .0625rem solid #d1d9e6;
  box-shadow: inset 1px 2px 1px #d2d2d2, inset -3px -3px 7px #eff0f5;
  border-radius: .55rem;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 1rem;
  border: none;
  background: var(--card-bg);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 5px 5px 10px var(--shadow-dark),
    -5px -5px 10px var(--shadow-light);
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 8px 8px 16px var(--shadow-dark),
    -8px -8px 16px var(--shadow-light);
}

.action-btn i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  font-style: normal;
}

.action-btn span {
  font-size: 0.9rem;
  color: var(--text-color);
  font-weight: 500;
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dashboard-col {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>
