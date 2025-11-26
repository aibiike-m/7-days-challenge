<template>
  <div class="calendar-view">
    <div class="header-section">
      <h2>Мои челленджи</h2>
      <p class="subtitle">Выберите день чтобы увидеть задачи</p>
    </div>

    <!-- Календарь -->
    <div class="calendar-card card">
      <div class="calendar-header">
        <button class="btn-icon" @click="previousMonth">‹</button>
        <h3 class="month-title">{{ currentMonthName }}</h3>
        <button class="btn-icon" @click="nextMonth">›</button>
      </div>

      <div class="calendar-grid">
        <div class="weekday" v-for="day in weekdays" :key="day">{{ day }}</div>
        <div
          v-for="date in calendarDates"
          :key="date.key"
          class="calendar-day"
          :class="{
            'other-month': date.isOtherMonth,
            'today': date.isToday,
            'selected': date.isSelected,
            'has-tasks': date.hasTasks
          }"
          @click="selectDate(date)"
        >
          {{ date.day }}
          <span v-if="date.hasTasks" class="task-indicator"></span>
        </div>
      </div>
    </div>

    <!-- Задачи выбранного дня -->
    <div v-if="selectedDate" class="tasks-section">
      <h3 class="section-title">
        Задачи на {{ formatSelectedDate }}
      </h3>

      <div v-if="loading" class="loading">Загрузка...</div>

      <div v-else-if="selectedDayTasks.length === 0" class="empty-tasks">
        <p>Нет задач на этот день</p>
      </div>

      <div v-else class="tasks-list">
        <TaskCard
          v-for="task in selectedDayTasks"
          :key="task.id"
          :task="task"
          @toggle="toggleTask"
        />
      </div>
    </div>

    <!-- Активные челленджи -->
    <div class="challenges-section">
      <h3 class="section-title">Активные челленджи</h3>
      
      <div v-if="activeChallenges.length === 0" class="empty-challenges">
        <span class="empty-icon">🎯</span>
        <p>У вас пока нет активных челленджей</p>
      </div>

      <div v-else class="challenges-list">
        <div
          v-for="challenge in activeChallenges"
          :key="challenge.id"
          class="challenge-card card"
          @click="viewChallenge(challenge)"
        >
          <h4>{{ challenge.goal }}</h4>
          <div class="challenge-meta">
            <span class="challenge-duration">{{ challenge.duration_days }} дней</span>
            <span class="challenge-progress">{{ challenge.progress_percentage }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: challenge.progress_percentage + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup>
import { ref, computed, onMounted} from 'vue'
import { useRouter } from 'vue-router'
import TaskCard from '@/components/TaskCard.vue'
import CreateChallengeModal from '@/components/CreateChallengeModal.vue'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const currentDate = ref(new Date())
const selectedDate = ref(null)
const activeChallenges = ref([])
const allTasks = ref([])

const weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const currentMonthName = computed(() => {
  return currentDate.value.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
})

const formatSelectedDate = computed(() => {
  if (!selectedDate.value) return ''
  return selectedDate.value.toLocaleDateString('ru-RU', { 
    day: 'numeric', 
    month: 'long',
    weekday: 'long'
  })
})

const calendarDates = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  
  let startDay = firstDay.getDay()
  if (startDay === 0) startDay = 7
  startDay -= 1
  
  const dates = []
  
  // Предыдущий месяц
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    dates.push({
      day: prevMonthLastDay - i,
      date: new Date(year, month - 1, prevMonthLastDay - i),
      isOtherMonth: true,
      key: `prev-${i}`
    })
  }
  
  // Текущий месяц
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i)
    dates.push({
      day: i,
      date: date,
      isOtherMonth: false,
      isToday: isSameDay(date, new Date()),
      isSelected: selectedDate.value ? isSameDay(date, selectedDate.value) : false,
      hasTasks: hasTasksOnDate(date),
      key: `current-${i}`
    })
  }
  
  // Следующий месяц
  const remainingDays = 42 - dates.length
  for (let i = 1; i <= remainingDays; i++) {
    dates.push({
      day: i,
      date: new Date(year, month + 1, i),
      isOtherMonth: true,
      key: `next-${i}`
    })
  }
  
  return dates
})

const selectedDayTasks = computed(() => {
  if (!selectedDate.value) return []
  return allTasks.value.filter(task => {
    return true
  })
})

function isSameDay(date1, date2) {
  return date1.getDate() === date2.getDate() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getFullYear() === date2.getFullYear()
}

function hasTasksOnDate(date) {
  return false
}

function selectDate(dateObj) {
  if (dateObj.isOtherMonth) return
  selectedDate.value = dateObj.date
  loadTasksForDate(dateObj.date)
}

function previousMonth() {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() - 1,
    1
  )
}

function nextMonth() {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() + 1,
    1
  )
}

async function loadActiveChallenges() {
  try {
    const response = await axios.get('/api/challenges/')
    activeChallenges.value = response.data.filter(c => c.status === 'active')
  } catch (error) {
    console.error('Error loading challenges:', error)
    activeChallenges.value = []
  }
}

async function loadTasksForDate(date) {
  loading.value = true
  try {
    allTasks.value = []
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

function viewChallenge(challenge) {
  console.log('View challenge:', challenge)
}

onMounted(() => {
  loadActiveChallenges()
})
</script>

<style scoped lang="scss">
// ;

.calendar-view {
  max-width: 700px;
  margin: 0 auto;
  padding: $spacing-lg;
  padding-bottom: 100px;
}

.header-section {
  margin-bottom: $spacing-xl;
  
  h2 {
    margin-bottom: $spacing-sm;
  }
}

.subtitle {
  color: $text-muted;
  font-size: $font-size-sm;
}

.card {
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  margin-bottom: $spacing-lg;
}

// ===== КАЛЕНДАРЬ =====
.calendar-card {
  margin-bottom: $spacing-xl;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.month-title {
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  text-transform: capitalize;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: $radius-full;
  border: none;
  background: $bg-secondary;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: $border-hover;
  }
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.weekday {
  text-align: center;
  font-size: $font-size-xs;
  font-weight: $font-weight-semibold;
  color: $text-muted;
  padding: $spacing-sm 0;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $radius-md;
  font-size: $font-size-sm;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
  
  &:hover {
    background: $bg-secondary;
  }
  
  &.other-month {
    color: $border-hover;
    cursor: default;
    
    &:hover {
      background: transparent;
    }
  }
  
  &.today {
    background: $bg-secondary;
    font-weight: $font-weight-semibold;
  }
  
  &.selected {
    background: $primary;
    color: $white;
    font-weight: $font-weight-semibold;
  }
  
  &.has-tasks::after {
    content: '';
    position: absolute;
    bottom: 4px;
    left: 50%;
    transform: translateX(-50%);
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: $primary;
  }
  
  &.selected.has-tasks::after {
    background: $white;
  }
}

// ===== ЗАДАЧИ =====
.tasks-section {
  margin-bottom: $spacing-xl;
}

.section-title {
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  color: $text-secondary;
  margin-bottom: $spacing-md;
}

.loading {
  text-align: center;
  padding: $spacing-xl;
  color: $text-muted;
}

.empty-tasks {
  text-align: center;
  padding: $spacing-xl;
  color: $text-muted;
  background: $bg-primary;
  border-radius: $radius-md;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

// ===== ЧЕЛЛЕНДЖИ =====
.challenges-section {
  margin-top: $spacing-xl;
}

.empty-challenges {
  text-align: center;
  padding: $spacing-xl;
  background: $bg-primary;
  border-radius: $radius-md;
  
  p {
    color: $text-muted;
  }
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: $spacing-md;
}

.challenges-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.challenge-card {
  cursor: pointer;
  transition: all 0.25s ease;
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }
  
  h4 {
    font-size: $font-size-base;
    font-weight: $font-weight-semibold;
    margin-bottom: $spacing-sm;
  }
}

.challenge-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-sm;
  font-size: $font-size-sm;
}

.challenge-duration {
  color: $text-secondary;
}

.challenge-progress {
  font-weight: $font-weight-semibold;
  color: $primary;
}

.progress-bar {
  height: 6px;
  background: $bg-secondary;
  border-radius: $radius-full;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $primary, $primary-light);
  transition: width 0.35s ease;
  border-radius: $radius-full;
}
</style>