/**
 * authStore.ts — Zustand store for authentication state.
 *
 * Persists the JWT token to localStorage so the user stays logged in across
 * page refreshes. The token is picked up by the Axios interceptor in client.ts.
 */

import { create } from 'zustand'
import * as authApi from '../api/authApi'
import { TOKEN_KEY } from '../api/client'
import type { ServiceStatus, User } from '../types/auth'

interface AuthState {
  /** The authenticated user (null if not logged in). */
  user: User | null
  /** The JWT access token (null if not logged in). */
  token: string | null
  /** True if a valid token is stored. */
  isAuthenticated: boolean
  /** Service connection status for Gmail, GCal, Notion. */
  serviceStatus: ServiceStatus | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchServiceStatus: () => Promise<void>
  /** Called by OAuthCallbackPage after a Google sign-in redirect. */
  setTokenFromOAuth: (token: string) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  // ---------------------------------------------------------------------------
  // Initial state — hydrate token from localStorage on first load
  // ---------------------------------------------------------------------------
  token: localStorage.getItem(TOKEN_KEY),
  user: null,
  isAuthenticated: Boolean(localStorage.getItem(TOKEN_KEY)),
  serviceStatus: null,

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------

  login: async (email, password) => {
    // TODO: decode the JWT to extract user info (id, email) without a /me endpoint
    const response = await authApi.login(email, password)
    localStorage.setItem(TOKEN_KEY, response.access_token)
    set({
      token: response.access_token,
      isAuthenticated: true,
      // TODO: set user from decoded JWT payload
    })
  },

  signup: async (email, password) => {
    const response = await authApi.signup(email, password)
    localStorage.setItem(TOKEN_KEY, response.access_token)
    set({
      token: response.access_token,
      isAuthenticated: true,
    })
  },

  logout: () => {
    authApi.logout().catch(() => {
      // Ignore errors — logout is best-effort on the server
    })
    localStorage.removeItem(TOKEN_KEY)
    set({ token: null, user: null, isAuthenticated: false, serviceStatus: null })
  },

  fetchServiceStatus: async () => {
    // TODO: handle errors gracefully (e.g. when backend is unavailable)
    const status = await authApi.getServiceStatus()
    set({ serviceStatus: status })
  },

  setTokenFromOAuth: (token: string) => {
    set({ token, isAuthenticated: true })
  },
}))
