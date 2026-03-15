import { useState } from 'react'
import type { ApiState } from '../services/api'
import { fetchDashboard, loadMockDashboard } from '../services/api'
import type { KnowledgeGap } from '../types/dashboard'
import { UserPicker } from '../components/UserPicker'

interface StudyVaultProps {
  api: ApiState
  setApi: (patch: Partial<ApiState>) => void
}

function KnowledgeGapRow({ gap, onSelect }: { gap: KnowledgeGap; onSelect: () => void }) {
  return (
    <button type="button" className="card gap-row" onClick={onSelect}>
      <div className="title">{gap.topic}</div>
      <div className="sub line-clamp-2">{gap.question_asked}</div>
      {gap.status && <span className="status-badge">{gap.status}</span>}
    </button>
  )
}

export function KnowledgeGapDetail({ gap, onBack }: { gap: KnowledgeGap; onBack: () => void }) {
  return (
    <div className="tab-content">
      <header className="tab-header">
        <button type="button" className="btn-back" onClick={onBack}>← Back</button>
        <h1>Knowledge Gap</h1>
      </header>
      <div className="scroll">
        <div className="gap-detail">
          <h2>{gap.topic}</h2>
          <div className="block">
            <label>Question</label>
            <p>{gap.question_asked}</p>
          </div>
          <div className="block wrong">
            <label>Your answer</label>
            <p>{gap.wrong_answer_given}</p>
          </div>
          <div className="block correct">
            <label>Correct concept</label>
            <p>{gap.correct_concept}</p>
          </div>
          <div className="block ref">
            <label>Study reference</label>
            <p>{gap.study_reference}</p>
          </div>
          {gap.youtube_link && (
            <a href={gap.youtube_link} target="_blank" rel="noopener noreferrer" className="btn-youtube">
              ▶ Watch on YouTube
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

export function StudyVault({ api, setApi }: StudyVaultProps) {
  const [showUserPicker, setShowUserPicker] = useState(false)
  const [selectedGap, setSelectedGap] = useState<KnowledgeGap | null>(null)

  const gaps = api.dashboard?.knowledge_gaps ?? []

  if (selectedGap) {
    return (
      <KnowledgeGapDetail gap={selectedGap} onBack={() => setSelectedGap(null)} />
    )
  }

  if (api.isLoading) {
    return (
      <div className="tab-content">
        <header className="tab-header">
          <h1>Study Vault</h1>
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
          <h1>Study Vault</h1>
          <button type="button" className="icon-btn" onClick={() => setShowUserPicker(true)}>👤</button>
        </header>
        <div className="empty-state">
          <p>No data</p>
          <p className="sub">{api.username == null ? 'Select a user to load data.' : 'Knowledge gaps will appear here.'}</p>
        </div>
        {showUserPicker && <UserPicker api={api} setApi={setApi} onClose={() => setShowUserPicker(false)} />}
      </div>
    )
  }

  return (
    <div className="tab-content">
      <header className="tab-header">
        <h1>Study Vault</h1>
        <div className="toolbar">
          <button type="button" className="btn-text" onClick={async () => {
            setApi({ isLoading: true })
            const { dashboard, error } = await fetchDashboard(api)
            setApi({ dashboard, error, isLoading: false })
          }}>Refresh</button>
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
        <div className="gap-list">
          {gaps.map((gap) => (
            <KnowledgeGapRow key={gap.gap_id} gap={gap} onSelect={() => setSelectedGap(gap)} />
          ))}
        </div>
      </div>
      {showUserPicker && <UserPicker api={api} setApi={setApi} onClose={() => setShowUserPicker(false)} />}
    </div>
  )
}
