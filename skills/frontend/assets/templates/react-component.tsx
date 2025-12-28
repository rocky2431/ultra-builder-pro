import { forwardRef, memo } from 'react';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export interface ComponentNameProps {
  /** Primary content */
  children?: React.ReactNode;
  /** Visual variant */
  variant?: 'default' | 'primary' | 'secondary';
  /** Size preset */
  size?: 'sm' | 'md' | 'lg';
  /** Disabled state */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
}

// =============================================================================
// Component
// =============================================================================

/**
 * ComponentName - Brief description of what this component does.
 *
 * @example
 * ```tsx
 * <ComponentName variant="primary" size="md">
 *   Content here
 * </ComponentName>
 * ```
 */
export const ComponentName = memo(
  forwardRef<HTMLDivElement, ComponentNameProps>(function ComponentName(
    {
      children,
      variant = 'default',
      size = 'md',
      disabled = false,
      className,
      onClick,
    },
    ref
  ) {
    // =========================================================================
    // Styles
    // =========================================================================

    const baseStyles = 'inline-flex items-center justify-center rounded-md';

    const variantStyles = {
      default: 'bg-gray-100 text-gray-900',
      primary: 'bg-blue-600 text-white',
      secondary: 'bg-gray-600 text-white',
    };

    const sizeStyles = {
      sm: 'px-2 py-1 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    // =========================================================================
    // Render
    // =========================================================================

    return (
      <div
        ref={ref}
        role="region"
        className={cn(
          baseStyles,
          variantStyles[variant],
          sizeStyles[size],
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        onClick={disabled ? undefined : onClick}
        aria-disabled={disabled}
      >
        {children}
      </div>
    );
  })
);

ComponentName.displayName = 'ComponentName';

// =============================================================================
// Compound Components (optional)
// =============================================================================

export const ComponentNameHeader = ({ children }: { children: React.ReactNode }) => (
  <div className="component-name-header">{children}</div>
);

export const ComponentNameBody = ({ children }: { children: React.ReactNode }) => (
  <div className="component-name-body">{children}</div>
);

export const ComponentNameFooter = ({ children }: { children: React.ReactNode }) => (
  <div className="component-name-footer">{children}</div>
);

// =============================================================================
// Exports
// =============================================================================

export default ComponentName;
