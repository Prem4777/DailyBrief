/**
 * DraftReplyDrawer.tsx — Expandable panel showing an editable draft reply.
 *
 * Props:
 *   - emailId: ID of the email this draft belongs to
 *   - draft: the draft text (null while loading)
 */

import { Check, Copy, Loader2 } from 'lucide-react'
import React, { useState } from 'react'
import { useBriefingStore } from '../../store/briefingStore'

interface DraftReplyDrawerProps {
  emailId: string
  draft: string | null
}

export default function DraftReplyDrawer({ emailId, draft }: DraftReplyDrawerProps) {
  const setDraft = useBriefingStore((s) => s.setDraft)
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    if (!draft) return
    try {
      await navigator.clipboard.writeText(draft)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // TODO: fallback for browsers that block clipboard API
    }
  }

  return (
    <div className="mt-3 rounded-lg border border-blue-100 bg-blue-50 p-3">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-semibold text-blue-700">Draft Reply</p>
        <button
          onClick={handleCopy}
          disabled={!draft}
          className="
            inline-flex items-center gap-1 rounded px-2 py-1
            text-xs text-blue-600 hover:bg-blue-100 transition-colors
            disabled:opacity-40
          "
          aria-label="Copy draft to clipboard"
        >
          {copied ? (
            <Check className="h-3 w-3" aria-hidden="true" />
          ) : (
            <Copy className="h-3 w-3" aria-hidden="true" />
          )}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      {draft === null ? (
        <div className="flex items-center gap-2 text-xs text-blue-500">
          <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
          Generating draft…
        </div>
      ) : (
        <textarea
          className="
            w-full rounded border border-blue-200 bg-white p-2
            text-xs text-gray-700 resize-none focus:outline-none focus:ring-1
            focus:ring-blue-400
          "
          rows={5}
          value={draft}
          onChange={(e) => setDraft(emailId, e.target.value)}
          aria-label="Editable draft reply"
        />
      )}
    </div>
  )
}
