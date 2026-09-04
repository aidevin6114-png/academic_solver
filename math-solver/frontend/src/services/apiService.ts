import axios, { AxiosError, AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const API_TIMEOUT = 30000 // 30 seconds

// Error types
export enum ErrorType {
  VALIDATION_ERROR = 'validation_error',
  FILE_ERROR = 'file_error',
  AI_ERROR = 'ai_error',
  API_ERROR = 'api_error',
  TIMEOUT_ERROR = 'timeout_error',
  NETWORK_ERROR = 'network_error',
  INTERNAL_ERROR = 'internal_error'
}

export interface APIError {
  message: string
  type: ErrorType
  details?: Record<string, any>
  retryable: boolean
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  file?: { name: string; data: string }
  messageId?: string
  timestamp?: string
}

export interface SolveRequest {
  problem: string
  file?: File
  sessionId?: string
  capabilities: {
    webSearch: boolean
    codeExecution: boolean
    stepByStep: boolean
  }
}

export interface SolveResponse {
  success: boolean
  solution?: string
  steps?: string[]
  code?: string
  confidence?: number
  error?: string
  errorType?: ErrorType
  sessionId?: string
  requestId?: string
}

export interface FileUploadResponse {
  success: boolean
  fileId?: string
  filename?: string
  error?: string
}

export interface HealthResponse {
  status: string
  aiSolverReady: boolean
  timestamp: string
}

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add request ID and logging
api.interceptors.request.use(config => {
  const requestId = generateRequestId()
  config.headers['X-Request-ID'] = requestId
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
      requestId,
      params: config.params,
      data: config.data
    })
  }
  
  return config
}, error => {
  return Promise.reject(error)
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] Response ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        requestId: response.headers['x-request-id'],
        data: response.data
      })
    }
    return response
  },
  error => {
    return Promise.reject(handleAxiosError(error))
  }
)

function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

function handleAxiosError(error: AxiosError): APIError {
  if (error.response) {
    // API error response
    const status = error.response.status
    const data = error.response.data as any
    
    switch (status) {
      case 400:
        return {
          message: data?.error || 'Invalid request',
          type: ErrorType.VALIDATION_ERROR,
          details: data?.details,
          retryable: false
        }
      case 422:
        return {
          message: data?.error || 'File processing failed',
          type: ErrorType.FILE_ERROR,
          details: data?.details,
          retryable: data?.retryable ?? false
        }
      case 429:
        return {
          message: 'Too many requests. Please try again later.',
          type: ErrorType.API_ERROR,
          retryable: true
        }
      case 503:
      case 502:
        return {
          message: data?.error || 'AI service temporarily unavailable',
          type: data?.error_type || ErrorType.AI_ERROR,
          retryable: true
        }
      case 504:
        return {
          message: 'Request timeout. Please try again.',
          type: ErrorType.TIMEOUT_ERROR,
          retryable: true
        }
      default:
        return {
          message: data?.error || `API error: ${status}`,
          type: ErrorType.INTERNAL_ERROR,
          retryable: status >= 500
        }
    }
  } else if (error.request) {
    // Network error
    return {
      message: 'Network error. Please check your connection.',
      type: ErrorType.NETWORK_ERROR,
      retryable: true
    }
  } else {
    // Client error
    return {
      message: error.message || 'Unknown error occurred',
      type: ErrorType.INTERNAL_ERROR,
      retryable: false
    }
  }
}

// Retry logic for transient failures
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelayMs: number = 1000
): Promise<T> {
  let lastError: any
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      
      // Check if error is retryable
      if (!isRetryableError(error) || attempt === maxRetries) {
        throw error
      }
      
      // Calculate delay with exponential backoff
      const delay = initialDelayMs * Math.pow(2, attempt) + Math.random() * 100
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`[API] Retrying after ${delay}ms (attempt ${attempt + 1}/${maxRetries})`)
      }
      
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  
  throw lastError
}

function isRetryableError(error: any): boolean {
  if (error.retryable !== undefined) {
    return error.retryable
  }
  if (error.response) {
    return error.response.status >= 500 || error.response.status === 429
  }
  return false
}

// Validate response structure
function validateResponse<T>(data: any, requiredFields: string[]): T {
  if (typeof data !== 'object' || data === null) {
    throw {
      message: 'Invalid response format',
      type: ErrorType.INTERNAL_ERROR,
      retryable: false
    } as APIError
  }
  
  for (const field of requiredFields) {
    if (!(field in data)) {
      throw {
        message: `Missing required field: ${field}`,
        type: ErrorType.INTERNAL_ERROR,
        retryable: false
      } as APIError
    }
  }
  
  return data as T
}

export const apiService = {
  async sendMessage(message: ChatMessage): Promise<ChatMessage> {
    return retryWithBackoff(async () => {
      const response = await api.post('/chat/send', message)
      return validateResponse<ChatMessage>(response.data, ['success'])
    })
  },

  async uploadFile(file: File): Promise<FileUploadResponse> {
    // Validate file before upload
    if (!file) {
      throw {
        message: 'No file selected',
        type: ErrorType.VALIDATION_ERROR,
        retryable: false
      } as APIError
    }
    
    const maxSizeMB = 50
    const fileSizeMB = file.size / (1024 * 1024)
    
    if (fileSizeMB > maxSizeMB) {
      throw {
        message: `File size (${fileSizeMB.toFixed(2)}MB) exceeds maximum (${maxSizeMB}MB)`,
        type: ErrorType.FILE_ERROR,
        retryable: false
      } as APIError
    }
    
    return retryWithBackoff(async () => {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return validateResponse<FileUploadResponse>(response.data, ['success'])
    }, 2) // Fewer retries for file uploads
  },

  async solveProblem(request: SolveRequest): Promise<SolveResponse> {
    // Validate request
    if (!request.problem || request.problem.trim().length === 0) {
      throw {
        message: 'Problem statement cannot be empty',
        type: ErrorType.VALIDATION_ERROR,
        retryable: false
      } as APIError
    }
    
    if (request.problem.length > 5000) {
      throw {
        message: 'Problem statement is too long (max 5000 characters)',
        type: ErrorType.VALIDATION_ERROR,
        retryable: false
      } as APIError
    }
    
    return retryWithBackoff(async () => {
      const formData = new FormData()
      formData.append('problem', request.problem)
      formData.append('capabilities', JSON.stringify(request.capabilities))
      
      if (request.sessionId) {
        formData.append('session_id', request.sessionId)
      }
      
      if (request.file) {
        formData.append('file', request.file)
      }
      
      const response = await api.post('/solve/problem', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return validateResponse<SolveResponse>(response.data, ['success'])
    })
  },

  async createScreenShareSession(): Promise<{ sessionId: string; url: string }> {
    const response = await api.post('/screenshare/create')
    return validateResponse<{ sessionId: string; url: string }>(response.data, [
      'success'
    ])
  },

  async getSessionHistory(sessionId: string): Promise<ChatMessage[]> {
    if (!sessionId) {
      throw {
        message: 'Session ID is required',
        type: ErrorType.VALIDATION_ERROR,
        retryable: false
      } as APIError
    }
    
    const response = await api.get(`/sessions/${sessionId}`)
    const data = validateResponse<any>(response.data, ['success'])
    return (data.messages || []) as ChatMessage[]
  },

  async deleteSession(sessionId: string): Promise<{ success: boolean }> {
    if (!sessionId) {
      throw {
        message: 'Session ID is required',
        type: ErrorType.VALIDATION_ERROR,
        retryable: false
      } as APIError
    }
    
    const response = await api.delete(`/sessions/${sessionId}`)
    return validateResponse<{ success: boolean }>(response.data, ['success'])
  },

  async healthCheck(): Promise<HealthResponse> {
    return retryWithBackoff(async () => {
      const response = await api.get('/health')
      return validateResponse<HealthResponse>(response.data, ['status'])
    }, 2)
  }
}

export default apiService