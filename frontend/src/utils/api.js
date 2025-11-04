/**
 * API Utility Functions
 * Helper functions for making API calls with proper error handling and authentication
 */

import { API_ENDPOINTS, getCurrentAPIBase } from '@/config/api'

/**
 * Make an authenticated API call
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} Response object
 */
export async function apiCall(endpoint, options = {}) {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers
    }
  }

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  }

  try {
    const response = await fetch(endpoint, config)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Unknown error' }))
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`)
    }

    return response
  } catch (error) {
    console.error('API Call failed:', error)
    throw error
  }
}

/**
 * Get data from API endpoint
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Parsed JSON response
 */
export async function getApiData(endpoint, options = {}) {
  const response = await apiCall(endpoint, { ...options, method: 'GET' })
  return response.json()
}

/**
 * Post data to API endpoint
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Data to send
 * @param {Object} options - Additional fetch options
 * @returns {Promise<Object>} Parsed JSON response
 */
export async function postApiData(endpoint, data = null, options = {}) {
  const response = await apiCall(endpoint, {
    ...options,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined
  })
  return response.json()
}

/**
 * Put data to API endpoint
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Data to send
 * @param {Object} options - Additional fetch options
 * @returns {Promise<Object>} Parsed JSON response
 */
export async function putApiData(endpoint, data = null, options = {}) {
  const response = await apiCall(endpoint, {
    ...options,
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined
  })
  return response.json()
}

/**
 * Delete from API endpoint
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Additional fetch options
 * @returns {Promise<Response>} Response object
 */
export async function deleteApiData(endpoint, options = {}) {
  return apiCall(endpoint, { ...options, method: 'DELETE' })
}

/**
 * Get user-specific API endpoint
 * @param {number|string} userId - User ID
 * @param {string} endpoint - Endpoint path
 * @param {...any} params - Additional parameters for URL building
 * @returns {string} Complete API endpoint URL
 */
export function getUserApiUrl(userId, endpoint, ...params) {
  const baseUrl = getCurrentAPIBase()
  let url = `${baseUrl}/users/${userId}/${endpoint}`
  
  // Replace parameters in URL
  params.forEach((param, index) => {
    url = url.replace(`{${index}}`, param)
  })
  return url
}

/**
 * Get API URL for avatars
 * @param {string} filename - Avatar filename
 * @returns {string} Avatar URL
 */
export function getAvatarUrl(filename) {
  const baseUrl = getCurrentAPIBase()
  return `${baseUrl}/avatars/${filename}`
}

/**
 * Get API URL for any path relative to base
 * @param {string} path - Path relative to API base
 * @returns {string} Complete API URL
 */
export function getApiUrl(path) {
  const baseUrl = getCurrentAPIBase()
  // Ensure path doesn't start with / to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  return `${baseUrl}/${cleanPath}`
}

/**
 * Quick reference to commonly used API endpoints
 */
export const API_HELPERS = {
  // V2 endpoints - currently active
  v2: {
    // Reference models
    getReferenceModels: () => API_ENDPOINTS.v2.referenceModels,
    
    // User minions
    getUserMinions: (userId) => getUserApiUrl(userId, 'minions'),
    getUserMinion: (userId, minionId) => getUserApiUrl(userId, `minions/${minionId}`),
    createMinion: (data) => postApiData(API_ENDPOINTS.v2.createMinion, data),
    
    // Spirits
    getSpirits: () => API_ENDPOINTS.v2.spirits,
    
    // Models
    getModels: () => API_ENDPOINTS.v2.models,
    getModelDetails: (modelName) => getApiUrl(`models/${encodeURIComponent(modelName)}`),
    
    // Datasets
    getDatasets: () => API_ENDPOINTS.v2.datasets,
    
    // Training jobs
    getTrainingJobs: () => API_ENDPOINTS.v2.trainingJobs,
    getTrainingJobStatus: (jobId) => getApiUrl(`training-jobs/${jobId}/status`),
    startTrainingJob: (jobId) => getApiUrl(`training-jobs/${jobId}/start`),
    stopTrainingJob: (jobId) => getApiUrl(`training-jobs/${jobId}/stop`),
    
    // External models
    getExternalModels: () => API_ENDPOINTS.v2.externalModels,
    
    // Avatars
    getAvatarUrl: getAvatarUrl,
    
    // Providers
    getProviders: () => API_ENDPOINTS.v2.providers
  },
  
  // Legacy V1 endpoints (for compatibility)
  v1: {
    getModels: () => API_ENDPOINTS.v1.models,
    getDatasets: () => API_ENDPOINTS.v1.datasets,
    getTrainingJobs: () => API_ENDPOINTS.v1.trainingJobs,
    // Add others as needed
  }
}

export default {
  apiCall,
  getApiData,
  postApiData,
  putApiData,
  deleteApiData,
  getUserApiUrl,
  getAvatarUrl,
  getApiUrl,
  API_HELPERS
}
