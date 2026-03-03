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
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: $spacing-responsive-md;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: $white;
  border-radius: $radius-lg;
  padding: $spacing-lg;
  max-width: 440px;
  width: 100%;
  box-shadow: $shadow-md;
  
  @include md {
    padding: $spacing-xl;
  }
}

.modal-title {
  font-size: $font-size-responsive-lg;
  font-weight: $font-weight-semibold;
  color: $text-primary;
  margin: 0 0 $spacing-md 0;

  @include md {
    font-size: $font-size-responsive-xl;
  }
}

.modal-message {
  font-size: $font-size-responsive-sm;
  color: $text-secondary;
  line-height: 1.6;
  margin-bottom: $spacing-lg;
}

.modal-actions {
  display: flex;
  gap: $spacing-sm;
  flex-direction: column-reverse;

  @include sm {
    flex-direction: row;
    justify-content: flex-end;
  }
}

.btn-cancel,
.btn-confirm {
  padding: $spacing-sm $spacing-lg;
  border-radius: $radius-md;
  font-weight: $font-weight-semibold;
  cursor: pointer;
  font-size: $font-size-responsive-sm;
  border: none;
  transition: all 0.2s ease;
  width: 100%;

  @include sm {
    width: auto;
    min-width: 100px;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-cancel {
  background: $bg-secondary;
  color: $text-secondary;
  &:hover:not(:disabled) { background: $border-hover; }
}

.btn-confirm {
  background: $primary;
  color: $white;
  
  &.danger {
    background: $danger;
    &:hover:not(:disabled) { background: $danger-dark; }
  }

  &:hover:not(:disabled) {
    background: $primary-hover;
    transform: translateY(-1px);
  }
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
  .modal-content { transition: transform 0.3s ease; }
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  .modal-content { transform: scale(0.9) translateY(20px); }
}
</style>