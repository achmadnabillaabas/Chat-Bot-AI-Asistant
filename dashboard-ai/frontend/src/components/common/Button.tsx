/**
 * Reusable Button component following Syntactic Slate design system
 */
import { cn } from '@/lib/utils'
import { ButtonHTMLAttributes, forwardRef } from 'react'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive'
  size?: 'compact' | 'regular'
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'regular', children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center gap-2 rounded-lg font-headline-sm text-headline-sm transition-colors focus-ring disabled:opacity-50 disabled:cursor-not-allowed',
          {
            'bg-primary-container text-on-primary-container hover:bg-primary': variant === 'primary',
            'border border-outline bg-transparent text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface': variant === 'secondary',
            'bg-transparent text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface': variant === 'ghost',
            'border border-danger/40 bg-transparent text-danger hover:bg-danger hover:text-white': variant === 'destructive',
            'h-7 px-3 text-label-md': size === 'compact',
            'h-9 px-4': size === 'regular',
          },
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button
