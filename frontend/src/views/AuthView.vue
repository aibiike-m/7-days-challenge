<template>
  <div class="auth-view">
    <div class="auth-container">
      <div class="app-name">7 Days Challenge</div>
      
      <div class="auth-card">
        <h1 class="auth-title">{{ isLogin ? 'Вход' : 'Регистрация' }}</h1>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <label for="login">{{ isLogin ? 'Имя пользователя или Email' : 'Имя пользователя' }}</label>
            <input
              id="login"
              v-model="username"
              type="text"
              :placeholder="isLogin ? 'Введите имя или email' : 'Введите имя пользователя'"
              required
            />
          </div>

          <div v-if="!isLogin" class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="Введите email"
              required
            />
          </div>

          <div class="form-group">
            <label for="password">Пароль</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="Введите пароль"
              required
            />
          </div>

          <button type="submit" class="btn btn-primary btn-full">
            {{ isLogin ? 'Войти' : 'Зарегистрироваться' }}
          </button>
        </form>

        <div class="divider">
          <span>или</span>
        </div>

        <div id="g_id_onload"
          :data-client_id="GOOGLE_CLIENT_ID"
          data-callback="handleCredentialResponse"
          class="google-button-container"
        ></div>
        <div id="g_id_signin" data-type="standard"></div>

        <p class="auth-toggle">
          {{ isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?' }}
          <button
            type="button"
            @click="isLogin = !isLogin"
            class="toggle-btn"
          >
            {{ isLogin ? 'Зарегистрируйтесь' : 'Войдите' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/index.js'

const router = useRouter()
const isLogin = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

window.handleCredentialResponse = async (response) => {
  await loginWithGoogle(response.credential)
}

async function loginWithGoogle(googleToken) {
  try {
    const response = await api.post('auth/google/', {
      token: googleToken
    })

    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    router.push('/today')
  } catch (error) {
    alert('Ошибка при входе с Google')
  }
}

async function handleSubmit() {
  try {
    if (isLogin.value) {
      const isEmail = username.value.includes('@')
      
      if (isEmail) {
        const response = await api.post('auth/login-by-email/', {
          email: username.value,
          password: password.value
        })
        
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        router.push('/today')
      } else {
        const response = await api.post('token/', {
          username: username.value,
          password: password.value
        })

        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        router.push('/today')
      }
    } else {
      const response = await api.post('register/', {
        username: username.value,
        email: email.value,
        password: password.value
      })

      if (response.data.success) {
        alert('Регистрация успешна! Войдите с вашими данными.')
        isLogin.value = true
        username.value = ''
        email.value = ''
        password.value = ''
      }
    }
  } catch (error) {
    alert('Ошибка: ' + (error.response?.data?.error || error.message))
  }
}

onMounted(() => {
  const script = document.createElement('script')
  script.src = 'https://accounts.google.com/gsi/client'
  script.async = true
  script.defer = true
  document.head.appendChild(script)

  script.onload = () => {
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: window.handleCredentialResponse
      })
      window.google.accounts.id.renderButton(
        document.getElementById('g_id_signin'),
        {
          theme: 'outline',
          size: 'large',
          text: 'signin'
        }
      )
    }
  }
})
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

.google-button-container {
  display: flex;
  justify-content: center;
  margin-bottom: $spacing-lg;
}

#g_id_signin {
  display: flex;
  justify-content: center !important;
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