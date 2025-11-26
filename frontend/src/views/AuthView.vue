<template>
  <div class="auth">
    <div class="card">
      <h1>{{ isLogin ? 'Вход' : 'Регистрация' }}</h1>
      
      <form @submit.prevent="submit">
        <input v-model="username" placeholder="Логин" required />
        
        <input 
          v-if="!isLogin" 
          v-model="email" 
          type="email" 
          placeholder="Email" 
          required 
        />
        
        <input v-model="password" type="password" placeholder="Пароль" required />
        
        <button type="submit" class="btn-primary">
          {{ isLogin ? 'Войти' : 'Создать аккаунт' }}
        </button>
      </form>

      <p class="switch">
        {{ isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?' }}
        <a @click="isLogin = !isLogin">{{ isLogin ? 'Зарегистрироваться' : 'Войти' }}</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const isLogin = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const router = useRouter()
const API = 'http://127.0.0.1:8000'

axios.defaults.withCredentials = true

async function submit() {
  try {
    if (!isLogin.value) {
      await axios.post(`${API}/api/register/`, {
        username: username.value,
        email: email.value,
        password: password.value
      })
      alert('Регистрация успешна! Входим...')
    }

    const res = await axios.post(`${API}/api/token/`, {
      username: username.value,
      password: password.value
    })

    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh) 

    router.push('/')
  } catch (err) {
    const msg = err.response?.data?.detail || err.message
    alert('Ошибка: ' + msg)
  }
}
</script>

<style scoped lang="scss">
.auth {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: $bg-primary;
}

.card {
  background: $white;
  padding: 3rem;
  border-radius: $radius-lg;  
  box-shadow: $shadow-sm;     
  width: 100%;
  max-width: 400px;
  text-align: center;
}

h1 {
  color: $text-primary;
  margin-bottom: 2rem;
  font-size: $font-size-2xl;
}

input {
  width: 100%;
  padding: 1rem;
  margin: 0.5rem 0;
  border: 2px solid $border;
  border-radius: $radius-md;
  font-size: $font-size-base;
  font-family: $font-family;
  transition: all 0.15s ease;
  
  &:focus {
    outline: none;
    border-color: $primary;
    box-shadow: 0 0 0 3px rgba($primary, 0.1);
  }
  
  &::placeholder {
    color: $text-muted;
  }
}

.btn-primary {
  width: 100%;
  padding: 1rem;
  margin-top: 1rem;
  background: $primary;
  color: $white;
  border: none;
  border-radius: $radius-md;
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.25s ease;
  
  &:hover {
    background: $primary-hover;
    transform: translateY(-1px);
    box-shadow: $shadow-md;
  }
  
  &:active {
    transform: translateY(0);
  }
}

.switch {
  margin-top: 2rem;
  font-size: $font-size-sm;
  color: $text-secondary;
  
  a {
    color: $primary;
    cursor: pointer;
    text-decoration: underline;
    font-weight: $font-weight-medium;
    
    &:hover {
      color: $primary-dark;
    }
  }
}
</style>