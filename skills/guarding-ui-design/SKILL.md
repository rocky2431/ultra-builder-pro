---
name: guarding-ui-design
description: "Prevents UI anti-patterns (distributional convergence) and guides design. TRIGGERS: Editing frontend files (.tsx/.jsx/.vue/.css/.scss/.sass/.less), discussing UI components/styling/design systems, creating new pages/components. ENFORCES: Avoid default fonts (Inter/Roboto/Open Sans/Lato), purple gradients, hard-coded colors. SUGGESTS: Design tokens, 3x+ typography jumps, established libraries (MUI/Ant Design/Chakra). DO NOT TRIGGER: Backend files (.py/.java/.go/.rs), API routes, database schemas, server configs, CLI tools."
allowed-tools: Read, Edit, Write
---

# UI Design Guardian

Prevents distributional convergence ("AI slop") and suggests actionable design improvements.

## Purpose

Guide frontend design toward cohesive, maintainable aesthetics by enforcing anti-patterns and suggesting design vectors.

## When

- Editing frontend files (.tsx/.jsx/.vue/.css/.scss)
- Discussing UI components, styling, or design
- Creating new components or pages

## Do

### Enforce (Hard Constraints)

**Avoid Default Fonts**:
- Never use: Inter, Roboto, Open Sans, Lato, system-ui
- Reason: Distributional convergence (makes all AI-generated UIs look the same)
- Alternative: Suggest specific font pairings (see examples)

**Avoid Clichéd Patterns**:
- Never use: Purple gradients on white backgrounds
- Never use: Scattered aesthetic choices without cohesive theme
- Reason: Creates generic "AI slop" appearance

**Prevent Design Debt**:
- Avoid hard-coded colors (use design tokens/CSS variables)
- Avoid inconsistent spacing (use theme spacing multiples)

### Suggest (Directional Guidance)

**1. Typography**:
- Size jumps: 3x+ scale between hierarchy levels (not 1.5x)
- Font pairing: High-contrast display font + monospace body
- Weight contrast: Avoid even weight distribution across elements

**2. Color & Theming**:
- Design tokens: Use CSS variables for all colors
- Dominant color: Choose one dominant with accents
- Inspiration: IDE themes, cultural aesthetics, brand guidelines

**3. Motion**:
- CSS-only first: Prefer transitions/animations over JS libraries
- Page load: Orchestrated staggered reveals (not scattered micro-interactions)
- Performance: Measure INP (<200ms target)

**4. Backgrounds**:
- Atmosphere: Subtle textures, gradients for depth
- Contrast: WCAG 2.1 AA (4.5:1 for text, 3:1 for UI elements)

**5. Design Systems**:
- Support multiple systems: Material Design, Tailwind, Chakra UI, Ant Design, custom
- Prefer established component libraries over custom basic components
- Examples: MUI, Ant Design, Chakra, Radix, shadcn/ui

**6. Accessibility**:
- WCAG 2.1 AA compliance (contrast, keyboard navigation, ARIA)
- Internationalization: Support Chinese + English where applicable

## Don't

- Do not enforce specific design systems (Material Design, Tailwind, etc.)
- Do not enforce specific color palettes (warm/cool is project-dependent)
- Do not enforce specific component libraries
- Do not provide vague guidance ("make it modern" - too abstract)

## Outputs

- Language: Chinese (simplified) at runtime
- Tone: Specific, actionable suggestions
- Format: Connect aesthetic intent to implementable code
- Examples: Provide concrete alternatives with code snippets

## Examples Location

Detailed design system examples available at:
- `examples/material-design-example.md`
- `examples/tailwind-example.md`
- `examples/chakra-ui-example.md`
