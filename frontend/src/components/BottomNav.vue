<template>
  <nav class="bottom-nav">
    <router-link to="/today" class="nav-item">
      <span class="icon">✓</span>
      <span class="label">{{ $t('nav.today') }}</span>
    </router-link>

    <router-link to="/calendar" class="nav-item">
      <span class="icon">📅</span>
      <span class="label">{{ $t('nav.calendar') }}</span>
    </router-link>

    <router-link to="/profile" class="nav-item">
      <span class="icon">👤</span>
      <span class="label">{{ $t('nav.profile') }}</span>
    </router-link>
  </nav>
</template>

<style scoped lang="scss">
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: $bg-card;
  border-top: 1px solid $border;
  display: flex;
  justify-content: space-around;
  padding: $spacing-responsive-sm 0;
  z-index: 100;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
  
  @include md {
    display: none;
  }
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: $spacing-responsive-sm $spacing-responsive-md;
  color: $text-muted;
  text-decoration: none;
  transition: all 0.15s ease;
  border-radius: $radius-md;
  min-width: 70px;
  
  @include sm {
    min-width: 80px;
  }
  
  .icon {
    font-size: 22px;
    filter: grayscale(100%);
    opacity: 0.6;
    transition: all 0.15s ease;
    
    @include sm {
      font-size: $font-size-2xl;
    }
  }
  
  .label {
    font-size: $font-size-xs;
    font-weight: $font-weight-medium;
  }
  
  &:hover {
    color: $primary;
    background: rgba($primary, 0.05);
    
    .icon {
      filter: grayscale(0%);
      opacity: 1;
    }
  }
  
  &.router-link-active {
    color: $primary;
    
    .icon {
      filter: grayscale(0%);
      opacity: 1;
      transform: scale(1.1);
    }
    
    .label {
      font-weight: $font-weight-semibold;
    }
  }
}
</style>