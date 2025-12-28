# Performance Optimization Reference

Core Web Vitals optimization guide for frontend applications.

---

## Core Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5s - 4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | 200ms - 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1 - 0.25 | > 0.25 |

---

## LCP Optimization

### Common LCP Elements

- Hero images
- Large text blocks
- Video poster images
- Background images (via CSS)

### Optimization Strategies

#### 1. Optimize Images

```tsx
// Next.js - use next/image
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority  // Preload LCP image
  sizes="100vw"
  placeholder="blur"
  blurDataURL="..."
/>

// React - responsive images
<picture>
  <source
    srcSet="/hero-mobile.webp"
    media="(max-width: 768px)"
    type="image/webp"
  />
  <source
    srcSet="/hero-desktop.webp"
    type="image/webp"
  />
  <img
    src="/hero.jpg"
    alt="Hero"
    loading="eager"  // LCP image should load eagerly
    fetchPriority="high"
  />
</picture>
```

#### 2. Preload Critical Resources

```html
<!-- In <head> -->
<link rel="preload" href="/hero.webp" as="image" />
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preconnect" href="https://api.example.com" />
```

#### 3. Optimize Server Response Time

```tsx
// Use CDN for static assets
// Enable compression (gzip/brotli)
// Implement caching headers

// Next.js - use ISR or static generation
export const revalidate = 3600; // Revalidate every hour

export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map((post) => ({ slug: post.slug }));
}
```

#### 4. Minimize Render-Blocking Resources

```html
<!-- Defer non-critical JS -->
<script src="/analytics.js" defer></script>

<!-- Async load non-critical CSS -->
<link rel="preload" href="/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

---

## INP Optimization

### Key Principles

1. Keep JavaScript execution time minimal
2. Break up long tasks
3. Optimize event handlers
4. Reduce main thread blocking

### Optimization Strategies

#### 1. Debounce/Throttle Events

```tsx
import { useDebouncedCallback } from 'use-debounce';

function SearchInput() {
  const [query, setQuery] = useState('');

  const handleSearch = useDebouncedCallback((value: string) => {
    // Expensive search operation
    performSearch(value);
  }, 300);

  return (
    <input
      value={query}
      onChange={(e) => {
        setQuery(e.target.value);
        handleSearch(e.target.value);
      }}
    />
  );
}
```

#### 2. Use Web Workers for Heavy Computation

```tsx
// worker.ts
self.onmessage = (e: MessageEvent) => {
  const result = heavyComputation(e.data);
  self.postMessage(result);
};

// component.tsx
function DataProcessor() {
  const workerRef = useRef<Worker>();

  useEffect(() => {
    workerRef.current = new Worker(
      new URL('./worker.ts', import.meta.url)
    );

    workerRef.current.onmessage = (e) => {
      setResult(e.data);
    };

    return () => workerRef.current?.terminate();
  }, []);

  const processData = (data: any) => {
    workerRef.current?.postMessage(data);
  };
}
```

#### 3. Optimize React Rendering

```tsx
// Use startTransition for non-urgent updates
import { startTransition } from 'react';

function handleChange(value: string) {
  // Urgent: update input immediately
  setInputValue(value);

  // Non-urgent: can be interrupted
  startTransition(() => {
    setFilteredList(filterList(value));
  });
}

// Use useDeferredValue for derived state
import { useDeferredValue } from 'react';

function SearchResults({ query }: { query: string }) {
  const deferredQuery = useDeferredValue(query);

  const results = useMemo(
    () => searchItems(deferredQuery),
    [deferredQuery]
  );

  return <ResultsList results={results} />;
}
```

#### 4. Virtualize Long Lists

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: virtualRow.start,
              height: virtualRow.size,
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

## CLS Optimization

### Common Causes

1. Images without dimensions
2. Ads, embeds, iframes without dimensions
3. Dynamically injected content
4. Web fonts causing FOIT/FOUT
5. Actions waiting for network before updating DOM

### Optimization Strategies

#### 1. Always Set Image Dimensions

```tsx
// Good - dimensions specified
<img src="/photo.jpg" width={400} height={300} alt="Photo" />

// Good - aspect-ratio with CSS
<img
  src="/photo.jpg"
  alt="Photo"
  style={{ aspectRatio: '16/9', width: '100%', height: 'auto' }}
/>

// Next.js - automatic
<Image src="/photo.jpg" alt="Photo" width={400} height={300} />
```

#### 2. Reserve Space for Dynamic Content

```css
/* Reserve space for ads */
.ad-container {
  min-height: 250px;
  background: #f0f0f0;
}

/* Skeleton loading */
.skeleton {
  height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

#### 3. Optimize Font Loading

```tsx
// Next.js - automatic optimization
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // Prevent FOIT
});

// Manual - preload + font-display
<link
  rel="preload"
  href="/fonts/inter.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>

// CSS
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
  font-display: swap;
}
```

#### 4. Transform Animations (Not Layout)

```css
/* Bad - triggers layout */
.animate-bad {
  animation: slide-bad 0.3s;
}
@keyframes slide-bad {
  from { left: -100px; }
  to { left: 0; }
}

/* Good - GPU accelerated */
.animate-good {
  animation: slide-good 0.3s;
}
@keyframes slide-good {
  from { transform: translateX(-100px); }
  to { transform: translateX(0); }
}
```

---

## Bundle Optimization

### Code Splitting

```tsx
// Route-based splitting (automatic in Next.js)
// Component-based splitting
const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Skeleton />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Tree Shaking

```tsx
// Bad - imports entire library
import _ from 'lodash';
_.debounce(fn, 300);

// Good - imports only what's needed
import debounce from 'lodash/debounce';
debounce(fn, 300);

// Best - use native or smaller alternatives
const debounce = (fn, ms) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), ms);
  };
};
```

### Analyze Bundle Size

```bash
# Next.js
ANALYZE=true npm run build

# Webpack
npx webpack-bundle-analyzer stats.json

# Vite
npx vite-bundle-visualizer
```

---

## Caching Strategies

### Static Assets

```nginx
# nginx config
location /static/ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

### API Responses

```tsx
// Next.js fetch caching
const data = await fetch(url, {
  next: { revalidate: 60 }, // ISR - revalidate every 60s
});

// React Query
const { data } = useQuery({
  queryKey: ['users'],
  queryFn: fetchUsers,
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 30 * 60 * 1000, // 30 minutes
});
```

---

## Measurement Tools

| Tool | Purpose |
|------|---------|
| **Lighthouse** | Lab metrics, audits |
| **PageSpeed Insights** | Real-world + lab data |
| **Chrome DevTools** | Performance profiling |
| **Web Vitals Extension** | Real-time CWV monitoring |
| **CrUX Dashboard** | Field data from real users |

### Lighthouse CLI

```bash
# Basic audit
lighthouse https://example.com --only-categories=performance

# JSON output for CI
lighthouse https://example.com --output=json --output-path=./report.json

# With throttling
lighthouse https://example.com --throttling-method=devtools
```
