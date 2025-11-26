<template>
  <button 
    v-if="showFAB" 
    class="fab" 
    @click="createChallenge"
    title="Создать челлендж"
  >
    <span class="icon">+</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const emit = defineEmits(['click'])

const showFAB = computed(() => route.path === '/calendar')

const createChallenge = () => {
  emit('click') 
}
</script>


<style scoped lang="scss">
.fab {
  position: fixed;
  bottom: calc(70px + $spacing-lg);
  right: $spacing-lg;
  width: 56px;
  height: 56px;
  border-radius: $radius-full;
  background: $primary;
  color: $white;
  border: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  z-index: 90;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
}

.fab .icon {
  font-size: 28px;
  font-weight: 400;
  line-height: 1;
}

.fab:hover {
  background: $primary-hover;
  transform: scale(1.05);
  box-shadow: 0 8px 32px rgba(91, 159, 216, 0.3);
}

.fab:active {
  transform: scale(0.95);
}

@media (min-width: 1024px) {
  .fab {
    right: calc((100vw - 480px) / 2 + $spacing-lg);
  }
}
</style>