/**
 * HistoryPage.tsx — Full briefing history list with search and detail modal.
 *
 * Features:
 *   - Fetches full history list via React Query
 *   - Text search filters items by date or focus suggestion
 *   - Clicking an item loads and shows the full briefing in a modal
 */

import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getBriefingById, getBriefingHistory } from '../api/briefingApi'
import type { Briefing, BriefingHistoryItem } from '../types/briefing'
import { ArrowLeft, Search, X } from 'lucide-react'

export default function HistoryPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const {
    data: history,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['briefing-history'],
    queryFn: getBriefingHistory,
  })

  const { data: selectedBriefing, isLoading: loadingDetail } = useQuery<Briefing>({
    queryKey: ['briefing-detail', selectedId],
    queryFn: () => getBriefingById(selectedId!),
    enabled: selectedId !== null,
  })

  const filtered = (history ?? []).filter((item: BriefingHistoryItem) => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      item.date.includes(q) ||
      (item.focus_suggestion ?? '').toLowerCase().includes(q)
    )
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center gap-4">
          <Link to="/" className="text-gray-500 hover:text-gray-700" aria-label="Back to dashboard">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-lg font-bold text-gray-900">Briefing History</h1>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-6">
        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" aria-hidden="true" />
          <input
            type="search"
            placeholder="Search by date or topic…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="
              w-full rounded-xl border border-gray-300 pl-9 pr-4 py-2 text-sm
              focus:outline-none focus:ring-2 focus:ring-blue-500
            "
            aria-label="Search briefing history"
          />
        </div>

        {/* List */}
        {isLoading && <p className="text-sm text-gray-500 text-center py-8">Loading history…</p>}
        {error && <p className="text-sm text-red-600 text-center py-8">Failed to load history.</p>}

        <div className="space-y-3">
          {filtered.map((item: BriefingHistoryItem) => (
            <button
              key={item.id}
              onClick={() => setSelectedId(item.id)}
              className="
                w-full text-left rounded-xl border border-gray-200 bg-white
                px-4 py-3 hover:bg-gray-50 transition-colors shadow-sm
              "
            >
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm font-semibold text-gray-800">{item.date}</p>
                <div className="flex gap-2 text-xs">
                  {item.urgent_email_count > 0 && (
                    <span className="text-red-600">{item.urgent_email_count} urgent</span>
                  )}
                  {item.meeting_count > 0 && (
                    <span className="text-blue-600">{item.meeting_count} meetings</span>
                  )}
                  {item.overdue_task_count > 0 && (
                    <span className="text-amber-600">{item.overdue_task_count} overdue</span>
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-500 line-clamp-2">
                {item.focus_suggestion ?? 'No summary available.'}
              </p>
              {item.partial && (
                <span className="inline-block mt-1 text-xs text-amber-600 bg-amber-50 rounded px-1.5 py-0.5">
                  Partial
                </span>
              )}
            </button>
          ))}
        </div>
      </main>

      {/* Detail modal */}
      {selectedId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between px-5 py-4 border-b">
              <p className="text-sm font-semibold text-gray-800">
                {selectedBriefing?.date ?? 'Loading…'}
              </p>
              <button
                onClick={() => setSelectedId(null)}
                aria-label="Close briefing detail"
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-5">
              {loadingDetail && (
                <p className="text-sm text-gray-500">Loading briefing details…</p>
              )}
              {selectedBriefing && (
                <>
                  {selectedBriefing.focus_suggestion && (
                    <p className="text-sm text-gray-700 leading-relaxed mb-4">
                      {selectedBriefing.focus_suggestion}
                    </p>
                  )}

                  {/* Emails */}
                  {selectedBriefing.emails && selectedBriefing.emails.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Emails</p>
                      <ul className="space-y-1.5">
                        {selectedBriefing.emails.map((e) => (
                          <li key={e.id} className="flex items-start gap-2 text-xs text-gray-700">
                            <span className={`mt-0.5 shrink-0 rounded px-1 py-0.5 font-medium ${
                              e.classification === 'urgent' ? 'bg-red-100 text-red-700' :
                              e.classification === 'can_wait' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-500'
                            }`}>
                              {e.classification === 'can_wait' ? 'wait' : e.classification}
                            </span>
                            <span><span className="font-medium">{e.sender}</span>: {e.subject}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Events */}
                  {selectedBriefing.events && selectedBriefing.events.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Calendar</p>
                      <ul className="space-y-1.5">
                        {selectedBriefing.events.map((ev) => (
                          <li key={ev.id} className="text-xs text-gray-700 flex items-center gap-1.5">
                            {ev.conflict_flag && <span className="text-red-500" title="Conflict">⚠</span>}
                            <span className="font-medium">{new Date(ev.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            <span>{ev.title}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Tasks */}
                  {selectedBriefing.tasks && selectedBriefing.tasks.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Tasks</p>
                      <ul className="space-y-1.5">
                        {selectedBriefing.tasks.map((t) => (
                          <li key={t.id} className="flex items-start gap-2 text-xs text-gray-700">
                            <span className={`mt-0.5 shrink-0 rounded px-1 py-0.5 font-medium ${
                              t.classification === 'overdue' ? 'bg-red-100 text-red-700' :
                              t.classification === 'due_today' ? 'bg-amber-100 text-amber-700' :
                              'bg-gray-100 text-gray-500'
                            }`}>
                              {t.classification.replace('_', ' ')}
                            </span>
                            <span>{t.title}{t.due_date ? <span className="text-gray-400 ml-1">· {t.due_date}</span> : null}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <p className="text-xs text-gray-400 mt-2 pt-3 border-t border-gray-100">
                    {selectedBriefing.urgent_email_count} urgent email(s) ·{' '}
                    {selectedBriefing.meeting_count} meeting(s) ·{' '}
                    {selectedBriefing.overdue_task_count} overdue task(s)
                    {selectedBriefing.partial && <span className="ml-2 text-amber-500">· partial</span>}
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
