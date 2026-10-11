/**
 * Empty State component for placeholder screens
 */
import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

export default function EmptyState({
  icon,
  title,
  description,
  action,
  className
}: EmptyStateProps) {
  return (
    <div className={cn('text-center max-w-2xl mx-auto px-4', className)}>
      {icon && (
        <div className="mb-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-surface-container flex items-center justify-center">
            {icon}
          </div>
        </div>
      )}
      <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2">
        {title}
      </h2>
      {description && (
        <p className="font-body-lg text-body-lg text-on-surface-variant mb-6">
          {description}
        </p>
      )}
      {action && (
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {action}
        </div>
      )}
    </div>
  )
}
