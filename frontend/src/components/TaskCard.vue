<template>
  <div class="task-card" :class="{ completed: task.is_completed }">
    <div class="task-main" @click.stop="toggleDescription">
      <div class="custom-checkbox" @click.stop="toggleTask">
        <input
          type="checkbox"
          :checked="task.is_completed"
          @change="$emit('toggle', task)"
          class="hidden-checkbox"
        />
        <div class="checkbox-box">
          <svg v-if="task.is_completed" class="check-icon" viewBox="0 0 24 24">
            <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
        </div>
      </div>

      <h4 class="task-title">{{ task.title }}</h4>

      <svg
        class="arrow-icon"
        :class="{ open: showDescription }"
        viewBox="0 0 24 24"
        width="20"
        height="20"
      >
        <path fill="currentColor" d="M7 10l5 5 5-5z"/>
      </svg>
    </div>

    <div class="description-wrapper" :class="{ open: showDescription }">
      <div class="description-content">
        <p class="task-description">{{ task.description }}</p>
        <div class="task-meta">
          <span class="task-day">День {{ task.day_number }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['toggle'])

const showDescription = ref(false)

const toggleDescription = () => {
  showDescription.value = !showDescription.value
}

const toggleTask = () => {
  emit('toggle', props.task)
}
</script>

<style scoped lang="scss">
.task-card {
  background: $bg-card;
  border: 1px solid $border;
  border-radius: $radius-lg;
  overflow: hidden;
  transition: all 0.25s ease;

  &:hover {
    border-color: $primary-light;
    box-shadow: $shadow-sm;
  }

  &.completed {
    opacity: 0.7;

    .task-title {
      text-decoration: line-through;
      color: $text-muted;
    }
  }
}

.task-main {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-lg;
  cursor: pointer;
  user-select: none;
}

.hidden-checkbox {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.custom-checkbox {
  flex-shrink: 0;
  position: relative;
}

.checkbox-box {
  width: 24px;
  height: 24px;
  border: 2px solid $border;
  border-radius: $radius-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: $white;

  .hidden-checkbox:checked + & {
    background: $primary;
    border-color: $primary;
  }

  &:hover {
    border-color: $primary;
  }
}

.check-icon {
  width: 16px;
  height: 16px;
  color: white;
}

.task-title {
  flex: 1;
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  margin: 0;
  color: $text-primary;
  word-break: break-word;
}

.arrow-icon {
  flex-shrink: 0;
  color: $text-muted;
  transition: transform 0.25s ease;

  &.open {
    transform: rotate(180deg);
  }
}

.description-wrapper {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1);

  &.open {
    max-height: 300px; 
  }
}

.description-content {
  padding: 0 $spacing-lg $spacing-lg $spacing-lg;
  border-top: 1px solid $border;
  padding-top: $spacing-md;
}

.task-description {
  margin: 0 0 $spacing-sm 0;
  color: $text-secondary;
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: $font-size-sm;
}

.task-meta {
  margin-top: $spacing-sm;
}

.task-day {
  font-size: $font-size-xs;
  color: $text-muted;
  background: $bg-secondary;
  padding: 4px $spacing-sm;
  border-radius: $radius-sm;
}
</style>