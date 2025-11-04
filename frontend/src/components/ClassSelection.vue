<template>
  <div class="class-selection">
    <!-- Header -->
    <div class="class-selection-header">
      <h3 class="class-selection-title">
        <span class="material-icons class-icon">psychology</span>
        Choose Your Minion Class
      </h3>
    </div>

    <!-- Category Filters -->
    <div class="class-filters" v-if="categories.length > 0">
      <button
        v-for="category in categories"
        :key="category"
        :class="['filter-btn', { active: selectedCategory === category }]"
        @click="filterByCategory(category)"
      >
        {{ category }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading available classes...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <span class="material-icons error-icon">error</span>
      <p>{{ error }}</p>
      <button @click="loadClasses" class="retry-btn">Try Again</button>
    </div>

    <!-- Class Grid -->
    <div v-else class="class-grid">
      <ClassCard
        v-for="classDef in filteredClasses"
        :key="classDef.class_name"
        :class-def="classDef"
        :can-unlock="classDef.can_unlock"
        :is-selected="selectedClass && selectedClass.class_name === classDef.class_name"
        @select="selectClass"
        @view-details="showClassDetails"
      />
    </div>

    <!-- Class Details Modal -->
    <ClassDetailsModal
      v-if="showDetails"
      :class-def="selectedClassForModal"
      :user-rank="userRank"
      :user-level="userLevel"
      @close="closeDetails"
      @use-class="useClass"
    />

    <!-- No Classes Found -->
    <div v-if="!loading && !error && filteredClasses.length === 0" class="no-classes">
      <span class="material-icons no-classes-icon">search_off</span>
      <p>No classes found for your current rank and level.</p>
      <p class="no-classes-hint">Try selecting a different category or level up to unlock more classes.</p>
    </div>
  </div>
</template>

<script>
import ClassCard from './ClassCard.vue'
import ClassDetailsModal from './ClassDetailsModal.vue'
import classService from '@/services/classService'

export default {
  name: 'ClassSelection',
  components: {
    ClassCard,
    ClassDetailsModal
  },
  props: {
    userRank: {
      type: String,
      default: 'Novice'
    },
    userLevel: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      classes: [],
      categories: [],
      loading: false,
      error: null,
      selectedCategory: 'All',
      selectedClass: null,
      showDetails: false,
      selectedClassForModal: null
    }
  },
  computed: {
    filteredClasses() {
      if (this.selectedCategory === 'All') {
        return this.classes
      }
      return this.classes.filter(classDef => classDef.category === this.selectedCategory)
    }
  },
  async mounted() {
    await this.loadClasses()
  },
  methods: {
    async loadClasses() {
      this.loading = true
      this.error = null
      
      try {
        // Load classes and categories in parallel
        const [classes, categories] = await Promise.all([
          classService.getAvailableClasses(this.userRank, this.userLevel),
          classService.getClassCategories()
        ])
        
        this.classes = classes
        this.categories = ['All', ...Object.keys(categories)]
        
        console.log(`Loaded ${classes.length} classes for ${this.userRank} Level ${this.userLevel}`)
      } catch (error) {
        console.error('Error loading classes:', error)
        this.error = error.message || 'Failed to load classes'
      } finally {
        this.loading = false
      }
    },

    filterByCategory(category) {
      this.selectedCategory = category
    },

    selectClass(classDef) {
      console.log('ClassSelection: Selecting class:', classDef)
      this.selectedClass = classDef
      console.log('ClassSelection: Emitting class-selected event:', classDef)
      this.$emit('class-selected', classDef)
    },

    showClassDetails(classDef) {
      this.selectedClassForModal = classDef
      this.showDetails = true
    },

    closeDetails() {
      this.showDetails = false
      this.selectedClassForModal = null
    },

    useClass(classDef) {
      this.closeDetails()
      this.selectClass(classDef)
    }
  }
}
</script>

<style scoped>
.class-selection {
  padding: 0;
  max-width: 100%;
  margin: 0;
}

.class-selection-header {
  text-align: left;
  margin-bottom: 1rem;
}

.class-selection-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.class-icon {
  font-size: 1.5rem;
  color: var(--primary);
}

.class-filters {
  display: flex;
  justify-content: flex-start;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filter-btn {
    padding: 5px 10px;
    border: 2px solid var(--border-color);
    background: var(--card-bg);
    color: var(--text-color);
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
    background-color: #4e73df17;
    border: 2px solid #4e73df59;
    font-size: 12px;
}

.filter-btn:hover {
  border-color: var(--primary);
  background: var(--primary-light);
}

.filter-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.class-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.loading-state,
.error-state,
.no-classes {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.no-classes-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--error);
}

.no-classes-icon {
  color: var(--secondary);
}

.retry-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 1rem;
  transition: background 0.3s ease;
}

.retry-btn:hover {
  background: var(--primary-dark);
}

.no-classes-hint {
  color: var(--secondary);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .class-selection {
    padding: 1rem;
  }
  
  .class-selection-title {
    font-size: 1.5rem;
  }
  
  .class-icon {
    font-size: 2rem;
  }
  
  .class-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .class-filters {
    gap: 0.25rem;
  }
  
  .filter-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
}
</style>
