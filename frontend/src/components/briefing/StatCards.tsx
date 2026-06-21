/**
 * StatCards.tsx — Three summary stat cards for urgent emails, meetings, and overdue tasks.
 *
 * Props:
 *   - urgentEmailCount: number of urgent emails
 *   - meetingCount: number of calendar events today
 *   - overdueTaskCount: number of overdue Notion tasks
 */

import { AlertCircle, CalendarDays, ClipboardList } from 'lucide-react'
import React from 'react'

interface StatCardsProps {
  urgentEmailCount: number
  meetingCount: number
  overdueTaskCount: number
}

interface StatCardProps {
  label: string
  value: number
  icon: React.ReactNode
  colorClass: string
}

function StatCard({ label, value, icon, colorClass }: StatCardProps) {
  return (
    <div
      className="flex items-center gap-3 rounded-xl border bg-white p-4 shadow-sm"
      role="status"
      aria-label={`${label}: ${value}`}
    >
      <div className={`rounded-lg p-2 ${colorClass}`}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-xs text-gray-500">{label}</p>
      </div>
    </div>
  )
}

export default function StatCards({
  urgentEmailCount,
  meetingCount,
  overdueTaskCount,
}: StatCardsProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <StatCard
        label="Urgent Emails"
        value={urgentEmailCount}
        icon={<AlertCircle className="h-5 w-5 text-red-600" aria-hidden="true" />}
        colorClass="bg-red-50"
      />
      <StatCard
        label="Meetings Today"
        value={meetingCount}
        icon={<CalendarDays className="h-5 w-5 text-blue-600" aria-hidden="true" />}
        colorClass="bg-blue-50"
      />
      <StatCard
        label="Overdue Tasks"
        value={overdueTaskCount}
        icon={<ClipboardList className="h-5 w-5 text-amber-600" aria-hidden="true" />}
        colorClass="bg-amber-50"
      />
    </div>
  )
}
