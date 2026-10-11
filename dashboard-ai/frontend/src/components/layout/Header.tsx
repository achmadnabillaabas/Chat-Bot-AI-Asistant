'use client'

import { cn } from '@/lib/utils'

interface HeaderProps {
  sidebarOpen: boolean
  onToggleSidebar: () => void
}

export default function Header({ sidebarOpen, onToggleSidebar }: HeaderProps) {
  return (
    <header 
      className={cn(
        'fixed top-0 right-0 h-14 bg-surface/90 backdrop-blur-xl z-40 flex items-center justify-between px-space-md md:px-space-lg shadow-[0_1px_8px_rgba(0,0,0,0.04)] transition-all duration-300',
        'left-0',
        sidebarOpen ? 'md:left-64' : 'md:left-0'
      )}
    >
      <div className="flex items-center gap-space-md min-w-0 flex-1">
        <button
          onClick={onToggleSidebar}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors shrink-0"
          title="Toggle Sidebar"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <div className="hidden sm:flex items-center gap-space-xs text-outline font-label-md text-label-md min-w-0">
          <span className="truncate">Workspace</span>
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span className="text-on-surface font-semibold truncate">Console</span>
        </div>
      </div>

      <div className="flex items-center gap-space-sm md:gap-space-md shrink-0">
        <div className="hidden md:flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-surface-container-low">
          <span className="w-2 h-2 rounded-full bg-secondary animate-pulse shrink-0"></span>
          <span className="font-label-sm text-label-sm text-on-surface font-medium whitespace-nowrap">9Router Active</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
          <svg className="w-5 h-5 text-on-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      </div>
    </header>
  )
}
