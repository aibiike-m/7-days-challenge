<template>
  <button
    v-if="showFAB"
    class="fab"
    @click="$emit('open-modal')"
    :title="$t('today.new_challenge')"
  >
    <span class="icon">+</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

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

  .icon {
    font-size: 28px;
    line-height: 1;
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
</style>