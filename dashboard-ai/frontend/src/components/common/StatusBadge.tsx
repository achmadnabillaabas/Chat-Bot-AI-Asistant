/**
 * Status Badge component for system status indicators
 */
import { cn } from '@/lib/utils'

export type StatusType = 'ready' | 'processing' | 'failed' | 'idle' | 'active'

interface StatusBadgeProps {
  status: StatusType
  label?: string
  className?: string
}

const statusConfig = {
  ready: {
    bg: 'bg-success/10',
    border: 'border-success',
    text: 'text-success',
    label: 'Ready',
  },
  processing: {
    bg: 'bg-warning/10',
    border: 'border-warning',
    text: 'text-warning',
    label: 'Processing',
  },
  failed: {
    bg: 'bg-danger/10',
    border: 'border-danger',
    text: 'text-danger',
    label: 'Failed',
  },
  idle: {
    bg: 'bg-outline/10',
    border: 'border-outline',
    text: 'text-outline',
    label: 'Idle',
  },
  active: {
    bg: 'bg-secondary/10',
    border: 'border-secondary',
    text: 'text-secondary',
    label: 'Active',
  },
}

export default function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const config = statusConfig[status]
  const displayLabel = label || config.label

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded border font-label-sm text-label-sm uppercase tracking-wide',
        config.bg,
        config.border,
        config.text,
        className
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {displayLabel}
    </span>
  )
}
