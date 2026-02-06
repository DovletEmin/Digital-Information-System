<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200"
    style="height: 70px"
  >
    <div class="h-full px-12 flex items-center justify-between">
      <!-- Logo -->
      <router-link
        to="/"
        class="text-2xl font-semibold text-gray-900 hover:text-primary-600"
      >
        SMU
      </router-link>

      <!-- Navigation tabs -->
      <nav class="flex items-center gap-8">
        <router-link
          to="/"
          class="text-base text-gray-700 hover:text-gray-900 font-medium"
          active-class="text-gray-900"
        >
          {{ $t("nav.articles") }}
        </router-link>
        <router-link
          to="/dissertations"
          class="text-base text-gray-700 hover:text-gray-900 font-medium"
          active-class="text-gray-900"
        >
          {{ $t("nav.dissertations") }}
        </router-link>
        <router-link
          to="/books"
          class="text-base text-gray-700 hover:text-gray-900 font-medium"
          active-class="text-gray-900"
        >
          {{ $t("nav.books") }}
        </router-link>
      </nav>

      <!-- Search and language -->
      <div class="flex items-center gap-4">
        <!-- Search button -->
        <button
          @click="showSearch = !showSearch"
          class="p-2 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-100"
        >
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
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </button>

        <!-- Language -->
        <LanguageSwitcher />

        <!-- User -->
        <div v-if="authStore.isAuthenticated" class="flex items-center gap-3">
          <router-link
            to="/profile"
            class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-sm font-bold text-gray-700 hover:bg-gray-400"
          >
            {{ authStore.user?.username?.charAt(0).toUpperCase() || "U" }}
          </router-link>
        </div>
        <div v-else class="flex items-center gap-3">
          <router-link
            to="/login"
            class="text-sm text-gray-700 hover:text-gray-900"
          >
            {{ $t("auth.login") }}
          </router-link>
          <router-link
            to="/register"
            class="px-4 py-2 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700"
          >
            {{ $t("auth.register") }}
          </router-link>
        </div>
      </div>
    </div>

    <!-- Search modal -->
    <Teleport to="body">
      <div
        v-if="showSearch"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-start justify-center pt-20"
        @click="showSearch = false"
      >
        <div class="bg-white rounded-lg p-6 w-full max-w-2xl" @click.stop>
          <div class="relative">
            <input
              v-model="searchQuery"
              type="search"
              :placeholder="$t('search.placeholder')"
              class="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              @keyup.enter="handleSearch"
              autofocus
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
          </div>
        </div>
      </div>
    </Teleport>
  </header>

  <!-- Spacer -->
  <div style="height: 70px"></div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import LanguageSwitcher from "@/components/common/LanguageSwitcher.vue";

const router = useRouter();
const authStore = useAuthStore();

const searchQuery = ref("");
const showSearch = ref(false);

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    showSearch.value = false;
    router.push({ name: "search", query: { q: searchQuery.value } });
    searchQuery.value = "";
  }
};

const handleLogout = async () => {
  await authStore.logout();
  router.push("/");
};
</script>
