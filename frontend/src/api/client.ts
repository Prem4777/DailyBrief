/**
 * client.ts — Configured Axios instance for all API calls.
 *
 * - Adds Authorization: Bearer <token> header from localStorage on every request.
 * - On 401 responses, clears the stored token and redirects to /login.
 */

import axios from 'axios'

const TOKEN_KEY = 'dailybrief_token'

const apiClient = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
})

// ---------------------------------------------------------------------------
// Request interceptor — attach JWT
// ---------------------------------------------------------------------------

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ---------------------------------------------------------------------------
// Response interceptor — handle 401 Unauthorized
// ---------------------------------------------------------------------------

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // TODO: trigger Zustand authStore.logout() instead of direct localStorage
      // manipulation once the circular dependency issue is resolved.
      localStorage.removeItem(TOKEN_KEY)
      // Redirect to login — use window.location to avoid React Router import
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export { TOKEN_KEY }
export default apiClient
