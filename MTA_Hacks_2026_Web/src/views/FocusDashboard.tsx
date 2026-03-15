import { useState } from 'react'
import type { ApiState } from '../services/api'
import { getErrorMessage, fetchDashboard, loadMockDashboard } from '../services/api'
import type { LiveStatus, Assignment } from '../types/dashboard'
import { parseDueDate, formatDate } from '../types/dashboard'
import { UserPicker } from '../components/UserPicker'

interface FocusDashboardProps {
  api: ApiState
  setApi: (patch: Partial<ApiState>) => void
}

function LiveStatusCard({ status }: { status: LiveStatus }) {
  return (
    <div className="card live-status-card">
      <span className={`icon ${status.is_gaming ? 'warn' : 'ok'}`}>
        {status.is_gaming ? '⚠' : '✓'}
      </span>
      <div>
        <div className="title">{status.is_gaming ? 'Gaming detected' : 'Focus mode'}</div>
        {status.is_gaming && status.current_activity && status.current_activity.toLowerCase() !== 'none' && (
          <div className="sub">{status.current_activity}</div>
        )}
      </div>
    </div>
  )
}

function AssignmentRow({ assignment }: { assignment: Assignment }) {
  const due = parseDueDate(assignment.due_date)
  return (
    <div className="card assignment-row">
      <div>
        <div className="title">{assignment.title}</div>
        <div className="sub">{formatDate(due, assignment.due_date)}</div>
      </div>
      {assignment.priority_score != null && (
        <span className="badge">P{assignment.priority_score}</span>
      )}
    </div>
  )
}

export function FocusDashboard({ api, setApi }: FocusDashboardProps) {
  const [showUserPicker, setShowUserPicker] = useState(false)

  const status = api.dashboard?.live_status ?? null
  const assignments = (api.dashboard?.assignments ?? [])
    .slice()
    .sort((a, b) => {
      const da = parseDueDate(a.due_date)?.getTime() ?? Infinity
      const db = parseDueDate(b.due_date)?.getTime() ?? Infinity
      return da - db
    })

  const handleRefresh = async () => {
    setApi({ isLoading: true, error: null })
    const { dashboard, error } = await fetchDashboard(api)
    setApi({ dashboard, error, isLoading: false })
  }

  if (api.isLoading) {
    return (
      <div className="tab-content">
        <header className="tab-header">
          <h1>Focus</h1>
          <button type="button" className="icon-btn" onClick={() => setShowUserPicker(true)} title="Server & user">👤</button>
        </header>
        <div className="empty-state">
          <p>Loading…</p>
        </div>
      </div>
    )
  }

  if (api.error) {
    return (
      <div className="tab-content">
        <header className="tab-header">
          <h1>Focus</h1>
          <button type="button" className="icon-btn" onClick={() => setShowUserPicker(true)}>👤</button>
        </header>
        <div className="empty-state">
          <p className="error">Couldn't load dashboard</p>
          <p className="sub">{getErrorMessage(api.error)}</p>
          <button type="button" className="btn-primary" onClick={() => setShowUserPicker(true)}>Server & user settings</button>
        </div>
      </div>
    )
  }

  if (!api.dashboard) {
    return (
      <div className="tab-content">
        <header className="tab-header">
          <h1>Focus</h1>
          <button type="button" className="icon-btn" onClick={() => setShowUserPicker(true)}>👤</button>
        </header>
        <div className="empty-state">
          <p>No data</p>
          <p className="sub">{api.username == null ? 'Select a user or use mock data.' : 'Pull to refresh or load mock data.'}</p>
          <button type="button" className="btn-primary" onClick={() => setShowUserPicker(true)}>
            {api.username == null ? 'Select user' : 'Server & user settings'}
          </button>
        </div>
        {showUserPicker && <UserPicker api={api} setApi={setApi} onClose={() => setShowUserPicker(false)} />}
      </div>
    )
  }

  return (
    <div className="tab-content">
      <header className="tab-header">
        <h1>Focus</h1>
        <div className="toolbar">
          <button type="button" className="btn-text" onClick={handleRefresh}>Refresh</button>
          <button type="button" className="icon-btn" onClick={() => setShowUserPicker(true)} title="Server & user">👤</button>
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
        <div className="focus-content">
          {status && (
            <>
              <div className="urgency-value-only">
                <span className={`urgency-number ${status.overall_urgency_score >= 8 ? 'high' : ''}`}>
                  {Math.min(10, Math.max(0, status.overall_urgency_score)).toFixed(1)}
                </span>
                <span className="urgency-label">Urgency</span>
              </div>
              <LiveStatusCard status={status} />
              <h2 className="section-title">Upcoming Assignments</h2>
              {assignments.map((a) => (
                <AssignmentRow key={a.assignment_id} assignment={a} />
              ))}
            </>
          )}
        </div>
      </div>
      {showUserPicker && <UserPicker api={api} setApi={setApi} onClose={() => setShowUserPicker(false)} />}
    </div>
  )
}
