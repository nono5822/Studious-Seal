import { useState, useEffect } from 'react'
import { createApiState } from './services/api'
import { fetchDashboard, loadMockDashboard } from './services/api'
import { createGradeStore } from './services/gradeStore'
import { FocusDashboard } from './views/FocusDashboard'
import { InterventionFeed } from './views/InterventionFeed'
import { StudyVault } from './views/StudyVault'
import { GradeCalculatorTab, GradeDisplayModeBar } from './views/GradeCalculator'
import type { ApiState } from './services/api'
import type { GradeStoreState } from './services/gradeStore'

type TabId = 'focus' | 'interventions' | 'vault' | 'grades'

export default function App() {
  const [api, setApiState] = useState<ApiState>(createApiState)
  const [store, setStore] = useState<GradeStoreState>(createGradeStore)
  const [tab, setTab] = useState<TabId>('focus')

  const setApi = (patch: Partial<ApiState>) => setApiState((prev) => ({ ...prev, ...patch }))

  useEffect(() => {
    setApi({ dashboard: loadMockDashboard(), error: null })
  }, [])

  useEffect(() => {
    if (api.username) {
      fetchDashboard(api).then(({ dashboard, error }) => setApi({ dashboard: dashboard ?? null, error }))
    }
  }, [api.username])

  return (
    <div className="app">
      <main className={`main ${tab === 'grades' ? 'main-with-grades-bar' : ''}`}>
        {tab === 'focus' && <FocusDashboard api={api} setApi={setApi} />}
        {tab === 'interventions' && <InterventionFeed api={api} setApi={setApi} />}
        {tab === 'vault' && <StudyVault api={api} setApi={setApi} />}
        {tab === 'grades' && (
          <GradeCalculatorTab api={api} setApi={setApi} store={store} setStore={setStore} />
        )}
      </main>
      {tab === 'grades' && (
        <div className="grades-display-mode-bar">
          <GradeDisplayModeBar store={store} setStore={setStore} />
        </div>
      )}
      <nav className="tab-bar">
        <button type="button" className={tab === 'focus' ? 'active' : ''} onClick={() => setTab('focus')} title="Focus">
          <span className="tab-icon">📊</span>
          <span>Focus</span>
        </button>
        <button type="button" className={tab === 'interventions' ? 'active' : ''} onClick={() => setTab('interventions')} title="Interventions">
          <span className="tab-icon">💬</span>
          <span>Interventions</span>
        </button>
        <button type="button" className={tab === 'vault' ? 'active' : ''} onClick={() => setTab('vault')} title="Study Vault">
          <span className="tab-icon">📚</span>
          <span>Study Vault</span>
        </button>
        <button type="button" className={tab === 'grades' ? 'active' : ''} onClick={() => setTab('grades')} title="Grades">
          <span className="tab-icon">%</span>
          <span>Grades</span>
        </button>
      </nav>
    </div>
  )
}
