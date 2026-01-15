<template>
  <div class="today-view">
    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>

    <div v-else-if="todayTasks.length === 0" class="empty-state">
      <span class="empty-icon">📝</span>
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

function onTaskToggled(task) {
  task.is_completed = !task.is_completed
}

function getChallengeForTask(task) {
  return allChallenges.value.find(c => c.id === task.challenge_id)
}

async function loadChallenges() {
  try {
    const response = await api.get('challenges/', {
      params: { language: locale.value }
    })
    allChallenges.value = response.data.results || response.data || []
    
  } catch (error) {
    if (!error.response) {
      notify.error('errors.network')
    } else {
      notify.error('errors.server')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Error loading challenges:', error)
    }
    
    allChallenges.value = []
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
    const tasks = Array.isArray(response.data) ? response.data : response.data.results || []
    allTasks.value = tasks
    
  } catch (error) {
    if (!error.response) {
      notify.error('errors.network')
    } else {
      notify.error('errors.server')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Error loading tasks:', error)
    }
    
    allTasks.value = []
  }
}

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
</script>

<style scoped lang="scss">
.today-view {
  max-width: 700px;
  margin: 0 auto;
  padding: $spacing-lg;
  padding-bottom: 120px;

  @media (min-width: 768px) {
    padding-left: $spacing-xl;
    padding-right: $spacing-xl;
  }

  @media (min-width: 1440px) {
    max-width: 800px;
  }
}

.loading,
.empty-state {
  text-align: center;
  padding: $spacing-xl;
  color: $text-muted;
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: $spacing-lg;
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.tasks-section {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.section-title {
  font-size: $font-size-base;
  font-weight: 600;
  color: $text-secondary;
  margin-bottom: $spacing-sm;
}

.completed-title {
  color: $primary;
}
</style>