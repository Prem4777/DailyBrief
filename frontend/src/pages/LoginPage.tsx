import React from 'react'
import { Navigate, useSearchParams } from 'react-router-dom'
import LoginForm from '../components/auth/LoginForm'
import { useAuthStore } from '../store/authStore'

export default function LoginPage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const [searchParams] = useSearchParams()
  const oauthError = searchParams.get('error')

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">DailyBrief</h1>
          <p className="text-sm text-gray-500 mt-1">Your AI-powered morning brief</p>
        </div>

        {oauthError && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700" role="alert">
            Google sign-in failed. Please try again or use email and password.
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Sign In</h2>
          <LoginForm />
        </div>
      </div>
    </div>
  )
}
