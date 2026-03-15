import { useState, useEffect } from 'react'

interface UrgencyMeterProps {
  score: number
}

export function UrgencyMeter({ score }: UrgencyMeterProps) {
  const [pulsing, setPulsing] = useState(false)
  const normalized = Math.min(10, Math.max(0, score))
  const isHigh = normalized >= 8

  useEffect(() => {
    if (!isHigh) return
    const id = setInterval(() => setPulsing((p) => !p), 800)
    return () => clearInterval(id)
  }, [isHigh])

  const halfCircleLength = Math.PI * 70
  const filledLength = (normalized / 10) * halfCircleLength

  return (
    <div className="urgency-meter">
      <div className="urgency-dial">
        <svg viewBox="0 0 160 100" className="urgency-svg">
          <path
            d="M 80 90 A 70 70 0 0 1 150 50"
            fill="none"
            stroke="var(--pastel-blue)"
            strokeWidth="20"
            opacity={0.4}
          />
          <path
            d="M 80 90 A 70 70 0 0 1 150 50"
            fill="none"
            stroke={isHigh ? '#c00' : 'var(--dark-blue)'}
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray={`${filledLength} ${halfCircleLength}`}
            opacity={isHigh && pulsing ? 0.85 : 1}
          />
        </svg>
        <span className={`urgency-value ${isHigh ? 'high' : ''}`}>{normalized.toFixed(1)}</span>
      </div>
      <div className="urgency-label">Urgency</div>
    </div>
  )
}
