  <template>
    <div class="challenge">
      <header class="header">
        <router-link to="/" class="back-btn">{{ $t('challenge.back') }}</router-link>
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
          <span class="day-number">{{ $t('challenge.day') }} {{ day }}</span>
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
          <p>{{ $t('challenge.no_tasks') }}</p>
        </div>
      </div>

      <transition name="fade">
        <div v-if="challenge.progress_percentage === 100" class="celebration">
          <div class="confetti"></div>
          <h2>{{ $t('challenge.congratulations') }}</h2>
        </div>
      </transition>
    </div>
  </template>

  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useI18n } from 'vue-i18n'
  import api from '@/services/api'
  import TaskItem from '../components/TaskItem.vue'
  import { useRouter } from 'vue-router'


  const { t, locale } = useI18n()
  const router = useRouter()
  const challenge = ref({})
  const selectedDay = ref(1)
  const isToday = computed(() => selectedDay.value === challenge.value.current_day)
  const loading = ref(true)
  const error = ref(null)
  const i18n = useI18n()



  async function loadChallenge() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get(`challenges/${route.params.id}/`, {
        params: { language: locale.value }
      })
      challenge.value = res.data
    } catch (err) {
      console.error(err)
      error.value = i18n.t('common.error')
      router.push('/today')  
    } finally {
      loading.value = false
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
      await api.post(`tasks/${taskId}/${action}/`, {}, {
        params: { language: locale.value }
      })
      await loadChallenge() 
    } catch (err) {
      console.error('Ошибка обновления задачи', err)
    }
  }

  onMounted(loadChallenge)
  </script>
