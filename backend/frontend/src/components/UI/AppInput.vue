<template>
  <div class="input-wrapper">
    <label v-if="label" :for="id" class="input-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <input
      v-if="type !== 'textarea'"
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :min="min"
      :max="max"
      :step="step"
      :class="inputClasses"
      @input="handleInput"
      @blur="handleBlur"
    />
    
    <textarea
      v-else
      :id="id"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :rows="rows"
      :class="inputClasses"
      @input="handleInput"
      @blur="handleBlur"
    ></textarea>
    
    <span v-if="error" class="input-error">{{ error }}</span>
    <span v-if="hint && !error" class="input-hint">{{ hint }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  type: {
    type: String,
    default: 'text'
  },
  label: String,
  placeholder: String,
  error: String,
  hint: String,
  disabled: Boolean,
  required: Boolean,
  id: String,
  min: [String, Number],
  max: [String, Number],
  step: [String, Number],
  rows: {
    type: Number,
    default: 4
  }
})

const emit = defineEmits(['update:modelValue', 'blur'])

const inputClasses = computed(() => {
  const classes = ['input']
  if (props.error) classes.push('input-error-state')
  if (props.disabled) classes.push('input-disabled')
  return classes.join(' ')
})

const handleInput = (e) => {
  let value = e.target.value
  
  if (props.type === 'number') {
    value = value === '' ? '' : Number(value)
  }
  
  emit('update:modelValue', value)
}

const handleBlur = (e) => {
  emit('blur', e)
}
</script>

<style scoped>
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #e74c3c;
}

.input,
textarea {
  width: 100%;
  padding: 0.625rem 0.875rem;
  font-size: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  transition: all 0.2s;
  font-family: inherit;
}

.input:focus,
textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-error-state {
  border-color: #e74c3c;
}

.input-error-state:focus {
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.input-disabled {
  background: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.6;
}

.input-error {
  font-size: 0.875rem;
  color: #e74c3c;
}

.input-hint {
  font-size: 0.875rem;
  color: #6b7280;
}

textarea {
  resize: vertical;
  min-height: 80px;
}
</style>