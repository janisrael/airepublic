
<template>
  <div>
  <!-- Loading Overlay -->
  <div v-if="isLoading" class="loading-overlay">
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <p>Loading...</p>
    </div>
  </div>

  <div class="dashboard-layout">
    <!-- Mobile Menu Toggle -->
    <button 
      class="mobile-menu-toggle"
      @click="toggleMobileMenu"
      :aria-label="isMobileMenuOpen ? 'Close menu' : 'Open menu'"
    >
      <span class="material-icons-round">{{ isMobileMenuOpen ? 'close' : 'menu' }}</span>
    </button>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'mobile-visible': isMobileMenuOpen }">
      <!-- DEBUG: Auth state -->
      <!-- <div style="background: red; color: white; padding: 5px; font-size: 12px;">
        DEBUG: isAuthenticated={{ isAuthenticated }}, user={{ authStore.user?.username }}
        <button @click="testLogin" style="background: white; color: black; padding: 2px 5px; margin-left: 10px;">Test Login</button>
      </div> -->
      <div class="logo-container">
        <h2>AI Republic</h2>
        <p>Gotta Train ’Em All.</p>
      </div>
      
      <ul class="nav-menu">
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link" 
            :class="{ 'active': activeRoute === 'dashboard' }"
            @click.prevent="navigateTo('Dashboard')"
          >
            <span class="material-icons-round">dashboard</span>
            <span>Dashboard</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'models' }"
            @click.prevent="navigateTo('Models')"
          >
            <span class="material-icons-round">smart_toy</span>
            <span>Models</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'modelcomparison' }"
            @click.prevent="navigateTo('ModelComparison')"
          >
            <span class="material-icons-round">compare_arrows</span>
            <span>Compare</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'training' }"
            @click.prevent="navigateTo('Training')"
          >
            <span class="material-icons-round">model_training</span>
            <span>Training</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'traininghistory' }"
            @click.prevent="navigateTo('TrainingHistory')"
          >
            <span class="material-icons-round">history</span>
            <span>History</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'datasets' }"
            @click.prevent="navigateTo('Datasets')"
          >
            <span class="material-icons-round">dataset</span>
            <span>Datasets</span>
          </a>
        </li>
        <li v-if="authStore.hasAnyRole(['admin', 'superuser', 'developer'])" class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'basemodelproviders' }"
            @click.prevent="navigateTo('BaseModelProviders')"
          >
            <span class="material-icons-round">api</span>
            <span>Base Models</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'airoom' }"
            @click.prevent="navigateTo('AIRoom')"
          >
            <span class="material-icons-round">chat</span>
            <span>AI Room</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'evaluation' }"
            @click.prevent="navigateTo('Evaluation')"
          >
            <span class="material-icons-round">assessment</span>
            <span>Evaluation</span>
          </a>
        </li>
      </ul>
      
      <!-- Sidebar Footer with User Info -->
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            <span class="material-icons-round">account_circle</span>
          </div>
          <div class="user-details">
            <h4>{{ userDisplayName }}</h4>
            <p>{{ userRole }}</p>
          </div>
          <button 
            v-if="isAuthenticated"
            class="btn btn-sm btn-outline" 
            @click="handleLogout"
            title="Logout"
          >
            <span class="material-icons-round">logout</span>
          </button>
          <button 
            v-else
            class="btn btn-sm btn-outline" 
            @click="navigateTo('Login')"
            title="Login"
          >
            <span class="material-icons-round">login</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <router-view v-if="$route"></router-view>
      <div v-else>
        <h1>Welcome to AI Refinement Dashboard</h1>
        <p>Select an option from the sidebar to get started.</p>
      </div>
    </main>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const isMobileMenuOpen = ref(false);
const activeRoute = ref('dashboard');


// Computed properties for user info
const userDisplayName = computed(() => {

  if (authStore.user) {
    return authStore.user.first_name && authStore.user.last_name 
      ? `${authStore.user.first_name} ${authStore.user.last_name}`
      : authStore.user.username || 'User';
  } else {
  
    return 'Guest';
  }

});

const userRole = computed(() => {
  if (authStore.user) {
    return authStore.user.role_name || 'User';
  }
  return 'Guest';
});

const isAuthenticated = computed(() => !!authStore.user);
const isLoading = computed(() => authStore.loading);

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const navigateTo = (routeName) => {
  // Convert route name to lowercase to match our activeRoute values
  const normalizedRoute = routeName.toLowerCase();
  activeRoute.value = normalizedRoute;
  isMobileMenuOpen.value = false;
  
  // Use the route name directly since that's what's defined in the router
  router.push({ name: routeName }).catch(err => {
    // Ignore the vuex err regarding  navigating to the page they are already on.
    if (err.name !== 'NavigationDuplicated') {
      console.error('Navigation error:', err);
    }
  });
};

const handleLogout = async () => {
  try {
    await authStore.logout();
    router.push('/login');
  } catch (error) {
    console.error('Logout error:', error);
  }
};

const testLogin = async () => {
  try {
    console.log('Testing login...');
    const result = await authStore.login({ username: 'user', password: 'admin123' });
    console.log('Login result:', result);
  } catch (error) {
    console.error('Test login error:', error);
  }
};

// Set initial active route
const updateActiveRoute = () => {
  const route = router.currentRoute.value;
  if (route.name) {
    activeRoute.value = route.name.toLowerCase();
  }
};

// Call on initial load
updateActiveRoute();

// Watch for route changes
router.afterEach((to) => {
  if (to.name) {
    activeRoute.value = to.name.toLowerCase();
  }
});

onMounted(async () => {
  // Initialize auth store

  console.log('App.vue: Initializing auth store...');
  await authStore.initialize();
  console.log('App.vue: Auth store initialized. User:', authStore.user, 'isAuthenticated:', !!authStore.user);
  
  // Check if we're on mobile
  const checkIfMobile = () => {
    isMobileMenuOpen.value = window.innerWidth > 992;
  };
  
  checkIfMobile();
  window.addEventListener('resize', checkIfMobile);
  
  return () => {
    window.removeEventListener('resize', checkIfMobile);
  };
});
</script>

<style scoped>
  @import '@/assets/navigation.css';
</style>
