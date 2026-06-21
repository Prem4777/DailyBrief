/**
 * useChat.ts — Custom hook managing chat state and assistant interactions.
 *
 * Handles message sending, typing indicator, and pending calendar actions
 * that the user needs to confirm or reject.
 */

import { useState } from 'react'
import { confirmCalendarAction } from '../api/actionsApi'
import { sendMessage as sendMessageApi } from '../api/chatApi'
import type { CalendarProposal } from '../types/briefing'
import type { ChatMessage } from '../types/chat'

interface UseChatResult {
  /** Full ordered list of chat messages in the conversation. */
  messages: ChatMessage[]
  /** True while waiting for the assistant's response. */
  isTyping: boolean
  /** Populated when the assistant proposes a calendar action. */
  pendingAction: CalendarProposal | null
  /** Send a text message to the assistant. */
  sendMessage: (text: string) => Promise<void>
  /** Confirm the pending calendar action. */
  confirmAction: () => Promise<void>
  /** Reject the pending calendar action. */
  rejectAction: () => void
}

export function useChat(): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [pendingAction, setPendingAction] = useState<CalendarProposal | null>(null)

  const sendMessage = async (text: string): Promise<void> => {
    if (!text.trim()) return

    // Optimistically add the user message
    const userMsg: ChatMessage = {
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])
    setIsTyping(true)

    try {
      const response = await sendMessageApi(text)
      setMessages((prev) => [...prev, response.message])

      if (response.pending_action) {
        setPendingAction(response.pending_action)
      }
    } catch (err) {
      // TODO: surface a proper error toast instead of a plain text message
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: 'Something went wrong. Please try again.',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsTyping(false)
    }
  }

  const confirmAction = async (): Promise<void> => {
    if (!pendingAction) return

    try {
      // TODO: surface the created event_id to the user (e.g. a success toast)
      await confirmCalendarAction(pendingAction)
      setPendingAction(null)

      const confirmMsg: ChatMessage = {
        role: 'assistant',
        content: `Done! "${pendingAction.task_title}" has been added to your calendar.`,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, confirmMsg])
    } catch {
      // TODO: proper error handling
    }
  }

  const rejectAction = (): void => {
    setPendingAction(null)
    const rejectMsg: ChatMessage = {
      role: 'assistant',
      content: "No problem — I've cancelled that suggestion.",
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, rejectMsg])
  }

  return {
    messages,
    isTyping,
    pendingAction,
    sendMessage,
    confirmAction,
    rejectAction,
  }
}
