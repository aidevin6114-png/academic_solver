<template>
  <div class="h-screen flex flex-col">
    <div class="flex-1 flex overflow-hidden">
      <!-- Chat Section -->
      <div class="flex-1 flex flex-col bg-white">
        <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="chatContainer">
          <div v-for="(message, index) in messages" :key="index" 
               :class="['flex', message.role === 'user' ? 'justify-end' : 'justify-start']">
            <div :class="['max-w-[70%] rounded-lg p-4', 
                       message.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-900']">
              <div v-if="message.file" class="mb-2">
                <div class="text-sm font-medium">📎 {{ message.file.name }}</div>
              </div>
              <div class="whitespace-pre-wrap">{{ message.content }}</div>
              <div v-if="message.code" class="mt-2 bg-gray-800 text-green-400 p-3 rounded text-sm font-mono">
                <pre>{{ message.code }}</pre>
              </div>
            </div>
          </div>
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
        <div class="border-t border-gray-200 p-4">
          <div class="flex space-x-4">
            <input 
              v-model="userInput" 
              @keyup.enter="sendMessage"
              type="text" 
              placeholder="Type your math problem or question..."
              class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              :disabled="isProcessing"
            />
            <button 
              @click="sendMessage"
              :disabled="isProcessing || !userInput.trim()"
              class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Send
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
            @click="$refs.fileInput.click()"
            :disabled="isProcessing"
            class="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            Choose File
          </button>
          <div v-if="uploadedFile" class="mt-2 text-sm text-gray-600">
            Selected: {{ uploadedFile.name }}
          </div>
        </div>
        
        <!-- Screen Share -->
        <div class="mb-6">
          <h3 class="font-medium mb-2">🖥️ Screen Share</h3>
          <button 
            @click="startScreenShare"
            :disabled="isProcessing || isScreenSharing"
            class="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
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
        
        <!-- Quick Actions -->
        <div>
          <h3 class="font-medium mb-2">⚡ Quick Actions</h3>
          <div class="space-y-2">
            <button 
              @click="quickAction('Solve this equation: ')"
              class="w-full text-left text-sm bg-white border border-gray-300 rounded px-3 py-2 hover:bg-gray-50"
            >
              📐 Solve Equation
            </button>
            <button 
              @click="quickAction('Explain this concept: ')"
              class="w-full text-left text-sm bg-white border border-gray-300 rounded px-3 py-2 hover:bg-gray-50"
            >
              📚 Explain Concept
            </button>
            <button 
              @click="quickAction('Write code to: ')"
              class="w-full text-left text-sm bg-white border border-gray-300 rounded px-3 py-2 hover:bg-gray-50"
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
import apiService from '../services/apiService'
import aiService from '../services/aiService'
import fileService from '../services/fileService'
import screenShareService from '../services/screenShareService'

interface Message {
  role: 'user' | 'assistant'
  content: string
  file?: { name: string }
  code?: string
}

const messages = ref<Message[]>([])
const userInput = ref('')
const isProcessing = ref(false)
const uploadedFile = ref<File | null>(null)
const isScreenSharing = ref(false)
const chatContainer = ref<HTMLElement>()
const fileInput = ref<HTMLInputElement>()

const aiCapabilities = ref({
  webSearch: true,
  codeExecution: true,
  stepByStep: true
})

const sendMessage = async () => {
  if (!userInput.value.trim() && !uploadedFile.value) return
  
  const messageContent = userInput.value
  const fileData = uploadedFile.value ? { name: uploadedFile.value.name } : undefined
  
  messages.value.push({
    role: 'user',
    content: messageContent,
    file: fileData
  })
  
  const currentFile = uploadedFile.value
  userInput.value = ''
  uploadedFile.value = null
  
  await scrollToBottom()
  
  isProcessing.value = true
  
  try {
    // Use AI service to solve the problem
    const response = await aiService.solveProblem({
      problem: messageContent,
      capabilities: aiCapabilities.value,
      file: currentFile || undefined
    })
    
    messages.value.push({
      role: 'assistant',
      content: response.solution,
      code: response.code
    })
    
    // Save to history
    saveToHistory(messageContent, response.solution)
    
    await scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.'
    })
  } finally {
    isProcessing.value = false
  }
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    
    // Validate file
    const validation = fileService.validateFile(file)
    if (!validation.valid) {
      alert(validation.error)
      return
    }
    
    uploadedFile.value = file
  }
}

const startScreenShare = async () => {
  if (!isScreenSharing.value) {
    try {
      isScreenSharing.value = true
      const session = await screenShareService.createSession()
      const roomName = screenShareService.generateRoomName()
      
      setTimeout(() => {
        screenShareService.loadJitsi('jitsi-container', roomName)
      }, 100)
    } catch (error) {
      console.error('Failed to start screen share:', error)
      alert('Failed to start screen sharing. Please try again.')
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
    type: determineProblemType(problem),
    date: new Date().toISOString()
  })
  localStorage.setItem('mathSolverHistory', JSON.stringify(history))
}

const determineProblemType = (problem: string): 'math' | 'science' | 'coding' | 'general' => {
  const lowerProblem = problem.toLowerCase()
  if (lowerProblem.match(/\d+|equation|solve|calculate|derivative|integral/)) return 'math'
  if (lowerProblem.match(/physics|chemistry|biology|science/)) return 'science'
  if (lowerProblem.match(/code|programming|function|algorithm|python|javascript/)) return 'coding'
  return 'general'
}

onMounted(() => {
  // Load session from localStorage if needed
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