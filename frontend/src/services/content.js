import apiClient from './api'

export const articleService = {
  // Get all articles with filters
  async getArticles(params = {}) {
    const response = await apiClient.get('/articles/', { params })
    return response.data
  },

  // Get single article by ID
  async getArticle(id) {
    const response = await apiClient.get(`/articles/${id}/`)
    return response.data
  },

  // Get article categories
  async getCategories() {
    console.log('articleService.getCategories called');
    const response = await apiClient.get('/article-categories/')
    console.log('Full axios response:', response);
    console.log('Response data:', response.data);
    return response.data
  },

  // Register article view
  async registerView(id) {
    try {
      await apiClient.post(`/views/article/${id}/`)
    } catch (error) {
      console.error('Failed to register view:', error)
    }
  }
}

export const bookService = {
  // Get all books with filters
  async getBooks(params = {}) {
    const response = await apiClient.get('/books/', { params })
    return response.data
  },

  // Get single book by ID
  async getBook(id) {
    const response = await apiClient.get(`/books/${id}/`)
    return response.data
  },

  // Get book categories
  async getCategories() {
    const response = await apiClient.get('/book-categories/')
    return response.data
  },

  // Register book view
  async registerView(id) {
    try {
      await apiClient.post(`/views/book/${id}/`)
    } catch (error) {
      console.error('Failed to register view:', error)
    }
  }
}

export const dissertationService = {
  // Get all dissertations with filters
  async getDissertations(params = {}) {
    const response = await apiClient.get('/dissertations/', { params })
    return response.data
  },

  // Get single dissertation by ID
  async getDissertation(id) {
    const response = await apiClient.get(`/dissertations/${id}/`)
    return response.data
  },

  // Get dissertation categories
  async getCategories() {
    const response = await apiClient.get('/dissertation-categories/')
    return response.data
  },

  // Register dissertation view
  async registerView(id) {
    try {
      await apiClient.post(`/views/dissertation/${id}/`)
    } catch (error) {
      console.error('Failed to register view:', error)
    }
  }
}
