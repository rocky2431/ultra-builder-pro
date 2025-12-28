---
name: frontend
description: |
  Multi-framework frontend development skill for React, Vue, and Next.js applications.
  This skill should be used when: building UI components (forms, tables, modals),
  optimizing Core Web Vitals (LCP, INP, CLS), reviewing frontend code quality,
  implementing design systems, or improving accessibility (a11y).
---

# Frontend Development Skill

Comprehensive frontend development guidance for modern web applications.

## Activation Context

This skill activates during:
- Component development (React/Vue/Next.js)
- Performance optimization discussions
- UI/UX design system implementation
- Accessibility (a11y) improvements
- Frontend code reviews

## Resources

| Resource | Purpose |
|----------|---------|
| `references/react-patterns.md` | React 18+ hooks, patterns, best practices |
| `references/vue-patterns.md` | Vue 3 Composition API patterns |
| `references/nextjs-patterns.md` | Next.js App Router, RSC, Server Actions |
| `references/performance.md` | Core Web Vitals optimization guide |
| `references/accessibility.md` | WCAG 2.1 compliance checklist |
| `scripts/performance_audit.py` | Analyze components for performance issues |
| `assets/templates/` | Component templates for quick scaffolding |

## Component Development Workflow

### 1. Component Design

Before writing code, determine:
- Component responsibility (single purpose)
- Props interface (TypeScript types)
- State management approach (local vs global)
- Accessibility requirements

### 2. Framework-Specific Patterns

**React Component:**
```tsx
// Use functional components with hooks
// Memoize expensive computations
// Extract custom hooks for reusable logic
// See references/react-patterns.md for details
```

**Vue Component:**
```vue
<!-- Use Composition API with <script setup> -->
<!-- Leverage computed for derived state -->
<!-- Use defineProps/defineEmits for type safety -->
<!-- See references/vue-patterns.md for details -->
```

**Next.js Page:**
```tsx
// Prefer Server Components by default
// Use 'use client' only when needed
// Implement loading.tsx and error.tsx
// See references/nextjs-patterns.md for details
```

### 3. Quality Checklist

Before completing a component:
- [ ] TypeScript types defined
- [ ] Accessibility attributes (aria-*, role)
- [ ] Keyboard navigation support
- [ ] Error and loading states handled
- [ ] Unit tests written
- [ ] Performance optimized (memoization, lazy loading)

## Performance Optimization

### Core Web Vitals Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP | < 2.5s | Largest Contentful Paint |
| INP | < 200ms | Interaction to Next Paint |
| CLS | < 0.1 | Cumulative Layout Shift |

### Quick Wins

1. **Image Optimization**
   - Use next/image or responsive images
   - Implement lazy loading
   - Serve WebP/AVIF formats

2. **Code Splitting**
   - Dynamic imports for routes
   - Lazy load heavy components
   - Tree-shake unused code

3. **Render Optimization**
   - React: useMemo, useCallback, React.memo
   - Vue: computed, shallowRef, v-once
   - Avoid layout thrashing

### Performance Audit

Run the audit script for detailed analysis:
```bash
python scripts/performance_audit.py <component-path>
```

## Accessibility (a11y)

### WCAG 2.1 Quick Reference

1. **Perceivable**
   - Alt text for images
   - Sufficient color contrast (4.5:1)
   - Captions for media

2. **Operable**
   - Keyboard navigable
   - Focus indicators visible
   - No keyboard traps

3. **Understandable**
   - Clear error messages
   - Consistent navigation
   - Input assistance

4. **Robust**
   - Valid HTML
   - ARIA used correctly
   - Works with assistive tech

### Common Patterns

```tsx
// Accessible button
<button
  aria-label="Close dialog"
  aria-pressed={isPressed}
  onClick={handleClick}
>
  <CloseIcon aria-hidden="true" />
</button>

// Accessible form field
<label htmlFor="email">Email</label>
<input
  id="email"
  type="email"
  aria-describedby="email-error"
  aria-invalid={hasError}
/>
{hasError && <span id="email-error" role="alert">{error}</span>}
```

## Component Templates

Quick-start templates available in `assets/templates/`:

| Template | Usage |
|----------|-------|
| `react-component.tsx` | React functional component with TypeScript |
| `vue-component.vue` | Vue 3 SFC with Composition API |
| `nextjs-page.tsx` | Next.js App Router page with metadata |

Copy and customize templates for rapid development.

## Code Review Checklist

When reviewing frontend code:

### Structure
- [ ] Single responsibility principle
- [ ] Proper component decomposition
- [ ] Clean imports organization

### Performance
- [ ] No unnecessary re-renders
- [ ] Proper memoization
- [ ] Optimized bundle size

### Accessibility
- [ ] Semantic HTML
- [ ] ARIA attributes where needed
- [ ] Keyboard support

### Type Safety
- [ ] Props properly typed
- [ ] No `any` types
- [ ] Null checks handled

## Output Format

Provide frontend guidance in Chinese at runtime:

```
前端分析报告
========================

组件: {component_name}
框架: {React/Vue/Next.js}

发现问题:
- {具体问题描述}

优化建议:
1. {建议1}
2. {建议2}

性能影响:
- LCP: {预估影响}
- INP: {预估影响}

========================
```
