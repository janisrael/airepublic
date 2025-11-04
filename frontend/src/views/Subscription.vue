<template>
  <div class="subscription-container">
    <div class="page-header">
      <h1>Subscription Management</h1>
      <p>Manage your subscription and billing preferences</p>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message', message.type]">
      <span class="material-icons-round">{{ message.icon }}</span>
      {{ message.text }}
    </div>

    <!-- Current Subscription -->
    <div v-if="currentSubscription" class="subscription-card">
      <div class="subscription-header">
        <h3 class="subscription-plan">{{ currentSubscription.plan_name }}</h3>
        <div class="subscription-status" :class="currentSubscription.status">
          {{ currentSubscription.status }}
        </div>
      </div>
      <div class="subscription-details">
        <div class="subscription-detail">
          <div class="subscription-detail-label">Billing Cycle</div>
          <div class="subscription-detail-value">{{ currentSubscription.billing_cycle }}</div>
        </div>
        <div class="subscription-detail">
          <div class="subscription-detail-label">Next Billing</div>
          <div class="subscription-detail-value">{{ formatDate(currentSubscription.next_billing_date) }}</div>
        </div>
        <div class="subscription-detail">
          <div class="subscription-detail-label">Amount</div>
          <div class="subscription-detail-value">${{ currentSubscription.amount }}</div>
        </div>
      </div>
      <div class="subscription-actions">
        <button 
          v-if="currentSubscription.status === 'active'"
          class="auth-button secondary" 
          @click="showCancelModal = true"
        >
          <span class="material-icons-round">cancel</span>
          Cancel Subscription
        </button>
        <button 
          v-if="currentSubscription.status === 'cancelled'"
          class="auth-button" 
          @click="handleReactivate"
        >
          <span class="material-icons-round">refresh</span>
          Reactivate Subscription
        </button>
        <button class="auth-button secondary" @click="showUpgradeModal = true">
          <span class="material-icons-round">upgrade</span>
          Change Plan
        </button>
      </div>
    </div>

    <!-- Available Plans -->
    <div class="plans-section">
      <h2>Available Plans</h2>
      <div class="plans-grid">
        <div 
          v-for="plan in availablePlans" 
          :key="plan.id" 
          class="plan-card"
          :class="{ 'current-plan': plan.id === currentSubscription?.plan_id, 'popular': plan.popular }"
        >
          <div v-if="plan.popular" class="plan-badge">Most Popular</div>
          <div class="plan-header">
            <h3 class="plan-name">{{ plan.name }}</h3>
            <div class="plan-price">
              <span class="price-amount">${{ plan.price }}</span>
              <span class="price-period">/{{ plan.billing_cycle }}</span>
            </div>
          </div>
          <div class="plan-description">
            <p>{{ plan.description }}</p>
          </div>
          <div class="plan-features">
            <div v-for="feature in plan.features" :key="feature" class="plan-feature">
              <span class="material-icons-round">check_circle</span>
              <span>{{ feature }}</span>
            </div>
          </div>
          <div class="plan-actions">
            <button 
              v-if="plan.id !== currentSubscription?.plan_id"
              class="auth-button" 
              @click="handleUpgrade(plan)"
              :disabled="loading"
            >
              <span class="material-icons-round">upgrade</span>
              {{ plan.id === 'free' ? 'Get Started' : 'Upgrade' }}
            </button>
            <button 
              v-else
              class="auth-button secondary" 
              disabled
            >
              <span class="material-icons-round">check</span>
              Current Plan
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Usage Limits -->
    <div class="usage-section">
      <h2>Usage Limits</h2>
      <div class="usage-cards">
        <div class="usage-card">
          <div class="usage-header">
            <h3 class="usage-title">Training Jobs</h3>
            <span class="usage-limit">{{ usageLimits.training.used }}/{{ usageLimits.training.limit }}</span>
          </div>
          <div class="usage-progress">
            <div 
              class="usage-progress-bar" 
              :style="{ width: (usageLimits.training.used / usageLimits.training.limit) * 100 + '%' }"
            ></div>
          </div>
          <div class="usage-stats">
            <span class="usage-used">{{ usageLimits.training.used }} used</span>
            <span class="usage-remaining">{{ usageLimits.training.limit - usageLimits.training.used }} remaining</span>
          </div>
        </div>

        <div class="usage-card">
          <div class="usage-header">
            <h3 class="usage-title">Model Storage</h3>
            <span class="usage-limit">{{ usageLimits.storage.used }}GB/{{ usageLimits.storage.limit }}GB</span>
          </div>
          <div class="usage-progress">
            <div 
              class="usage-progress-bar" 
              :style="{ width: (usageLimits.storage.used / usageLimits.storage.limit) * 100 + '%' }"
            ></div>
          </div>
          <div class="usage-stats">
            <span class="usage-used">{{ usageLimits.storage.used }}GB used</span>
            <span class="usage-remaining">{{ usageLimits.storage.limit - usageLimits.storage.used }}GB remaining</span>
          </div>
        </div>

        <div class="usage-card">
          <div class="usage-header">
            <h3 class="usage-title">API Calls</h3>
            <span class="usage-limit">{{ usageLimits.api.used }}/{{ usageLimits.api.limit }}</span>
          </div>
          <div class="usage-progress">
            <div 
              class="usage-progress-bar" 
              :style="{ width: (usageLimits.api.used / usageLimits.api.limit) * 100 + '%' }"
            ></div>
          </div>
          <div class="usage-stats">
            <span class="usage-used">{{ usageLimits.api.used }} used</span>
            <span class="usage-remaining">{{ usageLimits.api.limit - usageLimits.api.used }} remaining</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel Subscription Modal -->
    <div v-if="showCancelModal" class="modal-overlay" @click="showCancelModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Cancel Subscription</h3>
          <button class="modal-close" @click="showCancelModal = false">
            <span class="material-icons-round">close</span>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your current billing period.</p>
          <div class="modal-actions">
            <button class="auth-button secondary" @click="showCancelModal = false">Keep Subscription</button>
            <button class="auth-button danger" @click="handleCancelSubscription">Cancel Subscription</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Upgrade Plan Modal -->
    <div v-if="showUpgradeModal" class="modal-overlay" @click="showUpgradeModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Upgrade Plan</h3>
          <button class="modal-close" @click="showUpgradeModal = false">
            <span class="material-icons-round">close</span>
          </button>
        </div>
        <div class="modal-body">
          <p>Choose a new plan to upgrade to:</p>
          <div class="upgrade-plans">
            <div 
              v-for="plan in availablePlans.filter(p => p.id !== currentSubscription?.plan_id)" 
              :key="plan.id" 
              class="upgrade-plan"
              @click="handleUpgrade(plan)"
            >
              <h4>{{ plan.name }}</h4>
              <p>${{ plan.price }}/{{ plan.billing_cycle }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Subscription',
  setup() {
    const authStore = useAuthStore()
    
    // Reactive state
    const loading = ref(false)
    const message = ref(null)
    const showCancelModal = ref(false)
    const showUpgradeModal = ref(false)
    const currentSubscription = ref(null)
    
    // Mock data (replace with real API calls)
    const availablePlans = ref([
      {
        id: 'free',
        name: 'Free Plan',
        price: 0,
        billing_cycle: 'month',
        description: 'Perfect for getting started with AI model training',
        features: [
          '2 Training Jobs per month',
          '1GB Model Storage',
          '100 API Calls per month',
          'Basic Support'
        ],
        popular: false
      },
      {
        id: 'pro',
        name: 'Pro Plan',
        price: 29,
        billing_cycle: 'month',
        description: 'Ideal for developers and small teams',
        features: [
          '10 Training Jobs per month',
          '10GB Model Storage',
          '1000 API Calls per month',
          'Priority Support',
          'Advanced Analytics'
        ],
        popular: true
      },
      {
        id: 'enterprise',
        name: 'Enterprise Plan',
        price: 99,
        billing_cycle: 'month',
        description: 'For large teams and organizations',
        features: [
          'Unlimited Training Jobs',
          '100GB Model Storage',
          'Unlimited API Calls',
          '24/7 Support',
          'Custom Integrations',
          'Advanced Security'
        ],
        popular: false
      }
    ])
    
    const usageLimits = reactive({
      training: { used: 5, limit: 10 },
      storage: { used: 2.5, limit: 10 },
      api: { used: 150, limit: 1000 }
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
    
    const loadSubscriptionData = async () => {
      // Mock current subscription (replace with real API call)
      currentSubscription.value = {
        plan_id: 'pro',
        plan_name: 'Pro Plan',
        status: 'active',
        billing_cycle: 'Monthly',
        next_billing_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        amount: 29.99
      }
    }
    
    const handleUpgrade = async (plan) => {
      loading.value = true
      showUpgradeModal.value = false
      
      try {
        // Mock upgrade (replace with real API call)
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        showMessage('success', `Successfully upgraded to ${plan.name}!`, 'check_circle')
        await loadSubscriptionData()
      } catch (error) {
        showMessage('error', 'Upgrade failed. Please try again.', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const handleCancelSubscription = async () => {
      loading.value = true
      showCancelModal.value = false
      
      try {
        // Mock cancellation (replace with real API call)
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        showMessage('success', 'Subscription cancelled successfully. You will retain access until the end of your billing period.', 'check_circle')
        await loadSubscriptionData()
      } catch (error) {
        showMessage('error', 'Cancellation failed. Please try again.', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const handleReactivate = async () => {
      loading.value = true
      
      try {
        // Mock reactivation (replace with real API call)
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        showMessage('success', 'Subscription reactivated successfully!', 'check_circle')
        await loadSubscriptionData()
      } catch (error) {
        showMessage('error', 'Reactivation failed. Please try again.', 'error')
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadSubscriptionData()
    })
    
    return {
      // State
      loading,
      message,
      showCancelModal,
      showUpgradeModal,
      currentSubscription,
      availablePlans,
      usageLimits,
      
      // Methods
      handleUpgrade,
      handleCancelSubscription,
      handleReactivate,
      formatDate
    }
  }
}
</script>

<style scoped>
@import '@/assets/rbac.css';

/* Additional component-specific styles */
.subscription-container {
  max-width: 1200px;
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

.subscription-actions {
  display: flex;
  gap: var(--spacer-md);
  margin-top: var(--spacer-lg);
  padding-top: var(--spacer-lg);
  border-top: 1px solid var(--shadow-dark);
}

.plans-section {
  margin: var(--spacer-xl) 0;
}

.plans-section h2 {
  color: var(--text-color);
  margin-bottom: var(--spacer-lg);
  font-size: 1.5rem;
  font-weight: 600;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacer-lg);
}

.plan-card {
  position: relative;
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: var(--spacer-lg);
  box-shadow: var(--shadow);
  transition: var(--transition);
  border: 2px solid transparent;
}

.plan-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

.plan-card.current-plan {
  border-color: var(--primary);
  background: linear-gradient(135deg, var(--card-bg) 0%, rgba(78, 115, 223, 0.05) 100%);
}

.plan-card.popular {
  border-color: var(--success);
  transform: scale(1.05);
}

.plan-badge {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--success);
  color: white;
  padding: var(--spacer-sm) var(--spacer-md);
  border-radius: var(--radius);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.plan-header {
  text-align: center;
  margin-bottom: var(--spacer-lg);
}

.plan-name {
  color: var(--text-color);
  margin-bottom: var(--spacer-sm);
  font-size: 1.5rem;
  font-weight: 700;
}

.plan-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: var(--spacer-sm);
}

.price-amount {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
}

.price-period {
  font-size: 1rem;
  color: var(--text-muted);
}

.plan-description {
  text-align: center;
  margin-bottom: var(--spacer-lg);
}

.plan-description p {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
}

.plan-features {
  margin-bottom: var(--spacer-lg);
}

.plan-feature {
  display: flex;
  align-items: center;
  gap: var(--spacer-sm);
  margin-bottom: var(--spacer-sm);
  color: var(--text-color);
  font-size: 0.9rem;
}

.plan-feature .material-icons-round {
  color: var(--success);
  font-size: 1rem;
}

.plan-actions {
  text-align: center;
}

.usage-section {
  margin: var(--spacer-xl) 0;
}

.usage-section h2 {
  color: var(--text-color);
  margin-bottom: var(--spacer-lg);
  font-size: 1.5rem;
  font-weight: 600;
}

.usage-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacer-lg);
}

.usage-limit {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 600;
}

.usage-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: var(--spacer-sm);
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

.auth-button.danger {
  background-color: var(--danger);
  color: white;
}

.auth-button.danger:hover {
  background-color: #c0392b;
}

.upgrade-plans {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
  margin-top: var(--spacer-lg);
}

.upgrade-plan {
  padding: var(--spacer-md);
  border: 1px solid var(--shadow-dark);
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
}

.upgrade-plan:hover {
  border-color: var(--primary);
  background-color: rgba(78, 115, 223, 0.05);
}

.upgrade-plan h4 {
  color: var(--text-color);
  margin: 0 0 var(--spacer-sm);
  font-size: 1.1rem;
  font-weight: 600;
}

.upgrade-plan p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.9rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .plans-grid {
    grid-template-columns: 1fr;
  }
  
  .plan-card.popular {
    transform: none;
  }
  
  .usage-cards {
    grid-template-columns: 1fr;
  }
  
  .subscription-actions {
    flex-direction: column;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>
