/**
 * SettingsPage.tsx — Service connection management and account settings.
 *
 * Shows connection status for Gmail, GCal, and Notion.
 * Provides connect/disconnect buttons for each service.
 * Inline Notion token form.
 */

import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Unlink } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { startGoogleOAuth, saveNotionToken } from '../api/authApi'
import apiClient from '../api/client'

export default function SettingsPage() {
  const serviceStatus = useAuthStore((s) => s.serviceStatus)
  const fetchServiceStatus = useAuthStore((s) => s.fetchServiceStatus)

  const [notionToken, setNotionToken] = useState('')
  const [notionDbId, setNotionDbId] = useState('')
  const [notionSaving, setNotionSaving] = useState(false)
  const [notionError, setNotionError] = useState<string | null>(null)
  const [notionSuccess, setNotionSuccess] = useState(false)

  useEffect(() => {
    fetchServiceStatus()
  }, [fetchServiceStatus])

  const handleDisconnect = async (service: string) => {
    try {
      await apiClient.delete(`/api/settings/services/${service}`)
      await fetchServiceStatus()
    } catch {
      // TODO: show error toast
    }
  }

  const handleNotionSave = async () => {
    setNotionError(null)
    if (!notionToken.trim() || !notionDbId.trim()) {
      setNotionError('Both fields are required.')
      return
    }
    setNotionSaving(true)
    try {
      await saveNotionToken(notionToken, notionDbId)
      setNotionToken('')
      setNotionDbId('')
      setNotionSuccess(true)
      await fetchServiceStatus()
      setTimeout(() => setNotionSuccess(false), 3000)
    } catch {
      setNotionError('Failed to save Notion token.')
    } finally {
      setNotionSaving(false)
    }
  }

  const services = [
    { key: 'gmail', label: 'Gmail', connected: serviceStatus?.gmail ?? false },
    { key: 'gcal', label: 'Google Calendar', connected: serviceStatus?.gcal ?? false },
    { key: 'notion', label: 'Notion', connected: serviceStatus?.notion ?? false },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-xl mx-auto flex items-center gap-4">
          <Link to="/" className="text-gray-500 hover:text-gray-700" aria-label="Back to dashboard">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-lg font-bold text-gray-900">Settings</h1>
        </div>
      </header>

      <main className="max-w-xl mx-auto px-6 py-6 space-y-6">
        {/* Service connections */}
        <section aria-label="Service Connections">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
            Connected Services
          </h2>
          <div className="space-y-2">
            {services.map(({ key, label, connected }) => (
              <div
                key={key}
                className="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3"
              >
                <div className="flex items-center gap-2">
                  {connected ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" aria-hidden="true" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border-2 border-gray-300" aria-hidden="true" />
                  )}
                  <span className="text-sm font-medium text-gray-700">{label}</span>
                  {connected && (
                    <span className="text-xs text-green-600 bg-green-50 rounded-full px-2 py-0.5">
                      Connected
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  {!connected && key !== 'notion' && (
                    <button
                      onClick={startGoogleOAuth}
                      className="text-xs font-medium text-blue-600 hover:underline"
                      aria-label={`Connect ${label}`}
                    >
                      Connect
                    </button>
                  )}
                  {connected && (
                    <button
                      onClick={() => handleDisconnect(key)}
                      className="text-gray-400 hover:text-red-500 transition-colors"
                      aria-label={`Disconnect ${label}`}
                    >
                      <Unlink className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Notion token form */}
        {!serviceStatus?.notion && (
          <section aria-label="Notion Integration">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              Notion Token
            </h2>
            <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3">
              <p className="text-xs text-gray-500">
                Create an internal integration at{' '}
                <a
                  href="https://www.notion.so/my-integrations"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  notion.so/my-integrations
                </a>{' '}
                and paste the token and database ID below.
              </p>
              <input
                type="text"
                placeholder="secret_xxxxx"
                value={notionToken}
                onChange={(e) => setNotionToken(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Notion integration token"
              />
              <input
                type="text"
                placeholder="Database ID"
                value={notionDbId}
                onChange={(e) => setNotionDbId(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Notion database ID"
              />
              {notionError && <p className="text-sm text-red-600">{notionError}</p>}
              {notionSuccess && <p className="text-sm text-green-600">Notion connected!</p>}
              <button
                onClick={handleNotionSave}
                disabled={notionSaving}
                className="w-full rounded-lg bg-blue-600 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60 transition-colors"
              >
                {notionSaving ? 'Saving…' : 'Save Token'}
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}
