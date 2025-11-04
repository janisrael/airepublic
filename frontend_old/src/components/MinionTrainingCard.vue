<template>
    <div>
        <div class="minion-training-card" :id="`minion-card-${minion.id}`">
            <!-- Minion Header -->
            <div class="minion-header">
                <div class="minion-avatar">
                    <img :src="getMinionAvatar(minion)" :alt="minion.display_name" @error="handleImageError" />
                </div>
                <div class="minion-info">
                    <h3>{{ minion.display_name }}</h3>
                    <div class="minion-stats">
                        <span class="level">Level {{ minion.level || 1 }}</span>
                        <span class="xp">{{ (minion.total_training_xp || 0) + (minion.total_usage_xp || 0) }} XP</span>
                        <span class="rank">{{ minion.rank || 'Novice' }}</span>
                    </div>
                </div>
                <div class="minion-provider">
                    <span class="provider-badge" :class="minion.provider">
                        {{ minion.provider.toUpperCase() }}
                    </span>
                </div>
            </div>

            <!-- Training Info -->
            <div class="training-info">
                <h4>{{ minion.latest_training.job_name }}</h4>
                <div class="training-badges">
                    <span class="training-type">{{ getTrainingTypeLabel(minion.latest_training.training_type) }}</span>
                    <span class="training-status" :class="minion.latest_training.status.toLowerCase()">
                        {{ getStatusLabel(minion.latest_training.status) }}
                    </span>
                </div>
            </div>

            <!-- Cumulative Improvements -->
            <div class="improvements">
                <div class="improvements-header">
                    <span class="material-icons-round">trending_up</span>
                    <span>Total Improvements</span>
                </div>
                <div class="improvements-grid">
                    <div class="improvement-item">
                        <span class="material-icons-round improvement-icon">psychology</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Knowledge</span>
                            <span class="improvement-value"
                                :class="getImprovementClass(minion.cumulative_improvements.knowledge)">
                                {{ formatImprovement(minion.cumulative_improvements.knowledge) }}
                            </span>
                        </div>
                    </div>
                    <div class="improvement-item">
                        <span class="material-icons-round improvement-icon">verified</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Accuracy</span>
                            <span class="improvement-value"
                                :class="getImprovementClass(minion.cumulative_improvements.accuracy)">
                                {{ formatImprovement(minion.cumulative_improvements.accuracy) }}
                            </span>
                        </div>
                    </div>
                    <div class="improvement-item">
                        <span class="material-icons-round improvement-icon">speed</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Speed</span>
                            <span class="improvement-value"
                                :class="getImprovementClass(minion.cumulative_improvements.speed)">
                                {{ formatImprovement(minion.cumulative_improvements.speed) }}
                            </span>
                        </div>
                    </div>
                    <div class="improvement-item">
                        <span class="material-icons-round improvement-icon">lightbulb</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Context</span>
                            <span class="improvement-value"
                                :class="getImprovementClass(minion.cumulative_improvements.context_understanding)">
                                {{ formatImprovement(minion.cumulative_improvements.context_understanding) }}
                            </span>
                        </div>
                    </div>
                    <div class="improvement-item level-rank-item">
                        <span class="material-icons-round improvement-icon">military_tech</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Level</span>
                            <span class="improvement-value level-value">{{ minion.level || 1 }}</span>
                        </div>
                    </div>
                    <div class="improvement-item level-rank-item">
                        <span class="material-icons-round improvement-icon">emoji_events</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Rank</span>
                            <span class="improvement-value rank-value">{{ minion.rank || 'Novice' }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Training Count -->
            <div class="training-count">
                <span class="material-icons-round">history</span>
                <span>{{ minion.training_count }} Previous Training{{ minion.training_count !== 1 ? 's' : '' }}</span>
            </div>

            <!-- Actions -->
            <div class="actions">
                <!-- Default actions when no pending job -->
                <template v-if="!hasPendingJob">
                    <button class="btn btn-outline" @click="viewHistory">
                        <span class="material-icons-round">timeline</span>
                        View History
                    </button>
                    <button class="btn btn-primary upgrade-btn" @click="upgradeMinion">
                        <span class="material-icons-round">upgrade</span>
                        Upgrade
                    </button>
                </template>

                <!-- Pending job actions -->
                <template v-else>
                    <button class="btn btn-outline" @click="viewPendingJob">
                        <span class="material-icons-round">visibility</span>
                        View
                    </button>
                    <button class="btn btn-primary btn-train" @click="startPendingTraining"
                        :disabled="pendingJob.status === 'RUNNING'">
                        <span class="material-icons-round">play_arrow</span>
                        {{ pendingJob.status === 'RUNNING' ? 'Training...' : 'Train' }}
                    </button>
                    <button class="btn btn-danger btn-cancel" @click="deletePendingJob"
                        :disabled="pendingJob.status === 'RUNNING'">
                        <span class="material-icons-round">delete</span>
                        Delete
                    </button>
                </template>
            </div>

            <!-- Training Progress Overlay -->
            <div v-if="showTrainingOverlay" class="training-overlay" :id="`training-overlay-${minion.id}`">
                <div class="overlay-content">
                    <!-- Header with Status -->
                    <div class="overlay-header">
                        <div class="status-section">
                            <div class="loading-spinner">
                                <span class="material-icons-round">sync</span>
                            </div>
                            <div class="status-info">
                                <h3>{{ trainingStatus }}</h3>
                                <p>{{ currentStepMessage }}</p>
                            </div>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: trainingProgress + '%' }"></div>
                        </div>
                    </div>

                    <!-- Training Steps -->
                    <div class="training-steps">
                        <div v-for="step in trainingSteps" :key="step.id" class="training-step" :class="{
                            'completed': step.completed,
                            'active': step.active,
                            'pending': !step.completed && !step.active
                        }">
                            <div class="step-icon">
                                <span v-if="step.completed" class="material-icons-round check-icon">check_circle</span>
                                <span v-else-if="step.active"
                                    class="material-icons-round active-icon">radio_button_checked</span>
                                <span v-else class="material-icons-round pending-icon">radio_button_unchecked</span>
                            </div>
                            <div class="step-content">
                                <span class="step-name">{{ step.name }}</span>
                                <span v-if="step.completed" class="step-status completed">Completed</span>
                                <span v-else-if="step.active" class="step-status active">Running...</span>
                                <!-- <span v-else class="step-status pending">Pending</span> -->
                            </div>
                        </div>
                    </div>

                    <!-- Completion Message -->
                    <div v-if="trainingCompleted" class="completion-section">
                        <div class="completion-icon">
                            <span class="material-icons-round">celebration</span>
                        </div>
                        <h3>Training Complete!</h3>
                        <p>Your minion has been successfully upgraded with new knowledge and capabilities.</p>
                        <button class="btn btn-primary" @click="closeTrainingOverlay">
                            <span class="material-icons-round">close</span>
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { mapState } from 'pinia'

export default {
    name: 'MinionTrainingCard',
    props: {
        minion: {
            type: Object,
            required: true
        },
        pendingJobs: {
            type: Array,
            default: () => []
        }
    },
    data() {
        return {
            showTrainingOverlay: false,
            trainingStatus: 'Initializing RAG...',
            currentStepMessage: 'Preparing training environment...',
            trainingProgress: 0,
            trainingCompleted: false,
            trainingSteps: [
                { id: 1, name: 'Dataset Loading', completed: false, active: false },
                { id: 2, name: 'Dataset Refinement', completed: false, active: false },
                { id: 3, name: 'Knowledge Base Creation', completed: false, active: false },
                { id: 4, name: 'Embedding Creation', completed: false, active: false },
                { id: 5, name: 'Minion Update', completed: false, active: false },
                { id: 6, name: 'Training Validation', completed: false, active: false },
                { id: 7, name: 'Testing', completed: false, active: false },
                { id: 8, name: 'Metrics Collection', completed: false, active: false }
            ],
            currentStepIndex: 0,
            pollingInterval: null
        }
    },
    computed: {
        ...mapState(useAuthStore, ['user', 'token']),
        hasPendingJob() {
            return this.pendingJob !== null;
        },
        pendingJob() {
            return this.pendingJobs.find(job => job.minionId === this.minion.id) || null;
        }
    },
    mounted() {
        console.log('🔥 MinionTrainingCard mounted - status updates DISABLED by default')
    },
    beforeUnmount() {
        // 🔥 SMART STATUS UPDATES: Ensure cleanup on component destroy
        console.log('🔥 MinionTrainingCard destroyed - cleaning up status updates')
        this.stopRealTimeStatusUpdates()
    },
    methods: {
        getMinionAvatar(minion) {
            // Use minion's avatar if available, otherwise use default
            if (minion.avatar_url) {
                // If it's a relative path, make it absolute
                if (minion.avatar_url.startsWith('api/')) {
                    return `http://localhost:5000/${minion.avatar_url}`
                }
                return minion.avatar_url
            }
            if (minion.avatar_path) {
                // Extract filename from path and construct proper URL
                const filename = minion.avatar_path.split('/').pop()
                return `http://localhost:5000/api/avatars/${filename}`
            }
            // Default avatar based on provider
            return this.getDefaultAvatar(minion.provider)
        },

        getDefaultAvatar(provider) {
            const avatars = {
                nvidia: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiM3N0I4RkYiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMjQiIGhlaWdodD0iMjQiPgo8cGF0aCBkPSJNMTIgMTJIMjhWMjhIMTJWMTJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4KPC9zdmc+',
                openai: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiM0MEE5ODciLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMjQiIGhlaWdodD0iMjQiPgo8cGF0aCBkPSJNMTIgMTJIMjhWMjhIMTJWMTJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4KPC9zdmc+',
                anthropic: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiNGRjY1MDAiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMjQiIGhlaWdodD0iMjQiPgo8cGF0aCBkPSJNMTIgMTJIMjhWMjhIMTJWMTJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4KPC9zdmc+'
            }
            return avatars[provider] || avatars.nvidia
        },

        handleImageError(event) {
            event.target.src = this.getDefaultAvatar(this.minion.provider)
        },

        getTrainingTypeLabel(type) {
            const labels = {
                rag: 'RAG Training',
                lora: 'LoRA Training',
                hybrid: 'Hybrid Training',
                creation: 'Creation'
            }
            return labels[type] || type
        },

        getStatusLabel(status) {
            const labels = {
                PENDING: 'Pending',
                RUNNING: 'Running',
                COMPLETED: 'Completed',
                FAILED: 'Failed'
            }
            return labels[status] || status
        },

        formatImprovement(value) {
            if (value > 0) {
                return `+${value}%`
            } else if (value < 0) {
                return `${value}%`
            } else {
                return '0%'
            }
        },

        getImprovementClass(value) {
            if (value > 0) {
                return 'positive'
            } else if (value < 0) {
                return 'negative'
            } else {
                return 'neutral'
            }
        },

        viewHistory() {
            console.log('📊 MinionTrainingCard viewHistory - minion object:', this.minion)
            console.log('📊 MinionTrainingCard viewHistory - minion.id:', this.minion.id)
            console.log('📊 MinionTrainingCard viewHistory - minion.display_name:', this.minion.display_name)
            this.$emit('view-history', this.minion)
        },

        upgradeMinion() {
            this.$emit('upgrade-minion', this.minion)
        },


        viewPendingJob() {
            this.$emit('view-pending-job', this.pendingJob)
        },

        startPendingTraining() {
            this.$emit('start-pending-training', this.pendingJob)
        },

        deletePendingJob() {
            this.$emit('delete-pending-job', this.pendingJob)
        },

        // Training overlay methods
        startTrainingProgress(jobId) {
            console.log('🚀 Starting training progress overlay for job:', jobId)
            this.showTrainingOverlay = true
            this.trainingCompleted = false
            this.trainingProgress = 0
            this.currentStepIndex = 0

            // Reset all steps
            this.trainingSteps.forEach(step => {
                step.completed = false
                step.active = false
            })

            // 🔥 SMART STATUS UPDATES: Start real-time polling when training begins
            this.startRealTimeStatusUpdates(jobId)

            // Start the training simulation
            this.simulateTrainingProgress(jobId)
        },

        startRealTimeStatusUpdates(jobId) {
            console.log('🔥 Smart Status Updates: ENABLING real-time polling for job:', jobId)
            
            // Clear any existing polling
            this.stopRealTimeStatusUpdates()
            
            // Start polling every 2 seconds during training
            this.pollingInterval = setInterval(() => {
                this.pollTrainingStatus(jobId)
            }, 2000)
        },

        stopRealTimeStatusUpdates() {
            if (this.pollingInterval) {
                console.log('🔥 Smart Status Updates: DISABLED - stopping real-time polling')
                clearInterval(this.pollingInterval)
                this.pollingInterval = null
            }
        },

        simulateTrainingProgress(jobId) {
            const steps = [
                { name: 'Dataset Loading', message: 'Loading training datasets...', duration: 2000 },
                { name: 'Dataset Refinement', message: 'Refining and cleaning data...', duration: 3000 },
                { name: 'Knowledge Base Creation', message: 'Creating knowledge base...', duration: 1000 },
                { name: 'Embedding Creation', message: 'Generating embeddings...', duration: 4000 },
                { name: 'Minion Update', message: 'Updating minion configuration...', duration: 1000 },
                { name: 'Training Validation', message: 'Validating training results...', duration: 2000 },
                { name: 'Testing', message: 'Testing minion capabilities...', duration: 1000 },
                { name: 'Metrics Collection', message: 'Collecting performance metrics...', duration: 1000 }
            ]

            let currentStep = 0
            const totalSteps = steps.length

            const executeStep = () => {
                if (currentStep >= totalSteps) {
                    this.completeTraining()
                    return
                }

                const step = steps[currentStep]
                const stepIndex = currentStep

                // Update status
                this.trainingStatus = 'Running'
                this.currentStepMessage = step.message

                // Activate current step
                this.trainingSteps[stepIndex].active = true

                // Update progress
                this.trainingProgress = Math.round(((stepIndex + 1) / totalSteps) * 100)

                // Poll for real training status
                this.pollTrainingStatus(jobId)

                // Complete step after duration
                setTimeout(() => {
                    this.trainingSteps[stepIndex].active = false
                    this.trainingSteps[stepIndex].completed = true
                    currentStep++
                    executeStep()
                }, step.duration)
            }

            executeStep()
        },

        async pollTrainingStatus(jobId) {
            try {
                // Real status polling from backend
                console.log('📊 Polling training status for job:', jobId)
                
                const response = await fetch(`http://localhost:5000/api/users/${this.authStore.user.id}/external-training/jobs/${jobId}`)
                const result = await response.json()
                
                if (result.success && result.job) {
                    const job = result.job
                    console.log('📊 Job status update:', job.status, job.progress)
                    
                    // Update UI based on real status
                    if (job.status === 'COMPLETED' || job.status === 'FAILED') {
                        this.completeTraining()
                        this.$emit('training-completed', job)
                    } else if (job.status === 'RUNNING') {
                        this.trainingStatus = 'Running'
                        this.trainingProgress = job.progress || this.trainingProgress
                    }
                }
            } catch (error) {
                console.error('Error polling training status:', error)
            }
        },

        completeTraining() {
            console.log('✅ Training completed - stopping status updates')
            this.trainingStatus = 'Completed'
            this.currentStepMessage = 'Training completed successfully!'
            this.trainingProgress = 100
            this.trainingCompleted = true

            // 🔥 SMART STATUS UPDATES: Auto-disable polling when training completes
            this.stopRealTimeStatusUpdates()

            // Emit event to parent to refresh data
            this.$emit('training-completed', this.minion.id)
        },

        closeTrainingOverlay() {
            console.log('❌ Training overlay closed - stopping status updates')
            this.showTrainingOverlay = false
            this.trainingCompleted = false

            // 🔥 SMART STATUS UPDATES: Stop polling when user closes overlay
            this.stopRealTimeStatusUpdates()
        }
    }
}
</script>

<style scoped>
.minion-training-card {
    border-radius: 13px;
    box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light);
    /* background: #d3d3d300; */
    /* box-shadow: rgba(50, 50, 93, 0.25) 0px 2px 10px 0px inset, rgba(0, 0, 0, 0.3) 0px 18px 26px -18px inset; */
    background: var(--card-bg);
    /* border-radius: 16px; */
    padding: 1.5rem;
    /* box-shadow: var(--card-shadow); */
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
}

.minion-training-card:hover {
    transform: translateY(-2px);
    /* box-shadow: var(--card-shadow-hover); */
}

.minion-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.btn.upgrade-btn {
    background-color: #4e73df;

}
.loading-spinner {
    box-shadow: none !important;
}
.progress-bar {
    border-radius: 3px;
}
.minion-avatar {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    overflow: hidden;
    flex-shrink: 0;
}

.minion-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.minion-info {
    flex: 1;
}

.minion-info h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
}

.minion-stats {
    display: flex;
    gap: 0.75rem;
    font-size: 0.85rem;
}

.minion-stats span {
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-weight: 500;
}

.level {
    background: var(--primary-light);
    color: var(--primary-color);
}

.xp {
    background: var(--success-light);
    color: var(--success-color);
}

.rank {
    background: var(--warning-light);
    color: var(--warning-color);
}

.minion-provider {
    flex-shrink: 0;
}

.provider-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.provider-badge.nvidia {
    background: #77B8FF;
    color: white;
}

.provider-badge.openai {
    background: #40A987;
    color: white;
}

.provider-badge.anthropic {
    background: #FF6500;
    color: white;
}

.training-info {
    margin-bottom: 1.5rem;
}

.training-info h4 {
    margin: 0 0 0.75rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}

.training-badges {
    display: flex;
    gap: 0.5rem;
}

.training-type {
    padding: 0.25rem 0.75rem;
    background: var(--info-light);
    color: var(--info-color);
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 500;
}

.training-status {
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 500;
}

.training-status.completed {
    background: #16c887;
    color: #ffffff;
}

.training-status.running {
    background: var(--warning-light);
    color: var(--warning-color);
}

.training-status.pending {
    /* background: var(--info-light); */
    background: #6f91f4;
    color: #ffffff;
}

.training-status.failed {
    background: var(--danger-light);
    color: var(--danger-color);
}

.improvements {
    margin-bottom: 1.5rem;
}

.improvements-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-weight: 600;
    color: var(--text-primary);
}

.improvements-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}
.btn.btn-train {
    background-color: #25ab25;
}
.btn.btn-cancel {
    background-color: #e45f5f;
}
.improvement-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-secondary);
    border-radius: 8px;
}

.improvement-icon {
    font-size: 1.2rem;
    color: var(--text-secondary);
}

.improvement-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.improvement-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.improvement-value {
    font-size: 0.9rem;
    font-weight: 600;
}

.improvement-value.positive {
    color: var(--success-color);
}

.improvement-value.negative {
    color: var(--danger-color);
}

.improvement-value.neutral {
    color: var(--text-secondary);
}

.training-count {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    padding: 0.75rem;
    background: var(--bg-secondary);
    border-radius: 8px;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.actions {
    display: flex;
    gap: 0.75rem;
}

.actions .btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s ease;
    border: none;
    cursor: pointer;
}

.btn-outline {
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.btn-outline:hover {
    background: var(--hover-bg);
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
    .minion-training-card {
        background: var(--dark-card-bg);
        border-color: var(--dark-border-color);
    }

    .minion-info h3 {
        color: var(--dark-text-primary);
    }

    .improvements-header {
        color: var(--dark-text-primary);
    }

    .improvement-item {
        background: var(--dark-bg-secondary);
    }

    .improvement-label {
        color: var(--dark-text-secondary);
    }

    .training-count {
        background: var(--dark-bg-secondary);
        color: var(--dark-text-secondary);
    }

    .btn-outline {
        color: var(--dark-text-primary);
        border-color: var(--dark-border-color);
    }

    .btn-outline:hover {
        background: var(--dark-hover-bg);
    }
}
</style>
