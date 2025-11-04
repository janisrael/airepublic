<template>
  <div>
    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <Loader />
    </div>

    <div v-if="isloggedin" class="dashboard-layout" >
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
              :class="{ 'active': activeRoute === 'minionbuilder' }"
              @click.prevent="navigateTo('MinionBuilder')"
            >
              <span class="material-icons-round">smart_toy</span>
              <span>Minions</span>
            </a>
          </li>
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ 'active': activeRoute === 'spiritmarketplace' }"
              @click.prevent="navigateTo('SpiritMarketplace')"
            >
              <span class="material-icons-round">psychology</span>
              <span>Spirits</span>
            </a>
          </li>
          <!-- Models menu hidden -->
          <li v-if="false" class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ 'active': activeRoute === 'models' }"
              @click.prevent="navigateTo('Models')"
            >
              <span class="material-icons-round">storage</span>
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
          <h1>Welcome to AI Republic Dashboard</h1>
          <p>Select an option from the sidebar to get started.</p>
        </div>
      </main>
    </div>
    <div v-else >
      <Login @changelogin="handleLoginChange"/>
    </div>
  </div>
</template>

<script>
import { mapState } from 'pinia';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Login from './views/Login.vue';
import Loader from './components/Loader.vue';

export default {
  name: 'DashboardLayout',
  components: {
    Login,
    Loader,
  },
  data() {
    return {
      isMobileMenuOpen: false,
      activeRoute: 'dashboard',
      isloggedin: false,
    };
  },
  computed: {
    ...mapState(useAuthStore, ['user', 'loading']),
    
    authStore() {
   
      return useAuthStore();
    },
    isAuthenticated() {

      return !!this.authStore.user;
    },
    isLoading() {
      return this.authStore.loading;
    },
    userDisplayName() {
      if (this.authStore.user) {
        this.isloggedin = true;
        return this.authStore.user.first_name && this.authStore.user.last_name 
          ? `${this.authStore.user.first_name} ${this.authStore.user.last_name}`
          : this.authStore.user.username || 'User';
      } else {
        this.isloggedin = false
        return 'Guest';
      }
      
    },
    userRole() {
      return this.authStore.user ? this.authStore.user.role_name || 'User' : 'Guest';
    },
  },
  methods: {
    handleLoginChange(value) {
      this.isloggedin = value;
    },
    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen;
    },
    navigateTo(routeName) {
      const normalizedRoute = routeName.toLowerCase();
      this.activeRoute = normalizedRoute;
      this.isMobileMenuOpen = false;

      this.$router.push({ name: routeName }).catch(err => {
        if (err.name !== 'NavigationDuplicated') {
          console.error('Navigation error:', err);
        }
      });
    },
    async handleLogout() {
      try {
        await this.authStore.logout();
        this.$router.push('/login');
      } catch (error) {
        console.error('Logout error:', error);
      }
    },
    async testLogin() {
      try {
        console.log('Testing login...');
        const result = await this.authStore.login({ username: 'user', password: 'admin123' });
        console.log('Login result:', result);
      } catch (error) {
        console.error('Test login error:', error);
      }
    },
    updateActiveRoute() {
      const route = this.$router.currentRoute.value;
      if (route.name) {
        this.activeRoute = route.name.toLowerCase();
      }
    },
    checkIfMobile() {
      this.isMobileMenuOpen = window.innerWidth > 992;
    }
  },
  async mounted() {
    // Initialize auth store
    // console.log('DashboardLayout: Initializing auth store...');
    // this.authStore.initialize().then(() => {
    //   console.log('Auth store initialized. User:', this.authStore.user, 'isAuthenticated:', !!this.authStore.user);
    // });

    await this.authStore.initialize();

    if (this.authStore.user) {
      this.isloggedin = true;
      // Optional: redirect if already logged in
      this.$router.replace({ name: 'Dashboard' });
    } else {
      this.isloggedin = false;
    }

    // Initial active route
    this.updateActiveRoute();

    // Listen for route changes
    this.$router.afterEach((to) => {
      if (to.name) {
        this.activeRoute = to.name.toLowerCase();
      }
    });

    // Responsive check
    this.checkIfMobile();
    window.addEventListener('resize', this.checkIfMobile);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkIfMobile);
  },
};
</script>

<style scoped>
@import '@/assets/navigation.css';
</style>
