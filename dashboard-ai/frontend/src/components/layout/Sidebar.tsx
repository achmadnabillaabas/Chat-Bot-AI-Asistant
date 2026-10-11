'use client'

import { cn } from '@/lib/utils'
import { conversationsApi, ConversationListItem } from '@/lib/api'
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import QuickSearch from '@/components/common/QuickSearch'

interface SidebarProps {
  isOpen: boolean
  isMobileDrawerOpen: boolean
  onClose: () => void
}

const navigationItems = [
  { icon: 'chat_bubble', label: 'Chat', href: '/chat' },
  { icon: 'menu_book', label: 'Knowledge Base', href: '/knowledge' },
  { icon: 'data_usage', label: 'Token Usage', href: '/token-usage' },
  { icon: 'alt_route', label: 'Models & 9Router', href: '/models' },
  { icon: 'send', label: 'Telegram Bot', href: '/telegram' },
  { icon: 'settings', label: 'Settings', href: '/settings' },
]

export default function Sidebar({ isOpen, isMobileDrawerOpen, onClose }: SidebarProps) {
  const [conversations, setConversations] = useState<ConversationListItem[]>([])
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    loadConversations()
  }, [])

  // Keyboard shortcut for Quick Search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+K (Windows/Linux) or Cmd+K (Mac)
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setIsSearchOpen(true)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const loadConversations = async () => {
    try {
      const data = await conversationsApi.getAll()
      setConversations(data)
    } catch (err) {
      console.error('Failed to load conversations:', err)
    }
  }

  const handleNewChat = () => {
    router.push('/chat')
    onClose()
  }

  const handleSearchClick = () => {
    setIsSearchOpen(true)
  }

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen w-64 bg-surface-container-lowest flex flex-col z-50 shadow-[0_1px_8px_rgba(0,0,0,0.04)] transition-transform duration-300',
        // Desktop behavior
        'md:translate-x-0',
        !isOpen && 'md:-translate-x-full',
        // Mobile behavior
        'max-md:-translate-x-full',
        isMobileDrawerOpen && 'max-md:translate-x-0'
      )}
    >
      {/* Header */}
      <div className="p-space-md pb-space-sm flex flex-col gap-space-sm shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-space-sm min-w-0 flex-1">
            <div className="w-7 h-7 rounded-lg bg-surface-container flex items-center justify-center text-primary shrink-0">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="flex flex-col min-w-0 flex-1">
              <span className="font-headline-sm text-headline-sm text-on-surface font-bold leading-none truncate">
                AI Assistant
              </span>
              <span className="font-label-sm text-label-sm text-outline leading-tight truncate">
                Enterprise Workspace
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors shrink-0 md:hidden"
            title="Close Sidebar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* New Chat Button */}
        <button 
          onClick={handleNewChat}
          className="w-full mt-space-xs flex items-center justify-center gap-space-sm py-space-sm px-space-md rounded-lg bg-primary-container text-on-primary-container font-headline-sm text-headline-sm font-semibold hover:bg-primary transition-colors">
          <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="whitespace-nowrap">New Chat</span>
        </button>

        {/* Search */}
        <button 
          onClick={handleSearchClick}
          className="w-full flex items-center justify-between py-space-xs px-space-md rounded-lg bg-surface-container-low text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
        >
          <div className="flex items-center gap-space-sm min-w-0">
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span className="font-body-sm text-body-sm truncate">Quick Search</span>
          </div>
          <kbd className="font-label-sm text-label-sm px-1.5 py-0.5 rounded bg-surface-container-high text-outline shrink-0">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto px-space-md py-space-xs flex flex-col gap-space-md min-h-0">
        <div className="flex flex-col gap-space-xs shrink-0">
          <div className="px-space-xs py-1 flex items-center justify-between">
            <span className="font-label-sm text-label-sm text-outline uppercase tracking-wider font-semibold">
              Workspaces
            </span>
          </div>
          <nav className="flex flex-col gap-0.5">
            {navigationItems.map((item) => {
              const isActive = pathname.startsWith(item.href)
              return (
                <a
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center gap-space-sm px-space-sm py-1.5 rounded-lg transition-colors',
                    isActive
                      ? 'bg-surface-container text-primary font-semibold'
                      : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
                  )}
                >
                  <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span className="font-body-md text-body-md truncate">{item.label}</span>
                </a>
              )
            })}
          </nav>
        </div>

        {/* Recent conversations - Scrollable */}
        {conversations.length > 0 && (
          <>
            <div className="h-px bg-surface-container shrink-0"></div>
            <div className="flex flex-col gap-space-xs min-h-0 flex-1">
              <div className="px-space-xs py-1 flex items-center justify-between shrink-0">
                <span className="font-label-sm text-label-sm text-outline uppercase tracking-wider font-semibold">
                  Recent Chats
                </span>
                <span className="font-label-sm text-label-sm text-outline">
                  {conversations.length}
                </span>
              </div>
              {/* Scrollable conversation list */}
              <div className="flex flex-col gap-0.5 overflow-y-auto min-h-0 pr-1 scrollbar-thin">
                {conversations.map((conv) => (
                  <a
                    key={conv.id}
                    href={`/chat?id=${conv.id}`}
                    className="group flex items-center justify-between px-space-sm py-1.5 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors"
                    onClick={onClose}
                  >
                    <span className="font-body-sm text-body-sm truncate flex-1">
                      {conv.title}
                    </span>
                  </a>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="p-space-md pt-space-xs bg-surface-container-lowest flex flex-col gap-space-sm shadow-[0_1px_8px_rgba(0,0,0,0.04)] mt-auto shrink-0">
        <div className="flex items-center justify-between px-space-xs py-1 rounded bg-surface-container-low">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="w-2 h-2 rounded-full bg-secondary shrink-0"></span>
            <span className="font-label-sm text-label-sm text-on-surface truncate">9Router: Connected</span>
          </div>
          <span className="font-code-block text-code-block text-outline shrink-0">24ms</span>
        </div>
      </div>

      {/* Quick Search Dialog */}
      <QuickSearch isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </aside>
  )
}
