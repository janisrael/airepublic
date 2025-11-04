<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Forgot Password</h1>
        <p>Enter your email address and we'll send you a link to reset your password</p>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" :class="['message', message.type]">
        <span class="material-icons-round">{{ message.icon }}</span>
        {{ message.text }}
      </div>

      <!-- Forgot Password Form -->
      <form @submit.prevent="handleForgotPassword" class="auth-form">
        <div class="form-group">
          <label for="email" class="form-label">Email Address</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="Enter your email address"
            required
            :disabled="loading"
          />
          <div v-if="errors.email" class="form-error">{{ errors.email }}</div>
        </div>

        <button
          type="submit"
          class="auth-button"
          :disabled="loading || !isFormValid"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else class="material-icons-round">send</span>
          {{ loading ? 'Sending...' : 'Send Reset Link' }}
        </button>
      </form>

      <!-- Back to Login -->
      <div style="text-align: center; margin-top: var(--spacer-lg);">
        <p>
          Remember your password?
          <router-link to="/login" class="auth-link">Sign in</router-link>
        </p>
        <p>
          Don't have an account?
          <router-link to="/register" class="auth-link">Sign up</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'ForgotPassword',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Reactive form data
    const form = reactive({
      email: ''
    })
    
    // Reactive state
    const loading = ref(false)
    const errors = ref({})
    const message = ref(null)
    
    // Computed properties
    const isFormValid = computed(() => {
      return form.email.trim() && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)
    })
    
    // Methods
    const validateForm = () => {
      errors.value = {}
      
      if (!form.email.trim()) {
        errors.value.email = 'Email is required'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        errors.value.email = 'Please enter a valid email address'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const showMessage = (type, text, icon = 'info') => {
      message.value = { type, text, icon }
      setTimeout(() => {
        message.value = null
      }, 5000)
    }
    
    const handleForgotPassword = async () => {
      if (!validateForm()) return
      
      loading.value = true
      errors.value = {}
      message.value = null
      
      try {
        const response = await authStore.forgotPassword(form.email)
        
        if (response.success) {
          showMessage('success', response.message || 'Password reset link sent to your email!', 'check_circle')
          
          // Redirect to login after successful request
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        } else {
          showMessage('error', response.error || 'Failed to send reset link', 'error')
        }
      } catch (error) {
        console.error('Forgot password error:', error)
        showMessage('error', 'An unexpected error occurred', 'error')
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      loading,
      errors,
      message,
      isFormValid,
      handleForgotPassword
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

/* Animation for form elements */
.form-group {
  animation: slideInUp 0.6s ease-out;
}

.form-group:nth-child(1) { animation-delay: 0.1s; }

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