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
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <button class="absolute right-4 top-1/2 transform -translate-y-1/2">
            <svg
              class="w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Category buttons -->
      <div class="flex justify-center gap-4 mb-12 px-4">
        <router-link
          to="/"
          class="px-6 py-2.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-full hover:bg-gray-200 transition"
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
          class="px-6 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-full hover:bg-gray-800 transition"
        >
          Kitaplar
        </router-link>
      </div>
    </section>

    <div class="container mx-auto px-4 pb-8">
      <!-- Book category buttons -->
      <!-- Book category buttons -->
      <div class="mb-8 max-w-6xl mx-auto">
        <div class="flex flex-wrap items-center gap-2 mb-4">
          <button
            @click="categoryType = 'guides'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors border',
              categoryType === 'guides'
                ? 'bg-white border-primary-600 text-primary-600'
                : 'bg-white border-gray-300 text-gray-700',
            ]"
          >
            Okuw gollanmalary
          </button>
          <button
            @click="categoryType = 'subjects'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors border',
              categoryType === 'subjects'
                ? 'bg-white border-primary-600 text-primary-600'
                : 'bg-white border-gray-300 text-gray-700',
            ]"
          >
            Basgyz kitaplar
          </button>
        </div>

        <!-- Subject categories in grid -->
        <div
          v-if="categoryType === 'subjects'"
          class="flex flex-wrap gap-2 mb-6"
        >
          <button
            v-for="cat in subjectCategories"
            :key="cat"
            @click="selectedCategory = selectedCategory === cat ? null : cat"
            :class="[
              'px-3 py-2 text-xs font-medium rounded-lg transition-colors border',
              selectedCategory === cat
                ? 'bg-white border-primary-600 text-primary-600'
                : 'bg-white border-gray-300 text-gray-700 hover:border-gray-400',
            ]"
          >
            {{ cat }}
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <LoadingSpinner v-if="loading" />

      <!-- Books content -->
      <div
        v-else-if="books.length > 0 || recentBooks.length > 0"
        class="space-y-12 max-w-6xl mx-auto"
      >
        <!-- Recently Added -->
        <section v-if="recentBooks.length > 0">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6">
            Soňky goşulanlar
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            <BookCard
              v-for="book in recentBooks"
              :key="book.id"
              :book="book"
              @bookmark="handleBookmark(book.id)"
            />
          </div>
        </section>

        <!-- Most Popular -->
        <section v-if="books.length > 0">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6">
            Köp okalanlar
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            <BookCard
              v-for="book in books"
              :key="book.id"
              :book="book"
              @bookmark="handleBookmark(book.id)"
            />
          </div>
        </section>

        <!-- Pagination -->
        <Pagination
          v-if="totalPages > 1"
          :current-page="currentPage"
          :total-pages="totalPages"
          @update:current-page="handlePageChange"
        />
      </div>

      <!-- Empty state -->
      <div v-else class="text-center py-12 max-w-6xl mx-auto">
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
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Kitap tapylmady</h3>
        <p class="mt-1 text-sm text-gray-500">Başga kategoriýany saýlanyň</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useContentStore } from "@/stores/content";
import { useBookmarkStore } from "@/stores/bookmarks";
import BookCard from "@/components/common/BookCard.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import Pagination from "@/components/common/Pagination.vue";

const router = useRouter();
const contentStore = useContentStore();
const bookmarkStore = useBookmarkStore();

const searchQuery = ref("");
const categoryType = ref("subjects");
const selectedCategory = ref(null);
const currentPage = ref(1);
const recentBooks = ref([]);

const subjectCategories = [
  "TDU",
  "TMDDI",
  "TM we TU",
  "HYY we ÖU",
  "TDLU",
  "TMK",
  "TDMI",
  "TT we II",
  "TOHU",
  "TOHI",
  "TITU",
  "TDMHSI",
  "TDEI",
  "TTT we UKI",
  "TDY we DI",
  "TNGU",
];

const books = computed(() => contentStore.books);
const categories = computed(() => contentStore.bookCategories);
const loading = computed(() => contentStore.loading);
const totalPages = computed(() => {
  const perPage = 12;
  return Math.ceil(contentStore.pagination.books.total / perPage);
});

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: "search", query: { q: searchQuery.value } });
  }
};

const loadBooks = async () => {
  const params = {
    page: currentPage.value,
    ordering: "-views",
  };

  if (selectedCategory.value) {
    params.categories = selectedCategory.value;
  }

  await contentStore.fetchBooks(params);
};

const loadRecentBooks = async () => {
  const params = {
    page: 1,
    page_size: 6,
    ordering: "-created_at",
  };

  if (selectedCategory.value) {
    params.categories = selectedCategory.value;
  }

  const data = await contentStore.fetchBooks(params);
  recentBooks.value = data.results || [];
};

const handlePageChange = (page) => {
  currentPage.value = page;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const handleBookmark = async (bookId) => {
  await bookmarkStore.toggleBookmark(bookId, "book");
  await loadBooks();
  await loadRecentBooks();
};

watch([selectedCategory, categoryType], () => {
  currentPage.value = 1;
  loadBooks();
  loadRecentBooks();
});

watch(currentPage, loadBooks);

onMounted(async () => {
  await contentStore.fetchBookCategories();
  await Promise.all([loadBooks(), loadRecentBooks()]);
});
</script>
