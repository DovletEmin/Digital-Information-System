import apiClient from './api'

export const searchService = {
  // Full-text search across all content types
  async search(query, filters = {}) {
    const params = {
      q: query,
      ...filters
    }
    const response = await apiClient.get('/search/', { params })
    return response.data
  },

  // Search with pagination
  async searchPaginated(query, filters = {}, page = 1) {
    const params = {
      q: query,
      page,
      ...filters
    }
    const response = await apiClient.get('/search/', { params })
    return response.data
  },

  // Get search suggestions/autocomplete
  async getSuggestions(query) {
    if (!query || query.length < 2) return []
    
    try {
      const response = await apiClient.get('/search/suggestions/', {
        params: { q: query }
      })
      return response.data
    } catch (error) {
      console.error('Failed to get suggestions:', error)
      return []
    }
  }
}
