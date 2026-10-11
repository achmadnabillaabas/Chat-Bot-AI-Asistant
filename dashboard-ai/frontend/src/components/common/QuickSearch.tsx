'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { conversationsApi, ConversationListItem } from '@/lib/api'

interface QuickSearchProps {
  isOpen: boolean
  onClose: () => void
}

export default function QuickSearch({ isOpen, onClose }: QuickSearchProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [results, setResults] = useState<ConversationListItem[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()
  const searchTimeoutRef = useRef<NodeJS.Timeout>()

  // Focus input when dialog opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50)
      setSearchQuery('')
      setResults([])
      setSelectedIndex(0)
    }
  }, [isOpen])

  // Debounced search
  useEffect(() => {
    if (!isOpen) return

    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }

    if (!searchQuery.trim()) {
      setResults([])
      setIsSearching(false)
      return
    }

    setIsSearching(true)

    // Debounce search by 300ms
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        const conversations = await conversationsApi.getAll(searchQuery.trim())
        setResults(conversations)
        setSelectedIndex(0)
      } catch (err) {
        console.error('Search failed:', err)
        setResults([])
      } finally {
        setIsSearching(false)
      }
    }, 300)

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [searchQuery, isOpen])

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter' && results.length > 0) {
        e.preventDefault()
        handleSelectConversation(results[selectedIndex])
      }
    },
    [results, selectedIndex, onClose]
  )

  const handleSelectConversation = (conversation: ConversationListItem) => {
    router.push(`/chat?id=${conversation.id}`)
    onClose()
  }

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-[100] backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="fixed inset-0 z-[101] flex items-start justify-center pt-[20vh] px-4">
        <div className="bg-surface-container-low rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden border border-outline">
          {/* Search input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-outline">
            <svg className="w-5 h-5 text-outline shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              ref={inputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search conversations..."
              className="flex-1 bg-transparent text-on-surface font-body-lg text-body-lg outline-none placeholder:text-outline"
            />
            {isSearching && (
              <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin shrink-0" />
            )}
            <kbd className="px-2 py-1 rounded bg-surface-container text-outline font-label-sm text-label-sm shrink-0">
              ESC
            </kbd>
          </div>

          {/* Results */}
          <div className="max-h-[400px] overflow-y-auto">
            {searchQuery.trim() && !isSearching && results.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 px-4">
                <svg className="w-12 h-12 text-outline mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="font-body-lg text-body-lg text-on-surface-variant">
                  No conversations found
                </p>
                <p className="font-body-sm text-body-sm text-outline mt-1">
                  Try a different search term
                </p>
              </div>
            ) : !searchQuery.trim() ? (
              <div className="flex flex-col items-center justify-center py-12 px-4">
                <svg className="w-12 h-12 text-outline mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <p className="font-body-lg text-body-lg text-on-surface-variant">
                  Search your conversations
                </p>
                <p className="font-body-sm text-body-sm text-outline mt-1">
                  Type to start searching
                </p>
              </div>
            ) : (
              <div className="py-2">
                {results.map((conv, index) => (
                  <button
                    key={conv.id}
                    onClick={() => handleSelectConversation(conv)}
                    className={`w-full flex items-center justify-between px-4 py-3 transition-colors ${
                      index === selectedIndex
                        ? 'bg-surface-container-high'
                        : 'hover:bg-surface-container'
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <svg className="w-5 h-5 text-primary shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                      </svg>
                      <div className="flex flex-col items-start min-w-0 flex-1">
                        <span className="font-body-md text-body-md text-on-surface truncate w-full text-left">
                          {conv.title}
                        </span>
                        <span className="font-label-sm text-label-sm text-outline">
                          {conv.message_count} message{conv.message_count !== 1 ? 's' : ''} · {new Date(conv.updated_at || conv.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    {index === selectedIndex && (
                      <svg className="w-5 h-5 text-primary shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Footer hint */}
          {results.length > 0 && (
            <div className="flex items-center gap-4 px-4 py-2 border-t border-outline bg-surface-container-lowest">
              <div className="flex items-center gap-2">
                <kbd className="px-1.5 py-0.5 rounded bg-surface-container text-outline font-label-sm text-label-sm">
                  ↑↓
                </kbd>
                <span className="font-body-sm text-body-sm text-outline">Navigate</span>
              </div>
              <div className="flex items-center gap-2">
                <kbd className="px-1.5 py-0.5 rounded bg-surface-container text-outline font-label-sm text-label-sm">
                  ↵
                </kbd>
                <span className="font-body-sm text-body-sm text-outline">Select</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
