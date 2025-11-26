<template>
  <div class="challenge">
    <header class="header">
      <router-link to="/" class="back-btn">На главную</router-link>
      <h1 class="goal">{{ challenge.goal }}</h1>
      <div class="progress-container">
        <div class="progress-bar" :style="{ width: challenge.progress_percentage + '%' }"></div>
        <span class="progress-text">{{ challenge.progress_percentage }}%</span>
      </div>
    </header>

    <div class="calendar">
      <button
        v-for="day in 7"
        :key="day"
        @click="selectedDay = day"
        :class="{ 
          active: selectedDay === day, 
          completed: isDayCompleted(day),
          current: day === challenge.current_day && day !== selectedDay
        }"
        class="day-btn"
      >
        <span class="day-number">День {{ day }}</span>
        <span v-if="isDayCompleted(day)" class="check-icon">✓</span>
      </button>
    </div>

    <div class="tasks">
      <TaskItem
        v-for="task in tasksForSelectedDay"
        :key="task.id"
        :task="task"
        :disabled="selectedDay !== challenge.current_day"
        @toggle="toggleTask"
      />
      
      <div v-if="tasksForSelectedDay.length === 0" class="empty-day">
        <p>На этот день задач нет</p>
      </div>
    </div>

    <transition name="fade">
      <div v-if="challenge.progress_percentage === 100" class="celebration">
        <div class="confetti"></div>
        <h2>Поздравляю! Ты выполнил челлендж!</h2>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import TaskItem from '../components/TaskItem.vue'

const route = useRoute()
const challenge = ref({})
const selectedDay = ref(1)
const API_URL = 'http://127.0.0.1:8000/api'
const isToday = computed(() => selectedDay.value === challenge.value.current_day)

async function loadChallenge() {
  try {
    const res = await axios.get(`${API_URL}/challenges/${route.params.id}/`)
    challenge.value = res.data
    const today = new Date().getDate()
    const start = new Date(challenge.value.start_date)
    const currentDay = Math.min(Math.max(1, today - start.getDate() + 1), 7)
    selectedDay.value = currentDay
  } catch (err) {
    alert('Не удалось загрузить челлендж')
  }
}

const tasksForSelectedDay = computed(() => {
  return challenge.value.tasks?.filter(t => t.day_number === selectedDay.value) || []
})

function isDayCompleted(day) {
  const dayTasks = challenge.value.tasks?.filter(t => t.day_number === day) || []
  return dayTasks.length > 0 && dayTasks.every(t => t.is_completed)
}

async function toggleTask(taskId) {
  const task = challenge.value.tasks.find(t => t.id === taskId)
  const action = task.is_completed ? 'uncomplete' : 'complete'
  
  try {
    await axios.post(`${API_URL}/tasks/${taskId}/${action}/`)
    await loadChallenge() 
  } catch (err) {
    alert('Ошибка при обновлении задачи')
  }
}

onMounted(loadChallenge)
</script>

<style scoped lang="scss">

</style>