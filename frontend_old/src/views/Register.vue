<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Create Account</h1>
        <p>Join AI Refinement Dashboard and start building amazing models</p>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" :class="['message', message.type]">
        <span class="material-icons-round">{{ message.icon }}</span>
        {{ message.text }}
      </div>

      <!-- Registration Form -->
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="username" class="form-label">Username</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="form-input"
            placeholder="Choose a username"
            required
            :disabled="loading"
          />
          <div v-if="errors.username" class="form-error">{{ errors.username }}</div>
        </div>

        <div class="form-group">
          <label for="email" class="form-label">Email Address</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="Enter your email"
            required
            :disabled="loading"
          />
          <div v-if="errors.email" class="form-error">{{ errors.email }}</div>
      </div>

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
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="Create a strong password"
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
          <label for="confirmPassword" class="form-label">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            class="form-input"
            placeholder="Confirm your password"
            required
            :disabled="loading"
          />
          <div v-if="errors.confirmPassword" class="form-error">{{ errors.confirmPassword }}</div>
        </div>

        <div class="form-group">
          <label class="form-label">
            <input
              v-model="form.agreeToTerms"
              type="checkbox"
              required
              :disabled="loading"
            />
            I agree to the <a href="/terms" class="auth-link">Terms of Service</a> and <a href="/privacy" class="auth-link">Privacy Policy</a>
          </label>
          <div v-if="errors.agreeToTerms" class="form-error">{{ errors.agreeToTerms }}</div>
      </div>

        <div class="form-group">
          <label class="form-label">
            <input
              v-model="form.subscribeNewsletter"
              type="checkbox"
              :disabled="loading"
            />
            Subscribe to our newsletter for updates and tips
          </label>
    </div>

        <button
          type="submit"
          class="auth-button"
          :disabled="loading || !isFormValid"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else class="material-icons-round">person_add</span>
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>

      <!-- Divider -->
      <div class="auth-divider">
        <span>or</span>
      </div>

      <!-- Social Registration -->
      <div class="social-login">
        <button
          @click="handleSocialRegister('google')"
          class="social-button google"
          :disabled="loading"
        >
          <span class="material-icons-round">login</span>
          Sign up with Google
        </button>
        <button
          @click="handleSocialRegister('github')"
          class="social-button github"
          :disabled="loading"
        >
          <span class="material-icons-round">code</span>
          Sign up with GitHub
        </button>
      </div>

      <!-- Links -->
      <div style="text-align: center; margin-top: var(--spacer-lg);">
        <p>
          Already have an account?
          <router-link to="/login" class="auth-link">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Reactive form data
    const form = reactive({
      username: '',
      email: '',
      firstName: '',
      lastName: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false,
      subscribeNewsletter: false
    })
    
    // Reactive state
    const loading = ref(false)
    const errors = ref({})
    const message = ref(null)
    const passwordStrength = ref(null)
    
    // Computed properties
    const isFormValid = computed(() => {
      return form.username.trim() && 
             form.email.trim() && 
             form.password.trim() && 
             form.confirmPassword.trim() && 
             form.agreeToTerms
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
      
      // Username validation
      if (!form.username.trim()) {
        errors.value.username = 'Username is required'
      } else if (form.username.length < 3) {
        errors.value.username = 'Username must be at least 3 characters'
      } else if (!/^[a-zA-Z0-9_]+$/.test(form.username)) {
        errors.value.username = 'Username can only contain letters, numbers, and underscores'
      }
      
      // Email validation
      if (!form.email.trim()) {
        errors.value.email = 'Email is required'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        errors.value.email = 'Please enter a valid email address'
      }
      
      // Password validation
      if (!form.password.trim()) {
        errors.value.password = 'Password is required'
      } else if (form.password.length < 8) {
        errors.value.password = 'Password must be at least 8 characters'
      } else if (passwordStrength.value && passwordStrength.value.level === 'weak') {
        errors.value.password = 'Password is too weak. Please use a stronger password.'
      }
      
      // Confirm password validation
      if (!form.confirmPassword.trim()) {
        errors.value.confirmPassword = 'Please confirm your password'
      } else if (form.password !== form.confirmPassword) {
        errors.value.confirmPassword = 'Passwords do not match'
      }
      
      // Terms agreement validation
      if (!form.agreeToTerms) {
        errors.value.agreeToTerms = 'You must agree to the terms and conditions'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const showMessage = (type, text, icon = 'info') => {
      message.value = { type, text, icon }
      setTimeout(() => {
        message.value = null
      }, 5000)
    }
    
    const handleRegister = async () => {
      if (!validateForm()) return
      
      loading.value = true
      errors.value = {}
      message.value = null
      
      try {
        const response = await authStore.register({
          username: form.username,
          email: form.email,
          firstName: form.firstName,
          lastName: form.lastName,
          password: form.password,
          subscribeNewsletter: form.subscribeNewsletter
        })
        
        if (response.success) {
          showMessage('success', 'Account created successfully! Please check your email for verification.', 'check_circle')
          
          // Redirect to login after successful registration
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        } else {
          showMessage('error', response.error || 'Registration failed', 'error')
        }
      } catch (error) {
        console.error('Registration error:', error)
        showMessage('error', 'An unexpected error occurred', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const handleSocialRegister = async (provider) => {
      loading.value = true
      message.value = null
      
      try {
        const response = await authStore.socialRegister(provider)
        
        if (response.success) {
          showMessage('success', `Registration with ${provider} successful!`, 'check_circle')
          router.push('/dashboard')
      } else {
          showMessage('error', response.error || `${provider} registration failed`, 'error')
        }
      } catch (error) {
        console.error(`${provider} registration error:`, error)
        showMessage('error', `An error occurred with ${provider} registration`, 'error')
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      loading,
      errors,
      message,
      passwordStrength,
      isFormValid,
      handleRegister,
      handleSocialRegister
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
  max-width: 500px;
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

.social-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
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
.form-group:nth-child(3) { animation-delay: 0.3s; }
.form-group:nth-child(4) { animation-delay: 0.4s; }
.form-group:nth-child(5) { animation-delay: 0.5s; }
.form-group:nth-child(6) { animation-delay: 0.6s; }
.form-group:nth-child(7) { animation-delay: 0.7s; }
.form-group:nth-child(8) { animation-delay: 0.8s; }

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
  
  .social-login {
    gap: var(--spacer-sm);
  }
}
</style>
