<template>
  <div class="settings-container">
    <div class="page-header">
      <h1>Settings</h1>
      <p>Manage your account settings and preferences</p>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message', message.type]">
      <span class="material-icons-round">{{ message.icon }}</span>
      {{ message.text }}
    </div>

    <!-- Settings Tabs -->
    <div class="settings-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <span class="material-icons-round">{{ tab.icon }}</span>
        {{ tab.name }}
      </button>
    </div>

    <!-- General Settings -->
    <div v-if="activeTab === 'general'" class="settings-section">
      <div class="auth-card">
        <div class="auth-header">
          <h2>General Settings</h2>
          <p>Manage your general account preferences</p>
        </div>

        <form @submit.prevent="handleGeneralSettings" class="auth-form">
          <div class="form-group">
            <label for="firstName" class="form-label">First Name</label>
            <input
              id="firstName"
              v-model="generalForm.firstName"
              type="text"
              class="form-input"
              placeholder="Enter your first name"
              :disabled="loading"
            />
            <div v-if="errors.firstName" class="form-error">{{ errors.firstName }}</div>
          </div>

          <div class="form-group">
            <label for="lastName" class="form-label">Last Name</label>
            <input
              id="lastName"
              v-model="generalForm.lastName"
              type="text"
              class="form-input"
              placeholder="Enter your last name"
              :disabled="loading"
            />
            <div v-if="errors.lastName" class="form-error">{{ errors.lastName }}</div>
          </div>

          <div class="form-group">
            <label for="email" class="form-label">Email Address</label>
            <input
              id="email"
              v-model="generalForm.email"
              type="email"
              class="form-input"
              placeholder="Enter your email"
              :disabled="loading"
            />
            <div v-if="errors.email" class="form-error">{{ errors.email }}</div>
          </div>

          <div class="form-group">
            <label for="username" class="form-label">Username</label>
            <input
              id="username"
              v-model="generalForm.username"
              type="text"
              class="form-input"
              placeholder="Enter your username"
              :disabled="loading"
            />
            <div v-if="errors.username" class="form-error">{{ errors.username }}</div>
          </div>

          <div class="form-group">
            <label for="timezone" class="form-label">Timezone</label>
            <select
              id="timezone"
              v-model="generalForm.timezone"
              class="form-input"
              :disabled="loading"
            >
              <option value="UTC">UTC</option>
              <option value="America/New_York">Eastern Time</option>
              <option value="America/Chicago">Central Time</option>
              <option value="America/Denver">Mountain Time</option>
              <option value="America/Los_Angeles">Pacific Time</option>
              <option value="Europe/London">London</option>
              <option value="Europe/Paris">Paris</option>
              <option value="Asia/Tokyo">Tokyo</option>
              <option value="Asia/Shanghai">Shanghai</option>
            </select>
            <div v-if="errors.timezone" class="form-error">{{ errors.timezone }}</div>
          </div>

          <div class="form-group">
            <label for="language" class="form-label">Language</label>
            <select
              id="language"
              v-model="generalForm.language"
              class="form-input"
              :disabled="loading"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
              <option value="pt">Portuguese</option>
              <option value="ru">Russian</option>
              <option value="ja">Japanese</option>
              <option value="ko">Korean</option>
              <option value="zh">Chinese</option>
            </select>
            <div v-if="errors.language" class="form-error">{{ errors.language }}</div>
          </div>

          <button
            type="submit"
            class="auth-button"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else class="material-icons-round">save</span>
            {{ loading ? 'Saving...' : 'Save Settings' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Security Settings -->
    <div v-if="activeTab === 'security'" class="settings-section">
      <div class="auth-card">
        <div class="auth-header">
          <h2>Security Settings</h2>
          <p>Manage your account security and privacy</p>
        </div>

        <div class="security-options">
          <div class="security-option">
            <div class="option-info">
              <h3>Two-Factor Authentication</h3>
              <p>Add an extra layer of security to your account</p>
            </div>
            <button class="auth-button secondary" @click="toggle2FA">
              <span class="material-icons-round">security</span>
              {{ twoFAEnabled ? 'Disable 2FA' : 'Enable 2FA' }}
            </button>
          </div>

          <div class="security-option">
            <div class="option-info">
              <h3>Session Management</h3>
              <p>Manage your active sessions and devices</p>
            </div>
            <button class="auth-button secondary" @click="showSessions = !showSessions">
              <span class="material-icons-round">devices</span>
              View Sessions
            </button>
          </div>

          <div class="security-option">
            <div class="option-info">
              <h3>API Keys</h3>
              <p>Manage your API keys for external integrations</p>
            </div>
            <button class="auth-button secondary" @click="showAPIKeys = !showAPIKeys">
              <span class="material-icons-round">key</span>
              Manage API Keys
            </button>
          </div>
        </div>

        <!-- Change Password Form -->
        <div class="password-section">
          <h3>Change Password</h3>
          <form @submit.prevent="handleChangePassword" class="auth-form">
            <div class="form-group">
              <label for="currentPassword" class="form-label">Current Password</label>
              <input
                id="currentPassword"
                v-model="passwordForm.currentPassword"
                type="password"
                class="form-input"
                placeholder="Enter current password"
                :disabled="loading"
              />
              <div v-if="errors.currentPassword" class="form-error">{{ errors.currentPassword }}</div>
            </div>

            <div class="form-group">
              <label for="newPassword" class="form-label">New Password</label>
              <input
                id="newPassword"
                v-model="passwordForm.newPassword"
                type="password"
                class="form-input"
                placeholder="Enter new password"
                :disabled="loading"
              />
              <div v-if="errors.newPassword" class="form-error">{{ errors.newPassword }}</div>
            </div>

            <div class="form-group">
              <label for="confirmNewPassword" class="form-label">Confirm New Password</label>
              <input
                id="confirmNewPassword"
                v-model="passwordForm.confirmNewPassword"
                type="password"
                class="form-input"
                placeholder="Confirm new password"
                :disabled="loading"
              />
              <div v-if="errors.confirmNewPassword" class="form-error">{{ errors.confirmNewPassword }}</div>
            </div>

            <button
              type="submit"
              class="auth-button"
              :disabled="loading"
            >
              <span v-if="loading" class="loading-spinner"></span>
              <span v-else class="material-icons-round">lock</span>
              {{ loading ? 'Updating...' : 'Update Password' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Notifications Settings -->
    <div v-if="activeTab === 'notifications'" class="settings-section">
      <div class="auth-card">
        <div class="auth-header">
          <h2>Notification Settings</h2>
          <p>Manage how you receive notifications</p>
        </div>

        <form @submit.prevent="handleNotificationSettings" class="auth-form">
          <div class="notification-group">
            <h3>Email Notifications</h3>
            <div class="notification-options">
              <div class="notification-option">
                <label class="checkbox-label">
                  <input
                    v-model="notificationForm.email.trainingComplete"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Training job completed
                </label>
              </div>
              <div class="notification-option">
                <label class="checkbox-label">
                  <input
                    v-model="notificationForm.email.trainingFailed"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Training job failed
                </label>
              </div>
              <div class="notification-option">
                <label class="checkbox-label">
                  <input
                    v-model="notificationForm.email.evaluationComplete"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Model evaluation completed
                </label>
              </div>
              <div class="notification-option">
                <label class="checkbox-label">
                  <input
                    v-model="notificationForm.email.usageLimit"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Usage limit reached
                </label>
              </div>
              <div class="notification-option">
                <label class="checkbox-label">
                  <input
                    v-model="notificationForm.email.billing"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Billing and subscription updates
                </label>
              </div>
            </div>
          </div>

          <div class="notification-group">
            <h3>Push Notifications</h3>
            <div class="notification-options">
              <div class="notification-option">
                <label class="checkbox-label">
                  <input
                    v-model="notificationForm.push.trainingComplete"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Training job completed
                </label>
              </div>
              <div class="notification-option">
                <label class="checkbox-label">
                    <input
                      v-model="notificationForm.push.trainingFailed"
                      type="checkbox"
                      :disabled="loading"
                    />
                    <span class="checkmark"></span>
                    Training job failed
                  </label>
              </div>
              <div class="notification-option">
                <label class="checkbox-label">
                  <input
                    v-model="notificationForm.push.evaluationComplete"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Model evaluation completed
                </label>
              </div>
            </div>
          </div>

          <button
            type="submit"
            class="auth-button"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else class="material-icons-round">notifications</span>
            {{ loading ? 'Saving...' : 'Save Notifications' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Privacy Settings -->
    <div v-if="activeTab === 'privacy'" class="settings-section">
      <div class="auth-card">
        <div class="auth-header">
          <h2>Privacy Settings</h2>
          <p>Manage your privacy and data preferences</p>
        </div>

        <form @submit.prevent="handlePrivacySettings" class="auth-form">
          <div class="privacy-group">
            <h3>Data Sharing</h3>
            <div class="privacy-options">
              <div class="privacy-option">
                <label class="checkbox-label">
                  <input
                    v-model="privacyForm.analytics"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Allow usage analytics
                </label>
                <p class="option-description">Help us improve the service by sharing anonymous usage data</p>
              </div>
              <div class="privacy-option">
                <label class="checkbox-label">
                  <input
                    v-model="privacyForm.marketing"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Receive marketing emails
                </label>
                <p class="option-description">Get updates about new features and promotions</p>
              </div>
              <div class="privacy-option">
                <label class="checkbox-label">
                  <input
                    v-model="privacyForm.publicProfile"
                    type="checkbox"
                    :disabled="loading"
                  />
                  <span class="checkmark"></span>
                  Public profile
                </label>
                <p class="option-description">Allow others to see your public profile and models</p>
              </div>
            </div>
          </div>

          <div class="privacy-group">
            <h3>Data Management</h3>
            <div class="privacy-actions">
              <button type="button" class="auth-button secondary" @click="exportData">
                <span class="material-icons-round">download</span>
                Export My Data
              </button>
              <button type="button" class="auth-button danger" @click="deleteAccount">
                <span class="material-icons-round">delete</span>
                Delete Account
              </button>
            </div>
          </div>

          <button
            type="submit"
            class="auth-button"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else class="material-icons-round">privacy_tip</span>
            {{ loading ? 'Saving...' : 'Save Privacy Settings' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Settings',
  setup() {
    const authStore = useAuthStore()
    
    // Reactive state
    const loading = ref(false)
    const message = ref(null)
    const activeTab = ref('general')
    const twoFAEnabled = ref(false)
    const showSessions = ref(false)
    const showAPIKeys = ref(false)
    
    // Tabs configuration
    const tabs = ref([
      { id: 'general', name: 'General', icon: 'settings' },
      { id: 'security', name: 'Security', icon: 'security' },
      { id: 'notifications', name: 'Notifications', icon: 'notifications' },
      { id: 'privacy', name: 'Privacy', icon: 'privacy_tip' }
    ])
    
    // Form data
    const generalForm = reactive({
      firstName: '',
      lastName: '',
      email: '',
      username: '',
      timezone: 'UTC',
      language: 'en'
    })
    
    const passwordForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: ''
    })
    
    const notificationForm = reactive({
      email: {
        trainingComplete: true,
        trainingFailed: true,
        evaluationComplete: true,
        usageLimit: true,
        billing: true
      },
      push: {
        trainingComplete: true,
        trainingFailed: true,
        evaluationComplete: false
      }
    })
    
    const privacyForm = reactive({
      analytics: true,
      marketing: false,
      publicProfile: false
    })
    
    const errors = ref({})
    
    // Methods
    const showMessage = (type, text, icon = 'info') => {
      message.value = { type, text, icon }
      setTimeout(() => {
        message.value = null
      }, 5000)
    }
    
    const loadUserData = () => {
      const user = authStore.user
      if (user) {
        generalForm.firstName = user.firstName || ''
        generalForm.lastName = user.lastName || ''
        generalForm.email = user.email || ''
        generalForm.username = user.username || ''
        generalForm.timezone = user.timezone || 'UTC'
        generalForm.language = user.language || 'en'
      }
    }
    
    const handleGeneralSettings = async () => {
      loading.value = true
      errors.value = {}
      message.value = null
      
      try {
        const response = await authStore.updateProfile({
          firstName: generalForm.firstName,
          lastName: generalForm.lastName,
          email: generalForm.email,
          username: generalForm.username,
          timezone: generalForm.timezone,
          language: generalForm.language
        })
        
        if (response.success) {
          showMessage('success', 'General settings updated successfully!', 'check_circle')
        } else {
          showMessage('error', response.error || 'Failed to update settings', 'error')
        }
      } catch (error) {
        console.error('General settings error:', error)
        showMessage('error', 'An unexpected error occurred', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const handleChangePassword = async () => {
      loading.value = true
      errors.value = {}
      message.value = null
      
      try {
        const response = await authStore.changePassword(
          passwordForm.currentPassword,
          passwordForm.newPassword
        )
        
        if (response.success) {
          showMessage('success', 'Password changed successfully!', 'check_circle')
          passwordForm.currentPassword = ''
          passwordForm.newPassword = ''
          passwordForm.confirmNewPassword = ''
        } else {
          showMessage('error', response.error || 'Password change failed', 'error')
        }
      } catch (error) {
        console.error('Password change error:', error)
        showMessage('error', 'An unexpected error occurred', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const handleNotificationSettings = async () => {
      loading.value = true
      message.value = null
      
      try {
        // Mock API call (replace with real implementation)
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        showMessage('success', 'Notification settings updated successfully!', 'check_circle')
      } catch (error) {
        console.error('Notification settings error:', error)
        showMessage('error', 'An unexpected error occurred', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const handlePrivacySettings = async () => {
      loading.value = true
      message.value = null
      
      try {
        // Mock API call (replace with real implementation)
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        showMessage('success', 'Privacy settings updated successfully!', 'check_circle')
      } catch (error) {
        console.error('Privacy settings error:', error)
        showMessage('error', 'An unexpected error occurred', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const toggle2FA = () => {
      twoFAEnabled.value = !twoFAEnabled.value
      showMessage('info', `Two-factor authentication ${twoFAEnabled.value ? 'enabled' : 'disabled'}`, 'security')
    }
    
    const exportData = () => {
      showMessage('info', 'Data export started. You will receive an email when ready.', 'download')
    }
    
    const deleteAccount = () => {
      if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        showMessage('warning', 'Account deletion requested. Please contact support.', 'delete')
      }
    }
    
    onMounted(() => {
      loadUserData()
    })
    
    return {
      // State
      loading,
      message,
      activeTab,
      twoFAEnabled,
      showSessions,
      showAPIKeys,
      tabs,
      
      // Forms
      generalForm,
      passwordForm,
      notificationForm,
      privacyForm,
      errors,
      
      // Methods
      handleGeneralSettings,
      handleChangePassword,
      handleNotificationSettings,
      handlePrivacySettings,
      toggle2FA,
      exportData,
      deleteAccount
    }
  }
}
</script>

<style scoped>
@import '@/assets/rbac.css';

/* Additional component-specific styles */
.settings-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--spacer-lg);
}

.page-header {
  margin-bottom: var(--spacer-xl);
  text-align: center;
}

.page-header h1 {
  color: var(--text-color);
  margin-bottom: var(--spacer-sm);
  font-size: 2rem;
  font-weight: 700;
}

.page-header p {
  color: var(--text-muted);
  font-size: 1.1rem;
}

.settings-tabs {
  display: flex;
  gap: var(--spacer-sm);
  margin-bottom: var(--spacer-xl);
  border-bottom: 1px solid var(--shadow-dark);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: var(--spacer-sm);
  padding: var(--spacer-md) var(--spacer-lg);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition);
  border-bottom: 2px solid transparent;
  font-weight: 500;
}

.tab-button:hover {
  color: var(--text-color);
  background-color: var(--bg-color);
}

.tab-button.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.tab-button .material-icons-round {
  font-size: 1.2rem;
}

.settings-section {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.security-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-lg);
  margin-bottom: var(--spacer-xl);
}

.security-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacer-lg);
  background-color: var(--bg-color);
  border-radius: var(--radius);
  border: 1px solid var(--shadow-dark);
}

.option-info h3 {
  color: var(--text-color);
  margin: 0 0 var(--spacer-sm);
  font-size: 1.1rem;
  font-weight: 600;
}

.option-info p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.9rem;
}

.password-section {
  margin-top: var(--spacer-xl);
  padding-top: var(--spacer-xl);
  border-top: 1px solid var(--shadow-dark);
}

.password-section h3 {
  color: var(--text-color);
  margin-bottom: var(--spacer-lg);
  font-size: 1.2rem;
  font-weight: 600;
}

.notification-group {
  margin-bottom: var(--spacer-xl);
}

.notification-group h3 {
  color: var(--text-color);
  margin-bottom: var(--spacer-lg);
  font-size: 1.2rem;
  font-weight: 600;
}

.notification-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.notification-option {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacer-sm);
  cursor: pointer;
  color: var(--text-color);
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid var(--shadow-dark);
  border-radius: var(--radius-sm);
  position: relative;
  transition: var(--transition);
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
  background-color: var(--primary);
  border-color: var(--primary);
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '';
  position: absolute;
  left: 6px;
  top: 2px;
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.privacy-group {
  margin-bottom: var(--spacer-xl);
}

.privacy-group h3 {
  color: var(--text-color);
  margin-bottom: var(--spacer-lg);
  font-size: 1.2rem;
  font-weight: 600;
}

.privacy-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-lg);
}

.privacy-option {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-sm);
}

.option-description {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin: 0;
  margin-left: 28px;
}

.privacy-actions {
  display: flex;
  gap: var(--spacer-md);
  margin-top: var(--spacer-lg);
}

.auth-button.danger {
  background-color: var(--danger);
  color: white;
}

.auth-button.danger:hover {
  background-color: #c0392b;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .settings-tabs {
    flex-wrap: wrap;
  }
  
  .security-option {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacer-md);
  }
  
  .privacy-actions {
    flex-direction: column;
  }
}
</style>
