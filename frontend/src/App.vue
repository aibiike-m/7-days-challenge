<template>
  <NavBar />

  <router-view />

  <div class="global-bg"></div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>

<style>
.global-bg {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: -1;
}

#app {
  min-height: 100vh;
  position: relative;
}
</style>