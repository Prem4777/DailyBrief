/**
 * BriefingHistory.tsx — Button that opens a slide-over drawer of past briefings.
 *
 * Fetches history from the API when the drawer opens.
 * Clicking an item navigates to /history (full history page).
 */

import { History, X } from 'lucide-react'
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getBriefingHistory } from '../../api/briefingApi'
import type { BriefingHistoryItem } from '../../types/briefing'

export default function BriefingHistory() {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const navigate = useNavigate()

  const { data: history, isLoading } = useQuery({
    queryKey: ['briefing-history'],
    queryFn: getBriefingHistory,
    enabled: drawerOpen, // only fetch when the drawer is open
  })

  return (
    <>
      <button
        onClick={() => setDrawerOpen(true)}
        className="
          w-full flex items-center justify-center gap-2
          rounded-xl border border-gray-200 bg-white px-4 py-3
          text-sm font-medium text-gray-600 hover:bg-gray-50
          transition-colors
        "
      >
        <History className="h-4 w-4" aria-hidden="true" />
        View Briefing History
      </button>

      {/* Slide-over drawer */}
      {drawerOpen && (
        <div
          className="fixed inset-0 z-40 flex"
          role="dialog"
          aria-modal="true"
          aria-label="Briefing History"
        >
          {/* Backdrop */}
          <div
            className="flex-1 bg-black/30"
            onClick={() => setDrawerOpen(false)}
            aria-hidden="true"
          />

          {/* Drawer panel */}
          <div className="w-80 bg-white shadow-xl flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b">
              <h2 className="text-sm font-semibold text-gray-700">Briefing History</h2>
              <button
                onClick={() => setDrawerOpen(false)}
                aria-label="Close history drawer"
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {isLoading && (
                <p className="text-sm text-gray-500">Loading…</p>
              )}
              {history?.map((item: BriefingHistoryItem) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setDrawerOpen(false)
                    navigate(`/history`) // TODO: navigate to specific item
                  }}
                  className="
                    w-full text-left rounded-lg border border-gray-100
                    px-3 py-2 hover:bg-gray-50 transition-colors
                  "
                >
                  <p className="text-sm font-medium text-gray-800">{item.date}</p>
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                    {item.focus_suggestion ?? 'No summary available.'}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
