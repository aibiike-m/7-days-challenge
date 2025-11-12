<template>
  <div class="task-item" :class="{ completed: task.is_completed }">
    <label class="checkbox-container">
      <input
        type="checkbox"
        :checked="task.is_completed"
        @change="$emit('toggle', task.id)"
      />
      <span class="checkmark"></span>
    </label>

    <div class="task-content">
      <h3 class="task-title">{{ task.title }}</h3>
      <p class="task-description">{{ task.description }}</p>
      <span v-if="task.completed_at" class="completed-at">
        Выполнено: {{ formatDate(task.completed_at) }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps(['task'])
defineEmits(['toggle'])

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="scss">
@import "../styles/components/task-item.scss";
</style>