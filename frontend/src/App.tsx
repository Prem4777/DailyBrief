import React from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import DashboardPage from './pages/DashboardPage'
import HistoryPage from './pages/HistoryPage'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import OAuthCallbackPage from './pages/OAuthCallbackPage'
import SettingsPage from './pages/SettingsPage'
import SignupPage from './pages/SignupPage'
import { useAuthStore } from './store/authStore'

interface ProtectedRouteProps {
  children: React.ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      {/* Handles ?token= from Google OAuth redirect, then shows dashboard */}
      <Route path="/oauth/callback" element={<OAuthCallbackPage />} />

      {/* Protected */}
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/history"   element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
      <Route path="/settings"  element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
