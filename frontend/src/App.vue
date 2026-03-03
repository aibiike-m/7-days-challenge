<template>
  <div class="app">
    <AppHeader v-if="showNavigation" />
    <main class="main-content" :class="{ 'no-nav': !showNavigation }">
      <router-view @open-modal="isCreateModalOpen = true" />
    </main>
    <BottomNav v-if="showNavigation" />

    <FAB v-if="showNavigation" @open-modal="isCreateModalOpen = true" />

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

const showNavigation = computed(() => {
  return route.meta.requiresAuth === true
})

const isCreateModalOpen = ref(false)

const onChallengeCreated = () => {
  isCreateModalOpen.value = false
}
</script>

<style lang="scss" scoped>
.app {
  min-height: 100vh;
}

.main-content {
  padding-bottom: 100px;

  @include md {
    padding-bottom: 60px;
  }

  &.no-nav {
    padding-bottom: 0;
  }
}
</style>