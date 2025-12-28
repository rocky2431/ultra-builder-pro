# Accessibility Reference

WCAG 2.1 compliance guide for frontend applications.

---

## WCAG 2.1 Principles

### 1. Perceivable

Content must be presentable in ways users can perceive.

### 2. Operable

UI components must be operable by all users.

### 3. Understandable

Information and UI operation must be understandable.

### 4. Robust

Content must be robust enough for assistive technologies.

---

## Common Patterns

### Buttons

```tsx
// Icon button - needs accessible label
<button aria-label="Close dialog" onClick={onClose}>
  <CloseIcon aria-hidden="true" />
</button>

// Toggle button
<button
  aria-pressed={isActive}
  onClick={() => setIsActive(!isActive)}
>
  {isActive ? 'Active' : 'Inactive'}
</button>

// Loading button
<button disabled={isLoading} aria-busy={isLoading}>
  {isLoading ? (
    <>
      <Spinner aria-hidden="true" />
      <span className="sr-only">Loading...</span>
    </>
  ) : (
    'Submit'
  )}
</button>
```

### Forms

```tsx
// Accessible form field
<div className="form-field">
  <label htmlFor="email">
    Email
    <span aria-hidden="true" className="required">*</span>
  </label>

  <input
    id="email"
    type="email"
    aria-required="true"
    aria-invalid={!!error}
    aria-describedby={error ? 'email-error' : 'email-hint'}
  />

  <span id="email-hint" className="hint">
    We'll never share your email.
  </span>

  {error && (
    <span id="email-error" role="alert" className="error">
      {error}
    </span>
  )}
</div>

// Form with fieldset
<fieldset>
  <legend>Shipping Address</legend>

  <label htmlFor="street">Street</label>
  <input id="street" name="street" />

  <label htmlFor="city">City</label>
  <input id="city" name="city" />
</fieldset>
```

### Navigation

```tsx
// Skip link
<a href="#main-content" className="skip-link">
  Skip to main content
</a>

// CSS for skip link
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  z-index: 100;
}
.skip-link:focus {
  top: 0;
}

// Main navigation
<nav aria-label="Main navigation">
  <ul role="menubar">
    <li role="none">
      <a role="menuitem" href="/" aria-current="page">Home</a>
    </li>
    <li role="none">
      <a role="menuitem" href="/about">About</a>
    </li>
  </ul>
</nav>

// Breadcrumb
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><a href="/products">Products</a></li>
    <li aria-current="page">Widget</li>
  </ol>
</nav>
```

### Modals/Dialogs

```tsx
function Modal({ isOpen, onClose, title, children }) {
  const modalRef = useRef<HTMLDivElement>(null);

  // Trap focus inside modal
  useEffect(() => {
    if (isOpen) {
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements?.[0] as HTMLElement;
      firstElement?.focus();
    }
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      ref={modalRef}
    >
      <h2 id="modal-title">{title}</h2>
      {children}
      <button onClick={onClose}>Close</button>
    </div>
  );
}
```

### Tables

```tsx
<table>
  <caption>Monthly Sales Report</caption>
  <thead>
    <tr>
      <th scope="col">Product</th>
      <th scope="col">Q1</th>
      <th scope="col">Q2</th>
      <th scope="col">Total</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Widgets</th>
      <td>100</td>
      <td>150</td>
      <td>250</td>
    </tr>
  </tbody>
</table>
```

### Live Regions

```tsx
// Announce dynamic updates
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// Urgent announcements
<div role="alert" aria-live="assertive">
  {errorMessage}
</div>

// Status updates (less intrusive)
<div role="status" aria-live="polite">
  {loadingMessage}
</div>
```

### Tabs

```tsx
function Tabs({ tabs, defaultTab }) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <div>
      <div role="tablist" aria-label="Content tabs">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            onClick={() => setActiveTab(tab.id)}
            onKeyDown={(e) => {
              if (e.key === 'ArrowRight') {
                const next = tabs[(index + 1) % tabs.length];
                setActiveTab(next.id);
              }
              if (e.key === 'ArrowLeft') {
                const prev = tabs[(index - 1 + tabs.length) % tabs.length];
                setActiveTab(prev.id);
              }
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {tabs.map((tab) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== tab.id}
          tabIndex={0}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

---

## Color Contrast Requirements

| Text Size | Minimum Ratio (AA) | Enhanced Ratio (AAA) |
|-----------|-------------------|---------------------|
| Normal text (< 18px) | 4.5:1 | 7:1 |
| Large text (≥ 18px bold or ≥ 24px) | 3:1 | 4.5:1 |
| UI components | 3:1 | - |

### Tools

- WebAIM Contrast Checker
- Chrome DevTools Color Picker
- Figma Stark Plugin

---

## Keyboard Navigation

### Required Keys

| Key | Action |
|-----|--------|
| `Tab` | Move to next focusable element |
| `Shift + Tab` | Move to previous element |
| `Enter` / `Space` | Activate button/link |
| `Arrow keys` | Navigate within components |
| `Escape` | Close modal/dropdown |
| `Home` / `End` | Jump to first/last item |

### Focus Management

```tsx
// Visible focus indicator
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

// Don't remove focus for mouse users
:focus:not(:focus-visible) {
  outline: none;
}

// Custom focus style
.button:focus-visible {
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
}
```

### Focus Trap

```tsx
import { useFocusTrap } from '@mantine/hooks';

function Modal({ isOpen, children }) {
  const focusTrapRef = useFocusTrap(isOpen);

  return (
    <div ref={focusTrapRef}>
      {children}
    </div>
  );
}
```

---

## Screen Reader Only (sr-only)

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Show on focus (for skip links) */
.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  margin: 0;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

---

## ARIA Quick Reference

### Roles

| Role | Usage |
|------|-------|
| `button` | Non-button element that acts as button |
| `link` | Non-anchor element that acts as link |
| `dialog` | Modal/dialog window |
| `alert` | Important, time-sensitive message |
| `status` | Status update (less urgent) |
| `navigation` | Navigation landmark |
| `main` | Main content area |
| `complementary` | Sidebar/supporting content |

### States

| Attribute | Usage |
|-----------|-------|
| `aria-expanded` | Expandable element state |
| `aria-selected` | Selected state (tabs, listbox) |
| `aria-pressed` | Toggle button state |
| `aria-checked` | Checkbox/radio state |
| `aria-disabled` | Disabled state |
| `aria-hidden` | Hide from assistive tech |
| `aria-invalid` | Form validation state |
| `aria-busy` | Loading state |

### Properties

| Attribute | Usage |
|-----------|-------|
| `aria-label` | Accessible name (no visible label) |
| `aria-labelledby` | Reference to visible label element |
| `aria-describedby` | Reference to description element |
| `aria-controls` | Element this controls |
| `aria-live` | Dynamic content region |
| `aria-current` | Current item (page, step, etc.) |

---

## Testing Checklist

### Automated Testing

- [ ] Run axe-core / eslint-plugin-jsx-a11y
- [ ] Check color contrast ratios
- [ ] Validate HTML structure
- [ ] Test with Lighthouse accessibility audit

### Manual Testing

- [ ] Navigate with keyboard only
- [ ] Test with screen reader (VoiceOver/NVDA)
- [ ] Check focus visibility
- [ ] Verify skip links work
- [ ] Test at 200% zoom
- [ ] Disable CSS and verify content order

### Screen Reader Testing

| Platform | Screen Reader |
|----------|---------------|
| macOS | VoiceOver (built-in) |
| Windows | NVDA (free), JAWS |
| Mobile iOS | VoiceOver |
| Mobile Android | TalkBack |

---

## Common Issues

| Issue | Impact | Fix |
|-------|--------|-----|
| Missing alt text | Images not announced | Add descriptive alt |
| No focus indicator | Keyboard users lost | Add :focus-visible styles |
| Color only info | Color blind users | Add icons/text labels |
| Auto-playing media | Disruptive | Provide pause control |
| Missing form labels | Can't identify fields | Associate labels |
| Timeout without warning | Users locked out | Warn before timeout |
| Motion sickness | Vestibular issues | Respect prefers-reduced-motion |
