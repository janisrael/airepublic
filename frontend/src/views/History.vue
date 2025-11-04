<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1>History</h1>
      <p>Training history and model performance</p>
    </div>

    <!-- Stats Cards -->
    <div class="dashboard-grid">
      <div class="neumorphic-card stats-card" v-for="(card, index) in statsCards" :key="index">
        <div class="stats-icon" :class="card.class">
          <span class="material-icons-round">{{ card.icon }}</span>
        </div>
        <div class="stats-info">
          <h3>{{ card.value }}</h3>
          <p>{{ card.label }}</p>
        </div>
      </div>
    </div>

    <!-- Recent Activity and Model Performance -->
    <div class="dashboard-row">

      <div class="timeline timeline-three px-3 px-sm-0"><!-- Timeline Item 1 -->
        <div class="row no-gutters">
          <div class="col-sm"><!--spacer--></div><!-- timeline item 1 center image & middle line -->
          <div class="col-2 col-md-1 text-center flex-column d-none d-md-flex">
            <div class="stats-icon-timeline">
              <span 
                class="material-icons-round">smart_toy</span></div>
            <div class="row h-100">
              <div class="col middle-line">&nbsp;</div>
            </div>
          </div><!-- timeline profile card -->
          <div class="col-12 col-md py-2">
            <div class="profile-card">
              <div class="card bg-primary shadow-soft border-light p-4">
                <div class="card-body">
                  <h3 class="h5 mb-2">Jose Leos</h3><span class="h6 font-weight-normal text-gray mb-3">Co-Founder</span>
                  <p class="card-text my-4">I spend my days with my hands in many different areas of web development
                    from back end programming to front end engineering, digital accessibility.</p>
                  <ul class="list-unstyled d-flex mt-3 mb-4">
                    <li><a href="#" target="_blank" aria-label="facebook social link"
                        class="icon icon-xs icon-facebook mr-3"><span class="fab fa-facebook-f"></span></a></li>
                    <li><a href="#" target="_blank" aria-label="twitter social link"
                        class="icon icon-xs icon-twitter mr-3"><span class="fab fa-twitter"></span></a></li>
                    <li><a href="#" target="_blank" aria-label="slack social link"
                        class="icon icon-xs icon-slack mr-3"><span class="fab fa-slack-hash"></span></a></li>
                    <li><a href="#" target="_blank" aria-label="dribbble social link"
                        class="icon icon-xs icon-dribbble mr-3"><span class="fab fa-dribbble"></span></a></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div><!-- Timeline Item 2 -->
        <div class="row no-gutters"><!-- timeline profile card -->
          <div class="col-12 col-md py-2">
            <div class="card bg-primary shadow-soft border-light p-4">
              <div class="card-body">
                <h3 class="h5 mb-2">Neil Sims</h3>
                <span class="h6 font-weight-normal text-gray mb-3">Web Designer</span>
                <p class="card-text my-4">I spend my days with my hands in many different areas of web development from
                  back end programming to front end engineering, digital accessibility.</p>
                <ul class="list-unstyled d-flex mt-3 mb-4">
                  <li><a href="#" target="_blank" aria-label="facebook social link"
                      class="icon icon-xs icon-facebook mr-3"><span class="fab fa-facebook-f"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="twitter social link"
                      class="icon icon-xs icon-twitter mr-3"><span class="fab fa-twitter"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="slack social link"
                      class="icon icon-xs icon-slack mr-3"><span class="fab fa-slack-hash"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="dribbble social link"
                      class="icon icon-xs icon-dribbble mr-3"><span class="fab fa-dribbble"></span></a></li>
                </ul>
              </div>
            </div>
          </div><!-- timeline item 2 center image & middle line -->
          <div class="col-2 col-md-1 text-center flex-column d-none d-md-flex">
            <div data-v-89ccdf85="" class="stats-icon-timeline"><span data-v-89ccdf85=""
                class="material-icons-round">smart_toy</span></div>
            <div class="row h-100">
              <div class="col middle-line">&nbsp;</div>
            </div>
          </div>
          <div class="col-sm"><!--spacer--></div>
        </div><!-- Timeline Item 3 -->
        <div class="row no-gutters">
          <div class="col-sm"><!--spacer--></div><!-- timeline item 3 center image & middle line -->
          <div class="col-2 col-md-1 text-center flex-column d-none d-md-flex">
            <div data-v-89ccdf85="" class="stats-icon-timeline"><span data-v-89ccdf85="" class="material-icons-round">smart_toy</span></div>
            <div class="row h-100">
              <div class="col middle-line">&nbsp;</div>
            </div>
          </div><!-- timeline profile card -->
          <div class="col-12 col-md py-2">
            <div class="card bg-primary shadow-soft border-light p-4">
              <div class="card-body">
                <h3 class="h5 mb-2">Bonnie Green</h3><span class="h6 font-weight-normal text-gray mb-3">Marketing</span>
                <p class="card-text my-4">I spend my days with my hands in many different areas of web development from
                  back end programming to front end engineering, digital accessibility.</p>
                <ul class="list-unstyled d-flex mt-3 mb-4">
                  <li><a href="#" target="_blank" aria-label="facebook social link"
                      class="icon icon-xs icon-facebook mr-3"><span class="fab fa-facebook-f"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="twitter social link"
                      class="icon icon-xs icon-twitter mr-3"><span class="fab fa-twitter"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="slack social link"
                      class="icon icon-xs icon-slack mr-3"><span class="fab fa-slack-hash"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="dribbble social link"
                      class="icon icon-xs icon-dribbble mr-3"><span class="fab fa-dribbble"></span></a></li>
                </ul>
              </div>
            </div>
          </div>
        </div><!-- Timeline Item 4 -->
        <div class="row no-gutters"><!-- timeline profile card -->
          <div class="col-12 col-md py-2">
            <div class="card bg-primary shadow-soft border-light p-4">
              <div class="card-body">
                <h3 class="h5 mb-2">Christopher Wood</h3><span class="h6 font-weight-normal text-gray mb-3">SEO
                  Specialist</span>
                <p class="card-text my-4">I spend my days with my hands in many different areas of web development from
                  back end programming to front end engineering, digital accessibility.</p>
                <ul class="list-unstyled d-flex mt-3 mb-4">
                  <li><a href="#" target="_blank" aria-label="facebook social link"
                      class="icon icon-xs icon-facebook mr-3"><span class="fab fa-facebook-f"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="twitter social link"
                      class="icon icon-xs icon-twitter mr-3"><span class="fab fa-twitter"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="slack social link"
                      class="icon icon-xs icon-slack mr-3"><span class="fab fa-slack-hash"></span></a></li>
                  <li><a href="#" target="_blank" aria-label="dribbble social link"
                      class="icon icon-xs icon-dribbble mr-3"><span class="fab fa-dribbble"></span></a></li>
                </ul>
              </div>
            </div>
          </div><!-- timeline item 4 center image & middle line -->
          <div class="col-2 col-md-1 text-center flex-column d-none d-md-flex">
            <div class="stats-icon-timeline"><span data-v-89ccdf85="" class="material-icons-round">smart_toy</span></div>
              </div>
          <div class="col-sm"><!--spacer--></div>
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
    <div class="neumorphic-card quick-actions">
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
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs';
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
  name: 'History',
  components: { LineChart },
  data() {
    return {
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
      }
    };
  },
  methods: {
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
    display: flex
;
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
