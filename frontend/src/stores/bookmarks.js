import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { bookmarkService } from '@/services/interactions'

export const useBookmarkStore = defineStore('bookmarks', () => {
  const bookmarkedArticles = ref([])
  const bookmarkedBooks = ref([])
  const bookmarkedDissertations = ref([])
  const loading = ref(false)

  const allBookmarks = computed(() => [
    ...bookmarkedArticles.value,
    ...bookmarkedBooks.value,
    ...bookmarkedDissertations.value
  ])

  async function fetchBookmarks(contentType = null) {
    loading.value = true
    
    try {
      const data = await bookmarkService.getBookmarks(contentType)
      
      if (!contentType || contentType === 'article') {
        bookmarkedArticles.value = data.articles || []
      }
      if (!contentType || contentType === 'book') {
        bookmarkedBooks.value = data.books || []
      }
      if (!contentType || contentType === 'dissertation') {
        bookmarkedDissertations.value = data.dissertations || []
      }
      
      return data
    } catch (err) {
      console.error('Failed to fetch bookmarks:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function toggleBookmark(contentId, contentType) {
    try {
      const result = await bookmarkService.toggleBookmark(contentId, contentType)
      
      // Update local state
      const collection = getCollectionByType(contentType)
      const index = collection.findIndex(item => item.id === contentId)
      
      if (result.bookmarked && index === -1) {
        // Added to bookmarks - fetch fresh data
        await fetchBookmarks(contentType)
      } else if (!result.bookmarked && index !== -1) {
        // Removed from bookmarks
        collection.splice(index, 1)
      }
      
      return result
    } catch (err) {
      console.error('Failed to toggle bookmark:', err)
      throw err
    }
  }

  function isBookmarked(contentId, contentType) {
    const collection = getCollectionByType(contentType)
    return collection.some(item => item.id === contentId)
  }

  function getCollectionByType(contentType) {
    switch (contentType) {
      case 'article':
        return bookmarkedArticles.value
      case 'book':
        return bookmarkedBooks.value
      case 'dissertation':
        return bookmarkedDissertations.value
      default:
        return []
    }
  }

  return {
    bookmarkedArticles,
    bookmarkedBooks,
    bookmarkedDissertations,
    allBookmarks,
    loading,
    fetchBookmarks,
    toggleBookmark,
    isBookmarked
  }
})
