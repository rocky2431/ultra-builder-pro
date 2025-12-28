<script setup lang="ts">
/**
 * ComponentName - Brief description of what this component does.
 *
 * @example
 * ```vue
 * <ComponentName variant="primary" size="md">
 *   Content here
 * </ComponentName>
 * ```
 */

import { computed } from 'vue';

// =============================================================================
// Props
// =============================================================================

interface Props {
  /** Visual variant */
  variant?: 'default' | 'primary' | 'secondary';
  /** Size preset */
  size?: 'sm' | 'md' | 'lg';
  /** Disabled state */
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  disabled: false,
});

// =============================================================================
// Emits
// =============================================================================

const emit = defineEmits<{
  /** Emitted when component is clicked */
  click: [event: MouseEvent];
  /** Emitted when value changes */
  'update:modelValue': [value: string];
}>();

// =============================================================================
// Computed Styles
// =============================================================================

const baseStyles = 'inline-flex items-center justify-center rounded-md';

const variantStyles = computed(() => {
  const styles = {
    default: 'bg-gray-100 text-gray-900',
    primary: 'bg-blue-600 text-white',
    secondary: 'bg-gray-600 text-white',
  };
  return styles[props.variant];
});

const sizeStyles = computed(() => {
  const styles = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  return styles[props.size];
});

const componentClasses = computed(() => [
  baseStyles,
  variantStyles.value,
  sizeStyles.value,
  props.disabled && 'opacity-50 cursor-not-allowed',
]);

// =============================================================================
// Methods
// =============================================================================

function handleClick(event: MouseEvent) {
  if (!props.disabled) {
    emit('click', event);
  }
}
</script>

<template>
  <div
    role="region"
    :class="componentClasses"
    :aria-disabled="disabled"
    @click="handleClick"
  >
    <!-- Header Slot -->
    <div v-if="$slots.header" class="component-name-header">
      <slot name="header" />
    </div>

    <!-- Default Slot -->
    <div class="component-name-body">
      <slot />
    </div>

    <!-- Footer Slot -->
    <div v-if="$slots.footer" class="component-name-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<style scoped>
.component-name-header {
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.component-name-body {
  padding: 1rem 0;
}

.component-name-footer {
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color, #e5e7eb);
}
</style>
