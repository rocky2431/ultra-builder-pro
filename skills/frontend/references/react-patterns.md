# React Patterns Reference

React 18+ best practices and patterns for production applications.

---

## Component Patterns

### Functional Components (Standard)

```tsx
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({
  variant,
  size = 'md',
  disabled = false,
  children,
  onClick,
}: ButtonProps) {
  return (
    <button
      className={cn(styles.button, styles[variant], styles[size])}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### Compound Components

```tsx
// Context for shared state
const TabsContext = createContext<TabsContextValue | null>(null);

function Tabs({ children, defaultValue }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultValue);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

Tabs.List = function TabsList({ children }: { children: React.ReactNode }) {
  return <div role="tablist">{children}</div>;
};

Tabs.Tab = function Tab({ value, children }: TabProps) {
  const { activeTab, setActiveTab } = useContext(TabsContext)!;
  return (
    <button
      role="tab"
      aria-selected={activeTab === value}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  );
};

Tabs.Panel = function TabPanel({ value, children }: TabPanelProps) {
  const { activeTab } = useContext(TabsContext)!;
  if (activeTab !== value) return null;
  return <div role="tabpanel">{children}</div>;
};

// Usage
<Tabs defaultValue="tab1">
  <Tabs.List>
    <Tabs.Tab value="tab1">Tab 1</Tabs.Tab>
    <Tabs.Tab value="tab2">Tab 2</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="tab1">Content 1</Tabs.Panel>
  <Tabs.Panel value="tab2">Content 2</Tabs.Panel>
</Tabs>
```

---

## Hooks Patterns

### Custom Data Fetching Hook

```tsx
interface UseQueryResult<T> {
  data: T | undefined;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

function useQuery<T>(
  key: string,
  fetcher: () => Promise<T>
): UseQueryResult<T> {
  const [data, setData] = useState<T>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, [fetcher]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}
```

### useDebounce

```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Usage
const debouncedSearch = useDebounce(searchTerm, 300);
```

### useLocalStorage

```tsx
function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      setStoredValue((prev) => {
        const valueToStore = value instanceof Function ? value(prev) : value;
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
        return valueToStore;
      });
    },
    [key]
  );

  return [storedValue, setValue];
}
```

---

## Performance Patterns

### React.memo with Custom Comparison

```tsx
interface ListItemProps {
  item: { id: string; name: string; updatedAt: Date };
  onSelect: (id: string) => void;
}

const ListItem = memo(
  function ListItem({ item, onSelect }: ListItemProps) {
    return (
      <div onClick={() => onSelect(item.id)}>
        {item.name}
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Only re-render if item data changed
    return (
      prevProps.item.id === nextProps.item.id &&
      prevProps.item.updatedAt === nextProps.item.updatedAt
    );
  }
);
```

### useMemo for Expensive Calculations

```tsx
function DataTable({ data, filters }: DataTableProps) {
  // Memoize filtered and sorted data
  const processedData = useMemo(() => {
    return data
      .filter((item) => matchesFilters(item, filters))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [data, filters]);

  return (
    <table>
      {processedData.map((item) => (
        <TableRow key={item.id} item={item} />
      ))}
    </table>
  );
}
```

### useCallback for Stable References

```tsx
function ParentComponent() {
  const [items, setItems] = useState<Item[]>([]);

  // Stable reference - won't cause child re-renders
  const handleDelete = useCallback((id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []);

  return (
    <ItemList items={items} onDelete={handleDelete} />
  );
}
```

### Virtualized Lists

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // estimated row height
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            {items[virtualRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## State Management Patterns

### Context + useReducer

```tsx
interface State {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

type Action =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_ERROR'; payload: string }
  | { type: 'LOGOUT' };

function authReducer(state: State, action: Action): State {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true, error: null };
    case 'LOGIN_SUCCESS':
      return { ...state, isLoading: false, user: action.payload };
    case 'LOGIN_ERROR':
      return { ...state, isLoading: false, error: action.payload };
    case 'LOGOUT':
      return { ...state, user: null };
    default:
      return state;
  }
}

const AuthContext = createContext<{
  state: State;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isLoading: false,
    error: null,
  });

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

---

## Error Handling Patterns

### Error Boundary

```tsx
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<
  { children: ReactNode; fallback: ReactNode },
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Send to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorFallback />}>
  <App />
</ErrorBoundary>
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Props drilling | Passing props through many levels | Use Context or state management |
| Inline object/array props | Creates new reference each render | Move to useMemo or outside component |
| useEffect for derived state | Unnecessary re-renders | Use useMemo instead |
| Mutating state directly | React won't detect changes | Always create new objects/arrays |
| Missing dependency array | Stale closures or infinite loops | Include all dependencies |
| Index as key | Incorrect reconciliation | Use stable unique IDs |
