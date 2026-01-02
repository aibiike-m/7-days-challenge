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
  padding: $spacing-sm 0;
  z-index: 100;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05); 
  
  @media (min-width: 768px) {
    display: none;
  }
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: $spacing-sm $spacing-md;
  color: $text-muted;
  text-decoration: none;
  transition: all 0.15s ease;
  border-radius: $radius-md;
  min-width: 80px;
}

.nav-item .icon {
  font-size: 24px;
  filter: grayscale(100%);
  opacity: 0.6;
  transition: all 0.15s ease;
}

.nav-item .label {
  font-size: $font-size-xs;
  font-weight: $font-weight-medium;
}

.nav-item:hover {
  color: $primary;
  background: rgba(91, 159, 216, 0.05);
}

.nav-item:hover .icon {
  filter: grayscale(0%);
  opacity: 1;
}

.nav-item.router-link-active {
  color: $primary;
}

.nav-item.router-link-active .icon {
  filter: grayscale(0%);
  opacity: 1;
  transform: scale(1.1);
}

.nav-item.router-link-active .label {
  font-weight: $font-weight-semibold;
}
</style>