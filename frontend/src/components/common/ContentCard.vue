<template>
  <div
    class="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow group"
  >
    <router-link
      :to="{ name: detailRoute, params: { id: item.id } }"
      class="block"
    >
      <!-- Image -->
      <div v-if="item.image" class="relative h-48 overflow-hidden bg-gray-100">
        <img
          :src="item.image"
          :alt="item.title"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <div
        v-else
        class="h-48 bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center"
      >
        <svg
          class="w-16 h-16 text-white opacity-50"
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

      <!-- Content -->
      <div class="p-4">
        <!-- Title -->
        <h3
          class="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors"
        >
          {{ item.title }}
        </h3>

        <!-- Author -->
        <p class="text-sm text-gray-600 mb-3">
          {{ item.author }}
        </p>

        <!-- Meta info -->
        <div class="flex items-center justify-between text-xs text-gray-500">
          <div class="flex items-center space-x-3">
            <!-- Rating -->
            <div v-if="item.average_rating" class="flex items-center space-x-1">
              <svg
                class="w-4 h-4 text-yellow-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                />
              </svg>
              <span>{{ item.average_rating.toFixed(1) }}</span>
            </div>

            <!-- Views -->
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
              <span>{{ formatViews(item.views) }}</span>
            </div>

            <!-- Language badge -->
            <span
              :class="[
                'px-2 py-0.5 rounded text-xs font-medium',
                languageColor(item.language),
              ]"
            >
              {{ languageLabel(item.language) }}
            </span>
          </div>

          <!-- Bookmark button -->
          <button
            v-if="showBookmark"
            @click.prevent="handleBookmark"
            class="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <svg
              class="w-5 h-5"
              :class="
                isBookmarked ? 'text-primary-600 fill-current' : 'text-gray-400'
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
    </router-link>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  detailRoute: {
    type: String,
    required: true,
  },
  showBookmark: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(["bookmark"]);

const isBookmarked = computed(() => props.item.is_bookmarked || false);

const formatViews = (views) => {
  if (views >= 1000) {
    return `${(views / 1000).toFixed(1)}k`;
  }
  return views || 0;
};

const languageLabel = (lang) => {
  const labels = {
    tm: "TM",
    ru: "RU",
    en: "EN",
  };
  return labels[lang] || lang;
};

const languageColor = (lang) => {
  const colors = {
    tm: "bg-green-100 text-green-700",
    ru: "bg-blue-100 text-blue-700",
    en: "bg-purple-100 text-purple-700",
  };
  return colors[lang] || "bg-gray-100 text-gray-700";
};

const handleBookmark = () => {
  emit("bookmark", props.item.id);
};
</script>
