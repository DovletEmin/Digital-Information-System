import { defineStore } from 'pinia'
import { ref } from 'vue'
import { articleService, bookService, dissertationService } from '@/services/content'

export const useContentStore = defineStore('content', () => {
  const articles = ref([])
  const books = ref([])
  const dissertations = ref([])
  
  const articleCategories = ref([])
  const bookCategories = ref([])
  const dissertationCategories = ref([])
  
  const loading = ref(false)
  const error = ref(null)
  
  const pagination = ref({
    articles: { page: 1, total: 0, hasNext: false },
    books: { page: 1, total: 0, hasNext: false },
    dissertations: { page: 1, total: 0, hasNext: false }
  })

  // Articles
  async function fetchArticles(params = {}) {
    loading.value = true
    error.value = null
    
    try {
      const data = await articleService.getArticles(params)
      articles.value = data.results
      pagination.value.articles = {
        page: params.page || 1,
        total: data.count,
        hasNext: !!data.next
      }
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchArticleCategories() {
    try {
      console.log('Fetching categories from API...');
      const response = await articleService.getCategories();
      console.log('Raw API response:', response);
      articleCategories.value = response;
      console.log('Categories set to:', articleCategories.value);
    } catch (err) {
      console.error('Failed to fetch article categories:', err);
      console.error('Error details:', err.response);
    }
  }

  // Books
  async function fetchBooks(params = {}) {
    loading.value = true
    error.value = null
    
    try {
      const data = await bookService.getBooks(params)
      books.value = data.results
      pagination.value.books = {
        page: params.page || 1,
        total: data.count,
        hasNext: !!data.next
      }
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchBookCategories() {
    try {
      bookCategories.value = await bookService.getCategories()
    } catch (err) {
      console.error('Failed to fetch book categories:', err)
    }
  }

  // Dissertations
  async function fetchDissertations(params = {}) {
    loading.value = true
    error.value = null
    
    try {
      const data = await dissertationService.getDissertations(params)
      dissertations.value = data.results
      pagination.value.dissertations = {
        page: params.page || 1,
        total: data.count,
        hasNext: !!data.next
      }
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchDissertationCategories() {
    try {
      dissertationCategories.value = await dissertationService.getCategories()
    } catch (err) {
      console.error('Failed to fetch dissertation categories:', err)
    }
  }

  return {
    articles,
    books,
    dissertations,
    articleCategories,
    bookCategories,
    dissertationCategories,
    loading,
    error,
    pagination,
    fetchArticles,
    fetchArticleCategories,
    fetchBooks,
    fetchBookCategories,
    fetchDissertations,
    fetchDissertationCategories
  }
})
