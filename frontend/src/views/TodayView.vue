<template>
  <div class="today-view">
    <div class="header-section">
      <h2>Задачи на сегодня</h2>
      <p class="date">{{ currentDate }}</p>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="todayTasks.length === 0" class="empty-state">
      <span class="empty-icon">📝</span>
      <p>Нет задач на сегодня</p>
      <button class="btn btn-primary" @click="$router.push('/calendar')">
        Создать челлендж
      </button>
    </div>

    <div v-else class="tasks-container">
      <div class="tasks-section" v-if="activeTasks.length > 0">
        <h3 class="section-title">Осталось сделать ({{ activeTasks.length }})</h3>
        <TaskCard
          v-for="task in activeTasks"
          :key="task.id"
          :task="task"
          @toggle="toggleTask"
        />
      </div>

      <div class="tasks-section" v-if="completedTasks.length > 0">
        <h3 class="section-title completed-title">Выполнено ({{ completedTasks.length }})</h3>
        <TaskCard
          v-for="task in completedTasks"
          :key="task.id"
          :task="task"
          @toggle="toggleTask"
        />
      </div>

      <div class="progress-card card">
        <div class="progress-header">
          <span>Прогресс дня</span>
          <span class="progress-percent">{{ progressPercent }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TaskCard from '@/components/TaskCard.vue'
import axios from 'axios'

const loading = ref(true)
const todayTasks = ref([])

const currentDate = computed(() => {
  const date = new Date()
  return date.toLocaleDateString('ru-RU', { 
    weekday: 'long', 
    day: 'numeric', 
    month: 'long' 
  })
})

const activeTasks = computed(() => {
  return todayTasks.value.filter(t => !t.is_completed)
})

const completedTasks = computed(() => {
  return todayTasks.value.filter(t => t.is_completed)
})

const progressPercent = computed(() => {
  if (todayTasks.value.length === 0) return 0
  return Math.round((completedTasks.value.length / todayTasks.value.length) * 100)
})

async function loadTodayTasks() {
  try { 
    todayTasks.value = []
  } catch (error) {
    console.error('Error loading tasks:', error)
  } finally {
    loading.value = false
  }
}

async function toggleTask(task) {
  try {
    if (task.is_completed) {
      await axios.post(`/api/tasks/${task.id}/uncomplete/`)
    } else {
      await axios.post(`/api/tasks/${task.id}/complete/`)
    }
    task.is_completed = !task.is_completed
  } catch (error) {
    console.error('Error toggling task:', error)
  }
}

onMounted(() => {
  loadTodayTasks()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables';

.today-view {
  max-width: 600px;
  margin: 0 auto;
  padding: $spacing-lg;
  padding-bottom: 100px;
}

.header-section {
  margin-bottom: $spacing-xl;
  
  h2 {
    margin-bottom: $spacing-xl;
  }
  
  .date {
    color: $text-muted;
    font-size: $font-size-sm;
    text-transform: capitalize;
  }
}

.loading {
  text-align: center;
  padding: $spacing-xl;
  color: $text-muted;
}

.empty-state {
  text-align: center;
  padding: $spacing-xl;
  
  .empty-icon {
    font-size: 64px;
    display: block;
    margin-bottom: $spacing-lg;
  }
  
  p {
    color: $text-muted;
    margin-bottom: $spacing-lg;
  }
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
  color: $success;
}

.progress-card {
  margin-top: $spacing-lg;
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  
  .progress-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: $spacing-md;
    font-size: $font-size-sm;
    color: $text-secondary;
    
    .progress-percent {
      font-weight: $font-weight-semibold;
      color: $primary;
    }
  }
  
  .progress-bar {
    height: 8px;
    background: $bg-secondary;
    border-radius: $radius-full;
    overflow: hidden;
    
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, $primary, $primary-light);
      transition: width 0.35s ease;
      border-radius: $radius-full;
    }
  }
}
</style>