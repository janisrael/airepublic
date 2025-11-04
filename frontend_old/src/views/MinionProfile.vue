<template>
  <div class="minion-profile-page">
    <!-- Header Section -->
    <div class="profile-header" v-if="minionData">
      <div class="header-background"></div>
      <button class="btn btn-back">
        <span class="material-icons-round" @click="handleback()">arrow_back</span>
      </button>
      <div class="header-content">
        <div class="profile-avatar-section">
          <div class="avatar-container">
            <img 
              :src="getAvatarUrl(minionData?.avatar_path || minionData?.avatar_url)" 
              :alt="minionData?.display_name"
              class="profile-avatar"
              @error="handleAvatarError"
            />
            <div class="avatar-status" :class="{ 'online': minionData?.is_active }"></div>
          </div>
          <div class="profile-basic-info">
            <h1 class="profile-name">{{ minionData?.display_name || 'Unknown Minion' }}</h1>
            <p class="profile-title">{{ minionData?.description || 'AI Assistant' }}</p>
            <div class="profile-badges">
              <span class="badge level-badge">Level {{ minionData?.level || 1 }}</span>
              <span class="badge provider-badge">{{ minionData?.provider || 'Unknown' }}</span>
              <span class="badge status-badge" :class="{ 'active': minionData?.is_active }">
                {{ minionData?.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="profile-actions">
          <button class="btn btn-primary" @click="chatWithMinion">
            <span class="material-icons-round">chat</span>
            Chat
          </button>
          <button class="btn btn-outline" @click="toggleFavorite">
            <span class="material-icons-round">{{ isFavorite ? 'favorite' : 'favorite_border' }}</span>
            {{ isFavorite ? 'Favorited' : 'Favorite' }}
          </button>
          <button class="btn btn-outline" @click="shareMinion">
            <span class="material-icons-round">share</span>
            Share
          </button>
          <button class="btn btn-outline" @click="regenerateToken" v-if="canManageToken">
            <span class="material-icons-round">refresh</span>
            Regenerate Token
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="profile-content" v-if="minionData">
      <div class="content-grid">
        <!-- Left Column -->
        <div class="left-column">
          <!-- About Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">info</span>
              About
            </h2>
            <div class="section-content">
              <p class="about-text">{{ minionData?.description || 'No description available.' }}</p>
              <div class="about-details">
                <div class="detail-item">
                  <span class="detail-label">Experience</span>
                  <span class="detail-value">{{ minionData?.experience || 0 }} XP</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Created</span>
                  <span class="detail-value">{{ formatDate(minionData?.created_at) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Last Updated</span>
                  <span class="detail-value">{{ formatDate(minionData?.updated_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Capabilities Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">psychology</span>
              Capabilities
            </h2>
            <div class="section-content">
              <div class="capabilities-grid">
                <div 
                  v-for="capability in capabilities" 
                  :key="capability"
                  class="capability-item"
                >
                  <span class="material-icons-round">check_circle</span>
                  {{ capability }}
                </div>
              </div>
            </div>
          </div>

          <!-- Configuration Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">settings</span>
              Configuration
            </h2>
            <div class="section-content">
              <div class="config-grid">
                <div class="config-item">
                  <span class="config-label">Model ID</span>
                  <span class="config-value">{{ minionData?.model_id || 'N/A' }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">Parameters</span>
                  <span class="config-value">{{ minionData?.parameters || 'N/A' }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">Context Length</span>
                  <span class="config-value">{{ formatNumber(minionData?.context_length) }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">Max Tokens</span>
                  <span class="config-value">{{ formatNumber(minionData?.max_tokens) }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">Temperature</span>
                  <span class="config-value">{{ minionData?.temperature || 'N/A' }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">Top P</span>
                  <span class="config-value">{{ minionData?.top_p || 'N/A' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- System Prompt Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">smart_toy</span>
              System Prompt
            </h2>
            <div class="section-content">
              <div class="system-prompt-container">
                <pre class="system-prompt">{{ minionData?.system_prompt || 'No system prompt defined.' }}</pre>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="right-column">
          <!-- Token Section -->
          <div class="profile-section token-section">
            <h2 class="section-title">
              <span class="material-icons-round">key</span>
              Minion Token
            </h2>
            <div class="section-content">
              <div class="token-container">
                <div class="token-display">
                  <code class="token-value">{{ minionData?.minion_token || 'No token available' }}</code>
                  <button class="btn-icon" @click="copyToken" title="Copy token">
                    <span class="material-icons-round">content_copy</span>
                  </button>
                </div>
                <div class="token-info">
                  <p class="token-description">
                    Use this token to authenticate with the Minion API. Keep it secure and don't share it publicly.
                  </p>
                  <div class="token-actions">
                    <button class="btn btn-sm btn-outline" @click="showTokenUsage">
                      <span class="material-icons-round">code</span>
                      API Usage
                    </button>
                    <button class="btn btn-sm btn-outline" @click="regenerateToken" v-if="canManageToken">
                      <span class="material-icons-round">refresh</span>
                      Regenerate
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Stats Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">analytics</span>
              Statistics
            </h2>
            <div class="section-content">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ stats.total_queries || 0 }}</div>
                  <div class="stat-label">Total Queries</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ formatNumber(stats.total_tokens_used) || 0 }}</div>
                  <div class="stat-label">Tokens Used</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ stats.average_response_time || 0 }}ms</div>
                  <div class="stat-label">Avg Response</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ formatDate(stats.last_used) || 'Never' }}</div>
                  <div class="stat-label">Last Used</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Tags Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">local_offer</span>
              Tags
            </h2>
            <div class="section-content">
              <div class="tags-container">
                <span 
                  v-for="tag in tags" 
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <!-- Skillset Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">build</span>
              Skillset & Tools
            </h2>
            <div class="section-content">
              <div class="skillset-grid">
                <div 
                  v-for="skill in skillset" 
                  :key="skill.name"
                  class="skill-card"
                  :class="{ 'active': skill.enabled }"
                >
                  <div class="skill-icon">
                    <span class="material-icons-round">{{ skill.icon }}</span>
                  </div>
                  <div class="skill-info">
                    <h4 class="skill-name">{{ skill.name }}</h4>
                    <p class="skill-description">{{ skill.description }}</p>
                    <div class="skill-meta">
                      <span class="skill-category">{{ skill.category }}</span>
                      <span class="skill-status" :class="{ 'enabled': skill.enabled }">
                        {{ skill.enabled ? 'Active' : 'Inactive' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <span class="material-icons-round">refresh</span>
      </div>
      <p>Loading minion profile...</p>
    </div>

    <!-- Toast Notifications -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      <span class="material-icons-round">{{ toast.icon }}</span>
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'MinionProfile',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      minionData: null,
      isLoading: true,
      isFavorite: false,
      minionId: null,
      canManageToken: false,
      stats: {
        total_queries: 0,
        total_tokens_used: 0,
        average_response_time: 0,
        last_used: null
      },
      toast: {
        show: false,
        message: '',
        type: 'success',
        icon: 'check_circle'
      },
      skillset: [
        {
          name: 'Web Search',
          description: 'Search the web for real-time information and current events',
          category: 'Information',
          icon: 'search',
          enabled: true
        },
        {
          name: 'File Operations',
          description: 'Read, write, and manage files on the system',
          category: 'System',
          icon: 'folder',
          enabled: true
        },
        {
          name: 'Code Execution',
          description: 'Execute Python code and scripts safely',
          category: 'Development',
          icon: 'code',
          enabled: true
        },
        {
          name: 'Database Query',
          description: 'Query and manipulate database records',
          category: 'Data',
          icon: 'storage',
          enabled: false
        },
        {
          name: 'API Integration',
          description: 'Make HTTP requests to external APIs',
          category: 'Integration',
          icon: 'api',
          enabled: true
        },
        {
          name: 'Image Processing',
          description: 'Generate, edit, and analyze images',
          category: 'Media',
          icon: 'image',
          enabled: false
        },
        {
          name: 'Email Operations',
          description: 'Send and receive emails programmatically',
          category: 'Communication',
          icon: 'email',
          enabled: false
        },
        {
          name: 'Calendar Management',
          description: 'Create and manage calendar events',
          category: 'Productivity',
          icon: 'event',
          enabled: false
        }
      ]
    }
  },
  computed: {
    capabilities() {
      if (!this.minionData?.capabilities) return []
      try {
        return JSON.parse(this.minionData.capabilities)
      } catch {
        return Array.isArray(this.minionData.capabilities) 
          ? this.minionData.capabilities 
          : [this.minionData.capabilities]
      }
    },
    tags() {
      if (!this.minionData?.tags) return []
      try {
        return JSON.parse(this.minionData.tags)
      } catch {
        return Array.isArray(this.minionData.tags) 
          ? this.minionData.tags 
          : [this.minionData.tags]
      }
    },
  },
  async mounted() {
    this.minionId = this.$route.params.id
    console.log('MinionProfile mounted - minionId:', this.minionId, 'route params:', this.$route.params)
    if (!this.minionId) {
      this.showToast('Invalid minion ID', 'error')
      return
    }
    
    // Set canManageToken based on user role
    this.canManageToken = this.authStore.user && (
      this.authStore.user.role_name === 'superuser' || 
      this.authStore.user.role_name === 'admin' ||
      this.authStore.user.role_name === 'developer'
    )
    
    await this.loadMinionProfile()
  },
  methods: {
    async loadMinionProfile() {
      this.isLoading = true
      try {
        const token = this.authStore.token
        if (!token) {
          this.showToast('Please log in to view minion profile', 'error')
          return
        }

        const response = await fetch(`http://localhost:5000/api/users/${this.authStore.user.id}/minions/${this.minionId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        const data = await response.json()
        
        if (data.success) {
          this.minionData = data.minion
          this.isFavorite = data.minion.is_favorite || false
          await this.loadMinionStats()
        } else {
          this.showToast('Failed to load minion profile', 'error')
        }
      } catch (error) {
        console.error('Error loading minion profile:', error)
        this.showToast('Error loading minion profile', 'error')
      } finally {
        this.isLoading = false
      }
    },

    async loadMinionStats() {
      try {
        // For now, use mock stats since the minion stats endpoint requires minion token
        // TODO: Implement proper minion stats endpoint with user authentication
        this.stats = {
          total_queries: 0,
          total_tokens_used: 0,
          average_response_time: 0,
          last_used: null,
          status: 'active'
        }
      } catch (error) {
        console.error('Error loading minion stats:', error)
      }
    },

    async chatWithMinion() {
      // Navigate to chat interface or open chat modal
      this.$router.push(`/chat/${this.minionId}`)
    },

    async toggleFavorite() {
      try {
        const token = this.authStore.token
        const response = await fetch(`http://localhost:5000/api/external-models/${this.minionId}/toggle-favorite`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        const data = await response.json()
        if (data.success) {
          this.isFavorite = !this.isFavorite
          this.showToast(
            this.isFavorite ? 'Added to favorites' : 'Removed from favorites', 
            'success'
          )
        }
      } catch (error) {
        console.error('Error toggling favorite:', error)
        this.showToast('Error updating favorite status', 'error')
      }
    },

    shareMinion() {
      if (navigator.share) {
        navigator.share({
          title: `${this.minionData.display_name} - AI Minion`,
          text: this.minionData.description,
          url: window.location.href
        })
      } else {
        this.copyToClipboard(window.location.href)
        this.showToast('Profile link copied to clipboard', 'success')
      }
    },

    async regenerateToken() {
      if (!confirm('Are you sure you want to regenerate the minion token? This will invalidate the current token.')) {
        return
      }

      try {
        const token = this.authStore.token
        const response = await fetch(`http://localhost:5000/api/users/${this.authStore.user.id}/minions/${this.minionId}/regenerate-token`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        const data = await response.json()
        if (data.success) {
          this.minionData.minion_token = data.new_token
          this.showToast('Token regenerated successfully', 'success')
        } else {
          this.showToast('Failed to regenerate token', 'error')
        }
      } catch (error) {
        console.error('Error regenerating token:', error)
        this.showToast('Error regenerating token', 'error')
      }
    },

    copyToken() {
      if (this.minionData?.minion_token) {
        this.copyToClipboard(this.minionData.minion_token)
        this.showToast('Token copied to clipboard', 'success')
      }
    },

    showTokenUsage() {
      // Show API usage examples modal or navigate to documentation
      this.showToast('API usage documentation coming soon', 'info')
    },

    copyToClipboard(text) {
      navigator.clipboard.writeText(text)
    },

    showToast(message, type = 'success') {
      this.toast = {
        show: true,
        message,
        type,
        icon: type === 'success' ? 'check_circle' : 
              type === 'error' ? 'error' : 
              type === 'info' ? 'info' : 'check_circle'
      }
      
      setTimeout(() => {
        this.toast.show = false
      }, 3000)
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },

    formatNumber(num) {
      if (!num) return 'N/A'
      return new Intl.NumberFormat().format(num)
    },
    handleback() {
      this.$router.go(-1)
    },
    getAvatarUrl(avatarUrl) {
      if (!avatarUrl) {
        return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iMzUiIHI9IjE1IiBmaWxsPSIjQ0NDQ0NDIi8+CjxwYXRoIGQ9Ik0yMCA4MEMyMCA2NS42NDA2IDMxLjY0MDYgNTQgNDYgNTRINTRDNjguMzU5NCA1NCA4MCA2NS42NDA2IDgwIDgwVjEwMEgyMFY4MFoiIGZpbGw9IiNDQ0NDQ0MiLz4KPC9zdmc+'
      }
      
      // If it's already a full URL, return as is
      if (avatarUrl.startsWith('http')) {
        return avatarUrl
      }
      
      // Extract filename from path
      let filename = avatarUrl
      if (avatarUrl.includes('/')) {
        filename = avatarUrl.split('/').pop()
      }
      
      // Use the avatar API endpoint
      return `http://localhost:5000/api/avatars/${filename}`
    },

    handleAvatarError(event) {
      // Fallback to inline SVG avatar if image fails to load
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iMzUiIHI9IjE1IiBmaWxsPSIjQ0NDQ0NDIi8+CjxwYXRoIGQ9Ik0yMCA4MEMyMCA2NS42NDA2IDMxLjY0MDYgNTQgNDYgNTRINTRDNjguMzU5NCA1NCA4MCA2NS42NDA2IDgwIDgwVjEwMEgyMFY4MFoiIGZpbGw9IiNDQ0NDQ0MiLz4KPC9zdmc+'
    }
  }
}
</script>

<style scoped>
.minion-profile-page {
  min-height: 100vh;
  /* background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); */
  position: relative;
}

/* Header Section */
.profile-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
  color: white;
  border-radius: 20px;
  margin-top: 20px;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

.header-content {
  /* max-width: 1200px; */
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  position: relative;
  z-index: 1;
}

.profile-avatar-section {
  display: flex;
  align-items: flex-end;
  gap: 2rem;
}

.avatar-container {
  position: relative;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid white;
  object-fit: cover;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.avatar-status {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid white;
  background: #e0e0e0;
}

.avatar-status.online {
  background: #4caf50;
}

.profile-basic-info h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
.profile-title{
  color: white;
}

.profile-title {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0 0 1rem 0;
}

.profile-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.level-badge {
  background: rgba(76, 175, 80, 0.8);
}

.provider-badge {
  background: rgba(33, 150, 243, 0.8);
}

.status-badge.active {
  background: rgba(76, 175, 80, 0.8);
}

.profile-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  position: absolute;
  right: 15px;
  top: -40px;
}
.profile-actions .btn {
  padding: 5px 10px;
}
.btn.btn-back {
  padding:5px;
  background-color: #ffffff;
  box-shadow: none;
  margin-left: 20px;
  margin-top: -20px;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
}

.btn-primary {
  background: white;
  color: #667eea;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
}

.btn-icon {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #f5f5f5;
  color: #333;
}

/* Main Content */
.profile-content {
  /* max-width: 1200px; */
  margin: 0 auto;
  padding-top: 2rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}

/* Profile Sections */
.profile-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: #333;
}

.section-content {
  color: #666;
  line-height: 1.6;
}

/* About Section */
.about-text {
  font-size: 1rem;
  margin-bottom: 1.5rem;
  color: #555;
}

.about-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.875rem;
  color: #888;
  font-weight: 500;
}

.detail-value {
  font-size: 1rem;
  color: #333;
  font-weight: 600;
}

/* Capabilities Section */
.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.capability-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  font-weight: 500;
  color: #333;
}

.capability-item .material-icons-round {
  color: #4caf50;
  font-size: 1.25rem;
}

/* Configuration Section */
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.config-label {
  font-size: 0.875rem;
  color: #888;
  font-weight: 500;
}

.config-value {
  font-size: 1rem;
  color: #333;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

/* Token Section */
.token-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.token-section .section-title {
  color: white;
}

.token-container {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.token-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.token-value {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  color: white;
  word-break: break-all;
  background: none;
  border: none;
  padding: 0;
}

.token-info {
  color: rgba(255, 255, 255, 0.9);
}

.token-description {
  font-size: 0.875rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.token-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.token-actions .btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.token-actions .btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Stats Section */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #888;
  font-weight: 500;
}

/* Tags Section */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  padding: 0.375rem 0.75rem;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid #bbdefb;
}

/* System Prompt Section */
.system-prompt-container {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e9ecef;
}

.system-prompt {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  line-height: 1.5;
}

/* Skillset Styles */
.skillset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.skill-card {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.skill-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.skill-card.active {
  border-color: #28a745;
  background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
}

.skill-card:not(.active) {
  opacity: 0.7;
  background: #f8f9fa;
}

.skill-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.skill-card.active .skill-icon {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
}

.skill-card:not(.active) .skill-icon {
  background: #6c757d;
}

.skill-icon .material-icons-round {
  font-size: 24px;
}

.skill-info {
  flex: 1;
  min-width: 0;
}

.skill-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
}

.skill-card:not(.active) .skill-name {
  color: #6c757d;
}

.skill-description {
  font-size: 0.875rem;
  color: #666;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.skill-card:not(.active) .skill-description {
  color: #adb5bd;
}

.skill-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.skill-category {
  font-size: 0.75rem;
  font-weight: 500;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.skill-card.active .skill-category {
  color: #28a745;
  background: rgba(40, 167, 69, 0.1);
}

.skill-card:not(.active) .skill-category {
  color: #6c757d;
  background: rgba(108, 117, 125, 0.1);
}

.skill-status {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.skill-status.enabled {
  color: #28a745;
  background: rgba(40, 167, 69, 0.1);
}

.skill-status:not(.enabled) {
  color: #dc3545;
  background: rgba(220, 53, 69, 0.1);
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-spinner .material-icons-round {
  font-size: 3rem;
  color: #667eea;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Toast Notifications */
.toast {
  position: fixed;
  top: 2rem;
  right: 2rem;
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 1001;
  animation: slideIn 0.3s ease;
}

.toast.success {
  border-left: 4px solid #4caf50;
}

.toast.error {
  border-left: 4px solid #f44336;
}

.toast.info {
  border-left: 4px solid #2196f3;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }
  
  .profile-avatar-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .profile-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .profile-name {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .capabilities-grid {
    grid-template-columns: 1fr;
  }
}
</style>
