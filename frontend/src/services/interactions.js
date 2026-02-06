import apiClient from './api'

export const bookmarkService = {
  // Toggle bookmark for content
  async toggleBookmark(contentId, contentType) {
    const response = await apiClient.post(`/bookmarks/toggle/${contentId}/`, {
      content_type: contentType
    })
    return response.data
  },

  // Get user bookmarks
  async getBookmarks(contentType = null) {
    const params = contentType ? { content_type: contentType } : {}
    const response = await apiClient.get('/bookmarks/', { params })
    return response.data
  }
}

export const ratingService = {
  // Rate content
  async rateContent(contentId, contentType, rating) {
    const response = await apiClient.post('/rate/', {
      content_id: contentId,
      content_type: contentType,
      rating: rating
    })
    return response.data
  },

  // Get user's rating for content
  async getUserRating(contentId, contentType) {
    try {
      const response = await apiClient.get('/rate/', {
        params: {
          content_id: contentId,
          content_type: contentType
        }
      })
      return response.data.rating
    } catch (error) {
      return null
    }
  }
}
