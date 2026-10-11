/**
 * API client for backend communication
 */
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Debug logging in development
if (process.env.NODE_ENV === 'development') {
  console.log('[API Client] Base URL:', API_URL)
  console.log('[API Client] Full API URL:', `${API_URL}/api`)
}

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
})

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access (Phase 9)
      // localStorage.removeItem('token')
      // window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Type definitions
export interface ChatRequest {
  message: string
  conversation_id?: number
  model?: string
  rag_enabled?: boolean
  knowledge_base_id?: number | null
}

export interface TokenUsage {
  input_tokens: number
  output_tokens: number
  total_tokens: number
}

export interface MessageData {
  id: number
  role: string
  content: string
  model?: string
  created_at: string
}

export interface ChatResponse {
  conversation_id: number
  message: MessageData
  usage: TokenUsage
  model: string
  sources?: Array<{
    document_id: number
    document_name: string
    pages: number[] | null
  }>
}

export interface ConversationListItem {
  id: number
  title: string
  created_at: string
  updated_at?: string
  message_count: number
}

export interface ConversationDetail {
  id: number
  title: string
  created_at: string
  updated_at?: string
  messages: MessageData[]
}

export interface ComboInfo {
  id: string
  name: string
  type: string
}

export interface UsageSummary {
  total_requests: number
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
}

export interface DailyUsage {
  date: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  requests: number
}

export interface ComboUsage {
  combo_id: string
  requests: number
  input_tokens: number
  output_tokens: number
  total_tokens: number
  avg_input_tokens: number
  avg_output_tokens: number
}

export interface RequestDetail {
  id: number
  created_at: string
  conversation_id: number | null
  conversation_title: string | null
  model: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  request_type: string
  rag_enabled: boolean
  latency_ms: number | null
}

export interface RequestHistory {
  items: RequestDetail[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface TelegramBotInfo {
  bot_id: number
  bot_username: string
  bot_name: string
}

export interface TelegramStatus {
  is_connected: boolean
  bot_info?: TelegramBotInfo
  combo_id?: string
  connected_at?: string
}

export interface TelegramConnectRequest {
  bot_token: string
  combo_id: string
}

export interface TelegramDisconnectResponse {
  message: string
  is_connected: boolean
}

// API methods
export const chatApi = {
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[Chat API] Sending message:', {
        url: `${API_URL}/api/chat`,
        model: data.model,
        messageLength: data.message.length,
        conversationId: data.conversation_id,
      })
    }
    
    try {
      const response = await api.post<ChatResponse>('/chat', data)
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[Chat API] Response received:', {
          status: response.status,
          conversationId: response.data.conversation_id,
          model: response.data.model,
        })
      }
      
      return response.data
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[Chat API] Request failed:', {
          error: error,
          message: axios.isAxiosError(error) ? error.message : 'Unknown error',
          response: axios.isAxiosError(error) ? {
            status: error.response?.status,
            data: error.response?.data,
          } : undefined,
        })
      }
      throw error
    }
  },
}

export const conversationsApi = {
  getAll: async (search?: string): Promise<ConversationListItem[]> => {
    const params = new URLSearchParams()
    if (search) params.append('search', search)
    
    const url = search ? `/conversations?${params}` : '/conversations'
    const response = await api.get<ConversationListItem[]>(url)
    return response.data
  },
  getById: async (id: number): Promise<ConversationDetail> => {
    const response = await api.get<ConversationDetail>(`/conversations/${id}`)
    return response.data
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/conversations/${id}`)
  },
}

export const combosApi = {
  getAll: async (): Promise<ComboInfo[]> => {
    const response = await api.get<ComboInfo[]>('/combos')
    return response.data
  },
}

export const analyticsApi = {
  getSummary: async (days?: number, combo?: string): Promise<UsageSummary> => {
    const params = new URLSearchParams()
    if (days) params.append('days', days.toString())
    if (combo) params.append('combo', combo)
    
    const url = params.toString() ? `/analytics/usage/summary?${params}` : '/analytics/usage/summary'
    const response = await api.get<UsageSummary>(url)
    return response.data
  },
  
  getTimeseries: async (days: number = 7, combo?: string): Promise<DailyUsage[]> => {
    const params = new URLSearchParams({ days: days.toString() })
    if (combo) params.append('combo', combo)
    
    const response = await api.get<DailyUsage[]>(`/analytics/usage/timeseries?${params}`)
    return response.data
  },
  
  getByCombo: async (days?: number): Promise<ComboUsage[]> => {
    const params = new URLSearchParams()
    if (days) params.append('days', days.toString())
    
    const url = params.toString() ? `/analytics/usage/by-combo?${params}` : '/analytics/usage/by-combo'
    const response = await api.get<ComboUsage[]>(url)
    return response.data
  },
  
  getRequests: async (
    page: number = 1,
    pageSize: number = 50,
    days?: number,
    filters?: {
      combo?: string
      conversationId?: number
      requestType?: string
    }
  ): Promise<RequestHistory> => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })
    
    if (days) params.append('days', days.toString())
    if (filters?.combo) params.append('combo', filters.combo)
    if (filters?.conversationId) params.append('conversation_id', filters.conversationId.toString())
    if (filters?.requestType) params.append('request_type', filters.requestType)
    
    const response = await api.get<RequestHistory>(`/analytics/usage/requests?${params}`)
    return response.data
  },
}

export const telegramApi = {
  getStatus: async (): Promise<TelegramStatus> => {
    const response = await api.get<TelegramStatus>('/telegram/status')
    return response.data
  },
  
  connect: async (botToken: string, comboId: string): Promise<TelegramStatus> => {
    const response = await api.post<TelegramStatus>('/telegram/connect', {
      bot_token: botToken,
      combo_id: comboId
    })
    return response.data
  },
  
  disconnect: async (): Promise<TelegramDisconnectResponse> => {
    const response = await api.post<TelegramDisconnectResponse>('/telegram/disconnect')
    return response.data
  },
}

// Knowledge Base API types (imported from types file if needed)
export interface KnowledgeBase {
  id: number
  name: string
  description: string | null
  collection_name: string
  document_count: number
  created_at: string
  updated_at: string | null
}

export interface Document {
  id: number
  knowledge_base_id: number
  filename: string
  file_path: string
  file_type: string
  file_size: number
  status: string
  error_message: string | null
  chunk_count: number
  uploaded_at: string
  processed_at: string | null
}

export interface RAGSearchResult {
  document_id: number
  document_name: string
  chunk_index: number
  text: string
  score: number
  page_number: number | null
}

export const knowledgeBaseApi = {
  getAll: async (): Promise<KnowledgeBase[]> => {
    const response = await api.get<{ items: KnowledgeBase[], total: number }>('/knowledge-bases')
    return response.data.items
  },
  
  getById: async (id: number): Promise<KnowledgeBase> => {
    const response = await api.get<KnowledgeBase>(`/knowledge-bases/${id}`)
    return response.data
  },
  
  create: async (data: { name: string, description?: string }): Promise<KnowledgeBase> => {
    const response = await api.post<KnowledgeBase>('/knowledge-bases', data)
    return response.data
  },
  
  update: async (id: number, data: { name?: string, description?: string }): Promise<KnowledgeBase> => {
    const response = await api.patch<KnowledgeBase>(`/knowledge-bases/${id}`, data)
    return response.data
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/knowledge-bases/${id}`)
  },
  
  // Documents
  getDocuments: async (kbId: number): Promise<Document[]> => {
    const response = await api.get<{ items: Document[], total: number }>(`/knowledge-bases/${kbId}/documents`)
    return response.data.items
  },
  
  uploadDocument: async (kbId: number, file: File): Promise<Document> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post<Document>(`/knowledge-bases/${kbId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  
  deleteDocument: async (kbId: number, documentId: number): Promise<void> => {
    await api.delete(`/knowledge-bases/${kbId}/documents/${documentId}`)
  },
  
  reindexDocument: async (kbId: number, documentId: number): Promise<Document> => {
    const response = await api.post<Document>(`/knowledge-bases/${kbId}/documents/${documentId}/reindex`)
    return response.data
  },
  
  // RAG Search
  search: async (kbId: number, query: string, topK: number = 5): Promise<{
    results: RAGSearchResult[]
    sources: { document_id: number, document_name: string, pages: number[] | null }[]
  }> => {
    const response = await api.post<{
      results: RAGSearchResult[]
      sources: { document_id: number, document_name: string, pages: number[] | null }[]
    }>('/rag/search', {
      knowledge_base_id: kbId,
      query,
      top_k: topK
    })
    return response.data
  },
}
