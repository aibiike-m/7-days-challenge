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
    localStorage.setItem('refresh_token', res.data.refresh)  // на будущее

    router.push('/')
  } catch (err) {
    const msg = err.response?.data?.detail || err.message
    alert('Ошибка: ' + msg)
  }
}
</script>

<style scoped lang="scss">
@import "../styles/components/auth.scss";
</style>