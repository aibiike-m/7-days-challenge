<template>
  <header class="app-header">
    <div class="header-content">
      <h1 class="logo">{{ APP_NAME }}</h1>
      
      <nav class="desktop-nav">
        <router-link to="/today" class="nav-link">{{ $t('nav.today') }}</router-link>
        <router-link to="/calendar" class="nav-link">{{ $t('nav.calendar') }}</router-link>
        <router-link to="/profile" class="nav-link">{{ $t('nav.profile') }}</router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { APP_NAME } from '@/constants/index'
</script>

<style scoped lang="scss">
.app-header {
  position: sticky;
  top: 0;
  background: $bg-card;       
  border-bottom: 1px solid $border;
  z-index: 100;
  box-shadow: $shadow-sm;
  display: none;
  
  @include md {
    display: block;
  }
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-responsive-md;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-responsive-lg;
  
  @include md {
    padding: $spacing-responsive-lg;
  }
}

.logo {
  font-size: $font-size-responsive-xl;
  font-weight: $font-weight-bold;
  color: $primary;
  margin: 0;
  flex-shrink: 0;
}

.desktop-nav {
  display: flex;
  gap: $spacing-responsive-sm;
}

.nav-link {
  padding: $spacing-responsive-sm $spacing-responsive-md;
  color: $text-secondary;
  text-decoration: none;
  font-weight: $font-weight-medium;
  font-size: $font-size-responsive-base;
  border-radius: $radius-md;
  transition: all 0.15s ease;
  
  &:hover {
    color: $primary;
    background: rgba($primary, 0.1);
  }
  
  &.router-link-active {
    color: $primary;
    background: rgba($primary, 0.1);
    font-weight: $font-weight-semibold;
  }
}
</style>