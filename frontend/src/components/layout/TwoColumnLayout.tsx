/**
 * TwoColumnLayout.tsx — CSS Grid two-column wrapper.
 *
 * Left column (60%): briefing panel, independently scrollable.
 * Right column (40%): chat panel, independently scrollable.
 */

import React from 'react'

interface TwoColumnLayoutProps {
  left: React.ReactNode
  right: React.ReactNode
}

export default function TwoColumnLayout({ left, right }: TwoColumnLayoutProps) {
  return (
    <div className="grid h-screen overflow-hidden" style={{ gridTemplateColumns: '60% 40%' }}>
      {/* Left column — briefing content */}
      <div className="overflow-y-auto border-r border-gray-200 bg-white">
        {left}
      </div>

      {/* Right column — chat panel */}
      <div className="overflow-hidden bg-gray-50 flex flex-col">
        {right}
      </div>
    </div>
  )
}
