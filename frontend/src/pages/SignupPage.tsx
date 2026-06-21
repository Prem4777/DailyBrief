/**
 * SignupPage.tsx — Centered card page housing the SignupForm.
 *
 * Redirects to "/" if the user is already authenticated.
 */

import React from 'react'
import { Navigate } from 'react-router-dom'
import SignupForm from '../components/auth/SignupForm'
import { useAuthStore } from '../store/authStore'

export default function SignupPage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

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

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Create Account</h2>
          <SignupForm />
        </div>
      </div>
    </div>
  )
}
