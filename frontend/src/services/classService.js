/**
 * Class Service - API communication for minion classes
 * Handles all class-related API calls and data management
 */

import { getApiUrl } from '@/utils/api'

class ClassService {
  constructor() {
    this.baseUrl = getApiUrl('classes')
    this.cache = {
      classes: null,
      categories: null,
      lastFetch: null
    }
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
  }

  /**
   * Get all available classes for a user based on their rank and level
   * @param {string} userRank - User's current rank (Novice, Skilled, etc.)
   * @param {number} userLevel - User's current level
   * @returns {Promise<Array>} Array of available classes
   */
  async getAvailableClasses(userRank = 'Novice', userLevel = 1) {
    try {
      const response = await fetch(`${this.baseUrl}?user_rank=${userRank}&user_level=${userLevel}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        // Cache the results
        this.cache.classes = result.classes
        this.cache.lastFetch = Date.now()
        return result.classes
      } else {
        throw new Error(result.error || 'Failed to fetch available classes')
      }
    } catch (error) {
      console.error('Error fetching available classes:', error)
      throw error
    }
  }

  /**
   * Get detailed information about a specific class
   * @param {string} className - Name of the class to get details for
   * @returns {Promise<Object>} Class details including spirits and tools
   */
  async getClassDetails(className) {
    try {
      const response = await fetch(`${this.baseUrl}/${className}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        return result.class
      } else {
        throw new Error(result.error || 'Failed to fetch class details')
      }
    } catch (error) {
      console.error('Error fetching class details:', error)
      throw error
    }
  }

  /**
   * Check if user can unlock a specific class
   * @param {string} className - Name of the class to check
   * @param {string} userRank - User's current rank
   * @param {number} userLevel - User's current level
   * @returns {Promise<Object>} Unlock status and requirements
   */
  async checkUnlockRequirements(className, userRank, userLevel) {
    try {
      const response = await fetch(`${this.baseUrl}/${className}/unlock`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_rank: userRank,
          user_level: userLevel
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        return result
      } else {
        throw new Error(result.error || 'Failed to check unlock requirements')
      }
    } catch (error) {
      console.error('Error checking unlock requirements:', error)
      throw error
    }
  }

  /**
   * Install a class on a minion (assigns spirits and downloads desktop tools)
   * @param {number} minionId - ID of the minion
   * @param {string} className - Name of the class to install
   * @param {number} userId - ID of the user
   * @returns {Promise<Object>} Installation result
   */
  async installClassOnMinion(minionId, className, userId) {
    try {
      const response = await fetch(`${getApiUrl('minions')}/${minionId}/class`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          class_name: className,
          user_id: userId,
          install_desktop_tools: true // Flag to indicate desktop installation
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        return result
      } else {
        throw new Error(result.error || 'Failed to install class on minion')
      }
    } catch (error) {
      console.error('Error installing class on minion:', error)
      throw error
    }
  }

  /**
   * Get installation package for a class (spirits + desktop tools)
   * @param {string} className - Name of the class
   * @returns {Promise<Object>} Installation package details
   */
  async getClassInstallationPackage(className) {
    try {
      const response = await fetch(`${this.baseUrl}/${className}/installation-package`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        return result.package
      } else {
        throw new Error(result.error || 'Failed to get installation package')
      }
    } catch (error) {
      console.error('Error getting installation package:', error)
      throw error
    }
  }

  /**
   * Get the class assigned to a minion
   * @param {number} minionId - ID of the minion
   * @returns {Promise<Object|null>} Minion's assigned class or null
   */
  async getMinionClass(minionId) {
    try {
      const response = await fetch(`${getApiUrl('minions')}/${minionId}/class`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        return result.has_class ? result.class : null
      } else {
        throw new Error(result.error || 'Failed to fetch minion class')
      }
    } catch (error) {
      console.error('Error fetching minion class:', error)
      throw error
    }
  }

  /**
   * Get all spirits assigned to a minion
   * @param {number} minionId - ID of the minion
   * @returns {Promise<Array>} Array of assigned spirits
   */
  async getMinionSpirits(minionId) {
    try {
      const response = await fetch(`${getApiUrl('minions')}/${minionId}/spirits`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        return result.spirits
      } else {
        throw new Error(result.error || 'Failed to fetch minion spirits')
      }
    } catch (error) {
      console.error('Error fetching minion spirits:', error)
      throw error
    }
  }

  /**
   * Get all class categories
   * @returns {Promise<Object>} Categories with their classes
   */
  async getClassCategories() {
    try {
      // Check cache first
      if (this.cache.categories && this.cache.lastFetch && 
          (Date.now() - this.cache.lastFetch) < this.cacheTimeout) {
        return this.cache.categories
      }

      const response = await fetch(`${this.baseUrl}/categories`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        // Cache the results
        this.cache.categories = result.categories
        this.cache.lastFetch = Date.now()
        return result.categories
      } else {
        throw new Error(result.error || 'Failed to fetch class categories')
      }
    } catch (error) {
      console.error('Error fetching class categories:', error)
      throw error
    }
  }

  /**
   * Get class statistics
   * @returns {Promise<Object>} Class usage statistics
   */
  async getClassStatistics() {
    try {
      const response = await fetch(`${this.baseUrl}/statistics`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        return result.statistics
      } else {
        throw new Error(result.error || 'Failed to fetch class statistics')
      }
    } catch (error) {
      console.error('Error fetching class statistics:', error)
      throw error
    }
  }

  /**
   * Get detailed information about spirits in a class
   * @param {string} className - Name of the class
   * @returns {Promise<Array>} Array of spirits with their tools
   */
  async getClassSpirits(className) {
    try {
      const response = await fetch(`${this.baseUrl}/${className}/spirits`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        return result.spirits
      } else {
        throw new Error(result.error || 'Failed to fetch class spirits')
      }
    } catch (error) {
      console.error('Error fetching class spirits:', error)
      throw error
    }
  }

  /**
   * Clear the service cache
   */
  clearCache() {
    this.cache = {
      classes: null,
      categories: null,
      lastFetch: null
    }
  }

  /**
   * Get cached classes if available and not expired
   * @returns {Array|null} Cached classes or null
   */
  getCachedClasses() {
    if (this.cache.classes && this.cache.lastFetch && 
        (Date.now() - this.cache.lastFetch) < this.cacheTimeout) {
      return this.cache.classes
    }
    return null
  }

  /**
   * Get cached categories if available and not expired
   * @returns {Object|null} Cached categories or null
   */
  getCachedCategories() {
    if (this.cache.categories && this.cache.lastFetch && 
        (Date.now() - this.cache.lastFetch) < this.cacheTimeout) {
      return this.cache.categories
    }
    return null
  }
}

// Create and export a singleton instance
const classService = new ClassService()
export default classService
