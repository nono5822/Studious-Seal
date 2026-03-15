import type { DashboardResponse } from '../types/dashboard'

const DEFAULT_BASE_URL = 'http://localhost:5000/'
const BASE_URL_KEY = 'studiousseal.apiBaseURL'
const USERNAME_KEY = 'studiousseal.username'

export type APIError =
  | { kind: 'invalid_url' }
  | { kind: 'network'; message: string }
  | { kind: 'invalid_response' }
  | { kind: 'decoding'; message: string }
  | { kind: 'no_user' }
  | { kind: 'not_found'; username: string }

export function getErrorMessage(e: APIError): string {
  switch (e.kind) {
    case 'invalid_url': return 'Invalid server URL'
    case 'network': return `Network error: ${e.message}`
    case 'invalid_response': return 'Server returned an error'
    case 'decoding': return `Invalid data: ${e.message}`
    case 'no_user': return 'Select a user to load your dashboard'
    case 'not_found': return `No priority list found for ${e.username}`
  }
}

export interface ApiState {
  baseURLString: string
  username: string | null
  users: string[]
  dashboard: DashboardResponse | null
  isLoading: boolean
  error: APIError | null
}

function getStoredBaseURL(): string {
  try {
    const s = localStorage.getItem(BASE_URL_KEY)
    return s ?? DEFAULT_BASE_URL
  } catch {
    return DEFAULT_BASE_URL
  }
}

function getStoredUsername(): string | null {
  try {
    return localStorage.getItem(USERNAME_KEY)
  } catch {
    return null
  }
}

function setStoredBaseURL(url: string) {
  try {
    localStorage.setItem(BASE_URL_KEY, url)
  } catch {}
}

function setStoredUsername(name: string | null) {
  try {
    if (name == null) localStorage.removeItem(USERNAME_KEY)
    else localStorage.setItem(USERNAME_KEY, name)
  } catch {}
}

function baseURL(url: string): string {
  const trimmed = url.trim()
  return trimmed.endsWith('/') ? trimmed : trimmed + '/'
}

export function createApiState(): ApiState {
  return {
    baseURLString: getStoredBaseURL(),
    username: getStoredUsername(),
    users: [],
    dashboard: null,
    isLoading: false,
    error: null,
  }
}

export async function fetchUsers(state: ApiState): Promise<{ users: string[]; error: APIError | null }> {
  const base = baseURL(state.baseURLString)
  let url: URL
  try {
    url = new URL('api/users', base)
  } catch {
    return { users: [], error: { kind: 'invalid_url' } }
  }
  try {
    const res = await fetch(url.toString(), { signal: AbortSignal.timeout(15000) })
    if (!res.ok) return { users: [], error: { kind: 'invalid_response' } }
    const data = await res.json()
    if (!Array.isArray(data)) return { users: [], error: { kind: 'decoding', message: 'Expected array' } }
    return { users: data, error: null }
  } catch (e) {
    return { users: [], error: { kind: 'network', message: String(e) } }
  }
}

export async function fetchDashboard(state: ApiState): Promise<{ dashboard: DashboardResponse | null; error: APIError | null }> {
  const user = state.username?.trim()
  if (!user) return { dashboard: null, error: { kind: 'no_user' } }
  const base = baseURL(state.baseURLString)
  let url: URL
  try {
    url = new URL(`api/user/${encodeURIComponent(user)}/priority`, base)
  } catch {
    return { dashboard: null, error: { kind: 'invalid_url' } }
  }
  try {
    const res = await fetch(url.toString(), { signal: AbortSignal.timeout(15000) })
    if (res.status === 404) return { dashboard: null, error: { kind: 'not_found', username: user } }
    if (!res.ok) return { dashboard: null, error: { kind: 'invalid_response' } }
    const data = await res.json()
    return { dashboard: data as DashboardResponse, error: null }
  } catch (e) {
    return { dashboard: null, error: { kind: 'network', message: String(e) } }
  }
}

export function setBaseURL(url: string): string {
  const trimmed = url.trim()
  setStoredBaseURL(trimmed || DEFAULT_BASE_URL)
  return trimmed || DEFAULT_BASE_URL
}

export function setUsername(name: string | null): string | null {
  const value = name?.trim()
  const next = value === '' ? null : (value ?? null)
  setStoredUsername(next)
  return next
}

export function loadMockDashboard(): DashboardResponse {
  return {
    user_profile: {
      user_id: 'student_101',
      name: 'Alex',
      linked_platforms: ['discord', 'telegram', 'whatsapp'],
    },
    live_status: {
      overall_urgency_score: 8.5,
      is_gaming: true,
      current_activity: 'League of Legends',
      last_active_platform: 'discord',
      last_ping_timestamp: '2026-03-14T12:05:00Z',
    },
    classes: [
      { class_id: 'IFT-1010', name: 'Programming I', professor: 'Dr. Turing', syllabus_parsed: true },
      { class_id: 'BIOL-101', name: 'Intro to Biology', professor: 'Dr. Watson', syllabus_parsed: true },
      { class_id: 'MATH-201', name: 'Linear Algebra', professor: 'Prof. Gauss', syllabus_parsed: true },
    ],
    assignments: [
      { assignment_id: 'task_001', class_id: 'IFT-1010', title: 'Binary Tree Implementation', due_date: '2026-03-16T23:59:00Z', priority_score: 9, status: 'pending', type: 'project' },
      { assignment_id: 'task_002', class_id: 'IFT-1010', title: 'Weekly Quiz 5', due_date: '2026-03-18T23:59:00Z', priority_score: 5, status: 'pending', type: 'quiz' },
      { assignment_id: 'task_003', class_id: 'IFT-1010', title: 'Recursion Exercises', due_date: '2026-03-20T23:59:00Z', priority_score: 6, status: 'pending', type: 'homework' },
      { assignment_id: 'task_004', class_id: 'BIOL-101', title: 'Lab Report 2 – Mitosis', due_date: '2026-03-19T23:59:00Z', priority_score: 7, status: 'pending', type: 'lab' },
      { assignment_id: 'task_005', class_id: 'BIOL-101', title: 'Midterm Exam', due_date: '2026-03-25T09:00:00Z', priority_score: 10, status: 'pending', type: 'exam' },
      { assignment_id: 'task_006', class_id: 'MATH-201', title: 'Problem Set 4', due_date: '2026-03-22T23:59:00Z', priority_score: 6, status: 'pending', type: 'homework' },
      { assignment_id: 'task_007', class_id: 'MATH-201', title: 'Eigenvalues Quiz', due_date: '2026-03-21T23:59:00Z', priority_score: 5, status: 'pending', type: 'quiz' },
    ],
    intervention_logs: [
      { log_id: 'log_089', timestamp: '2026-03-14T12:00:00Z', platform: 'discord', trigger: 'gaming_detected', message_sent: "Hey Alex! I see you're in the Rift. Your IFT-1010 project is due in 2 days. Urgency is at a 9/10. Log off and study!", user_reply: 'Logging off now, promise.' },
      { log_id: 'log_088', timestamp: '2026-03-13T20:30:00Z', platform: 'telegram', trigger: 'reminder', message_sent: 'Quick reminder: Quiz 5 for Programming I is in 5 days. Have you reviewed the recursion chapter?', user_reply: "I'll do it tonight." },
      { log_id: 'log_087', timestamp: '2026-03-13T14:00:00Z', platform: 'discord', trigger: 'study_check', message_sent: "You've been focused for 2 hours — great job! Take a short break and then consider tackling the Binary Tree project.", user_reply: null },
    ],
    knowledge_gaps: [
      { gap_id: 'gap_001', class_id: 'BIOL-101', topic: 'Cellular Respiration', question_asked: 'Where does the Krebs cycle occur?', wrong_answer_given: 'Nucleus', correct_concept: 'The Krebs cycle occurs in the mitochondrial matrix.', study_reference: 'Syllabus.pdf - Page 14', youtube_link: 'https://youtube.com/results?search_query=Krebs+cycle+explained', status: 'needs_review' },
      { gap_id: 'gap_002', class_id: 'IFT-1010', topic: 'Recursion', question_asked: 'What is the base case in a recursive function?', wrong_answer_given: 'The first line of the function', correct_concept: 'The base case is the condition that stops the recursion and returns without making another recursive call.', study_reference: 'Lecture 6 slides - Slide 12', youtube_link: 'https://youtube.com/results?search_query=recursion+base+case', status: 'reviewed' },
      { gap_id: 'gap_003', class_id: 'MATH-201', topic: 'Eigenvalues', question_asked: 'What does it mean for λ to be an eigenvalue of matrix A?', wrong_answer_given: 'A − λ is invertible', correct_concept: 'λ is an eigenvalue of A if there exists a nonzero vector v such that Av = λv; equivalently, det(A − λI) = 0.', study_reference: 'Textbook Ch. 5 - Section 5.1', youtube_link: 'https://youtube.com/results?search_query=eigenvalues+linear+algebra', status: 'needs_review' },
    ],
  }
}
