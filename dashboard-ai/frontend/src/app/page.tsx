'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to chat page
    router.push('/chat')
  }, [router])

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <p className="font-body-lg text-body-lg text-on-surface-variant">
        Loading...
      </p>
    </div>
  )
}
