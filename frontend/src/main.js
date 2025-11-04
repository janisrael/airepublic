import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
// import './assets/models.css';
import './assets/main.css';
import { iconCSS } from '@/utils/icons'
// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Toast Service
import '@/utils/toast';

// Import PrimeVue
import PrimeVue from 'primevue/config';
import Timeline from 'primevue/timeline';

const app = createApp(App);
const pinia = createPinia();
// Add the CSS to your app
const style = document.createElement('style')
style.textContent = iconCSS
document.head.appendChild(style)
// Register PrimeVue
app.use(PrimeVue);
app.component('Timeline', Timeline);

app.use(pinia);
app.use(router);

// Add global error handler
app.config.errorHandler = (err) => {
  console.error('Vue error:', err);
};

// Mount the app
app.mount('#app');
