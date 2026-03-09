<template>
  <div class="settings-view page-container">
    <div class="settings-header">
      <button @click="goBack" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="settings-title">{{ $t('settings.title') }}</h1>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ $t('settings.account_info') }}</h2>
      <div class="info-row">
        <span class="info-label">{{ $t('settings.email') }}:</span>
        <span class="info-value">{{ user?.email }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">{{ $t('settings.username') }}:</span>
        <span class="info-value">{{ user?.display_name || $t('profile.default_username') }}</span>
      </div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ $t('settings.new_username') }}</h2>
      <div class="form-group">
        <input v-model="newDisplayName" type="text" :placeholder="$t('settings.new_username')" class="input-field" maxlength="150" />
        <button @click="changeDisplayName" class="btn btn-primary" :disabled="!newDisplayName.trim() || displayNameLoading">
          {{ displayNameLoading ? $t('common.loading') : $t('settings.save') }}
        </button>
      </div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ $t('settings.change_email') }}</h2>
      <div v-if="!emailChangeRequested" class="form-group">
        <input v-model="newEmail" type="email" :placeholder="$t('settings.new_email')" class="input-field" />
        <button @click="requestEmailChange" class="btn btn-primary" :disabled="!emailValidation.isValid || emailLoading">
          {{ emailLoading ? $t('common.loading') : $t('settings.send_code') }}
        </button>
      </div>
      <div v-else class="form-group">
        <p class="info-text">{{ $t('settings.code_sent_to') }} {{ newEmail }}</p>
        <input v-model="emailCode" type="text" :placeholder="$t('settings.enter_code')" maxlength="6" class="input-field" />
        <div class="button-group">
          <button @click="confirmEmailChange" class="btn btn-primary" :disabled="!emailCode || emailCode.length !== 6 || emailLoading">
            {{ emailLoading ? $t('common.loading') : $t('settings.confirm') }}
          </button>
          <button @click="cancelEmailChange" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
        </div>
      </div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">
        {{ hasPassword ? $t('settings.change_password') : $t('settings.set_password') }}
      </h2>

      <div v-if="hasPassword" class="form-group">
        <p class="password-hint-text">
          {{ $t('settings.password_hint_create_strong') }}
        </p>
        <div class="password-input">
          <input v-model="passwords.old" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('settings.current_password')" class="input-field" />
          <button type="button" @click="showPasswords = !showPasswords" class="password-toggle">
            <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
          </button>
        </div>
        <div class="password-input">
          <input v-model="passwords.new" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('settings.new_password')" class="input-field" />
          <button type="button" @click="showPasswords = !showPasswords" class="password-toggle">
            <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
          </button>
        </div>
        <div class="password-input">
          <input v-model="passwords.confirm" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('settings.confirm_password')" class="input-field" />
          <button type="button" @click="showPasswords = !showPasswords" class="password-toggle">
            <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
          </button>
        </div>
        <div class="forgot-link-row">
          <button @click="changePassword" class="btn btn-primary btn-full" :disabled="!isPasswordFormValid || passwords.new !== passwords.confirm || passwordLoading">
            {{ passwordLoading ? $t('common.loading') : $t('settings.change_password') }}
          </button>
          <div class="forgot-link-row">
            <button type="button" @click="openPasswordReset" class="link-btn">
              {{ $t('auth.forgot_password') }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="form-group">
        <p class="info-text">{{ $t('settings.no_password_set') }}</p>
        <p class="password-hint-text">
          {{ $t('settings.password_hint_create_strong') }}
        </p>
        <div class="password-input">
          <input v-model="passwords.new" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('settings.new_password')" class="input-field" />
          <button type="button" @click="showPasswords = !showPasswords" class="password-toggle">
            <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
          </button>
        </div>
        <div class="password-input">
          <input v-model="passwords.confirm" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('settings.confirm_password')" class="input-field" />
          <button type="button" @click="showPasswords = !showPasswords" class="password-toggle">
            <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
          </button>
        </div>
        <button @click="setPassword" class="btn btn-primary btn-full" :disabled="!isSetPasswordFormValid || passwords.new !== passwords.confirm || passwordLoading">
          {{ passwordLoading ? $t('common.loading') : $t('settings.set_password') }}
        </button>
      </div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ $t('settings.language') }}</h2>

      <div class="language-section">
        <div class="custom-select">             
          <div class="select-trigger" 
            @click.stop="isOpen = !isOpen" 
            :class="{ 'is-open': isOpen }"
          >
            <span>{{ locale === 'ru' ? 'Русский' : 'English' }}</span>
            <span class="arrow"></span>
          </div>
          <div v-if="isOpen" class="select-dropdown">
            <div class="select-option" @click="changeLanguage('ru')">Русский</div>
            <div class="select-option" @click="changeLanguage('en')">English</div>
          </div>
        </div>
      </div>
    </div>

    <div class="settings-card settings-card--danger">
      <h2 class="section-title section-title--danger">{{ $t('settings.delete_account') }}</h2>
      <p class="info-text">{{ $t('settings.delete_account_description') }}</p>
      <button @click="openDeleteModal" class="btn btn-danger btn-full">
        {{ $t('settings.delete_account_btn') }}
      </button>
    </div>
  </div>

    <ConfirmModal
      :isOpen="showDeleteWarningModal"
      :title="$t('settings.delete_warning_title')"
      :message="$t('settings.delete_warning_message')"
      :confirmText="$t('settings.delete_account')"
      :dangerMode="true"
      @close="showDeleteWarningModal = false"
      @confirm="onWarningConfirmed"
    />

    <ConfirmModal
      :isOpen="showDeletePasswordModal"
      :title="$t('settings.delete_password_title')"
      :confirmText="$t('settings.delete_confirm_btn')"
      :processingText="$t('common.loading')"
      :dangerMode="true"
      @close="closeDeletePasswordModal"
      @confirm="deleteAccountWithPassword"
    >
      <template #extra>
        <input
          v-model="deletePassword"
          type="password"
          :placeholder="$t('settings.current_password')"
          class="input-field"
          @keyup.enter="deleteAccountWithPassword"
        />
        <div class="modal-forgot-link">
          <button type="button" @click="openForgotFromDeleteModal" class="link-btn link-btn--danger">
            {{ $t('auth.forgot_password') }}
          </button>
        </div>
      </template>
    </ConfirmModal>

    <ConfirmModal
      :isOpen="showDeleteEmailSentModal"
      :title="$t('settings.delete_email_sent_title')"
      :message="$t('settings.delete_email_sent_message')"
      :confirmText="$t('common.confirm')"
      :dangerMode="false"
      @close="showDeleteEmailSentModal = false"
      @confirm="showDeleteEmailSentModal = false"
    />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNotification } from '@/composables/useNotification'
import { handleApiError } from '@/utils/errorHandler'
import api from '@/services/api'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { validatePassword, validateEmail } from '@/utils/validators'

const router = useRouter()
const i18n = useI18n()
const { t } = i18n
const notify = useNotification() 

const user = ref(null)
const hasPassword = ref(false)
const newDisplayName = ref('')
const displayNameLoading = ref(false)
const newEmail = ref('')
const emailCode = ref('')
const emailChangeRequested = ref(false)
const emailLoading = ref(false)
const passwords = ref({ old: '', new: '', confirm: '' })
const showPasswords = ref(false)
const passwordLoading = ref(false)
const showDeleteWarningModal = ref(false)
const showDeletePasswordModal = ref(false)
const showDeleteEmailSentModal = ref(false)
const deletePassword = ref('')
const deleteLoading = ref(false)
const isOpen = ref(false)

const locale = computed(() => i18n.locale.value)
const passwordValidation = computed(() => validatePassword(passwords.value.new))
const emailValidation = computed(() => validateEmail(newEmail.value))

const isPasswordFormValid = computed(() => {
  const val = passwordValidation.value
  return !!(passwords.value.old && val.minLength && val.notOnlyNumbers)
})

const isSetPasswordFormValid = computed(() => {
  const val = passwordValidation.value
  return !!(val.minLength && val.notOnlyNumbers)
})

const goBack = () => router.push('/profile')

const loadUserData = async () => {
  try {
    const [userRes, passwordRes] = await Promise.all([
      api.get('/users/me/'),
      api.get('/users/has-password/')
    ])

    user.value = userRes.data
    hasPassword.value = passwordRes.data.has_password

    const serverLang = user.value.language
    
    if (serverLang && serverLang !== i18n.locale.value) {
      i18n.locale.value = serverLang
      localStorage.setItem('language', serverLang)
    }
  } catch (error) {
    handleApiError(error, notify)

    if (import.meta.env.DEV) {
      console.error('Error loading user data:', error)
    }
  }
}

const changeDisplayName = async () => {
  if (!newDisplayName.value.trim()) return
  displayNameLoading.value = true
  
  try {
    const response = await api.patch('/users/me/', { 
      display_name: newDisplayName.value.trim() 
    })
    user.value.display_name = response.data.display_name
    notify.success('success.profile_saved')
    newDisplayName.value = ''
    
  } catch (error) {
    handleApiError(error, notify)
    
  } finally {
    displayNameLoading.value = false
  }
}

const requestEmailChange = async () => {
  if (!newEmail.value) return
  emailLoading.value = true
  
  try {
    await api.post('/users/request-email-change/', { new_email: newEmail.value })
    emailChangeRequested.value = true
    notify.success('success.code_sent')
    
  } catch (error) {
    handleApiError(error, notify)
    
  } finally {
    emailLoading.value = false
  }
}

const confirmEmailChange = async () => {
  if (!emailCode.value || emailCode.value.length !== 6) return
  emailLoading.value = true
  
  try {
    const res = await api.post('/users/confirm-email-change/', { code: emailCode.value })
    user.value = { ...user.value, email: res.data.new_email }
    notify.success('success.email_changed')
    newEmail.value = ''
    emailCode.value = ''
    emailChangeRequested.value = false
    
    setTimeout(async () => {
      try {
        const refreshToken = localStorage.getItem('refresh')
        if (refreshToken) await api.post('logout/', { refresh: refreshToken })
      } catch {
      } finally {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh')
        router.push('/auth')
      }
    }, 1800)
    
  } catch (error) {
    handleApiError(error, notify, {
      400: () => notify.error('errors.invalid_code')
    })
    
  } finally {
    emailLoading.value = false
  }
}

const cancelEmailChange = () => {
  newEmail.value = ''
  emailCode.value = ''
  emailChangeRequested.value = false
}

const changePassword = async () => {
  if (!isPasswordFormValid.value) return
  if (passwords.value.new !== passwords.value.confirm) {
    notify.error('errors.password_mismatch')
    return
  }
  
  passwordLoading.value = true
  
  try {
    await api.post('/users/change-password/', {
      old_password: passwords.value.old,
      new_password: passwords.value.new,
      confirm_password: passwords.value.confirm
    })
    
    notify.success('success.password_changed')  
    passwords.value = { old: '', new: '', confirm: '' }
    showPasswords.value = false
    
  } catch (error) {
    handleApiError(error, notify)
    
  } finally {
    passwordLoading.value = false
  }
}

const setPassword = async () => {
  if (!isSetPasswordFormValid.value) return
  if (passwords.value.new !== passwords.value.confirm) {
    notify.error('errors.password_mismatch')
    return
  }
  
  passwordLoading.value = true
  
  try {
    await api.post('/users/set-password/', {
      new_password: passwords.value.new,
      confirm_password: passwords.value.confirm
    })
    
    hasPassword.value = true
    notify.success('success.password_set')
    passwords.value = { old: '', new: '', confirm: '' }
    showPasswords.value = false
    
  } catch (error) {
    handleApiError(error, notify)
    
  } finally {
    passwordLoading.value = false
  }
}

async function changeLanguage(lang) {
  if (locale.value === lang) {
    isOpen.value = false
    return
  }

  try {
    await api.patch('users/me/', { language: lang })
    
    i18n.locale.value = lang
    localStorage.setItem('language', lang)
    isOpen.value = false
    notify.success('success.profile_saved')
    
  } catch (error) {
    handleApiError(error, notify)
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Error saving language:', error)
    }
  }
}

onMounted(() => {
  window.addEventListener('click', () => isOpen.value = false)
  loadUserData()
})

const openPasswordReset = () => {
  router.push({ 
    name: 'reset-password',
    query: { 
      email: user.value?.email,
      from: 'settings'
    }
  })
}

const openForgotFromDeleteModal = () => {
  showDeletePasswordModal.value = false
  deletePassword.value = ''
  router.push({ 
    name: 'reset-password',
    query: { email: user.value?.email, from: 'delete' }
  })
}

const openDeleteModal = () => { 
  showDeleteWarningModal.value = true 
}

const onWarningConfirmed = (done) => {
  showDeleteWarningModal.value = false
  if (hasPassword.value) {
    showDeletePasswordModal.value = true
  } else {
    requestAccountDeletion()
  }
  if (typeof done === 'function') done()
}

const closeDeletePasswordModal = () => {
  showDeletePasswordModal.value = false
  deletePassword.value = ''
}

const requestAccountDeletion = async () => {
  deleteLoading.value = true
  
  try {
    await api.post('/users/delete-account/', {})
    showDeleteEmailSentModal.value = true
    
  } catch (error) {
    handleApiError(error, notify)
    
  } finally {
    deleteLoading.value = false
  }
}

const deleteAccountWithPassword = async (done) => {
  if (!deletePassword.value) {
    notify.error('errors.validation')
    if (typeof done === 'function') done()
    return
  }
  
  deleteLoading.value = true
  
  try {
    await api.post('/users/delete-account/', { password: deletePassword.value })
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh')
    notify.success('success.account_deleted')
    router.push('/auth')
    
  } catch (error) {
    handleApiError(error, notify)
    
  } finally {
    deleteLoading.value = false
    deletePassword.value = ''
    if (typeof done === 'function') done()
  }
}
</script>

<style scoped lang="scss">
.settings-view {
  min-height: 100vh;
  background: $bg-primary;
  max-width: 600px; 
  padding-top: $spacing-responsive-md;
  padding-bottom: 100px;
  
  @include md {
    padding-top: $spacing-responsive-lg;
  }
}

.settings-header {
  display: flex;
  align-items: center;
  gap: $spacing-responsive-md;
  margin-bottom: $spacing-responsive-lg;
}

.btn-back {
  background: $white;
  border: 1px solid $border;
  border-radius: $radius-md;
  padding: $spacing-responsive-sm;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $text-secondary;
  flex-shrink: 0;

  &:hover { 
    background: $bg-secondary; 
    border-color: $primary; 
    color: $primary; 
  }
  
  svg { display: block; }
}

.settings-title { 
  font-size: $font-size-responsive-lg;
  font-weight: $font-weight-bold;
 
  color: $text-primary; 
  margin: 0;
  
  @include md {
    font-size: $font-size-responsive-xl;
  }
}

.settings-card {
  background: $white;
  border-radius: $radius-md;
  padding: $spacing-responsive-md;
  margin-bottom: $spacing-responsive-md;
  box-shadow: $shadow-sm;

  @include md {
    padding: $spacing-responsive-lg;
    border-radius: $radius-lg;
  }

  &--danger { 
    border: 1px solid rgba($danger, 0.3); 
    background: $danger-light; 
  }
}

.section-title {
  font-size: $font-size-responsive-base;
  font-weight: $font-weight-semibold;
  color: $text-primary;
  margin: 0 0 $spacing-responsive-md 0;

  @include md {
    font-size: $font-size-responsive-lg;
  }

  &--danger { color: $danger-dark; }
}

.info-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: $spacing-responsive-sm 0;
  border-bottom: 1px solid $border;
  gap: $spacing-responsive-xs;

  &:last-child { border-bottom: none; }
  
  @include md {
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-start;
    gap: $spacing-responsive-sm;
  }
}

.info-label { 
  font-weight: $font-weight-semibold;
 
  color: $text-secondary; 
  font-size: $font-size-responsive-sm;
  flex-shrink: 0;
}

.info-value {
  color: $text-primary;
  font-size: $font-size-responsive-sm;
  text-align: left;
  word-break: break-word;
  
  @include md {
    text-align: right;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-responsive-sm;
  
  @include md {
    gap: $spacing-responsive-md;
  }
}

.input-field {
  padding: $spacing-responsive-sm $spacing-responsive-md;
  border: 1px solid $border;
  border-radius: $radius-md;
  font-size: $font-size-responsive-sm;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;

  @include md {
    font-size: $font-size-responsive-base;
  }

  &:focus { 
    outline: none; 
    border-color: $primary; 
    box-shadow: 0 0 0 3px rgba($primary, 0.1); 
  }
  
  &[readonly] { 
    background: $bg-secondary; 
    color: $text-secondary; 
    cursor: default; 
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
    right: $spacing-responsive-md;
    background: none;
    border: none;
    cursor: pointer;
    color: $text-muted;
    padding: $spacing-sm;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s ease;

    &:hover { color: $primary; }
    svg { display: block; }
  }
}

.info-text { 
  color: $text-secondary; 
  font-size: $font-size-responsive-sm; 
  margin: 0; 
  line-height: 1.5; 
}

.button-group { 
  display: flex; 
  flex-direction: column;
  gap: $spacing-responsive-sm;
  
  @include md {
    flex-direction: row;
    
    .btn {
      width: auto;
    }
  }

  .btn {
    width: 100%;
    @include md {
      width: auto;
    }
  }
}

.forgot-link-row, .modal-forgot-link {
  text-align: center;
  margin-top: $spacing-responsive-sm;
  margin-bottom: $spacing-responsive-sm;
}

.link-btn {
  background: none;
  border: none;
  padding: 0;
  font-size: $font-size-responsive-sm;
  font-weight: $font-weight-semibold;
  color: $primary;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
  display: inline-block;

  &:hover,
  &:focus-visible {
    color: $primary-dark;
    text-decoration: underline;
  }

  &:active {
    color: $primary-hover;
  }

  &:disabled {
    color: $text-muted;
    cursor: not-allowed;
    text-decoration: none;
    opacity: 0.6;
  }

  &--danger {
    color: $danger;
    
    &:hover,
    &:focus-visible {
      color: $danger-dark;
      text-decoration: underline;
    }
    
    &:active {
      color: $danger;
    }
  }
}

.btn {
  padding: $spacing-responsive-sm $spacing-responsive-md;
  border: none;
  border-radius: $radius-md;
  font-size: $font-size-responsive-sm;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.2s ease;

  @include md {
    padding: $spacing-responsive-sm $spacing-responsive-lg;
  }

  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

.btn-primary {
  background: $primary;
  color: white;

  &:hover:not(:disabled) { 
    background: $primary-hover; 
    transform: translateY(-1px); 
  }
  
  &:active:not(:disabled) { 
    transform: translateY(0); 
  }
}

.btn-secondary {
  background: $bg-secondary;
  color: $text-primary;
  flex: 1;

  &:hover:not(:disabled) { 
    background: $border-hover; 
  }
}

.btn-danger {
  background: $danger-dark;
  color: $white;
  margin-top: $spacing-responsive-sm;

  &:hover:not(:disabled) { 
    background: $danger-dark; 
    transform: translateY(-1px); 
  }
  
  &:active:not(:disabled) { 
    transform: translateY(0); 
  }
}

.btn-full { width: 100%; }


.language-section {
  margin-top: $spacing-responsive-sm;
}

.custom-select {
  position: relative;
  width: 100%;
  min-width: 160px;
  user-select: none;
}

.select-trigger {
  padding: $spacing-responsive-sm $spacing-responsive-md;
  background: $bg-primary;
  border: 1px solid $border;      
  border-radius: $radius-md;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: $font-size-responsive-base;
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
  box-shadow: $shadow-md;
  overflow: hidden;
}

.select-option {
  padding: $spacing-responsive-sm $spacing-responsive-md;
  cursor: pointer;
  font-size: $font-size-responsive-base;
  transition: background 0.2s;

  &:hover {
    background: rgba($primary, 0.05);
    color: $primary;
  }
}

.requirement-item {
  font-size: $font-size-xs;
  transition: color 0.2s ease;
  
  &.valid {
    color: $success-dark;
  }
  
  &.invalid {
    color: $text-muted;
  }
}

.text-danger {
  color: $danger;
  margin-top: $spacing-responsive-xs;

}
.password-hint-text {
  font-size: $font-size-xs;
  color: $text-secondary;
  margin: 0 0 $spacing-responsive-sm 0;
  line-height: 1.4;
  font-weight: $font-weight-normal;

  @include md {
    font-size: $font-size-sm;
  }
}
</style>