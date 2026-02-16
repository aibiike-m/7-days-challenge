<template>
  <div class="deletion-view">
    <div class="deletion-card">

      <div v-if="status === 'loading'" class="state">
        <div class="spinner"></div>
        <p class="state-text">{{ $t('deletion.loading') }}</p>
      </div>

      <div v-else-if="status === 'success'" class="state">
        <div class="icon icon--success">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
        <h1 class="state-title">{{ $t('deletion.success_title') }}</h1>
        <p class="state-text">{{ $t('deletion.success_message') }}</p>
      </div>

      <div v-else-if="status === 'error'" class="state">
        <div class="icon icon--error">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <h1 class="state-title">{{ $t('deletion.error_title') }}</h1>
        <p class="state-text">{{ errorMessage }}</p>
        <button class="btn-home" @click="goHome">{{ $t('deletion.go_home') }}</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const status = ref('loading')
const errorMessage = ref('')

const goHome = () => {
  router.push('/auth')
}

onMounted(async () => {
  const token = route.query.token

  if (!token) {
    status.value = 'error'
    errorMessage.value = t('deletion.error_no_token')
    return
  }

  try {
    await api.get(`/users/confirm-account-deletion/?token=${token}`)

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh')

    status.value = 'success'

    setTimeout(() => router.push('/auth'), 3000)
  } catch (error) {
    status.value = 'error'
    errorMessage.value =
      error.response?.data?.error || t('deletion.error_generic')
  }
})
</script>

<style scoped lang="scss">
.deletion-view {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-md;
}

.deletion-card {
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-xl;
  max-width: 440px;
  width: 100%;
  box-shadow: $shadow-md;
  text-align: center;
}

.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-md;
}

.icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  &--success {
    background: $success-light;
    color: $success;
  }

  &--error {
    background: $danger-light;
    color: $danger-dark;
  }
}

.state-title {
  font-size: 22px;
  font-weight: 700;
  color: $text-primary;
  margin: 0;
}

.state-text {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
  margin: 0;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid $border;
  border-top-color: $primary;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-home {
  margin-top: $spacing-sm;
  padding: $spacing-sm $spacing-lg;
  background: $primary;
  color: $white;
  border: none;
  border-radius: $radius-md;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: $primary-hover;
    transform: translateY(-1px);
  }
}
</style>