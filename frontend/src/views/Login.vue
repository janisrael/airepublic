<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Welcome Back</h1>
        <p>Sign in to your AI Republic account</p>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" :class="['message', message.type]">
        <span class="material-icons-round">{{ message.icon }}</span>
        {{ message.text }}
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="username" class="form-label">Username or Email</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="form-input"
            placeholder="Enter your username or email"
            required
            :disabled="loading"
          />
          <div v-if="errors.username" class="form-error">{{ errors.username }}</div>
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="Enter your password"
            required
            :disabled="loading"
          />
          <div v-if="errors.password" class="form-error">{{ errors.password }}</div>
        </div>
        
        <div class="form-group">
          <label class="form-label">
            <input
              v-model="form.rememberMe"
              type="checkbox"
              :disabled="loading"
            />
            Remember me
          </label>
        </div>

        <button
          type="submit"
          class="auth-button"
          :disabled="loading || !isFormValid"
        >
          <Loader v-if="loading" />
          <span v-else class="material-icons-round">login</span>
          {{ loading ? 'Signing In...' : 'Sign In' }}
        </button>
      </form>

      <!-- Divider -->
      <div class="auth-divider">
        <span>or</span>
      </div>

      <!-- Social Login -->
      <div class="social-login">
        <button
          @click="handleSocialLogin('google')"
          class="social-button google"
          :disabled="loading"
        >
          <span class="material-icons-round">login</span>
          Continue with Google
        </button>
        <button
          @click="handleSocialLogin('github')"
          class="social-button github"
          :disabled="loading"
        >
          <span class="material-icons-round">code</span>
          Continue with GitHub
        </button>
      </div>

      <!-- Links -->
      <div style="text-align: center; margin-top: var(--spacer-lg);">
        <p>
          Don't have an account?
          <router-link to="/register" class="auth-link">Sign up</router-link>
        </p>
        <p>
          <router-link to="/forgot-password" class="auth-link">Forgot your password?</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Loader from '@/components/Loader.vue'

export default {
  name: 'Login',
  components: {
    Loader
  },
  data() {
    return {
      form: {
        username: '',
        password: '',
        rememberMe: false
      },
      errors: {},
      message: null
    }
  },
  computed: {
    authStore() {
      return useAuthStore()
    },
    loading() {
      return this.authStore.loading
    },
    isFormValid() {
      return this.form.username.trim() && this.form.password.trim()
    }
  },
  methods: {
    validateForm() {
      this.errors = {}

      if (!this.form.username.trim()) {
        this.errors.username = 'Username or email is required'
      }

      if (!this.form.password.trim()) {
        this.errors.password = 'Password is required'
      } else if (this.form.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters'
      }

      return Object.keys(this.errors).length === 0
    },
    showMessage(type, text, icon = 'info') {
      this.message = { type, text, icon }
      setTimeout(() => {
        this.message = null
      }, 5000)
    },
    async handleLogin() {
      if (!this.validateForm()) return

      this.errors = {}
      this.message = null

      try {
        const response = await this.authStore.login({
          username: this.form.username,
          password: this.form.password,
          rememberMe: this.form.rememberMe
        })

        if (response.success) {
          this.showMessage('success', 'Login successful! Redirecting...', 'check_circle')
          this.$emit('changelogin', true)
          setTimeout(() => {
            this.$router.push('/dashboard')
          }, 1000)
        } else {
          this.showMessage('error', response.error || 'Login failed', 'error')
        }
      } catch (error) {
        console.error('Login error:', error)
        this.showMessage('error', 'An unexpected error occurred', 'error')
      }
    },
    async handleSocialLogin(provider) {
      this.message = null

      try {
        const response = await this.authStore.socialLogin(provider)
        if (response.success) {
          this.showMessage('success', `Login with ${provider} successful!`, 'check_circle')
          this.$router.push('/dashboard')
        } else {
          this.showMessage('error', response.error || `${provider} login failed`, 'error')
        }
      } catch (error) {
        console.error(`${provider} login error:`, error)
        this.showMessage('error', `An error occurred with ${provider} login`, 'error')
      }
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
  padding: 30px;
}
.form-input {
  padding: 10px !important;
}
.form-input:focus {
  box-shadow: var(--shadow-inset), 0 0 0 3px rgba(78, 115, 223, 0.1);
}

.auth-button {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  
}
.auth-divider {
  margin: 10px;
}
.auth-form {
  gap: 0px;
}
.social-button, .auth-button {
  padding: 10px;
}
.auth-button:hover {
  background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
}

.social-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

/* Animation for form elements */
.form-group {
  animation: slideInUp 0.6s ease-out;
}

.form-group:nth-child(1) { animation-delay: 0.1s; }
.form-group:nth-child(2) { animation-delay: 0.2s; }
.form-group:nth-child(3) { animation-delay: 0.3s; }

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