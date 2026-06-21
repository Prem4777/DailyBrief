/**
 * ChatInput.tsx — Auto-resizing textarea with a Send button.
 *
 * Enter submits the message.
 * Shift+Enter inserts a newline.
 * Input and button are disabled while isTyping (via `disabled` prop).
 *
 * Props:
 *   - onSend: callback called with the trimmed message text
 *   - disabled: true while the assistant is typing
 */

import { SendHorizonal } from 'lucide-react'
import React, { useRef, useState } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled: boolean
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    // Auto-resize: reset to auto then set to scrollHeight
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }

  return (
    <div className="flex items-end gap-2 p-3">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        disabled={disabled}
        placeholder="Ask me about your day…"
        rows={1}
        className="
          flex-1 resize-none overflow-hidden rounded-xl border border-gray-300
          px-3 py-2 text-sm text-gray-800 placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-blue-400
          disabled:opacity-50 disabled:bg-gray-50
        "
        aria-label="Chat message input"
        aria-multiline="true"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        className="
          flex-shrink-0 rounded-xl bg-blue-600 p-2.5 text-white
          hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors
        "
        aria-label="Send message"
      >
        <SendHorizonal className="h-4 w-4" aria-hidden="true" />
      </button>
    </div>
  )
}
