/**
 * MessageBubble.tsx — Renders a single chat message as a styled bubble.
 *
 * User messages: right-aligned, blue background.
 * Assistant messages: left-aligned, gray background.
 *
 * Props:
 *   - message: ChatMessage data
 */

import React from 'react'
import type { ChatMessage } from '../../types/chat'

interface MessageBubbleProps {
  message: ChatMessage
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-2`}
      role="listitem"
      aria-label={`${isUser ? 'You' : 'Assistant'}: ${message.content}`}
    >
      <div
        className={`
          max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed
          ${isUser
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-gray-100 text-gray-800 rounded-bl-sm'
          }
        `}
      >
        {message.content}
        <p
          className={`text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-400'}`}
          aria-label="Message time"
        >
          {new Date(message.created_at).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  )
}
