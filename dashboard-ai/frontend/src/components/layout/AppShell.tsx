'use client'

import { useState, ReactNode } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

interface AppShellProps {
  children: ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)

  const toggleSidebar = () => {
    if (window.innerWidth < 768) {
      setMobileDrawerOpen(!mobileDrawerOpen)
    } else {
      setSidebarOpen(!sidebarOpen)
    }
  }

  const closeMobileDrawer = () => {
    setMobileDrawerOpen(false)
  }

  return (
    <div className="min-h-screen bg-surface">
      {/* Mobile overlay */}
      {mobileDrawerOpen && (
        <div
          className="fixed inset-0 bg-surface/80 z-40 md:hidden"
          onClick={closeMobileDrawer}
        />
      )}

      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        isMobileDrawerOpen={mobileDrawerOpen}
        onClose={closeMobileDrawer}
      />

      {/* Main content area */}
      <div
        className={`min-h-screen transition-all duration-300 ${
          sidebarOpen ? 'md:pl-64' : 'md:pl-0'
        }`}
      >
        {/* Header */}
        <Header
          sidebarOpen={sidebarOpen}
          onToggleSidebar={toggleSidebar}
        />

        {/* Main content */}
        <main className="pt-14 bg-surface min-h-screen">
          {children}
        </main>
      </div>
    </div>
  )
}
