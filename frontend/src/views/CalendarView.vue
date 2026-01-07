<template>
  <div class="calendar-view">
    <div class="calendar-layout">
      <div class="left-column">
        <div class="calendar-card card">
          <div class="calendar-header">
            <button class="btn-icon" @click="previousMonth">‹</button>
            <h3 class="month-title">{{ currentMonthName }}</h3>
            <button class="btn-icon" @click="nextMonth">›</button>
          </div>

          <div class="calendar-grid">
            <div class="weekday" v-for="(day, idx) in weekdays" :key="idx">{{ day }}</div>
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

        <div v-if="challengesForSelectedDate.length > 0" class="challenges-section">
          <div class="challenges-list">
            <div
              v-for="challenge in challengesForSelectedDate"
              :key="challenge.id"
              class="challenge-card card"
              @click="viewChallenge(challenge)"
            >
              <h4>{{ challenge.goal }}</h4>
              <div class="challenge-meta">
                <span class="challenge-duration">{{ challenge.duration_days }} {{ $t('calendar.day') }}</span>
                <span class="challenge-progress">{{ challenge.progress_percentage }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: challenge.progress_percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedDate" class="tasks-section right-column">
        <button 
          class="fab-desktop"
          @click="$emit('open-modal')"
          title="Создать челлендж"
        >
        {{ $t('today.new_challenge')}}
        </button>

        <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>

        <div v-else-if="selectedDayTasks.length === 0" class="empty-tasks">
          <p>{{ $t('today.noTasks') }}</p>
        </div>

        <div v-else class="tasks-list">
          <TaskCard
          v-for="task in selectedDayTasks"
          :key="task.id"
          :task="task"
          :challenge="getChallengeForTask(task)"
          @toggle="onTaskToggled"
          @notify="showToast"
          />
        </div>
        <transition name="toast">
          <div v-if="toast.message" class="toast-notification" :class="toast.type">
            {{ toast.message }}
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TaskCard from '@/components/TaskCard.vue'
import api from '@/services/api/index.js'
import { getTasksForDate, isSameDay } from '@/utils/taskHelpers'

const toast = ref({ message: '', type: 'info' })

function showToast({ message, type = 'info' }, duration = 4500) {
  toast.value = { message, type }

  setTimeout(() => {
    toast.value = { message: '', type: 'info' }
  }, duration)
}

const router = useRouter()
const i18n = useI18n()
const loading = ref(true)
const currentDate = ref(new Date())
const selectedDate = ref(null)
const allChallenges = ref([])
const allTasks = ref([])

defineEmits(['open-modal'])

const weekdaysRu = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const weekdaysEn = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const weekdays = computed(() => 
  i18n.locale.value === 'ru' ? weekdaysRu : weekdaysEn
)

const currentMonthName = computed(() => {
  const locale = i18n.locale.value === 'ru' ? 'ru-RU' : 'en-US'
  return currentDate.value.toLocaleDateString(locale, { month: 'long', year: 'numeric' })
})

const selectedDayTasks = computed(() => {
  if (!selectedDate.value) return []

  return allTasks.value.filter(task => {
    const challenge = allChallenges.value.find(c => c.id === task.challenge_id)
    if (!challenge) return false

    const taskDate = new Date(challenge.start_date)
    taskDate.setDate(taskDate.getDate() + (task.day_number - 1))

    return isSameDay(taskDate, selectedDate.value)
  })
})

const challengesForSelectedDate = computed(() => {
  if (!selectedDate.value || allTasks.value.length === 0) return []

  const taskChallengeIds = new Set(
    selectedDayTasks.value
      .map(task => task.challenge_id)
      .filter(Boolean)
  )

  return allChallenges.value.filter(challenge => 
    challenge.status === 'active' && taskChallengeIds.has(challenge.id)
  )
})

const todayTasks = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return getTasksForDate(allTasks.value, allChallenges.value, today)
})


function hasTasksOnDate(date) {
  return allTasks.value.some(task => {
    const challenge = allChallenges.value.find(c => c.id === task.challenge_id)
    if (!challenge) return false

    const taskDate = new Date(challenge.start_date)
    taskDate.setDate(taskDate.getDate() + (task.day_number - 1))
    return isSameDay(taskDate, date)
  })
}

const calendarDates = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  let startDay = firstDay.getDay()
  if (startDay === 0) startDay = 7
  startDay -= 1

  const dates = []

  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    dates.push({
      day: prevMonthLastDay - i,
      date: new Date(year, month - 1, prevMonthLastDay - i),
      isOtherMonth: true,
      key: `prev-${i}`
    })
  }

  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i)
    dates.push({
      day: i,
      date,
      isOtherMonth: false,
      isToday: isSameDay(date, new Date()),
      isSelected: selectedDate.value ? isSameDay(date, selectedDate.value) : isSameDay(date, new Date()),
      hasTasks: hasTasksOnDate(date),
      key: `current-${i}`
    })
  }

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

function selectDate(dateObj) {
  if (dateObj.isOtherMonth) return
  selectedDate.value = dateObj.date
}

function previousMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
}

function nextMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
}

function getChallengeForTask(task) {
  return allChallenges.value.find(c => c.id === task.challenge_id)
}

function onTaskToggled(task) {
  task.is_completed = !task.is_completed
}

async function loadChallenges() {
  try {
    const response = await api.get('challenges/', {
      params: { language: i18n.locale.value }
    })
    allChallenges.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Ошибка загрузки челленджей:', error)
    allChallenges.value = []
  }
}

async function loadAllTasks() {
  if (allChallenges.value.length === 0) {
    allTasks.value = []
    return
  }

  const challengeIds = allChallenges.value.map(c => c.id)
  try {
    const response = await api.get('tasks/', {
      params: {
        challenge_ids: challengeIds.join(','),
        language: i18n.locale.value
      }
    })
    const tasks = Array.isArray(response.data) ? response.data : response.data.results || []
    allTasks.value = tasks
  } catch (error) {
    console.error('Ошибка загрузки задач:', error)
    allTasks.value = []
  }
}

function viewChallenge(challenge) {
  router.push(`/challenge/${challenge.id}`)
}

onMounted(async () => {
  loading.value = true
  try {
    await loadChallenges()
    if (allChallenges.value.length > 0) {
      await loadAllTasks()
    }
  } catch (error) {
    console.error('Ошибка загрузки данных:', error)
  } finally {
    loading.value = false
    selectedDate.value = new Date()
  }
})
</script>

<style scoped lang="scss">
.calendar-view {
  width: 100%;
  padding: $spacing-sm;
  padding-bottom: 100px;
  position: relative;

  @media (min-width: 640px) {
    padding: $spacing-md;
  }

  @media (min-width: 1024px) {
    padding: $spacing-lg;
    max-width: 1400px;
    margin: 0 auto;
  }
}

.card {
  background: $white;
  border-radius: $radius-md;
  padding: $spacing-md;
  box-shadow: $shadow-sm;
  margin-bottom: $spacing-md;

  @media (min-width: 768px) {
    border-radius: $radius-lg;
    padding: $spacing-lg;
    margin-bottom: $spacing-lg;
  }
}
.toast-notification {
  position: fixed;
  bottom: 120px; 
  left: 50%;
  transform: translateX(-50%);
  min-width: 300px;
  max-width: 90%;
  padding: $spacing-lg $spacing-xl;
  border-radius: $radius-lg;
  box-shadow: $shadow-md;
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  text-align: center;
  z-index: 10000;
  color: white;
  background: rgba(30, 30, 30, 0.92); 
  backdrop-filter: blur(12px); 
  animation: toastSlideUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes toastSlideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

.toast-enter-active {
  transition: all 0.4s ease;
}
.toast-leave-active {
  transition: opacity 0.3s ease;
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(30px);
}
// ===== Calendar =====
.calendar-card {
  margin-bottom: $spacing-lg;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;

  @media (min-width: 768px) {
    margin-bottom: $spacing-lg;
  }
}

.month-title {
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  text-transform: capitalize;

  @media (min-width: 768px) {
    font-size: $font-size-lg;
  }
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: $radius-full;
  border: none;
  background: $bg-secondary;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  @media (min-width: 768px) {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  &:hover {
    background: $border-hover;
  }
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;

  @media (min-width: 768px) {
    gap: 4px;
  }
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: $radius-sm;
  font-size: $font-size-xs;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
  
  @media (min-width: 768px) {
    border-radius: $radius-md;
    font-size: $font-size-sm;
  }
  
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
    bottom: 30%;
    left: 50%;
    transform: translateX(-50%);
    width: 10px;
    height: 2px;
    border-radius: 1px;
    background: $primary;
  }
  
  &.selected.has-tasks::after {
    background: $white;
  }
}

// ===== Tasks =====
.tasks-section {
  min-height: 200px;
}

.loading {
  text-align: center;
  padding: $spacing-lg;
  color: $text-muted;
}

.empty-tasks {
  text-align: center;
  padding: $spacing-lg;
  color: $text-muted;
  background: $bg-primary;
  border-radius: $radius-md;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;

  @media (min-width: 768px) {
    gap: $spacing-sm;
  }
}

// ===== Challenges =====
.challenges-section {
  margin-top: $spacing-lg;
}

.challenges-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;

  @media (min-width: 768px) {
    gap: $spacing-lg;
  }
}

.challenge-card {
  cursor: pointer;
  transition: all 0.25s ease;
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }
  
  h4 {
    font-size: $font-size-sm;
    font-weight: $font-weight-semibold;
    margin-bottom: $spacing-sm;

    @media (min-width: 768px) {
      font-size: $font-size-base;
    }
  }
}

.challenge-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-sm;
  font-size: $font-size-xs;

  @media (min-width: 768px) {
    font-size: $font-size-sm;
  }
}

.challenge-duration {
  color: $text-secondary;
}

.challenge-progress {
  font-weight: $font-weight-semibold;
  color: $primary;
}

.progress-bar {
  height: 4px;
  background: $bg-secondary;
  border-radius: $radius-full;
  overflow: hidden;

  @media (min-width: 768px) {
    height: 6px;
  }
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $primary, $primary-light);
  transition: width 0.35s ease;
  border-radius: $radius-full;
}

.calendar-layout {
  display: flex;
  flex-direction: column;

  @media (min-width: 768px) {
    flex-direction: row;
    gap: $spacing-lg;

    .left-column {
      flex: 1;
    }

    .right-column {
      flex: 1.2;
    }
  }
}

// ===== FAB Desktop Button =====
.fab-desktop {
  display: none;
  width: fit-content;
  padding: $spacing-md $spacing-lg;
  background: $primary;
  color: $white;
  border: none;
  border-radius: $radius-md;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: $font-size-base;
  box-shadow: $shadow-md;
  margin-bottom: $spacing-lg;

  @media (min-width: 768px) {
    display: block;
  }

  &:hover {
    background: $primary-hover;
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }

  &:active {
    transform: translateY(0);
  }
}
</style>