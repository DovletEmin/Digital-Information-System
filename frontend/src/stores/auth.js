import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!user.value)

  async function login(credentials) {
    loading.value = true
    error.value = null
    
    try {
      await authService.login(credentials)
      await fetchProfile()
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = null
    
    try {
      await authService.register(userData)
      await login({
        username: userData.username,
        password: userData.password
      })
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    
    try {
      await authService.logout()
    } finally {
      user.value = null
      loading.value = false
    }
  }

  async function fetchProfile() {
    loading.value = true
    
    try {
      user.value = await authService.getProfile()
    } catch (err) {
      user.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  async function checkAuth() {
    if (authService.isAuthenticated()) {
      try {
        await fetchProfile()
      } catch (err) {
        // Token invalid, clear storage
        await logout()
      }
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    fetchProfile,
    checkAuth
  }
})
