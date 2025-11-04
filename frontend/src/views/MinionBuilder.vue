<template>
  <div class="minion-builder-view">
    <MinionBuilder :user-id="userId" />
  </div>
</template>

<script>
import MinionBuilder from '@/components/MinionBuilder.vue'

export default {
  name: 'MinionBuilderView',
  components: {
    MinionBuilder
  },
  data() {
    return {
      userId: 1
    }
  }
}
</script>

<style scoped>
.minion-builder-view {
  min-height: 100vh;
  /* background: #f5f5f5; */
}
</style>