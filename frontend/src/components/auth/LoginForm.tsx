/**
 * LoginForm.tsx — Email + password login form.
 *
 * Calls authStore.login() on submit.
 * Displays server-side or network errors below the form.
 * Includes a link to the signup page.
 */

import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import GoogleSignInButton from './GoogleSignInButton'

export default function LoginForm() {
  const login = useAuthStore((s) => s.login)
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      await login(email, password)
      navigate('/dashboard', { replace: true })
    } catch {
      // TODO: parse server error response for more specific messages
      setError('Invalid email or password. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email address
        </label>
        <input
          id="email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="
            w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
            focus:outline-none focus:ring-2 focus:ring-blue-500
          "
          aria-required="true"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="
            w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
            focus:outline-none focus:ring-2 focus:ring-blue-500
          "
          aria-required="true"
        />
      </div>

      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="
          w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white
          hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed
          transition-colors
        "
      >
        {isSubmitting ? 'Signing in…' : 'Sign In'}
      </button>

      <p className="text-center text-sm text-gray-500">
        Don't have an account?{' '}
        <Link to="/signup" className="font-medium text-blue-600 hover:underline">
          Sign up
        </Link>
      </p>

      <div className="relative my-1">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-white px-2 text-gray-400">or</span>
        </div>
      </div>

      <GoogleSignInButton />
    </form>
  )
}
