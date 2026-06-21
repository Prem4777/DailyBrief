/**
 * EmailSection.tsx — Three collapsible groups of emails: Urgent, Can Wait, FYI.
 *
 * Props:
 *   - emails: full list of ClassifiedEmail objects from the briefing
 */

import React, { useState } from 'react'
import type { ClassifiedEmail } from '../../types/briefing'
import EmailCard from './EmailCard'

interface EmailSectionProps {
  emails: ClassifiedEmail[]
  onDraftReply: (emailId: string) => void
}

interface EmailGroupProps {
  title: string
  count: number
  emails: ClassifiedEmail[]
  badgeColor: string
  defaultOpen?: boolean
  onDraftReply: (emailId: string) => void
}

function EmailGroup({ title, count, emails, badgeColor, defaultOpen = false, onDraftReply }: EmailGroupProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  if (count === 0) return null

  return (
    <div className="border border-gray-100 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
        onClick={() => setIsOpen((o) => !o)}
        aria-expanded={isOpen}
        aria-controls={`email-group-${title.toLowerCase().replace(' ', '-')}`}
      >
        <span className="text-sm font-semibold text-gray-700">{title}</span>
        <span className={`text-xs font-bold rounded-full px-2 py-0.5 ${badgeColor}`}>
          {count}
        </span>
      </button>

      {isOpen && (
        <div
          id={`email-group-${title.toLowerCase().replace(' ', '-')}`}
          className="divide-y divide-gray-100"
        >
          {emails.map((email) => (
            <EmailCard
              key={email.id}
              email={email}
              onDraftReply={onDraftReply}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function EmailSection({ emails, onDraftReply }: EmailSectionProps) {
  const urgent = emails.filter((e) => e.classification === 'urgent')
  const canWait = emails.filter((e) => e.classification === 'can_wait')
  const fiy = emails.filter((e) => e.classification === 'fyi')

  if (emails.length === 0) return null

  return (
    <section aria-label="Emails">
      <h2 className="text-base font-semibold text-gray-800 mb-3">Emails</h2>
      <div className="space-y-2">
        <EmailGroup title="Urgent" count={urgent.length} emails={urgent}
          badgeColor="bg-red-100 text-red-700" defaultOpen onDraftReply={onDraftReply} />
        <EmailGroup title="Can Wait" count={canWait.length} emails={canWait}
          badgeColor="bg-yellow-100 text-yellow-700" onDraftReply={onDraftReply} />
        <EmailGroup title="FYI" count={fiy.length} emails={fiy}
          badgeColor="bg-gray-200 text-gray-600" onDraftReply={onDraftReply} />
      </div>
    </section>
  )
}
