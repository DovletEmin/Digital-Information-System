<template>
  <div class="relative group">
    <button
      @click="isOpen = !isOpen"
      class="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
    >
      <svg
        class="w-5 h-5 text-gray-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
        />
      </svg>
      <span class="text-sm font-medium text-gray-700">{{
        currentLangLabel
      }}</span>
      <svg
        class="w-4 h-4 text-gray-600 transition-transform"
        :class="{ 'rotate-180': isOpen }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7"
        />
      </svg>
    </button>

    <div
      v-show="isOpen"
      class="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-lg py-1 z-50"
    >
      <button
        v-for="lang in languages"
        :key="lang.code"
        @click="changeLanguage(lang.code)"
        :class="[
          'w-full text-left px-4 py-2 text-sm hover:bg-gray-100 transition-colors',
          currentLocale === lang.code
            ? 'text-primary-600 font-medium'
            : 'text-gray-700',
        ]"
      >
        {{ lang.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";

const { locale } = useI18n();
const isOpen = ref(false);

const languages = [
  { code: "tm", label: "Türkmençe" },
  { code: "ru", label: "Русский" },
  { code: "en", label: "English" },
];

const currentLocale = computed(() => locale.value);
const currentLangLabel = computed(() => {
  const lang = languages.find((l) => l.code === locale.value);
  return lang ? lang.label : "Language";
});

const changeLanguage = (lang) => {
  locale.value = lang;
  localStorage.setItem("locale", lang);
  isOpen.value = false;
};

const handleClickOutside = (event) => {
  const target = event.target;
  if (!target.closest(".relative.group")) {
    isOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>
