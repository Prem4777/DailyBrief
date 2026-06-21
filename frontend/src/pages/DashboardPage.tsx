/**
 * DashboardPage.tsx — The main application view.
 *
 * On load, checks whether all required services are connected.
 * If any service is missing → shows ServiceConnectionPrompt.
 * Once all services are connected → shows TwoColumnLayout (BriefingPanel + ChatPanel).
 */

import React, { useEffect, useState } from 'react'
import ServiceConnectionPrompt from '../components/auth/ServiceConnectionPrompt'
import BriefingPanel from '../components/layout/BriefingPanel'
import ChatPanel from '../components/layout/ChatPanel'
import TwoColumnLayout from '../components/layout/TwoColumnLayout'
import { useAuthStore } from '../store/authStore'

export default function DashboardPage() {
  const serviceStatus = useAuthStore((s) => s.serviceStatus)
  const fetchServiceStatus = useAuthStore((s) => s.fetchServiceStatus)
  const [statusLoading, setStatusLoading] = useState(true)

  useEffect(() => {
    fetchServiceStatus().finally(() => setStatusLoading(false))
  }, [fetchServiceStatus])

  const allConnected =
    serviceStatus !== null &&
    serviceStatus.gmail &&
    serviceStatus.gcal &&
    serviceStatus.notion

  // Loading service status
  if (statusLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
          <p className="text-sm text-gray-500">Loading…</p>
        </div>
      </div>
    )
  }

  // One or more services not connected (or status fetch failed)
  if (!allConnected) {
    return (
      <ServiceConnectionPrompt
        serviceStatus={serviceStatus ?? { gmail: false, gcal: false, notion: false }}
        onStatusRefresh={fetchServiceStatus}
      />
    )
  }

  // All services connected — show the main briefing UI
  return (
    <TwoColumnLayout
      left={<BriefingPanel />}
      right={<ChatPanel />}
    />
  )
}
