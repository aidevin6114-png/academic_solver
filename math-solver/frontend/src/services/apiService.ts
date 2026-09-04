import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  file?: { name: string; data: string }
}

export interface SolveRequest {
  problem: string
  file?: File
  capabilities: {
    webSearch: boolean
    codeExecution: boolean
    stepByStep: boolean
  }
}

export interface SolveResponse {
  solution: string
  steps?: string[]
  code?: string
  error?: string
}

export const apiService = {
  async sendMessage(message: ChatMessage): Promise<SolveResponse> {
    const response = await api.post('/chat/send', message)
    return response.data
  },

  async uploadFile(file: File): Promise<{ fileId: string }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async solveProblem(request: SolveRequest): Promise<SolveResponse> {
    const formData = new FormData()
    formData.append('problem', request.problem)
    formData.append('capabilities', JSON.stringify(request.capabilities))
    
    if (request.file) {
      formData.append('file', request.file)
    }
    
    const response = await api.post('/solve/problem', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async createScreenShareSession(): Promise<{ sessionId: string; url: string }> {
    const response = await api.post('/screenshare/create')
    return response.data
  },

  async getSessionHistory(sessionId: string): Promise<ChatMessage[]> {
    const response = await api.get(`/sessions/${sessionId}`)
    return response.data
  },

  healthCheck(): Promise<{ status: string }> {
    return api.get('/health').then(response => response.data)
  }
}

export default apiService