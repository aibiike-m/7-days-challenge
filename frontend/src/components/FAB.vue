<template>
  <button
    v-if="showFAB"
    class="fab"
    :class="{ 'fab-loading': loading }"
    @click="$emit('open-modal')"
    :disabled="loading"
    :title="$t('today.new_challenge')"
  >
    <span v-if="loading" class="loading-spinner">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path fill-rule="evenodd" d="M4.755 10.059a7.5 7.5 0 0 1 12.548-3.364l1.903 1.903h-3.183a.75.75 0 1 0 0 1.5h4.992a.75.75 0 0 0 .75-.75V4.356a.75.75 0 0 0-1.5 0v3.18l-1.9-1.9A9 9 0 0 0 3.306 9.67a.75.75 0 1 0 1.45.388Zm15.408 3.352a.75.75 0 0 0-.919.53 7.5 7.5 0 0 1-12.548 3.364l-1.902-1.903h3.183a.75.75 0 0 0 0-1.5H2.984a.75.75 0 0 0-.75.75v4.992a.75.75 0 0 0 1.5 0v-3.18l1.9 1.9a9 9 0 0 0 15.059-4.035.75.75 0 0 0-.53-.918Z" clip-rule="evenodd" />
      </svg>
    </span>
    
    <span v-else class="icon">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path fill-rule="evenodd" d="M12 3.75a.75.75 0 0 1 .75.75v6.75h6.75a.75.75 0 0 1 0 1.5h-6.75v6.75a.75.75 0 0 1-1.5 0v-6.75H4.5a.75.75 0 0 1 0-1.5h6.75V4.5a.75.75 0 0 1 .75-.75Z" clip-rule="evenodd" />
      </svg>
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  loading: Boolean
})

const route = useRoute()
const showFAB = computed(() => route.path === '/calendar')

defineEmits(['open-modal'])
</script>

<style scoped lang="scss">
.fab {
  position: fixed;
  bottom: calc(80px + $spacing-lg);
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

  .icon, .loading-spinner {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    svg {
      width: 100%;
      height: 100%;
    }
  }

  .loading-spinner {
    animation: spin 1s linear infinite;
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.8;
  }

  @include md {
    display: none;
  }
  &:hover {
    background: $primary-hover;
    transform: scale(1.05);
  }

  @include lg {
    right: calc((100vw - 1400px) / 2 + $spacing-lg);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>