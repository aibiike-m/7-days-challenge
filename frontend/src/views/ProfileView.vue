<template>
  <div class="profile-view">
    <div class="card profile-card">
      <div class="avatar">
        {{ userInitial }}
      </div>
      <h2>{{ username }}</h2>
      <p class="email">{{ email }}</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-value">{{ stats.completedChallenges }}</div>
        <div class="stat-label">Завершено</div>
      </div>
      <div class="stat-card card">
        <div class="stat-value">{{ stats.activeDays }}</div>
        <div class="stat-label">Дней активности</div>
      </div>
      <div class="stat-card card">
        <div class="stat-value">{{ stats.completedTasks }}</div>
        <div class="stat-label">Выполнено задач</div>
      </div>
    </div>

    <div class="settings-section mobile-only">
      <h3>Настройки</h3>
      
      <div class="setting-item card">
        <div class="setting-info">
          <span class="setting-icon">🌙</span>
          <span class="setting-label">Тема</span>
        </div>
        <select v-model="theme" class="setting-select">
          <option value="light">Светлая</option>
          <option value="dark">Темная</option>
          <option value="auto">Авто</option>
        </select>
      </div>

      <div class="setting-item card">
        <div class="setting-info">
          <span class="setting-icon">🌐</span>
          <span class="setting-label">Язык</span>
        </div>
        <select v-model="language" class="setting-select">
          <option value="ru">Русский</option>
          <option value="en">English</option>
        </select>
      </div>
    </div>

    <button class="btn btn-secondary logout-btn" @click="logout">
      Выйти из аккаунта
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('Пользователь')
const email = ref('user@example.com')

const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase()
})

const stats = ref({
  completedChallenges: 0,
  activeDays: 0,
  completedTasks: 0
})

const theme = ref('light')
const language = ref('ru')

function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/auth')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';

.profile-view {
  max-width: 600px;
  margin: 0 auto;
  padding: $spacing-lg;
  padding-bottom: 100px;
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.card {
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
}

.profile-card {
  text-align: center;
  padding: $spacing-xl;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: $radius-full;
  background: linear-gradient(135deg, $primary, $primary-light);
  color: $white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: $font-weight-bold;
  margin: 0 auto $spacing-lg;
}

.profile-card h2 {
  margin-bottom: $spacing-sm;
}

.profile-card .email {
  color: $text-muted;
  font-size: $font-size-sm;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-md;
}

.stat-card {
  text-align: center;
  padding: $spacing-lg;
}

.stat-value {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: $primary;
  margin-bottom: $spacing-sm;
}

.stat-label {
  font-size: $font-size-xs;
  color: $text-muted;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  
  h3 {
    margin-bottom: $spacing-md;
    font-size: $font-size-lg;
  }
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
}

.setting-info {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.setting-icon {
  font-size: 24px;
}

.setting-label {
  font-weight: $font-weight-medium;
}

.setting-select {
  width: auto;
  min-width: 120px;
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border;
  border-radius: $radius-md;
  background: $bg-secondary;
  font-size: $font-size-sm;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: $primary;
  }
}

.mobile-only {
  display: flex;
  
  @media (min-width: 768px) {
    display: none;
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-lg;
  border: none;
  border-radius: $radius-md;
  font-family: $font-family;
  font-size: $font-size-base;
  font-weight: $font-weight-medium;
  cursor: pointer;
  transition: all 0.25s ease;
  outline: none;
}

.btn-secondary {
  background: $bg-secondary;
  color: $text-primary;
}

.logout-btn {
  margin-top: $spacing-lg;
  color: $danger;
  
  &:hover {
    background: rgba($danger, 0.1);
  }
}
</style>