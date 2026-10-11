'use client'

import { useState, useEffect, useRef } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { chatApi, conversationsApi, combosApi, knowledgeBaseApi, ComboInfo, MessageData, TokenUsage, KnowledgeBase } from '@/lib/api'
import ReactMarkdown from 'react-markdown'

interface Message extends MessageData {
  usage?: TokenUsage
  sources?: Array<{
    document_id: number
    document_name: string
    pages: number[] | null
  }>
}

export default function ChatContent() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingConversation, setIsLoadingConversation] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [combos, setCombos] = useState<ComboInfo[]>([])
  const [selectedCombo, setSelectedCombo] = useState<string | null>(null)
  
  // RAG state
  const [ragEnabled, setRagEnabled] = useState(false)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKnowledgeBaseId, setSelectedKnowledgeBaseId] = useState<number | null>(null)
  const [isLoadingKBs, setIsLoadingKBs] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const loadingConversationIdRef = useRef<number | null>(null)
  const searchParams = useSearchParams()
  const router = useRouter()

  // Load combos and knowledge bases on mount
  useEffect(() => {
    loadCombos()
    loadKnowledgeBases()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Load conversation from URL parameter OR clear state when no parameter
  useEffect(() => {
    const conversationIdParam = searchParams.get('id')
    
    if (conversationIdParam) {
      // Load conversation if ID exists
      const id = parseInt(conversationIdParam, 10)
      if (!isNaN(id)) {
        // Only load if it's different from current
        if (id !== conversationId) {
          loadConversation(id)
        }
      }
    } else {
      // Clear state when no ID parameter (new chat)
      if (conversationId !== null || messages.length > 0) {
        if (process.env.NODE_ENV === 'development') {
          console.log('[Chat Page] Clearing conversation state (New Chat)')
        }
        // Cancel any ongoing conversation loading
        loadingConversationIdRef.current = null
        setConversationId(null)
        setMessages([])
        setError(null)
        setIsLoadingConversation(false)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadCombos = async () => {
    try {
      const comboList = await combosApi.getAll()
      setCombos(comboList)
      if (comboList.length > 0 && !selectedCombo) {
        setSelectedCombo(comboList[0].id)
      }
    } catch (err) {
      console.error('Failed to load combos:', err)
      setError('Unable to load AI Combos. Please refresh the page.')
    }
  }

  const loadKnowledgeBases = async () => {
    try {
      setIsLoadingKBs(true)
      const kbList = await knowledgeBaseApi.getAll()
      setKnowledgeBases(kbList)
    } catch (err) {
      console.error('Failed to load knowledge bases:', err)
      // Don't show error, just disable RAG functionality
      setKnowledgeBases([])
    } finally {
      setIsLoadingKBs(false)
    }
  }

  const loadConversation = async (id: number) => {
    // Set loading conversation ID to prevent stale responses
    loadingConversationIdRef.current = id
    setIsLoadingConversation(true)
    setError(null)
    
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[Chat Page] Loading conversation:', id)
      }
      
      const conversation = await conversationsApi.getById(id)
      
      // Check if this conversation is still the one we want to load
      // (user might have clicked New Chat while loading)
      if (loadingConversationIdRef.current !== id) {
        if (process.env.NODE_ENV === 'development') {
          console.log('[Chat Page] Ignoring stale conversation response:', id)
        }
        return
      }
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[Chat Page] Conversation loaded:', conversation)
      }
      
      // Set conversation ID
      setConversationId(conversation.id)
      
      // Set messages
      setMessages(conversation.messages.map(msg => ({
        ...msg,
        usage: undefined // Usage not included in conversation detail
      })))
      
      // Preserve selected combo (don't change it)
      // User can manually change if needed
      
    } catch (err: any) {
      // Only show error if this is still the conversation being loaded
      if (loadingConversationIdRef.current === id) {
        console.error('[Chat Page] Failed to load conversation:', err)
        setError(`Failed to load conversation: ${err.response?.data?.detail || err.message || 'Unknown error'}`)
      }
    } finally {
      // Only clear loading if this is still the conversation being loaded
      if (loadingConversationIdRef.current === id) {
        setIsLoadingConversation(false)
        loadingConversationIdRef.current = null
      }
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    if (!selectedCombo) {
      setError('Please select an AI Combo before sending a message.')
      return
    }

    // Validate RAG: if enabled, KB must be selected
    if (ragEnabled && !selectedKnowledgeBaseId) {
      setError('Please select a Knowledge Base first.')
      return
    }

    const userMessage = input.trim()
    setInput('')
    setError(null)

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMessage])
    setIsLoading(true)

    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('[Chat Page] Sending message:', {
          combo: selectedCombo,
          messageLength: userMessage.length,
          conversationId,
          ragEnabled,
          knowledgeBaseId: ragEnabled ? selectedKnowledgeBaseId : null,
        })
      }
      
      const response = await chatApi.sendMessage({
        message: userMessage,
        conversation_id: conversationId || undefined,
        model: selectedCombo,
        rag_enabled: ragEnabled,
        knowledge_base_id: ragEnabled ? selectedKnowledgeBaseId : null
      })

      if (process.env.NODE_ENV === 'development') {
        console.log('[Chat Page] Response received:', response)
      }

      // Update conversation ID if new
      const isNewConversation = !conversationId
      if (isNewConversation) {
        setConversationId(response.conversation_id)
        // Update URL to include conversation ID
        router.push(`/chat?id=${response.conversation_id}`)
        
        if (process.env.NODE_ENV === 'development') {
          console.log('[Chat Page] New conversation created, updated URL to:', `/chat?id=${response.conversation_id}`)
        }
      }

      // Add assistant message with usage and sources
      const assistantMessage: Message = {
        ...response.message,
        usage: response.usage,
        sources: response.sources || undefined
      }

      setMessages(prev => [...prev.slice(0, -1), tempUserMessage, assistantMessage])
    } catch (err: any) {
      console.error('[Chat Page] Error:', err)
      
      // Remove temp user message on error
      setMessages(prev => prev.slice(0, -1))
      
      // Detailed error messages in development
      if (process.env.NODE_ENV === 'development') {
        if (err.code === 'ERR_NETWORK') {
          setError(`Network Error: Cannot connect to backend at ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}. Is the backend running?`)
        } else if (err.code === 'ECONNABORTED') {
          setError('Request Timeout: Backend took too long to respond.')
        } else if (err.response?.status === 503) {
          setError('AI Combo is currently unavailable. Please try again or select another Combo.')
        } else if (err.response?.status === 400) {
          setError(err.response.data.detail || 'Invalid request. Please try again.')
        } else if (err.response?.status) {
          setError(`Backend Error (${err.response.status}): ${err.response.data?.detail || err.message}`)
        } else {
          setError(`Error: ${err.message || 'Failed to send message. Please try again.'}`)
        }
      } else {
        // Production: friendly messages
        if (err.response?.status === 503) {
          setError('AI Combo is currently unavailable. Please try again or select another Combo.')
        } else if (err.response?.status === 400) {
          setError(err.response.data.detail || 'Invalid request. Please try again.')
        } else {
          setError('Failed to send message. Please try again.')
        }
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewChat = () => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[Chat Page] New Chat clicked - clearing state')
    }
    
    // Explicitly clear all state immediately
    loadingConversationIdRef.current = null
    setConversationId(null)
    setMessages([])
    setError(null)
    setIsLoadingConversation(false)
    
    // Navigate to /chat without ID parameter
    router.push('/chat')
  }

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)] max-w-5xl mx-auto w-full">
      {/* Chat header */}
      <div className="sticky top-14 z-30 py-space-sm px-space-md md:px-space-lg bg-surface-container-low border-b border-border-subtle">
        <div className="flex flex-col gap-space-sm">
          <div className="flex items-center justify-between flex-wrap gap-space-sm">
            {/* Combo selector */}
            <div className="flex items-center gap-2">
              <span className="font-label-md text-label-md text-on-surface-variant whitespace-nowrap">
                AI Combo:
              </span>
              <select
                value={selectedCombo || ''}
                onChange={(e) => setSelectedCombo(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-surface-container border border-outline text-on-surface font-body-md text-body-md focus:outline-none focus:border-primary transition-colors min-w-[160px]"
                disabled={isLoading || combos.length === 0}
              >
                {combos.length === 0 ? (
                  <option value="">Loading...</option>
                ) : (
                  combos.map((combo) => (
                    <option key={combo.id} value={combo.id}>
                      {combo.name}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* New chat button */}
            <button
              onClick={handleNewChat}
              className="px-3 py-1.5 rounded-lg border border-outline text-on-surface-variant bg-transparent hover:bg-surface-container-high hover:text-on-surface transition-colors font-body-md text-body-md whitespace-nowrap"
            >
              New Chat
            </button>
          </div>

          {/* RAG Controls */}
          <div className="flex items-center gap-space-md flex-wrap">
            {/* RAG Toggle */}
            <div className="flex items-center gap-2">
              <span className="font-label-md text-label-md text-on-surface-variant whitespace-nowrap">
                RAG:
              </span>
              <button
                onClick={() => {
                  setRagEnabled(!ragEnabled)
                  if (ragEnabled) {
                    // When turning off, clear selection
                    setSelectedKnowledgeBaseId(null)
                  }
                }}
                className={`px-3 py-1 rounded-lg font-label-md text-label-md font-semibold transition-colors ${
                  ragEnabled
                    ? 'bg-secondary text-on-secondary'
                    : 'bg-surface-container text-on-surface-variant border border-outline'
                }`}
                disabled={isLoading || isLoadingKBs}
              >
                {ragEnabled ? 'ON' : 'OFF'}
              </button>
            </div>

            {/* Knowledge Base Selector */}
            <div className="flex items-center gap-2">
              <span className="font-label-md text-label-md text-on-surface-variant whitespace-nowrap">
                Knowledge Base:
              </span>
              <select
                value={selectedKnowledgeBaseId || ''}
                onChange={(e) => setSelectedKnowledgeBaseId(e.target.value ? parseInt(e.target.value) : null)}
                className="px-3 py-1.5 rounded-lg bg-surface-container border border-outline text-on-surface font-body-md text-body-md focus:outline-none focus:border-primary transition-colors min-w-[200px] disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!ragEnabled || isLoading || isLoadingKBs}
              >
                <option value="">
                  {isLoadingKBs ? 'Loading...' : knowledgeBases.length === 0 ? 'No Knowledge Bases' : 'Select Knowledge Base'}
                </option>
                {knowledgeBases.map((kb) => (
                  <option key={kb.id} value={kb.id}>
                    {kb.name} ({kb.document_count} docs)
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
        {isLoadingConversation ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="font-body-lg text-body-lg text-on-surface-variant animate-pulse">
                Loading conversation...
              </p>
            </div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-2xl">
              {combos.length === 0 ? (
                <>
                  <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2">
                    No AI Combo configured
                  </h2>
                  <p className="font-body-lg text-body-lg text-on-surface-variant">
                    Please configure AI Combos to start chatting
                  </p>
                </>
              ) : (
                <>
                  <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2">
                    Start a conversation
                  </h2>
                  <p className="font-body-lg text-body-lg text-on-surface-variant">
                    Send a message using {combos.find(c => c.id === selectedCombo)?.name || 'AI Combo'}
                  </p>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-6 max-w-3xl mx-auto">
            {messages.map((message, index) => (
              <div
                key={`${message.id}-${index}`}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center shrink-0">
                    <svg className="w-5 h-5 text-on-primary-container" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                )}

                <div className={`flex flex-col gap-2 flex-1 min-w-0 ${
                  message.role === 'user' ? 'items-end' : 'items-start'
                }`}>
                  <div
                    className={`px-4 py-3 rounded-xl max-w-2xl ${
                      message.role === 'user'
                        ? 'bg-surface-container-high rounded-tr-sm'
                        : 'bg-surface-container rounded-tl-sm'
                    }`}
                  >
                    <div className="font-body-lg text-body-lg text-on-surface prose prose-invert max-w-none">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  </div>

                  {/* Token usage */}
                  {message.usage && (
                    <div className="flex items-center gap-2 px-2 py-1 rounded bg-surface-container-low font-code-block text-code-block text-outline">
                      <span className="text-on-surface-variant">{message.usage.input_tokens} in</span>
                      <span>•</span>
                      <span className="text-on-surface-variant">{message.usage.output_tokens} out</span>
                      <span>•</span>
                      <span className="text-secondary">{message.usage.total_tokens} total</span>
                    </div>
                  )}

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 px-3 py-2 rounded-lg bg-surface-container-low border border-outline">
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <svg className="w-4 h-4 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="font-label-sm text-label-sm text-secondary font-semibold uppercase">Sources</span>
                      </div>
                      <div className="flex flex-col gap-1">
                        {message.sources.map((source, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-body-sm text-on-surface">
                            <span className="text-outline">•</span>
                            <span>{source.document_name}</span>
                            {source.pages && source.pages.length > 0 && (
                              <span className="text-outline text-label-sm">
                                (Pages: {source.pages.join(', ')})
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {message.role === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-surface-container-highest flex items-center justify-center shrink-0">
                    <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                )}
              </div>
            ))}

            {/* Loading state */}
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-lg bg-surface-container-highest flex items-center justify-center shrink-0 animate-pulse">
                  <svg className="w-5 h-5 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="px-4 py-3 rounded-xl bg-surface-container-low">
                  <p className="font-body-md text-body-md text-on-surface-variant animate-pulse">
                    Generating response...
                  </p>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="px-4 md:px-8 py-3 bg-error-container border-t border-danger">
          <div className="max-w-3xl mx-auto flex items-center gap-2">
            <svg className="w-5 h-5 text-danger shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="font-body-md text-body-md text-on-error-container flex-1">
              {error}
            </p>
            <button
              onClick={() => setError(null)}
              className="text-on-error-container hover:text-danger transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Input area */}
      <div className="border-t border-border-subtle bg-surface px-4 md:px-8 py-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Shift+Enter for new line)"
              className="flex-1 px-4 py-3 rounded-lg bg-surface-container-low border border-outline text-on-surface placeholder:text-outline resize-none focus:outline-none focus:border-primary transition-colors font-body-md text-body-md min-h-[52px] max-h-[200px]"
              rows={1}
              disabled={isLoading || combos.length === 0}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading || combos.length === 0}
              className="px-6 py-3 rounded-lg bg-primary-container text-on-primary-container font-headline-sm text-headline-sm font-semibold hover:bg-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
            >
              Send
            </button>
          </div>
          <p className="mt-2 font-body-sm text-body-sm text-outline text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}
