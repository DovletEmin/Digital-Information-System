import apiClient from './api'

export const authService = {
  // Register new user
  async register(userData) {
    const response = await apiClient.post('/auth/register/', {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      password_confirm: userData.passwordConfirm
    })
    return response.data
  },

  // Login
  async login(credentials) {
    const response = await apiClient.post('/auth/login/', {
      username: credentials.username,
      password: credentials.password
    })
    
    const { access, refresh } = response.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    
    return response.data
  },

  // Logout
  async logout() {
    try {
      await apiClient.post('/auth/logout/')
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  },

  // Get current user profile
  async getProfile() {
    const response = await apiClient.get('/auth/profile/')
    return response.data
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  }
}
