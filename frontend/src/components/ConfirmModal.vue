<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-content" @click.stop>
          <h3 class="modal-title">{{ title }}</h3>
          
          <p v-if="message" class="modal-message">{{ message }}</p>

          <div v-if="$slots.extra" class="modal-extra">
            <slot name="extra" />
          </div>

          <div class="modal-actions">
            <button 
              class="btn-cancel" 
              @click="closeModal"
              :disabled="isProcessing"
            >
              {{ cancelText || $t('common.cancel') }}
            </button>
            <button 
              :class="['btn-confirm', { 'danger': dangerMode }]"
              @click="handleConfirm"
              :disabled="isProcessing"
            >
              {{ isProcessing ? (processingText || $t('common.loading')) : (confirmText || $t('common.confirm')) }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    default: ''
  },
  confirmText: {
    type: String,
    default: ''
  },
  cancelText: {
    type: String,
    default: ''
  },
  processingText: {
    type: String,
    default: ''
  },
  dangerMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'confirm'])

const isProcessing = ref(false)

function closeModal() {
  if (!isProcessing.value) {
    emit('close')
  }
}

function handleOverlayClick() {
  closeModal()
}

function handleConfirm() {
  isProcessing.value = true
  const done = () => { isProcessing.value = false }
  emit('confirm', done)
}
</script>

<style scoped lang="scss">
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
}

.modal-content {
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-lg;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
  margin: 0 0 $spacing-lg 0;

  @media (min-width: 768px) {
    font-size: 20px;
  }
}

.modal-message {
  font-size: 14px;
  color: $text-secondary;
  line-height: 1.6;
  margin: 0 0 $spacing-md 0;
}

.modal-extra {
  margin-bottom: $spacing-md;

  input {
    padding: $spacing-sm $spacing-md;
    border: 1px solid $border;
    border-radius: $radius-md;
    font-size: 1rem;
    width: 100%;
    box-sizing: border-box;
    transition: all 0.2s ease;

    &:focus {
      outline: none;
      border-color: $danger;
      box-shadow: 0 0 0 3px rgba($danger, 0.15);
    }
  }
}

.modal-actions {
  display: flex;
  gap: $spacing-sm;
  justify-content: flex-end;
  margin-top: $spacing-lg;
}

.btn-cancel,
.btn-confirm {
  padding: $spacing-sm $spacing-lg;
  border-radius: $radius-md;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  border: none;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-cancel {
  background: $bg-secondary;
  color: $text-secondary;

  &:hover:not(:disabled) {
    background: $border-hover;
  }
}

.btn-confirm {
  background: $primary;
  color: $white;

  &:hover:not(:disabled) {
    background: $primary-hover;
  }

  &.danger {
    background: $danger;

    &:hover:not(:disabled) {
      background: $danger-dark;
    }
  }

  &:active:not(:disabled) {
    transform: translateY(1px);
  }
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
  
  .modal-content {
    transition: transform 0.2s ease;
  }
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  
  .modal-content {
    transform: scale(0.95);
  }
}
</style>