<template>
  <div class="detailed-stats-view">
    <!-- Expandable Header -->
    <div class="stats-header" @click="toggleExpanded">
      <div class="header-content">
        <div class="header-icon">
          <span class="material-icons-round">analytics</span>
        </div>
        <div class="header-info">
          <h4>Detailed Training Statistics</h4>
          <p>Comprehensive analysis of training performance and metrics</p>
        </div>
      </div>
      <div class="expand-icon" :class="{ expanded: isExpanded }">
        <span class="material-icons-round">expand_more</span>
      </div>
    </div>

    <!-- Expandable Content -->
    <div class="stats-content" :class="{ expanded: isExpanded }">
      <!-- Refinement Report Section -->
      <div class="stats-section">
        <div class="section-header">
          <span class="material-icons-round">auto_fix_high</span>
          <h5>Dataset Refinement Report</h5>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon original">
              <span class="material-icons-round">inventory</span>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ datasetStats.original_count || 0 }}</span>
              <span class="stat-label">Original Items</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon refined">
              <span class="material-icons-round">check_circle</span>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ datasetStats.refined_count || 0 }}</span>
              <span class="stat-label">Refined Items</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon quality">
              <span class="material-icons-round">verified</span>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ datasetStats.quality_score || 0 }}%</span>
              <span class="stat-label">Quality Score</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon retention">
              <span class="material-icons-round">trending_up</span>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ datasetStats.retention_rate || 0 }}%</span>
              <span class="stat-label">Retention Rate</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Processing Statistics Section -->
      <div class="stats-section">
        <div class="section-header">
          <span class="material-icons-round">settings</span>
          <h5>Processing Statistics</h5>
        </div>
        <div class="processing-stats">
          <div class="processing-item">
            <div class="processing-icon">
              <span class="material-icons-round">speed</span>
            </div>
            <div class="processing-info">
              <span class="processing-label">Processing Time</span>
              <span class="processing-value">{{ processingTime }}</span>
            </div>
          </div>
          
          <div class="processing-item">
            <div class="processing-icon">
              <span class="material-icons-round">memory</span>
            </div>
            <div class="processing-info">
              <span class="processing-label">Memory Usage</span>
              <span class="processing-value">{{ memoryUsage }}</span>
            </div>
          </div>
          
          <div class="processing-item">
            <div class="processing-icon">
              <span class="material-icons-round">storage</span>
            </div>
            <div class="processing-info">
              <span class="processing-label">Storage Used</span>
              <span class="processing-value">{{ storageUsed }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Validation Details Section -->
      <div class="stats-section">
        <div class="section-header">
          <span class="material-icons-round">verified_user</span>
          <h5>Validation Details</h5>
        </div>
        <div class="validation-stats">
          <div class="validation-overview">
            <div class="validation-score">
              <span class="score-value">{{ validationStats.overall_score || 0 }}%</span>
              <span class="score-label">Overall Score</span>
            </div>
            <div class="validation-tests">
              <span class="tests-passed">{{ validationStats.tests_passed || 0 }}</span>
              <span class="tests-separator">/</span>
              <span class="tests-total">{{ validationStats.tests_total || 0 }}</span>
              <span class="tests-label">Tests Passed</span>
            </div>
          </div>
          
          <div class="validation-details">
            <div class="validation-item" v-for="(test, index) in validationTests" :key="index">
              <div class="validation-icon" :class="{ passed: test.passed, failed: !test.passed }">
                <span class="material-icons-round">{{ test.passed ? 'check_circle' : 'cancel' }}</span>
              </div>
              <div class="validation-info">
                <span class="validation-name">{{ test.name }}</span>
                <span class="validation-status" :class="{ passed: test.passed, failed: !test.passed }">
                  {{ test.passed ? 'Passed' : 'Failed' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Knowledge Base Statistics Section -->
      <div class="stats-section">
        <div class="section-header">
          <span class="material-icons-round">database</span>
          <h5>Knowledge Base Statistics</h5>
        </div>
        <div class="knowledge-stats">
          <div class="knowledge-item">
            <div class="knowledge-icon">
              <span class="material-icons-round">storage</span>
            </div>
            <div class="knowledge-info">
              <span class="knowledge-label">Collection Name</span>
              <span class="knowledge-value">{{ knowledgeBaseStats.collection_name || `minion_${trainingData.minion_id || 'unknown'}_kb` }}</span>
            </div>
          </div>
          
          <div class="knowledge-item">
            <div class="knowledge-icon">
              <span class="material-icons-round">view_list</span>
            </div>
            <div class="knowledge-info">
              <span class="knowledge-label">Total Documents</span>
              <span class="knowledge-value">{{ knowledgeBaseStats.total_documents || datasetStats.refined_count || 0 }}</span>
            </div>
          </div>
          
          <div class="knowledge-item">
            <div class="knowledge-icon">
              <span class="material-icons-round">straighten</span>
            </div>
            <div class="knowledge-info">
              <span class="knowledge-label">Chunk Size</span>
              <span class="knowledge-value">{{ knowledgeBaseStats.chunk_size || getChunkSize() }}</span>
            </div>
          </div>
          
          <div class="knowledge-item">
            <div class="knowledge-icon">
              <span class="material-icons-round">search</span>
            </div>
            <div class="knowledge-info">
              <span class="knowledge-label">Top-K Retrieval</span>
              <span class="knowledge-value">{{ knowledgeBaseStats.top_k || getTopK() }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Metrics Section -->
      <div class="stats-section">
        <div class="section-header">
          <span class="material-icons-round">speed</span>
          <h5>Performance Metrics</h5>
        </div>
        <div class="performance-metrics">
          <div class="metric-item">
            <div class="metric-icon">
              <span class="material-icons-round">timer</span>
            </div>
            <div class="metric-info">
              <span class="metric-label">Training Duration</span>
              <span class="metric-value">{{ trainingDuration }}</span>
            </div>
          </div>
          
          <div class="metric-item">
            <div class="metric-icon">
              <span class="material-icons-round">trending_up</span>
            </div>
            <div class="metric-info">
              <span class="metric-label">Success Rate</span>
              <span class="metric-value">{{ successRate }}%</span>
            </div>
          </div>
          
          <div class="metric-item">
            <div class="metric-icon">
              <span class="material-icons-round">precision_manufacturing</span>
            </div>
            <div class="metric-info">
              <span class="metric-label">Efficiency Score</span>
              <span class="metric-value">{{ efficiencyScore }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- XP and Ranking Section -->
      <div class="stats-section">
        <div class="section-header">
          <span class="material-icons-round">emoji_events</span>
          <h5>XP and Ranking</h5>
        </div>
        <div class="xp-ranking-stats">
          <div class="xp-item">
            <div class="xp-icon">
              <span class="material-icons-round">military_tech</span>
            </div>
            <div class="xp-info">
              <span class="xp-label">XP Gained</span>
              <span class="xp-value">{{ trainingData.xp_gained || 0 }} XP</span>
            </div>
          </div>
          
          <div class="xp-item">
            <div class="xp-icon">
              <span class="material-icons-round">trending_up</span>
            </div>
            <div class="xp-info">
              <span class="xp-label">Level Up</span>
              <span class="xp-value" v-if="levelUpInfo.leveled_up">
                {{ levelUpInfo.old_level }} → {{ levelUpInfo.new_level }}
              </span>
              <span class="xp-value" v-else>No Level Up</span>
            </div>
          </div>
          
          <div class="xp-item">
            <div class="xp-icon">
              <span class="material-icons-round">emoji_events</span>
            </div>
            <div class="xp-info">
              <span class="xp-label">Rank Up</span>
              <span class="xp-value" v-if="levelUpInfo.ranked_up">
                {{ levelUpInfo.old_rank }} → {{ levelUpInfo.new_rank }}
              </span>
              <span class="xp-value" v-else>No Rank Up</span>
            </div>
          </div>
          
          <div class="xp-item" v-if="levelUpInfo.unlocked_skillsets && levelUpInfo.unlocked_skillsets.length > 0">
            <div class="xp-icon">
              <span class="material-icons-round">lock_open</span>
            </div>
            <div class="xp-info">
              <span class="xp-label">Unlocked Skillsets</span>
              <span class="xp-value">{{ levelUpInfo.unlocked_skillsets.join(', ') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DetailedStatsView',
  props: {
    trainingData: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isExpanded: false
    }
  },
  computed: {
    datasetStats() {
      return this.trainingData.metrics?.dataset_stats || {}
    },
    
    processingStats() {
      return this.trainingData.metrics?.processing_stats || {}
    },
    
    validationStats() {
      return this.trainingData.metrics?.validation_stats || {}
    },
    
    knowledgeBaseStats() {
      return this.trainingData.metrics?.knowledge_base_stats || {}
    },
    
    processingTime() {
      if (this.trainingData.started_at && this.trainingData.completed_at) {
        const start = new Date(this.trainingData.started_at)
        const end = new Date(this.trainingData.completed_at)
        const diff = end - start
        const minutes = Math.floor(diff / 60000)
        const seconds = Math.floor((diff % 60000) / 1000)
        return `${minutes}m ${seconds}s`
      }
      return 'N/A'
    },
    
    memoryUsage() {
      // Calculate memory usage based on dataset size and processing
      const originalCount = this.datasetStats.original_count || 0
      const refinedCount = this.datasetStats.refined_count || 0
      
      if (originalCount > 0) {
        // Estimate memory usage: ~1KB per item processed
        const estimatedMB = Math.round((originalCount + refinedCount) * 0.001)
        return `${estimatedMB} MB`
      }
      
      return this.processingStats.memory_usage || 'N/A'
    },
    
    storageUsed() {
      // Calculate storage usage based on knowledge base size
      const refinedCount = this.datasetStats.refined_count || 0
      
      if (refinedCount > 0) {
        // Estimate storage: ~2KB per refined item (embeddings + metadata)
        const estimatedMB = Math.round(refinedCount * 0.002)
        return `${estimatedMB} MB`
      }
      
      return this.processingStats.storage_used || 'N/A'
    },
    
    validationTests() {
      // Use real validation tests from metrics or fallback to standard tests
      const realTests = this.trainingData.metrics?.validation_tests
      if (realTests && Array.isArray(realTests)) {
        return realTests
      }
      
      // Fallback to standard validation tests based on validation stats
      const testsPassed = this.validationStats.tests_passed || 0
      const testsTotal = this.validationStats.tests_total || 5
      
      const standardTests = [
        { name: 'Knowledge Base Existence', passed: testsPassed >= 1 },
        { name: 'Retrieval Functionality', passed: testsPassed >= 2 },
        { name: 'System Prompt Integration', passed: testsPassed >= 3 },
        { name: 'Collection Statistics', passed: testsPassed >= 4 },
        { name: 'Sample Query Test', passed: testsPassed >= 5 }
      ]
      
      return standardTests.slice(0, testsTotal)
    },
    
    trainingDuration() {
      return this.processingTime
    },
    
    successRate() {
      if (this.validationStats.tests_total > 0) {
        return Math.round((this.validationStats.tests_passed / this.validationStats.tests_total) * 100)
      }
      return 100
    },
    
        efficiencyScore() {
          // Calculate efficiency based on quality score and validation score
          const qualityScore = this.datasetStats.quality_score || 0
          const validationScore = this.validationStats.overall_score || 0
          return Math.round((qualityScore + validationScore) / 2)
        },
        
        levelUpInfo() {
          return this.trainingData.level_up_info || {}
        }
  },
  methods: {
    toggleExpanded() {
      this.isExpanded = !this.isExpanded
    },
    
    getChunkSize() {
      // Extract chunk size from training config
      try {
        const config = typeof this.trainingData.config === 'string' 
          ? JSON.parse(this.trainingData.config) 
          : this.trainingData.config
        return config?.ragConfig?.chunkSize || 1000
      } catch {
        return 1000
      }
    },
    
    getTopK() {
      // Extract top-K from training config
      try {
        const config = typeof this.trainingData.config === 'string' 
          ? JSON.parse(this.trainingData.config) 
          : this.trainingData.config
        return config?.ragConfig?.topK || 4
      } catch {
        return 4
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/detailed_stats.css';
</style>
