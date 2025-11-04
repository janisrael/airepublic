<template>
  <div>
    <MinionTrainingHistory :minion-id="minionId" />
  </div>
</template>

<script>
import MinionTrainingHistory from '@/components/MinionTrainingHistory.vue'

export default {
  name: 'MinionHistoryPage',
  components: { MinionTrainingHistory },
  props: {},
  computed: {
    minionId() {
      return this.$route.params.id
    }
  }
}
</script>

<style scoped>
/* Page-level styles can be added here if needed */
</style>


