<template>
  <aside class="w-64 flex-shrink-0">
    <div class="bg-white rounded-lg shadow-sm p-4 sticky top-20">
      <h3 class="font-semibold text-gray-900 mb-4">{{ title }}</h3>

      <nav class="space-y-1">
        <button
          v-for="category in categories"
          :key="category.id"
          @click="$emit('select', category.id)"
          :class="[
            'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors',
            selectedId === category.id
              ? 'bg-primary-50 text-primary-700 font-medium'
              : 'text-gray-700 hover:bg-gray-50',
          ]"
        >
          {{ category.name }}
        </button>
      </nav>

      <button
        v-if="selectedId"
        @click="$emit('select', null)"
        class="w-full mt-4 px-3 py-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
      >
        {{ $t("common.clearFilter") }}
      </button>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  categories: {
    type: Array,
    default: () => [],
  },
  selectedId: {
    type: Number,
    default: null,
  },
});

defineEmits(["select"]);
</script>
