<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">
      {{ $t("nav.bookmarks") }}
    </h1>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="hasBookmarks" class="space-y-8">
      <!-- Bookmarked Articles -->
      <div v-if="bookmarkedArticles.length > 0">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">
          {{ $t("nav.articles") }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ContentCard
            v-for="article in bookmarkedArticles"
            :key="`article-${article.id}`"
            :item="article"
            detail-route="article-detail"
            @bookmark="removeBookmark(article.id, 'article')"
          />
        </div>
      </div>

      <!-- Bookmarked Books -->
      <div v-if="bookmarkedBooks.length > 0">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">
          {{ $t("nav.books") }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ContentCard
            v-for="book in bookmarkedBooks"
            :key="`book-${book.id}`"
            :item="book"
            detail-route="book-detail"
            @bookmark="removeBookmark(book.id, 'book')"
          />
        </div>
      </div>

      <!-- Bookmarked Dissertations -->
      <div v-if="bookmarkedDissertations.length > 0">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">
          {{ $t("nav.dissertations") }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ContentCard
            v-for="dissertation in bookmarkedDissertations"
            :key="`dissertation-${dissertation.id}`"
            :item="dissertation"
            detail-route="dissertation-detail"
            @bookmark="removeBookmark(dissertation.id, 'dissertation')"
          />
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-12">
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
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
      <h3 class="mt-2 text-sm font-medium text-gray-900">No bookmarks yet</h3>
      <p class="mt-1 text-sm text-gray-500">
        Start bookmarking content to see it here.
      </p>
      <div class="mt-6">
        <router-link
          to="/articles"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
        >
          Browse Articles
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useBookmarkStore } from "@/stores/bookmarks";
import ContentCard from "@/components/common/ContentCard.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

const bookmarkStore = useBookmarkStore();

const loading = computed(() => bookmarkStore.loading);
const bookmarkedArticles = computed(() => bookmarkStore.bookmarkedArticles);
const bookmarkedBooks = computed(() => bookmarkStore.bookmarkedBooks);
const bookmarkedDissertations = computed(
  () => bookmarkStore.bookmarkedDissertations,
);
const hasBookmarks = computed(() => bookmarkStore.allBookmarks.length > 0);

const removeBookmark = async (contentId, contentType) => {
  await bookmarkStore.toggleBookmark(contentId, contentType);
};

onMounted(async () => {
  await bookmarkStore.fetchBookmarks();
});
</script>
