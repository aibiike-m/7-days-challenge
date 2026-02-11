<template>
  <div class="profile-view">
    <div class="container">
      <h1 class="page-title">{{ APP_NAME }}</h1>

      <div class="profile-layout">
        <div class="left-side">
          <div class="card profile-card">
            <h2 class="username">{{ displayName }}</h2>

            <div class="language-section">
              <div class="custom-select">             
                <div class="select-trigger" 
                  @click.stop="isOpen = !isOpen" 
                  :class="{ 'is-open': isOpen }"
                >
                  <span>{{ i18n.locale.value === 'ru' ? 'Русский' : 'English' }}</span>
                  <span class="arrow"></span>
                </div>
                <div v-if="isOpen" class="select-dropdown">
                  <div class="select-option" @click="changeLanguage('ru')">Русский</div>
                  <div class="select-option" @click="changeLanguage('en')">English</div>
                </div>
              </div>
            </div>

            <button class="btn-settings" @click="goToSettings">{{ $t('profile.settings') }}</button>
          </div>
        </div>

        <div class="right-side">
          <div class="card chart-card">
            <h3 class="chart-title">{{ $t('profile.statistics') }}</h3>
            <div class="chart-wrapper">
              <canvas ref="chartCanvas"></canvas>
            </div>
          </div>

          <button class="btn-logout" @click="showLogoutModal = true">
            {{ $t('profile.logout') }}
          </button>
        </div>
      </div>
    </div>
    <ConfirmModal
      :is-open="showLogoutModal"
      :title="$t('profile.logout_confirm_title')"
      :confirm-text="$t('profile.logout')"
      :danger-mode="true"
      @close="showLogoutModal = false"
      @confirm="confirmLogout"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import api from '@/services/api' 
import { useNotification } from '@/composables/useNotification'
import { APP_NAME } from '@/constants/index'
import ConfirmModal from '@/components/ConfirmModal.vue'

const router = useRouter()
const i18n = useI18n()
const notify = useNotification()
const displayName = ref('Loading...')
const weeklyStats = ref([])
const chartCanvas = ref(null)
const isOpen = ref(false)
const showLogoutModal = ref(false)
let chartInstance = null

onMounted(() => {
  window.addEventListener('click', () => isOpen.value = false)
})

async function loadProfile() {
  try {
    const res = await api.get('users/me/')
    displayName.value = res.data.display_name || 'User'
    
    const serverLang = res.data.language || 'en'
    i18n.locale.value = serverLang
    localStorage.setItem('language', serverLang)
    
  } catch (e) {
    if (!e.response) {
      notify.error('errors.network')
    } else {
      notify.error('errors.server')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Profile error:', e)
    }
  }
}

async function loadStats() {
  try {
    const res = await api.get('users/stats/weekly/', {
      params: { language: i18n.locale.value }
    })
    weeklyStats.value = res.data
    
  } catch (e) {
    if (process.env.NODE_ENV === 'development') {
      console.error('Statistics error:', e)
    }
  }
}

function createChart() {
  if (!chartCanvas.value) return
  if (chartInstance) chartInstance.destroy()

  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels: weeklyStats.value.map(d => d.day),
      datasets: [{
        data: weeklyStats.value.map(d => d.percent),
        backgroundColor: '#5B9FD8',
        borderRadius: 4,
        barThickness: 28,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } },
        x: { grid: { display: false } }
      }
    }
  })
}

watch(weeklyStats, async (newStats) => {
  if (newStats.length > 0) {
    await nextTick()
    createChart()
  }
})

async function changeLanguage(lang) {
  if (i18n.locale.value === lang) {
    isOpen.value = false
    return
  }

  try {
    await api.patch('users/me/', { language: lang })
    
    i18n.locale.value = lang
    localStorage.setItem('language', lang)
    isOpen.value = false

    await loadStats()
    notify.success('success.profile_saved')
    
  } catch (error) {
    if (!error.response) {
      notify.error('errors.network')
    } else {
      notify.error('errors.server')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Error saving language:', error)
    }
  }
}

function goToSettings() {
  router.push('/settings')
}

async function confirmLogout() {
  try {
    const refreshToken = localStorage.getItem('refresh')
    
    if (refreshToken) {
      await api.post('logout/', {
        refresh: refreshToken
      })
    }
    
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      console.error('Logout error:', error)
    }
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh')
    
    setTimeout(() => {
      window.location.href = '/auth'
    }, 500)
  }
}

onMounted(async () => {
  await loadProfile()
  await loadStats()
})
</script>

<style scoped lang="scss">
.profile-view {
  padding: $spacing-md 0;
  min-height: 100vh;
  background: $bg-primary;

  @media (min-width: 768px) {
    padding: $spacing-lg 0;
  }
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 $spacing-sm;
  display: flex;
  flex-direction: column;

  @media (min-width: 640px) {
    padding: 0 $spacing-md;
  }

  @media (min-width: 1024px) {
    padding: 0 $spacing-lg;
  }
}

.page-title {
  display: none;
  text-align: center;
  color: $primary;
  margin: 0 0 $spacing-lg 0;
  padding-top: $spacing-sm;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;

  @media (max-width: 767px) {
    display: block;
  }
}

.profile-layout {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  flex: 1;

  @media (min-width: 768px) {
    flex-direction: row;
    align-items: start;
    gap: $spacing-lg;
  }
}

.left-side {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;

  @media (min-width: 768px) {
    gap: $spacing-lg;
    flex: 0 0 auto;
  }
}

.right-side {
  flex: 1;
  min-width: 0;
}

.card {
  background: $white;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
  padding: $spacing-md;

  @media (min-width: 768px) {
    padding: $spacing-lg;
    border-radius: $radius-lg;
  }
}

.profile-card {
  text-align: center;
}

.username {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
  margin: 0 0 $spacing-md 0;

  @media (min-width: 768px) {
    font-size: 22px;
    margin-bottom: $spacing-md;
  }
}

.custom-select {
  position: relative;
  width: 100%;
  min-width: 160px;
  user-select: none;
  margin-bottom: $spacing-md;
}

.select-trigger {
  padding: $spacing-sm $spacing-md;
  background: $bg-primary;
  border: 1px solid $border;      
  border-radius: $radius-md;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: $font-size-sm;        
  transition: all 0.2s;

  &.is-open {
    border-color: $primary;
    background: $white;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }
}

.arrow {
  border: solid $text-secondary; 
  border-width: 0 2px 2px 0;
  display: inline-block;
  padding: 3px;
  transform: rotate(45deg);
  transition: transform 0.2s;
}

.is-open .arrow {
  transform: rotate(-135deg);
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid $primary;
  border-top: none;
  border-bottom-left-radius: $radius-md;
  border-bottom-right-radius: $radius-md;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  overflow: hidden;
}

.select-option {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;

  &:hover {
    background: rgba($primary, 0.05);
    color: $primary;
  }
}

.btn-settings {
  background: $primary;
  color: white;
  border: none;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-md;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;

  svg {
    width: 18px;
    height: 18px;
  }

  &:hover {
    background: $primary-hover;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-secondary;
  margin: 0 0 $spacing-md 0;

  @media (min-width: 768px) {
    font-size: 18px;
    margin-bottom: $spacing-lg;
  }
}

.chart-wrapper {
  position: relative;
  height: 200px;

  @media (min-width: 768px) {
    height: 260px;
  }
}

.btn-logout {
  background: $primary-dark;
  color: white;
  border: none;
  padding: $spacing-sm $spacing-lg;
  border-radius: $radius-md;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  width: fit-content;
  margin-left: auto;
  margin-top: $spacing-lg;
  display: block;

  &:hover {
    background: $danger;
    color: white;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
}
</style>