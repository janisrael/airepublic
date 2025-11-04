/**
 * API Configuration for AI Refinement Dashboard
 * Centralized configuration for API endpoints
 */

// Environment-based API configuration using .env variables
const API_CONFIG = {
  V1_BASE_URL: import.meta.env.VITE_V1_BASE_URL || 'http://localhost:5001/api', // V1 server (now using port 5001)
  V2_BASE_URL: import.meta.env.VITE_V2_BASE_URL || 'http://localhost:5001/api', // V2 PostgreSQL server
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api', // Use V2 server
  AUTH_ENDPOINT: import.meta.env.VITE_AUTH_ENDPOINT || 'http://localhost:5001/api/auth', // Use V2 server
  CURRENT_VERSION: import.meta.env.VITE_API_VERSION || 'v2', // Use V2 PostgreSQL
  DEV_MODE: import.meta.env.VITE_DEV_MODE === 'true',
  DEBUG_API_CALLS: import.meta.env.VITE_DEBUG_API_CALLS === 'true'
}

// Get current configuration
const config = API_CONFIG

// API endpoints
export const API_ENDPOINTS = {
  // Authentication endpoints
  auth: {
    login: `${config.AUTH_ENDPOINT}/login`,
    register: `${config.AUTH_ENDPOINT}/register`,
    logout: `${config.AUTH_ENDPOINT}/logout`,
    refresh: `${config.AUTH_ENDPOINT}/refresh`,
    verify: `${config.AUTH_ENDPOINT}/verify`,
    profile: `${config.AUTH_ENDPOINT}/profile`,
    forgotPassword: `${config.AUTH_ENDPOINT}/forgot-password`,
    resetPassword: `${config.AUTH_ENDPOINT}/reset-password`,
    changePassword: `${config.AUTH_ENDPOINT}/change-password`,
    social: (provider, action = 'login') => 
      `${config.AUTH_ENDPOINT}/social/${provider}${action === 'register' ? '?action=register' : ''}`
  },

  // V2 Specific endpoints (PostgreSQL + SQLAlchemy) - Clean /api/v2/ structure
  v2: {
    referenceModels: `${config.API_BASE_URL}/v2/reference-models`,
    userMinions: `${config.API_BASE_URL}/v2/user-minions`,
    spirits: `${config.API_BASE_URL}/v2/spirits`,
    status: `${config.API_BASE_URL}/status`,
    models: `${config.API_BASE_URL}/v2/models`,
    datasets: `${config.API_BASE_URL}/v2/datasets`,
    trainingJobs: `${config.API_BASE_URL}/v2/training-jobs`,
    externalModels: `${config.API_BASE_URL}/v2/external-models`,
    minions: `${config.API_BASE_URL}/v2/minions`,
    spiritsMinion: `${config.API_BASE_URL}/v2/spirits/minion`,
    createMinion: `${config.API_BASE_URL}/v2/minions`,
    loadDataset: `${config.API_BASE_URL}/v2/load-dataset`,
    startTraining: `${config.API_BASE_URL}/start-training`,
    detectStuckTraining: `${config.API_BASE_URL}/detect-stuck-training`,
    chromadbCollections: `${config.API_BASE_URL}/chromadb/collections`,
    evaluations: `${config.API_BASE_URL}/evaluations`,
    providers: `${config.API_BASE_URL}/providers`,
    avatars: `${config.API_BASE_URL}/avatars`,
  },

  // V1 Legacy endpoints (SQLite)
  v1: {
    models: `${config.V1_BASE_URL}/models`,
    datasets: `${config.V1_BASE_URL}/datasets`,
    trainingJobs: `${config.V1_BASE_URL}/training-jobs`,
    externalModels: `${config.V1_BASE_URL}/external-models`,
    minions: `${config.V1_BASE_URL}/minions`,
    referenceModels: `${config.V1_BASE_URL}/reference-models`,
    loadDataset: `${config.V1_BASE_URL}/load-dataset`,
    startTraining: `${config.V1_BASE_URL}/start-training`,
    detectStuckTraining: `${config.V1_BASE_URL}/detect-stuck-training`,
    chromadbCollections: `${config.V1_BASE_URL}/chromadb/collections`,
    evaluations: `${config.V1_BASE_URL}/evaluations`,
    providers: `${config.V1_BASE_URL}/providers`,
    avatars: `${config.V1_BASE_URL}/avatars`,
  }
}

// Helper function to get current API base URL
export const getCurrentAPIBase = () => {
  return config.CURRENT_VERSION === 'v2' ? `${config.API_BASE_URL}/v2` : config.V1_BASE_URL
}

// Helper function to get API endpoint based on current version
export const getAPIEndpoint = (category, endpoint, ...params) => {
  const version = config.CURRENT_VERSION
  const baseURL = version === 'v2' ? config.API_BASE_URL : config.V1_BASE_URL
  
  if (version === 'v2' && API_ENDPOINTS.v2[endpoint]) {
    let url = API_ENDPOINTS.v2[endpoint]
    // Replace parameters in URL
    params.forEach((param, index) => {
      url = url.replace(`{${index}}`, param)
    })
    return url
  } else if (API_ENDPOINTS.v1[endpoint]) {
    let url = API_ENDPOINTS.v1[endpoint]
    // Replace parameters in URL
    params.forEach((param, index) => {
      url = url.replace(`{${index}}`, param)
    })
    return url
  }
  
  // Fallback to generic endpoint construction
  return `${baseURL}/${category}/${endpoint}`
}

// Helper function to get user-specific endpoints
export const getUserEndpoint = (userId, endpoint, ...params) => {
  const version = config.CURRENT_VERSION
  if (version === 'v2') {
    return `${config.API_BASE_URL}/v2/users/${userId}/${endpoint}`
  }
  return `${config.V1_BASE_URL}/users/${userId}/${endpoint}`
}

// Helper function to get avatar URLs
export const getAvatarUrl = (filename) => {
  if (!filename) {
    // Return default avatar from server
    const serverBaseUrl = config.API_BASE_URL.replace('/api', '')
    return `${serverBaseUrl}/uploads/avatars/default-avatar.png`
  }
  
  // Get the server base URL (without /api/v2)
  const serverBaseUrl = config.API_BASE_URL.replace('/api', '')
  
  // If filename already includes the full path, use it directly
  if (filename.startsWith('uploads/avatars/')) {
    return `${serverBaseUrl}/${filename}`
  }
  
  // Otherwise, assume it's just the filename
  return `${serverBaseUrl}/uploads/avatars/${filename}`
}

// Helper function to get user-specific API URLs
export const getUserApiUrl = (userId, endpoint, ...params) => {
  const version = config.CURRENT_VERSION
  const baseUrl = version === 'v2' ? `${config.API_BASE_URL}/v2` : getCurrentAPIBase()
  let url = `${baseUrl}/users/${userId}/${endpoint}`
  
  // Append parameters to URL
  if (params.length > 0) {
    url += '/' + params.join('/')
  }
  return url
}

// Helper function to get API URL for any path relative to base
export const getApiUrl = (path) => {
  const baseUrl = getCurrentAPIBase()
  // Ensure path doesn't start with / to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  return `${baseUrl}/${cleanPath}`
}

// Export configuration
export default {
  ...config,
  endpoints: API_ENDPOINTS
}
