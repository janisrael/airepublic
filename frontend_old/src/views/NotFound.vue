<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-icon">
        <span class="material-icons-round">error_outline</span>
      </div>
      
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>The page you're looking for doesn't exist or has been moved.</p>
      
      <div class="not-found-actions">
        <router-link to="/dashboard" class="auth-button">
          <span class="material-icons-round">home</span>
          Go to Dashboard
        </router-link>
        
        <button @click="goBack" class="auth-button secondary">
          <span class="material-icons-round">arrow_back</span>
          Go Back
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'NotFound',
  setup() {
    const router = useRouter()
    
    const goBack = () => {
      router.go(-1)
    }
    
    return {
      goBack
    }
  }
}
</script>

<style scoped>
@import '@/assets/rbac.css';

.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacer-lg);
  background: linear-gradient(135deg, var(--bg-color) 0%, var(--card-bg) 100%);
}

.not-found-content {
  text-align: center;
  max-width: 500px;
  padding: var(--spacer-xl);
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-hover);
}

.error-icon {
  margin-bottom: var(--spacer-lg);
}

.error-icon .material-icons-round {
  font-size: 5rem;
  color: var(--danger);
}

.not-found-content h1 {
  font-size: 6rem;
  font-weight: 700;
  color: var(--primary);
  margin: 0 0 var(--spacer-md);
  line-height: 1;
}

.not-found-content h2 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 var(--spacer-md);
}

.not-found-content p {
  color: var(--text-muted);
  font-size: 1.1rem;
  margin: 0 0 var(--spacer-xl);
  line-height: 1.6;
}

.not-found-actions {
  display: flex;
  gap: var(--spacer-md);
  justify-content: center;
  flex-wrap: wrap;
}

.not-found-actions .auth-button {
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--spacer-sm);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .not-found-content h1 {
    font-size: 4rem;
  }
  
  .not-found-content h2 {
    font-size: 1.5rem;
  }
  
  .not-found-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .not-found-actions .auth-button {
    width: 100%;
    max-width: 200px;
  }
}
</style>
