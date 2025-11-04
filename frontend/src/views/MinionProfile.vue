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
            <!-- Display Mode -->
            <div v-if="!editingBasicInfo">
              <h1 class="profile-name">{{ minionData?.display_name || 'Unknown Minion' }}</h1>
              <p class="profile-title">{{ minionData?.title || 'AI Assistant' }}</p>
              <p class="profile-description">{{ minionData?.description || 'AI Assistant' }}</p>
              <div class="profile-badges">
                <span class="badge level-badge">Level {{ minionData?.level || 1 }}</span>
                <span class="badge provider-badge">{{ minionData?.provider || 'External Model' }}</span>
                <span class="badge company-badge">{{ minionData?.company || 'AI Republic' }}</span>
                <span class="badge status-badge" :class="{ 'active': minionData?.is_active }">
                  {{ minionData?.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <button class="btn btn-sm btn-outline" @click="editBasicInfo" v-if="canEdit">
                <span class="material-icons-round">edit</span>
                Edit Basic Info
              </button>
            </div>
            
            <!-- Edit Mode -->
            <div v-else class="edit-form">
              <div class="form-group">
                <label for="display_name">Display Name</label>
                <input 
                  id="display_name"
                  v-model="editForm.display_name" 
                  type="text" 
                  class="form-control"
                  :class="{ 'error': formErrors.display_name }"
                  placeholder="Enter display name"
                />
                <span v-if="formErrors.display_name" class="error-message">{{ formErrors.display_name }}</span>
              </div>
              
              <div class="form-group">
                <label for="title">Title</label>
                <input 
                  id="title"
                  v-model="editForm.title" 
                  type="text" 
                  class="form-control"
                  :class="{ 'error': formErrors.title }"
                  placeholder="Enter title (e.g., Strategic Planning Specialist)"
                />
                <span v-if="formErrors.title" class="error-message">{{ formErrors.title }}</span>
              </div>
              
              <div class="form-group">
                <label for="description">Description</label>
                <textarea 
                  id="description"
                  v-model="editForm.description" 
                  class="form-control"
                  :class="{ 'error': formErrors.description }"
                  placeholder="Enter description"
                  rows="3"
                ></textarea>
                <span v-if="formErrors.description" class="error-message">{{ formErrors.description }}</span>
              </div>
              
              <div class="form-actions">
                <button 
                  class="btn btn-primary" 
                  @click="saveBasicInfo"
                  :disabled="saving"
                >
                  <span v-if="saving" class="material-icons-round">hourglass_empty</span>
                  <span v-else class="material-icons-round">save</span>
                  {{ saving ? 'Saving...' : 'Save' }}
                </button>
                <button 
                  class="btn btn-outline" 
                  @click="cancelEdit('BasicInfo')"
                  :disabled="saving"
                >
                  <span class="material-icons-round">cancel</span>
                  Cancel
                </button>
              </div>
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
              <div class="capabilities-grid" v-if="capabilities.length > 0">
                <div 
                  v-for="capability in capabilities" 
                  :key="capability"
                  class="capability-item"
                >
                  <span class="material-icons-round">check_circle</span>
                  {{ capability }}
                </div>
              </div>
              <div v-else class="no-capabilities">
                <span class="material-icons-round">info</span>
                <p>No specific capabilities defined. This minion can perform general AI tasks.</p>
              </div>
            </div>
          </div>

          <!-- Traits Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">psychology</span>
              Traits System
              <button class="btn btn-sm btn-outline" @click="editTraits" v-if="canEdit">
                <span class="material-icons-round">edit</span>
                Edit
              </button>
            </h2>
            <div class="section-content">
              <div v-if="traitsData" class="traits-container">
                <!-- Traits Overview -->
                <div class="traits-overview">
                  <div class="traits-stats">
                    <div class="stat-item">
                      <span class="stat-label">Available Slots</span>
                      <span class="stat-value">{{ traitsData.slots || 0 }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">Points Available</span>
                      <span class="stat-value">{{ traitsData.points_available || 0 }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">Points Spent</span>
                      <span class="stat-value">{{ traitsData.points_spent || 0 }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">Compatibility</span>
                      <span class="stat-value">{{ traitsData.compatibility_score || 0 }}%</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">Effectiveness Bonus</span>
                      <span class="stat-value">{{ traitsData.effectiveness_bonus || 0 }}%</span>
                    </div>
                  </div>
                </div>
                
                <!-- Active Traits -->
                <div class="active-traits" v-if="activeTraits.length > 0">
                  <h3 class="subsection-title">Active Traits</h3>
                  <div class="traits-grid">
                    <div 
                      v-for="(intensity, trait) in traitsData.traits_intensities" 
                      :key="trait"
                      class="trait-card"
                    >
                      <div class="trait-header">
                        <span class="trait-name">{{ trait }}</span>
                        <span class="trait-intensity">{{ intensity }}</span>
                      </div>
                      <div class="trait-bar">
                        <div 
                          class="trait-progress" 
                          :style="{ width: `${(intensity / 10) * 100}%` }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-else class="no-traits">
                  <span class="material-icons-round">info</span>
                  <p>No traits assigned yet. Edit traits to customize this minion's personality.</p>
                </div>
              </div>
              
              <div v-else class="no-traits">
                <span class="material-icons-round">info</span>
                <p>Traits system not initialized. This minion uses default personality settings.</p>
              </div>
            </div>
          </div>

          <!-- Configuration Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">settings</span>
              Configuration
              <button class="btn btn-sm btn-outline" @click="editConfiguration" v-if="canEdit && !editingConfiguration">
                <span class="material-icons-round">edit</span>
                Edit
              </button>
            </h2>
            <div class="section-content">
              <!-- Display Mode -->
              <div v-if="!editingConfiguration" class="config-grid">
                <div class="config-item">
                  <span class="config-label">Model ID</span>
                  <span class="config-value">{{ minionData?.model_id || 'N/A' }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">Parameters</span>
                  <span class="config-value">{{ formatParameters(minionData?.parameters) }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">Context Length</span>
                  <span class="config-value">{{ formatNumber(minionData?.context_length) }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">Quantization</span>
                  <span class="config-value">{{ formatQuantization(minionData?.quantization, minionData?.parameters) }}</span>
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
              
              <!-- Edit Mode -->
              <div v-else class="edit-form">
                <div class="form-group">
                  <label for="temperature">Temperature</label>
                  <input 
                    id="temperature"
                    v-model="editForm.temperature" 
                    type="number" 
                    step="0.1"
                    min="0"
                    max="2"
                    class="form-control"
                    :class="{ 'error': formErrors.temperature }"
                    placeholder="0.7"
                  />
                  <span v-if="formErrors.temperature" class="error-message">{{ formErrors.temperature }}</span>
                  <small class="form-help">Controls randomness (0 = deterministic, 2 = very random)</small>
                </div>
                
                <div class="form-group">
                  <label for="max_tokens">Max Tokens</label>
                  <input 
                    id="max_tokens"
                    v-model="editForm.max_tokens" 
                    type="number" 
                    min="1"
                    max="100000"
                    class="form-control"
                    :class="{ 'error': formErrors.max_tokens }"
                    placeholder="4096"
                  />
                  <span v-if="formErrors.max_tokens" class="error-message">{{ formErrors.max_tokens }}</span>
                  <small class="form-help">Maximum tokens to generate in response</small>
                </div>
                
                <div class="form-group">
                  <label for="top_p">Top P</label>
                  <input 
                    id="top_p"
                    v-model="editForm.top_p" 
                    type="number" 
                    step="0.1"
                    min="0"
                    max="1"
                    class="form-control"
                    :class="{ 'error': formErrors.top_p }"
                    placeholder="0.9"
                  />
                  <span v-if="formErrors.top_p" class="error-message">{{ formErrors.top_p }}</span>
                  <small class="form-help">Controls diversity (0 = focused, 1 = diverse)</small>
                </div>
                
                <div class="form-actions">
                  <button 
                    class="btn btn-primary" 
                    @click="saveConfiguration"
                    :disabled="saving"
                  >
                    <span v-if="saving" class="material-icons-round">hourglass_empty</span>
                    <span v-else class="material-icons-round">save</span>
                    {{ saving ? 'Saving...' : 'Save' }}
                  </button>
                  <button 
                    class="btn btn-outline" 
                    @click="cancelEdit('Configuration')"
                    :disabled="saving"
                  >
                    <span class="material-icons-round">cancel</span>
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- System Prompt Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">smart_toy</span>
              System Prompt
              <button class="btn btn-sm btn-outline" @click="editSystemPrompt" v-if="canEdit && !editingSystemPrompt">
                <span class="material-icons-round">edit</span>
                Edit
              </button>
            </h2>
            <div class="section-content">
              <!-- Display Mode -->
              <div v-if="!editingSystemPrompt" class="system-prompt-container">
                <pre class="system-prompt">{{ minionData?.system_prompt || 'No system prompt defined.' }}</pre>
              </div>
              
              <!-- Edit Mode -->
              <div v-else class="edit-form">
                <div class="form-group">
                  <label for="system_prompt">System Prompt</label>
                  <textarea 
                    id="system_prompt"
                    v-model="editForm.system_prompt" 
                    class="form-control system-prompt-textarea"
                    :class="{ 'error': formErrors.system_prompt }"
                    placeholder="Enter system prompt that defines the minion's behavior and personality..."
                    rows="8"
                  ></textarea>
                  <span v-if="formErrors.system_prompt" class="error-message">{{ formErrors.system_prompt }}</span>
                  <small class="form-help">This prompt defines how the minion behaves and responds. Be specific about its role and personality.</small>
                </div>
                
                <div class="form-actions">
                  <button 
                    class="btn btn-primary" 
                    @click="saveSystemPrompt"
                    :disabled="saving"
                  >
                    <span v-if="saving" class="material-icons-round">hourglass_empty</span>
                    <span v-else class="material-icons-round">save</span>
                    {{ saving ? 'Saving...' : 'Save' }}
                  </button>
                  <button 
                    class="btn btn-outline" 
                    @click="cancelEdit('SystemPrompt')"
                    :disabled="saving"
                  >
                    <span class="material-icons-round">cancel</span>
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="right-column">
          <!-- Token Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">key</span>
              Minion Token
              <span class="public-badge">PUBLIC</span>
            </h2>
            <div class="section-content">
              <div class="token-container">
                <div class="token-display">
                  <div class="token-label">Public Minion Token:</div>
                  <code class="token-value-large">{{ minionData?.minion_token || 'No token available' }}</code>
                  <button class="btn-icon" @click="copyToken" title="Copy token">
                    <span class="material-icons-round">content_copy</span>
                  </button>
                </div>
                <div class="token-info">
                  <div class="info-item">
                    <span class="material-icons-round">info</span>
                    <div class="info-text">
                      <strong>Public Token:</strong> This token is safe to share publicly and can be used to identify this minion.
                    </div>
                  </div>
                  <div class="info-item">
                    <span class="material-icons-round">security</span>
                    <div class="info-text">
                      <strong>Security:</strong> This token does not provide API access - it's only for identification.
                    </div>
                  </div>
                  <div class="info-item">
                    <span class="material-icons-round">link</span>
                    <div class="info-text">
                      <strong>Usage:</strong> Use this token to reference this minion in external integrations or APIs.
                    </div>
                  </div>
                </div>
                <div class="token-actions">
                  <button class="btn btn-sm btn-outline" @click="showTokenUsage">
                    <span class="material-icons-round">code</span>
                    API Usage
                  </button>
                  <button class="btn btn-sm btn-outline" @click="regenerateToken" v-if="canManageToken">
                    <span class="material-icons-round">refresh</span>
                    Regenerate
                  </button>
                  <button class="btn btn-sm btn-outline" @click="shareToken">
                    <span class="material-icons-round">share</span>
                    Share Token
                  </button>
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
                <!-- XP & Level Stats -->
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.level || 1 }}</div>
                  <div class="stat-label">Level</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.experience || 0 }}</div>
                  <div class="stat-label">Total XP</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.xp_to_next_level || 0 }}</div>
                  <div class="stat-label">XP to Next Level</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.xp_progress_percentage || 0 }}%</div>
                  <div class="stat-label">Level Progress</div>
                </div>
                
                <!-- Rank Stats -->
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.rank_display_name || 'Novice' }}</div>
                  <div class="stat-label">Rank</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.rank_level || 1 }}</div>
                  <div class="stat-label">Rank Level</div>
                </div>
                
                <!-- Score Stats -->
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.score || 0 }}</div>
                  <div class="stat-label">Total Score</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.traits_compatibility_score || 0 }}%</div>
                  <div class="stat-label">Trait Compatibility</div>
                </div>
                
                <!-- Training Stats -->
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.total_training_xp || 0 }}</div>
                  <div class="stat-label">Training XP</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.total_usage_xp || 0 }}</div>
                  <div class="stat-label">Usage XP</div>
                </div>
                
                <!-- Model Stats -->
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.context_length || 0 }}</div>
                  <div class="stat-label">Context Length</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.max_tokens || 0 }}</div>
                  <div class="stat-label">Max Tokens</div>
                </div>
                
                <!-- Traits Stats -->
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.traits_slots || 0 }}</div>
                  <div class="stat-label">Trait Slots</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ minionData?.traits_points_spent || 0 }}</div>
                  <div class="stat-label">Trait Points Spent</div>
                </div>
                
                <!-- Usage Stats -->
                <div class="stat-item">
                  <div class="stat-value">{{ formatDate(minionData?.created_at) || 'Unknown' }}</div>
                  <div class="stat-label">Created</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ formatDate(minionData?.updated_at) || 'Unknown' }}</div>
                  <div class="stat-label">Last Updated</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Rank & Score Section -->
          <div class="profile-section">
            <h2 class="section-title">
              <span class="material-icons-round">emoji_events</span>
              Rank & Score
            </h2>
            <div class="section-content">
              <div class="rank-score-container">
                <!-- Current Rank Display -->
                <div class="current-rank">
                  <div class="rank-badge-large" :class="`rank-${minionData?.rank || 'novice'}`">
                    <span class="rank-icon">🏆</span>
                    <div class="rank-info">
                      <div class="rank-name">{{ minionData?.rank_display_name || 'Novice' }}</div>
                      <div class="rank-level">Level {{ minionData?.rank_level || 1 }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- Score Breakdown -->
                <div class="score-breakdown" v-if="minionData?.score_breakdown">
                  <h3 class="subsection-title">Score Breakdown</h3>
                  <div class="score-grid">
                    <div class="score-item">
                      <span class="score-label">XP Score</span>
                      <span class="score-value">{{ minionData.score_breakdown.xp_score || 0 }}</span>
                    </div>
                    <div class="score-item">
                      <span class="score-label">Rank Score</span>
                      <span class="score-value">{{ minionData.score_breakdown.rank_score || 0 }}</span>
                    </div>
                    <div class="score-item">
                      <span class="score-label">Parameters</span>
                      <span class="score-value">{{ minionData.score_breakdown.param_score || 0 }}</span>
                    </div>
                    <div class="score-item">
                      <span class="score-label">Context</span>
                      <span class="score-value">{{ minionData.score_breakdown.context_score || 0 }}</span>
                    </div>
                    <div class="score-item">
                      <span class="score-label">Capabilities</span>
                      <span class="score-value">{{ minionData.score_breakdown.cap_score || 0 }}</span>
                    </div>
                    <div class="score-item">
                      <span class="score-label">Architecture</span>
                      <span class="score-value">{{ minionData.score_breakdown.arch_score || 0 }}</span>
                    </div>
                  </div>
                  <div class="total-score">
                    <span class="total-label">Total Score</span>
                    <span class="total-value">{{ minionData?.score || 0 }}</span>
                  </div>
                </div>
                
                <!-- XP Progress Bar -->
                <div class="xp-progress-section">
                  <h3 class="subsection-title">Level Progress</h3>
                  <div class="xp-progress-bar">
                    <div class="xp-progress-fill" :style="{ width: `${minionData?.xp_progress_percentage || 0}%` }"></div>
                  </div>
                  <div class="xp-progress-text">
                    <span>{{ minionData?.experience || 0 }} XP</span>
                    <span>{{ minionData?.xp_to_next_level || 0 }} XP to next level</span>
                  </div>
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

    <!-- Error/Empty State -->
    <div v-else-if="!minionData" class="error-state">
      <div class="error-content">
        <span class="material-icons-round error-icon">error_outline</span>
        <h2>Minion Not Found</h2>
        <p>The requested minion could not be loaded. Please check the URL or try again.</p>
        <button class="btn btn-primary" @click="loadMinionProfile">
          <span class="material-icons-round">refresh</span>
          Retry
        </button>
        <button class="btn btn-outline" @click="handleback">
          <span class="material-icons-round">arrow_back</span>
          Go Back
        </button>
      </div>
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
import { getUserApiUrl, getApiUrl, getAvatarUrl } from '@/config/api'

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
      // Edit states
      editingBasicInfo: false,
      editingConfiguration: false,
      editingSystemPrompt: false,
      editingTraits: false,
      // Edit form data
      editForm: {
        display_name: '',
        title: '',
        description: '',
        temperature: 0.7,
        max_tokens: 4096,
        top_p: 0.9,
        system_prompt: '',
        traits_intensities: {}
      },
      // Form validation
      formErrors: {},
      saving: false,
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
    
    // Traits system computed properties
    traitsData() {
      if (!this.minionData) return null
      return {
        slots: this.minionData.traits_slots || 0,
        points_available: this.minionData.traits_points_available || 0,
        points_spent: this.minionData.traits_points_spent || 0,
        traits_intensities: this.minionData.traits_intensities || {},
        compatibility_score: this.minionData.traits_compatibility_score || 0,
        effectiveness_bonus: this.minionData.traits_effectiveness_bonus || 0
      }
    },
    
    activeTraits() {
      if (!this.traitsData?.traits_intensities) return []
      return Object.keys(this.traitsData.traits_intensities)
    },
    
    canEdit() {
      // Add logic to determine if user can edit this minion
      return true // For now, allow editing
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

        console.log('Making API request to:', getUserApiUrl(this.authStore.user.id, 'minions', this.minionId))
        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'minions', this.minionId), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        const data = await response.json()
        console.log('MinionProfile API response:', data)
        
        if (data.success && data.minion) {
          this.minionData = data.minion
          this.isFavorite = data.minion.is_favorite || false
          console.log('Minion data loaded successfully:', this.minionData)
          await this.loadMinionStats()
        } else {
          console.error('Failed to load minion profile:', data)
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
        const response = await fetch(getApiUrl(`external-models/${this.minionId}/toggle-favorite`), {
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
        const response = await fetch(getUserApiUrl(this.authStore.user.id, `minions/${this.minionId}/regenerate-token`), {
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
      if (!num) return 'Not Specified'
      return new Intl.NumberFormat().format(num)
    },

    formatParameters(parameters) {
      if (!parameters) return 'N/A'

      // If parameters is JSON string, try to parse
      if (typeof parameters === 'string') {
        try {
          const parsed = JSON.parse(parameters)
          return this.formatParameters(parsed)
        } catch {
          // If it's a plain string like "7B", return as-is
          return parameters
        }
      }

      // If it's an object, try common keys
      if (typeof parameters === 'object') {
        const count = parameters.size || parameters.parameters || parameters.param_count || parameters.num_params
        if (count) {
          // Handle values like 7000000000 -> 7,000,000,000
          if (typeof count === 'number') return this.formatNumber(count)
          return String(count) // This will show "49B" directly
        }
        return 'API Model'
      }

      return 'N/A'
    },

    formatQuantization(quantization, parameters) {
      // Prefer explicit quantization field, then infer from parameters
      let value = quantization

      if (!value && parameters) {
        let paramsObj = parameters
        if (typeof parameters === 'string') {
          try {
            paramsObj = JSON.parse(parameters)
          } catch {
            paramsObj = null
          }
        }
        if (paramsObj && typeof paramsObj === 'object') {
          value = paramsObj.quantization || paramsObj.dtype || paramsObj.precision || null
        }
      }

      return value || 'N/A'
    },
    handleback() {
      this.$router.go(-1)
    },
    
    editTraits() {
      // Navigate to traits editor or open modal
      this.$router.push(`/minions/${this.minionId}/traits`)
    },
    
    editConfiguration() {
      // Navigate to configuration editor or open modal
      this.$router.push(`/minions/${this.minionId}/config`)
    },
    
    editSystemPrompt() {
      // Navigate to system prompt editor or open modal
      this.$router.push(`/minions/${this.minionId}/system-prompt`)
    },
    
    async updateMinion(updateData) {
      try {
        const token = this.authStore.token
        if (!token) {
          this.showToast('Please log in to update minion', 'error')
          return
        }

        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'minions', this.minionId), {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updateData)
        })

        const data = await response.json()
        
        if (data.success) {
          this.showToast('Minion updated successfully', 'success')
          await this.loadMinionProfile() // Reload data
        } else {
          this.showToast(data.error || 'Failed to update minion', 'error')
        }
      } catch (error) {
        console.error('Error updating minion:', error)
        this.showToast('Failed to update minion', 'error')
      }
    },
    
    copyToken() {
      if (this.minionData?.minion_token) {
        navigator.clipboard.writeText(this.minionData.minion_token)
        this.showToast('Token copied to clipboard', 'success')
      }
    },
    
    shareToken() {
      if (this.minionData?.minion_token) {
        const shareData = {
          title: `${this.minionData.display_name} - Minion Token`,
          text: `Minion Token: ${this.minionData.minion_token}`,
          url: window.location.href
        }
        
        if (navigator.share) {
          navigator.share(shareData)
        } else {
          // Fallback: copy to clipboard
          navigator.clipboard.writeText(`Minion Token: ${this.minionData.minion_token}`)
          this.showToast('Token copied to clipboard for sharing', 'success')
        }
      }
    },
    
    showTokenUsage() {
      const usageExample = `
// Example API usage with minion token
curl -X POST "https://your-api.com/v1/minions/chat" \\
  -H "Authorization: Bearer ${this.minionData?.minion_token}" \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hello minion!"}'
      `.trim()
      
      navigator.clipboard.writeText(usageExample)
      this.showToast('API usage example copied to clipboard', 'success')
    },
    
    async regenerateToken() {
      try {
        const token = this.authStore.token
        if (!token) {
          this.showToast('Please log in to regenerate token', 'error')
          return
        }

        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'minions', this.minionId, 'regenerate-token'), {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        const data = await response.json()
        
        if (data.success) {
          this.showToast('Token regenerated successfully', 'success')
          await this.loadMinionProfile() // Reload data
        } else {
          this.showToast(data.error || 'Failed to regenerate token', 'error')
        }
      } catch (error) {
        console.error('Error regenerating token:', error)
        this.showToast('Failed to regenerate token', 'error')
      }
    },

    // Edit functionality methods
    editBasicInfo() {
      this.editingBasicInfo = true
      this.editForm.display_name = this.minionData?.display_name || ''
      this.editForm.title = this.minionData?.title || ''
      this.editForm.description = this.minionData?.description || ''
    },

    editConfiguration() {
      this.editingConfiguration = true
      this.editForm.temperature = this.minionData?.temperature || 0.7
      this.editForm.max_tokens = this.minionData?.max_tokens || 4096
      this.editForm.top_p = this.minionData?.top_p || 0.9
    },

    editSystemPrompt() {
      this.editingSystemPrompt = true
      this.editForm.system_prompt = this.minionData?.system_prompt || ''
    },

    editTraits() {
      this.editingTraits = true
      this.editForm.traits_intensities = { ...this.minionData?.traits_intensities || {} }
    },

    cancelEdit(section) {
      this[`editing${section}`] = false
      this.formErrors = {}
    },

    async saveBasicInfo() {
      this.saving = true
      this.formErrors = {}

      try {
        const token = this.authStore.token
        if (!token) {
          this.showToast('Please log in to save changes', 'error')
          return
        }

        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'minions', this.minionId), {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            display_name: this.editForm.display_name,
            title: this.editForm.title,
            description: this.editForm.description
          })
        })

        const data = await response.json()
        
        if (data.success) {
          this.showToast('Basic information updated successfully', 'success')
          this.editingBasicInfo = false
          await this.loadMinionProfile()
        } else {
          this.showToast(data.error || 'Failed to update basic information', 'error')
          if (data.errors) {
            this.formErrors = data.errors
          }
        }
      } catch (error) {
        console.error('Error saving basic info:', error)
        this.showToast('Failed to save basic information', 'error')
      } finally {
        this.saving = false
      }
    },

    async saveConfiguration() {
      this.saving = true
      this.formErrors = {}

      try {
        const token = this.authStore.token
        if (!token) {
          this.showToast('Please log in to save changes', 'error')
          return
        }

        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'minions', this.minionId), {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            temperature: parseFloat(this.editForm.temperature),
            max_tokens: parseInt(this.editForm.max_tokens),
            top_p: parseFloat(this.editForm.top_p)
          })
        })

        const data = await response.json()
        
        if (data.success) {
          this.showToast('Configuration updated successfully', 'success')
          this.editingConfiguration = false
          await this.loadMinionProfile()
        } else {
          this.showToast(data.error || 'Failed to update configuration', 'error')
          if (data.errors) {
            this.formErrors = data.errors
          }
        }
      } catch (error) {
        console.error('Error saving configuration:', error)
        this.showToast('Failed to save configuration', 'error')
      } finally {
        this.saving = false
      }
    },

    async saveSystemPrompt() {
      this.saving = true
      this.formErrors = {}

      try {
        const token = this.authStore.token
        if (!token) {
          this.showToast('Please log in to save changes', 'error')
          return
        }

        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'minions', this.minionId), {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            system_prompt: this.editForm.system_prompt
          })
        })

        const data = await response.json()
        
        if (data.success) {
          this.showToast('System prompt updated successfully', 'success')
          this.editingSystemPrompt = false
          await this.loadMinionProfile()
        } else {
          this.showToast(data.error || 'Failed to update system prompt', 'error')
          if (data.errors) {
            this.formErrors = data.errors
          }
        }
      } catch (error) {
        console.error('Error saving system prompt:', error)
        this.showToast('Failed to save system prompt', 'error')
      } finally {
        this.saving = false
      }
    },

    async saveTraits() {
      this.saving = true
      this.formErrors = {}

      try {
        const token = this.authStore.token
        if (!token) {
          this.showToast('Please log in to save changes', 'error')
          return
        }

        const response = await fetch(getUserApiUrl(this.authStore.user.id, 'minions', this.minionId, 'traits'), {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            traits_intensities: this.editForm.traits_intensities
          })
        })

        const data = await response.json()
        
        if (data.success) {
          this.showToast('Traits updated successfully', 'success')
          this.editingTraits = false
          await this.loadMinionProfile()
        } else {
          this.showToast(data.error || 'Failed to update traits', 'error')
          if (data.errors) {
            this.formErrors = data.errors
          }
        }
      } catch (error) {
        console.error('Error saving traits:', error)
        this.showToast('Failed to save traits', 'error')
      } finally {
        this.saving = false
      }
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
      return getAvatarUrl(filename)
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
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
}

/* Header Section */
.profile-header {
  position: relative;
  background: var(--card-bg);
  box-shadow: var(--shadow);
  padding: 2rem 1.5rem;
  color: var(--text-color);
  border-radius: var(--radius-lg);
  margin: 1.5rem;
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
  color: var(--text-color);
}
.profile-title{
  color: var(--text-muted);
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.profile-description {
  font-size: 1rem;
  color: var(--text-color);
  margin-bottom: 1rem;
  line-height: 1.5;
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
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.section-content {
  color: var(--text-color);
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

.no-capabilities {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #e0f2fe;
  color: #0369a1;
}

.no-capabilities .material-icons-round {
  color: #0369a1;
  font-size: 1.5rem;
}

.no-capabilities p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
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

/* Error State Styles */
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 2rem;
}

.error-content {
  text-align: center;
  max-width: 500px;
}

.error-icon {
  font-size: 4rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-content h2 {
  color: #1f2937;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
}

.error-content p {
  color: #6b7280;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.error-content .btn {
  margin: 0 0.5rem;
}

/* Traits System Styles */
.traits-container {
  margin-top: 1rem;
}

.traits-overview {
  margin-bottom: 1.5rem;
}

.traits-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.traits-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: var(--shadow-sm);
}

.traits-stats .stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.traits-stats .stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

.subsection-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.traits-grid {
  display: grid;
  gap: 1rem;
}

.trait-card {
  background: var(--card-bg);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.trait-card:hover {
  background: var(--card-bg);
  border-color: var(--primary);
  box-shadow: var(--shadow);
}

.trait-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.trait-name {
  font-weight: 600;
  color: var(--text-color);
  text-transform: capitalize;
}

.trait-intensity {
  font-weight: 700;
  color: #4f46e5;
  background: rgba(79, 70, 229, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.trait-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.trait-progress {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.no-traits {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.no-traits .material-icons-round {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-traits p {
  margin: 0;
  font-size: 0.95rem;
}

/* Section title with edit button */
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title .btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

/* Rank & Score Section Styles */
.rank-score-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.current-rank {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.rank-badge-large {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.rank-badge-large.rank-novice {
  border-color: #6b7280;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
}

.rank-badge-large.rank-apprentice {
  border-color: #10b981;
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
}

.rank-badge-large.rank-skilled {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
}

.rank-badge-large.rank-expert {
  border-color: #8b5cf6;
  background: linear-gradient(135deg, #ede9fe, #ddd6fe);
}

.rank-badge-large.rank-master {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
}

.rank-badge-large.rank-grandmaster {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fee2e2, #fecaca);
}

.rank-badge-large.rank-legendary {
  border-color: #f97316;
  background: linear-gradient(135deg, #fed7aa, #fdba74);
}

.rank-icon {
  font-size: 3rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.rank-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.rank-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  text-transform: capitalize;
}

.rank-level {
  font-size: 1rem;
  color: var(--text-muted);
  font-weight: 500;
}

.score-breakdown {
  margin-bottom: 1.5rem;
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.score-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  text-align: center;
}

.score-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary);
}

.total-score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--primary);
  color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.total-label {
  font-size: 1.1rem;
  font-weight: 600;
}

.total-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.xp-progress-section {
  margin-top: 1rem;
}

.xp-progress-bar {
  width: 100%;
  height: 12px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.xp-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--success));
  border-radius: 6px;
  transition: width 0.3s ease;
}

.xp-progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* Public Badge */
.public-badge {
  background: var(--success);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Enhanced Token Display */
.token-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.token-value-large {
  font-family: 'Courier New', monospace;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary);
  background: rgba(79, 70, 229, 0.1);
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  border: 1px solid rgba(79, 70, 229, 0.2);
  word-break: break-all;
  display: block;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(79, 70, 229, 0.05);
  border-radius: var(--radius);
  border-left: 3px solid var(--primary);
}

.info-item .material-icons-round {
  color: var(--primary);
  font-size: 1.25rem;
  margin-top: 0.125rem;
}

.info-text {
  flex: 1;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--text-color);
}

.info-text strong {
  color: var(--text-color);
  font-weight: 600;
}

.token-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.company-badge {
  background: var(--primary);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Edit Form Styles */
.edit-form {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--shadow);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-color);
  color: var(--text-color);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-control.error {
  border-color: #ef4444;
}

.form-control.system-prompt-textarea {
  font-family: 'Courier New', monospace;
  line-height: 1.5;
  resize: vertical;
  min-height: 200px;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.form-help {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.form-actions .btn {
  flex: 1;
  min-width: 120px;
}
</style>

