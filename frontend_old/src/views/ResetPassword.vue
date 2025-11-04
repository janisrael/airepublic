<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Reset Password</h1>
        <p>Enter your new password below</p>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" :class="['message', message.type]">
        <span class="material-icons-round">{{ message.icon }}</span>
        {{ message.text }}
      </div>

      <!-- Reset Password Form -->
      <form @submit.prevent="handleResetPassword" class="auth-form">
        <div class="form-group">
          <label for="password" class="form-label">New Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="Enter your new password"
            required
            :disabled="loading"
          />
          <div v-if="errors.password" class="form-error">{{ errors.password }}</div>
          <div v-if="passwordStrength" class="password-strength">
            <div class="strength-bar">
              <div 
                :class="['strength-fill', passwordStrength.level]"
                :style="{ width: passwordStrength.percentage + '%' }"
              ></div>
            </div>
            <span class="strength-text">{{ passwordStrength.text }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword" class="form-label">Confirm New Password</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            class="form-input"
            placeholder="Confirm your new password"
            required
            :disabled="loading"
          />
          <div v-if="errors.confirmPassword" class="form-error">{{ errors.confirmPassword }}</div>
        </div>

        <button
          type="submit"
          class="auth-button"
          :disabled="loading || !isFormValid"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else class="material-icons-round">lock_reset</span>
          {{ loading ? 'Resetting...' : 'Reset Password' }}
        </button>
      </form>

      <!-- Back to Login -->
      <div style="text-align: center; margin-top: var(--spacer-lg);">
        <p>
          Remember your password?
          <router-link to="/login" class="auth-link">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'ResetPassword',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()
    
    // Reactive form data
    const form = reactive({
      password: '',
      confirmPassword: ''
    })
    
    // Reactive state
    const loading = ref(false)
    const errors = ref({})
    const message = ref(null)
    const passwordStrength = ref(null)
    const resetToken = ref('')
    
    // Computed properties
    const isFormValid = computed(() => {
      return form.password.trim() && 
             form.confirmPassword.trim() && 
             form.password === form.confirmPassword &&
             passwordStrength.value && 
             passwordStrength.value.level !== 'weak'
    })
    
    // Watch password for strength calculation
    watch(() => form.password, (newPassword) => {
      if (newPassword) {
        passwordStrength.value = calculatePasswordStrength(newPassword)
      } else {
        passwordStrength.value = null
      }
    })
    
    // Methods
    const calculatePasswordStrength = (password) => {
      let score = 0
      let feedback = []
      
      // Length check
      if (password.length >= 8) score += 1
      else feedback.push('At least 8 characters')
      
      // Uppercase check
      if (/[A-Z]/.test(password)) score += 1
      else feedback.push('One uppercase letter')
      
      // Lowercase check
      if (/[a-z]/.test(password)) score += 1
      else feedback.push('One lowercase letter')
      
      // Number check
      if (/\d/.test(password)) score += 1
      else feedback.push('One number')
      
      // Special character check
      if (/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) score += 1
      else feedback.push('One special character')
      
      const levels = ['weak', 'fair', 'good', 'strong', 'very-strong']
      const percentages = [20, 40, 60, 80, 100]
      const texts = ['Very Weak', 'Weak', 'Fair', 'Good', 'Very Strong']
      
      const levelIndex = Math.min(score - 1, 4)
      
      return {
        level: levels[levelIndex],
        percentage: percentages[levelIndex],
        text: texts[levelIndex],
        feedback: feedback
      }
    }
    
    const validateForm = () => {
      errors.value = {}
      
      if (!form.password.trim()) {
        errors.value.password = 'Password is required'
      } else if (form.password.length < 8) {
        errors.value.password = 'Password must be at least 8 characters'
      } else if (passwordStrength.value && passwordStrength.value.level === 'weak') {
        errors.value.password = 'Password is too weak. Please use a stronger password.'
      }
      
      if (!form.confirmPassword.trim()) {
        errors.value.confirmPassword = 'Please confirm your password'
      } else if (form.password !== form.confirmPassword) {
        errors.value.confirmPassword = 'Passwords do not match'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const showMessage = (type, text, icon = 'info') => {
      message.value = { type, text, icon }
      setTimeout(() => {
        message.value = null
      }, 5000)
    }
    
    const handleResetPassword = async () => {
      if (!validateForm()) return
      
      loading.value = true
      errors.value = {}
      message.value = null
      
      try {
        const response = await authStore.resetPassword(resetToken.value, form.password)
        
        if (response.success) {
          showMessage('success', response.message || 'Password reset successfully!', 'check_circle')
          
          // Redirect to login after successful reset
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        } else {
          showMessage('error', response.error || 'Password reset failed', 'error')
        }
      } catch (error) {
        console.error('Reset password error:', error)
        showMessage('error', 'An unexpected error occurred', 'error')
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      // Get reset token from route params
      resetToken.value = route.params.token
      
      if (!resetToken.value) {
        showMessage('error', 'Invalid reset token', 'error')
        setTimeout(() => {
          router.push('/forgot-password')
        }, 2000)
      }
    })
    
    return {
      form,
      loading,
      errors,
      message,
      passwordStrength,
      resetToken,
      isFormValid,
      handleResetPassword
    }
  }
}
</script>

<style scoped>
@import '@/assets/rbac.css';

/* Additional component-specific styles */
.auth-container {
  background: linear-gradient(135deg, var(--bg-color) 0%, #d1d9e6 100%);
}

.auth-card {
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.form-input:focus {
  box-shadow: var(--shadow-inset), 0 0 0 3px rgba(78, 115, 223, 0.1);
}

.auth-button {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
}

.auth-button:hover {
  background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
}

/* Password strength indicator */
.password-strength {
  margin-top: var(--spacer-sm);
}

.strength-bar {
  width: 100%;
  height: 4px;
  background-color: var(--bg-color);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: var(--spacer-sm);
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: var(--radius-sm);
}

.strength-fill.weak {
  background-color: var(--danger);
}

.strength-fill.fair {
  background-color: var(--warning);
}

.strength-fill.good {
  background-color: var(--info);
}

.strength-fill.strong {
  background-color: var(--success);
}

.strength-fill.very-strong {
  background-color: var(--success);
}

.strength-text {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.strength-text.weak {
  color: var(--danger);
}

.strength-text.fair {
  color: var(--warning);
}

.strength-text.good {
  color: var(--info);
}

.strength-text.strong {
  color: var(--success);
}

.strength-text.very-strong {
  color: var(--success);
}

/* Animation for form elements */
.form-group {
  animation: slideInUp 0.6s ease-out;
}

.form-group:nth-child(1) { animation-delay: 0.1s; }
.form-group:nth-child(2) { animation-delay: 0.2s; }

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Loading state */
.loading {
  opacity: 0.7;
  pointer-events: none;
}

/* Responsive adjustments */
@media (max-width: 480px) {
  .auth-card {
    margin: var(--spacer);
    padding: var(--spacer-lg);
  }
  
  .auth-header h1 {
    font-size: 1.5rem;
  }
}
</style>
