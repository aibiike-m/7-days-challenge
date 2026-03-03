<template>
  <transition name="modal-fade">
    <div v-if="isOpen" class="modal-overlay" @click="close">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ t('modal.goal_label') }}</h2>
          <button class="close-btn" @click="close">×</button>
        </div>
        
        <form @submit.prevent="submit">
          <div class="form-group">
            <textarea 
              id="goal"
              v-model="goal" 
              autofocus
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
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: $spacing-responsive-sm;
  
  @include md {
    padding: $spacing-responsive-md;
  }
}

.modal-content {
  background: $white;
  border-radius: $radius-md;
  padding: $spacing-responsive-md;
  max-width: 500px;
  width: 100%;
  box-shadow: $shadow-md;

  @include md {
    padding: $spacing-responsive-xl;
    border-radius: $radius-lg;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-responsive-sm;

  @include md {
    margin-bottom: $spacing-responsive-lg;
  }

  h2 {
    font-size: $font-size-responsive-lg;
    margin: 0;
    color: $text-primary;
    
    @include md {
      font-size: $font-size-responsive-xl;
    }
  }
}

.close-btn {
  background: none;
  border: none;
  font-size: $font-size-2xl;
  color: $text-muted;
  cursor: pointer;
  line-height: 1;
  padding: $spacing-responsive-xs;
  
  @include md {
    font-size: 28px;
  }
  
  &:hover { color: $text-primary; }
}

.form-group {
  margin-bottom: $spacing-responsive-sm;
  
  @include md {
    margin-bottom: $spacing-responsive-lg;
  }

  label {
    display: block;
    font-size: $font-size-xs;
    font-weight: $font-weight-semibold;
    margin-bottom: $spacing-responsive-xs;
    color: $text-secondary;
    
    @include md {
      font-size: $font-size-sm;
      margin-bottom: $spacing-responsive-sm;
    }
  }

  textarea {
    width: 100%;
    padding: $spacing-responsive-sm;
    border: 1px solid $border;
    border-radius: $radius-md;
    font-family: inherit;
    font-size: $font-size-responsive-sm;
    resize: none;
    overflow-y: auto;
    transition: all 0.2s;
    
    @include md {
      padding: $spacing-responsive-md;
      font-size: $font-size-responsive-base;
    }

    &:focus {
      outline: none;
      border-color: $primary;
      box-shadow: 0 0 0 3px rgba($primary, 0.1);
    }
  }
}

.char-counter {
  margin-top: $spacing-responsive-xs;
  text-align: right;
  font-size: $font-size-xs;
  color: $text-muted;
  
  @include md {
    margin-top: $spacing-responsive-sm;
  }
  
  &.valid { color: $success; }
}

.modal-actions {
  display: flex;
  gap: $spacing-responsive-sm;
  justify-content: flex-end;
  
  @include md {
    gap: $spacing-responsive-md;
  }
}

.btn {
  width: 100%;
  padding: $spacing-responsive-sm $spacing-responsive-md;
  border-radius: $radius-md;
  font-weight: $font-weight-semibold;
  font-size: $font-size-responsive-sm;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  
  @include md {
    width: auto;
    padding: $spacing-responsive-sm $spacing-responsive-lg;
  }

  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.btn-primary {
  background: $primary;
  color: $white;
  &:hover:not(:disabled) { background: $primary-hover; }
}

.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.3s ease;
  .modal-content { transition: transform 0.3s ease; }
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
  .modal-content { transform: translateY(-20px); }
}
</style>