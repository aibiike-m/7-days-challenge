<template>
  <transition name="modal-fade">
    <div v-if="isOpen" class="modal-overlay" @click="close">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ t('today.new_challenge') }}</h2>
          <button class="close-btn" @click="close">×</button>
        </div>
        
        <form @submit.prevent="submit">
          <div class="form-group">
            <label for="goal">{{ t('modal.goal_label') }}</label>
            <textarea 
              id="goal"
              v-model="goal" 
              :placeholder="t('modal.goal_placeholder')"
              :maxlength="MAX_GOAL_LENGTH"
              rows="4"
              required
              :disabled="loading"
            ></textarea>
            <div 
              class="char-counter" 
              :class="{ valid: goal.trim().length >= MIN_GOAL_LENGTH }"
            >
              {{ goal.trim().length }} / {{ MIN_GOAL_LENGTH }}
            </div>
          </div>
          
          <div class="modal-actions">
            <button 
              type="submit" 
              class="btn btn-primary" 
              :disabled="loading || !isGoalValid"
            >
              <span v-if="loading" class="loading-spinner">⏳</span>
              {{ loading ? t('modal.creating') : t('modal.create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import api from '@/services/api/index.js'
import { MIN_GOAL_LENGTH, MAX_GOAL_LENGTH } from '@/constants/index'

const { t, locale } = useI18n()
const router = useRouter()
const notify = useNotification()
const emit = defineEmits(['close', 'created'])

const goal = ref('')
const loading = ref(false)

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const isGoalValid = computed(() => {
  const length = goal.value.trim().length
  return length >= MIN_GOAL_LENGTH && length <= MAX_GOAL_LENGTH
})

watch(() => props.isOpen, (newVal) => {
  if (!newVal) {
    goal.value = ''
  }
})

const close = () => {
  if (!loading.value) {
    emit('close')
  }
}

const submit = async () => {  
  if (!isGoalValid.value) {
    notify.warning('errors.validation')
    return
  }
  
  loading.value = true
  
  try {
    const response = await api.post('challenges/', {
      goal: goal.value.trim(),
      language: locale.value
    })
    
    notify.success('success.challenge_created')
    
    emit('created', response.data)
    emit('close')
    goal.value = ''
    
    setTimeout(() => {
      router.go(0) 
    }, 2000)
    
  } catch (err) {
    if (err.response?.status === 401) {
      notify.error('errors.unauthorized')
    } else if (!err.response) {
      notify.error('errors.network')
    } else {
      notify.error('errors.challenge_create')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Challenge creation error:', err)
    }
    
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: $spacing-md;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-xl;
  width: 100%;
  max-width: 550px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-xl;
  
  h2 {
    margin: 0;
    font-size: $font-size-xl;
    color: $text-primary;
  }
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: $radius-full;
  border: none;
  background: $bg-secondary;
  color: $text-secondary;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: $border-hover;
    color: $text-primary;
  }
}

.form-group {
  margin-bottom: $spacing-xl;
  
  label {
    display: block;
    font-weight: $font-weight-semibold;
    color: $text-primary;
    margin-bottom: $spacing-sm;
    font-size: $font-size-base;
  }
  
  textarea {
    width: 100%;
    padding: $spacing-md;
    border: 2px solid $border;
    border-radius: $radius-md;
    font-family: $font-family;
    font-size: $font-size-base;
    resize: vertical;
    transition: all 0.15s ease;
    
    &:focus {
      outline: none;
      border-color: $primary;
      box-shadow: 0 0 0 3px rgba($primary, 0.1);
    }
    
    &::placeholder {
      color: $text-muted;
    }
    
    &:disabled {
      background: $bg-secondary;
      cursor: not-allowed;
    }
  }
}

.char-counter {
  margin-top: 6px;
  text-align: right;
  font-size: $font-size-sm;       
  font-weight: 500;
  transition: color 0.25s ease;  
  color: $text-secondary;      
  
  &.valid {
    color: $primary-hover;     
  }
}

.modal-actions {
  display: flex;
  gap: $spacing-md;
  justify-content: flex-end;
}

.btn {
  padding: $spacing-sm $spacing-lg;
  border: none;
  border-radius: $radius-md;
  font-family: $font-family;
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  transition: all 0.25s ease;
  display: inline-flex;
  align-items: center;
  gap: $spacing-sm;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-primary {
  background: $primary;
  color: $white;
  
  &:hover:not(:disabled) {
    background: $primary-hover;
    transform: translateY(-1px);
    box-shadow: $shadow-md;
  }
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>