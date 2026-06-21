/**
 * DateHeader.tsx — Shows today's date and the "Run Briefing" button.
 *
 * Props:
 *   - onRunBriefing: callback to trigger briefing generation
 *   - isLoading: shows a spinner on the button while running
 */

import { Loader2, Settings, Sparkles } from 'lucide-react'
import React from 'react'
import { Link } from 'react-router-dom'

interface DateHeaderProps {
  onRunBriefing: () => void
  isLoading: boolean
}

function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default function DateHeader({ onRunBriefing, isLoading }: DateHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-xs font-medium uppercase tracking-widest text-gray-400">
          Today
        </p>
        <h1 className="text-2xl font-bold text-gray-900">{formatDate(new Date())}</h1>
      </div>

      <div className="flex items-center gap-2">
        <Link
          to="/settings"
          className="inline-flex items-center justify-center rounded-lg border border-gray-200 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors"
          aria-label="Settings"
        >
          <Settings className="h-4 w-4" aria-hidden="true" />
        </Link>

        <button
          onClick={onRunBriefing}
          disabled={isLoading}
          className="
            inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2
            text-sm font-semibold text-white shadow-sm
            hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed
            transition-colors
          "
          aria-label="Run morning briefing"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Sparkles className="h-4 w-4" aria-hidden="true" />
          )}
          {isLoading ? 'Running…' : 'Run Briefing'}
        </button>
      </div>
    </div>
  )
}
