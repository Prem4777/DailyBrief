/**
 * CalendarSection.tsx — List of today's calendar events.
 *
 * Shows a degraded warning banner when GCal was unavailable during generation.
 *
 * Props:
 *   - events: CalendarEvent list from the briefing
 *   - unavailable: true if GCal was unavailable
 */

import { AlertTriangle } from 'lucide-react'
import React from 'react'
import type { CalendarEvent } from '../../types/briefing'
import EventCard from './EventCard'

interface CalendarSectionProps {
  events: CalendarEvent[]
  unavailable: boolean
}

export default function CalendarSection({ events, unavailable }: CalendarSectionProps) {
  return (
    <section aria-label="Calendar">
      <h2 className="text-base font-semibold text-gray-800 mb-3">Calendar</h2>

      {unavailable && (
        <div
          className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700 mb-3"
          role="alert"
        >
          <AlertTriangle className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
          Google Calendar was unavailable — events may be incomplete.
        </div>
      )}

      {events.length === 0 && !unavailable && (
        <p className="text-sm text-gray-500">No events scheduled for today.</p>
      )}

      <div className="space-y-2">
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </section>
  )
}
