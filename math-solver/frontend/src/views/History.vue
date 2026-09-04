<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Problem History</h1>
    
    <div v-if="history.length === 0" class="text-center py-12 text-gray-500">
      <p>No problems solved yet. Start solving to see your history here.</p>
    </div>
    
    <div v-else class="space-y-4">
      <div v-for="(item, index) in history" :key="index" class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="font-semibold text-lg">{{ item.problem }}</h3>
            <p class="text-sm text-gray-500">{{ item.date }}</p>
          </div>
          <span class="px-3 py-1 rounded-full text-sm"
                :class="item.type === 'math' ? 'bg-blue-100 text-blue-800' : 
                       item.type === 'science' ? 'bg-green-100 text-green-800' : 
                       'bg-purple-100 text-purple-800'">
            {{ item.type }}
          </span>
        </div>
        
        <div class="bg-gray-50 rounded p-4">
          <h4 class="font-medium mb-2">Solution:</h4>
          <p class="text-gray-700 whitespace-pre-wrap">{{ item.solution }}</p>
        </div>
        
        <div class="mt-4 flex space-x-2">
          <button class="text-indigo-600 hover:text-indigo-800 text-sm">View Details</button>
          <button class="text-gray-600 hover:text-gray-800 text-sm">Share</button>
          <button @click="deleteItem(index)" class="text-red-600 hover:text-red-800 text-sm">Delete</button>
        </div>
      </div>
    </div>
    
    <div class="mt-6">
      <button 
        @click="clearHistory"
        v-if="history.length > 0"
        class="text-red-600 hover:text-red-800 text-sm"
      >
        Clear All History
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface HistoryItem {
  problem: string
  solution: string
  type: 'math' | 'science' | 'coding' | 'general'
  date: string
}

const history = ref<HistoryItem[]>([])

const loadHistory = () => {
  const savedHistory = localStorage.getItem('mathSolverHistory')
  if (savedHistory) {
    try {
      history.value = JSON.parse(savedHistory)
    } catch (e) {
      console.error('Failed to load history:', e)
    }
  }
}

const deleteItem = (index: number) => {
  history.value.splice(index, 1)
  saveHistory()
}

const clearHistory = () => {
  if (confirm('Are you sure you want to clear all history?')) {
    history.value = []
    saveHistory()
  }
}

const saveHistory = () => {
  localStorage.setItem('mathSolverHistory', JSON.stringify(history.value))
}

onMounted(() => {
  loadHistory()
})
</script>