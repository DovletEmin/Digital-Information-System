<template>
  <div class="min-h-screen">
    <!-- Hero section -->
    <section class="text-center py-8 mt-12">
      <h2 class="text-3xl font-semibold text-gray-900 mb-6">
        Sizi gyzyklandyrýan temalary tapyň
      </h2>

      <!-- Search bar -->
      <div class="max-w-2xl mx-auto px-4 mb-8">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Gözleg"
            class="w-full px-4 py-3 pl-12 border border-gray-300 rounded-3xl focus:outline-none focus:ring-2 focus:ring-primary-500"
            @keyup.enter="handleSearch"
          />
          <svg
            class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <button class="absolute right-4 top-1/2 transform -translate-y-1/2">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Category buttons -->
      <div class="flex justify-center gap-4 mb-12 px-4">
        <router-link
          to="/"
          class="px-6 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-full hover:bg-gray-800 transition"
        >
          Makalalar
        </router-link>
        <router-link
          to="/dissertations"
          class="px-6 py-2.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-full hover:bg-gray-200 transition"
        >
          Dissertasiýalar
        </router-link>
        <router-link
          to="/books"
          class="px-6 py-2.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-full hover:bg-gray-200 transition"
        >
          Kitaplar
        </router-link>
      </div>
    </section>

    <div class="container mx-auto px-4 pb-8">

      <!-- Categories in 3 columns -->
      <div class="mb-12 max-w-6xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-x-24 gap-y-3">
          <div v-for="category in categories" :key="category.id">
            <button
              @click="handleCategoryChange(category.id)"
              :class="[
                'text-sm hover:text-primary-600 transition-colors',
                selectedCategory === category.id
                  ? 'text-primary-600 font-medium'
                  : 'text-gray-700',
              ]"
            >
              {{ category.name }}
            </button>
          </div>
        </div>
      </div>

    <!-- "Iň köp okalanlar" section -->
    <div class="mb-6">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">
        Iň köp okalanlar
      </h2>

        <!-- Loading state -->
        <LoadingSpinner v-if="loading" />

        <!-- Articles list -->
        <div v-else-if="articles.length > 0" class="space-y-4">
          <article
            v-for="article in articles"
            :key="article.id"
            class="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center gap-2 text-xs text-gray-500 mb-2">
                  <span>{{ article.categories?.[0]?.name || "Habarlar" }}</span>
                  <span>•</span>
                  <span>{{ article.institution || "Türkmenistanyň Ylymlar akademiýasy" }}</span>
                </div>

                <router-link
                  :to="{ name: 'article-detail', params: { id: article.id } }"
                  class="block"
                >
                  <h3
                    class="text-lg font-semibold text-gray-900 hover:text-primary-600 mb-2"
                  >
                    {{ article.title }}
                  </h3>
                </router-link>

                <p class="text-sm text-gray-600 mb-3 line-clamp-2">
                  {{
                    article.excerpt ||
                    article.content?.substring(0, 200) + "..."
                  }}
                </p>

                <div class="flex items-center gap-4 text-xs text-gray-500">
                  <span>{{ formatDate(article.publication_date) }}</span>
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {{ article.views || 0 }}
                  </span>
                  <span v-if="article.average_rating" class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    {{ article.average_rating.toFixed(1) }}
                  </span>
                </div>
              </div>

              <!-- Image on the right -->
              <div v-if="article.image" class="ml-4 flex-shrink-0">
                <img
                  :src="article.image"
                  :alt="article.title"
                  class="w-32 h-24 object-cover rounded-lg"
                />
              </div>
div v-if="article.image" class="ml-6 flex-shrink-0">
                <img
                  :src="article.image"
                  :alt="article.title"
                  class="w-32 h-24 object-cover rounded-lg"
                />
              </div>

              <router-link
                :to="{ name: 'article-detail', params: { id: article.id } }"
                class="ml-6 px-6 py-2 bg-primary-600 text-white text-sm rounded-full hover:bg-primary-700 transition whitespace-nowrap"
              >
                Oka
              </router-link>
            </div>
          </articlete:current-page="handlePageChange"
        />
      </div>

      <!-- Empty state -->
      <div v-else class="text-center py-12">
        <svg

        <!-- Empty state -->
            viewBox="0 0 24 24"
        >
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">Makala tapylmady</h3>
          <p class="mt-1 text-sm text-gray-500">Başga kategoriýany saýlanyň</p>
        </div
import { ref, computed, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useContentStore } from "@/stores/content";
import { useBookmarkStore } from "@/stores/bookmarks";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import Pagination from "@/components/common/Pagination.vue";

const router = useRouter();
const contentStore = useContentStore();
const bookmarkStore = useBookmarkStore();

const selectedCategory = ref(null);
const searchQuery = ref("");
const currentPage = ref(1);

const articles = computed(() => contentStore.articles);
const categories = computed(() => contentStore.articleCategories);
const loading = computed(() => contentStore.loading);
const totalPages = computed(() => {
  const perPage = 12;
  return Math.ceil(contentStore.pagination.articles.total / perPage);
});

const formatDate = (date) => {
  return new Date(date).toLocaleDateString("tm-TM", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
};

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: "search", query: { q: searchQuery.value } });
  }
};

const loadArticles = async () => {
  const params = {
    page: currentPage.value,
    ordering: "-views",
  };

  if (selectedCategory.value) {
    params.categories = selectedCategory.value;
  }

  await contentStore.fetchArticles(params);
};

const handleCategoryChange = (categoryId) => {
  selectedCategory.value =
    selectedCategory.value === categoryId ? null : categoryId;
  currentPage.value = 1;
};

const handlePageChange = (page) => {
  currentPage.value = page;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const handleBookmark = async (articleId) => {
  await bookmarkStore.toggleBookmark(articleId, "article");
  await loadArticles();
};

watch(selectedCategory, () => {
  currentPage.value = 1;
  loadArticles();
});

watch(currentPage, loadArticles);

onMounted(async () => {
  await contentStore.fetchArticleCategories();
  await loadArticles();
});
</script>
