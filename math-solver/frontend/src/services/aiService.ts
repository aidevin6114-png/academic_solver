import apiService from './apiService'

export interface AICapabilities {
  webSearch: boolean
  codeExecution: boolean
  stepByStep: boolean
}

export interface AIRequest {
  problem: string
  capabilities: AICapabilities
  file?: File
}

export interface AIResponse {
  solution: string
  steps?: string[]
  code?: string
  error?: string
}

export const aiService = {
  async solveProblem(request: AIRequest): Promise<AIResponse> {
    try {
      return await apiService.solveProblem({
        problem: request.problem,
        capabilities: request.capabilities,
        file: request.file
      })
    } catch (error) {
      console.error('AI service error:', error)
      return {
        solution: 'Sorry, I encountered an error while solving the problem.',
        error: 'Failed to connect to AI service'
      }
    }
  },

  async chatWithAI(message: string, context?: string[]): Promise<string> {
    try {
      const response = await apiService.sendMessage({
        role: 'user',
        content: message
      })
      return response.solution
    } catch (error) {
      console.error('Chat error:', error)
      return 'Sorry, I encountered an error. Please try again.'
    }
  },

  generatePrompt(problem: string, capabilities: AICapabilities): string {
    let prompt = `Solve this problem: ${problem}\n\n`
    
    if (capabilities.webSearch) {
      prompt += "Feel free to search the web for current information if needed.\n"
    }
    
    if (capabilities.codeExecution) {
      prompt += "You can write and execute code to solve this problem.\n"
    }
    
    if (capabilities.stepByStep) {
      prompt += "Please provide a step-by-step explanation of your solution.\n"
    }
    
    return prompt
  }
}

export default aiService