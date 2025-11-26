<template>
  <header class="app-header">
    <div class="header-content">
      <h1 class="logo">7 Days Challenge</h1>
      
      <nav class="desktop-nav">
        <router-link to="/today" class="nav-link">Сегодня</router-link>
        <router-link to="/calendar" class="nav-link">Календарь</router-link>
        <router-link to="/profile" class="nav-link">Профиль</router-link>
      </nav>
      
      <div class="header-actions">
        <button class="btn-icon" @click="toggleTheme" title="Переключить тему">
          🌙
        </button>
        <button class="btn-icon" @click="toggleLanguage" title="Язык">
          🌐
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
const toggleTheme = () => {
  console.log('Toggle theme')
}

const toggleLanguage = () => {
  console.log('Toggle language')
}
</script>

<style scoped lang="scss">
.app-header {
  position: sticky;
  top: 0;
  background: $bg-card;       
  border-bottom: 1px solid $border;
  z-index: 100;
  box-shadow: $shadow-sm;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-lg;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-xl;
}

.logo {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: $primary;
  margin: 0;
  flex-shrink: 0;
}

.desktop-nav {
  display: none; 
  gap: $spacing-sm;
  
  @media (min-width: 768px) {
    display: flex; 
  }
}

.nav-link {
  padding: $spacing-sm $spacing-md;
  color: $text-secondary;
  text-decoration: none;
  font-weight: $font-weight-medium;
  font-size: $font-size-base; 
  border-radius: $radius-md;
  transition: all 0.15s ease;
  
  &:hover {
    color: $primary;
    background: rgba(91, 159, 216, 0.1);
  }
  
  &.router-link-active {
    color: $primary;
    background: rgba(91, 159, 216, 0.1);
    font-weight: $font-weight-semibold;
  }
}

.header-actions {
  display: none; 
  gap: $spacing-sm;
  
  @media (min-width: 768px) {
    display: flex; 
  }
}

.btn-icon {
  width: 40px;
  height: 40px;
  padding: 0;
  border-radius: $radius-full;
  border: none;
  font-size: 20px;
  background: $bg-secondary;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: $border-hover;
}
</style>