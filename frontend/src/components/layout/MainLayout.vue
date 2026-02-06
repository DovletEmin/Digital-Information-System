<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />
    <main>
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import AppHeader from "@/components/layout/AppHeader.vue";
import AppFooter from "@/components/layout/AppFooter.vue";

const authStore = useAuthStore();

onMounted(() => {
  authStore.checkAuth();
});
</script>
