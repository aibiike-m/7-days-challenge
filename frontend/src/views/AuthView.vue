<template>
  <div class="auth-view">
    <div class="auth-container">
      <div class="app-name">{{ APP_NAME }}</div>

      <div class="language-switcher">
        <button @click="changeLanguage('en')" :class="{ active: i18n.locale.value === 'en' }" class="lang-btn">EN</button>
        <button @click="changeLanguage('ru')" :class="{ active: i18n.locale.value === 'ru' }" class="lang-btn">RU</button>
      </div>
      
      <div v-if="!showForgotPassword" class="auth-card">
        <h1 class="auth-title">
          {{ isLogin ? $t('auth.login_title') : $t('auth.register_title') }}
        </h1>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <input id="email" v-model="email" type="email" :placeholder="$t('auth.email')" autocomplete="email" required />
          </div>

          <div class="form-group">
            <div class="password-input">
              <input
                id="password"
                v-model="password"
                :type="showPasswords ? 'text' : 'password'"
                :placeholder="$t('auth.password')"
                :autocomplete="isLogin ? 'current-password' : 'new-password'"
                required
              />
              <button type="button" @click="showPasswords = !showPasswords" class="password-toggle" :aria-label="showPasswords ? 'Hide password' : 'Show password'">
                <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
              </button>
            </div>
          </div>

          <div v-if="!isLogin" class="form-group">
            <div class="password-input">
              <input id="password-confirm" v-model="passwordConfirm" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('auth.password_confirm')" autocomplete="new-password" required />
            </div>
          </div>

          <button type="submit" class="btn btn-primary btn-full" :disabled="isLoading">
            {{ isLoading ? $t('common.loading') : (isLogin ? $t('auth.login_btn') : $t('auth.register_btn')) }}
          </button>        
        </form>

        <div v-if="isLogin" class="forgot-password-link">
          <button type="button" @click="openForgotPassword" class="link-btn">
            {{ $t('auth.forgot_password') }}
          </button>
        </div>

        <div class="divider"><span>{{ $t('auth.or') }}</span></div>
        <div class="google-button-container"><div id="g_id_signin"></div></div>

        <p class="auth-toggle">
          {{ isLogin ? $t('auth.no_account') : $t('auth.have_account') }}
          <button type="button" @click="toggleAuthMode" class="toggle-btn">
            {{ isLogin ? $t('auth.register_link') : $t('auth.login_link') }}
          </button>
        </p>
      </div>

      <div v-else class="auth-card">

        <template v-if="resetStep === 'email'">
          <h1 class="auth-title">{{ $t('auth.forgot_password_title') }}</h1>
          <p class="auth-subtitle">{{ $t('auth.forgot_password_subtitle') }}</p>
          <form @submit.prevent="requestPasswordReset" class="auth-form">
            <div class="form-group">
              <input v-model="resetEmail" type="email" :placeholder="$t('auth.email')" autocomplete="email" required />
            </div>
            <button type="submit" class="btn btn-primary btn-full" :disabled="isLoading || !resetEmail">
              {{ isLoading ? $t('common.loading') : $t('auth.send_reset_code') }}
            </button>
          </form>
          <div class="forgot-password-link">
            <button type="button" @click="closeForgotPassword" class="link-btn">← {{ $t('auth.back_to_login') }}</button>
          </div>
        </template>

        <template v-else-if="resetStep === 'code'">
          <h1 class="auth-title">{{ $t('auth.enter_reset_code_title') }}</h1>
          <p class="auth-subtitle">{{ $t('auth.enter_reset_code_subtitle', { email: resetEmail }) }}</p>
          <form @submit.prevent="verifyResetCode" class="auth-form">
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
            <button type="submit" class="btn btn-primary btn-full" :disabled="isLoading || resetCode.length !== 6">
              {{ isLoading ? $t('common.loading') : $t('auth.verify_code_btn') }}
            </button>
          </form>
          <div class="resend-row">
            <button type="button" @click="requestPasswordReset" class="link-btn" :disabled="isLoading">
              {{ $t('auth.resend_code') }}
            </button>
          </div>
          <div class="forgot-password-link">
            <button type="button" @click="resetStep = 'email'" class="link-btn">← {{ $t('auth.back') }}</button>
          </div>
        </template>

        <template v-else-if="resetStep === 'new-password'">
          <h1 class="auth-title">{{ $t('auth.new_password_title') }}</h1>
          <p class="auth-subtitle">{{ $t('auth.new_password_subtitle') }}</p>
          <form @submit.prevent="confirmPasswordReset" class="auth-form">
            <div class="form-group">
              <div class="password-input">
                <input
                  v-model="resetNewPassword"
                  :type="showPasswords ? 'text' : 'password'"
                  :placeholder="$t('auth.new_password')"
                  autocomplete="new-password"
                  required
                />
                <button type="button" @click="showPasswords = !showPasswords" class="password-toggle">
                  <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                </button>
              </div>
            </div>
            <div class="form-group">
              <div class="password-input">
                <input v-model="resetConfirmPassword" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('auth.confirm_new_password')" autocomplete="new-password" required />
              </div>
            </div>
            <button type="submit" class="btn btn-primary btn-full" :disabled="isLoading || !isResetPasswordFormValid">
              {{ isLoading ? $t('common.loading') : $t('auth.reset_password_btn') }}
            </button>
          </form>
        </template>

        <template v-else-if="resetStep === 'success'">
          <div class="reset-success">
            <div class="success-icon">✓</div>
            <h1 class="auth-title">{{ $t('auth.reset_success_title') }}</h1>
            <p class="auth-subtitle">{{ $t('auth.reset_success_subtitle') }}</p>
            <button class="btn btn-primary btn-full" @click="closeForgotPassword">
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
import { useI18n } from 'vue-i18n'
import { useNotification } from '@/composables/useNotification'
import api from '@/services/api/index.js'
import { APP_NAME } from '@/constants/index'

const i18n = useI18n()
const notify = useNotification()

const isLogin = ref(true)
const email = ref('')  
const password = ref('')
const passwordConfirm = ref('')
const showPasswords = ref(false)
const isLoading = ref(false)  
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

const showForgotPassword = ref(false)
const resetStep = ref('email')
const resetEmail = ref('')
const resetCode = ref('')
const resetNewPassword = ref('')
const resetConfirmPassword = ref('')

const isResetPasswordFormValid = computed(() =>
  resetNewPassword.value.length >= 8 &&
  resetNewPassword.value === resetConfirmPassword.value
)

const openForgotPassword = () => {
  resetEmail.value = email.value
  resetStep.value = 'email'
  resetCode.value = ''
  resetNewPassword.value = ''
  resetConfirmPassword.value = ''
  showPasswords.value = false
  showForgotPassword.value = true
}

const closeForgotPassword = () => {
  showForgotPassword.value = false
  resetStep.value = 'email'
  resetEmail.value = ''
  resetCode.value = ''
  resetNewPassword.value = ''
  resetConfirmPassword.value = ''
  showPasswords.value = false
}

const requestPasswordReset = async () => {
  if (isLoading.value) return
  isLoading.value = true
  try {
    await api.post('auth/request-password-reset/', { email: resetEmail.value })
    resetCode.value = ''
    resetStep.value = 'code'
  } catch (error) {
    notify.error(!error.response ? 'errors.network' : 'errors.server')
    if (import.meta.env.DEV) console.error('Password reset request error:', error)
  } finally {
    isLoading.value = false
  }
}

const verifyResetCode = () => {
  if (resetCode.value.length !== 6) return
  resetStep.value = 'new-password'
  showPasswords.value = false
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
    resetStep.value = 'success'
  } catch (error) {
    if (!error.response) {
      notify.error('errors.network')
    } else if (error.response?.status === 400) {
      const err = error.response?.data
      if (err?.confirm_password) {
        notify.error('errors.passwords_dont_match')
      } else {
        notify.error('errors.invalid_code')
        resetStep.value = 'code'
      }
    } else {
      notify.error('errors.server')
    }
    if (import.meta.env.DEV) console.error('Password reset confirm error:', error)
  } finally {
    isLoading.value = false
  }
}

const toggleAuthMode = () => {
  isLogin.value = !isLogin.value
  email.value = ''
  password.value = ''
  passwordConfirm.value = ''
  showPasswords.value = false
}

const saveAuthAndRedirect = (data, successMessageKey) => {
  localStorage.setItem('access_token', data.access)
  localStorage.setItem('refresh', data.refresh)
  const serverLanguage = data.user?.language || 'en'
  localStorage.setItem('language', serverLanguage)
  i18n.locale.value = serverLanguage
  notify.success(successMessageKey)  
  setTimeout(() => { window.location.href = '/today' }, 100)
}

const handleGoogleResponse = async (response) => {
  isLoading.value = true  
  try {
    const res = await api.post('auth/google/', { credential: response.credential, language: i18n.locale.value })
    saveAuthAndRedirect(res.data, 'success.login')
  } catch (error) {
    if (!error.response) notify.error('errors.network')
    else if (error.response?.status === 401) notify.error('errors.google_login')
    else notify.error('errors.server')
    if (import.meta.env.DEV) console.error('Google login error:', error)
  } finally {
    isLoading.value = false
  }
}

function renderGoogleButton() {
  const container = document.getElementById('g_id_signin')
  if (!container || !window.google?.accounts) return
  container.innerHTML = ''
  window.google.accounts.id.initialize({ client_id: GOOGLE_CLIENT_ID, callback: handleGoogleResponse, auto_select: false, context: 'signin' })
  window.google.accounts.id.renderButton(container, { type: 'icon', shape: 'circle', theme: 'outline', size: 'large' })
}

function changeLanguage(lang) {
  i18n.locale.value = lang
  localStorage.setItem('language', lang)
}

onMounted(() => {
  if (window.google?.accounts) { renderGoogleButton(); return }
  const script = document.createElement('script')
  script.src = 'https://accounts.google.com/gsi/client'
  script.async = true
  script.defer = true
  script.onload = renderGoogleButton
  script.onerror = () => { if (import.meta.env.DEV) console.error('Failed to load Google Identity Services') }
  document.head.appendChild(script)
})

async function handleSubmit() {
  if (isLoading.value) return
  isLoading.value = true
  try {
    if (isLogin.value) {
      const response = await api.post('auth/login-by-email/', { email: email.value, password: password.value })
      saveAuthAndRedirect(response.data, 'success.login')
    } else {
      if (password.value !== passwordConfirm.value) {
        notify.error('errors.passwords_dont_match')
        isLoading.value = false
        return
      }
      await api.post('auth/users/', { email: email.value, password: password.value, re_password: passwordConfirm.value })
      const loginResponse = await api.post('auth/login-by-email/', { email: email.value, password: password.value })
      saveAuthAndRedirect(loginResponse.data, 'success.registration')
    }
  } catch (error) {
    if (!error.response) notify.error('errors.network')
    else if (error.response?.status === 401) notify.error('errors.invalid_credentials')
    else if (error.response?.status === 400) {
      const serverError = error.response?.data
      if (import.meta.env.DEV) console.log('Server error details:', serverError)
      if (serverError?.email) notify.error('errors.email_taken')
      else if (serverError?.password) notify.error('errors.password_weak')
      else notify.error('errors.validation')
    } else {
      notify.error('errors.server')
    }
    if (import.meta.env.DEV) console.error('Auth error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.auth-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, $primary, $primary-light);
  padding: $spacing-lg;
}

.auth-container {
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

.language-switcher {
  display: flex;
  gap: $spacing-sm;                   
  justify-content: center;
  margin-bottom: $spacing-md;
}

.lang-btn {
  padding: $spacing-sm $spacing-md;   
  background: rgba($white, 0.2);
  color: $white;
  border: 2px solid rgba($white, 0.3);
  border-radius: $radius-md;
  font-weight: $font-weight-semibold;
  font-size: $font-size-sm; 
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover { background: rgba($white, 0.3); transform: translateY(-2px); }
  &.active { background: $white; color: $primary; border-color: $white; }
}

.auth-card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $spacing-xl;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.auth-title {
  text-align: center;
  font-size: 1.75rem;
  margin-bottom: $spacing-md;
  color: $text-primary;
}

.auth-subtitle {
  text-align: center;
  font-size: $font-size-sm;
  color: $text-muted;
  margin-bottom: $spacing-lg;
  line-height: 1.5;
}

.auth-form {
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

    &:focus { outline: none; border-color: $primary; box-shadow: 0 0 0 3px rgba($primary, 0.1); }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}

.password-input {
  position: relative;
  display: flex;
  align-items: center;

  input { width: 100%; padding-right: 2.8rem; }

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

    &:hover { color: $primary; }
    svg { display: block; }
  }
}

.btn-full {
  width: 100%;
  padding: $spacing-md;
  font-size: 1rem;
  font-weight: $font-weight-semibold;

  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

.forgot-password-link {
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
  color: $primary;
  font-size: $font-size-sm;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;

  &:hover { color: $primary-light; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.divider {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin: $spacing-lg 0;
  color: $text-muted;

  &::before, &::after { content: ''; flex: 1; height: 1px; background: $border; }
  span { font-size: $font-size-sm; }
}

.auth-toggle {
  text-align: center;
  font-size: $font-size-sm;
  color: $text-muted;
  margin-top: $spacing-lg;

  .toggle-btn {
    background: none;
    border: none;
    color: $primary;
    font-weight: $font-weight-semibold;
    cursor: pointer;
    text-decoration: underline;
    padding: 0;

    &:hover { color: $primary-light; }
  }
}

.google-button-container {
  display: flex;
  justify-content: center;
  margin: $spacing-md 0;
}

#g_id_signin {
  display: inline-block;
  transition: transform 0.2s ease;
  &:hover { transform: scale(1.05); }
}

.btn {
  background: $primary;
  color: $white;
  border: none;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) { background: $primary-light; transform: translateY(-2px); }
  &:active:not(:disabled) { transform: translateY(0); }
}

.btn-primary { background: $primary; color: $white; }

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

  .auth-title { margin-bottom: $spacing-sm; }
  .auth-subtitle { margin-bottom: $spacing-xl; }
}
</style>