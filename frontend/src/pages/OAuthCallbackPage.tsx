/**
 * OAuthCallbackPage.tsx — Handles the redirect from Google OAuth.
 *
 * The backend redirects here after a successful OAuth flow with:
 *   /oauth/callback?token=<jwt>
 *
 * This page stores the token and redirects to /dashboard.
 */

import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { TOKEN_KEY } from '../api/client'

export default function OAuthCallbackPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const token = params.get('token')
    const error = params.get('error')

    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
      // Reload auth store state by navigating — the store hydrates from localStorage
      navigate('/dashboard', { replace: true })
      window.location.reload()
    } else {
      // OAuth failed or was denied
      navigate('/login?error=oauth_failed', { replace: true })
    }
  }, [navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
        <p className="text-sm text-gray-500">Completing sign in…</p>
      </div>
    </div>
  )
}
