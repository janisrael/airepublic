<template>
  <div class="payment-container">
    <div class="page-header">
      <h1>Payment</h1>
      <p>Manage your payment methods and billing</p>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message', message.type]">
      <span class="material-icons-round">{{ message.icon }}</span>
      {{ message.text }}
    </div>

    <!-- Payment Content -->
    <div class="payment-content">
      <div class="auth-card">
        <div class="auth-header">
          <h2>Payment Methods</h2>
          <p>Manage your payment methods and billing information</p>
        </div>

        <div class="payment-placeholder">
          <span class="material-icons-round">payment</span>
          <h3>Payment System</h3>
          <p>Payment integration will be implemented here</p>
          <p>This component is ready for future payment integration</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Payment',
  setup() {
    const authStore = useAuthStore()
    
    // Reactive state
    const message = ref(null)
    
    // Methods
    const showMessage = (type, text, icon = 'info') => {
      message.value = { type, text, icon }
      setTimeout(() => {
        message.value = null
      }, 5000)
    }
    
    onMounted(() => {
      showMessage('info', 'Payment page loaded', 'payment')
    })
    
    return {
      message,
      showMessage
    }
  }
}
</script>

<style scoped>
@import '@/assets/rbac.css';

.payment-container {
  max-width: 800px;
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

.payment-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-lg);
}

.payment-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacer-xl);
  text-align: center;
  color: var(--text-muted);
}

.payment-placeholder .material-icons-round {
  font-size: 4rem;
  margin-bottom: var(--spacer-lg);
  color: var(--primary);
}

.payment-placeholder h3 {
  color: var(--text-color);
  margin: 0 0 var(--spacer-md);
  font-size: 1.5rem;
  font-weight: 600;
}

.payment-placeholder p {
  margin: 0 0 var(--spacer-sm);
  font-size: 1rem;
}

.payment-placeholder p:last-child {
  font-size: 0.9rem;
  color: var(--text-muted);
}
</style>
