<template>
  <div class="reset-view">
    <div class="reset-container">
      <div class="app-name">{{ APP_NAME }}</div>

      <div class="reset-card">
        <template v-if="resetStep === 'email'">
          <h1 class="reset-title">{{ $t('auth.forgot_password_title') }}</h1>
          <p class="reset-subtitle">{{ $t('auth.forgot_password_subtitle') }}</p>
          
          <form @submit.prevent="requestPasswordReset" class="reset-form">
            <div class="form-group">
              <input 
                v-model="resetEmail" 
                type="email" 
                :placeholder="$t('auth.email')" 
                autocomplete="email" 
                required 
              />
            </div>
            
            <button 
              type="submit" 
              class="btn btn-primary btn-full" 
              :disabled="isLoading || !resetEmail"
            >
              {{ isLoading ? $t('common.loading') : $t('auth.send_reset_code') }}
            </button>
          </form>
          
          <div class="back-link">
            <button type="button" @click="goBack" class="link-btn">
              ← {{ comeFrom === 'delete' ? $t('settings.title') : comeFrom === 'settings' ? $t('settings.title') : $t('auth.back_to_login') }}
            </button>
          </div>
        </template>

        <template v-else-if="resetStep === 'code'">
          <h1 class="reset-title">{{ $t('auth.enter_reset_code_title') }}</h1>
          <p class="reset-subtitle">{{ $t('auth.enter_reset_code_subtitle', { email: resetEmail }) }}</p>
          
          <form @submit.prevent="proceedToNewPassword" class="reset-form">
            <div class="form-group">
              <input
                v-model="resetCode"
                type="text"
                :placeholder="$t('auth.reset_code')"
                maxlength="6"
                inputmode="numeric"
                autocomplete="one-time-code"
                required
              />
            </div>
            
            <button 
              type="submit" 
              class="btn btn-primary btn-full" 
              :disabled="resetCode.length !== 6"
            >
              {{ $t('auth.verify_code_btn') }}
            </button>
          </form>
          
          <div class="resend-row">
            <button 
              type="button" 
              @click="requestPasswordReset" 
              class="link-btn" 
              :disabled="isLoading"
            >
              {{ $t('auth.resend_code') }}
            </button>
          </div>
          
          <div class="back-link">
            <button type="button" @click="resetStep = 'email'" class="link-btn">
              ← {{ $t('auth.back') }}
            </button>
          </div>
        </template>

        <template v-else-if="resetStep === 'new-password'">
          <h1 class="reset-title">{{ $t('auth.new_password_title') }}</h1>
          <p class="reset-subtitle">{{ $t('auth.new_password_subtitle') }}</p>
          
          <form @submit.prevent="confirmPasswordReset" class="reset-form">
            <div class="form-group">
              <div class="password-input">
                <input
                  v-model="resetNewPassword"
                  :type="showPasswords ? 'text' : 'password'"
                  :placeholder="$t('auth.new_password')"
                  autocomplete="new-password"
                  required
                />
                <button 
                  type="button" 
                  @click="showPasswords = !showPasswords" 
                  class="password-toggle"
                  :aria-label="showPasswords ? 'Hide password' : 'Show password'"
                >
                  <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="form-group">
              <div class="password-input">
                <input 
                  v-model="resetConfirmPassword" 
                  :type="showPasswords ? 'text' : 'password'" 
                  :placeholder="$t('auth.confirm_new_password')" 
                  autocomplete="new-password" 
                  required 
                />
              </div>
            </div>
            
            <button 
              type="submit" 
              class="btn btn-primary btn-full" 
              :disabled="isLoading || !isResetPasswordFormValid"
            >
              {{ isLoading ? $t('common.loading') : $t('auth.reset_password_btn') }}
            </button>
          </form>
        </template>

        <template v-else-if="resetStep === 'success'">
          <div class="reset-success">
            <div class="success-icon">✓</div>
            <h1 class="reset-title">{{ $t('auth.reset_success_title') }}</h1>
            <p class="reset-subtitle">{{ $t('auth.reset_success_subtitle') }}</p>
            <button class="btn btn-primary btn-full" @click="goToLogin">
              {{ $t('auth.go_to_login') }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNotification } from '@/composables/useNotification'
import api from '@/services/api/index.js'
import { APP_NAME } from '@/constants/index'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const notify = useNotification()

const resetStep = ref('email')
const resetEmail = ref('')
const resetCode = ref('')
const resetNewPassword = ref('')
const resetConfirmPassword = ref('')
const showPasswords = ref(false)
const isLoading = ref(false)
const comeFrom = ref(route.query.from || 'auth')

const isResetPasswordFormValid = computed(() =>
  resetNewPassword.value.length >= 8 &&
  resetNewPassword.value === resetConfirmPassword.value
)

const requestPasswordReset = async () => {
  if (isLoading.value) return
  isLoading.value = true
  try {
    await api.post('auth/request-password-reset/', { email: resetEmail.value })
    resetCode.value = ''
    resetStep.value = 'code'
  } catch (error) {
    notify.error(!error.response ? t('errors.network') : t('errors.server'))
    if (import.meta.env.DEV) console.error('Password reset request error:', error)
  } finally {
    isLoading.value = false
  }
}

const proceedToNewPassword = async () => {
  if (resetCode.value.length !== 6 || isLoading.value) return
  isLoading.value = true
  
  try {
    await api.post('auth/verify-password-reset-code/', {
      email: resetEmail.value,
      code: resetCode.value,
    })
    
    resetStep.value = 'new-password'
    showPasswords.value = false
  } catch (error) {
    if (!error.response) {
      notify.error(t('errors.network'))
    } else if (error.response?.status === 400) {
      notify.error(t('errors.invalid_code'))
      resetCode.value = ''
    } else {
      notify.error(t('errors.server'))
    }
    if (import.meta.env.DEV) console.error('Code verification error:', error)
  } finally {
    isLoading.value = false
  }
}

const confirmPasswordReset = async () => {
  if (isLoading.value || !isResetPasswordFormValid.value) return
  isLoading.value = true
  try {
    await api.post('auth/confirm-password-reset/', {
      email: resetEmail.value,
      code: resetCode.value,
      new_password: resetNewPassword.value,
      confirm_password: resetConfirmPassword.value,
    })
    
    await logoutUser()
    resetStep.value = 'success'
  } catch (error) {
    if (!error.response) {
      notify.error(t('errors.network'))
      return
    }

    if (error.response.status === 400) {
      const err = error.response.data
      
      if (err?.new_password) {
        const msg = Array.isArray(err.new_password) ? err.new_password[0] : err.new_password
        notify.error(msg)
      } 
      else if (err?.confirm_password) {
        const msg = Array.isArray(err.confirm_password) ? err.confirm_password[0] : err.confirm_password
        notify.error(msg)
      }
      else if (err?.non_field_errors && Array.isArray(err.non_field_errors)) {
        notify.error(err.non_field_errors[0])
      } 
      else if (err?.error && err.error.toLowerCase().includes('code')) {
        notify.error(t('errors.invalid_code'))
        resetStep.value = 'code'
        resetCode.value = ''
      } 
      else if (err?.detail || err?.error || err?.message) {
        notify.error(err.detail || err.error || err.message)
      }
      else {
        notify.error(t('errors.server'))
      }
    } else {
      notify.error(t('errors.server'))
    }
    
    if (import.meta.env.DEV) console.error('Password reset confirm error:', error)
  } finally {
    isLoading.value = false
  }
}

const logoutUser = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh')
    if (refreshToken) {
      await api.post('logout/', { refresh: refreshToken })
    }
  } catch (error) {
    if (import.meta.env.DEV) console.log('Logout error (ignored):', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh')
  }
}

const goBack = () => {
  if (comeFrom.value === 'settings' || comeFrom.value === 'delete') {
    router.push('/settings')
  } else {
    router.push('/auth')
  }
}

const goToLogin = () => {
  router.push('/auth')
}

onMounted(() => {
  if (route.query.email) {
    resetEmail.value = route.query.email
  }
  if (route.query.from) {
    comeFrom.value = route.query.from
  }
})
</script>

<style scoped lang="scss">
.reset-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, $primary, $primary-light);
  padding: $spacing-lg;
}

.reset-container {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.app-name {
  text-align: center;
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: $white;
  text-shadow: $shadow-md;
}

.reset-card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $spacing-xl;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.reset-title {
  text-align: center;
  font-size: 1.75rem;
  margin-bottom: $spacing-md;
  color: $text-primary;
}

.reset-subtitle {
  text-align: center;
  font-size: $font-size-sm;
  color: $text-muted;
  margin-bottom: $spacing-lg;
  line-height: 1.5;
}

.reset-form {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.form-group {
  display: flex;
  flex-direction: column;

  input {
    padding: $spacing-sm $spacing-md;
    border: 1px solid $border;
    border-radius: $radius-md;
    font-size: 1rem;
    transition: all 0.2s ease;

    &:focus {
      outline: none;
      border-color: $primary;
      box-shadow: 0 0 0 3px rgba($primary, 0.1);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.password-input {
  position: relative;
  display: flex;
  align-items: center;

  input {
    width: 100%;
    padding-right: 2.8rem;
  }

  .password-toggle {
    position: absolute;
    right: $spacing-md;
    background: none;
    border: none;
    cursor: pointer;
    color: $text-muted;
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s ease;

    &:hover {
      color: $primary;
    }

    svg {
      display: block;
    }
  }
}

.btn {
  background: $primary;
  color: $white;
  border: none;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: $primary-light;
    transform: translateY(-2px);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-full {
  width: 100%;
  padding: $spacing-md;
  font-size: 1rem;
  font-weight: $font-weight-semibold;
}

.btn-primary {
  background: $primary;
  color: $white;
}

.back-link {
  text-align: center;
  margin-top: $spacing-md;
}

.resend-row {
  text-align: center;
  margin-top: $spacing-sm;
}

.link-btn {
  background: none;
  border: none;
  padding: 0;
  font-size: $font-size-sm;
  font-weight: $font-weight-semibold;
  color: $primary;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.16s ease, opacity 0.16s ease;

  &:hover,
  &:focus-visible {
    color: $primary-light;
  }

  &:active {
    color: $primary-light;
  }

  &:disabled {
    color: $text-muted;
    cursor: not-allowed;
    opacity: 0.6;
  }
}

.reset-success {
  text-align: center;
  padding: $spacing-md 0;

  .success-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: rgba($primary, 0.1);
    color: $primary;
    font-size: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto $spacing-lg;
  }

  .reset-title {
    margin-bottom: $spacing-sm;
  }

  .reset-subtitle {
    margin-bottom: $spacing-xl;
  }
}
</style>