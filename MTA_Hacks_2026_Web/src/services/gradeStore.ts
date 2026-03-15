import type { GradeDisplayMode, GradeFolder, GradeClass, GradeComponent } from '../types/grades'
import { componentPercentage, weightedContribution } from '../types/grades'

const GRADE_DATA_KEY = 'sealsensei.gradeData'

interface PersistedGradeData {
  folders: GradeFolder[]
  classes: GradeClass[]
  components: GradeComponent[]
  display_mode: GradeDisplayMode
}

function uuid(): string {
  return crypto.randomUUID()
}

function load(): PersistedGradeData {
  try {
    const raw = localStorage.getItem(GRADE_DATA_KEY)
    if (!raw) return defaultData()
    const data = JSON.parse(raw) as PersistedGradeData
    return {
      folders: data.folders ?? [],
      classes: data.classes ?? [],
      components: data.components ?? [],
      display_mode: data.display_mode === 'points' ? 'points' : 'percentage',
    }
  } catch {
    return defaultData()
  }
}

function defaultData(): PersistedGradeData {
  return {
    folders: [],
    classes: [],
    components: [],
    display_mode: 'percentage',
  }
}

function save(data: PersistedGradeData) {
  try {
    localStorage.setItem(GRADE_DATA_KEY, JSON.stringify(data))
  } catch {}
}

export interface GradeStoreState {
  folders: GradeFolder[]
  classes: GradeClass[]
  components: GradeComponent[]
  displayMode: GradeDisplayMode
}

export function createGradeStore(): GradeStoreState {
  const data = load()
  return {
    folders: data.folders,
    classes: data.classes,
    components: data.components,
    displayMode: data.display_mode,
  }
}

function toPersisted(state: GradeStoreState): PersistedGradeData {
  return {
    folders: state.folders,
    classes: state.classes,
    components: state.components,
    display_mode: state.displayMode,
  }
}

export function addFolder(state: GradeStoreState): GradeStoreState {
  const name = prompt('Folder name')?.trim()
  if (!name) return state
  const next: GradeStoreState = {
    ...state,
    folders: [...state.folders, { id: uuid(), name, created_at: new Date().toISOString() }].sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })),
  }
  save(toPersisted(next))
  return next
}

export function deleteFolder(state: GradeStoreState, folder: GradeFolder): GradeStoreState {
  const classIds = new Set(state.classes.filter((c) => c.folder_id === folder.id).map((c) => c.id))
  const next: GradeStoreState = {
    ...state,
    folders: state.folders.filter((f) => f.id !== folder.id),
    classes: state.classes.filter((c) => c.folder_id !== folder.id),
    components: state.components.filter((c) => !classIds.has(c.class_id)),
  }
  save(toPersisted(next))
  return next
}

export function classesInFolder(state: GradeStoreState, folderId: string): GradeClass[] {
  return state.classes.filter((c) => c.folder_id === folderId).sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
}

export function unfiledClasses(state: GradeStoreState): GradeClass[] {
  return state.classes.filter((c) => c.folder_id == null).sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
}

export function addClass(state: GradeStoreState, name: string, folderId: string | null): GradeStoreState {
  const next: GradeStoreState = {
    ...state,
    classes: [...state.classes, { id: uuid(), name, folder_id: folderId, created_at: new Date().toISOString() }].sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })),
  }
  save(toPersisted(next))
  return next
}

export function deleteClass(state: GradeStoreState, gradeClass: GradeClass): GradeStoreState {
  const next: GradeStoreState = {
    ...state,
    classes: state.classes.filter((c) => c.id !== gradeClass.id),
    components: state.components.filter((c) => c.class_id !== gradeClass.id),
  }
  save(toPersisted(next))
  return next
}

export function moveClass(state: GradeStoreState, gradeClass: GradeClass, toFolderId: string | null): GradeStoreState {
  const next: GradeStoreState = {
    ...state,
    classes: state.classes.map((c) => (c.id === gradeClass.id ? { ...c, folder_id: toFolderId } : c)),
  }
  save(toPersisted(next))
  return next
}

export function componentsForClass(state: GradeStoreState, classId: string): GradeComponent[] {
  return state.components.filter((c) => c.class_id === classId).sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
}

export function overallPercentage(state: GradeStoreState, classId: string): number | null {
  const comps = componentsForClass(state, classId)
  if (comps.length === 0) return null
  const totalWeight = comps.reduce((s, c) => s + c.weight_percent, 0)
  if (totalWeight <= 0) return null
  const sum = comps.reduce((s, c) => s + weightedContribution(c), 0)
  return (sum / totalWeight) * 100
}

export function addComponent(state: GradeStoreState, classId: string, name: string, weightPercent: number, earnedPoints: number, maxPoints: number): GradeStoreState {
  const next: GradeStoreState = {
    ...state,
    components: [...state.components, { id: uuid(), class_id: classId, name, weight_percent: weightPercent, earned_points: earnedPoints, max_points: maxPoints }],
  }
  save(toPersisted(next))
  return next
}

export function updateComponent(state: GradeStoreState, component: GradeComponent): GradeStoreState {
  const next: GradeStoreState = {
    ...state,
    components: state.components.map((c) => (c.id === component.id ? component : c)),
  }
  save(toPersisted(next))
  return next
}

export function deleteComponent(state: GradeStoreState, component: GradeComponent): GradeStoreState {
  const next: GradeStoreState = {
    ...state,
    components: state.components.filter((c) => c.id !== component.id),
  }
  save(toPersisted(next))
  return next
}

export function setDisplayMode(state: GradeStoreState, mode: GradeDisplayMode): GradeStoreState {
  const next = { ...state, displayMode: mode }
  save(toPersisted(next))
  return next
}

export function formatGradeDisplay(store: GradeStoreState, pct: number): string {
  return store.displayMode === 'percentage' ? `${pct.toFixed(1)}%` : `${pct.toFixed(1)} / 100`
}

export function formatComponentDisplay(store: GradeStoreState, c: GradeComponent): string {
  const pct = componentPercentage(c)
  return store.displayMode === 'percentage' ? `${pct.toFixed(1)}%` : `${c.earned_points} / ${c.max_points}`
}
