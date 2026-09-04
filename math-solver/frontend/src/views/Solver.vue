<template>
  <div class="h-screen flex flex-col">
    <div class="flex-1 flex overflow-hidden">
      <!-- Chat Section -->
      <div class="flex-1 flex flex-col bg-white">
        <!-- Error Banner -->
        <div v-if="globalError" class="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-red-700 font-medium">Error</p>
              <p class="text-red-600 text-sm">{{ globalError.message }}</p>
              <p v-if="globalError.details" class="text-red-500 text-xs mt-1">{{ globalError.details }}</p>
            </div>
            <button 
              @click="globalError = null"
              class="text-red-400 hover:text-red-600 text-xl"
            >
              ×
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="chatContainer">
          <div v-for="(message, index) in messages" :key="index" 
               :class="['flex gap-2', message.role === 'user' ? 'justify-end' : 'justify-start']">
            <!-- User Message -->
            <div v-if="message.role === 'user'" class="flex gap-2 max-w-[70%]">
              <div class="bg-indigo-600 text-white rounded-lg p-4">
                <div v-if="message.file" class="mb-2">
                  <div class="text-sm font-medium">📎 {{ message.file.name }}</div>
                </div>
                <div class="whitespace-pre-wrap">{{ message.content }}</div>
              </div>
            </div>

            <!-- Assistant Message -->
            <div v-else class="flex gap-2 max-w-[70%]">
              <div class="flex-1">
                <!-- Error State -->
                <div v-if="message.error" class="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div class="flex items-start gap-2">
                    <span class="text-red-500 mt-1">⚠️</span>
                    <div class="flex-1">
                      <p class="font-medium text-red-700">{{ message.error.type }}</p>
                      <p class="text-red-600 text-sm mt-1">{{ message.error.message }}</p>
                      <p v-if="message.error.details" class="text-red-500 text-xs mt-2">{{ message.error.details }}</p>
                      <div v-if="message.error.retryable" class="mt-3 flex gap-2">
                        <button 
                          @click="retryMessage(index)"
                          :disabled="isProcessing"
                          class="text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 disabled:bg-gray-300"
                        >
                          Retry
                        </button>
                        <button 
                          @click="removeMessage(index)"
                          class="text-sm bg-gray-300 text-gray-700 px-3 py-1 rounded hover:bg-gray-400"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Success State -->
                <div v-else class="bg-gray-100 rounded-lg p-4">
                  <div class="whitespace-pre-wrap">{{ message.content }}</div>
                  <div v-if="message.code" class="mt-3 bg-gray-800 text-green-400 p-3 rounded text-sm font-mono overflow-x-auto">
                    <pre>{{ message.code }}</pre>
                  </div>
                  <div v-if="message.steps && message.steps.length > 0" class="mt-3">
                    <p class="font-medium text-sm mb-2">Steps:</p>
                    <ol class="list-decimal list-inside space-y-1">
                      <li v-for="(step, idx) in message.steps" :key="idx" class="text-sm text-gray-700">
                        {{ step }}
                      </li>
                    </ol>
                  </div>
                  <div v-if="message.confidence" class="mt-2 text-xs text-gray-600">
                    Confidence: {{ (message.confidence * 100).toFixed(0) }}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Processing State -->
          <div v-if="isProcessing" class="flex justify-start">
            <div class="bg-gray-100 rounded-lg p-4">
              <div class="flex space-x-2">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Input Section -->
        <div class="border-t border-gray-200 p-4 bg-white">
          <div class="flex space-x-4">
            <input 
              v-model="userInput" 
              @keyup.enter="!isProcessing && sendMessage()"
              type="text" 
              placeholder="Type your math problem or question..."
              class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              :disabled="isProcessing"
            />
            <button 
              @click="sendMessage"
              :disabled="isProcessing || (!userInput.trim() && !uploadedFile)"
              class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              {{ isProcessing ? 'Processing...' : 'Send' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Sidebar -->
      <div class="w-80 bg-gray-50 border-l border-gray-200 p-4 overflow-y-auto">
        <h2 class="text-lg font-semibold mb-4">Tools</h2>
        
        <!-- File Upload -->
        <div class="mb-6">
          <h3 class="font-medium mb-2">📁 Upload File</h3>
          <input 
            type="file" 
            @change="handleFileUpload"
            ref="fileInput"
            class="hidden"
            accept="image/*,.pdf,.doc,.docx,.txt"
          />
          <button 
            @click="$refs.fileInput?.click()"
            :disabled="isProcessing"
            class="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed transition"
          >
            Choose File
          </button>
          <div v-if="uploadedFile" class="mt-2 text-sm text-gray-600">
            Selected: {{ uploadedFile.name }}
          </div>
          <div v-if="fileError" class="mt-2 text-sm text-red-600">
            {{ fileError }}
          </div>
        </div>
        
        <!-- Screen Share -->
        <div class="mb-6">
          <h3 class="font-medium mb-2">🖥️ Screen Share</h3>
          <button 
            @click="startScreenShare"
            :disabled="isProcessing || isScreenSharing"
            class="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed transition"
          >
            {{ isScreenSharing ? 'Stop Sharing' : 'Start Screen Share' }}
          </button>
        </div>
        
        <!-- Screen Share Container -->
        <div v-if="isScreenSharing" class="mb-4">
          <div id="jitsi-container" class="w-full h-64 bg-gray-200 rounded-lg"></div>
        </div>
        
        <!-- AI Capabilities -->
        <div class="mb-6">
          <h3 class="font-medium mb-2">🤖 AI Capabilities</h3>
          <div class="space-y-2">
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="aiCapabilities.webSearch" class="rounded" />
              <span class="text-sm">Web Search</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="aiCapabilities.codeExecution" class="rounded" />
              <span class="text-sm">Code Execution</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="aiCapabilities.stepByStep" class="rounded" />
              <span class="text-sm">Step-by-Step Explanation</span>
            </label>
          </div>
        </div>
        
        <!-- Session Management -->
        <div class="mb-6">
          <h3 class="font-medium mb-2">📊 Session</h3>
          <button 
            @click="clearSession"
            class="w-full text-left text-sm bg-white border border-gray-300 rounded px-3 py-2 hover:bg-gray-50 transition"
          >
            Clear Conversation
          </button>
        </div>
        
        <!-- Quick Actions -->
        <div>
          <h3 class="font-medium mb-2">⚡ Quick Actions</h3>
          <div class="space-y-2">
            <button 
              @click="quickAction('Solve this equation: ')"
              class="w-full text-left text-sm bg-white border border-gray-300 rounded px-3 py-2 hover:bg-gray-50 transition"
            >
              📐 Solve Equation
            </button>
            <button 
              @click="quickAction('Explain this concept: ')"
              class="w-full text-left text-sm bg-white border border-gray-300 rounded px-3 py-2 hover:bg-gray-50 transition"
            >
              📚 Explain Concept
            </button>
            <button 
              @click="quickAction('Write code to: ')"
              class="w-full text-left text-sm bg-white border border-gray-300 rounded px-3 py-2 hover:bg-gray-50 transition"
            >
              💻 Write Code
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import apiService, { ErrorType, APIError } from '../services/apiService'

interface MessageContent {
  role: 'user' | 'assistant'
  content: string
  file?: { name: string }
  code?: string
  steps?: string[]
  confidence?: number
  error?: APIError
}

interface UserMessage {
  content: string
  file?: File
  capabilities: {
    webSearch: boolean
    codeExecution: boolean
    stepByStep: boolean
  }
}

const messages = ref<MessageContent[]>([])
const userInput = ref('')
const isProcessing = ref(false)
const uploadedFile = ref<File | null>(null)
const fileError = ref('')
const isScreenSharing = ref(false)
const chatContainer = ref<HTMLElement>()
const fileInput = ref<HTMLInputElement>()
const globalError = ref<APIError | null>(null)
const lastUserMessage = ref<UserMessage | null>(null)

const aiCapabilities = ref({
  webSearch: true,
  codeExecution: true,
  stepByStep: true
})

const sendMessage = async () => {
  if (!userInput.value.trim() && !uploadedFile.value) return
  
  const messageContent = userInput.value
  const currentFile = uploadedFile.value
  
  const userMessage: UserMessage = {
    content: messageContent,
    file: currentFile,
    capabilities: aiCapabilities.value
  }
  
  lastUserMessage.value = userMessage
  
  messages.value.push({
    role: 'user',
    content: messageContent,
    file: currentFile ? { name: currentFile.name } : undefined
  })
  
  userInput.value = ''
  uploadedFile.value = null
  fileError.value = ''
  globalError.value = null
  
  await scrollToBottom()
  
  await processMessage(userMessage)
}

const processMessage = async (userMessage: UserMessage) => {
  isProcessing.value = true
  
  try {
    const response = await apiService.solveProblem({
      problem: userMessage.content,
      file: userMessage.file,
      capabilities: userMessage.capabilities
    })
    
    if (response.success) {
      messages.value.push({
        role: 'assistant',
        content: response.solution || 'No solution generated',
        code: response.code,
        steps: response.steps,
        confidence: response.confidence
      })
      
      saveToHistory(userMessage.content, response.solution || '')
    } else {
      const error: APIError = {
        message: response.error || 'Failed to process your request',
        type: response.errorType || ErrorType.AI_ERROR,
        retryable: true
      }
      messages.value.push({
        role: 'assistant',
        content: '',
        error
      })
    }
    
    await scrollToBottom()
  } catch (error: any) {
    const apiError: APIError = error.retryable !== undefined ? error : {
      message: error.message || 'An unexpected error occurred',
      type: ErrorType.INTERNAL_ERROR,
      retryable: false
    }
    
    messages.value.push({
      role: 'assistant',
      content: '',
      error: apiError
    })
    
    globalError.value = apiError
  } finally {
    isProcessing.value = false
  }
}

const retryMessage = async (messageIndex: number) => {
  // Remove the error message
  messages.value.splice(messageIndex, 1)
  
  // Retry the last user message if available
  if (lastUserMessage.value) {
    await processMessage(lastUserMessage.value)
  }
}

const removeMessage = (messageIndex: number) => {
  messages.value.splice(messageIndex, 1)
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    fileError.value = ''
    
    // Client-side validation
    const maxSizeMB = 50
    const fileSizeMB = file.size / (1024 * 1024)
    
    if (fileSizeMB > maxSizeMB) {
      fileError.value = `File size (${fileSizeMB.toFixed(2)}MB) exceeds maximum (${maxSizeMB}MB)`
      uploadedFile.value = null
      return
    }
    
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    
    if (!allowedTypes.includes(file.type)) {
      fileError.value = `File type not supported. Allowed: images, PDF, text, Word documents`
      uploadedFile.value = null
      return
    }
    
    uploadedFile.value = file
  }
}

const startScreenShare = async () => {
  if (!isScreenSharing.value) {
    try {
      isScreenSharing.value = true
      // Implement screen share logic
    } catch (error) {
      globalError.value = {
        message: 'Failed to start screen sharing',
        type: ErrorType.INTERNAL_ERROR,
        retryable: false
      }
      isScreenSharing.value = false
    }
  } else {
    isScreenSharing.value = false
    const container = document.getElementById('jitsi-container')
    if (container) {
      container.innerHTML = ''
    }
  }
}

const quickAction = (prefix: string) => {
  userInput.value = prefix
}

const clearSession = () => {
  if (confirm('Clear all messages?')) {
    messages.value = []
    localStorage.removeItem('mathSolverSession')
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const saveToHistory = (problem: string, solution: string) => {
  const history = JSON.parse(localStorage.getItem('mathSolverHistory') || '[]')
  history.push({
    problem,
    solution,
    date: new Date().toISOString()
  })
  localStorage.setItem('mathSolverHistory', JSON.stringify(history))
}

onMounted(() => {
  const savedSession = localStorage.getItem('mathSolverSession')
  if (savedSession) {
    try {
      messages.value = JSON.parse(savedSession)
    } catch (e) {
      console.error('Failed to load session:', e)
    }
  }
})

// Save session to localStorage
const saveSession = () => {
  localStorage.setItem('mathSolverSession', JSON.stringify(messages.value))
}

// Watch for changes and save
watch(messages, saveSession, { deep: true })
</script>