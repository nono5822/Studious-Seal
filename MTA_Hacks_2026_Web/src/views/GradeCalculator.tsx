import { useState } from 'react'
import type { ApiState } from '../services/api'
import { loadMockDashboard } from '../services/api'
import type { GradeFolder, GradeClass, GradeComponent } from '../types/grades'
import type { GradeStoreState } from '../services/gradeStore'
import {
  addFolder,
  deleteFolder,
  addClass,
  deleteClass,
  classesInFolder,
  unfiledClasses,
  componentsForClass,
  overallPercentage,
  addComponent,
  updateComponent,
  deleteComponent,
  setDisplayMode,
  formatGradeDisplay,
  formatComponentDisplay,
} from '../services/gradeStore'
import { UserPicker } from '../components/UserPicker'

interface GradeCalculatorProps {
  api: ApiState
  setApi: (patch: Partial<ApiState>) => void
  store: GradeStoreState
  setStore: (next: GradeStoreState) => void
}

export function GradeDisplayModeBar({ store, setStore }: { store: GradeStoreState; setStore: (s: GradeStoreState) => void }) {
  return (
    <div className="display-mode-bar">
      <button
        type="button"
        className={store.displayMode === 'percentage' ? 'active' : ''}
        onClick={() => setStore(setDisplayMode(store, 'percentage'))}
      >
        Percentage
      </button>
      <button
        type="button"
        className={store.displayMode === 'points' ? 'active' : ''}
        onClick={() => setStore(setDisplayMode(store, 'points'))}
      >
        Points
      </button>
    </div>
  )
}

function GradeClassRow({
  store,
  gradeClass,
  onSelect,
}: {
  store: GradeStoreState
  gradeClass: GradeClass
  onSelect: () => void
}) {
  const pct = overallPercentage(store, gradeClass.id)
  return (
    <button type="button" className="list-row" onClick={onSelect}>
      <span>{gradeClass.name}</span>
      {pct != null && (
        <span className="secondary">{formatGradeDisplay(store, pct)}</span>
      )}
    </button>
  )
}

// --- Folder list (main Grades tab)
export function GradeCalculatorTab({ api, setApi, store, setStore }: GradeCalculatorProps) {
  const [showUserPicker, setShowUserPicker] = useState(false)
  const [nav, setNav] = useState<'list' | 'folder' | 'class'>('list')
  const [selectedFolder, setSelectedFolder] = useState<GradeFolder | null>(null)
  const [selectedClass, setSelectedClass] = useState<GradeClass | null>(null)

  const unfiled = unfiledClasses(store)

  const handleAddFolder = () => {
    const next = addFolder(store)
    if (next !== store) setStore(next)
  }

  const handleAddUnfiledClass = () => {
    const name = prompt('Class name')
    if (!name?.trim()) return
    setStore(addClass(store, name.trim(), null))
  }

  const handleDeleteFolder = (f: GradeFolder) => {
    if (confirm(`Delete folder "${f.name}" and its classes?`)) setStore(deleteFolder(store, f))
  }

  const handleDeleteUnfiledClass = (c: GradeClass) => {
    if (confirm(`Delete class "${c.name}"?`)) setStore(deleteClass(store, c))
  }

  if (nav === 'folder' && selectedFolder) {
    return (
      <FolderDetailView
        folder={selectedFolder}
        store={store}
        setStore={setStore}
        onBack={() => { setNav('list'); setSelectedFolder(null) }}
        onSelectClass={(c) => { setSelectedClass(c); setNav('class') }}
      />
    )
  }

  if (nav === 'class' && selectedClass) {
    return (
      <ClassGradeView
        gradeClass={selectedClass}
        store={store}
        setStore={setStore}
        onBack={() => { setNav('list'); setSelectedClass(null) }}
      />
    )
  }

  return (
    <div className="tab-content">
      <header className="tab-header">
        <h1>Grades</h1>
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
        <section className="section">
          <h2>Folders</h2>
          {store.folders.map((f) => (
            <div key={f.id} className="list-row-wrap">
              <button type="button" className="list-row" onClick={() => { setSelectedFolder(f); setNav('folder') }}>
                <span>📁 {f.name}</span>
              </button>
              <button type="button" className="btn-icon danger" onClick={() => handleDeleteFolder(f)} title="Delete folder">×</button>
            </div>
          ))}
          <button type="button" className="btn-text add" onClick={handleAddFolder}>+ New folder</button>
        </section>
        <section className="section">
          <h2>Unfiled classes</h2>
          {unfiled.map((c) => (
            <div key={c.id} className="list-row-wrap">
              <button type="button" className="list-row" onClick={() => { setSelectedClass(c); setNav('class') }}>
                <span>{c.name}</span>
                {overallPercentage(store, c.id) != null && (
                  <span className="secondary">{formatGradeDisplay(store, overallPercentage(store, c.id)!)}</span>
                )}
              </button>
              <button type="button" className="btn-icon danger" onClick={() => handleDeleteUnfiledClass(c)}>×</button>
            </div>
          ))}
          <button type="button" className="btn-text add" onClick={handleAddUnfiledClass}>+ Add class (no folder)</button>
        </section>
      </div>
      {showUserPicker && <UserPicker api={api} setApi={setApi} onClose={() => setShowUserPicker(false)} />}
    </div>
  )
}

// --- Folder detail: classes in folder
function FolderDetailView({
  folder,
  store,
  setStore,
  onBack,
  onSelectClass,
}: {
  folder: GradeFolder
  store: GradeStoreState
  setStore: (s: GradeStoreState) => void
  onBack: () => void
  onSelectClass: (c: GradeClass) => void
}) {
  const [newName, setNewName] = useState('')
  const folderClasses = classesInFolder(store, folder.id)

  const handleAddClass = () => {
    const name = newName.trim() || prompt('Class name')
    if (!name?.trim()) return
    setStore(addClass(store, name.trim(), folder.id))
    setNewName('')
  }

  return (
    <div className="tab-content">
      <header className="tab-header">
        <button type="button" className="btn-back" onClick={onBack}>← Back</button>
        <h1>{folder.name}</h1>
      </header>
      <div className="scroll">
        <div className="section">
          <h2>Classes</h2>
          {folderClasses.map((c) => (
            <div key={c.id} className="list-row-wrap">
              <GradeClassRow
                store={store}
                gradeClass={c}
                onSelect={() => onSelectClass(c)}
              />
              <button type="button" className="btn-icon danger" onClick={(e) => { e.stopPropagation(); if (confirm(`Delete "${c.name}"?`)) setStore(deleteClass(store, c)) }} title="Delete class">×</button>
            </div>
          ))}
          <div className="add-inline">
            <input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Class name" onKeyDown={(e) => e.key === 'Enter' && handleAddClass()} />
            <button type="button" className="btn-primary" onClick={handleAddClass}>Add class</button>
          </div>
        </div>
      </div>
    </div>
  )
}

function colorForGrade(pct: number): string {
  if (pct >= 90) return 'var(--grade-a)'
  if (pct >= 80) return 'var(--grade-b)'
  if (pct >= 70) return 'var(--grade-c)'
  return 'var(--grade-d)'
}

// --- Class detail: grade components
function ClassGradeView({
  gradeClass,
  store,
  setStore,
  onBack,
}: {
  gradeClass: GradeClass
  store: GradeStoreState
  setStore: (s: GradeStoreState) => void
  onBack: () => void
}) {
  const [editing, setEditing] = useState<GradeComponent | null>(null)
  const [showNew, setShowNew] = useState(false)
  const [name, setName] = useState('')
  const [weight, setWeight] = useState('')
  const [earned, setEarned] = useState('')
  const [max, setMax] = useState('')

  const comps = componentsForClass(store, gradeClass.id)
  const overall = overallPercentage(store, gradeClass.id)

  const openEdit = (c: GradeComponent) => {
    setEditing(c)
    setName(c.name)
    setWeight(String(c.weight_percent))
    setEarned(String(c.earned_points))
    setMax(String(c.max_points))
  }

  const closeForm = () => {
    setEditing(null)
    setShowNew(false)
    setName('')
    setWeight('')
    setEarned('')
    setMax('')
  }

  const saveComponent = () => {
    const n = name.trim()
    const w = parseFloat(weight)
    const e = parseFloat(earned)
    const m = parseFloat(max)
    if (!n || isNaN(w) || w < 0 || w > 100 || isNaN(e) || e < 0 || isNaN(m) || m <= 0) return
    if (editing) {
      setStore(updateComponent(store, { ...editing, name: n, weight_percent: w, earned_points: e, max_points: m }))
    } else {
      setStore(addComponent(store, gradeClass.id, n, w, e, m))
    }
    closeForm()
  }

  return (
    <div className="tab-content">
      <header className="tab-header">
        <button type="button" className="btn-back" onClick={onBack}>← Back</button>
        <h1>{gradeClass.name}</h1>
      </header>
      <div className="scroll">
        {overall != null && (
          <div className="card overall-row" style={{ color: colorForGrade(overall) }}>
            <span>Overall</span>
            <strong>{formatGradeDisplay(store, overall)}</strong>
          </div>
        )}
        <section className="section">
          <h2>Graded items</h2>
          {comps.map((c) => (
            <div key={c.id} className="list-row-wrap">
              <button type="button" className="list-row" onClick={() => openEdit(c)}>
                <div>
                  <div className="title">{c.name}</div>
                  <div className="sub">{c.weight_percent}% weight</div>
                </div>
                <span className="secondary">{formatComponentDisplay(store, c)}</span>
              </button>
              <button type="button" className="btn-icon danger" onClick={() => setStore(deleteComponent(store, c))}>×</button>
            </div>
          ))}
          <button type="button" className="btn-text add" onClick={() => { setShowNew(true); setEditing(null); setName(''); setWeight(''); setEarned(''); setMax(''); }}>
            + Add graded item
          </button>
        </section>
        {(showNew || editing) && (
          <div className="modal-overlay" onClick={closeForm}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h3>{editing ? 'Edit item' : 'New graded item'}</h3>
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
              <input type="number" value={weight} onChange={(e) => setWeight(e.target.value)} placeholder="Weight %" />
              <input type="number" value={earned} onChange={(e) => setEarned(e.target.value)} placeholder="Earned" />
              <input type="number" value={max} onChange={(e) => setMax(e.target.value)} placeholder="Max" />
              <p className="hint">Weight is % of final grade. Enter earned and max points.</p>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={closeForm}>Cancel</button>
                <button type="button" className="btn-primary" onClick={saveComponent}>{editing ? 'Save' : 'Add'}</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}