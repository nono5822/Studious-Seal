export interface DashboardResponse {
  user_profile: UserProfile
  live_status: LiveStatus
  classes: Class[]
  assignments: Assignment[]
  intervention_logs: InterventionLog[]
  knowledge_gaps: KnowledgeGap[]
}

export interface UserProfile {
  user_id: string
  name: string
  linked_platforms: string[]
}

export interface LiveStatus {
  overall_urgency_score: number
  is_gaming: boolean
  current_activity: string | null
  last_active_platform: string | null
  last_ping_timestamp: string | null
}

export interface Class {
  class_id: string
  name: string
  professor: string | null
  syllabus_parsed: boolean
}

export interface Assignment {
  assignment_id: string
  class_id: string
  title: string
  due_date: string
  priority_score: number | null
  status: string
  type: string | null
}

export interface InterventionLog {
  log_id: string
  timestamp: string
  platform: string
  trigger: string | null
  message_sent: string
  user_reply: string | null
}

export interface KnowledgeGap {
  gap_id: string
  class_id: string
  topic: string
  question_asked: string
  wrong_answer_given: string
  correct_concept: string
  study_reference: string
  youtube_link: string | null
  status: string | null
}

export function parseDueDate(dueDate: string): Date | null {
  const d = new Date(dueDate)
  return isNaN(d.getTime()) ? null : d
}

export function parseTimestamp(ts: string): Date | null {
  const d = new Date(ts)
  return isNaN(d.getTime()) ? null : d
}

export function formatDate(d: Date | null, fallback: string): string {
  if (!d) return fallback
  return d.toLocaleDateString(undefined, { dateStyle: 'medium' }) + ' ' + d.toLocaleTimeString(undefined, { timeStyle: 'short' })
}
