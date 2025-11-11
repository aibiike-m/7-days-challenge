<template>
  <div class="home">
    <div class="card">
      <h1>7 Days Challenge</h1>
      <p class="subtitle">Напиши свою цель — ИИ создаст план на 7 дней</p>

      <form @submit.prevent="createChallenge" class="form">
        <textarea
          v-model="goal"
          placeholder="Например: Выучить 50 английских слов, Пробежать 5 км, Написать главу книги..."
          required
          class="textarea"
          rows="5"
        ></textarea>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading">ИИ думает...</span>
          <span v-else>Начать челлендж</span>
        </button>
      </form>

      <button v-if="hasActive" @click="goToActive" class="btn-secondary">
        Продолжить текущий челлендж
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const goal = ref('')
const loading = ref(false)
const hasActive = ref(false)
const router = useRouter()

const API_URL = 'http://127.0.0.1:8000'

async function createChallenge() {
  if (!goal.value.trim()) return
  loading.value = true
  try {
    const res = await axios.post(`${API_URL}/challenges/`, { goal: goal.value })
    router.push(`/challenge/${res.data.id}`)
  } catch (err) {
    alert('Ошибка: ' + (err.response?.data?.error || err.message))
  } finally {
    loading.value = false
  }
}

async function checkActive() {
  try {
    const res = await axios.get(`${API_URL}/challenges/active/`)
    if (res.data.id) hasActive.value = true
  } catch (err) {
  }
}

async function goToActive() {
  try {
    const res = await axios.get(`${API_URL}/challenges/active/`)
    router.push(`/challenge/${res.data.id}`)
  } catch (err) {
    alert('Не удалось загрузить челлендж')
  }
}

onMounted(checkActive)
</script>

<style scoped lang="scss">
@import "../styles/components/home.scss";
</style>