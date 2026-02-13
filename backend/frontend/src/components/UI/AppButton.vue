<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <span v-if="loading" class="spinner"></span>
    <slot v-else></slot>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'button'
  },
  variant: {
    type: String,
    default: 'primary', // primary, secondary, danger, success
    validator: (value) => ['primary', 'secondary', 'danger', 'success', 'outline'].includes(value)
  },
  size: {
    type: String,
    default: 'md', // sm, md, lg
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  disabled: Boolean,
  loading: Boolean,
  fullWidth: Boolean
})

const emit = defineEmits(['click'])

const buttonClasses = computed(() => {
  const classes = ['btn']
  
  classes.push(`btn-${props.variant}`)
  classes.push(`btn-${props.size}`)
  
  if (props.fullWidth) classes.push('btn-full')
  if (props.disabled) classes.push('btn-disabled')
  if (props.loading) classes.push('btn-loading')
  
  return classes.join(' ')
})

const handleClick = (e) => {
  if (!props.disabled && !props.loading) {
    emit('click', e)
  }
}
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

/* Sizes */
.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-md {
  padding: 0.625rem 1.25rem;
  font-size: 1rem;
}

.btn-lg {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
}

/* Variants */
.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(.btn-disabled) {
  background: #5568d3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(.btn-disabled) {
  background: #5a6268;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(.btn-disabled) {
  background: #c0392b;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover:not(.btn-disabled) {
  background: #229954;
}

.btn-outline {
  background: transparent;
  border: 2px solid #667eea;
  color: #667eea;
}

.btn-outline:hover:not(.btn-disabled) {
  background: #667eea;
  color: white;
}

/* States */
.btn-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-full {
  width: 100%;
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>