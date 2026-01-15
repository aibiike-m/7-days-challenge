<template>
  <div class="auth-view">
    <div class="auth-container">
      <div class="app-name">{{ APP_NAME }}</div>

      <div class="language-switcher">
        <button 
          @click="changeLanguage('en')" 
          :class="{ active: i18n.locale.value === 'en' }"
          class="lang-btn"
        >
          EN
        </button>
        <button 
          @click="changeLanguage('ru')"
          :class="{ active: i18n.locale.value === 'ru' }"
          class="lang-btn"
        >
          RU
        </button>
      </div>
      
      <div class="auth-card">
        <h1 class="auth-title">{{ isLogin ? $t('auth.login_title') : $t('auth.register_title') }}</h1>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <label for="login">{{ isLogin ? $t('auth.username') : $t('auth.username_register') }}</label>
            <input
              id="login"
              v-model="username"
              type="text"
              :placeholder="isLogin ? $t('auth.username') : $t('auth.username_register')"
              required
            />
          </div>

          <div v-if="!isLogin" class="form-group">
            <label for="email">{{ $t('auth.email') }}</label>
            <input
              id="email"
              v-model="email"
              type="email"
              :placeholder="$t('auth.email')"
              required
            />
          </div>

          <div class="form-group">
            <label for="password">{{ $t('auth.password') }}</label>
            <input
              id="password"
              v-model="password"
              type="password"
              :placeholder="$t('auth.password')"
              required
            />
          </div>

          <button type="submit" class="btn btn-primary btn-full">
            {{ isLogin ? $t('auth.login_btn') : $t('auth.register_btn') }}
          </button>
        </form>

        <div class="divider">
          <span>{{ $t('auth.or') }}</span>
        </div>

        <div class="google-button-container">
          <div id="g_id_signin"></div>
        </div>

        <p class="auth-toggle">
          {{ isLogin ? $t('auth.no_account') : $t('auth.have_account') }}
          <button
            type="button"
            @click="isLogin = !isLogin"
            class="toggle-btn"
          >
            {{ isLogin ? $t('auth.register_link') : $t('auth.login_link') }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useNotification } from '@/composables/useNotification'
import api from '@/services/api/index.js'
import { APP_NAME } from '@/constants/index'

const i18n = useI18n()
const notify = useNotification()

const isLogin = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

const handleGoogleResponse = async (response) => {
  try {
    const res = await api.post('auth/google/', { 
      token: response.credential,
      language: i18n.locale.value  
    })
    
    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)
    
    const serverLanguage = res.data.user?.language || 'en'
    localStorage.setItem('language', serverLanguage)
    i18n.locale.value = serverLanguage
    
    notify.success('success.login')
    
    setTimeout(() => {
      window.location.href = '/today'
    }, 500)
    
  } catch (error) {
    if (!error.response) {
      notify.error('errors.network')
    } else if (error.response?.status === 401) {
      notify.error('errors.google_login')
    } else {
      notify.error('errors.server')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Google login error:', error)
    }
  }
}

function renderGoogleButton() {
  const container = document.getElementById('g_id_signin')
  if (!container || !window.google?.accounts) return

  container.innerHTML = ''

  window.google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: handleGoogleResponse,
    auto_select: false,
    context: 'signin'
  })

  window.google.accounts.id.renderButton(container, {
    type: 'icon',
    shape: 'circle',
    theme: 'outline',
    size: 'large'
  })
}

function changeLanguage(lang) {
  i18n.locale.value = lang
  localStorage.setItem('language', lang)
}

onMounted(() => {
  if (window.google?.accounts) {
    renderGoogleButton()
    return
  }

  const script = document.createElement('script')
  script.src = 'https://accounts.google.com/gsi/client'
  script.async = true
  script.defer = true
  script.onload = renderGoogleButton
  script.onerror = () => {
    if (process.env.NODE_ENV === 'development') {
      console.error('Failed to load Google Identity Services')
    }
  }
  document.head.appendChild(script)
})

async function handleSubmit() {
  try {
    if (isLogin.value) {
      // Login
      const isEmail = username.value.includes('@')
      const endpoint = isEmail ? 'auth/login-by-email/' : 'token/'
      const payload = isEmail 
        ? { email: username.value, password: password.value }
        : { username: username.value, password: password.value }

      const response = await api.post(endpoint, payload)
      
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      
      const serverLanguage = response.data.user?.language || 'en'
      localStorage.setItem('language', serverLanguage)
      i18n.locale.value = serverLanguage
      
      notify.success('success.login')
      
      setTimeout(() => {
        window.location.href = '/today'
      }, 500)
      
    } else {
      // Register
      const response = await api.post('register/', {
        username: username.value,
        email: email.value,
        password: password.value,
        language: i18n.locale.value  
      })

      if (response.data.success) {        
        isLogin.value = true
        username.value = ''
        email.value = ''
        password.value = ''
      }
    }
  } catch (error) {
    if (!error.response) {
      notify.error('errors.network')
    } else if (error.response?.status === 401) {
      notify.error('errors.invalid_credentials')
    } else if (error.response?.status === 400) {
      const serverError = error.response?.data?.error
      if (serverError?.includes('username') || serverError?.includes('Username')) {
        notify.error('errors.username_taken')
      } else if (serverError?.includes('email') || serverError?.includes('Email')) {
        notify.error('errors.email_taken')
      } else {
        notify.error('errors.validation')
      }
    } else {
      notify.error('errors.server')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Auth error:', error)
    }
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
  font-size: 32px;
  font-weight: 700;
  color: $white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.language-switcher {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: $spacing-md;
}

.lang-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: $white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: $radius-md;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }

  &.active {
    background: $white;
    color: $primary;
    border-color: $white;
  }
}

.auth-card {
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-xl;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.auth-title {
  text-align: center;
  font-size: 28px;
  margin-bottom: $spacing-lg;
  color: $text-primary;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-weight: 600;
    font-size: 14px;
    color: $text-secondary;
  }

  input {
    padding: $spacing-sm $spacing-md;
    border: 1px solid $border;
    border-radius: $radius-md;
    font-size: 15px;
    transition: all 0.2s;

    &:focus {
      outline: none;
      border-color: $primary;
      box-shadow: 0 0 0 3px rgba($primary, 0.1);
    }
  }
}

.btn-full {
  width: 100%;
  padding: $spacing-md;
  font-size: 16px;
  font-weight: 600;
}

.divider {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin: $spacing-lg 0;
  color: $text-muted;

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: $border;
  }

  span {
    font-size: 14px;
  }
}

.auth-toggle {
  text-align: center;
  font-size: 14px;
  color: $text-muted;
  margin-top: $spacing-lg;

  .toggle-btn {
    background: none;
    border: none;
    color: $primary;
    font-weight: 600;
    cursor: pointer;
    text-decoration: underline;
    padding: 0;

    &:hover {
      color: $primary-light;
    }
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
  
  &:hover {
    transform: scale(1.05);
  }
}

.btn {
  background: $primary;
  color: $white;
  border: none;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: $primary-light;
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
  }
}

.btn-primary {
  background: $primary;
  color: $white;
}
</style>