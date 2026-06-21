/**
 * TaskSection.tsx — Three groups of tasks: Overdue, Due Today, Due Later.
 *
 * Each group has a colored header to signal urgency.
 *
 * Props:
 *   - tasks: ClassifiedTask list from the briefing
 */

import React from 'react'
import type { ClassifiedTask, TaskClassification } from '../../types/briefing'
import TaskCard from './TaskCard'

interface TaskSectionProps {
  tasks: ClassifiedTask[]
}

interface TaskGroupConfig {
  classification: TaskClassification
  label: string
  headerColor: string
}

const GROUPS: TaskGroupConfig[] = [
  { classification: 'overdue', label: 'Overdue', headerColor: 'text-red-600' },
  { classification: 'due_today', label: 'Due Today', headerColor: 'text-amber-600' },
  { classification: 'due_later', label: 'Due Later', headerColor: 'text-green-600' },
]

export default function TaskSection({ tasks }: TaskSectionProps) {
  if (tasks.length === 0) return null

  return (
    <section aria-label="Tasks">
      <h2 className="text-base font-semibold text-gray-800 mb-3">Tasks</h2>
      <div className="space-y-4">
        {GROUPS.map(({ classification, label, headerColor }) => {
          const group = tasks.filter((t) => t.classification === classification)
          if (group.length === 0) return null

          return (
            <div key={classification}>
              <h3 className={`text-xs font-bold uppercase tracking-wider mb-2 ${headerColor}`}>
                {label} ({group.length})
              </h3>
              <div className="space-y-2">
                {group.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
