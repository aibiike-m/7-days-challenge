<template>
  <div class="profile-view">
    <div class="container">
      <h1 class="page-title">{{ APP_NAME }}</h1>

      <div class="profile-layout">
        <div class="profile-header">
          <h2 class="username">{{ displayName }}</h2>
        </div>

        <div class="card chart-card">
          <h3 class="chart-title">{{ $t('profile.statistics') }}</h3>
          <div class="chart-wrapper">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>

        <div class="profile-actions">
          <button class="btn-settings" @click="goToSettings">
            {{ $t('profile.settings') }}
          </button>
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
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import api from '@/services/api' 
import { useNotification } from '@/composables/useNotification'
import { APP_NAME } from '@/constants/index'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { handleApiError } from '@/utils/errorHandler'

const router = useRouter()
const i18n = useI18n()
const notify = useNotification()

const displayName = ref('Loading...')
const weeklyStats = ref([])
const chartCanvas = ref(null)
const showLogoutModal = ref(false)
let chartInstance = null

onMounted(async () => {
  await loadProfile()
  await loadStats()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

watch(weeklyStats, async (newStats) => {
  if (newStats.length > 0) {
    await nextTick()
    createChart()
  }
})

async function loadProfile() {
  try {
    const res = await api.get('users/me/')
    displayName.value = res.data.display_name || 'User'
    
    const serverLang = res.data.language || 'en'
    i18n.locale.value = serverLang
    localStorage.setItem('language', serverLang)
  } catch (e) {
    handleApiError(e, 'Profile error:')
  }
}

async function loadStats() {
  try {
    const res = await api.get('users/stats/weekly/', {
      params: { language: i18n.locale.value }
    })
    weeklyStats.value = res.data
  } catch (e) {
    if (process.env.NODE_ENV === 'development') console.error('Stats error:', e)
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

function goToSettings() {
  router.push('/settings')
}

async function confirmLogout() {
  try {
    const refreshToken = localStorage.getItem('refresh')
    if (refreshToken) {
      await api.post('logout/', { refresh: refreshToken })
    }
  } catch (error) {
    if (process.env.NODE_ENV === 'development') console.error('Logout error:', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh')
    window.location.href = '/auth'
  }
}
</script>

<style scoped lang="scss">
.profile-view {
  padding: $spacing-responsive-md 0;
  min-height: 100vh;
  background: $bg-primary;
  @include md { padding: $spacing-responsive-lg 0; }
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 $spacing-responsive-sm;
  display: flex;
  flex-direction: column;
  @include md { padding: 0 $spacing-responsive-md; }
  @include lg { padding: 0 $spacing-responsive-lg; }
}

.page-title {
  display: block;
  text-align: center;
  color: $primary;
  margin: 0 0 $spacing-responsive-lg 0;
  padding-top: $spacing-responsive-sm;
  font-size: $font-size-responsive-xl;
  font-weight: $font-weight-bold;
  letter-spacing: -0.5px;
  @include md { display: none; }
}

.profile-layout {
  display: flex;
  flex-direction: column;
  gap: $spacing-responsive-md;
  flex: 1;
}

.profile-header {
  padding: $spacing-responsive-sm 0;
  text-align: left;
  @include md { padding: $spacing-responsive-md 0; }
}

.username {
  font-size: $font-size-responsive-xl;
  font-weight: 800;
  color: $text-primary;
  margin: 0;
  letter-spacing: -0.4px;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  @include md { font-size: $font-size-responsive-2xl; }
}

.card {
  background: $white;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
  padding: $spacing-responsive-md;
  @include md {
    padding: $spacing-responsive-lg;
    border-radius: $radius-lg;
  }
}

.chart-title {
  font-size: $font-size-responsive-xl;
  font-weight: $font-weight-semibold;
  color: $text-secondary;
  margin: 0 0 $spacing-responsive-md 0;
}

.chart-wrapper {
  position: relative;
  height: 200px;
  @include md { height: 260px; }
}

.profile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-responsive-sm;
  justify-content: center;
  @include md {
    justify-content: flex-end;
    gap: $spacing-responsive-sm $spacing-responsive-md;
  }
}

.btn-settings,
.btn-logout {
  flex: 1 1 45%;
  padding: $spacing-responsive-sm $spacing-responsive-md;
  border-radius: $radius-md;
  font-weight: $font-weight-semibold;
  font-size: $font-size-responsive-sm;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  color: white;
  @include md {
    flex: 0 1 auto;
    min-width: 140px;
    padding: $spacing-responsive-sm $spacing-responsive-lg;
  }
}

.btn-settings {
  background: $primary;
  &:hover:not(:disabled) {
    background: $primary-hover;
    transform: translateY(-1px);
  }
}

.btn-logout {
  background: $danger;
  &:hover:not(:disabled) {
    background: $danger-dark;
    transform: translateY(-1px);
  }
}
</style>