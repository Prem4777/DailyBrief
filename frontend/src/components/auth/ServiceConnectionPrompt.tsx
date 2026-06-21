/**
 * ServiceConnectionPrompt.tsx — Guides the user to connect required services.
 *
 * Shows which services (Gmail, GCal, Notion) are not yet connected and
 * provides buttons to start each connection flow.
 *
 * Props:
 *   - serviceStatus: current connection state for each service
 */

import { CheckCircle2, Link as LinkIcon } from 'lucide-react'
import React, { useState } from 'react'
import { saveNotionToken, startGoogleOAuth } from '../../api/authApi'
import type { ServiceStatus } from '../../types/auth'

interface ServiceConnectionPromptProps {
  serviceStatus: ServiceStatus
  onStatusRefresh: () => void
}

interface ServiceRowProps {
  name: string
  connected: boolean
  onConnect: () => void
}

function ServiceRow({ name, connected, onConnect }: ServiceRowProps) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-gray-100 bg-white px-4 py-3">
      <div className="flex items-center gap-2">
        {connected ? (
          <CheckCircle2 className="h-4 w-4 text-green-500" aria-hidden="true" />
        ) : (
          <div className="h-4 w-4 rounded-full border-2 border-gray-300" aria-hidden="true" />
        )}
        <span className="text-sm font-medium text-gray-700">{name}</span>
      </div>
      {!connected && (
        <button
          onClick={onConnect}
          className="
            inline-flex items-center gap-1 rounded-lg border border-blue-200
            bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700
            hover:bg-blue-100 transition-colors
          "
          aria-label={`Connect ${name}`}
        >
          <LinkIcon className="h-3 w-3" aria-hidden="true" />
          Connect
        </button>
      )}
    </div>
  )
}

export default function ServiceConnectionPrompt({
  serviceStatus,
  onStatusRefresh,
}: ServiceConnectionPromptProps) {
  const [notionToken, setNotionToken] = useState('')
  const [notionDbId, setNotionDbId] = useState('')
  const [showNotionForm, setShowNotionForm] = useState(false)
  const [notionSaving, setNotionSaving] = useState(false)
  const [notionError, setNotionError] = useState<string | null>(null)

  const handleNotionSave = async () => {
    if (!notionToken.trim() || !notionDbId.trim()) {
      setNotionError('Both fields are required.')
      return
    }
    setNotionSaving(true)
    setNotionError(null)
    try {
      await saveNotionToken(notionToken, notionDbId)
      setShowNotionForm(false)
      onStatusRefresh()
    } catch {
      setNotionError('Failed to save token. Please check and try again.')
    } finally {
      setNotionSaving(false)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16 px-4">
      <h1 className="text-xl font-bold text-gray-900 mb-2">Connect Your Services</h1>
      <p className="text-sm text-gray-500 mb-6">
        DailyBrief needs access to your email, calendar, and tasks to generate your briefing.
      </p>

      <div className="space-y-3">
        <ServiceRow
          name="Gmail"
          connected={serviceStatus.gmail}
          onConnect={startGoogleOAuth}
        />
        <ServiceRow
          name="Google Calendar"
          connected={serviceStatus.gcal}
          onConnect={startGoogleOAuth}
        />
        <ServiceRow
          name="Notion"
          connected={serviceStatus.notion}
          onConnect={() => setShowNotionForm(true)}
        />
      </div>

      {/* Notion token form — shown inline */}
      {showNotionForm && !serviceStatus.notion && (
        <div className="mt-4 rounded-xl border border-gray-200 p-4 space-y-3">
          <p className="text-sm font-semibold text-gray-700">Notion Integration Token</p>
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
          <div className="flex gap-2">
            <button
              onClick={handleNotionSave}
              disabled={notionSaving}
              className="flex-1 rounded-lg bg-blue-600 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60 transition-colors"
            >
              {notionSaving ? 'Saving…' : 'Save'}
            </button>
            <button
              onClick={() => setShowNotionForm(false)}
              className="flex-1 rounded-lg bg-gray-100 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
