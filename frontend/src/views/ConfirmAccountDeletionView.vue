<template>
  <div class="deletion-view page-container">
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
        <button class="btn-home" @click="goHome">{{ $t('deletion.go_home') }}</button>
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
import { handleApiError } from '@/utils/errorHandler'
import { useNotification } from '@/composables/useNotification'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const notify = useNotification()
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

  } catch (error) {
    status.value = 'error'
    
    if (error.response?.data?.error) {
      errorMessage.value = error.response.data.error
    } else {
      errorMessage.value = t('deletion.error_generic')
    }
    
    handleApiError(error, notify)
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
  
  padding-top: $spacing-responsive-md;
  padding-bottom: $spacing-responsive-md;
  
  @include md {
    padding-top: $spacing-responsive-lg;
    padding-bottom: $spacing-responsive-lg;
  }
}

.deletion-card {
  background: $white;
  border-radius: $radius-md;
  padding: $spacing-responsive-lg;
  width: 100%;
  max-width: 600px;
  box-shadow: $shadow-md;
  text-align: center;
  
  @include md {
    padding: $spacing-responsive-xl;
    border-radius: $radius-lg;
  }
}

.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-responsive-sm;
  
  @include md {
    gap: $spacing-responsive-md;
  }
}

.icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    width: 32px;
    height: 32px;
  }

  @include md {
    width: 72px;
    height: 72px;
    
    svg {
      width: auto;
      height: auto;
    }
  }

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
  font-size: $font-size-responsive-lg;
  font-weight: $font-weight-bold;
  color: $text-primary;
  margin: 0;
  
  @include md {
    font-size: $font-size-responsive-xl;
  }
}

.state-text {
  font-size: $font-size-xs;
  color: $text-secondary;
  line-height: 1.6;
  margin: 0;
  
  @include md {
    font-size: $font-size-responsive-sm;
  }
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid $border;
  border-top-color: $primary;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  
  @include md {
    width: 48px;
    height: 48px;
    border-width: 4px;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-home {
  margin-top: $spacing-responsive-sm;
  width: max-content;
  min-width: 160px;
  padding: $spacing-responsive-xs $spacing-responsive-md;
  background: $primary;
  color: $white;
  border: none;
  border-radius: $radius-md;
  font-size: $font-size-responsive-sm;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.2s ease;

  @include md {
    min-width: 200px;
  }

  &:hover {
    background: $primary-hover;
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
}
</style>