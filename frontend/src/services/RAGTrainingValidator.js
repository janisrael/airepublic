/**
 * RAG Training Validation Service
 * Frontend-only validation to detect duplicate training requests
 * Does NOT modify existing working code - purely additive
 */

class RAGTrainingValidator {
  constructor() {
    this.validationCache = new Map()
  }

  /**
   * Check if this training request is a duplicate
   * @param {Object} trainingData - The training configuration
   * @returns {Object} Validation result with recommendation
   */
  async validateTrainingRequest(trainingData) {
    try {
      const { minionId, selectedDatasets, ragConfig } = trainingData
      
      // Generate fingerprint for this training request
      const fingerprint = this.generateFingerprint(minionId, selectedDatasets, ragConfig)
      
      // Check cache first
      if (this.validationCache.has(fingerprint)) {
        return this.validationCache.get(fingerprint)
      }
      
      // Check against training history
      const duplicateCheck = await this.checkTrainingHistory(minionId, selectedDatasets, ragConfig)
      
      // Cache the result
      this.validationCache.set(fingerprint, duplicateCheck)
      
      return duplicateCheck
      
    } catch (error) {
      console.warn('RAG validation failed:', error)
      // If validation fails, allow training to proceed
      return {
        isDuplicate: false,
        recommendation: 'proceed',
        message: 'Validation unavailable - proceeding with training'
      }
    }
  }

  /**
   * Generate unique fingerprint for training request
   */
  generateFingerprint(minionId, selectedDatasets, ragConfig) {
    const datasetStr = selectedDatasets.sort().join(',')
    const configStr = JSON.stringify({
      collectionName: ragConfig.collectionName,
      embeddingModel: ragConfig.embeddingModel,
      chunkSize: ragConfig.chunkSize,
      chunkOverlap: ragConfig.chunkOverlap,
      knowledgeBaseStrategy: ragConfig.knowledgeBaseStrategy
    })
    
    return btoa(`${minionId}-${datasetStr}-${configStr}`)
  }

  /**
   * Check training history for duplicates
   */
  async checkTrainingHistory(minionId, selectedDatasets, ragConfig) {
    try {
      // Call backend to get training history for this minion
      const response = await fetch(`/api/v2/minions/${minionId}/training-history`)
      const data = await response.json()
      
      if (!data.success || !data.training_history) {
        return { isDuplicate: false, recommendation: 'proceed' }
      }
      
      // Check for duplicates
      const duplicates = this.findDuplicates(data.training_history, selectedDatasets, ragConfig)
      
      if (duplicates.length === 0) {
        return {
          isDuplicate: false,
          recommendation: 'proceed',
          message: 'No duplicate training detected'
        }
      }
      
      // Return duplicate information
      const latestDuplicate = duplicates[0] // Most recent
      return {
        isDuplicate: true,
        recommendation: this.getRecommendation(latestDuplicate, ragConfig),
        message: this.generateDuplicateMessage(latestDuplicate),
        duplicateInfo: latestDuplicate,
        allDuplicates: duplicates
      }
      
    } catch (error) {
      console.error('Error checking training history:', error)
      return { isDuplicate: false, recommendation: 'proceed' }
    }
  }

  /**
   * Find duplicate training records
   */
  findDuplicates(trainingHistory, selectedDatasets, ragConfig) {
    return trainingHistory.filter(record => {
      // Check if same datasets were used
      const recordDatasets = this.extractDatasetsFromRecord(record)
      const datasetsMatch = this.arraysEqual(recordDatasets, selectedDatasets)
      
      // Check if same collection name (for create_new strategy)
      const collectionMatch = ragConfig.knowledgeBaseStrategy === 'create_new' && 
                            record.collection_name === ragConfig.collectionName
      
      // Check if same embedding model and chunk settings
      const configMatch = this.configsMatch(record.rag_config, ragConfig)
      
      return datasetsMatch && (collectionMatch || configMatch)
    })
  }

  /**
   * Extract dataset IDs from training record
   */
  extractDatasetsFromRecord(record) {
    // Try to extract from rag_config or other fields
    if (record.rag_config && record.rag_config.selectedDatasets) {
      return record.rag_config.selectedDatasets
    }
    
    // Fallback - this might need adjustment based on actual data structure
    return []
  }

  /**
   * Check if two arrays are equal (order independent)
   */
  arraysEqual(arr1, arr2) {
    if (arr1.length !== arr2.length) return false
    const sorted1 = [...arr1].sort()
    const sorted2 = [...arr2].sort()
    return sorted1.every((val, index) => val === sorted2[index])
  }

  /**
   * Check if RAG configs match
   */
  configsMatch(recordConfig, newConfig) {
    if (!recordConfig || !newConfig) return false
    
    const keyFields = ['embeddingModel', 'chunkSize', 'chunkOverlap']
    return keyFields.every(field => 
      recordConfig[field] === newConfig[field]
    )
  }

  /**
   * Get recommendation based on duplicate type
   */
  getRecommendation(duplicateRecord, ragConfig) {
    // If using existing collection, it's safe to proceed
    if (ragConfig.knowledgeBaseStrategy === 'use_existing') {
      return 'proceed'
    }
    
    // If same collection name, suggest overwrite
    if (duplicateRecord.collection_name === ragConfig.collectionName) {
      return 'overwrite'
    }
    
    // Otherwise suggest creating new collection
    return 'create_new'
  }

  /**
   * Generate user-friendly duplicate message
   */
  generateDuplicateMessage(duplicateRecord) {
    const date = new Date(duplicateRecord.created_at).toLocaleDateString()
    const xp = duplicateRecord.xp_gained || 0
    
    return `This dataset combination was previously trained on ${date} (XP gained: ${xp}). What would you like to do?`
  }

  /**
   * Clear validation cache
   */
  clearCache() {
    this.validationCache.clear()
  }
}

// Export for use in components
export default RAGTrainingValidator
