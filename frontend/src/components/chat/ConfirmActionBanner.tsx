/**
 * ConfirmActionBanner.tsx — Yellow banner asking the user to confirm a calendar proposal.
 *
 * Shown in the chat panel when the assistant proposes scheduling a task.
 *
 * Props:
 *   - proposal:  the CalendarProposal to confirm or reject
 *   - onConfirm: callback when the user confirms
 *   - onReject:  callback when the user rejects
 */

import { CalendarPlus, X } from 'lucide-react'
import React from 'react'
import type { CalendarProposal } from '../../types/briefing'

interface ConfirmActionBannerProps {
  proposal: CalendarProposal
  onConfirm: () => void
  onReject: () => void
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export default function ConfirmActionBanner({
  proposal,
  onConfirm,
  onReject,
}: ConfirmActionBannerProps) {
  return (
    <div
      className="border-b border-amber-200 bg-amber-50 px-4 py-3"
      role="alert"
      aria-label="Pending calendar action"
    >
      <div className="flex items-start gap-2">
        <CalendarPlus
          className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600"
          aria-hidden="true"
        />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-amber-800">Schedule Task</p>
          <p className="text-xs text-amber-700 mt-0.5">
            <strong>{proposal.task_title}</strong>
            <br />
            {formatDateTime(proposal.proposed_start)} → {formatDateTime(proposal.proposed_end)}
          </p>
          <p className="text-xs text-amber-600 mt-1">{proposal.rationale}</p>
        </div>
      </div>

      <div className="flex gap-2 mt-2">
        <button
          onClick={onConfirm}
          className="
            flex-1 rounded-lg bg-green-600 py-1.5 text-xs font-semibold text-white
            hover:bg-green-700 transition-colors
          "
          aria-label="Confirm calendar action"
        >
          Confirm
        </button>
        <button
          onClick={onReject}
          className="
            flex-1 rounded-lg bg-red-100 py-1.5 text-xs font-semibold text-red-700
            hover:bg-red-200 transition-colors
          "
          aria-label="Cancel calendar action"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}
