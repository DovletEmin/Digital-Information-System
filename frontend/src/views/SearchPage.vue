<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-3xl mx-auto">
      <!-- Search header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">
          {{ $t("search.searchFor") }} "{{ query }}"
        </h1>

        <!-- Search filters -->
        <div class="flex flex-wrap gap-3">
          <button
            @click="contentTypeFilter = null"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              !contentTypeFilter
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50',
            ]"
          >
            {{ $t("filters.all") }}
          </button>
          <button
            @click="contentTypeFilter = 'article'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              contentTypeFilter === 'article'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50',
            ]"
          >
            {{ $t("nav.articles") }}
          </button>
          <button
            @click="contentTypeFilter = 'book'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              contentTypeFilter === 'book'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50',
            ]"
          >
            {{ $t("nav.books") }}
          </button>
          <button
            @click="contentTypeFilter = 'dissertation'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              contentTypeFilter === 'dissertation'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50',
            ]"
          >
            {{ $t("nav.dissertations") }}
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <LoadingSpinner v-if="loading" />

      <!-- Results -->
      <div v-else-if="results.length > 0" class="space-y-6">
        <p class="text-gray-600">
          {{ $t("search.results") }}: {{ totalResults }}
        </p>

        <div class="space-y-4">
          <div
            v-for="result in results"
            :key="`${result.content_type}-${result.id}`"
            class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
          >
            <router-link :to="getDetailRoute(result)" class="block">
              <!-- Type badge -->
              <span
                class="inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium mb-2"
              >
                {{ getTypeName(result.content_type) }}
              </span>

              <!-- Title -->
              <h3
                class="text-xl font-semibold text-gray-900 hover:text-primary-600 mb-2"
              >
                {{ result.title }}
              </h3>

              <!-- Author -->
              <p class="text-sm text-gray-600 mb-2">
                {{ result.author }}
              </p>

              <!-- Excerpt -->
              <p v-if="result.excerpt" class="text-gray-700 line-clamp-3 mb-3">
                {{ result.excerpt }}
              </p>

              <!-- Meta -->
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <div class="flex items-center space-x-1">
                  <svg
                    class="w-4 h-4"
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
                  <span>{{ result.views }}</span>
                </div>
                <div
                  v-if="result.average_rating"
                  class="flex items-center space-x-1"
                >
                  <svg
                    class="w-4 h-4 text-yellow-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                    />
                  </svg>
                  <span>{{ result.average_rating.toFixed(1) }}</span>
                </div>
              </div>
            </router-link>
          </div>
        </div>

        <!-- Pagination -->
        <Pagination
          v-if="totalPages > 1"
          :current-page="currentPage"
          :total-pages="totalPages"
          @update:current-page="handlePageChange"
        />
      </div>

      <!-- No results -->
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
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">
          {{ $t("search.noResults") }}
        </h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ $t("content.tryDifferentFilter") }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useSearchStore } from "@/stores/search";
import { useI18n } from "vue-i18n";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import Pagination from "@/components/common/Pagination.vue";

const route = useRoute();
const searchStore = useSearchStore();
const { t } = useI18n();

const contentTypeFilter = ref(null);
const currentPage = ref(1);

const query = computed(() => route.query.q || "");
const results = computed(() => searchStore.results);
const loading = computed(() => searchStore.loading);
const totalResults = computed(() => searchStore.pagination.total);
const totalPages = computed(() => Math.ceil(totalResults.value / 10));

const performSearch = async () => {
  if (!query.value) return;

  const filters = {};
  if (contentTypeFilter.value) {
    filters.content_type = contentTypeFilter.value;
  }

  await searchStore.search(query.value, filters, currentPage.value);
};

const getDetailRoute = (result) => {
  const routes = {
    article: "article-detail",
    book: "book-detail",
    dissertation: "dissertation-detail",
  };
  return { name: routes[result.content_type], params: { id: result.id } };
};

const getTypeName = (type) => {
  const names = {
    article: t("nav.articles"),
    book: t("nav.books"),
    dissertation: t("nav.dissertations"),
  };
  return names[type] || type;
};

const handlePageChange = (page) => {
  currentPage.value = page;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

watch([() => route.query.q, contentTypeFilter], () => {
  currentPage.value = 1;
  performSearch();
});

watch(currentPage, performSearch);

onMounted(() => {
  if (query.value) {
    performSearch();
  }
});
</script>
