<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading state -->
    <LoadingSpinner v-if="loading" />

    <!-- Dissertation content -->
    <div v-else-if="dissertation" class="max-w-4xl mx-auto">
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

      <!-- Dissertation header -->
      <div class="bg-white rounded-lg shadow-sm p-8 mb-6">
        <!-- Title -->
        <h1 class="text-3xl font-bold text-gray-900 mb-4">
          {{ dissertation.title }}
        </h1>

        <!-- Meta info -->
        <div class="flex items-center justify-between mb-6 pb-6 border-b">
          <div class="space-y-2">
            <p class="text-gray-700">
              <span class="font-semibold">{{ $t("content.author") }}:</span>
              {{ dissertation.author }}
            </p>
            <p
              v-if="dissertation.author_workplace"
              class="text-gray-600 text-sm"
            >
              {{ dissertation.author_workplace }}
            </p>
            <p class="text-gray-600 text-sm">
              <span class="font-semibold"
                >{{ $t("content.publishedDate") }}:</span
              >
              {{ formatDate(dissertation.publication_date) }}
            </p>
          </div>

          <div class="flex items-center space-x-4">
            <!-- Bookmark button -->
            <button
              @click="handleBookmark"
              class="p-3 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <svg
                class="w-6 h-6"
                :class="
                  dissertation.is_bookmarked
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
        </div>

        <!-- Stats -->
        <div class="flex items-center space-x-6 text-sm text-gray-600 mb-6">
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
            <span>{{ dissertation.views }} {{ $t("content.views") }}</span>
          </div>

          <div
            v-if="dissertation.average_rating"
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
              >{{ dissertation.average_rating.toFixed(1) }} ({{
                dissertation.rating_count
              }})</span
            >
          </div>
        </div>

        <!-- Categories -->
        <div
          v-if="dissertation.categories && dissertation.categories.length > 0"
          class="flex flex-wrap gap-2 mb-6"
        >
          <span
            v-for="category in dissertation.categories"
            :key="category.id"
            class="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
          >
            {{ category.name }}
          </span>
        </div>

        <!-- Abstract -->
        <div v-if="dissertation.abstract" class="mb-6">
          <h3 class="text-lg font-semibold mb-2">Abstract</h3>
          <div class="prose prose-lg max-w-none text-gray-700">
            {{ dissertation.abstract }}
          </div>
        </div>

        <!-- Dissertation content -->
        <div
          class="prose prose-lg max-w-none"
          v-html="dissertation.content"
        ></div>
      </div>

      <!-- Rating section -->
      <div
        v-if="authStore.isAuthenticated"
        class="bg-white rounded-lg shadow-sm p-6 mb-6"
      >
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

    <!-- Error state -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600">{{ $t("content.dissertationNotFound") }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { dissertationService } from "@/services/content";
import { ratingService } from "@/services/interactions";
import { useBookmarkStore } from "@/stores/bookmarks";
import { useAuthStore } from "@/stores/auth";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

const route = useRoute();
const bookmarkStore = useBookmarkStore();
const authStore = useAuthStore();

const dissertation = ref(null);
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
  await bookmarkStore.toggleBookmark(dissertation.value.id, "dissertation");
  dissertation.value.is_bookmarked = !dissertation.value.is_bookmarked;
};

const handleRate = async (rating) => {
  try {
    await ratingService.rateContent(
      dissertation.value.id,
      "dissertation",
      rating,
    );
    userRating.value = rating;

    const updated = await dissertationService.getDissertation(route.params.id);
    dissertation.value.average_rating = updated.average_rating;
    dissertation.value.rating_count = updated.rating_count;
  } catch (error) {
    console.error("Failed to rate dissertation:", error);
  }
};

onMounted(async () => {
  try {
    dissertation.value = await dissertationService.getDissertation(
      route.params.id,
    );
    await dissertationService.registerView(route.params.id);

    if (authStore.isAuthenticated) {
      userRating.value =
        (await ratingService.getUserRating(
          dissertation.value.id,
          "dissertation",
        )) || 0;
    }
  } catch (error) {
    console.error("Failed to load dissertation:", error);
  } finally {
    loading.value = false;
  }
});
</script>
