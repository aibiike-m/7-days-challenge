<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const isAuthenticated = ref(false)
const router = useRouter()
const API = 'http://127.0.0.1:8000'

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

async function checkAuth() {
  const token = localStorage.getItem('access_token')
  if (!token) {
    isAuthenticated.value = false
    return
  }

  try {
    await axios.get(`${API}/api/challenges/active/`)
    isAuthenticated.value = true
  } catch (err) {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    isAuthenticated.value = false
  }
}

async function logout() {
  const refreshToken = localStorage.getItem('refresh_token')
  if (refreshToken) {
    try {
      await axios.post(`${API}/api/token/blacklist/`, { refresh: refreshToken })
    } catch (err) {
      console.warn('Blacklist failed')
    }
  }

  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  isAuthenticated.value = false
  router.push('/auth')
}


onMounted(checkAuth)
</script>

<template>
  <nav class="navbar">
    <router-link to="/" class="logo">7DC</router-link>

    <div class="nav-links">
      <router-link to="/" class="nav-link">Главная</router-link>

      <template v-if="isAuthenticated">
        <button @click="logout" class="nav-link btn-logout">Выйти</button>
      </template>
      <template v-else>
        <router-link to="/auth" class="nav-link btn-auth">Войти</router-link>
      </template>
    </div>
  </nav>
</template>

<style scoped lang="scss">
@import "../styles/components/nav-bar.scss";
</style>