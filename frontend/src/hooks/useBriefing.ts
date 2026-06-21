/**
 * useBriefing.ts — Custom hook providing briefing data and derived selectors.
 *
 * Wraps the briefingStore and exposes convenient filtered lists so components
 * don't need to perform their own array filtering.
 */

import { useBriefingStore } from '../store/briefingStore'
import type { CalendarEvent, ClassifiedEmail, ClassifiedTask } from '../types/briefing'

interface UseBriefingResult {
  briefing: ReturnType<typeof useBriefingStore.getState>['briefing']
  isLoading: boolean
  error: string | null
  runBriefing: () => Promise<void>

  // Derived email selectors
  urgentEmails: ClassifiedEmail[]
  canWaitEmails: ClassifiedEmail[]
  fiyEmails: ClassifiedEmail[]

  // Derived task selectors
  overdueTasks: ClassifiedTask[]
  dueTodayTasks: ClassifiedTask[]
  dueLaterTasks: ClassifiedTask[]

  // Derived event selectors
  conflictEvents: CalendarEvent[]
}

export function useBriefing(): UseBriefingResult {
  // Call the store once — Zustand infers the full typed state here
  const { briefing, isLoading, error, runBriefing } = useBriefingStore()

  const emails = briefing?.emails ?? []
  const tasks = briefing?.tasks ?? []
  const events = briefing?.events ?? []

  return {
    briefing,
    isLoading,
    error,
    runBriefing,

    // Email selectors
    urgentEmails: emails.filter((e: ClassifiedEmail) => e.classification === 'urgent'),
    canWaitEmails: emails.filter((e: ClassifiedEmail) => e.classification === 'can_wait'),
    fiyEmails: emails.filter((e: ClassifiedEmail) => e.classification === 'fyi'),

    // Task selectors
    overdueTasks: tasks.filter((t: ClassifiedTask) => t.classification === 'overdue'),
    dueTodayTasks: tasks.filter((t: ClassifiedTask) => t.classification === 'due_today'),
    dueLaterTasks: tasks.filter((t: ClassifiedTask) => t.classification === 'due_later'),

    // Event selectors
    conflictEvents: events.filter((e: CalendarEvent) => e.conflict_flag),
  }
}
