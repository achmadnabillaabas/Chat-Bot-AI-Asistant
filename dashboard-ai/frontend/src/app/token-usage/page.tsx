'use client'

import { useState, useEffect } from 'react'
import AppShell from '@/components/layout/AppShell'
import { analyticsApi, type UsageSummary, type DailyUsage, type ComboUsage, type RequestHistory } from '@/lib/api'

export default function TokenUsagePage() {
  const [summary, setSummary] = useState<UsageSummary | null>(null)
  const [timeseries, setTimeseries] = useState<DailyUsage[]>([])
  const [comboUsage, setComboUsage] = useState<ComboUsage[]>([])
  const [requests, setRequests] = useState<RequestHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [days, setDays] = useState(7)
  const [page, setPage] = useState(1)

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [summaryData, timeseriesData, comboData, requestsData] = await Promise.all([
        analyticsApi.getSummary(days),
        analyticsApi.getTimeseries(days),
        analyticsApi.getByCombo(days),
        analyticsApi.getRequests(page, 20, days)
      ])
      
      setSummary(summaryData)
      setTimeseries(timeseriesData)
      setComboUsage(comboData)
      setRequests(requestsData)
    } catch (err) {
      console.error('Failed to load analytics:', err)
      setError('Failed to load analytics data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [days, page])

  if (loading && !summary) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-full">
          <p className="font-body-lg text-body-lg text-on-surface-variant">Loading analytics...</p>
        </div>
      </AppShell>
    )
  }

  const hasData = summary && summary.total_requests > 0

  return (
    <AppShell>
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="font-headline-lg text-headline-lg text-on-surface">Token Usage</h1>
          <button
            onClick={loadData}
            className="px-4 py-2 rounded-lg border border-outline text-on-surface bg-transparent hover:bg-surface-container-high transition-colors font-body-md text-body-md"
          >
            Refresh
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 rounded-lg bg-error-container border border-danger">
            <p className="font-body-md text-body-md text-on-error-container">{error}</p>
          </div>
        )}

        {!hasData ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="text-center max-w-md">
              <h2 className="font-headline-md text-headline-md text-on-surface mb-2">No token usage yet</h2>
              <p className="font-body-lg text-body-lg text-on-surface-variant">
                Your AI request statistics will appear here after your first conversation.
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* KPI Summary */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="p-4 rounded-lg bg-surface-container border border-border-subtle">
                <p className="font-label-sm text-label-sm text-on-surface-variant mb-1">Total Requests</p>
                <p className="font-headline-md text-headline-md text-on-surface font-code-block">{summary.total_requests.toLocaleString()}</p>
              </div>
              <div className="p-4 rounded-lg bg-surface-container border border-border-subtle">
                <p className="font-label-sm text-label-sm text-on-surface-variant mb-1">Input Tokens</p>
                <p className="font-headline-md text-headline-md text-on-surface font-code-block">{summary.total_input_tokens.toLocaleString()}</p>
              </div>
              <div className="p-4 rounded-lg bg-surface-container border border-border-subtle">
                <p className="font-label-sm text-label-sm text-on-surface-variant mb-1">Output Tokens</p>
                <p className="font-headline-md text-headline-md text-on-surface font-code-block">{summary.total_output_tokens.toLocaleString()}</p>
              </div>
              <div className="p-4 rounded-lg bg-surface-container border border-border-subtle">
                <p className="font-label-sm text-label-sm text-on-surface-variant mb-1">Total Tokens</p>
                <p className="font-headline-md text-headline-md text-on-surface font-code-block">{summary.total_tokens.toLocaleString()}</p>
              </div>
            </div>

            {/* Time Period Filter */}
            <div className="flex items-center gap-2 mb-4">
              <span className="font-label-md text-label-md text-on-surface-variant">Period:</span>
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="px-3 py-1.5 rounded-lg bg-surface-container border border-outline text-on-surface font-body-md text-body-md focus:outline-none focus:border-primary transition-colors"
              >
                <option value={1}>Today</option>
                <option value={7}>7 Days</option>
                <option value={30}>30 Days</option>
                <option value={90}>90 Days</option>
              </select>
            </div>

            {/* Usage by Combo */}
            {comboUsage.length > 0 && (
              <div className="mb-8">
                <h2 className="font-headline-sm text-headline-sm text-on-surface mb-4">Usage by AI Combo</h2>
                <div className="rounded-lg border border-border-subtle overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-surface-container-high">
                      <tr>
                        <th className="px-4 py-3 text-left font-label-md text-label-md text-on-surface-variant">Combo</th>
                        <th className="px-4 py-3 text-right font-label-md text-label-md text-on-surface-variant">Requests</th>
                        <th className="px-4 py-3 text-right font-label-md text-label-md text-on-surface-variant">Input</th>
                        <th className="px-4 py-3 text-right font-label-md text-label-md text-on-surface-variant">Output</th>
                        <th className="px-4 py-3 text-right font-label-md text-label-md text-on-surface-variant">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comboUsage.map((combo) => (
                        <tr key={combo.combo_id} className="border-t border-border-subtle hover:bg-surface-container-low">
                          <td className="px-4 py-3 font-body-md text-body-md text-on-surface">{combo.combo_id}</td>
                          <td className="px-4 py-3 font-code-block text-code-block text-on-surface text-right">{combo.requests}</td>
                          <td className="px-4 py-3 font-code-block text-code-block text-on-surface text-right">{combo.input_tokens.toLocaleString()}</td>
                          <td className="px-4 py-3 font-code-block text-code-block text-on-surface text-right">{combo.output_tokens.toLocaleString()}</td>
                          <td className="px-4 py-3 font-code-block text-code-block text-secondary text-right font-semibold">{combo.total_tokens.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Request History */}
            {requests && requests.items.length > 0 && (
              <div>
                <h2 className="font-headline-sm text-headline-sm text-on-surface mb-4">Request History</h2>
                <div className="rounded-lg border border-border-subtle overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-surface-container-high">
                      <tr>
                        <th className="px-4 py-3 text-left font-label-md text-label-md text-on-surface-variant">Time</th>
                        <th className="px-4 py-3 text-left font-label-md text-label-md text-on-surface-variant">Combo</th>
                        <th className="px-4 py-3 text-right font-label-md text-label-md text-on-surface-variant">Input</th>
                        <th className="px-4 py-3 text-right font-label-md text-label-md text-on-surface-variant">Output</th>
                        <th className="px-4 py-3 text-right font-label-md text-label-md text-on-surface-variant">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {requests.items.map((req) => (
                        <tr key={req.id} className="border-t border-border-subtle hover:bg-surface-container-low">
                          <td className="px-4 py-3 font-body-sm text-body-sm text-on-surface-variant">
                            {new Date(req.created_at).toLocaleString()}
                          </td>
                          <td className="px-4 py-3 font-body-md text-body-md text-on-surface">{req.model}</td>
                          <td className="px-4 py-3 font-code-block text-code-block text-on-surface text-right">{req.input_tokens}</td>
                          <td className="px-4 py-3 font-code-block text-code-block text-on-surface text-right">{req.output_tokens}</td>
                          <td className="px-4 py-3 font-code-block text-code-block text-secondary text-right">{req.total_tokens}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Pagination */}
                {requests.pages > 1 && (
                  <div className="flex items-center justify-between mt-4">
                    <p className="font-body-sm text-body-sm text-on-surface-variant">
                      Page {requests.page} of {requests.pages} ({requests.total} total)
                    </p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-3 py-1 rounded-lg border border-outline text-on-surface bg-transparent hover:bg-surface-container-high disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-body-sm text-body-sm"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setPage(p => Math.min(requests.pages, p + 1))}
                        disabled={page === requests.pages}
                        className="px-3 py-1 rounded-lg border border-outline text-on-surface bg-transparent hover:bg-surface-container-high disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-body-sm text-body-sm"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </AppShell>
  )
}
