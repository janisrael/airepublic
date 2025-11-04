<template>
  <div class="timeline timeline-three px-3 px-sm-0">
    <div v-for="(item, idx) in items" :key="item.id || idx" class="row no-gutters align-items-center timeline-row">
      <!-- Left spacer or card depending on index -->
      <div v-if="isEven(idx)" class="col-sm"><!-- spacer --></div>

      <!-- Center avatar & middle line -->
      <div class="col-2 col-md-1 text-center flex-column d-none d-md-flex">
        <span class="m-3 avatar-separator shadow-inset rounded-circle">
          <img v-if="getAvatar(item)" :src="getAvatar(item)" class="img-fluid rounded-circle p-1 p-lg-2" :alt="getAvatarAlt(item)" />
          <span v-else class="material-icons-round avatar-icon">smart_toy</span>
        </span>
        <div class="row h-100"><div class="col middle-line">&nbsp;</div></div>
      </div>

      <!-- Profile card -->
      <div class="col-12 col-md py-2">
        <div class="profile-card">
          <div :class="['card shadow-soft border-light p-4', cardBgClass(item)]">
            <div class="card-body">
              <h3 class="h5 mb-2">{{ item.job_name || ('Job ' + (item.job_id || item.id || idx)) }}</h3>
              <span class="h6 font-weight-normal text-gray mb-3">{{ (item.training_type || 'RAG').toUpperCase() }}</span>
              <p class="card-text my-4">{{ item.description || item.summary?.training_type || 'Training session' }}</p>
              <ul class="list-unstyled d-flex mt-3 mb-4">
                <li class="mr-3"><span class="badge">XP: {{ item.xp_gained || item.summary?.xp_gained || 0 }}</span></li>
                <li class="mr-3"><span class="badge">Accuracy: {{ formatImprovement(item.improvements?.accuracy) }}</span></li>
                <li class="mr-3"><span class="badge">Knowledge: {{ formatImprovement(item.improvements?.knowledge) }}</span></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Right spacer when odd to balance -->
      <div v-if="!isEven(idx)" class="col-sm"><!-- spacer --></div>
    </div>
  </div>
</template>

<script>
import '@/assets/timeline-three.css'
export default {
  name: 'TimelineThree',
  props: {
    items: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    isEven(i) { return i % 2 === 0 },
    getAvatar(item) {
      // Prefer collection avatar or minion avatar if provided
      return item.avatar_url || item.minion_avatar || null
    },
    getAvatarAlt(item) { return item.job_name || 'Minion avatar' },
    cardBgClass(item) {
      return (item.status || '').toUpperCase() === 'COMPLETED' ? 'bg-primary' : 'bg-light'
    },
    formatImprovement(v) {
      if (!v) return '--'
      // v may be "+15.5%" or number
      return typeof v === 'string' ? v : (v > 0 ? `+${v}%` : `${v}%`)
    }
  }
}
</script>

<!-- Styles are centralized in assets/timeline-three.css -->


