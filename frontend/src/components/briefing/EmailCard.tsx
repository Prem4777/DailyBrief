/**
 * EmailCard.tsx — A single email item card.
 *
 * Props:
 *   - email: ClassifiedEmail data
 *   - onDraftReply: callback to trigger draft generation for this email
 */

import { PenLine } from 'lucide-react'
import React, { useState } from 'react'
import type { ClassifiedEmail } from '../../types/briefing'
import DraftReplyDrawer from './DraftReplyDrawer'
import { useBriefingStore } from '../../store/briefingStore'

interface EmailCardProps {
  email: ClassifiedEmail
  onDraftReply: (emailId: string) => void
}

function formatTime(isoString: string): string {
  return new Date(isoString).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  })
}

export default function EmailCard({ email, onDraftReply }: EmailCardProps) {
  const [draftOpen, setDraftOpen] = useState(false)
  const draft = useBriefingStore((s) => s.draftsByEmailId[email.id] ?? null)

  const handleDraftClick = () => {
    setDraftOpen((o) => !o)
    if (!draft) {
      onDraftReply(email.id)
    }
  }

  return (
    <div className="p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-gray-900 truncate">{email.sender}</p>
          <p className="text-sm text-gray-700 truncate">{email.subject}</p>
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{email.snippet}</p>
        </div>
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <span className="text-xs text-gray-400">{formatTime(email.received_at)}</span>
          {email.classification === 'urgent' && (
            <button
              onClick={handleDraftClick}
              className="
                inline-flex items-center gap-1 rounded-md bg-blue-50 px-2 py-1
                text-xs font-medium text-blue-700 hover:bg-blue-100 transition-colors
              "
              aria-label={`Draft reply to: ${email.subject}`}
            >
              <PenLine className="h-3 w-3" aria-hidden="true" />
              Draft Reply
            </button>
          )}
        </div>
      </div>

      {/* Expandable draft drawer */}
      {draftOpen && (
        <DraftReplyDrawer
          emailId={email.id}
          draft={draft}
        />
      )}
    </div>
  )
}
