<template>
  <span :class="['status-badge', badgeClass]">
    {{ statusLabel }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const statusConfig = {
  pending: { label: 'Ожидает', class: 'status-pending' },
  accepted: { label: 'Принят', class: 'status-accepted' },
  in_progress: { label: 'В работе', class: 'status-in_progress' },
  done: { label: 'Готов', class: 'status-done' },
  delivered: { label: 'Сдан', class: 'status-delivered' },
  // Keep some legacy/fallback just in case
  new: { label: 'Новый', class: 'status-pending' },
  completed: { label: 'Завершен', class: 'status-done' },
  cancelled: { label: 'Отменен', class: 'status-cancelled' }
}

const statusLabel = computed(() => {
  return statusConfig[props.status]?.label || props.status
})

const badgeClass = computed(() => {
  return statusConfig[props.status]?.class || 'status-default'
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.25;
  white-space: nowrap;
}

.status-pending { /* Warning/Amber */
  background-color: #fef3c7;
  color: #92400e;
}

.status-accepted { /* Info/Blue */
  background-color: #dbeafe;
  color: #1e40af;
}

.status-in_progress { /* Primary/Indigo */
  background-color: #e0e7ff;
  color: #3730a3;
}

.status-done { /* Success/Green */
  background-color: #d1fae5;
  color: #065f46;
}

.status-delivered { /* Complete/Green or Darker */
  background-color: #dcfce7;
  color: #166534;
}

.status-cancelled { /* Danger/Red */
  background-color: #fee2e2;
  color: #991b1b;
}

.status-default {
  background-color: #f3f4f6;
  color: #374151;
}
</style>
