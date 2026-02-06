<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading state -->
    <LoadingSpinner v-if="loading" />

    <!-- Book content -->
    <div v-else-if="book" class="max-w-5xl mx-auto">
      <!-- Back button -->
      <button
        @click="$router.back()"
        class="flex items-center text-primary-600 hover:text-primary-700 mb-6"
      >
        <svg
          class="w-5 h-5 mr-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 19l-7-7 7-7"
          />
        </svg>
        {{ $t("common.back") }}
      </button>

      <div class="bg-white rounded-lg shadow-sm p-8">
        <div class="flex flex-col md:flex-row gap-8">
          <!-- Book Cover -->
          <div class="md:w-1/3">
            <div class="sticky top-20">
              <div class="aspect-[2/3] rounded-lg overflow-hidden shadow-lg">
                <img
                  v-if="book.cover_image || book.image"
                  :src="book.cover_image || book.image"
                  :alt="book.title"
                  class="w-full h-full object-cover"
                />
                <div
                  v-else
                  class="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center"
                >
                  <svg
                    class="w-24 h-24 text-white opacity-50"
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
              </div>

              <!-- Actions -->
              <div class="mt-6 space-y-3">
                <button
                  @click="handleBookmark"
                  :class="[
                    'w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors',
                    book.is_bookmarked
                      ? 'bg-primary-600 text-white hover:bg-primary-700'
                      : 'bg-white border-2 border-primary-600 text-primary-600 hover:bg-primary-50',
                  ]"
                >
                  <svg
                    class="w-5 h-5"
                    :class="book.is_bookmarked ? 'fill-current' : ''"
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
                  <span>{{ book.is_bookmarked ? "Saved" : "Save" }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Book Details -->
          <div class="md:w-2/3">
            <!-- Title -->
            <h1 class="text-3xl font-bold text-gray-900 mb-4">
              {{ book.title }}
            </h1>

            <!-- Author -->
            <p class="text-xl text-gray-700 mb-6">
              <span class="font-semibold">{{ $t("content.author") }}:</span>
              {{ book.author }}
            </p>

            <!-- Stats -->
            <div
              class="flex items-center space-x-6 text-sm text-gray-600 mb-6 pb-6 border-b"
            >
              <div class="flex items-center space-x-2">
                <svg
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
                <span>{{ book.views }} {{ $t("content.views") }}</span>
              </div>

              <div
                v-if="book.average_rating"
                class="flex items-center space-x-2"
              >
                <svg
                  class="w-5 h-5 text-yellow-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                  />
                </svg>
                <span
                  >{{ book.average_rating.toFixed(1) }} ({{
                    book.rating_count
                  }})</span
                >
              </div>

              <div class="flex items-center space-x-2">
                <svg
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span>{{ formatDate(book.publication_date) }}</span>
              </div>
            </div>

            <!-- Categories -->
            <div
              v-if="book.categories && book.categories.length > 0"
              class="flex flex-wrap gap-2 mb-6"
            >
              <span
                v-for="category in book.categories"
                :key="category.id"
                class="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
              >
                {{ category.name }}
              </span>
            </div>

            <!-- Description -->
            <div v-if="book.description" class="mb-6">
              <h3 class="text-lg font-semibold mb-2">
                {{ $t("content.description") }}
              </h3>
              <p class="text-gray-700 leading-relaxed">
                {{ book.description }}
              </p>
            </div>

            <!-- Book content -->
            <div class="prose prose-lg max-w-none" v-html="book.content"></div>

            <!-- Rating section -->
            <div v-if="authStore.isAuthenticated" class="mt-8 pt-6 border-t">
              <h3 class="text-lg font-semibold mb-4">
                {{ $t("content.rateArticle") }}
              </h3>
              <div class="flex items-center space-x-2">
                <button
                  v-for="star in 5"
                  :key="star"
                  @click="handleRate(star)"
                  class="focus:outline-none"
                >
                  <svg
                    class="w-8 h-8 transition-colors"
                    :class="
                      star <= (userRating || 0)
                        ? 'text-yellow-400 fill-current'
                        : 'text-gray-300'
                    "
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600">{{ $t("content.bookNotFound") }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { bookService } from "@/services/content";
import { ratingService } from "@/services/interactions";
import { useBookmarkStore } from "@/stores/bookmarks";
import { useAuthStore } from "@/stores/auth";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

const route = useRoute();
const bookmarkStore = useBookmarkStore();
const authStore = useAuthStore();

const book = ref(null);
const loading = ref(true);
const userRating = ref(0);

const formatDate = (date) => {
  return new Date(date).toLocaleDateString("tm-TM", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const handleBookmark = async () => {
  await bookmarkStore.toggleBookmark(book.value.id, "book");
  book.value.is_bookmarked = !book.value.is_bookmarked;
};

const handleRate = async (rating) => {
  try {
    await ratingService.rateContent(book.value.id, "book", rating);
    userRating.value = rating;

    const updated = await bookService.getBook(route.params.id);
    book.value.average_rating = updated.average_rating;
    book.value.rating_count = updated.rating_count;
  } catch (error) {
    console.error("Failed to rate book:", error);
  }
};

onMounted(async () => {
  try {
    book.value = await bookService.getBook(route.params.id);
    await bookService.registerView(route.params.id);

    if (authStore.isAuthenticated) {
      userRating.value =
        (await ratingService.getUserRating(book.value.id, "book")) || 0;
    }
  } catch (error) {
    console.error("Failed to load book:", error);
  } finally {
    loading.value = false;
  }
});
</script>
