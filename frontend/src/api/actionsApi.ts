/**
 * actionsApi.ts — API functions for draft generation and calendar actions.
 */

import type { CalendarProposal } from '../types/briefing'
import apiClient from './client'

/**
 * Generate a draft email reply for a given email ID.
 *
 * @param emailId - The ClassifiedEmail ID to draft a reply for.
 * @returns An object containing the generated draft text.
 */
export async function generateDraft(emailId: string): Promise<{ draft: string }> {
  const { data } = await apiClient.post<{ draft: string }>('/api/actions/draft', null, {
    params: { email_id: emailId },
  })
  return data
}

/**
 * Request a calendar slot proposal for a task.
 *
 * @param taskId - The ClassifiedTask ID to propose a slot for.
 * @returns A CalendarProposal for the user to confirm or reject.
 */
export async function proposeCalendarSlot(taskId: string): Promise<CalendarProposal> {
  const { data } = await apiClient.post<CalendarProposal>(
    '/api/actions/calendar/propose',
    null,
    { params: { task_id: taskId } },
  )
  return data
}

/**
 * Confirm a calendar proposal and create the event.
 *
 * @param proposal - The CalendarProposal the user confirmed.
 * @returns An object containing the created Google Calendar event ID.
 */
export async function confirmCalendarAction(
  proposal: CalendarProposal,
): Promise<{ event_id: string }> {
  const { data } = await apiClient.post<{ event_id: string }>(
    '/api/actions/calendar/confirm',
    proposal,
  )
  return data
}
