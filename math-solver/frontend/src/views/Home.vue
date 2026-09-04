<template>
  <div class="text-center py-12">
    <h1 class="text-4xl font-bold text-gray-900 mb-4">Welcome to Math Problem Solver</h1>
    <p class="text-xl text-gray-600 mb-8">Solve math problems, science questions, and coding challenges with AI</p>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
      <div class="bg-white p-6 rounded-lg shadow-md">
        <div class="text-3xl mb-4">📝</div>
        <h3 class="text-lg font-semibold mb-2">Messaging</h3>
        <p class="text-gray-600">Chat with AI to solve problems step-by-step</p>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-md">
        <div class="text-3xl mb-4">📁</div>
        <h3 class="text-lg font-semibold mb-2">File Upload</h3>
        <p class="text-gray-600">Upload images, PDFs, and documents for analysis</p>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-md">
        <div class="text-3xl mb-4">🖥️</div>
        <h3 class="text-lg font-semibold mb-2">Screen Share</h3>
        <p class="text-gray-600">Share your screen for collaborative problem solving</p>
      </div>
    </div>
    
    <div class="mt-12">
      <router-link to="/solver" class="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
        Start Solving
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>