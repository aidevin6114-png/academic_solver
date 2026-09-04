<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-indigo-600">🧮 Math Problem Solver</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/" class="text-gray-700 hover:text-indigo-600 px-3 py-2">Home</router-link>
            <router-link to="/solver" class="text-gray-700 hover:text-indigo-600 px-3 py-2">Solver</router-link>
            <router-link to="/history" class="text-gray-700 hover:text-indigo-600 px-3 py-2">History</router-link>
          </div>
        </div>
      </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
</style>