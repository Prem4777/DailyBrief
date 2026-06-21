/** Urgency classification for an email. */
export type EmailClassification = 'urgent' | 'can_wait' | 'fyi'

/** A Gmail message enriched with AI classification. */
export interface ClassifiedEmail {
  id: string
  subject: string
  sender: string
  sender_email: string
  snippet: string
  received_at: string // ISO 8601
  classification: EmailClassification
  classification_reason: string
  thread_id: string
}

/** A Google Calendar event with conflict/back-to-back metadata. */
export interface CalendarEvent {
  id: string
  title: string
  start: string // ISO 8601
  end: string   // ISO 8601
  attendees: string[]
  description: string | null
  location: string | null
  conflict_flag: boolean
  back_to_back_flag: boolean
  conflict_with_id: string | null
}

/** A contiguous free time window on the calendar. */
export interface FreeSlot {
  start: string  // ISO 8601
  end: string    // ISO 8601
  duration_minutes: number
}

/** Due-date classification for a Notion task. */
export type TaskClassification = 'overdue' | 'due_today' | 'due_later'

/** A Notion task enriched with a deterministic due-date classification. */
export interface ClassifiedTask {
  id: string
  title: string
  due_date: string | null // ISO date YYYY-MM-DD
  classification: TaskClassification
  project: string | null
  url: string
}

/** A semantic link between an email, event, and/or task. */
export interface CrossReference {
  email_id: string | null
  event_id: string | null
  task_id: string | null
  relationship_description: string
}

/** An AI-generated suggestion to schedule a task in a free slot. */
export interface CalendarProposal {
  task_id: string
  task_title: string
  proposed_start: string // ISO 8601
  proposed_end: string   // ISO 8601
  rationale: string
}

/** The full morning briefing payload. */
export interface Briefing {
  user_id: string
  generated_at: string // ISO 8601
  date: string         // YYYY-MM-DD
  focus_suggestion: string

  // Stats
  urgent_email_count: number
  meeting_count: number
  overdue_task_count: number
  calendar_conflict_flag: boolean

  // Detailed data
  emails: ClassifiedEmail[]
  events: CalendarEvent[]
  free_slots: FreeSlot[]
  tasks: ClassifiedTask[]

  // Enrichments
  cross_references: CrossReference[]
  proposals: CalendarProposal[]

  // Degraded state
  partial: boolean
  unavailable_sources: string[]
}

/** Lightweight summary for the briefing history list. */
export interface BriefingHistoryItem {
  id: string
  date: string         // YYYY-MM-DD
  generated_at: string // ISO 8601
  focus_suggestion: string | null
  urgent_email_count: number
  meeting_count: number
  overdue_task_count: number
  calendar_conflict_flag: boolean
  partial: boolean
}
