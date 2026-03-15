export type GradeDisplayMode = 'points' | 'percentage'

export interface GradeFolder {
  id: string
  name: string
  created_at: string
}

export interface GradeClass {
  id: string
  name: string
  folder_id: string | null
  created_at: string
}

export interface GradeComponent {
  id: string
  class_id: string
  name: string
  weight_percent: number
  earned_points: number
  max_points: number
}

export function componentPercentage(c: GradeComponent): number {
  return c.max_points > 0 ? (c.earned_points / c.max_points) * 100 : 0
}

export function weightedContribution(c: GradeComponent): number {
  return (componentPercentage(c) / 100) * c.weight_percent
}
