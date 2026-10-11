/**
 * Knowledge Base type definitions
 */

export interface KnowledgeBase {
  id: number
  name: string
  description: string | null
  collection_name: string
  document_count: number
  created_at: string
  updated_at: string | null
}

export interface KnowledgeBaseListResponse {
  items: KnowledgeBase[]
  total: number
}

export interface KnowledgeBaseCreate {
  name: string
  description?: string
}

export interface KnowledgeBaseUpdate {
  name?: string
  description?: string
}

export interface Document {
  id: number
  knowledge_base_id: number
  filename: string
  file_path: string
  file_type: string
  file_size: number
  status: DocumentStatus
  error_message: string | null
  chunk_count: number
  uploaded_at: string
  processed_at: string | null
}

export type DocumentStatus = 
  | 'uploading'
  | 'extracting'
  | 'chunking'
  | 'embedding'
  | 'indexing'
  | 'ready'
  | 'failed'

export interface DocumentListResponse {
  items: Document[]
  total: number
}

export interface RAGSearchRequest {
  knowledge_base_id: number
  query: string
  top_k?: number
}

export interface RAGSearchResult {
  document_id: number
  document_name: string
  chunk_index: number
  text: string
  score: number
  page_number: number | null
}

export interface RAGSearchResponse {
  results: RAGSearchResult[]
  sources: {
    document_id: number
    document_name: string
    pages: number[] | null
  }[]
  knowledge_base_id: number
  query: string
}
