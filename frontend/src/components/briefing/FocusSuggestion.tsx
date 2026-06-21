/**
 * FocusSuggestion.tsx — Card displaying the AI-generated focus paragraph.
 *
 * Props:
 *   - text: the focus suggestion string from the Briefing
 */

import { Lightbulb } from 'lucide-react'
import React from 'react'

interface FocusSuggestionProps {
  text: string
}

export default function FocusSuggestion({ text }: FocusSuggestionProps) {
  return (
    <div
      className="
        rounded-xl p-4
        bg-gradient-to-r from-blue-50 to-indigo-50
        border border-blue-100
      "
      role="region"
      aria-label="AI Focus Suggestion"
    >
      <div className="flex items-start gap-3">
        <Lightbulb
          className="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-500"
          aria-hidden="true"
        />
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-blue-600 mb-1">
            Focus Suggestion
          </p>
          <p className="text-sm text-gray-700 leading-relaxed">{text}</p>
        </div>
      </div>
    </div>
  )
}
