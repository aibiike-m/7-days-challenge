<template>
  <NavBar />
  <router-view />
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>

<style>
body, #app {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>