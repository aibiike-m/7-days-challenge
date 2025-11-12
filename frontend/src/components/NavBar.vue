<template>
  <nav class="navbar">
    <router-link to="/" class="logo">7DC</router-link>
    
    <div class="nav-links">
      <router-link to="/" class="nav-link">Главная</router-link>
      <button v-if="hasActive" @click="goToActive" class="nav-link btn-active">
        Текущий челлендж
      </button>
      <router-link v-else to="/" class="nav-link">Новый челлендж</router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const hasActive = ref(false)
const router = useRouter()
const API = 'http://127.0.0.1:8000'

async function checkActive() {
  try {
    const res = await axios.get(`${API}/challenges/active/`)
    hasActive.value = !!res.data.id
  } catch (err) {
    hasActive.value = false
  }
}

async function goToActive() {
  const res = await axios.get(`${API}/challenges/active/`)
  router.push(`/challenge/${res.data.id}`)
}

onMounted(checkActive)
</script>

<style scoped lang="scss">
@import "../styles/components/nav-bar.scss";
</style>