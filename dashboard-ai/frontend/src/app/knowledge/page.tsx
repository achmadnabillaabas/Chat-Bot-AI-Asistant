'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AppShell from '@/components/layout/AppShell'
import { knowledgeBaseApi, type KnowledgeBase } from '@/lib/api'
import Button from '@/components/common/Button'
import EmptyState from '@/components/common/EmptyState'

export default function KnowledgePage() {
  const router = useRouter()
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [createForm, setCreateForm] = useState({ name: '', description: '' })
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  const loadKnowledgeBases = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await knowledgeBaseApi.getAll()
      setKnowledgeBases(data)
    } catch (err) {
      console.error('Failed to load knowledge bases:', err)
      setError('Failed to load knowledge bases')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!createForm.name.trim()) return

    try {
      setIsCreating(true)
      await knowledgeBaseApi.create({
        name: createForm.name.trim(),
        description: createForm.description.trim() || undefined
      })
      setIsCreateModalOpen(false)
      setCreateForm({ name: '', description: '' })
      loadKnowledgeBases()
    } catch (err) {
      console.error('Failed to create knowledge base:', err)
      alert('Failed to create knowledge base')
    } finally {
      setIsCreating(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      setIsDeleting(true)
      await knowledgeBaseApi.delete(id)
      setDeleteConfirm(null)
      loadKnowledgeBases()
    } catch (err) {
      console.error('Failed to delete knowledge base:', err)
      alert('Failed to delete knowledge base')
    } finally {
      setIsDeleting(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-on-surface-variant">Loading knowledge bases...</p>
          </div>
        </div>
      </AppShell>
    )
  }

  if (error) {
    return (
      <AppShell>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-error">{error}</p>
            <Button onClick={loadKnowledgeBases} className="mt-4">
              Retry
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
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface font-bold">
              Knowledge Base
            </h1>
            <p className="text-body-md text-on-surface-variant mt-1">
              Manage your document collections for RAG-powered conversations
            </p>
          </div>
          <Button
            onClick={() => setIsCreateModalOpen(true)}
            className="shrink-0"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Knowledge Base
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto bg-surface-container-low">
        <div className="max-w-7xl mx-auto px-space-lg py-space-lg">
          {knowledgeBases.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              }
              title="No Knowledge Bases Yet"
              description="Create your first knowledge base to start organizing documents for AI-powered conversations."
              action={
                <Button onClick={() => setIsCreateModalOpen(true)}>
                  Create Knowledge Base
                </Button>
              }
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-md">
              {knowledgeBases.map((kb) => (
                <div
                  key={kb.id}
                  className="bg-surface-container rounded-lg p-space-md hover:shadow-md transition-shadow border border-surface-container-high"
                >
                  <div className="flex items-start justify-between mb-space-sm">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold truncate">
                        {kb.name}
                      </h3>
                      {kb.description && (
                        <p className="text-body-sm text-on-surface-variant mt-1 line-clamp-2">
                          {kb.description}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-space-md text-label-sm text-on-surface-variant mb-space-md">
                    <div className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span>{kb.document_count} docs</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span>{formatDate(kb.created_at)}</span>
                    </div>
                  </div>

                  <div className="flex gap-space-sm">
                    <button
                      onClick={() => router.push(`/knowledge/${kb.id}`)}
                      className="flex-1 px-space-sm py-space-xs rounded-lg bg-primary-container text-on-primary-container hover:bg-primary transition-colors font-label-md text-label-md font-semibold"
                    >
                      Open
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(kb.id)}
                      className="px-space-sm py-space-xs rounded-lg bg-error-container text-on-error-container hover:bg-error transition-colors"
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

      {/* Create Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-space-md">
          <div className="bg-surface-container rounded-lg max-w-md w-full p-space-lg">
            <h2 className="font-headline-md text-headline-md text-on-surface font-bold mb-space-md">
              Create Knowledge Base
            </h2>
            
            <form onSubmit={handleCreate}>
              <div className="mb-space-md">
                <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                  Name *
                </label>
                <input
                  type="text"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  className="w-full px-space-sm py-space-xs rounded-lg bg-surface-container-low border border-outline text-on-surface focus:border-primary focus:outline-none"
                  placeholder="e.g., Company Policies"
                  required
                  disabled={isCreating}
                />
              </div>

              <div className="mb-space-lg">
                <label className="block font-label-md text-label-md text-on-surface mb-space-xs">
                  Description
                </label>
                <textarea
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  className="w-full px-space-sm py-space-xs rounded-lg bg-surface-container-low border border-outline text-on-surface focus:border-primary focus:outline-none"
                  placeholder="Optional description..."
                  rows={3}
                  disabled={isCreating}
                />
              </div>

              <div className="flex gap-space-sm justify-end">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setIsCreateModalOpen(false)
                    setCreateForm({ name: '', description: '' })
                  }}
                  disabled={isCreating}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isCreating || !createForm.name.trim()}>
                  {isCreating ? 'Creating...' : 'Create'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm !== null && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-space-md">
          <div className="bg-surface-container rounded-lg max-w-md w-full p-space-lg">
            <h2 className="font-headline-md text-headline-md text-on-surface font-bold mb-space-sm">
              Delete Knowledge Base?
            </h2>
            <p className="text-body-md text-on-surface-variant mb-space-lg">
              All documents associated with this knowledge base will also be deleted. This action cannot be undone.
            </p>
            
            <div className="flex gap-space-sm justify-end">
              <Button
                variant="secondary"
                onClick={() => setDeleteConfirm(null)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleDelete(deleteConfirm)}
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
