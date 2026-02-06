import { defineStore } from 'pinia'
import { ref } from 'vue'
import { searchService } from '@/services/search'

export const useSearchStore = defineStore('search', () => {
  const results = ref([])
  const query = ref('')
  const filters = ref({
    content_type: null, // 'article', 'book', 'dissertation'
    language: null,     // 'tm', 'ru', 'en'
    categories: []
  })
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    total: 0,
    hasNext: false
  })

  async function search(searchQuery, searchFilters = {}, page = 1) {
    loading.value = true
    query.value = searchQuery
    filters.value = { ...filters.value, ...searchFilters }

    try {
      const data = await searchService.searchPaginated(searchQuery, searchFilters, page)
      results.value = data.results
      pagination.value = {
        page,
        total: data.count,
        hasNext: !!data.next
      }
      return data
    } catch (err) {
      console.error('Search failed:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearSearch() {
    results.value = []
    query.value = ''
    filters.value = {
      content_type: null,
      language: null,
      categories: []
    }
    pagination.value = {
      page: 1,
      total: 0,
      hasNext: false
    }
  }

  return {
    results,
    query,
    filters,
    loading,
    pagination,
    search,
    clearSearch
  }
})
