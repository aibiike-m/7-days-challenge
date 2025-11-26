<template>
  <div class="task-card" :class="{ completed: task.is_completed }">
    <div class="task-checkbox" @click="toggleTask">
      <div class="checkbox" :class="{ checked: task.is_completed }"></div>
    </div>
    
    <div class="task-content">
      <h3 class="task-title">{{ task.title }}</h3>
      <p class="task-description">{{ task.description }}</p>
      <div class="task-meta">
        <span class="task-day">День {{ task.day_number }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['toggle'])

const toggleTask = () => {
  emit('toggle', props.task)
}
</script>

<style scoped lang="scss">
.task-card {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-lg;
  background: $bg-card;
  border-radius: $radius-lg;
  border: 1px solid $border;
  transition: all 0.25s ease;
  cursor: pointer;
}

.task-card:hover {
  border-color: $primary-light;
  box-shadow: $shadow-sm;
}

.task-card.completed {
  opacity: 0.6;
}

.task-card.completed .task-title {
  text-decoration: line-through;
  color: $text-muted;
}

.task-card.completed .task-description {
  color: $text-muted;
}

.task-checkbox {
  flex-shrink: 0;
  padding-top: 2px;
}

.checkbox {
  width: 24px;
  height: 24px;
  border: 2px solid $border;
  border-radius: $radius-sm;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
}

.checkbox:hover {
  border-color: $primary;
}

.checkbox.checked {
  background: $primary;
  border-color: $primary;
}

.checkbox.checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: $white;
  font-size: 14px;
  font-weight: $font-weight-bold;
}

.task-content {
  flex: 1;
}

.task-title {
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  color: $text-primary;
  margin-bottom: 0.25rem;
}

.task-description {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.5;
  margin-bottom: $spacing-sm;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-meta {
  display: flex;
  gap: $spacing-sm;
  align-items: center;
}

.task-day {
  font-size: $font-size-xs;
  color: $text-muted;
  background: $bg-secondary;
  padding: 2px $spacing-sm;
  border-radius: $radius-sm;
}
</style>