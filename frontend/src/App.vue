<template>
  <div class="app">
    <AppHeader v-if="!isAuthPage" />
    <main class="main-content">
      <router-view @open-modal="isCreateModalOpen = true" />
    </main>
    <BottomNav v-if="!isAuthPage" />

    <FAB v-if="!isAuthPage" @open-modal="isCreateModalOpen = true" />

    <CreateChallengeModal
      :is-open="isCreateModalOpen"
      @close="isCreateModalOpen = false"
      @created="onChallengeCreated"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import BottomNav from '@/components/BottomNav.vue'
import FAB from '@/components/FAB.vue'
import CreateChallengeModal from '@/components/CreateChallengeModal.vue'

const route = useRoute()
const isAuthPage = computed(() => route.path === '/auth')
const isCreateModalOpen = ref(false)

const onChallengeCreated = () => {
  isCreateModalOpen.value = false
  alert('Челлендж успешно создан!')
  window.location.reload()
}
</script>

<style scoped>
.app {
  min-height: 100vh;
}

.main-content {
  padding-bottom: 100px; 
}

@media (min-width: 768px) {
  .main-content {
    padding-bottom: 60px;
  }
}
</style>