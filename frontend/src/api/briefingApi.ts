/**
 * briefingApi.ts — API functions for briefing generation and history.
 */

import type { Briefing, BriefingHistoryItem } from '../types/briefing'
import apiClient from './client'

/** Trigger a new briefing generation and return the result. */
export async function runBriefing(): Promise<Briefing> {
  const { data } = await apiClient.post<Briefing>('/api/briefing/run')
  return data
}

/**
 * Return the current session briefing, or null if none has been generated.
 */
export async function getCurrentBriefing(): Promise<Briefing | null> {
  const { data } = await apiClient.get<Briefing | null>('/api/briefing/current')
  return data
}

/** Return a list of past briefing summaries, most recent first. */
export async function getBriefingHistory(): Promise<BriefingHistoryItem[]> {
  const { data } = await apiClient.get<BriefingHistoryItem[]>('/api/briefing/history')
  return data
}

/** Return the full briefing for a given history item ID. */
export async function getBriefingById(id: string): Promise<Briefing> {
  const { data } = await apiClient.get<Briefing>(`/api/briefing/history/${id}`)
  return data
}
