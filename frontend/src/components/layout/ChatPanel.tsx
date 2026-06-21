/**
 * ChatPanel.tsx — Right-column chat container.
 *
 * Fixed height, internal scroll for the message list.
 * Renders: ConfirmActionBanner (when pending), MessageList, ChatInput.
 */

import React from 'react'
import ChatInput from '../chat/ChatInput'
import ConfirmActionBanner from '../chat/ConfirmActionBanner'
import MessageList from '../chat/MessageList'
import { useChat } from '../../hooks/useChat'

export default function ChatPanel() {
  const {
    messages,
    isTyping,
    pendingAction,
    sendMessage,
    confirmAction,
    rejectAction,
  } = useChat()

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-white">
        <h2 className="text-sm font-semibold text-gray-700">DailyBrief Assistant</h2>
      </div>

      {/* Pending action banner */}
      {pendingAction && (
        <ConfirmActionBanner
          proposal={pendingAction}
          onConfirm={confirmAction}
          onReject={rejectAction}
        />
      )}

      {/* Message list — flex-1 so it fills remaining height */}
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} isTyping={isTyping} />
      </div>

      {/* Input — pinned to bottom */}
      <div className="border-t border-gray-200 bg-white">
        <ChatInput onSend={sendMessage} disabled={isTyping} />
      </div>
    </div>
  )
}
