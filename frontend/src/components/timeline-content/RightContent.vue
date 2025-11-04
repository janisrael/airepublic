<template>
    <div class="row no-gutters align-items-start">
        <div class="col-sm"><!--spacer--></div>
        <div class="col-2 col-md-1 text-center flex-column d-none d-md-flex">
            <div class="stats-icon-timeline"><span class="material-icons-round">smart_toy</span></div>
            <div class="row h-100">
                <div class="col middle-line">&nbsp;</div>
            </div>
        </div>
        <div class="col-12 col-md py-2">
            <div class="card bg-primary shadow-soft border-light p-4">
                <h3 class="h5 mb-2">{{ item.training_type || 'Training Job' }} #{{ item.job_id || prefix || index + 1 }}</h3>
                <div class="improvement-badge" v-if="item.overall_improvement">
                    <span class="material-icons-round">trending_up</span>
                    <span class="improvement-text">Overall Improvement</span>
                    <span class="improvement-value">{{ item.overall_improvement }}%</span>
                </div>
                <div class="card-body">
                    <div class="nav-wrapper position-relative mb-4">
                        <ul class="nav nav-pills nav-fill flex-column flex-md-row" :id="`tabs-${prefix}-nav`" role="tablist">
                            <li class="nav-item">
                                <a class="nav-link mb-sm-3 mb-md-0" 
                                   :class="{ active: activeTab === 1 }"
                                   @click.prevent="setActiveTab(1)"
                                   href="#"
                                   role="tab">Details</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link mb-sm-3 mb-md-0" 
                                   :class="{ active: activeTab === 2 }"
                                   @click.prevent="setActiveTab(2)"
                                   href="#"
                                   role="tab">Improvements</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link mb-sm-3 mb-md-0" 
                                   :class="{ active: activeTab === 3 }"
                                   @click.prevent="setActiveTab(3)"
                                   href="#"
                                   role="tab">Charts</a>
                            </li>
                        </ul>
                    </div>
                    <div class="card shadow-inset bg-primary border-light p-4 rounded">
                        <div class="card-body p-0">
                            <div class="tab-content">
                                <div v-if="activeTab === 1" class="tab-pane">
                                    <div class="training-details">
                                        <div class="detail-item">
                                            <span class="material-icons-round">work</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Job ID</span>
                                                <span class="detail-value">{{ item.job_id || item.id || '—' }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item">
                                            <span class="material-icons-round">schedule</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Created</span>
                                                <span class="detail-value">{{ formatDate(item.created_at) }}</span>
                                            </div>
                                        </div>
                                        
                                        <div class="detail-item">
                                            <span class="material-icons-round">memory</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Provider</span>
                                                <span class="detail-value">{{ item.provider || '—' }}</span>
                                            </div>
                                        </div>
                                        
                                        <div class="detail-item">
                                            <span class="material-icons-round">model_training</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Model</span>
                                                <span class="detail-value">{{ item.model_name || item.model || '—' }}</span>
                                            </div>
                                        </div>
                                        
                                        <div class="detail-item">
                                            <span class="material-icons-round">dataset</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Collection</span>
                                                <span class="detail-value">{{ item.collection_name || '—' }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item">
                                            <span class="material-icons-round">description</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Description</span>
                                                <span class="detail-value">{{ item.description || '—' }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item">
                                            <span class="material-icons-round">category</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Training Type</span>
                                                <span class="detail-value">{{ item.training_type || '—' }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item">
                                            <span class="material-icons-round">star</span>
                                            <div class="detail-content">
                                                <span class="detail-label">XP Gained</span>
                                                <span class="detail-value">{{ item.xp_gained || 0 }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item">
                                            <span class="material-icons-round">trending_up</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Level Up</span>
                                                <span class="detail-value">{{ item.level_up ? 'Yes' : 'No' }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item">
                                            <span class="material-icons-round">emoji_events</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Rank Up</span>
                                                <span class="detail-value">{{ item.rank_up ? 'Yes' : 'No' }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item">
                                            <span class="material-icons-round">schedule</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Duration</span>
                                                <span class="detail-value">{{ calculateDuration(item.created_at, item.completed_at) }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div v-if="activeTab === 2" class="tab-pane">
                                    <div class="training-details">
                                        <div class="detail-item">
                                            <span class="material-icons-round">description</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Description</span>
                                                <span class="detail-value">{{ getDescription(item) }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item" v-if="getDatasetNames(item).length > 0">
                                            <span class="material-icons-round">dataset</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Training Data</span>
                                                <div class="dataset-chips">
                                                    <span v-for="dataset in getDatasetNames(item)" :key="dataset" class="dataset-chip">{{ dataset }}</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="detail-item">
                                            <span class="material-icons-round">psychology</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Knowledge</span>
                                                <span class="detail-value">{{ item.improvements?.knowledge || item.knowledge_improvement || '—' }}</span>
                                            </div>
                                        </div>
                                        
                                        <div class="detail-item">
                                            <span class="material-icons-round">target</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Accuracy</span>
                                                <span class="detail-value">{{ item.improvements?.accuracy || item.accuracy_improvement || '—' }}</span>
                                            </div>
                                        </div>
                                        
                                        <div class="detail-item">
                                            <span class="material-icons-round">speed</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Speed</span>
                                                <span class="detail-value">{{ item.improvements?.speed || item.speed_improvement || '—' }}</span>
                                            </div>
                                        </div>
                                        
                                        <div class="detail-item">
                                            <span class="material-icons-round">lightbulb</span>
                                            <div class="detail-content">
                                                <span class="detail-label">Context Understanding</span>
                                                <span class="detail-value">{{ item.improvements?.context_understanding || item.context_improvement || '—' }}</span>
                                            </div>
                                        </div>

                                        <div class="detail-item">
                                            <span class="material-icons-round">star</span>
                                            <div class="detail-content">
                                                <span class="detail-label">XP Gained</span>
                                                <span class="detail-value">{{ item.xp_gained || item.summary?.xp_gained || 0 }}</span>
                                            </div>
                                        </div>

                                        <!-- Training Configuration Section -->
                                        
                                    </div>
                                    <div class="config-section">
                                            <h6 class="config-title">
                                                <span class="material-icons-round">settings</span>
                                                Training Configuration
                                            </h6>
                                            
                                            <div class="config-grid">
                                                <div class="detail-item">
                                                    <span class="config-label">Training Type:</span>
                                                    <span class="config-value">{{ item.training_type || 'RAG' }}</span>
                                                </div>
                                                
                                                <div class="detail-item">
                                                    <span class="config-label">Collection:</span>
                                                    <span class="config-value">{{ item.collection_name || 'New Collection' }}</span>
                                                </div>
                                                
                                                <div class="detail-item" v-if="getRagConfig(item).embeddingModel">
                                                    <span class="config-label">Embedding Model:</span>
                                                    <span class="config-value">{{ getRagConfig(item).embeddingModel }}</span>
                                                </div>
                                                
                                                <div class="detail-item" v-if="getRagConfig(item).chunkSize">
                                                    <span class="config-label">Chunk Size:</span>
                                                    <span class="config-value">{{ getRagConfig(item).chunkSize }} tokens</span>
                                                </div>
                                                
                                                <div class="detail-item" v-if="getRagConfig(item).topK">
                                                    <span class="config-label">Top K Results:</span>
                                                    <span class="config-value">{{ getRagConfig(item).topK }}</span>
                                                </div>
                                                
                                                <div class="detail-item" v-if="getRagConfig(item).similarityThreshold">
                                                    <span class="config-label">Similarity Threshold:</span>
                                                    <span class="config-value">{{ getRagConfig(item).similarityThreshold }}</span>
                                                </div>
                                                
                                                <div class="detail-item" v-if="getRagConfig(item).retrievalMethod">
                                                    <span class="config-label">Retrieval Method:</span>
                                                    <span class="config-value">{{ getRagConfig(item).retrievalMethod }}</span>
                                                </div>
                                                
                                                <div class="detail-item" v-if="getRagConfig(item).knowledgeBaseStrategy">
                                                    <span class="config-label">Knowledge Strategy:</span>
                                                    <span class="config-value">{{ getRagConfig(item).knowledgeBaseStrategy }}</span>
                                                </div>
                                                
                                                <div class="detail-item" v-if="getRagConfig(item).updateStrategy">
                                                    <span class="config-label">Update Strategy:</span>
                                                    <span class="config-value">{{ getRagConfig(item).updateStrategy }}</span>
                                                </div>
                                            </div>
                                        </div>
                                </div>
                                <div v-if="activeTab === 3" class="tab-pane">
                                    <div class="chart-container">
                                        <div ref="radarChart" class="radar-chart"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
    name: 'RightContent',
    props: {
        item: { type: Object, default: () => ({}) },
        prefix: { type: [String, Number], default: 0 },
        index: { type: Number, default: 0 }
    },
    data() {
        return {
            activeTab: 1,
            radarChart: null
        }
    },
    mounted() {
        this.$nextTick(() => {
            this.initRadarChart()
        })
    },
    beforeUnmount() {
        if (this.radarChart) {
            this.radarChart.dispose()
        }
    },
    methods: {
        setActiveTab(tabNumber) {
            this.activeTab = tabNumber;
            if (tabNumber === 3) {
                this.$nextTick(() => {
                    this.initRadarChart()
                })
            }
        },
        formatDate(dateString) {
            if (!dateString) return '—';
            try {
                return new Date(dateString).toLocaleDateString();
            } catch {
                return '—';
            }
        },
        calculateDuration(start, end) {
            if (!start || !end) return 'N/A';
            const startDate = new Date(start);
            const endDate = new Date(end);
            const diff = endDate - startDate;
            const minutes = Math.floor(diff / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);
            return `${minutes}m ${seconds}s`;
        },
        getDatasetNames(item) {
            try {
                if (!item.rag_config) return [];
                const ragConfig = typeof item.rag_config === 'string' ? JSON.parse(item.rag_config) : item.rag_config;
                return ragConfig.selectedDatasets || [];
            } catch (e) {
                return [];
            }
        },
        getDescription(item) {
            try {
                if (!item.minion_config) return '—';
                const minionConfig = typeof item.minion_config === 'string' ? JSON.parse(item.minion_config) : item.minion_config;
                return minionConfig.description || minionConfig.roleDefinition || '—';
            } catch (e) {
                return '—';
            }
        },
        getRagConfig(item) {
            try {
                if (!item.rag_config) return {};
                return typeof item.rag_config === 'string' ? JSON.parse(item.rag_config) : item.rag_config;
            } catch (e) {
                return {};
            }
        },
        initRadarChart() {
            if (!this.$refs.radarChart) return
            
            // Dispose existing chart
            if (this.radarChart) {
                this.radarChart.dispose()
            }
            
            this.radarChart = echarts.init(this.$refs.radarChart)
            
            // Get performance data from the item
            const beforeMetrics = this.item.before_metrics || {}
            const afterMetrics = this.item.after_metrics || {}
            
            // Extract performance values (normalize to 0-100 scale)
            const beforeData = [
                Math.min(100, Math.max(0, (beforeMetrics.accuracy || 0) * 100)),
                Math.min(100, Math.max(0, (beforeMetrics.speed || 0) * 100)),
                Math.min(100, Math.max(0, (beforeMetrics.knowledge || 0) * 100)),
                Math.min(100, Math.max(0, (beforeMetrics.context_understanding || 0) * 100)),
                Math.min(100, Math.max(0, (beforeMetrics.response_quality || 0) * 100)),
                Math.min(100, Math.max(0, (beforeMetrics.consistency || 0) * 100))
            ]
            
            const afterData = [
                Math.min(100, Math.max(0, (afterMetrics.accuracy || 0) * 100)),
                Math.min(100, Math.max(0, (afterMetrics.speed || 0) * 100)),
                Math.min(100, Math.max(0, (afterMetrics.knowledge || 0) * 100)),
                Math.min(100, Math.max(0, (afterMetrics.context_understanding || 0) * 100)),
                Math.min(100, Math.max(0, (afterMetrics.response_quality || 0) * 100)),
                Math.min(100, Math.max(0, (afterMetrics.consistency || 0) * 100))
            ]
            
            // If no real data, use sample data based on improvements
            const sampleBeforeData = [
                75 + Math.random() * 10,
                70 + Math.random() * 15,
                80 + Math.random() * 10,
                65 + Math.random() * 15,
                70 + Math.random() * 20,
                75 + Math.random() * 10
            ]
            
            const sampleAfterData = sampleBeforeData.map((value, index) => {
                const improvement = [
                    this.item.accuracy_improvement || 0,
                    this.item.speed_improvement || 0,
                    this.item.knowledge_improvement || 0,
                    this.item.context_improvement || 0,
                    5 + Math.random() * 10, // response quality
                    3 + Math.random() * 8   // consistency
                ][index]
                return Math.min(100, value + improvement)
            })
            
            const option = {
                title: {
                    text: 'Performance Radar',
                    left: 'center',
                    textStyle: {
                        color: '#ffffff',
                        fontSize: 16,
                        fontWeight: 'bold'
                    }
                },
                tooltip: {
                    trigger: 'item',
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    borderColor: '#4e73df',
                    textStyle: {
                        color: '#ffffff'
                    }
                },
                legend: {
                    orient: 'horizontal',
                    bottom: 10,
                    textStyle: {
                        color: '#ffffff'
                    },
                    data: ['Before Training', 'After Training']
                },
                radar: {
                    indicator: [
                        { name: 'Accuracy', max: 100 },
                        { name: 'Speed', max: 100 },
                        { name: 'Knowledge', max: 100 },
                        { name: 'Context', max: 100 },
                        { name: 'Quality', max: 100 },
                        { name: 'Consistency', max: 100 }
                    ],
                    name: {
                        textStyle: {
                            color: '#ffffff',
                            fontSize: 12
                        }
                    },
                    splitArea: {
                        areaStyle: {
                            color: ['rgba(78, 115, 223, 0.1)', 'rgba(78, 115, 223, 0.05)', 'rgba(78, 115, 223, 0.1)', 'rgba(78, 115, 223, 0.05)', 'rgba(78, 115, 223, 0.1)']
                        }
                    },
                    splitLine: {
                        lineStyle: {
                            color: 'rgba(78, 115, 223, 0.3)'
                        }
                    },
                    axisLine: {
                        lineStyle: {
                            color: 'rgba(78, 115, 223, 0.5)'
                        }
                    }
                },
                series: [{
                    name: 'Performance Comparison',
                    type: 'radar',
                    data: [
                        {
                            value: beforeData.some(v => v > 0) ? beforeData : sampleBeforeData,
                            name: 'Before Training',
                            itemStyle: {
                                color: '#e74a3b'
                            },
                            areaStyle: {
                                color: 'rgba(231, 74, 59, 0.2)'
                            }
                        },
                        {
                            value: afterData.some(v => v > 0) ? afterData : sampleAfterData,
                            name: 'After Training',
                            itemStyle: {
                                color: '#4e73df'
                            },
                            areaStyle: {
                                color: 'rgba(78, 115, 223, 0.2)'
                            }
                        }
                    ]
                }]
            }
            
            this.radarChart.setOption(option)
            
            // Handle resize
            window.addEventListener('resize', () => {
                if (this.radarChart) {
                    this.radarChart.resize()
                }
            })
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/assets/scss/neumorphism.scss';
</style>
<style scoped>
.card-body {
    padding: 0px !important;
}
.mb-4 {
    margin-bottom: 0px !important;
}

.improvement-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.75rem 1rem;
    background: linear-gradient(135deg, rgba(78, 115, 223, 0.1), rgba(78, 115, 223, 0.05));
    border: 1px solid rgba(78, 115, 223, 0.2);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(78, 115, 223, 0.1);
}

.improvement-badge .material-icons-round {
    font-size: 20px;
    color: #4e73df;
}

.improvement-text {
    font-size: 0.9rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.improvement-value {
    font-size: 1.2rem;
    color: #4e73df;
    font-weight: 700;
    margin-left: auto;
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
.card.shadow-inset.bg-primary.border-light.p-4.rounded{
    padding: 0px !important;
}
.col-2.col-md-1.text-center.flex-column.d-none.d-md-flex {
  padding-left: 10px;
  padding-right: 10px;
  height: 100%;
}

.chart-placeholder {
  text-align: center;
  padding: 2rem;
  color: var(--secondary);
}

.chart-placeholder .material-icons-round {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}
.col-md {
    max-width: 46%;
}

.tab-pane {
    padding: 1rem;
    min-height: 200px;
    display: block !important;
}

.tab-pane p {
    margin-bottom: 0.5rem;
    color: #333;
}

.tab-pane div {
    /* margin-bottom: 0.5rem; */
    color: #333;
}
.chart-placeholder p {
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.chart-placeholder small {
  opacity: 0.7;
}

.training-details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.detail-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    transition: all 0.2s ease;
    border: 2px solid #80808030;
}

.detail-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.detail-item .material-icons-round {
    font-size: 18px;
    color: var(--primary);
    flex-shrink: 0;
}

.detail-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    flex: 1;
}

.detail-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.detail-value {
    font-size: 0.9rem;
    color: var(--text-primary);
    font-weight: 600;
}

.dataset-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.dataset-chip {
    background: rgba(78, 115, 223, 0.1);
    color: var(--primary);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: 1px solid rgba(78, 115, 223, 0.2);
}

.config-section {
    margin-top: 1.5rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.config-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    color: var(--primary);
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.config-title .material-icons-round {
    font-size: 18px;
}

.config-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.config-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.config-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.config-value {
    font-size: 0.85rem;
    color: var(--text-primary);
    font-weight: 600;
}

.chart-container {
    padding: 1rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.radar-chart {
    width: 100%;
    height: 400px;
    min-height: 300px;
}
</style>