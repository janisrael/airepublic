<template>
  <div class="spirit-marketplace-view">
    <SpiritMarketplace 
      :minion-id="selectedMinionId"
      :user-id="userId"
      @assign-spirit="handleSpiritAssignment"
      @spirit-assigned="handleSpiritAssigned"
      @show-message="showMessage"
    />
  </div>
</template>

<script>
import SpiritMarketplace from '@/components/SpiritMarketplace.vue'

export default {
  name: 'SpiritMarketplaceView',
  components: {
    SpiritMarketplace
  },
  data() {
    return {
      selectedMinionId: null,
      userId: 1
    }
  },
  methods: {
    handleSpiritAssignment(spirit) {
      console.log('Spirit assignment requested:', spirit)
      // Could open a minion selection modal here
    },
    
    handleSpiritAssigned(data) {
      console.log('Spirit assigned:', data)
      // Could show success notification
    },
    
    showMessage(message) {
      console.log('Message:', message)
      // Could show toast notification
    }
  }
}
</script>

<style scoped>
.spirit-marketplace-view {
  min-height: 100vh;
  /* background: #f5f5f5; */
}
</style>