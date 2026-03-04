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
                    {{ calculateChallengeProgress(challenge.id) }}%
                  </span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ 
                      width: calculateChallengeProgress(challenge.id) + '%',
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
          @click="isModalOpen = true"
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
    <CreateChallengeModal 
      :is-open="isModalOpen" 
      @close="isModalOpen = false"
      @created="handleChallengeCreated" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNotification } from '@/composables/useNotification'
import TaskCard from '@/components/TaskCard.vue'
import ConfirmModal from '@/components/ConfirmModal.vue' 
import CreateChallengeModal from '@/components/CreateChallengeModal.vue'
import api from '@/services/api/index.js'
import { getTasksForDate, isSameDay } from '@/utils/taskHelpers.js'

const router = useRouter()
const { t, locale } = useI18n()
const notify = useNotification()

const loading = ref(true)
const currentDate = ref(new Date())
const selectedDate = ref(null)
const allChallenges = ref([])
const allTasks = ref([])

const isSelectionMode = ref(false)
const selectedChallengeIds = ref([])
const showDeleteModal = ref(false)
const isModalOpen = ref(false)

const weekdaysRu = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const weekdaysEn = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const weekdays = computed(() => 
  locale.value === 'ru' ? weekdaysRu : weekdaysEn
)

const currentMonthName = computed(() => {
  const loc = locale.value === 'ru' ? 'ru-RU' : 'en-US'
  return currentDate.value.toLocaleDateString(loc, { month: 'long', year: 'numeric' })
})

const selectedDayTasks = computed(() => {
  if (!selectedDate.value) return []

  const tasks = getTasksForDate(allTasks.value, allChallenges.value, selectedDate.value)

  const challengeOrder = {};
  allChallenges.value.forEach((ch, index) => {
    challengeOrder[ch.id] = index;
  });

  return [...tasks].sort((a, b) => {
    const orderA = challengeOrder[a.challenge_id] ?? 999;
    const orderB = challengeOrder[b.challenge_id] ?? 999;

    if (orderA !== orderB) {
      return orderA - orderB;
    }
    return a.id - b.id;
  });
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
  const prevMonth = month === 0 ? 11 : month - 1
  const prevYear = month === 0 ? year - 1 : year
  
  for (let i = startDay - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i
    dates.push({
      day,
      date: new Date(prevYear, prevMonth, day),
      isOtherMonth: true,
      key: `${prevYear}-${prevMonth}-${day}`
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
      key: `${year}-${month}-${i}`
    })
  }

  const totalDaysSoFar = dates.length
  const targetTotal = totalDaysSoFar <= 35 ? 35 : 42
  const remainingDays = targetTotal - totalDaysSoFar
  const nextMonth = month === 11 ? 0 : month + 1
  const nextYear = month === 11 ? year + 1 : year

  for (let i = 1; i <= remainingDays; i++) {
    dates.push({
      day: i,
      date: new Date(nextYear, nextMonth, i),
      isOtherMonth: true,
      key: `${nextYear}-${nextMonth}-${i}`
    })
  }

  return dates
})




// const tasksForSelectedDate = computed(() => {
//   if (!selectedDate.value) return [];

//   return allTasks.value
//     .filter(task => {
//       const taskDate = calculateTaskDate(task);
//       return taskDate === selectedDate.value;
//     })
//     .sort((a, b) => {
//       // 1. Сначала группируем по челленджу
//       if (a.challenge_id !== b.challenge_id) {
//         return a.challenge_id - b.challenge_id;
//       }
//       // 2. Внутри челленджа сортируем по ID задачи
//       return a.id - b.id;
//     });
// });

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

async function handleChallengeCreated(newChallenge) {
  await loadChallenges()
  
  if (allChallenges.value.length > 0) {
    await loadAllTasks()
  }
}

async function confirmDelete() {
  try {
    await api.bulkDeleteChallenges(selectedChallengeIds.value);

    allChallenges.value = allChallenges.value.filter(
      challenge => !selectedChallengeIds.value.includes(challenge.id)
    );

    allTasks.value = allTasks.value.filter(
      task => !selectedChallengeIds.value.includes(task.challenge_id)
    );

    notify.success('success.challenges_deleted');
    
    closeDeleteModal();
    cancelSelection();

  } catch (error) {
    if (!error.response) {
      notify.error('errors.network');
    } else {
      notify.error('errors.challenge_delete');
    }
    console.error('Error deleting challenges:', error);
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

function calculateChallengeProgress(challengeId) {
  const challengeTasks = allTasks.value.filter(t => t.challenge_id === challengeId)
  if (challengeTasks.length === 0) return 0
  
  const completed = challengeTasks.filter(t => t.is_completed).length
  return Math.round((completed / challengeTasks.length) * 100)
}

async function onTaskToggled(task) {
  const originalStatus = task.is_completed;
  try {
    task.is_completed = !task.is_completed;
    await api.updateTaskStatus(task.id, task.is_completed);
  } catch (error) {
    task.is_completed = originalStatus;
    if (!error.response) {
      notify.error('errors.network')
    } else {
      notify.error('errors.task_update')
    }
  }
}
async function loadChallenges() {
  try {
    const response = await api.getChallenges()
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
    const response = await api.getAllTasks()
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
  padding: $spacing-responsive-sm;
  padding-bottom: 100px;
  position: relative;

  @include sm {
    padding: $spacing-responsive-md;
  }

  @include lg {
    padding: $spacing-responsive-lg;
    max-width: 1400px;
    margin: 0 auto;
  }
}

.card {
  background: $white;
  border-radius: $radius-md;
  padding: $spacing-responsive-md;
  box-shadow: $shadow-sm;
  margin-bottom: $spacing-responsive-md;

  @include md {
    border-radius: $radius-lg;
    padding: $spacing-responsive-lg;
    margin-bottom: $spacing-responsive-lg;
  }
}

// ===== Calendar =====
.calendar-card {
  background: $white;
  border-radius: $radius-md;
  padding: $spacing-md;
  box-shadow: $shadow-sm;
  
  @include md {
    padding: $spacing-lg;
    border-radius: $radius-lg;
  }
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-responsive-md;

  @include md {
    margin-bottom: $spacing-responsive-lg;
  }
}

.month-title {
  font-size: $font-size-responsive-base;
  font-weight: $font-weight-semibold;
  text-transform: capitalize;

  @include md {
    font-size: $font-size-responsive-lg;
  }
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: $radius-full;
  border: none;
  background: $bg-secondary;
  font-size: $font-size-responsive-lg;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  @include md {
    width: 40px;
    height: 40px;
    font-size: $font-size-responsive-base;
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
  gap: $spacing-responsive-xs;
}

.weekday {
  text-align: center;
  font-size: $font-size-xs;
  font-weight: $font-weight-semibold;
  color: $text-muted;
  padding: $spacing-responsive-sm 0;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: $radius-sm;
  padding: $spacing-responsive-xs;
  font-size: $font-size-xs;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;

  @include md {
    border-radius: $radius-md;
    font-size: $font-size-responsive-sm;
  }
  
  &:hover {
    background: $bg-secondary;
  }
  
  &.other-month {
    color: $border-hover; 
    cursor: pointer;      
    &:hover { background: $bg-secondary; }
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

.loading, .empty-tasks {
  text-align: center;
  padding: $spacing-responsive-lg;
  color: $text-muted;
}

.empty-tasks {
  background: $bg-primary;
  border-radius: $radius-md;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-responsive-md;

  @include md {
    gap: $spacing-responsive-sm;
  }
}

// ===== Challenges =====
.challenges-section {
  margin-top: $spacing-responsive-lg;
}

.selection-controls {
  display: flex;
  gap: $spacing-responsive-sm;
  margin-bottom: $spacing-responsive-md;
  flex-wrap: wrap;

  @include md {
    flex-wrap: nowrap;
  }
}

.control-btn {
  padding: $spacing-responsive-xs $spacing-responsive-sm;
  font-size: $font-size-xs;
  border-radius: $radius-md;
  border: none;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  @include md {
    padding: $spacing-responsive-sm $spacing-responsive-md;
    font-size: $font-size-responsive-sm;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.btn-manage {
    background: $primary;
    color: $white;
    &:hover:not(:disabled) {
      background: $primary-hover;
      transform: translateY(-2px);
      box-shadow: $shadow-sm;
    }
  }

  &.btn-select-all, &.btn-cancel {
    background: $bg-secondary;
    color: $text-primary;
    &:hover:not(:disabled) { background: $border-hover; }
  }

  &.btn-delete {
    background: $danger;
    color: $white;
    &:hover:not(:disabled) {
      background: $danger-dark;
      transform: translateY(-2px);
    }
  }
}

.challenges-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-responsive-md;

  @include md {
    gap: $spacing-responsive-lg;
  }
}

.challenge-card {
  cursor: pointer;
  transition: all 0.25s ease;
  border-left: 4px solid transparent;
  display: flex;
  gap: $spacing-responsive-sm;
  padding: $spacing-responsive-sm;
  align-items: flex-start;
  
  @include md {
    gap: $spacing-responsive-md;
    padding: $spacing-responsive-lg;
  }

  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }

  &.selected {
    background: rgba($primary, 0.05);
  }
}

.challenge-checkbox {
  flex-shrink: 0;
  padding-top: 2px;
}

.hidden-checkbox {
  position: absolute;
  opacity: 0;
  width: 0;
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
    font-size: $font-size-responsive-sm;
    font-weight: $font-weight-semibold;
    margin-bottom: $spacing-responsive-sm;
    word-break: break-word;

    @include md {
      font-size: $font-size-base;
    }
  }
}

.challenge-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-responsive-sm;
  font-size: $font-size-xs;

  @include md {
    font-size: $font-size-responsive-sm;
  }
}

.challenge-duration { color: $text-secondary; }
.challenge-progress { font-weight: $font-weight-semibold; }

.progress-bar {
  height: 4px;
  background: $bg-secondary;
  border-radius: $radius-full;
  overflow: hidden;

  @include md {
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

  @include md {
    flex-direction: row;
    gap: $spacing-responsive-lg;

    .left-column { flex: 1; }
    .right-column { flex: 1.2; }
  }
}

.fab-desktop {
  display: none;
  width: fit-content;
  padding: $spacing-responsive-md $spacing-responsive-lg;
  background: $primary;
  color: $white;
  border: none;
  border-radius: $radius-md;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: $font-size-base;
  box-shadow: $shadow-md;
  margin-bottom: $spacing-responsive-lg;

  @include md {
    display: block;
  }

  &:hover {
    background: $primary-hover;
    transform: translateY(-2px);
  }
}

.challenges-to-delete {
  display: flex;
  flex-direction: column;
  gap: $spacing-responsive-sm;
  max-height: 240px;
  overflow-y: auto;
  margin-top: $spacing-responsive-sm;
}

.challenge-item-delete {
  padding: $spacing-responsive-sm $spacing-responsive-md;
  background: $bg-secondary;
  border-radius: $radius-md;
  border-left: 4px solid;
  font-size: $font-size-responsive-sm;
  color: $text-primary;
  word-break: break-word;
}
</style>