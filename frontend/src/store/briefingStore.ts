/**
 * briefingStore.ts — Zustand store for briefing state.
 *
 * Manages the current briefing, loading/error state, and per-email draft replies.
 */

import { create } from 'zustand'
import * as briefingApi from '../api/briefingApi'
import type { Briefing } from '../types/briefing'

interface BriefingState {
  /** The most recently generated or loaded briefing. */
  briefing: Briefing | null
  /** True while the briefing pipeline is running. */
  isLoading: boolean
  /** Error message from the last failed operation, or null. */
  error: string | null
  /** Map from email ID → generated draft reply text. */
  draftsByEmailId: Record<string, string>

  // Actions
  runBriefing: () => Promise<void>
  setDraft: (emailId: string, draft: string) => void
  clearDraft: (emailId: string) => void
}

export const useBriefingStore = create<BriefingState>((set) => ({
  briefing: null,
  isLoading: false,
  error: null,
  draftsByEmailId: {},

  runBriefing: async () => {
    set({ isLoading: true, error: null })
    try {
      const briefing = await briefingApi.runBriefing()
      set({ briefing, isLoading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An unknown error occurred'
      set({ isLoading: false, error: message })
    }
  },

  setDraft: (emailId, draft) => {
    set((state) => ({
      draftsByEmailId: { ...state.draftsByEmailId, [emailId]: draft },
    }))
  },

  clearDraft: (emailId) => {
    set((state) => {
      const updated = { ...state.draftsByEmailId }
      delete updated[emailId]
      return { draftsByEmailId: updated }
    })
  },
}))
