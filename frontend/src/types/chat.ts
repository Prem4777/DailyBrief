import type { CalendarProposal } from './briefing'

/** Role of a message participant. */
export type MessageRole = 'user' | 'assistant'

/** A single chat message in the conversation history. */
export interface ChatMessage {
  role: MessageRole
  content: string
  created_at: string // ISO 8601
}

/** Request body for POST /api/chat. */
export interface ChatRequest {
  message: string
}

/** Response from POST /api/chat. */
export interface ChatResponse {
  message: ChatMessage
  /** Populated when the assistant is proposing a calendar action. */
  pending_action: CalendarProposal | null
}
