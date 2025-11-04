import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import existing views
import Dashboard from '@/views/Dashboard.vue'
import Models from '@/views/Models.vue'
import ModelComparison from '@/views/ModelComparison.vue'
import Training from '@/views/Training.vue'
import TrainingHistory from '@/views/TrainingHistory.vue'
import Datasets from '@/views/Datasets.vue'
import AIRoom from '@/views/AIRoom.vue'
import Evaluation from '@/views/Evaluation.vue'

// Import new authentication views
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

// Import provider management view
import BaseModelProviders from '@/views/BaseModelProviders.vue'

// Import minion profile view
import MinionProfile from '@/views/MinionProfile.vue'

// Import spirit system views
import SpiritMarketplace from '@/views/SpiritMarketplace.vue'
import MinionBuilder from '@/views/MinionBuilder.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  // Existing routes (keep as-is, no auth required for now)
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/models',
    name: 'Models',
    component: Models
  },
  {
    path: '/modelcomparison',
    name: 'ModelComparison',
    component: ModelComparison
  },
  {
    path: '/training',
    name: 'Training',
    component: Training
  },
  {
    path: '/traininghistory',
    name: 'TrainingHistory',
    component: TrainingHistory
  },
  {
    path: '/datasets',
    name: 'Datasets',
    component: Datasets
  },
  {
    path: '/airoom',
    name: 'AIRoom',
    component: AIRoom
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: Evaluation
  },
  
  // New authentication routes
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/reset-password/:token',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPassword.vue'),
    meta: { requiresGuest: true }
  },
  
  // New user management routes (optional, for future use)
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { requiresAuth: true, requiresRole: ['admin', 'superuser'] }
  },
  {
    path: '/subscription',
    name: 'Subscription',
    component: () => import('@/views/Subscription.vue'),
    meta: { requiresAuth: true }
  },
      {
        path: '/payment',
        name: 'Payment',
        component: () => import('@/views/Payment.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/base-model-providers',
        name: 'BaseModelProviders',
        component: BaseModelProviders,
        meta: { 
          requiresAuth: true, 
          requiresRole: ['admin', 'superuser', 'developer'] 
        }
      },
      {
        path: '/minion/:id',
        name: 'MinionProfile',
        component: MinionProfile,
        meta: {
          requiresAuth: true
        }
      },
      {
        path: '/spirit-marketplace',
        name: 'SpiritMarketplace',
        component: SpiritMarketplace
      },
      {
        path: '/minion-builder',
        name: 'MinionBuilder',
        component: MinionBuilder
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/NotFound.vue')
      }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards (optional - only for new auth routes)
router.beforeEach(async (to, from, next) => {
  // Only apply auth guards to routes that explicitly require them
  if (to.meta.requiresAuth || to.meta.requiresGuest || to.meta.requiresRole || to.meta.requiresPermission) {
    const authStore = useAuthStore()
    
    // Initialize auth store if not already done
    if (!authStore.isAuthenticated && authStore.token) {
      await authStore.initialize()
    }

    // Check if route requires authentication
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next('/login')
      return
    }

    // Check if route requires guest (not authenticated)
    if (to.meta.requiresGuest && authStore.isAuthenticated) {
      next('/dashboard')
      return
    }

    // Check if route requires specific role
    if (to.meta.requiresRole) {
      const hasRequiredRole = authStore.hasAnyRole(to.meta.requiresRole)
      if (!hasRequiredRole) {
        next('/dashboard')
        return
      }
    }

    // Check if route requires specific permission
    if (to.meta.requiresPermission) {
      const hasRequiredPermission = authStore.hasPermission(to.meta.requiresPermission)
      if (!hasRequiredPermission) {
        next('/dashboard')
        return
      }
    }
  }

  next()
})

// Global error handler
router.onError((error) => {
  console.error('Router error:', error)
})

export default router