<template>
  <div class="task-card" :class="{ completed: task.is_completed, locked: isTaskLocked }">
    <div class="task-main" @click.stop="toggleDescription">
      <div class="custom-checkbox" @click.stop="handleCheckboxClick">
        <input
          type="checkbox"
          :checked="task.is_completed"
          :disabled="isTaskLocked || isLoading"
          class="hidden-checkbox"
          :aria-label="$t('task.toggle_complete', { title: task.title })"
        />
        <div class="checkbox-box" :class="{ loading: isLoading }">
          <svg v-if="isLoading" class="spinner-icon" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/>
            <path d="M12 2 A10 10 0 0 1 22 12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
          </svg>
          <svg v-else-if="task.is_completed" class="check-icon" viewBox="0 0 24 24">
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
        :aria-label="showDescription ? $t('task.hide_description') : $t('task.show_description')"
      >
        <path fill="currentColor" d="M7 10l5 5 5-5z"/>
      </svg>
    </div>

    <div class="description-wrapper" :class="{ open: showDescription }">
      <div class="description-content">
        <p class="task-description">{{ task.description }}</p>
        <div class="task-meta">
          <span class="task-day">{{ $t('challenge.day') }} {{ task.day_number }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useNotification } from '@/composables/useNotification'
import { handleApiError } from '@/utils/errorHandler'
import api from '@/services/api/index.js'

const props = defineProps({
  task: { type: Object, required: true },
  challenge: { type: Object, required: true }
})

const emit = defineEmits(['toggle'])

const { locale } = useI18n()
const notify = useNotification()
const showDescription = ref(false)
const isLoading = ref(false)

const toggleDescription = () => {
  showDescription.value = !showDescription.value
}

const taskDate = computed(() => {
  const start = new Date(props.challenge.start_date + 'T00:00:00Z') 
  start.setUTCDate(start.getUTCDate() + props.task.day_number - 1)
  return new Date(start.getUTCFullYear(), start.getUTCMonth(), start.getUTCDate())  
})

const today = computed(() => {
  const d = new Date()
  return new Date(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate())  
})

const isTaskLocked = computed(() => {
  return taskDate.value > today.value
})

async function handleCheckboxClick() {
  if (isTaskLocked.value || isLoading.value) {
    if (isTaskLocked.value) {
      notify.warning('errors.future_task')
    }
    return
  }

  isLoading.value = true
  const previousState = props.task.is_completed
  
  emit('toggle', props.task)

  try {
    const endpoint = previousState ? 'uncomplete' : 'complete'
    await api.post(`tasks/${props.task.id}/${endpoint}/`, {}, {
      params: { language: locale.value }
    })
    
    
  } catch (error) {
  emit('toggle', props.task)
  
  handleApiError(error, notify, {
    403: () => notify.error('errors.future_task')
  })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.task-card {
  background: $bg-card;
  border: 1px solid $border;
  border-left: 4px solid v-bind('props.challenge.color');
  border-radius: $radius-lg;
  overflow: hidden;
  transition: all 0.25s ease;

  @include md {
    &:hover {
      border-color: $primary-light;
      box-shadow: $shadow-sm;
    }
  }

  &.completed {
    opacity: 0.7;
    .task-title {
      text-decoration: line-through;
      color: $text-muted;
    }
  }

  &.locked {
    .checkbox-box:hover { border-color: $border; }
    .custom-checkbox { cursor: pointer; }
  }
}

.task-main {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-sm;
  cursor: pointer;
  user-select: none;

  @include md {
    padding: $spacing-lg;
  }
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
    background: v-bind('props.challenge.color');
    border-color: v-bind('props.challenge.color');
  }

  @include md {
    &:hover {
      border-color: v-bind('props.challenge.color');
    }
  }
}

.hidden-checkbox {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.check-icon {
  width: 16px;
  height: 16px;
  color: white;
}

.task-title {
  flex: 1;
  font-size: $font-size-responsive-base;
  font-weight: $font-weight-semibold;
  margin: 0;
  color: $text-primary;
  word-break: break-word;
}

.arrow-icon {
  flex-shrink: 0;
  color: $text-muted;
  transition: transform 0.25s ease;
  &.open { transform: rotate(180deg); }
}

.description-wrapper {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  &.open { max-height: 300px; }
}

.description-content {
  padding: 0 $spacing-lg $spacing-lg;
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

.task-day {
  font-size: $font-size-xs;
  color: white;
  background: v-bind('props.challenge.color');
  padding: 4px $spacing-sm;
  border-radius: $radius-sm;
}
.spinner-icon {
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  
  &.loading {
    border-color: $primary;
    cursor: wait;
  }

  .hidden-checkbox:checked + & {
    background: v-bind('props.challenge.color');
    border-color: v-bind('props.challenge.color');
  }

  @include md {
    &:hover:not(.loading) {
      border-color: v-bind('props.challenge.color');
    }
  }
}
</style>