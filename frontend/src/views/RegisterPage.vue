<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-gray-900">
          {{ $t("auth.register") }}
        </h2>
        <p class="text-gray-600 mt-2">SMU {{ $t("footer.aboutText") }}</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <!-- Error message -->
        <div
          v-if="error"
          class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm"
        >
          {{ error }}
        </div>

        <!-- Username -->
        <div>
          <label
            for="username"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            {{ $t("auth.username") }}
          </label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <!-- Email -->
        <div>
          <label
            for="email"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            {{ $t("auth.email") }}
          </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <!-- Password -->
        <div>
          <label
            for="password"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            {{ $t("auth.password") }}
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            minlength="6"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <!-- Password Confirmation -->
        <div>
          <label
            for="passwordConfirm"
            class="block text-sm font-medium text-gray-700 mb-2"
          >
            {{ $t("auth.passwordConfirm") }}
          </label>
          <input
            id="passwordConfirm"
            v-model="form.passwordConfirm"
            type="password"
            required
            minlength="6"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <!-- Submit button -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ loading ? $t("common.loading") : $t("auth.registerButton") }}
        </button>
      </form>

      <!-- Login link -->
      <p class="text-center text-sm text-gray-600 mt-6">
        {{ $t("auth.haveAccount") }}
        <router-link
          to="/login"
          class="text-primary-600 hover:text-primary-700 font-medium"
        >
          {{ $t("auth.login") }}
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const form = ref({
  username: "",
  email: "",
  password: "",
  passwordConfirm: "",
});

const loading = ref(false);
const error = ref(null);

const handleRegister = async () => {
  if (form.value.password !== form.value.passwordConfirm) {
    error.value = "Passwords do not match";
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    await authStore.register(form.value);
    router.push("/");
  } catch (err) {
    error.value =
      err.response?.data?.message || "Registration failed. Please try again.";
  } finally {
    loading.value = false;
  }
};
</script>
