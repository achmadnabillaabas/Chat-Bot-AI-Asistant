'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import AppShell from '@/components/layout/AppShell'
import { knowledgeBaseApi, type KnowledgeBase, type Document } from '@/lib/api'
import Button from '@/components/common/Button'
import StatusBadge from '@/components/common/StatusBadge'
import EmptyState from '@/components/common/EmptyState'

export default function KnowledgeBaseDetailPage() {
  const router = useRouter()
  const params = useParams()
  const kbId = parseInt(params.id as string)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [kb, setKb] = useState<KnowledgeBase | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [deleteDocConfirm, setDeleteDocConfirm] = useState<number | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    if (kbId) {
      loadData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kbId])

  useEffect(() => {
    // Poll for document status changes
    const interval = setInterval(() => {
      if (documents.some(d => !['ready', 'failed'].includes(d.status))) {
        loadDocuments()
      }
    }, 3000)

    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documents])

  const loadData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const [kbData, docsData] = await Promise.all([
        knowledgeBaseApi.getById(kbId),
        knowledgeBaseApi.getDocuments(kbId)
      ])
      setKb(kbData)
      setDocuments(docsData)
    } catch (err) {
      console.error('Failed to load knowledge base:', err)
      setError('Failed to load knowledge base')
    } finally {
      setIsLoading(false)
    }
  }

  const loadDocuments = async () => {
    try {
      const docsData = await knowledgeBaseApi.getDocuments(kbId)
      setDocuments(docsData)
    } catch (err) {
      console.error('Failed to refresh documents:', err)
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      setIsUploading(true)
      await knowledgeBaseApi.uploadDocument(kbId, file)
      loadDocuments()
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      console.error('Failed to upload document:', err)
      alert('Failed to upload document')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDeleteDoc = async (docId: number) => {
    try {
      setIsDeleting(true)
      await knowledgeBaseApi.deleteDocument(kbId, docId)
      setDeleteDocConfirm(null)
      loadDocuments()
    } catch (err) {
      console.error('Failed to delete document:', err)
      alert('Failed to delete document')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    try {
      setIsSearching(true)
      const results = await knowledgeBaseApi.search(kbId, searchQuery, 5)
      setSearchResults(results.results || [])
    } catch (err) {
      console.error('Failed to search:', err)
      alert('Failed to search knowledge base')
    } finally {
      setIsSearching(false)
    }
  }

  const getStatusProps = (status: string): { status: 'ready' | 'processing' | 'failed' | 'idle' | 'active', label: string } => {
    if (status === 'ready') return { status: 'ready', label: 'Ready' }
    if (status === 'failed') return { status: 'failed', label: 'Failed' }
    if (['uploading', 'extracting', 'chunking', 'embedding', 'indexing'].includes(status)) {
      return { status: 'processing', label: status.charAt(0).toUpperCase() + status.slice(1) }
    }
    return { status: 'idle', label: status }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-on-surface-variant">Loading...</p>
          </div>
        </div>
      </AppShell>
    )
  }

  if (error || !kb) {
    return (
      <AppShell>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-error">{error || 'Knowledge base not found'}</p>
            <Button onClick={() => router.push('/knowledge')} className="mt-4">
              Back to Knowledge Bases
            </Button>
          </div>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-surface-container-lowest px-space-lg py-space-md border-b border-surface-container">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => router.push('/knowledge')}
            className="flex items-center gap-1 text-on-surface-variant hover:text-on-surface mb-space-sm"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="text-body-sm">Back</span>
          </button>
          
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="font-headline-lg text-headline-lg text-on-surface font-bold">
                {kb.name}
              </h1>
              {kb.description && (
                <p className="text-body-md text-on-surface-variant mt-1">
                  {kb.description}
                </p>
              )}
              <div className="flex items-center gap-space-md mt-space-sm text-label-sm text-on-surface-variant">
                <span>ID: {kb.id}</span>
                <span>•</span>
                <span>{kb.document_count} documents</span>
                <span>•</span>
                <span>Created {formatDate(kb.created_at)}</span>
              </div>
            </div>
            
            <div className="flex gap-space-sm">
              <Button
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
              >
                {isUploading ? 'Uploading...' : 'Upload Document'}
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                accept=".txt,.pdf,.doc,.docx,.md,.csv"
                className="hidden"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto bg-surface-container-low">
        <div className="max-w-7xl mx-auto px-space-lg py-space-lg space-y-space-lg">
          {/* Test Search Section */}
          <div className="bg-surface-container rounded-lg p-space-md">
            <h2 className="font-headline-md text-headline-md text-on-surface font-semibold mb-space-md">
              Test Knowledge Base
            </h2>
            <form onSubmit={handleSearch} className="flex gap-space-sm">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-space-sm py-space-xs rounded-lg bg-surface-container-low border border-outline text-on-surface focus:border-primary focus:outline-none"
                placeholder="Ask something about this knowledge base..."
              />
              <Button type="submit" disabled={isSearching || !searchQuery.trim()}>
                {isSearching ? 'Searching...' : 'Search'}
              </Button>
            </form>

            {searchResults.length > 0 && (
              <div className="mt-space-md space-y-space-sm">
                {searchResults.map((result, idx) => (
                  <div key={idx} className="bg-surface-container-low rounded-lg p-space-sm border border-surface-container-high">
                    <div className="flex items-start justify-between mb-space-xs">
                      <span className="font-label-md text-label-md text-on-surface font-semibold">
                        {result.document_name}
                      </span>
                      <span className="text-label-sm text-outline">
                        Score: {result.score.toFixed(3)}
                      </span>
                    </div>
                    <p className="text-body-sm text-on-surface-variant">
                      {result.text}
                    </p>
                    {result.page_number && (
                      <span className="text-label-sm text-outline mt-space-xs inline-block">
                        Page {result.page_number}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Documents Section */}
          <div className="bg-surface-container rounded-lg p-space-md">
            <h2 className="font-headline-md text-headline-md text-on-surface font-semibold mb-space-md">
              Documents
            </h2>
            
            {documents.length === 0 ? (
              <EmptyState
                icon={
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                }
                title="No Documents Yet"
                description="Upload documents to start using this knowledge base for RAG conversations."
                action={
                  <Button onClick={() => fileInputRef.current?.click()}>
                    Upload Document
                  </Button>
                }
              />
            ) : (
              <div className="space-y-space-sm">
                {documents.map((doc) => (
                  <div key={doc.id} className="bg-surface-container-low rounded-lg p-space-sm border border-surface-container-high">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-space-sm mb-space-xs">
                          <h3 className="font-label-lg text-label-lg text-on-surface font-semibold truncate">
                            {doc.filename}
                          </h3>
                          <StatusBadge status={getStatusProps(doc.status).status} label={getStatusProps(doc.status).label} />
                        </div>
                        
                        <div className="flex items-center gap-space-md text-label-sm text-on-surface-variant">
                          <span>{doc.file_type.toUpperCase()}</span>
                          <span>•</span>
                          <span>{formatFileSize(doc.file_size)}</span>
                          <span>•</span>
                          <span>{doc.chunk_count} chunks</span>
                          <span>•</span>
                          <span>Uploaded {formatDate(doc.uploaded_at)}</span>
                        </div>
                        
                        {doc.error_message && (
                          <p className="text-label-sm text-error mt-space-xs">
                            Error: {doc.error_message}
                          </p>
                        )}
                      </div>
                      
                      <button
                        onClick={() => setDeleteDocConfirm(doc.id)}
                        className="ml-space-sm px-space-sm py-space-xs rounded-lg text-error hover:bg-error-container transition-colors"
                        title="Delete"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Delete Document Confirmation Modal */}
      {deleteDocConfirm !== null && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-space-md">
          <div className="bg-surface-container rounded-lg max-w-md w-full p-space-lg">
            <h2 className="font-headline-md text-headline-md text-on-surface font-bold mb-space-sm">
              Delete Document?
            </h2>
            <p className="text-body-md text-on-surface-variant mb-space-lg">
              This document and all its chunks will be permanently deleted. This action cannot be undone.
            </p>
            
            <div className="flex gap-space-sm justify-end">
              <Button
                variant="secondary"
                onClick={() => setDeleteDocConfirm(null)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleDeleteDoc(deleteDocConfirm)}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </div>
        </div>
      )}
      </div>
    </AppShell>
  )
}
