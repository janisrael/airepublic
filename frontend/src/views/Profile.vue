<template>
  <div class="profile-container">
    <div class="page-header">
      <h1>User Profile</h1>
      <p>Manage your account settings and preferences</p>
    </div>

    <!-- Profile Header -->
    <div class="profile-header">
      <div class="profile-avatar">
        <span class="material-icons-round">account_circle</span>
      </div>
      <div class="profile-info">
        <h1>{{ user?.firstName }} {{ user?.lastName }}</h1>
        <p>{{ user?.email }}</p>
        <div class="profile-badge" :class="userRole">{{ userRole }}</div>
      </div>
      <button class="auth-button secondary" @click="editProfile = !editProfile">
        <span class="material-icons-round">edit</span>
        {{ editProfile ? 'Cancel' : 'Edit Profile' }}
      </button>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message', message.type]">
      <span class="material-icons-round">{{ message.icon }}</span>
      {{ message.text }}
    </div>

    <!-- Profile Form -->
    <div v-if="editProfile" class="auth-card">
      <div class="auth-header">
        <h2>Edit Profile</h2>
        <p>Update your personal information</p>
      </div>

      <form @submit.prevent="handleUpdateProfile" class="auth-form">
        <div class="form-group">
          <label for="firstName" class="form-label">First Name</label>
          <input
            id="firstName"
            v-model="form.firstName"
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
            v-model="form.lastName"
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
            v-model="form.email"
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
            v-model="form.username"
            type="text"
            class="form-input"
            placeholder="Enter your username"
            :disabled="loading"
          />
          <div v-if="errors.username" class="form-error">{{ errors.username }}</div>
        </div>

        <button
          type="submit"
          class="auth-button"
          :disabled="loading"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else class="material-icons-round">save</span>
          {{ loading ? 'Updating...' : 'Update Profile' }}
        </button>
      </form>
    </div>

    <!-- Account Information -->
    <div class="usage-card">
      <div class="usage-header">
        <h3 class="usage-title">Account Information</h3>
      </div>
      <div class="account-details">
        <div class="account-detail">
          <span class="account-label">Member Since</span>
          <span class="account-value">{{ formatDate(user?.created_at) }}</span>
        </div>
        <div class="account-detail">
          <span class="account-label">Last Login</span>
          <span class="account-value">{{ formatDate(user?.last_login) }}</span>
        </div>
        <div class="account-detail">
          <span class="account-label">Account Status</span>
          <span class="account-value" :class="user?.is_active ? 'active' : 'inactive'">
            {{ user?.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Role and Permissions -->
    <div class="role-card">
      <div class="role-header">
        <h3 class="role-name">Current Role</h3>
        <div class="role-badge" :class="userRole">{{ userRole }}</div>
      </div>
      <div class="permission-list">
        <div v-for="permission in userPermissions" :key="permission" class="permission-item">
          <span class="material-icons-round permission-icon">check_circle</span>
          <span>{{ formatPermission(permission) }}</span>
        </div>
      </div>
    </div>

    <!-- Usage Limits -->
    <div class="usage-card">
      <div class="usage-header">
        <h3 class="usage-title">Usage Limits</h3>
      </div>
      <div class="usage-stats">
        <div class="usage-stat">
          <div class="usage-label">Training Jobs</div>
          <div class="usage-progress">
            <div class="usage-progress-bar" :style="{ width: trainingUsage + '%' }"></div>
          </div>
          <div class="usage-text">{{ trainingUsed }}/{{ trainingLimit }}</div>
        </div>
        <div class="usage-stat">
          <div class="usage-label">Model Storage</div>
          <div class="usage-progress">
            <div class="usage-progress-bar" :style="{ width: storageUsage + '%' }"></div>
          </div>
          <div class="usage-text">{{ storageUsed }}/{{ storageLimit }}</div>
        </div>
        <div class="usage-stat">
          <div class="usage-label">API Calls</div>
          <div class="usage-progress">
            <div class="usage-progress-bar" :style="{ width: apiUsage + '%' }"></div>
          </div>
          <div class="usage-text">{{ apiUsed }}/{{ apiLimit }}</div>
        </div>
      </div>
    </div>

    <!-- Security Settings -->
    <div class="auth-card">
      <div class="auth-header">
        <h2>Security Settings</h2>
        <p>Manage your account security</p>
      </div>

      <div class="security-actions">
        <button class="auth-button secondary" @click="showChangePassword = !showChangePassword">
          <span class="material-icons-round">lock</span>
          Change Password
        </button>
        <button class="auth-button secondary" @click="handleLogout">
          <span class="material-icons-round">logout</span>
          Sign Out
        </button>
      </div>

      <!-- Change Password Form -->
      <div v-if="showChangePassword" class="password-form">
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
</template>

<script>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Profile',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Reactive state
    const loading = ref(false)
    const errors = ref({})
    const message = ref(null)
    const editProfile = ref(false)
    const showChangePassword = ref(false)
    
    // Form data
    const form = reactive({
      firstName: '',
      lastName: '',
      email: '',
      username: ''
    })
    
    const passwordForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: ''
    })
    
    // Computed properties
    const user = computed(() => authStore.user)
    const userRole = computed(() => authStore.userRole)
    const userPermissions = computed(() => authStore.userPermissions)
    
    // Mock usage data (replace with real API calls)
    const trainingUsed = ref(5)
    const trainingLimit = ref(10)
    const storageUsed = ref(2.5)
    const storageLimit = ref(5)
    const apiUsed = ref(150)
    const apiLimit = ref(1000)
    
    const trainingUsage = computed(() => (trainingUsed.value / trainingLimit.value) * 100)
    const storageUsage = computed(() => (storageUsed.value / storageLimit.value) * 100)
    const apiUsage = computed(() => (apiUsed.value / apiLimit.value) * 100)
    
    // Methods
    const showMessage = (type, text, icon = 'info') => {
      message.value = { type, text, icon }
      setTimeout(() => {
        message.value = null
      }, 5000)
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
    
    const formatPermission = (permission) => {
      return permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
    
    const validateProfileForm = () => {
      errors.value = {}
      
      if (!form.firstName.trim()) {
        errors.value.firstName = 'First name is required'
      }
      
      if (!form.lastName.trim()) {
        errors.value.lastName = 'Last name is required'
      }
      
      if (!form.email.trim()) {
        errors.value.email = 'Email is required'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        errors.value.email = 'Please enter a valid email address'
      }
      
      if (!form.username.trim()) {
        errors.value.username = 'Username is required'
      } else if (form.username.length < 3) {
        errors.value.username = 'Username must be at least 3 characters'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const validatePasswordForm = () => {
      errors.value = {}
      
      if (!passwordForm.currentPassword.trim()) {
        errors.value.currentPassword = 'Current password is required'
      }
      
      if (!passwordForm.newPassword.trim()) {
        errors.value.newPassword = 'New password is required'
      } else if (passwordForm.newPassword.length < 8) {
        errors.value.newPassword = 'Password must be at least 8 characters'
      }
      
      if (!passwordForm.confirmNewPassword.trim()) {
        errors.value.confirmNewPassword = 'Please confirm your new password'
      } else if (passwordForm.newPassword !== passwordForm.confirmNewPassword) {
        errors.value.confirmNewPassword = 'Passwords do not match'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const handleUpdateProfile = async () => {
      if (!validateProfileForm()) return
      
      loading.value = true
      errors.value = {}
      message.value = null
      
      try {
        const response = await authStore.updateProfile({
          firstName: form.firstName,
          lastName: form.lastName,
          email: form.email,
          username: form.username
        })
        
        if (response.success) {
          showMessage('success', 'Profile updated successfully!', 'check_circle')
          editProfile.value = false
        } else {
          showMessage('error', response.error || 'Profile update failed', 'error')
        }
      } catch (error) {
        console.error('Profile update error:', error)
        showMessage('error', 'An unexpected error occurred', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const handleChangePassword = async () => {
      if (!validatePasswordForm()) return
      
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
          showChangePassword.value = false
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
    
    const handleLogout = async () => {
      await authStore.logout()
      router.push('/login')
    }
    
    const loadUserData = () => {
      if (user.value) {
        form.firstName = user.value.firstName || ''
        form.lastName = user.value.lastName || ''
        form.email = user.value.email || ''
        form.username = user.value.username || ''
      }
    }
    
    onMounted(() => {
      loadUserData()
    })
    
    return {
      // State
      loading,
      errors,
      message,
      editProfile,
      showChangePassword,
      
      // Forms
      form,
      passwordForm,
      
      // Computed
      user,
      userRole,
      userPermissions,
      trainingUsage,
      storageUsage,
      apiUsage,
      
      // Usage data
      trainingUsed,
      trainingLimit,
      storageUsed,
      storageLimit,
      apiUsed,
      apiLimit,
      
      // Methods
      handleUpdateProfile,
      handleChangePassword,
      handleLogout,
      formatDate,
      formatPermission
    }
  }
}
</script>

<style scoped>
@import '@/assets/rbac.css';

/* Additional component-specific styles */
.profile-container {
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

.profile-header {
  display: flex;
  align-items: center;
  gap: var(--spacer-lg);
  margin-bottom: var(--spacer-xl);
  padding: var(--spacer-lg);
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: var(--radius-full);
  background-color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow);
}

.profile-avatar .material-icons-round {
  font-size: 4rem;
  color: white;
}

.profile-info {
  flex: 1;
}

.profile-info h1 {
  color: var(--text-color);
  margin-bottom: var(--spacer-sm);
  font-size: 1.8rem;
  font-weight: 700;
}

.profile-info p {
  color: var(--text-muted);
  margin-bottom: var(--spacer-md);
  font-size: 1.1rem;
}

.account-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacer-md);
}

.account-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-sm);
}

.account-label {
  font-size: 0.9rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 600;
}

.account-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
}

.account-value.active {
  color: var(--success);
}

.account-value.inactive {
  color: var(--danger);
}

.usage-stats {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.usage-stat {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-sm);
}

.usage-label {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 600;
}

.usage-text {
  font-size: 0.9rem;
  color: var(--text-color);
  font-weight: 600;
  text-align: right;
}

.security-actions {
  display: flex;
  gap: var(--spacer-md);
  margin-bottom: var(--spacer-lg);
}

.password-form {
  margin-top: var(--spacer-lg);
  padding-top: var(--spacer-lg);
  border-top: 1px solid var(--shadow-dark);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-avatar {
    width: 100px;
    height: 100px;
  }
  
  .profile-avatar .material-icons-round {
    font-size: 3rem;
  }
  
  .security-actions {
    flex-direction: column;
  }
  
  .account-details {
    grid-template-columns: 1fr;
  }
}
</style>
