/**
 * EventCard.tsx — A single calendar event card.
 *
 * Shows time range, title, attendee count.
 * Displays a red "Conflict" or amber "Back-to-back" badge when flagged.
 *
 * Props:
 *   - event: CalendarEvent data
 */

import React from 'react'
import type { CalendarEvent } from '../../types/briefing'

interface EventCardProps {
  event: CalendarEvent
}

function formatTimeRange(start: string, end: string): string {
  const fmt = (iso: string) =>
    new Date(iso).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
  return `${fmt(start)} – ${fmt(end)}`
}

export default function EventCard({ event }: EventCardProps) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-gray-100 bg-white p-4">
      {/* Time column */}
      <div className="w-20 flex-shrink-0 text-right">
        <p className="text-xs font-medium text-gray-500 leading-tight">
          {formatTimeRange(event.start, event.end)}
        </p>
      </div>

      {/* Content column */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="text-sm font-semibold text-gray-900">{event.title}</p>

          {/* Conflict badge */}
          {event.conflict_flag && (
            <span
              className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700"
              role="status"
              aria-label="Calendar conflict"
            >
              Conflict
            </span>
          )}

          {/* Back-to-back badge */}
          {!event.conflict_flag && event.back_to_back_flag && (
            <span
              className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700"
              role="status"
              aria-label="Back-to-back meeting"
            >
              Back-to-back
            </span>
          )}
        </div>

        {/* Attendees */}
        {event.attendees.length > 0 && (
          <p className="text-xs text-gray-500 mt-1">
            {event.attendees.length} attendee{event.attendees.length !== 1 ? 's' : ''}
          </p>
        )}

        {/* Location */}
        {event.location && (
          <p className="text-xs text-gray-400 mt-0.5">{event.location}</p>
        )}
      </div>
    </div>
  )
}
