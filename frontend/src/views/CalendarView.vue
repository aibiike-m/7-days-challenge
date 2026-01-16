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

          <div class="calendar-overflow-container">
            <transition name="calendar-fade" mode="out-in">
              <div class="calendar-grid" :key="currentMonthName">
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
            </transition>
          </div>
        </div>

        <!-- Challenges Section with Selection Mode -->
        <div v-if="challengesForSelectedDate.length > 0" class="challenges-section">
          <div class="selection-controls">
            <button 
              v-if="!isSelectionMode" 
              class="control-btn btn-manage"
              @click="toggleSelectionMode"
            >
              {{ $t('calendar.manage_challenges') }}
            </button>
            
            <template v-else>
              <button 
                class="control-btn btn-select-all"
                @click="toggleSelectAll"
              >
                {{ allSelected ? $t('calendar.deselect_all') : $t('calendar.select_all') }}
              </button>
              <button 
                class="control-btn btn-delete"
                @click="openDeleteModal"
                :disabled="selectedChallengeIds.length === 0"
              >
                {{ $t('calendar.delete_selected', { count: selectedChallengeIds.length }) }}
              </button>
              <button 
                class="control-btn btn-cancel"
                @click="cancelSelection"
              >
                {{ $t('common.cancel') }}
              </button>
            </template>
          </div>

          <div class="challenges-list">
            <div
              v-for="challenge in challengesForSelectedDate"
              :key="challenge.id"
              class="challenge-card card"
              :class="{ 
                'selection-mode': isSelectionMode,
                'selected': selectedChallengeIds.includes(challenge.id)
              }"
              :style="{ borderLeftColor: challenge.color, borderLeftWidth: '4px' }"
              @click="handleChallengeClick(challenge)"
            >
              <!-- Checkbox in Selection Mode -->
              <div v-if="isSelectionMode" class="challenge-checkbox" @click.stop="toggleChallengeSelection(challenge.id)">
                <input
                  type="checkbox"
                  :checked="selectedChallengeIds.includes(challenge.id)"
                  class="hidden-checkbox"
                />
                <div class="checkbox-box">
                  <svg v-if="selectedChallengeIds.includes(challenge.id)" class="check-icon" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                  </svg>
                </div>
              </div>

              <div class="challenge-content">
                <h4>{{ challenge.goal }}</h4>
                <div class="challenge-meta">
                  <span class="challenge-duration">{{ challenge.duration_days }} {{ $t('calendar.day') }}</span>
                  <span class="challenge-progress" :style="{ color: challenge.color }">
                    {{ challenge.progress_percentage }}%
                  </span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ 
                      width: challenge.progress_percentage + '%',
                      background: challenge.color 
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedDate" class="tasks-section right-column">
        <button 
          class="fab-desktop"
          @click="$emit('open-modal')"
          title="Create challenge"
        >
          {{ $t('today.new_challenge') }}
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
          />
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :is-open="showDeleteModal"
      :title="$t('modal.delete_title')"
      :message="$t('modal.delete_message')"
      :confirm-text="$t('modal.delete_confirm')"
      :processing-text="$t('modal.deleting')"
      :danger-mode="true"
      @close="closeDeleteModal"
      @confirm="confirmDelete"
    >
    <div v-if="selectedChallenges.length > 0" class="challenges-to-delete">
        <div 
          v-for="challenge in selectedChallenges" 
          :key="challenge.id"
          class="challenge-item-delete"
          :style="{ borderLeftColor: challenge.color }"
        >
          {{ challenge.goal }}
        </div>
      </div>
    </ConfirmModal>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNotification } from '@/composables/useNotification'
import TaskCard from '@/components/TaskCard.vue'
import ConfirmModal from '@/components/ConfirmModal.vue' 
import api from '@/services/api/index.js'
import { getTasksForDate, isSameDay } from '@/utils/taskHelpers'

const router = useRouter()
const i18n = useI18n()
const notify = useNotification()

const loading = ref(true)
const currentDate = ref(new Date())
const selectedDate = ref(null)
const allChallenges = ref([])
const allTasks = ref([])

// Selection Mode State
const isSelectionMode = ref(false)
const selectedChallengeIds = ref([])
const showDeleteModal = ref(false)

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

const selectedChallenges = computed(() => {
  return allChallenges.value.filter(c => selectedChallengeIds.value.includes(c.id))
})

const allSelected = computed(() => {
  return challengesForSelectedDate.value.length > 0 &&
         selectedChallengeIds.value.length === challengesForSelectedDate.value.length
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

  const totalDaysSoFar = dates.length
  const targetTotal = totalDaysSoFar <= 35 ? 35 : 42
  const remainingDays = targetTotal - totalDaysSoFar

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

// Selection Mode Functions
function toggleSelectionMode() {
  isSelectionMode.value = !isSelectionMode.value
  if (!isSelectionMode.value) {
    selectedChallengeIds.value = []
  }
}

function cancelSelection() {
  isSelectionMode.value = false
  selectedChallengeIds.value = []
}

function toggleChallengeSelection(challengeId) {
  const index = selectedChallengeIds.value.indexOf(challengeId)
  if (index > -1) {
    selectedChallengeIds.value.splice(index, 1)
  } else {
    selectedChallengeIds.value.push(challengeId)
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedChallengeIds.value = []
  } else {
    selectedChallengeIds.value = challengesForSelectedDate.value.map(c => c.id)
  }
}

function handleChallengeClick(challenge) {
  if (isSelectionMode.value) {
    toggleChallengeSelection(challenge.id)
  } else {
    viewChallenge(challenge)
  }
}

function openDeleteModal() {
  if (selectedChallengeIds.value.length > 0) {
    showDeleteModal.value = true
  }
}

function closeDeleteModal() {
  showDeleteModal.value = false
}

async function confirmDelete() {
  try {
    await Promise.all(
      selectedChallengeIds.value.map(id => 
        api.delete(`challenges/${id}/`, {
          params: { language: i18n.locale.value }
        })
      )
    )

    notify.success('success.challenges_deleted')
    
    await loadChallenges()
    if (allChallenges.value.length > 0) {
      await loadAllTasks()
    } else {
      allTasks.value = []
    }

    closeDeleteModal()
    cancelSelection()

  } catch (error) {
    if (!error.response) {
      notify.error('errors.network')
    } else {
      notify.error('errors.challenge_delete')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Error deleting challenges:', error)
    }
  }
}

function selectDate(dateObj) {
  selectedDate.value = dateObj.date
  
  const newDate = dateObj.date
  const currentView = currentDate.value

  if (newDate.getMonth() !== currentView.getMonth() || 
      newDate.getFullYear() !== currentView.getFullYear()) {
    
    currentDate.value = new Date(newDate.getFullYear(), newDate.getMonth(), 1)
  }
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
    if (process.env.NODE_ENV === 'development') {
      console.error('Error loading data:', error)
    }
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

.calendar-overflow-container {
  overflow: hidden;
  position: relative;
}

.calendar-fade-enter-active,
.calendar-fade-leave-active {
  transition: all 0.3s ease;
}

.calendar-fade-enter-from {
  opacity: 0;
  transform: translateX(10px); 
}

.calendar-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px); 
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
    cursor: pointer;      
    
    &:hover {
      background: $bg-secondary; 
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

.selection-controls {
  display: flex;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
  flex-wrap: wrap;

  @media (min-width: 768px) {
    flex-wrap: nowrap;
  }
}

.control-btn {
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-md;
  border: none;
  font-size: $font-size-sm;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.btn-manage {
    background: $primary;
    color: $white;

    &:hover:not(:disabled) {
      background: $primary-hover;
      transform: translateY(-1px);
      box-shadow: $shadow-sm;
    }
  }

  &.btn-select-all {
    background: $bg-secondary;
    color: $text-primary;

    &:hover:not(:disabled) {
      background: $border-hover;
    }
  }

  &.btn-delete {
    background: $danger;
    color: $white;

    &:hover:not(:disabled) {
      background: $danger-dark;
      transform: translateY(-1px);
      box-shadow: $shadow-sm;
    }
  }

  &.btn-cancel {
    background: $bg-secondary;
    color: $text-primary;

    &:hover:not(:disabled) {
      background: $border-hover;
    }
  }
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
  border-left: 4px solid transparent;
  display: flex;
  gap: $spacing-md;
  align-items: flex-start;
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }

  &.selection-mode {
    cursor: pointer;
  }

  &.selected {
    background: rgba($primary, 0.05);
  }
}

.challenge-checkbox {
  flex-shrink: 0;
  padding-top: 2px;
  cursor: pointer;
}

.hidden-checkbox {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
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
    background: $primary;
    border-color: $primary;
  }

  &:hover {
    border-color: $primary;
  }
}

.check-icon {
  width: 16px;
  height: 16px;
  color: white;
}

.challenge-content {
  flex: 1;
  min-width: 0;

  h4 {
    font-size: $font-size-sm;
    font-weight: $font-weight-semibold;
    margin-bottom: $spacing-sm;
    word-break: break-word;

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

// ===== Delete challenges =====
.challenges-to-delete {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
  max-height: 240px;
  overflow-y: auto;
  margin-top: $spacing-sm;
}

.challenge-item-delete {
  padding: $spacing-sm $spacing-md;
  background: $bg-secondary;
  border-radius: $radius-md;
  border-left: 4px solid;
  font-size: $font-size-sm;
  color: $text-primary;
  word-break: break-word;
}

</style>