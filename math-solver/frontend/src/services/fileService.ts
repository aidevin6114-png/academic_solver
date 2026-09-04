import apiService from './apiService'

export interface FileUploadResponse {
  fileId: string
  filename: string
  file_type: string
  status: string
}

export const fileService = {
  async uploadFile(file: File): Promise<FileUploadResponse> {
    try {
      return await apiService.uploadFile(file)
    } catch (error) {
      console.error('File upload error:', error)
      throw new Error('Failed to upload file')
    }
  },

  validateFile(file: File): { valid: boolean; error?: string } {
    const maxSize = 10 * 1024 * 1024 // 10MB
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 
                         'application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'text/plain']
    
    if (file.size > maxSize) {
      return { valid: false, error: 'File size exceeds 10MB limit' }
    }
    
    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: 'File type not supported' }
    }
    
    return { valid: true }
  },

  getFileType(file: File): string {
    if (file.type.startsWith('image/')) return 'image'
    if (file.type === 'application/pdf') return 'pdf'
    if (file.type.includes('word')) return 'document'
    if (file.type === 'text/plain') return 'text'
    return 'unknown'
  },

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }
}

export default fileService