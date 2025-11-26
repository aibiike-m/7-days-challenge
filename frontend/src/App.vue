<template>
  <div class="app">
    <AppHeader v-if="!isAuthPage" />
    <main class="main-content">
      <router-view />
    </main>
    <BottomNav v-if="!isAuthPage" />
    <FAB v-if="!isAuthPage" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import BottomNav from '@/components/BottomNav.vue'
import FAB from '@/components/FAB.vue'

const route = useRoute()
const isAuthPage = computed(() => route.path === '/auth')
</script>

<style>
.app {
  min-height: 100vh;
}

.main-content {
  min-height: calc(100vh - 70px); 
}

@media (min-width: 768px) {
  .main-content {
    min-height: calc(100vh - 60px); 
  }
}
</style>
