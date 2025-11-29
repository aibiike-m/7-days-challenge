<template>
  <div class="today-view">
    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="todayTasks.length === 0" class="empty-state">
      <span class="empty-icon">Нет задач</span>
      <p>Нет задач на сегодня</p>
      <button class="btn btn-primary" @click="$router.push('/calendar')">
        Создать челлендж
      </button>
    </div>

    <div v-else class="tasks-container">
      <!-- Незавершённые задачи -->
      <div class="tasks-section" v-if="activeTasks.length > 0">
        <h3 class="section-title">Осталось сделать {{ activeTasks.length }}</h3>
        <TaskCard
          v-for="task in activeTasks"
          :key="task.id"
          :task="task"
          @toggle="toggleTask"
        />
      </div>

      <!-- Выполненные задачи -->
      <div class="tasks-section" v-if="completedTasks.length > 0">
        <h3 class="section-title completed-title">
          Выполнено {{ completedTasks.length }}
        </h3>
        <TaskCard
          v-for="task in completedTasks"
          :key="task.id"
          :task="task"
          @toggle="toggleTask"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TaskCard from '@/components/TaskCard.vue'
import api from '@/services/api/index.js'

const router = useRouter()
const loading = ref(true)
const allChallenges = ref([])
const allTasks = ref([])

const today = new Date()
today.setHours(0, 0, 0, 0)

const currentDate = computed(() => {
  return new Date().toLocaleDateString('ru-RU', {
    weekday: 'long',
    day: 'numeric',
    month: 'long'
  })
})

const todayTasks = computed(() => {
  return allTasks.value.filter(task => {
    const challenge = allChallenges.value.find(c => c.id === task.challenge_id)
    if (!challenge) return false

    const taskDate = new Date(challenge.start_date)
    taskDate.setDate(taskDate.getDate() + (task.day_number - 1))
    taskDate.setHours(0, 0, 0, 0)

    return taskDate.getTime() === today.getTime()
  })
})

const activeTasks = computed(() => todayTasks.value.filter(t => !t.is_completed))
const completedTasks = computed(() => todayTasks.value.filter(t => t.is_completed))

async function loadChallenges() {
  try {
    const response = await api.get('challenges/')
    allChallenges.value = response.data.results || []
  } catch (error) {
    console.error('Ошибка загрузки челленджей:', error)
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
      params: { challenge_ids: challengeIds.join(',') }
    })
    const tasks = Array.isArray(response.data) ? response.data : response.data.results || []
    allTasks.value = tasks.map(task => ({
      ...task,
      challenge_id: task.challenge_id
    }))
  } catch (error) {
    console.error('Ошибка загрузки задач:', error)
    allTasks.value = []
  }
}

async function toggleTask(task) {
  try {
    if (task.is_completed) {
      await api.post(`tasks/${task.id}/uncomplete/`)
    } else {
      await api.post(`tasks/${task.id}/complete/`)
    }
    task.is_completed = !task.is_completed
  } catch (error) {
    console.error('Ошибка переключения задачи:', error)
  }
}

onMounted(async () => {
  loading.value = true
  await loadChallenges()
  await loadTasks()
  loading.value = false
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

.header-section {
  margin-bottom: $spacing-xl;
  text-align: center;

  h2 {
    margin-bottom: $spacing-sm;
  }

  .date {
    color: $text-muted;
    font-size: $font-size-lg;
    text-transform: capitalize;
  }
}

.loading, .empty-state {
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
  font-weight: $font-weight-semibold;
  color: $text-secondary;
  margin-bottom: $spacing-sm;
}

.completed-title {
  color: $primary;
}

.btn-primary {
  margin-top: $spacing-lg;
}
</style>