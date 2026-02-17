<template>
  <div class="settings-view">
    <div class="settings-container">
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
          <button @click="requestEmailChange" class="btn btn-primary" :disabled="!newEmail || emailLoading">
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

        <div v-if="hasPassword && !showInlinePasswordReset" class="form-group">
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
          <button @click="changePassword" class="btn btn-primary btn-full" :disabled="!isPasswordFormValid || passwordLoading">
            {{ passwordLoading ? $t('common.loading') : $t('settings.change_password') }}
          </button>
          <div class="forgot-link-row">
            <button type="button" @click="openInlinePasswordReset" class="link-btn">
              {{ $t('auth.forgot_password') }}
            </button>
          </div>
        </div>

        <div v-else-if="!hasPassword" class="form-group">
          <p class="info-text">{{ $t('settings.no_password_set') }}</p>
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
          <button @click="setPassword" class="btn btn-primary btn-full" :disabled="!isSetPasswordFormValid || passwordLoading">
            {{ passwordLoading ? $t('common.loading') : $t('settings.set_password') }}
          </button>
        </div>

        <div v-if="showInlinePasswordReset" class="inline-reset">

          <template v-if="inlineResetStep === 'email'">
            <p class="info-text">{{ $t('auth.forgot_password_subtitle') }}</p>
            <div class="form-group">
              <input v-model="inlineResetEmail" type="email" :placeholder="$t('auth.email')" class="input-field" readonly />
              <button @click="inlineRequestReset" class="btn btn-primary btn-full" :disabled="inlineResetLoading">
                {{ inlineResetLoading ? $t('common.loading') : $t('auth.send_reset_code') }}
              </button>
              <button type="button" @click="closeInlinePasswordReset" class="link-btn">{{ $t('common.cancel') }}</button>
            </div>
          </template>

          <template v-else-if="inlineResetStep === 'code'">
            <p class="info-text">{{ $t('auth.enter_reset_code_subtitle', { email: inlineResetEmail }) }}</p>
            <div class="form-group">
              <input v-model="inlineResetCode" type="text" :placeholder="$t('auth.reset_code')" maxlength="6" inputmode="numeric" class="input-field" />
              <button @click="inlineVerifyCode" class="btn btn-primary btn-full" :disabled="inlineResetLoading || inlineResetCode.length !== 6">
                {{ inlineResetLoading ? $t('common.loading') : $t('auth.verify_code_btn') }}
              </button>
              <div class="inline-reset-footer">
                <button type="button" @click="inlineResetStep = 'email'" class="link-btn">← {{ $t('auth.back') }}</button>
                <button type="button" @click="inlineRequestReset" class="link-btn" :disabled="inlineResetLoading">{{ $t('auth.resend_code') }}</button>
              </div>
            </div>
          </template>

          <template v-else-if="inlineResetStep === 'new-password'">
            <div class="form-group">
              <div class="password-input">
                <input v-model="inlineNewPassword" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('auth.new_password')" class="input-field" />
                <button type="button" @click="showPasswords = !showPasswords" class="password-toggle">
                  <svg v-if="!showPasswords" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                </button>
              </div>
              <div class="password-input">
                <input v-model="inlineConfirmPassword" :type="showPasswords ? 'text' : 'password'" :placeholder="$t('settings.confirm_password')" class="input-field" />
              </div>
              <button @click="inlineConfirmReset" class="btn btn-primary btn-full" :disabled="inlineResetLoading || !isInlineResetFormValid">
                {{ inlineResetLoading ? $t('common.loading') : $t('auth.reset_password_btn') }}
              </button>
            </div>
          </template>

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
      :message="$t('settings.delete_password_message')"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useNotification } from '@/composables/useNotification'
import ConfirmModal from '@/components/ConfirmModal.vue'

const router = useRouter()
const { t } = useI18n()
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
const showInlinePasswordReset = ref(false)
const inlineResetStep = ref('email')
const inlineResetEmail = ref('')
const inlineResetCode = ref('')
const inlineNewPassword = ref('')
const inlineConfirmPassword = ref('')
const inlineResetLoading = ref(false)

const isPasswordFormValid = computed(() =>
  passwords.value.old && passwords.value.new && passwords.value.confirm && passwords.value.new.length >= 8
)

const isSetPasswordFormValid = computed(() =>
  passwords.value.new && passwords.value.confirm && passwords.value.new.length >= 8
)

const isInlineResetFormValid = computed(() =>
  inlineNewPassword.value.length >= 8 &&
  inlineNewPassword.value === inlineConfirmPassword.value
)

const goBack = () => router.push('/profile')

const loadUserData = async () => {
  try {
    const [userRes, passwordRes] = await Promise.all([
      api.get('/users/me/'),
      api.get('/users/has-password/')
    ])
    user.value = userRes.data
    hasPassword.value = passwordRes.data.has_password
  } catch {
    notify.error(t('errors.load_failed'))
  }
}

const changeDisplayName = async () => {
  if (!newDisplayName.value.trim()) return
  displayNameLoading.value = true
  try {
    const response = await api.patch('/users/me/', { display_name: newDisplayName.value.trim() })
    user.value.display_name = response.data.display_name
    notify.success(t('success.profile_saved'))
    newDisplayName.value = ''
  } catch (error) {
    notify.error(error.response?.data?.username?.[0] || error.response?.data?.error || t('errors.update_failed'))
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
    notify.success(t('success.code_sent'))
  } catch (error) {
    notify.error(error.response?.data?.new_email?.[0] || error.response?.data?.error || t('errors.request_failed'))
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
    notify.success(t('success.email_changed'))
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
    notify.error(error.response?.data?.error || t('errors.invalid_code'))
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
    notify.error(t('errors.password_mismatch'))
    return
  }
  passwordLoading.value = true
  try {
    await api.post('/users/change-password/', {
      old_password: passwords.value.old,
      new_password: passwords.value.new,
      confirm_password: passwords.value.confirm
    })
    notify.success(t('success.password_changed'))
    passwords.value = { old: '', new: '', confirm: '' }
    showPasswords.value = false
  } catch (error) {
    notify.error(
      error.response?.data?.old_password?.[0] ||
      error.response?.data?.new_password?.[0] ||
      error.response?.data?.error ||
      t('errors.update_failed')
    )
  } finally {
    passwordLoading.value = false
  }
}

const setPassword = async () => {
  if (!isSetPasswordFormValid.value) return
  if (passwords.value.new !== passwords.value.confirm) {
    notify.error(t('errors.password_mismatch'))
    return
  }
  passwordLoading.value = true
  try {
    await api.post('/users/set-password/', {
      new_password: passwords.value.new,
      confirm_password: passwords.value.confirm
    })
    hasPassword.value = true
    notify.success(t('success.password_set'))
    passwords.value = { old: '', new: '', confirm: '' }
    showPasswords.value = false
  } catch (error) {
    notify.error(
      error.response?.data?.new_password?.[0] ||
      error.response?.data?.error ||
      t('errors.update_failed')
    )
  } finally {
    passwordLoading.value = false
  }
}

const openInlinePasswordReset = () => {
  inlineResetEmail.value = user.value?.email || ''
  inlineResetStep.value = 'email'
  inlineResetCode.value = ''
  inlineNewPassword.value = ''
  inlineConfirmPassword.value = ''
  showPasswords.value = false
  passwords.value = { old: '', new: '', confirm: '' }
  showInlinePasswordReset.value = true
}

const closeInlinePasswordReset = () => {
  showInlinePasswordReset.value = false
  inlineResetStep.value = 'email'
  inlineResetCode.value = ''
  inlineNewPassword.value = ''
  inlineConfirmPassword.value = ''
}

const openForgotFromDeleteModal = () => {
  showDeletePasswordModal.value = false
  deletePassword.value = ''
  openInlinePasswordReset()
  setTimeout(() => {
    document.querySelector('.settings-card:nth-child(4)')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 100)
}

const inlineRequestReset = async () => {
  inlineResetLoading.value = true
  try {
    await api.post('/auth/request-password-reset/', { email: inlineResetEmail.value })
    inlineResetCode.value = ''
    inlineResetStep.value = 'code'
  } catch (error) {
    notify.error(!error.response ? t('errors.network') : t('errors.server'))
  } finally {
    inlineResetLoading.value = false
  }
}

const inlineVerifyCode = () => {
  if (inlineResetCode.value.length !== 6) return
  inlineResetStep.value = 'new-password'
  showPasswords.value = false
}

const inlineConfirmReset = async () => {
  if (!isInlineResetFormValid.value) return
  inlineResetLoading.value = true
  try {
    await api.post('/auth/confirm-password-reset/', {
      email: inlineResetEmail.value,
      code: inlineResetCode.value,
      new_password: inlineNewPassword.value,
      confirm_password: inlineConfirmPassword.value,
    })
    notify.success(t('success.password_changed'))
    closeInlinePasswordReset()
    hasPassword.value = true
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
    if (error.response?.status === 400) {
      const err = error.response?.data
      if (err?.confirm_password) {
        notify.error(t('errors.passwords_dont_match'))
      } else {
        notify.error(t('errors.invalid_code'))
        inlineResetStep.value = 'code'
      }
    } else {
      notify.error(t('errors.server'))
    }
  } finally {
    inlineResetLoading.value = false
  }
}

const openDeleteModal = () => { showDeleteWarningModal.value = true }

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
  } catch {
    notify.error(t('errors.request_failed'))
  } finally {
    deleteLoading.value = false
  }
}

const deleteAccountWithPassword = async (done) => {
  if (!deletePassword.value) {
    notify.error(t('errors.validation'))
    if (typeof done === 'function') done()
    return
  }
  deleteLoading.value = true
  try {
    await api.post('/users/delete-account/', { password: deletePassword.value })
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh')
    notify.success(t('success.account_deleted'))
    router.push('/auth')
  } catch (error) {
    notify.error(
      error.response?.data?.password?.[0] ||
      error.response?.data?.error ||
      t('errors.request_failed')
    )
  } finally {
    deleteLoading.value = false
    deletePassword.value = ''
    if (typeof done === 'function') done()
  }
}

onMounted(() => { loadUserData() })
</script>

<style scoped lang="scss">
.settings-view {
  min-height: 100vh;
  background: $bg-primary;
  padding: $spacing-md;

  @media (min-width: 768px) { padding: $spacing-lg; }
}

.settings-container { max-width: 600px; margin: 0 auto; }

.settings-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.btn-back {
  background: $white;
  border: 1px solid $border;
  border-radius: $radius-md;
  padding: $spacing-sm;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $text-secondary;

  &:hover { background: $bg-secondary; border-color: $primary; color: $primary; }
  svg { display: block; }
}

.settings-title { font-size: 24px; font-weight: 700; color: $text-primary; margin: 0; }

.settings-card {
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
  box-shadow: $shadow-sm;

  &--danger { border: 1px solid rgba($danger, 0.3); background: $danger-light; }
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
  margin: 0 0 $spacing-md 0;

  &--danger { color: $danger-dark; }
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-sm 0;
  border-bottom: 1px solid $border;

  &:last-child { border-bottom: none; }
}

.info-label { font-weight: 600; color: $text-secondary; font-size: $font-size-sm; }
.info-value { color: $text-primary; font-size: $font-size-sm; }

.form-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.input-field {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border;
  border-radius: $radius-md;
  font-size: 1rem;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;

  &:focus { outline: none; border-color: $primary; box-shadow: 0 0 0 3px rgba($primary, 0.1); }
  &[readonly] { background: $bg-secondary; color: $text-secondary; cursor: default; }
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

.info-text { color: $text-secondary; font-size: $font-size-sm; margin: 0; line-height: 1.5; }

.button-group { display: flex; gap: $spacing-sm; }

// Ссылка "Забыли пароль?" под формой смены пароля
.forgot-link-row {
  text-align: center;
  margin-top: -$spacing-sm;
}

// Ссылка "Забыли пароль?" внутри модалки
.modal-forgot-link {
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

  &--danger { color: $danger-dark; &:hover { color: $danger; } }
}

// Инлайн-флоу сброса пароля
.inline-reset {
  margin-top: $spacing-lg;
  padding-top: $spacing-lg;
  border-top: 1px solid $border;
}

.inline-reset-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn {
  padding: $spacing-sm $spacing-lg;
  border: none;
  border-radius: $radius-md;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

.btn-primary {
  background: $primary;
  color: white;

  &:hover:not(:disabled) { background: $primary-hover; transform: translateY(-1px); }
  &:active:not(:disabled) { transform: translateY(0); }
}

.btn-secondary {
  background: $bg-secondary;
  color: $text-primary;
  flex: 1;

  &:hover:not(:disabled) { background: $border-hover; }
}

.btn-danger {
  background: $danger-dark;
  color: $white;
  margin-top: $spacing-sm;

  &:hover:not(:disabled) { background: $danger-dark; transform: translateY(-1px); }
  &:active:not(:disabled) { transform: translateY(0); }
}

.btn-full { width: 100%; }
</style>