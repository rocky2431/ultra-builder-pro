# Vue 3 Patterns Reference

Vue 3 Composition API best practices and patterns.

---

## Component Patterns

### Script Setup (Recommended)

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

// Props with defaults
interface Props {
  title: string;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  disabled: false,
});

// Emits with validation
const emit = defineEmits<{
  click: [event: MouseEvent];
  update: [value: string];
}>();

// Reactive state
const count = ref(0);

// Computed
const doubleCount = computed(() => count.value * 2);

// Methods
function handleClick(event: MouseEvent) {
  count.value++;
  emit('click', event);
}

// Lifecycle
onMounted(() => {
  console.log('Component mounted');
});
</script>

<template>
  <button
    :class="[$style.button, $style[variant]]"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot>{{ title }}</slot>
  </button>
</template>

<style module>
.button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
}
.primary {
  background: var(--color-primary);
}
.secondary {
  background: var(--color-secondary);
}
</style>
```

### Compound Components with Provide/Inject

```vue
<!-- Tabs.vue -->
<script setup lang="ts">
import { provide, ref } from 'vue';

const props = defineProps<{ defaultValue: string }>();

const activeTab = ref(props.defaultValue);

provide('tabs', {
  activeTab,
  setActiveTab: (value: string) => {
    activeTab.value = value;
  },
});
</script>

<template>
  <div class="tabs">
    <slot />
  </div>
</template>

<!-- TabsList.vue -->
<template>
  <div role="tablist" class="tabs-list">
    <slot />
  </div>
</template>

<!-- Tab.vue -->
<script setup lang="ts">
import { inject } from 'vue';

const props = defineProps<{ value: string }>();
const { activeTab, setActiveTab } = inject('tabs')!;
</script>

<template>
  <button
    role="tab"
    :aria-selected="activeTab === value"
    @click="setActiveTab(value)"
  >
    <slot />
  </button>
</template>

<!-- TabPanel.vue -->
<script setup lang="ts">
import { inject } from 'vue';

const props = defineProps<{ value: string }>();
const { activeTab } = inject('tabs')!;
</script>

<template>
  <div v-if="activeTab === value" role="tabpanel">
    <slot />
  </div>
</template>
```

---

## Composables (Custom Hooks)

### useFetch

```ts
import { ref, watchEffect, type Ref } from 'vue';

interface UseFetchResult<T> {
  data: Ref<T | null>;
  isLoading: Ref<boolean>;
  error: Ref<Error | null>;
  refetch: () => Promise<void>;
}

export function useFetch<T>(url: Ref<string> | string): UseFetchResult<T> {
  const data = ref<T | null>(null) as Ref<T | null>;
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  async function fetchData() {
    isLoading.value = true;
    error.value = null;

    try {
      const urlValue = typeof url === 'string' ? url : url.value;
      const response = await fetch(urlValue);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      data.value = await response.json();
    } catch (e) {
      error.value = e instanceof Error ? e : new Error('Unknown error');
    } finally {
      isLoading.value = false;
    }
  }

  watchEffect(() => {
    fetchData();
  });

  return { data, isLoading, error, refetch: fetchData };
}
```

### useDebounce

```ts
import { ref, watch, type Ref } from 'vue';

export function useDebounce<T>(value: Ref<T>, delay: number): Ref<T> {
  const debouncedValue = ref(value.value) as Ref<T>;

  let timeout: ReturnType<typeof setTimeout>;

  watch(value, (newValue) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      debouncedValue.value = newValue;
    }, delay);
  });

  return debouncedValue;
}
```

### useLocalStorage

```ts
import { ref, watch, type Ref } from 'vue';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): Ref<T> {
  const storedValue = ref<T>(initialValue) as Ref<T>;

  // Initialize from localStorage
  if (typeof window !== 'undefined') {
    const item = localStorage.getItem(key);
    if (item) {
      try {
        storedValue.value = JSON.parse(item);
      } catch {
        storedValue.value = initialValue;
      }
    }
  }

  // Sync to localStorage
  watch(
    storedValue,
    (newValue) => {
      localStorage.setItem(key, JSON.stringify(newValue));
    },
    { deep: true }
  );

  return storedValue;
}
```

### useEventListener

```ts
import { onMounted, onUnmounted } from 'vue';

export function useEventListener<K extends keyof WindowEventMap>(
  target: Window | HTMLElement,
  event: K,
  handler: (event: WindowEventMap[K]) => void
) {
  onMounted(() => {
    target.addEventListener(event, handler as EventListener);
  });

  onUnmounted(() => {
    target.removeEventListener(event, handler as EventListener);
  });
}
```

---

## Performance Patterns

### shallowRef for Large Objects

```ts
import { shallowRef, triggerRef } from 'vue';

// For large arrays/objects where you control mutations
const items = shallowRef<Item[]>([]);

function addItem(item: Item) {
  items.value.push(item);
  triggerRef(items); // Manually trigger update
}
```

### v-once for Static Content

```vue
<template>
  <!-- Rendered once, never updated -->
  <header v-once>
    <h1>{{ staticTitle }}</h1>
    <nav>...</nav>
  </header>

  <!-- Dynamic content -->
  <main>{{ dynamicContent }}</main>
</template>
```

### v-memo for Expensive Templates

```vue
<template>
  <div v-for="item in list" :key="item.id" v-memo="[item.id, item.selected]">
    <!-- Only re-render when id or selected changes -->
    <ExpensiveComponent :item="item" />
  </div>
</template>
```

### Async Components

```ts
import { defineAsyncComponent } from 'vue';

const AsyncModal = defineAsyncComponent({
  loader: () => import('./Modal.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,
  timeout: 3000,
});
```

---

## State Management with Pinia

### Store Definition

```ts
import { defineStore } from 'pinia';

interface User {
  id: string;
  name: string;
  email: string;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    isLoading: false,
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    userName: (state) => state.user?.name ?? 'Guest',
  },

  actions: {
    async login(credentials: { email: string; password: string }) {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await api.login(credentials);
        this.user = response.user;
      } catch (e) {
        this.error = e instanceof Error ? e.message : 'Login failed';
        throw e;
      } finally {
        this.isLoading = false;
      }
    },

    logout() {
      this.user = null;
    },
  },
});
```

### Setup Store (Composition API Style)

```ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0);
  const doubleCount = computed(() => count.value * 2);

  function increment() {
    count.value++;
  }

  function decrement() {
    count.value--;
  }

  return { count, doubleCount, increment, decrement };
});
```

---

## Template Patterns

### Slot Patterns

```vue
<!-- BaseCard.vue -->
<template>
  <div class="card">
    <header v-if="$slots.header" class="card-header">
      <slot name="header" />
    </header>

    <div class="card-body">
      <slot />
    </div>

    <footer v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </footer>
  </div>
</template>

<!-- Scoped Slot -->
<template>
  <ul>
    <li v-for="item in items" :key="item.id">
      <slot name="item" :item="item" :index="index">
        {{ item.name }}
      </slot>
    </li>
  </ul>
</template>

<!-- Usage -->
<ItemList :items="items">
  <template #item="{ item, index }">
    <span>{{ index + 1 }}. {{ item.name }}</span>
  </template>
</ItemList>
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Options API in new code | Less type-safe, harder to compose | Use Composition API with `<script setup>` |
| Mutating props | Unexpected behavior | Emit events to parent |
| Watchers for derived data | Unnecessary complexity | Use computed properties |
| Deep watchers on large objects | Performance issues | Use shallowRef or specific paths |
| this in setup() | Undefined in setup | Use ref/reactive directly |
| Missing key in v-for | Incorrect updates | Always use unique keys |
