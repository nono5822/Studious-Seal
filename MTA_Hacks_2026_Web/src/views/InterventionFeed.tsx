import { useState } from 'react'
import type { ApiState } from '../services/api'
import { loadMockDashboard } from '../services/api'
import type { InterventionLog } from '../types/dashboard'
import { parseTimestamp, formatDate } from '../types/dashboard'
import { UserPicker } from '../components/UserPicker'

interface InterventionFeedProps {
  api: ApiState
  setApi: (patch: Partial<ApiState>) => void
}

function platformIcon(platform: string): string {
  switch (platform.toLowerCase()) {
    case 'discord': return '💬'
    case 'telegram': return '✈'
    case 'whatsapp': return '💭'
    default: return '💬'
  }
}

function platformColor(platform: string): string {
  switch (platform.toLowerCase()) {
    case 'discord': return '#6688dd'
    case 'telegram': return '#3399dd'
    case 'whatsapp': return '#25d366'
    default: return '#3399dd'
  }
}

function InterventionLogRow({ log }: { log: InterventionLog }) {
  const ts = parseTimestamp(log.timestamp)
  const color = platformColor(log.platform)
  return (
    <div className="card intervention-row">
      <span className="platform-icon" style={{ color }}>{platformIcon(log.platform)}</span>
      <div className="intervention-body">
        <div className="meta">
          <span className="time">{formatDate(ts, log.timestamp)}</span>
          <span className="platform-badge" style={{ backgroundColor: color + '33', color }}>{log.platform}</span>
        </div>
        <p className="message">{log.message_sent}</p>
        {log.user_reply && <p className="reply">You: {log.user_reply}</p>}
      </div>
    </div>
  )
}

export function InterventionFeed({ api, setApi }: InterventionFeedProps) {
  const [showUserPicker, setShowUserPicker] = useState(false)

  const logs = (api.dashboard?.intervention_logs ?? [])
    .slice()
    .sort((a, b) => {
      const ta = parseTimestamp(a.timestamp)?.getTime() ?? 0
      const tb = parseTimestamp(b.timestamp)?.getTime() ?? 0
      return tb - ta
    })

  if (api.isLoading) {
    return (
      <div className="tab-content">
        <header className="tab-header">
          <h1>Interventions</h1>
          <button type="button" className="icon-btn" onClick={() => setShowUserPicker(true)}>👤</button>
        </header>
        <div className="empty-state"><p>Loading…</p></div>
      </div>
    )
  }

  if (!api.dashboard && !api.error) {
    return (
      <div className="tab-content">
        <header className="tab-header">
          <h1>Interventions</h1>
          <button type="button" className="icon-btn" onClick={() => setShowUserPicker(true)}>👤</button>
        </header>
        <div className="empty-state">
          <p>No data</p>
          <p className="sub">{api.username == null ? 'Select a user in Focus to load data.' : 'Interventions will appear here.'}</p>
        </div>
        {showUserPicker && <UserPicker api={api} setApi={setApi} onClose={() => setShowUserPicker(false)} />}
      </div>
    )
  }

  return (
    <div className="tab-content">
      <header className="tab-header">
        <h1>Interventions</h1>
        <div className="toolbar">
          <button type="button" className="icon-btn" onClick={() => setShowUserPicker(true)}>👤</button>
          <div className="dropdown">
            <button type="button" className="icon-btn">⋮</button>
            <div className="dropdown-menu">
              <button type="button" onClick={() => setShowUserPicker(true)}>Server & user</button>
              <button type="button" onClick={() => setApi({ dashboard: loadMockDashboard(), error: null })}>Mock data</button>
            </div>
          </div>
        </div>
      </header>
      <div className="scroll">
        <div className="intervention-list">
          {logs.map((log) => (
            <InterventionLogRow key={log.log_id} log={log} />
          ))}
        </div>
      </div>
      {showUserPicker && <UserPicker api={api} setApi={setApi} onClose={() => setShowUserPicker(false)} />}
    </div>
  )
}
