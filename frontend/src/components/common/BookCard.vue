<template>
  <router-link
    :to="{ name: 'book-detail', params: { id: book.id } }"
    class="group block"
  >
    <div
      class="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow"
    >
      <!-- Book Cover -->
      <div class="relative aspect-[2/3] overflow-hidden bg-gray-100">
        <img
          v-if="book.cover_image || book.image"
          :src="book.cover_image || book.image"
          :alt="book.title"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div
          v-else
          class="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center"
        >
          <svg
            class="w-16 h-16 text-white opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
        </div>

        <!-- Bookmark button -->
        <button
          @click.prevent="$emit('bookmark', book.id)"
          class="absolute top-2 right-2 p-2 bg-white rounded-full shadow-md hover:bg-gray-50 transition-colors"
        >
          <svg
            class="w-5 h-5"
            :class="
              book.is_bookmarked
                ? 'text-primary-600 fill-current'
                : 'text-gray-400'
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
            />
          </svg>
        </button>
      </div>

      <!-- Book Info -->
      <div class="p-3">
        <h3
          class="font-semibold text-sm text-gray-900 line-clamp-2 group-hover:text-primary-600 transition-colors mb-1"
        >
          {{ book.title }}
        </h3>
        <p class="text-xs text-gray-600 line-clamp-1">
          {{ book.author }}
        </p>
      </div>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  book: {
    type: Object,
    required: true,
  },
});

defineEmits(["bookmark"]);
</script>
