import { Suspense } from 'react'
import AppShell from '@/components/layout/AppShell'
import ChatContent from './ChatContent'

export default function ChatPage() {
  return (
    <AppShell>
      <Suspense fallback={
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-on-surface-variant">Loading chat...</p>
          </div>
        </div>
      }>
        <ChatContent />
      </Suspense>
    </AppShell>
  )
}
