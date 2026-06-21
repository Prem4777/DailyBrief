/**
 * BriefingPanel.tsx — Left-column container that assembles all briefing sections.
 *
 * Renders in this order:
 *   1. DateHeader        (date + run button)
 *   2. FocusSuggestion   (AI paragraph)
 *   3. StatCards         (urgent emails / meetings / overdue tasks)
 *   4. EmailSection      (grouped by classification)
 *   5. CalendarSection   (today's events)
 *   6. TaskSection       (grouped by due status)
 *   7. BriefingHistory   (link to history)
 */

import React from 'react'
import BriefingHistory from '../briefing/BriefingHistory'
import CalendarSection from '../briefing/CalendarSection'
import DateHeader from '../briefing/DateHeader'
import EmailSection from '../briefing/EmailSection'
import FocusSuggestion from '../briefing/FocusSuggestion'
import StatCards from '../briefing/StatCards'
import TaskSection from '../briefing/TaskSection'
import { useBriefing } from '../../hooks/useBriefing'
import { useBriefingStore } from '../../store/briefingStore'
import { generateDraft } from '../../api/actionsApi'

export default function BriefingPanel() {
  const { briefing, isLoading, runBriefing } = useBriefing()
  const setDraft = useBriefingStore((s) => s.setDraft)

  const handleDraftReply = async (emailId: string) => {
    try {
      const { draft } = await generateDraft(emailId)
      setDraft(emailId, draft)
    } catch (err) {
      console.error('Draft generation failed:', err)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <DateHeader onRunBriefing={runBriefing} isLoading={isLoading} />

      {briefing && (
        <>
          <FocusSuggestion text={briefing.focus_suggestion} />
          <StatCards
            urgentEmailCount={briefing.urgent_email_count}
            meetingCount={briefing.meeting_count}
            overdueTaskCount={briefing.overdue_task_count}
          />
          <EmailSection emails={briefing.emails} onDraftReply={handleDraftReply} />
          <CalendarSection
            events={briefing.events}
            unavailable={briefing.unavailable_sources.includes('gcal')}
          />
          <TaskSection tasks={briefing.tasks} />
          <BriefingHistory />
        </>
      )}

      {!briefing && !isLoading && (
        <p className="text-center text-gray-500 mt-16">
          Click "Run Briefing" to generate your morning brief.
        </p>
      )}
    </div>
  )
}
