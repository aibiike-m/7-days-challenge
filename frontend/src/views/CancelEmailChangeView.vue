<template>
  <div class="cancel-email-view page-container">
    <div class="cancel-email-card">

      <div v-if="status === 'loading'" class="state">
        <div class="spinner"></div>
        <p class="state-text">{{ $t('email_change.loading') }}</p>
      </div>

      <div v-else-if="status === 'success'" class="state">
        <div class="icon icon--success">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
        <h1 class="state-title">{{ $t('email_change.cancelled_title') }}</h1>
        <p class="state-text">{{ $t('email_change.cancelled_message') }}</p>
        
        <div v-if="emailWasRestored" class="warning-box">
          <div class="warning-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          <div class="warning-content">
            <p class="warning-title">{{ $t('email_change.security_warning_title') }}</p>
            <p class="warning-text">{{ $t('email_change.security_warning_message') }}</p>
          </div>
        </div>

        <button class="btn-home" @click="goToLogin">
          {{ $t('email_change.go_to_login') }}
        </button>
      </div>

      <div v-else-if="status === 'error'" class="state">
        <div class="icon icon--error">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <h1 class="state-title">{{ $t('email_change.error_title') }}</h1>
        <p class="state-text">{{ errorMessage }}</p>
        <button class="btn-home" @click="goToLogin">{{ $t('email_change.go_to_login') }}</button>
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
const emailWasRestored = ref(false)

const goToLogin = () => {
  router.push('/auth')
}

onMounted(async () => {
  const token = route.query.token

  if (!token) {
    status.value = 'error'
    errorMessage.value = t('email_change.error_no_token')
    return
  }

  try {
    const response = await api.cancelEmailChange(token)
    
    emailWasRestored.value = response.data.email_was_restored || false
    
    status.value = 'success'

  } catch (error) {
    status.value = 'error'
    errorMessage.value = error.response?.data?.error || t('email_change.error_generic')
  }
})
</script>

<style scoped lang="scss">
.cancel-email-view {
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

.cancel-email-card {
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

.warning-box {
  margin-top: $spacing-responsive-md;
  padding: $spacing-responsive-sm $spacing-responsive-md;
  background: rgba($warning, 0.08);
  border: 1px solid rgba($warning, 0.3);
  border-radius: $radius-md;
  display: flex;
  gap: $spacing-responsive-sm;
  text-align: left;
  
  @include md {
    padding: $spacing-responsive-md;
    gap: $spacing-responsive-md;
  }
}

.warning-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  color: $warning-dark;
  
  @include md {
    width: 28px;
    height: 28px;
  }
  
  svg {
    width: 100%;
    height: 100%;
  }
}

.warning-content {
  flex: 1;
}

.warning-title {
  font-size: $font-size-xs;
  font-weight: $font-weight-semibold;
  color: $warning-dark;
  margin: 0 0 4px 0;
  
  @include md {
    font-size: $font-size-responsive-sm;
    margin-bottom: 6px;
  }
}

.warning-text {
  font-size: $font-size-xs;
  color: $text-secondary;
  line-height: 1.5;
  margin: 0;
  
  @include md {
    font-size: $font-size-sm;
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