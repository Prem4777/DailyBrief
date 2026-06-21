/**
 * MessageList.tsx — Scrollable list of chat messages with auto-scroll.
 *
 * Auto-scrolls to the bottom whenever messages change.
 * Shows a typing indicator when isTyping is true.
 *
 * Props:
 *   - messages: ordered list of ChatMessage objects
 *   - isTyping: true while waiting for the assistant response
 */

import React, { useEffect, useRef } from 'react'
import type { ChatMessage } from '../../types/chat'
import MessageBubble from './MessageBubble'

interface MessageListProps {
  messages: ChatMessage[]
  isTyping: boolean
}

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-2" aria-live="polite" aria-label="Assistant is typing">
      <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 flex gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
            style={{ animationDelay: `${i * 150}ms` }}
            aria-hidden="true"
          />
        ))}
      </div>
    </div>
  )
}

export default function MessageList({ messages, isTyping }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Scroll to bottom whenever the message list or typing state changes
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <div
      className="p-4 space-y-0"
      role="list"
      aria-label="Chat messages"
    >
      {messages.length === 0 && (
        <p className="text-center text-sm text-gray-400 py-8">
          Ask me anything about your day…
        </p>
      )}

      {messages.map((msg, idx) => (
        <MessageBubble key={idx} message={msg} />
      ))}

      {isTyping && <TypingIndicator />}

      {/* Invisible scroll anchor */}
      <div ref={bottomRef} aria-hidden="true" />
    </div>
  )
}
