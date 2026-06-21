/**
 * TaskCard.tsx — A single task item card.
 *
 * Shows task title, project name, and a colored due-date chip.
 * Links to the Notion page via task.url.
 *
 * Props:
 *   - task: ClassifiedTask data
 */

import { ExternalLink } from 'lucide-react'
import React from 'react'
import type { ClassifiedTask } from '../../types/briefing'

interface TaskCardProps {
  task: ClassifiedTask
}

const DUE_CHIP_COLORS: Record<ClassifiedTask['classification'], string> = {
  overdue: 'bg-red-100 text-red-700',
  due_today: 'bg-amber-100 text-amber-700',
  due_later: 'bg-green-100 text-green-700',
}

const DUE_CHIP_LABELS: Record<ClassifiedTask['classification'], string> = {
  overdue: 'Overdue',
  due_today: 'Due Today',
  due_later: 'Due Later',
}

export default function TaskCard({ task }: TaskCardProps) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-gray-100 bg-white px-4 py-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="text-sm font-medium text-gray-900 truncate">{task.title}</p>
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-semibold ${DUE_CHIP_COLORS[task.classification]}`}
            aria-label={`Due status: ${DUE_CHIP_LABELS[task.classification]}`}
          >
            {task.due_date ?? DUE_CHIP_LABELS[task.classification]}
          </span>
        </div>
        {task.project && (
          <p className="text-xs text-gray-400 mt-0.5">{task.project}</p>
        )}
      </div>

      <a
        href={task.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
        aria-label={`Open "${task.title}" in Notion`}
      >
        <ExternalLink className="h-4 w-4" aria-hidden="true" />
      </a>
    </div>
  )
}
