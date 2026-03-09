<template>
  <div class="today-view page-container">
    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>

    <div v-else-if="todayTasks.length === 0" class="empty-state">
      <span class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" d="M7.502 6h7.128A3.375 3.375 0 0 1 18 9.375v9.375a3 3 0 0 0 3-3V6.108c0-1.505-1.125-2.811-2.664-2.94a48.972 48.972 0 0 0-.673-.05A3 3 0 0 0 15 1.5h-1.5a3 3 0 0 0-2.663 1.618c-.225.015-.45.032-.673.05C8.662 3.295 7.554 4.542 7.502 6ZM13.5 3A1.5 1.5 0 0 0 12 4.5h4.5A1.5 1.5 0 0 0 15 3h-1.5Z" clip-rule="evenodd" />
          <path fill-rule="evenodd" d="M3 9.375C3 8.339 3.84 7.5 4.875 7.5h9.75c1.036 0 1.875.84 1.875 1.875v11.25c0 1.035-.84 1.875-1.875 1.875h-9.75A1.875 1.875 0 0 1 3 20.625V9.375Zm9.586 4.594a.75.75 0 0 0-1.172-.938l-2.476 3.096-.908-.907a.75.75 0 0 0-1.06 1.06l1.5 1.5a.75.75 0 0 0 1.116-.062l3-3.75Z" clip-rule="evenodd" />
        </svg>
      </span>
      <p>{{ $t('today.noTasks') }}</p>
    </div>

    <div v-else class="tasks-container">
      <div class="tasks-section" v-if="activeTasks.length > 0">
        <h3 class="section-title">{{ $t('today.remaining') }} {{ activeTasks.length }}</h3>
        <TaskCard
          v-for="task in activeTasks"
          :key="task.id"
          :task="task"
          :challenge="getChallengeForTask(task)"
          @toggle="onTaskToggled"
        />
      </div>

      <div class="tasks-section" v-if="completedTasks.length > 0">
        <h3 class="section-title completed-title">
          {{ $t('today.completed') }} {{ completedTasks.length }}
        </h3>
        <TaskCard
          v-for="task in completedTasks"
          :key="task.id"
          :task="task"
          :challenge="getChallengeForTask(task)"
          @toggle="onTaskToggled"  
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useNotification } from '@/composables/useNotification'
import { handleApiError } from '@/utils/errorHandler'
import TaskCard from '@/components/TaskCard.vue'
import api from '@/services/api/index.js'
import { getTasksForDate } from '@/utils/taskHelpers'

const { locale } = useI18n()
const notify = useNotification()

const loading = ref(true)
const allChallenges = ref([])
const allTasks = ref([])

const todayTasks = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return getTasksForDate(allTasks.value, allChallenges.value, today)
})

const activeTasks = computed(() => todayTasks.value.filter(t => !t.is_completed))
const completedTasks = computed(() => todayTasks.value.filter(t => t.is_completed))

onMounted(async () => {
  loading.value = true
  
  try {
    await loadChallenges()
    if (allChallenges.value.length > 0) {
      await loadTasks()
    }
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      console.error('Error loading data:', error)
    }
  } finally {
    loading.value = false
  }
})

async function loadChallenges() {
  try {
    const response = await api.get('challenges/', {
      params: { language: locale.value }
    })
    allChallenges.value = response.data.results || response.data || []
    
  } catch (error) {
    allChallenges.value = []
    handleApiError(error, notify)
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Error loading challenges:', error)
    }
  }
}

async function loadTasks() {
  if (allChallenges.value.length === 0) {
    allTasks.value = []
    return
  }

  const challengeIds = allChallenges.value.map(c => c.id)
  
  try {
    const response = await api.get('tasks/', {
      params: {
        challenge_ids: challengeIds.join(','),
        language: locale.value
      }
    })
    allTasks.value = Array.isArray(response.data) ? response.data : response.data.results || []
    
  } catch (error) {
    allTasks.value = []
    handleApiError(error, notify)
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Error loading tasks:', error)
    }
  }
}

function onTaskToggled(task) {
  task.is_completed = !task.is_completed
}

function getChallengeForTask(task) {
  return allChallenges.value.find(c => c.id === task.challenge_id)
}
</script>

<style scoped lang="scss">
.today-view {  
  max-width: 700px;
  padding-top: $spacing-responsive-md;
  padding-bottom: 100px;

  @include md {
    padding-top: $spacing-responsive-lg;
    padding-bottom: 120px;
  }

  @include xl {
    max-width: 800px;
  }
}

.loading,
.empty-state {
  text-align: center;
  color: $text-muted;
  padding: $spacing-responsive-lg;
  
  @include md {
    padding: $spacing-responsive-xl;
  }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: $spacing-responsive-md;
  display: block;
  
  @include md {
    font-size: 64px;
    margin-bottom: $spacing-responsive-lg;
  }
}
.empty-icon {
  margin-bottom: $spacing-responsive-md;
  display: flex;
  justify-content: center;
  color: $text-muted;

  svg {
    width: 64px;
    height: 64px;

    @include md {
      width: 80px;
      height: 80px;
    }
  }
  
  @include md {
    margin-top: $spacing-responsive-xl;
    margin-bottom: $spacing-responsive-lg;
  }
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: $spacing-responsive-lg;
  
  @include md {
    gap: $spacing-responsive-xl;
  }
}

.tasks-section {
  display: flex;
  flex-direction: column;
  gap: $spacing-responsive-sm;
  
  @include md {
    gap: $spacing-responsive-md;
  }
}

.section-title {
  font-size: $font-size-responsive-sm;
  font-weight: $font-weight-semibold;
  color: $text-secondary;
  margin-bottom: $spacing-responsive-sm;
  
  @include md {
    font-size: $font-size-responsive-base;
  }
}

.completed-title {
  color: $primary;
}
</style>