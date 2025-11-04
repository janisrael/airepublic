<template>
  <div class="admin-container">
    <div class="page-header">
      <h1>Admin Dashboard</h1>
      <p>Manage users, system settings, and analytics</p>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message', message.type]">
      <span class="material-icons-round">{{ message.icon }}</span>
      {{ message.text }}
    </div>

    <!-- Admin Tabs -->
    <div class="admin-tabs">
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

    <!-- Overview Tab -->
    <div v-if="activeTab === 'overview'" class="admin-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <span class="material-icons-round">people</span>
          </div>
          <div class="stat-content">
            <h3>Total Users</h3>
            <p class="stat-number">{{ stats.totalUsers }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <span class="material-icons-round">smart_toy</span>
          </div>
          <div class="stat-content">
            <h3>Active Models</h3>
            <p class="stat-number">{{ stats.activeModels }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <span class="material-icons-round">model_training</span>
          </div>
          <div class="stat-content">
            <h3>Training Jobs</h3>
            <p class="stat-number">{{ stats.trainingJobs }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <span class="material-icons-round">attach_money</span>
          </div>
          <div class="stat-content">
            <h3>Revenue</h3>
            <p class="stat-number">${{ stats.revenue }}</p>
          </div>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-card">
          <h3>User Growth</h3>
          <div class="chart-placeholder">
            <span class="material-icons-round">trending_up</span>
            <p>User growth chart would be displayed here</p>
          </div>
        </div>

        <div class="chart-card">
          <h3>Revenue Analytics</h3>
          <div class="chart-placeholder">
            <span class="material-icons-round">bar_chart</span>
            <p>Revenue analytics chart would be displayed here</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Tab -->
    <div v-if="activeTab === 'users'" class="admin-section">
      <div class="section-header">
        <h2>User Management</h2>
        <button class="auth-button" @click="showAddUser = true">
          <span class="material-icons-round">person_add</span>
          Add User
        </button>
      </div>

      <div class="users-table">
        <div class="table-header">
          <div>Username</div>
          <div>Email</div>
          <div>Role</div>
          <div>Status</div>
          <div>Created</div>
          <div>Actions</div>
        </div>
        <div v-for="user in users" :key="user.id" class="table-row">
          <div>{{ user.username }}</div>
          <div>{{ user.email }}</div>
          <div>
            <span class="role-badge" :class="user.role">{{ user.role }}</span>
          </div>
          <div>
            <span class="status-badge" :class="user.status">{{ user.status }}</span>
          </div>
          <div>{{ formatDate(user.created_at) }}</div>
          <div class="actions">
            <button class="action-btn edit" @click="editUser(user)">
              <span class="material-icons-round">edit</span>
            </button>
            <button class="action-btn delete" @click="deleteUser(user)">
              <span class="material-icons-round">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Roles Tab -->
    <div v-if="activeTab === 'roles'" class="admin-section">
      <div class="section-header">
        <h2>Role Management</h2>
        <button class="auth-button" @click="showAddRole = true">
          <span class="material-icons-round">add</span>
          Add Role
        </button>
      </div>

      <div class="roles-grid">
        <div v-for="role in roles" :key="role.id" class="role-card">
          <div class="role-header">
            <h3>{{ role.name }}</h3>
            <div class="role-actions">
              <button class="action-btn edit" @click="editRole(role)">
                <span class="material-icons-round">edit</span>
              </button>
              <button class="action-btn delete" @click="deleteRole(role)">
                <span class="material-icons-round">delete</span>
              </button>
            </div>
          </div>
          <p class="role-description">{{ role.description }}</p>
          <div class="role-stats">
            <span>{{ role.userCount }} users</span>
            <span>{{ role.permissionCount }} permissions</span>
          </div>
          <div class="permissions-list">
            <div v-for="permission in role.permissions" :key="permission" class="permission-tag">
              {{ permission }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Tab -->
    <div v-if="activeTab === 'system'" class="admin-section">
      <div class="system-settings">
        <div class="setting-group">
          <h3>System Configuration</h3>
          <div class="setting-item">
            <label>Maintenance Mode</label>
            <button 
              :class="['toggle-btn', { active: systemSettings.maintenanceMode }]"
              @click="toggleMaintenanceMode"
            >
              {{ systemSettings.maintenanceMode ? 'ON' : 'OFF' }}
            </button>
          </div>
          <div class="setting-item">
            <label>Registration Enabled</label>
            <button 
              :class="['toggle-btn', { active: systemSettings.registrationEnabled }]"
              @click="toggleRegistration"
            >
              {{ systemSettings.registrationEnabled ? 'ON' : 'OFF' }}
            </button>
          </div>
          <div class="setting-item">
            <label>Email Notifications</label>
            <button 
              :class="['toggle-btn', { active: systemSettings.emailNotifications }]"
              @click="toggleEmailNotifications"
            >
              {{ systemSettings.emailNotifications ? 'ON' : 'OFF' }}
            </button>
          </div>
        </div>

        <div class="setting-group">
          <h3>Resource Limits</h3>
          <div class="setting-item">
            <label>Max Training Jobs per User</label>
            <input 
              v-model="systemSettings.maxTrainingJobs" 
              type="number" 
              class="form-input"
            />
          </div>
          <div class="setting-item">
            <label>Max Storage per User (GB)</label>
            <input 
              v-model="systemSettings.maxStorage" 
              type="number" 
              class="form-input"
            />
          </div>
          <div class="setting-item">
            <label>Max API Calls per User</label>
            <input 
              v-model="systemSettings.maxAPICalls" 
              type="number" 
              class="form-input"
            />
          </div>
        </div>

        <div class="setting-group">
          <h3>Database Management</h3>
          <div class="setting-actions">
            <button class="auth-button secondary" @click="backupDatabase">
              <span class="material-icons-round">backup</span>
              Backup Database
            </button>
            <button class="auth-button secondary" @click="optimizeDatabase">
              <span class="material-icons-round">speed</span>
              Optimize Database
            </button>
            <button class="auth-button danger" @click="clearCache">
              <span class="material-icons-round">clear_all</span>
              Clear Cache
            </button>
          </div>
        </div>

        <button class="auth-button" @click="saveSystemSettings">
          <span class="material-icons-round">save</span>
          Save System Settings
        </button>
      </div>
    </div>

    <!-- Analytics Tab -->
    <div v-if="activeTab === 'analytics'" class="admin-section">
      <div class="analytics-grid">
        <div class="analytics-card">
          <h3>User Activity</h3>
          <div class="analytics-placeholder">
            <span class="material-icons-round">analytics</span>
            <p>User activity analytics would be displayed here</p>
          </div>
        </div>

        <div class="analytics-card">
          <h3>Model Performance</h3>
          <div class="analytics-placeholder">
            <span class="material-icons-round">assessment</span>
            <p>Model performance metrics would be displayed here</p>
          </div>
        </div>

        <div class="analytics-card">
          <h3>System Health</h3>
          <div class="analytics-placeholder">
            <span class="material-icons-round">health_and_safety</span>
            <p>System health monitoring would be displayed here</p>
          </div>
        </div>

        <div class="analytics-card">
          <h3>Error Logs</h3>
          <div class="analytics-placeholder">
            <span class="material-icons-round">bug_report</span>
            <p>Error logs and monitoring would be displayed here</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Add User Modal -->
    <div v-if="showAddUser" class="modal-overlay" @click="showAddUser = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New User</h3>
          <button class="modal-close" @click="showAddUser = false">
            <span class="material-icons-round">close</span>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleAddUser" class="auth-form">
            <div class="form-group">
              <label for="newUsername" class="form-label">Username</label>
              <input
                id="newUsername"
                v-model="newUser.username"
                type="text"
                class="form-input"
                placeholder="Enter username"
                required
              />
            </div>
            <div class="form-group">
              <label for="newEmail" class="form-label">Email</label>
              <input
                id="newEmail"
                v-model="newUser.email"
                type="email"
                class="form-input"
                placeholder="Enter email"
                required
              />
            </div>
            <div class="form-group">
              <label for="newRole" class="form-label">Role</label>
              <select id="newRole" v-model="newUser.role" class="form-input" required>
                <option value="user">User</option>
                <option value="premium_user">Premium User</option>
                <option value="developer">Developer</option>
                <option value="admin">Admin</option>
                <option value="superuser">Superuser</option>
              </select>
            </div>
            <div class="modal-actions">
              <button type="button" class="auth-button secondary" @click="showAddUser = false">Cancel</button>
              <button type="submit" class="auth-button">Add User</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Admin',
  setup() {
    const authStore = useAuthStore()
    
    // Reactive state
    const loading = ref(false)
    const message = ref(null)
    const activeTab = ref('overview')
    const showAddUser = ref(false)
    const showAddRole = ref(false)
    
    // Tabs configuration
    const tabs = ref([
      { id: 'overview', name: 'Overview', icon: 'dashboard' },
      { id: 'users', name: 'Users', icon: 'people' },
      { id: 'roles', name: 'Roles', icon: 'admin_panel_settings' },
      { id: 'system', name: 'System', icon: 'settings' },
      { id: 'analytics', name: 'Analytics', icon: 'analytics' }
    ])
    
    // Mock data (replace with real API calls)
    const stats = reactive({
      totalUsers: 1247,
      activeModels: 89,
      trainingJobs: 342,
      revenue: 45678
    })
    
    const users = ref([
      {
        id: 1,
        username: 'superuser',
        email: 'superuser@airepublic.com',
        role: 'superuser',
        status: 'active',
        created_at: new Date().toISOString()
      },
      {
        id: 2,
        username: 'admin',
        email: 'admin@airepublic.com',
        role: 'admin',
        status: 'active',
        created_at: new Date().toISOString()
      },
      {
        id: 3,
        username: 'premium',
        email: 'premium@airepublic.com',
        role: 'premium_user',
        status: 'active',
        created_at: new Date().toISOString()
      },
      {
        id: 4,
        username: 'user',
        email: 'user@airepublic.com',
        role: 'user',
        status: 'active',
        created_at: new Date().toISOString()
      },
      {
        id: 5,
        username: 'developer',
        email: 'developer@airepublic.com',
        role: 'developer',
        status: 'active',
        created_at: new Date().toISOString()
      }
    ])
    
    const roles = ref([
      {
        id: 1,
        name: 'superuser',
        description: 'Full system access',
        userCount: 1,
        permissionCount: 16,
        permissions: ['manage_users', 'manage_roles', 'manage_subscriptions', 'view_analytics']
      },
      {
        id: 2,
        name: 'admin',
        description: 'Administrative access',
        userCount: 1,
        permissionCount: 13,
        permissions: ['manage_users', 'manage_subscriptions', 'view_analytics']
      },
      {
        id: 3,
        name: 'premium_user',
        description: 'Premium features access',
        userCount: 1,
        permissionCount: 9,
        permissions: ['train_models', 'evaluate_models', 'access_premium_features']
      },
      {
        id: 4,
        name: 'user',
        description: 'Basic features access',
        userCount: 1,
        permissionCount: 4,
        permissions: ['train_models', 'evaluate_models']
      },
      {
        id: 5,
        name: 'developer',
        description: 'Development tools access',
        userCount: 1,
        permissionCount: 10,
        permissions: ['train_models', 'evaluate_models', 'access_premium_features']
      }
    ])
    
    const systemSettings = reactive({
      maintenanceMode: false,
      registrationEnabled: true,
      emailNotifications: true,
      maxTrainingJobs: 10,
      maxStorage: 10,
      maxAPICalls: 1000
    })
    
    const newUser = reactive({
      username: '',
      email: '',
      role: 'user'
    })
    
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
        month: 'short',
        day: 'numeric'
      })
    }
    
    const editUser = (user) => {
      showMessage('info', `Edit user: ${user.username}`, 'edit')
    }
    
    const deleteUser = (user) => {
      if (confirm(`Are you sure you want to delete user: ${user.username}?`)) {
        showMessage('success', `User ${user.username} deleted successfully`, 'delete')
      }
    }
    
    const editRole = (role) => {
      showMessage('info', `Edit role: ${role.name}`, 'edit')
    }
    
    const deleteRole = (role) => {
      if (confirm(`Are you sure you want to delete role: ${role.name}?`)) {
        showMessage('success', `Role ${role.name} deleted successfully`, 'delete')
      }
    }
    
    const handleAddUser = async () => {
      loading.value = true
      
      try {
        // Mock API call (replace with real implementation)
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        showMessage('success', `User ${newUser.username} added successfully`, 'person_add')
        showAddUser.value = false
        
        // Reset form
        newUser.username = ''
        newUser.email = ''
        newUser.role = 'user'
      } catch (error) {
        showMessage('error', 'Failed to add user', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const toggleMaintenanceMode = () => {
      systemSettings.maintenanceMode = !systemSettings.maintenanceMode
      showMessage('info', `Maintenance mode ${systemSettings.maintenanceMode ? 'enabled' : 'disabled'}`, 'settings')
    }
    
    const toggleRegistration = () => {
      systemSettings.registrationEnabled = !systemSettings.registrationEnabled
      showMessage('info', `Registration ${systemSettings.registrationEnabled ? 'enabled' : 'disabled'}`, 'settings')
    }
    
    const toggleEmailNotifications = () => {
      systemSettings.emailNotifications = !systemSettings.emailNotifications
      showMessage('info', `Email notifications ${systemSettings.emailNotifications ? 'enabled' : 'disabled'}`, 'settings')
    }
    
    const saveSystemSettings = async () => {
      loading.value = true
      
      try {
        // Mock API call (replace with real implementation)
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        showMessage('success', 'System settings saved successfully', 'save')
      } catch (error) {
        showMessage('error', 'Failed to save system settings', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const backupDatabase = () => {
      showMessage('info', 'Database backup started', 'backup')
    }
    
    const optimizeDatabase = () => {
      showMessage('info', 'Database optimization started', 'speed')
    }
    
    const clearCache = () => {
      showMessage('info', 'Cache cleared successfully', 'clear_all')
    }
    
    onMounted(() => {
      // Load admin data
      showMessage('info', 'Admin dashboard loaded', 'admin_panel_settings')
    })
    
    return {
      // State
      loading,
      message,
      activeTab,
      showAddUser,
      showAddRole,
      tabs,
      
      // Data
      stats,
      users,
      roles,
      systemSettings,
      newUser,
      
      // Methods
      editUser,
      deleteUser,
      editRole,
      deleteRole,
      handleAddUser,
      toggleMaintenanceMode,
      toggleRegistration,
      toggleEmailNotifications,
      saveSystemSettings,
      backupDatabase,
      optimizeDatabase,
      clearCache,
      formatDate
    }
  }
}
</script>

<style scoped>
@import '@/assets/rbac.css';

/* Additional component-specific styles */
.admin-container {
  max-width: 1400px;
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

.admin-tabs {
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

.admin-section {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacer-lg);
  margin-bottom: var(--spacer-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacer-lg);
  padding: var(--spacer-lg);
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  transition: var(--transition);
}

.stat-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--radius);
  background-color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon .material-icons-round {
  font-size: 2rem;
}

.stat-content h3 {
  color: var(--text-muted);
  margin: 0 0 var(--spacer-sm);
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
}

.stat-number {
  color: var(--text-color);
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacer-lg);
}

.chart-card {
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: var(--spacer-lg);
  box-shadow: var(--shadow);
}

.chart-card h3 {
  color: var(--text-color);
  margin: 0 0 var(--spacer-lg);
  font-size: 1.2rem;
  font-weight: 600;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background-color: var(--bg-color);
  border-radius: var(--radius);
  color: var(--text-muted);
}

.chart-placeholder .material-icons-round {
  font-size: 3rem;
  margin-bottom: var(--spacer-md);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacer-lg);
}

.section-header h2 {
  color: var(--text-color);
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.users-table {
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr;
  gap: var(--spacer-md);
  padding: var(--spacer-lg);
  background-color: var(--bg-color);
  font-weight: 600;
  color: var(--text-color);
  border-bottom: 1px solid var(--shadow-dark);
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr;
  gap: var(--spacer-md);
  padding: var(--spacer-lg);
  border-bottom: 1px solid var(--shadow-dark);
  transition: var(--transition);
}

.table-row:hover {
  background-color: var(--bg-color);
}

.table-row:last-child {
  border-bottom: none;
}

.role-badge {
  padding: var(--spacer-sm) var(--spacer-md);
  border-radius: var(--radius);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-badge.superuser {
  background-color: var(--danger);
  color: white;
}

.role-badge.admin {
  background-color: var(--warning);
  color: white;
}

.role-badge.premium_user {
  background-color: var(--info);
  color: white;
}

.role-badge.user {
  background-color: var(--success);
  color: white;
}

.role-badge.developer {
  background-color: var(--secondary);
  color: white;
}

.status-badge {
  padding: var(--spacer-sm) var(--spacer-md);
  border-radius: var(--radius);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background-color: var(--success);
  color: white;
}

.status-badge.inactive {
  background-color: var(--danger);
  color: white;
}

.actions {
  display: flex;
  gap: var(--spacer-sm);
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn.edit {
  background-color: var(--info);
  color: white;
}

.action-btn.edit:hover {
  background-color: #2980b9;
}

.action-btn.delete {
  background-color: var(--danger);
  color: white;
}

.action-btn.delete:hover {
  background-color: #c0392b;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacer-lg);
}

.role-card {
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: var(--spacer-lg);
  box-shadow: var(--shadow);
  transition: var(--transition);
}

.role-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

.role-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacer-md);
}

.role-header h3 {
  color: var(--text-color);
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  text-transform: capitalize;
}

.role-actions {
  display: flex;
  gap: var(--spacer-sm);
}

.role-description {
  color: var(--text-muted);
  margin: 0 0 var(--spacer-md);
  font-size: 0.9rem;
}

.role-stats {
  display: flex;
  gap: var(--spacer-md);
  margin-bottom: var(--spacer-md);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacer-sm);
}

.permission-tag {
  padding: var(--spacer-sm) var(--spacer-md);
  background-color: var(--bg-color);
  border-radius: var(--radius);
  font-size: 0.8rem;
  color: var(--text-color);
  border: 1px solid var(--shadow-dark);
}

.system-settings {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-xl);
}

.setting-group {
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: var(--spacer-lg);
  box-shadow: var(--shadow);
}

.setting-group h3 {
  color: var(--text-color);
  margin: 0 0 var(--spacer-lg);
  font-size: 1.2rem;
  font-weight: 600;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacer-md) 0;
  border-bottom: 1px solid var(--shadow-dark);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item label {
  color: var(--text-color);
  font-weight: 500;
}

.toggle-btn {
  padding: var(--spacer-sm) var(--spacer-md);
  border: none;
  border-radius: var(--radius);
  background-color: var(--danger);
  color: white;
  cursor: pointer;
  transition: var(--transition);
  font-weight: 600;
}

.toggle-btn.active {
  background-color: var(--success);
}

.setting-actions {
  display: flex;
  gap: var(--spacer-md);
  margin-top: var(--spacer-lg);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacer-lg);
}

.analytics-card {
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: var(--spacer-lg);
  box-shadow: var(--shadow);
}

.analytics-card h3 {
  color: var(--text-color);
  margin: 0 0 var(--spacer-lg);
  font-size: 1.2rem;
  font-weight: 600;
}

.analytics-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 150px;
  background-color: var(--bg-color);
  border-radius: var(--radius);
  color: var(--text-muted);
}

.analytics-placeholder .material-icons-round {
  font-size: 2rem;
  margin-bottom: var(--spacer-sm);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-hover);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacer-lg);
  border-bottom: 1px solid var(--shadow-dark);
}

.modal-header h3 {
  color: var(--text-color);
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: var(--spacer-sm);
  border-radius: var(--radius);
  transition: var(--transition);
}

.modal-close:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.modal-body {
  padding: var(--spacer-lg);
}

.modal-actions {
  display: flex;
  gap: var(--spacer-md);
  margin-top: var(--spacer-lg);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .admin-tabs {
    flex-wrap: wrap;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: var(--spacer-sm);
  }
  
  .roles-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .setting-actions {
    flex-direction: column;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>
