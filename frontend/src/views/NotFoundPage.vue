<template>
  <div class="container mx-auto px-4 py-16 text-center">
    <div class="max-w-md mx-auto">
      <svg
        class="mx-auto h-24 w-24 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <h1 class="mt-6 text-4xl font-bold text-gray-900">404</h1>
      <p class="mt-4 text-xl text-gray-600">Sahypa tapylmady</p>
      <p class="mt-2 text-gray-500">
        Siziň gözleýän sahypaňyz ýok ýa-da pozuldy.
      </p>
      <div class="mt-8">
        <router-link
          to="/"
          class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700"
        >
          Baş sahypa
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup></script>
