'use client'

import { useState, useEffect } from 'react'
import AppShell from '@/components/layout/AppShell'
import { telegramApi, combosApi, type TelegramStatus, type ComboInfo } from '@/lib/api'

export default function TelegramPage() {
  const [status, setStatus] = useState<TelegramStatus | null>(null)
  const [combos, setCombos] = useState<ComboInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [connecting, setConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Form state
  const [botToken, setBotToken] = useState('')
  const [selectedCombo, setSelectedCombo] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [statusData, comboList] = await Promise.all([
        telegramApi.getStatus(),
        combosApi.getAll()
      ])
      
      setStatus(statusData)
      setCombos(comboList)
      
      if (comboList.length > 0 && !selectedCombo) {
        setSelectedCombo(statusData.combo_id || comboList[0].id)
      }
    } catch (err) {
      console.error('Failed to load data:', err)
      setError('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async () => {
    if (!botToken.trim() || !selectedCombo) {
      setError('Please enter bot token and select AI Combo')
      return
    }

    setConnecting(true)
    setError(null)

    try {
      const result = await telegramApi.connect(botToken.trim(), selectedCombo)
      setStatus(result)
      setBotToken('') // Clear token after successful connection
      setError(null)
    } catch (err: any) {
      console.error('Failed to connect:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to connect bot'
      setError(errorMsg)
    } finally {
      setConnecting(false)
    }
  }

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect the Telegram bot?')) {
      return
    }

    setConnecting(true)
    setError(null)

    try {
      await telegramApi.disconnect()
      await loadData() // Reload status
    } catch (err: any) {
      console.error('Failed to disconnect:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to disconnect bot'
      setError(errorMsg)
    } finally {
      setConnecting(false)
    }
  }

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-full">
          <p className="font-body-lg text-body-lg text-on-surface-variant">Loading...</p>
        </div>
      </AppShell>
    )
  }

  const isConnected = status?.is_connected || false

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto px-4 md:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="font-headline-lg text-headline-lg text-on-surface mb-2">Telegram Bot</h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Connect your Telegram bot to provide AI assistance via Telegram
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 p-4 rounded-lg bg-error-container border border-danger">
            <p className="font-body-md text-body-md text-on-error-container">{error}</p>
          </div>
        )}

        {/* Main Card */}
        <div className="rounded-lg bg-surface-container border border-border-subtle p-6">
          {/* Status Section */}
          <div className="mb-6">
            <h2 className="font-headline-sm text-headline-sm text-on-surface mb-4">Status</h2>
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-success' : 'bg-outline'}`} />
              <span className="font-body-lg text-body-lg text-on-surface">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          {!isConnected ? (
            /* Disconnected State - Show Connection Form */
            <>
              <div className="mb-6">
                <label htmlFor="botToken" className="block font-label-md text-label-md text-on-surface mb-2">
                  Bot Token
                </label>
                <input
                  id="botToken"
                  type="password"
                  value={botToken}
                  onChange={(e) => setBotToken(e.target.value)}
                  placeholder="Enter your Telegram Bot Token"
                  className="w-full px-4 py-3 rounded-lg bg-surface-container-low border border-outline text-on-surface placeholder:text-outline focus:outline-none focus:border-primary transition-colors font-body-md text-body-md"
                  disabled={connecting}
                />
                <p className="mt-2 font-body-sm text-body-sm text-outline">
                  Get your bot token from @BotFather on Telegram
                </p>
              </div>

              <div className="mb-6">
                <label htmlFor="combo" className="block font-label-md text-label-md text-on-surface mb-2">
                  AI Combo
                </label>
                <select
                  id="combo"
                  value={selectedCombo}
                  onChange={(e) => setSelectedCombo(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-surface-container-low border border-outline text-on-surface focus:outline-none focus:border-primary transition-colors font-body-md text-body-md"
                  disabled={connecting || combos.length === 0}
                >
                  {combos.length === 0 ? (
                    <option value="">Loading...</option>
                  ) : (
                    combos.map((combo) => (
                      <option key={combo.id} value={combo.id}>
                        {combo.name}
                      </option>
                    ))
                  )}
                </select>
                <p className="mt-2 font-body-sm text-body-sm text-outline">
                  AI Combo to use for bot responses
                </p>
              </div>

              <button
                onClick={handleConnect}
                disabled={connecting || !botToken.trim() || !selectedCombo}
                className="px-6 py-3 rounded-lg bg-primary-container text-on-primary-container font-headline-sm text-headline-sm font-semibold hover:bg-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {connecting ? 'Connecting...' : 'Connect'}
              </button>
            </>
          ) : (
            /* Connected State - Show Bot Info */
            <>
              {status?.bot_info && (
                <div className="mb-6 space-y-4">
                  <div>
                    <span className="block font-label-sm text-label-sm text-on-surface-variant mb-1">Bot</span>
                    <span className="font-body-lg text-body-lg text-on-surface">
                      @{status.bot_info.bot_username}
                    </span>
                  </div>

                  <div>
                    <span className="block font-label-sm text-label-sm text-on-surface-variant mb-1">Bot Name</span>
                    <span className="font-body-lg text-body-lg text-on-surface">
                      {status.bot_info.bot_name}
                    </span>
                  </div>

                  <div>
                    <span className="block font-label-sm text-label-sm text-on-surface-variant mb-1">AI Combo</span>
                    <span className="font-body-lg text-body-lg text-on-surface">
                      {combos.find(c => c.id === status.combo_id)?.name || status.combo_id}
                    </span>
                  </div>

                  <div>
                    <span className="block font-label-sm text-label-sm text-on-surface-variant mb-1">Token</span>
                    <span className="font-body-lg text-body-lg text-outline font-code-block">
                      ••••••••••••••••
                    </span>
                  </div>
                </div>
              )}

              <button
                onClick={handleDisconnect}
                disabled={connecting}
                className="px-6 py-3 rounded-lg border border-danger text-danger bg-transparent hover:bg-danger hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-headline-sm text-headline-sm font-semibold"
              >
                {connecting ? 'Disconnecting...' : 'Disconnect'}
              </button>
            </>
          )}
        </div>

        {/* Info Section */}
        {!isConnected && (
          <div className="mt-6 rounded-lg bg-surface-container-low border border-border-subtle p-6">
            <h3 className="font-headline-sm text-headline-sm text-on-surface mb-3">How to Connect</h3>
            <ol className="space-y-2 font-body-md text-body-md text-on-surface-variant list-decimal list-inside">
              <li>Open Telegram and search for @BotFather</li>
              <li>Send /newbot to create a new bot</li>
              <li>Follow the instructions to get your bot token</li>
              <li>Paste the token above and select an AI Combo</li>
              <li>Click Connect to start your bot</li>
            </ol>
          </div>
        )}
      </div>
    </AppShell>
  )
}
