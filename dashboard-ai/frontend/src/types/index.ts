/**
 * TypeScript type definitions
 */

// User types
export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

// Conversation types
export interface Conversation {
  id: number
  user_id: number
  title: string
  created_at: string
  updated_at: string
  messages?: Message[]
}

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  model?: string
  knowledge_base_id?: number
  rag_enabled: boolean
  rag_context?: string
  created_at: string
  token_usage?: TokenUsage
}

// Token usage types
export interface TokenUsage {
  id: number
  user_id: number
  conversation_id?: number
  message_id?: number
  model: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  request_type: string
  rag_enabled: boolean
  knowledge_base_id?: number
  latency_ms?: number
  estimated_cost?: number
  created_at: string
}

// Knowledge base types
export type ProcessingStatus = 
  | 'uploading' 
  | 'extracting' 
  | 'chunking' 
  | 'embedding' 
  | 'indexing' 
  | 'ready' 
  | 'failed'

export interface KnowledgeBase {
  id: number
  name: string
  description?: string
  collection_name: string
  created_at: string
  updated_at: string
  documents?: Document[]
}

export interface Document {
  id: number
  knowledge_base_id: number
  filename: string
  file_path: string
  file_type: string
  file_size: number
  status: ProcessingStatus
  error_message?: string
  chunk_count: number
  uploaded_at: string
  processed_at?: string
}

export interface DocumentChunk {
  id: number
  document_id: number
  chunk_index: number
  content: string
  page_number?: number
  char_count: number
  vector_id?: string
  created_at: string
}

// Model types
export interface Model {
  id: number
  name: string
  display_name: string
  provider: string
  model_type: 'chat' | 'embedding'
  is_active: boolean
  is_default: boolean
  input_cost_per_million?: number
  output_cost_per_million?: number
  max_tokens?: number
  context_window?: number
  created_at: string
  updated_at: string
}

// Chat types
export interface ChatRequest {
  message: string
  conversation_id?: number
  model?: string
  knowledge_base_id?: number
  rag_enabled?: boolean
}

export interface ChatResponse {
  message: Message
  conversation_id: number
  token_usage: TokenUsage
}

// Analytics types
export interface UsageStats {
  total_requests: number
  input_tokens: number
  output_tokens: number
  total_tokens: number
  estimated_cost: number
}

export interface UsageByModel {
  model: string
  total_requests: number
  total_tokens: number
  input_tokens: number
  output_tokens: number
  estimated_cost: number
}

// Telegram types
export interface TelegramConfig {
  id: number
  bot_token: string
  bot_username?: string
  webhook_url?: string
  is_active: boolean
  is_connected: boolean
  allowed_users?: string[]
  default_model?: string
  created_at: string
  updated_at: string
  last_connected_at?: string
}
