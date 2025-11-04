/**
 * Spirit System Service
 * Connects frontend to the new spirit system API endpoints
 */

import { API_ENDPOINTS } from '@/config/api';

const SPIRIT_API_BASE = API_ENDPOINTS.v2.spirits;
const MINION_API_BASE = API_ENDPOINTS.v2.minions;

class SpiritService {
  constructor() {
    this.baseUrl = SPIRIT_API_BASE;
  }

  /**
   * Get all available spirits
   */
  async getAllSpirits() {
    try {
      const response = await fetch(`${this.baseUrl}/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error('Error fetching spirits:', error);
      return [];
    }
  }

  /**
   * Get free spirits only
   */
  async getFreeSpirits() {
    try {
      const response = await fetch(`${this.baseUrl}/free`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error('Error fetching free spirits:', error);
      return [];
    }
  }

  /**
   * Get spirits by pricing tier
   */
  async getSpiritsByTier(tier) {
    try {
      const response = await fetch(`${this.baseUrl}/tier/${tier}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error(`Error fetching ${tier} spirits:`, error);
      return [];
    }
  }

  /**
   * Get spirit by ID
   */
  async getSpiritById(id) {
    try {
      const response = await fetch(`${this.baseUrl}/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : null;
    } catch (error) {
      console.error(`Error fetching spirit ${id}:`, error);
      return null;
    }
  }

  /**
   * Get spirits available for user rank/level
   */
  async getAvailableSpirits(rank = 'Novice', level = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/available?rank=${rank}&level=${level}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error('Error fetching available spirits:', error);
      return [];
    }
  }

  /**
   * Calculate spirit synergy
   */
  async calculateSpiritSynergy(spiritIds) {
    try {
      const response = await fetch(`${this.baseUrl}/synergy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ spirit_ids: spiritIds })
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : null;
    } catch (error) {
      console.error('Error calculating spirit synergy:', error);
      return null;
    }
  }

  /**
   * Get spirit bundles
   */
  async getSpiritBundles() {
    try {
      const response = await fetch(`${this.baseUrl}/bundles`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error('Error fetching spirit bundles:', error);
      return [];
    }
  }

  /**
   * Get subscription plans
   */
  async getSubscriptionPlans() {
    try {
      const response = await fetch(`${this.baseUrl}/subscription-plans`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error('Error fetching subscription plans:', error);
      return [];
    }
  }

  /**
   * MINION-SPIRIT INTEGRATION METHODS
   */

  /**
   * Get spirits assigned to a minion
   */
  async getMinionSpirits(minionId) {
    try {
      const response = await fetch(`${MINION_API_BASE}/${minionId}/spirits`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error(`Error fetching spirits for minion ${minionId}:`, error);
      return [];
    }
  }

  /**
   * Get spirits available for assignment to a minion
   */
  async getAvailableSpiritsForMinion(minionId, userId = 1) {
    try {
      const response = await fetch(`${MINION_API_BASE}/${minionId}/spirits/available?user_id=${userId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error(`Error fetching available spirits for minion ${minionId}:`, error);
      return [];
    }
  }

  /**
   * Assign a spirit to a minion
   */
  async assignSpiritToMinion(minionId, spiritId, userId = 1) {
    try {
      const response = await fetch(`${MINION_API_BASE}/${minionId}/spirits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ spirit_id: spiritId, user_id: userId })
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Error assigning spirit ${spiritId} to minion ${minionId}:`, error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Remove a spirit from a minion
   */
  async removeSpiritFromMinion(minionId, spiritId) {
    try {
      const response = await fetch(`${MINION_API_BASE}/${minionId}/spirits/${spiritId}`, {
        method: 'DELETE'
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Error removing spirit ${spiritId} from minion ${minionId}:`, error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get minion spirit synergy
   */
  async getMinionSpiritSynergy(minionId) {
    try {
      const response = await fetch(`${MINION_API_BASE}/${minionId}/spirits/synergy`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data.data : null;
    } catch (error) {
      console.error(`Error fetching synergy for minion ${minionId}:`, error);
      return null;
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Spirit service health check failed:', error);
      return false;
    }
  }
}

// Create and export singleton instance
const spiritService = new SpiritService();
export default spiritService;
