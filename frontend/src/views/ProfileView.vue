<template>
  <div class="profile-view">
    <div class="container">
      <h1 class="page-title">7 Days Challenge</h1>
      
      <div class="profile-layout">
        <div class="left-side">
          <div class="card profile-card">
            <h2 class="username">{{ username }}</h2>
            <p class="email">{{ email }}</p>
          </div>
        </div>

        <div class="right-side">
          <div class="card chart-card">
            <h3 class="chart-title">Статистика за неделю</h3>
            <div class="chart-wrapper">
              <canvas ref="chartCanvas"></canvas>
            </div>
          </div>
          
          <button class="btn-logout" @click="logout">
            Выйти из аккаунта
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import api from '@/services/api/index.js'

const router = useRouter()
const username = ref('')
const email = ref('')
const weeklyStats = ref([])
const chartCanvas = ref(null)
let chartInstance = null

async function loadProfile() {
  try {
    const res = await api.get('users/me/')
    username.value = res.data.username || 'Пользователь'
    email.value = res.data.email || ''
  } catch (e) { console.error(e) }
}

async function loadStats() {
  try {
    const res = await api.get('users/stats/weekly/')
    weeklyStats.value = res.data
  } catch (e) { 
    console.error('Error loading stats:', e)
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
        backgroundColor: '#3b82f6',
        borderColor: '#3b82f6',
        borderWidth: 0,
        borderRadius: 2,
        borderSkipped: false,
        barThickness: 28,
        categoryPercentage: 0.7,
        barPercentage: 0.85
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 10,
          titleFont: { size: 14 },
          bodyFont: { size: 13 },
          callbacks: {
            label: function(context) {
              return context.parsed.y + '%'
            }
          }
        }
      },
      animation: { duration: 1000, easing: 'easeOutQuart' },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { 
            stepSize: 20, 
            color: '#999', 
            font: { size: 12 },
            callback: function(value) {
              return value + '%'
            }
          },
          grid: { 
            color: 'rgba(0, 0, 0, 0.05)', 
            lineWidth: 1,
            drawBorder: false
          },
          border: { display: false }
        },
        x: {
          ticks: { color: '#666', font: { size: 13 } },
          grid: { display: false },
          border: { display: false }
        }
      }
    }
  })
}

watch(weeklyStats, async (newStats) => {
  if (newStats.length === 7) {
    await nextTick()
    createChart()
  }
})

async function logout() {
  try {
    await api.post('logout/')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/auth')
  } catch (e) {
    console.error('Ошибка выхода:', e)
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
  font-weight: $font-weight-bold;
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
  font-weight: $font-weight-semibold;
  color: $text-primary;
  margin: 0 0 $spacing-sm 0;

  @media (min-width: 768px) {
    font-size: 22px;
    margin-bottom: $spacing-sm;
  }
}

.email {
  color: $text-muted;
  font-size: 13px;
  margin: 0;

  @media (min-width: 768px) {
    font-size: 14px;
  }
}

.chart-title {
  font-size: 16px;
  font-weight: $font-weight-semibold;
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
  color: $white;
  border: none;
  padding: $spacing-sm $spacing-lg;
  border-radius: $radius-md;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  width: fit-content;
  margin-left: auto;
  margin-top: $spacing-lg;
  display: block;

  &:hover {
    background: $danger;
    color: $white;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
}
</style>