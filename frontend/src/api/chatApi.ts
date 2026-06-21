/**
 * chatApi.ts — API function for the conversational chat endpoint.
 */

import type { ChatResponse } from '../types/chat'
import apiClient from './client'

/**
 * Send a user message to the DailyBrief assistant.
 *
 * @param message - The plain-text message from the user.
 * @returns The assistant's ChatResponse, optionally including a pending_action.
 */
export async function sendMessage(message: string): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/api/chat', { message })
  return data
}
