import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomePage.vue'),
      meta: { title: 'Baş sahypa' }
    },
    {
      path: '/articles',
      name: 'articles',
      component: () => import('@/views/ArticleListPage.vue'),
      meta: { title: 'Makalalar' }
    },
    {
      path: '/articles/:id',
      name: 'article-detail',
      component: () => import('@/views/ArticleDetailPage.vue'),
      meta: { title: 'Makala' }
    },
    {
      path: '/books',
      name: 'books',
      component: () => import('@/views/BookListPage.vue'),
      meta: { title: 'Kitaplar' }
    },
    {
      path: '/books/:id',
      name: 'book-detail',
      component: () => import('@/views/BookDetailPage.vue'),
      meta: { title: 'Kitap' }
    },
    {
      path: '/dissertations',
      name: 'dissertations',
      component: () => import('@/views/DissertationListPage.vue'),
      meta: { title: 'Dissertasiýalar' }
    },
    {
      path: '/dissertations/:id',
      name: 'dissertation-detail',
      component: () => import('@/views/DissertationDetailPage.vue'),
      meta: { title: 'Dissertasiýa' }
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchPage.vue'),
      meta: { title: 'Gözleg' }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginPage.vue'),
      meta: { title: 'Giriş', guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterPage.vue'),
      meta: { title: 'Hasaba durmak', guest: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfilePage.vue'),
      meta: { title: 'Profil', requiresAuth: true }
    },
    {
      path: '/bookmarks',
      name: 'bookmarks',
      component: () => import('@/views/BookmarksPage.vue'),
      meta: { title: 'Saýlanlar', requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundPage.vue'),
      meta: { title: '404' }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Check authentication status
  if (!authStore.user && authStore.isAuthenticated) {
    await authStore.checkAuth()
  }

  // Redirect if requires auth
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Redirect if guest only
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  // Update page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - SMU`
  }

  next()
})

export default router
