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
                    <span class="provider-badge" :class="minion.provider || 'external'">
                        {{ (minion.provider || 'external').toUpperCase() }}
                    </span>
                </div>
            </div>

            <!-- Class Information -->
            <div class="class-info" v-if="minion.class_name">
                <div class="class-badge">
                    <span class="material-icons class-icon">{{ getClassIcon(minion.class_name) }}</span>
                    <span class="class-name">{{ getClassDisplayName(minion.class_name) }}</span>
                </div>
                <div class="class-description">{{ getClassDescription(minion.class_name) }}</div>
            </div>

            <!-- Training Info -->
            <div class="training-info" v-if="minion.latest_training">
                <h4>{{ minion.latest_training.job_name }}</h4>
                <div class="training-badges">
                    <span class="training-type">{{ getTrainingTypeLabel(minion.latest_training.training_type) }}</span>
                    <span class="training-status" :class="(minion.latest_training.status || 'PENDING').toLowerCase()">
                        {{ getStatusLabel(minion.latest_training.status || 'PENDING') }}
                    </span>
                </div>
            </div>
            <div class="training-info" v-else>
                <h4>No training yet</h4>
                <div class="training-badges">
                    <span class="training-status pending">No history</span>
                </div>
            </div>

            <!-- Minion Stats -->
            <div class="improvements">
                <div class="improvements-header">
                    <span class="material-icons-round">trending_up</span>
                    <span>Minion Statistics</span>
                </div>
                <div class="improvements-grid">
                    <div class="improvement-item">
                        <span class="material-icons-round improvement-icon">memory</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Parameters</span>
                            <span class="improvement-value">{{ formatParameters(minion.parameters) }}</span>
                        </div>
                    </div>
                    <div class="improvement-item">
                        <span class="material-icons-round improvement-icon">speed</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Context Length</span>
                            <span class="improvement-value">{{ formatNumber(minion.context_length) }}</span>
                        </div>
                    </div>
                    <div class="improvement-item">
                        <span class="material-icons-round improvement-icon">tune</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Quantization</span>
                            <span class="improvement-value">{{ formatQuantization(minion.quantization, minion.parameters) }}</span>
                        </div>
                    </div>
                    <div class="improvement-item">
                        <span class="material-icons-round improvement-icon">star</span>
                        <div class="improvement-info">
                            <span class="improvement-label">Score</span>
                            <span class="improvement-value">{{ minion.score || 0 }}</span>
                        </div>
                    </div>
                    <!-- <div class="improvement-item level-rank-item">
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
                            <span class="improvement-value rank-value">{{ minion.rank_display_name || minion.rank || 'Novice' }}</span>
                        </div>
                    </div> -->
                </div>
            </div>

            <!-- Capabilities -->
            <div class="capabilities-section" v-if="minion.capabilities && minion.capabilities.length > 0">
                <div class="capabilities-header">
                    <span class="material-icons-round">psychology</span>
                    <span>Capabilities</span>
                </div>
                <div class="capabilities-list">
                    <span v-for="capability in minion.capabilities" :key="capability" class="capability-tag">
                        {{ capability }}
                    </span>
                </div>
            </div>

            <!-- Training Count / Pending Job -->
            <div class="training-count">
                <span class="material-icons-round">history</span>
                <template v-if="pendingJob">
                    <span class="pending-label">Pending Job: <strong>{{ pendingJob.job_name || pendingJob.jobName || pendingJob.jobName }}</strong></span>
                </template>
                <template v-else>
                    <span>{{ minion.training_count || 0 }} Previous Training{{ (minion.training_count || 0) !== 1 ? 's' : '' }}</span>
                </template>
            </div>

            <!-- Actions -->
            <div class="actions">
                <!-- Default actions when no pending job -->
                <template v-if="!hasPendingJob">
                    <button class="btn btn-outline" @click="viewHistory" :disabled="!hasTrainingHistory">
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
                            <div v-if="connecting" class="loading-spinner connecting">
                                <span class="material-icons-round">bolt</span>
                            </div>
                            <div v-else class="loading-spinner">
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
import { API_ENDPOINTS, getUserEndpoint, getAvatarUrl, getApiUrl } from '@/config/api'
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
            connecting: false,
            trainingStatus: 'Initializing RAG...',
            currentStepMessage: 'Preparing training environment...',
            trainingProgress: 0,
            trainingCompleted: false,
            socket: null, // Websocket connection
            trainingSteps: [
                { id: 0, name: 'Capture Before Metrics', completed: false, active: false },
                { id: 1, name: 'Dataset Loading & Refinement', completed: false, active: false },
                { id: 2, name: 'Knowledge Base Creation', completed: false, active: false },
                { id: 3, name: 'Embedding Creation', completed: false, active: false },
                { id: 4, name: 'Minion Update', completed: false, active: false },
                { id: 5, name: 'Training Validation', completed: false, active: false },
                { id: 6, name: 'Testing', completed: false, active: false },
                { id: 7, name: 'Capture After Metrics', completed: false, active: false },
                { id: 8, name: 'Calculate Improvements', completed: false, active: false }
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
        hasTrainingHistory() {
            // Check if minion has any training history
            return (this.minion.training_count && this.minion.training_count > 0) || 
                   (this.minion.latest_training && this.minion.latest_training.status === 'COMPLETED');
        },
        pendingJob() {
            // Find pending jobs for this minion (ignore completed/failed)
            let candidates = (this.pendingJobs || []).filter(job => 
                job.minionId === this.minion.id && 
                job.status !== 'COMPLETED' && 
                job.status !== 'completed' &&
                job.status !== 'FAILED' && 
                job.status !== 'failed'
            );
            
            if (!candidates.length) return null;

            // If the minion has a latest_training reference, only consider pending jobs
            // that were created after the latest training record. This prevents showing
            // pending controls when the latest training is already completed.
            try {
                const latestCreated = this.minion?.latest_training?.created_at;
                const latestStatus = this.minion?.latest_training?.status;
                
                if (latestCreated && latestStatus) {
                    // Only filter by date if latest training is COMPLETED
                    // If latest is PENDING/RUNNING, show it
                    if (latestStatus === 'COMPLETED' || latestStatus === 'completed') {
                        candidates = candidates.filter(j => new Date(j.created_at) > new Date(latestCreated));
                    }
                }
            } catch (e) {
                console.warn('Error filtering candidates by date:', e);
            }

            if (!candidates.length) return null;

            // Prefer the pending job that matches latest_training id if present
            // BUT only if latest_training is not COMPLETED
            const latestId = this.minion?.latest_training?.id;
            const latestStatus = this.minion?.latest_training?.status;
            
            if (latestId && latestStatus && latestStatus !== 'COMPLETED' && latestStatus !== 'completed') {
                const match = candidates.find(j => String(j.id) === String(latestId));
                if (match) return match;
            }

            // Otherwise return the most recently created pending job
            candidates.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            return candidates[0] || null;
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
                if (minion.avatar_url.startsWith('uploads/avatars/')) {
                    return getAvatarUrl(minion.avatar_url)
                }
                if (minion.avatar_url.startsWith('api/')) {
                    return getApiUrl(minion.avatar_url.replace('api/', ''))
                }
                return minion.avatar_url
            }
            if (minion.avatar_path) {
                // Extract filename from path and construct proper URL
                const filename = minion.avatar_path.split('/').pop()
                return getAvatarUrl(filename)
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
        },

        getClassDisplayName(className) {
            // Convert class name to display name
            const displayNames = {
                'Planner': 'Strategic Planner',
                'Developer': 'Full-Stack Developer',
                'Creative Assistant': 'Creative Assistant',
                'Data Scientist': 'Data Scientist',
                'API Integration Specialist': 'API Integration Specialist',
                'Security Specialist': 'Security Specialist',
                'Swiss Army Knife': 'Swiss Army Knife'
            }
            return displayNames[className] || className
        },

        getClassDescription(className) {
            // Get class description
            const descriptions = {
                'Planner': 'Strategic planning and problem-solving specialist',
                'Developer': 'Full-stack development with security focus',
                'Creative Assistant': 'Content creation and artistic design',
                'Data Scientist': 'Advanced data analysis and machine learning',
                'API Integration Specialist': 'System integration and API connectivity',
                'Security Specialist': 'Cybersecurity and vulnerability assessment',
                'Swiss Army Knife': 'General-purpose problem solving'
            }
            return descriptions[className] || 'Specialized minion class'
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

        formatParameters(parameters) {
            if (!parameters) return 'Unknown'
            if (typeof parameters === 'string') return parameters
            if (typeof parameters === 'object') {
                if (parameters.size) return parameters.size
                if (parameters.parameters) return parameters.parameters
                return Object.values(parameters).join(', ')
            }
            return String(parameters)
        },

        formatNumber(num) {
            if (!num) return 'N/A'
            return new Intl.NumberFormat().format(num)
        },

        formatQuantization(quantization, parameters) {
            if (quantization) return quantization
            if (parameters && parameters.quantization) return parameters.quantization
            return 'Unknown'
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

        setConnecting(val) {
            this.connecting = !!val
        },

        deletePendingJob() {
            // Call parent handler to delete by job id
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

            // 🔄 SMART STATUS UPDATES: Use polling as primary method (more reliable)
            this.startRealTimeStatusUpdates(jobId)
        },

        startWebsocketConnection(jobId) {
            console.log('🔌 Starting websocket connection for job:', jobId)
            
            // Import socket.io-client dynamically
            import('socket.io-client').then(({ io }) => {
                this.socket = io('http://localhost:5001', {
                    transports: ['websocket', 'polling']
                })
                
                // Join training room
                this.socket.emit('join_training_room', { job_id: jobId })
                
                // Listen for progress updates
                this.socket.on('training_progress', (data) => {
                    console.log('📡 Received training progress:', data)
                    this.updateTrainingProgressFromWebsocket(data)
                })
                
                // Listen for completion
                this.socket.on('training_completed', (data) => {
                    console.log('✅ Training completed via websocket:', data)
                    this.handleTrainingCompletion(data)
                })
                
                // Handle connection events
                this.socket.on('connect', () => {
                    console.log('🔌 Websocket connected')
                })
                
                this.socket.on('disconnect', () => {
                    console.log('🔌 Websocket disconnected')
                })
                
                this.socket.on('joined_room', (data) => {
                    console.log('🔌 Joined training room:', data)
                })
            }).catch(error => {
                console.error('❌ Failed to load socket.io-client:', error)
                // Fallback to polling
                this.startRealTimeStatusUpdates(jobId)
            })
        },
        
        updateTrainingProgressFromWebsocket(data) {
            const { step, step_name, progress_percent, message } = data
            
            // Update progress
            this.trainingProgress = progress_percent
            this.trainingStatus = 'Running'
            this.currentStepMessage = message || step_name
            
            // Update training steps
            this.trainingSteps.forEach((stepItem, index) => {
                if (index < step) {
                    stepItem.completed = true
                    stepItem.active = false
                } else if (index === step) {
                    stepItem.completed = false
                    stepItem.active = true
                } else {
                    stepItem.completed = false
                    stepItem.active = false
                }
            })
        },
        
        handleTrainingCompletion(data) {
            const { success, xp_gained, error_message } = data
            
            if (success) {
                this.trainingStatus = 'Completed'
                this.trainingProgress = 100
                this.trainingCompleted = true
                this.currentStepMessage = `Training completed! XP gained: ${xp_gained}`
                
                // Mark all steps as completed
                this.trainingSteps.forEach(step => {
                    step.completed = true
                    step.active = false
                })
                
                // Emit completion event
                this.$emit('training-completed', { xp_gained })
            } else {
                this.trainingStatus = 'Failed'
                this.trainingProgress = 0
                this.currentStepMessage = `Training failed: ${error_message}`
                this.showTrainingOverlay = false
            }
            
            // Close websocket connection
            this.closeWebsocketConnection()
        },
        
        closeWebsocketConnection() {
            if (this.socket) {
                console.log('🔌 Closing websocket connection')
                this.socket.disconnect()
                this.socket = null
            }
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

                // Use mapped auth state (this.user / this.token) instead of authStore
                if (!this.user) {
                    console.warn('No user available for polling; skipping');
                    return;
                }

                const url = getApiUrl(`training-jobs/${jobId}`)
                const response = await fetch(url, {
                    headers: {
                        ...(this.token ? { 'Authorization': `Bearer ${this.token}` } : {})
                    }
                })

                if (!response.ok) {
                    console.warn('Training job endpoint returned', response.status)
                    return
                }

                const result = await response.json()

                if (result.success && result.job) {
                    const job = result.job
                    const status = job.status
                    const progress = job.progress || 0
                    
                    console.log('📊 Job status update:', status, 'progress:', progress)

                    // Update UI based on real status
                    if (status === 'COMPLETED') {
                        this.completeTraining()
                        this.$emit('training-completed', { status, progress, xp_gained: job.xp_gained })
                    } else if (status === 'FAILED') {
                        this.trainingStatus = 'Failed'
                        this.trainingProgress = 0
                        this.currentStepMessage = 'Training failed: ' + (job.error_message || 'Unknown error')
                        this.stopRealTimeStatusUpdates()
                        // Keep overlay visible so user can see the error
                    } else if (status === 'RUNNING') {
                        this.trainingStatus = 'Running'
                        this.trainingProgress = progress
                        this.currentStepMessage = 'Training in progress...'
                        
                        // Update step indicators based on progress
                        const stepIndex = Math.floor((progress || 0) / (100 / this.trainingSteps.length))
                        this.currentStepIndex = Math.min(stepIndex, this.trainingSteps.length - 1)
                        
                        // Mark completed steps
                        for (let i = 0; i < this.currentStepIndex; i++) {
                            this.trainingSteps[i].completed = true
                            this.trainingSteps[i].active = false
                        }
                        
                        // Mark current step as active
                        if (this.trainingSteps[this.currentStepIndex]) {
                            this.trainingSteps[this.currentStepIndex].active = true
                            this.trainingSteps[this.currentStepIndex].completed = false
                        }
                    } else if (status === 'PENDING') {
                        this.trainingStatus = 'Pending'
                        this.trainingProgress = 0
                        this.currentStepMessage = 'Training job queued...'
                    }
                }
            } catch (error) {
                console.error('Error polling training status:', error)
            }
        },

        updateTrainingProgress(job) {
            console.log('📊 Updating training progress:', job);
            
            // Update progress based on job status
            if (job.status === 'RUNNING') {
                this.trainingStatus = 'Running'
                this.trainingProgress = job.progress || this.trainingProgress
                this.currentStepMessage = 'Training in progress...'
                
                // Update current step based on progress
                const stepIndex = Math.floor((job.progress || 0) / (100 / this.trainingSteps.length))
                this.currentStepIndex = Math.min(stepIndex, this.trainingSteps.length - 1)
                
                // Mark completed steps
                for (let i = 0; i < this.currentStepIndex; i++) {
                    this.trainingSteps[i].completed = true
                    this.trainingSteps[i].active = false
                }
                
                // Mark current step as active
                if (this.trainingSteps[this.currentStepIndex]) {
                    this.trainingSteps[this.currentStepIndex].active = true
                    this.trainingSteps[this.currentStepIndex].completed = false
                }
                
            } else if (job.status === 'COMPLETED') {
                this.completeTraining()
                this.$emit('training-completed', job)
                
            } else if (job.status === 'FAILED') {
                this.trainingStatus = 'Failed'
                this.trainingProgress = 0
                this.currentStepMessage = 'Training failed: ' + (job.error || 'Unknown error')
                this.stopRealTimeStatusUpdates()
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

            // ✅ KEEP OVERLAY VISIBLE - Don't close automatically
            // User can manually close with the X button

            // Emit event to parent to refresh data
            this.$emit('training-completed', this.minion.id)
        },

        closeTrainingOverlay() {
            console.log('❌ Training overlay closed - stopping status updates')
            this.showTrainingOverlay = false
            this.trainingCompleted = false

            // 🔥 SMART STATUS UPDATES: Stop polling when user closes overlay
            this.stopRealTimeStatusUpdates()
            
            // Close websocket connection
            this.closeWebsocketConnection()
        },

        // 🔄 SMART POLLING: Primary method for status updates (no websockets)
        startRealTimeStatusUpdates(jobId) {
            console.log('🔄 Starting smart polling for job:', jobId)
            
            // Clear any existing polling
            this.stopRealTimeStatusUpdates()
            
            // Start polling immediately
            this.pollTrainingStatus(jobId)
            
            // Set up regular polling every 3 seconds
            this.pollingInterval = setInterval(() => {
                if (this.showTrainingOverlay && !this.trainingCompleted) {
                    this.pollTrainingStatus(jobId)
                } else {
                    // Stop polling if overlay is closed or training completed
                    this.stopRealTimeStatusUpdates()
                }
            }, 3000) // Poll every 3 seconds
        },

        // 🛡️ POLLING FALLBACK: Backup method when websockets fail
        startPollingFallback(jobId) {
            console.log('🛡️ Starting polling fallback for job:', jobId)
            
            // Wait 10 seconds, then start polling if no websocket updates received
            setTimeout(() => {
                if (this.showTrainingOverlay && !this.trainingCompleted) {
                    console.log('🔄 No websocket updates received, starting polling fallback')
                    this.startRealTimeStatusUpdates(jobId)
                }
            }, 10000) // 10 second delay
        },

        // 🔍 SMART STATUS DETECTION: Check for running jobs when component loads
        async checkForRunningJobs() {
            try {
                console.log('🔍 Checking for running jobs for minion:', this.minion.id)
                
                // Check if there are any running jobs for this minion
                const url = getApiUrl(`users/${this.user.id}/external-training/jobs?group_by=minion&latest_only=true`)
                const response = await fetch(url, {
                    headers: {
                        ...(this.token ? { 'Authorization': `Bearer ${this.token}` } : {})
                    }
                })
                
                if (response.ok) {
                    const data = await response.json()
                    
                    // Find this minion in the results
                    if (data.minions) {
                        const minionData = data.minions.find(m => m.minion_id === this.minion.id)
                        
                        if (minionData && minionData.latest_job) {
                            const job = minionData.latest_job
                            
                            // If job is running, show overlay and start polling
                            if (job.status === 'RUNNING') {
                                console.log('🔄 Found running job:', job.id, 'starting polling')
                                this.showTrainingOverlay = true
                                this.trainingStatus = 'Running'
                                this.currentStepMessage = 'Training in progress...'
                                this.startRealTimeStatusUpdates(job.id)
                            }
                            // If job just completed, show completion state
                            else if (job.status === 'COMPLETED' && !this.trainingCompleted) {
                                console.log('✅ Found completed job:', job.id)
                                this.showTrainingOverlay = true
                                this.trainingStatus = 'Completed'
                                this.currentStepMessage = `Training completed! XP gained: ${job.xp_gained || 0}`
                                this.trainingProgress = 100
                                this.trainingCompleted = true
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Error checking for running jobs:', error)
            }
        }
    },
    
    mounted() {
        // 🔍 SMART STATUS DETECTION: Check for running jobs when component loads
        this.checkForRunningJobs()
    },

    beforeUnmount() {
        // Cleanup websocket connection
        this.closeWebsocketConnection()
        this.stopRealTimeStatusUpdates()
    }
}
</script>

<style scoped>
.minion-training-card {
    position: relative;
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

/* Class Information */
.class-info {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--primary-light);
    border: 1px solid var(--primary);
    border-radius: 8px;
}

.class-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.class-icon {
    font-size: 1.25rem;
    color: var(--primary);
}

.class-name {
    font-weight: 600;
    color: var(--primary);
    font-size: 1rem;
}

.class-description {
    font-size: 0.9rem;
    color: var(--text-color);
    line-height: 1.4;
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

.capabilities-section {
    margin-bottom: 1.5rem;
}

.capabilities-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
    color: var(--text-primary);
}

.capabilities-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.capability-tag {
    background-color: #1dd11d25;
    border: 1px solid #00800059;
    padding: 0.25rem 0.75rem;
    /* background: var(--info-light); */
    color: var(--info-color);
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 500;
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

.actions .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background-color: #6c757d;
    color: #fff;
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

/* Training Overlay Styles */
.training-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.overlay-content {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
  /* max-width: 400px; */
  width: 100%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  border: 5px solid #afdc33;
}

.overlay-header {
  margin-bottom: 20px;
}

.status-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  border-radius: 50%;
  animation: spin 2s linear infinite;
}

.loading-spinner .material-icons-round {
    color: #383838;
    font-size: 30px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-info h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.2rem;
  font-weight: 600;
}

.status-info p {
  margin: 4px 0 0 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #1baec6;
  border-radius: 4px;
  transition: width 0.5s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.training-steps {
  margin-bottom: 20px;
}

.training-step {
  display: flex;
  align-items: center;
  gap: 12px;
  /* padding: 8px 0; */
  transition: all 0.3s ease;
}

.step-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: all 0.3s ease;
}

.training-step.pending .step-icon {
  background: var(--border-color);
  color: var(--text-muted);
}

.training-step.active .step-icon {
  /* background: var(--primary-color); */
  color: white;
  animation: pulse 1.5s infinite;
}
.training-step.active .step-icon {
    background-color: #456ee4;
}
.training-step.active .step-icon .material-icons-round {
    color: #ffffff;
}
.training-step.completed .step-icon {
  background: var(--success-color);
  color: white;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.step-text {
  flex: 1;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.training-step.pending .step-text {
  color: var(--text-muted);
}

.training-step.active .step-text {
  color: var(--text-color);
  font-weight: 500;
}

.training-step.completed .step-text {
  color: var(--success-color);
  font-weight: 500;
}

.overlay-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-close-overlay {
  background: var(--border-color);
  color: var(--text-color);
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn-close-overlay:hover {
  background: var(--hover-bg);
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

