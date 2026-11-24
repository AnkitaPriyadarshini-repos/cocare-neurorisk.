import { useState } from 'react'
import ScoreBandBadge from './ScoreBandBadge'
import { t } from '../../i18n'

export default function AssessmentCompare({ history = [], lang = 'or' }) {
  if (!history || history.length < 2) return null

  // By default, compare earliest (baseline) with newest
  const [baseId, setBaseId] = useState(history[history.length - 1]?.id)
  const [recentId, setRecentId] = useState(history[0]?.id)
  const [isOpen, setIsOpen] = useState(true)

  const baseline = history.find((h) => h.id === baseId) || history[history.length - 1]
  const recent = history.find((h) => h.id === recentId) || history[0]

  const baseScore = typeof baseline?.score === 'number' ? baseline.score : parseFloat(baseline?.score || 0)
  const recentScore = typeof recent?.score === 'number' ? recent.score : parseFloat(recent?.score || 0)

  const delta = recentScore - baseScore
  const deltaFormatted = (delta >= 0 ? `+` : ``) + delta.toFixed(3)

  let trajectory = 'stable'
  let trajectoryColor = '#1b5e20'
  let trajectoryBg = '#e8f5e9'
  let trajectoryText = t('status_stable', lang)

  if (delta <= -0.02) {
    trajectory = 'improving'
    trajectoryColor = '#1b5e20'
    trajectoryBg = '#e8f5e9'
    trajectoryText = t('status_improving', lang)
  } else if (delta >= 0.02) {
    trajectory = 'elevated'
    trajectoryColor = '#8c3109'
    trajectoryBg = '#fff3e0'
    trajectoryText = t('status_elevated', lang)
  }

  return (
    <div
      className="assessment-compare"
      style={{
        background: 'var(--card)',
        border: '2px solid var(--line)',
        borderRadius: '16px',
        padding: '1.25rem',
        marginBottom: '1.5rem',
        boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🔄</span> {t('comparison_title', lang)}
        </h2>
        <button
          type="button"
          className="small link"
          onClick={() => setIsOpen(!isOpen)}
          style={{ fontSize: '0.9rem', color: 'var(--muted)' }}
        >
          {isOpen ? '▲ Hide' : '▼ Show'}
        </button>
      </div>

      {isOpen && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Selectors for comparison pair */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.9rem' }}>
            <div style={{ flex: '1 1 180px' }}>
              <label htmlFor="select-baseline" style={{ display: 'block', fontWeight: '700', marginBottom: '0.25rem' }}>
                📌 {t('baseline', lang)}:
              </label>
              <select
                id="select-baseline"
                value={baseId}
                onChange={(e) => setBaseId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  borderRadius: '8px',
                  border: '1px solid var(--line)',
                  fontSize: '0.92rem',
                }}
              >
                {history.map((h) => (
                  <option key={h.id} value={h.id}>
                    {h.date?.slice(0, 10)} ({typeof h.score === 'number' ? h.score.toFixed(3) : h.score})
                  </option>
                ))}
              </select>
            </div>

            <div style={{ flex: '1 1 180px' }}>
              <label htmlFor="select-recent" style={{ display: 'block', fontWeight: '700', marginBottom: '0.25rem' }}>
                ⏱️ {t('latest', lang)}:
              </label>
              <select
                id="select-recent"
                value={recentId}
                onChange={(e) => setRecentId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  borderRadius: '8px',
                  border: '1px solid var(--line)',
                  fontSize: '0.92rem',
                }}
              >
                {history.map((h) => (
                  <option key={h.id} value={h.id}>
                    {h.date?.slice(0, 10)} ({typeof h.score === 'number' ? h.score.toFixed(3) : h.score})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Comparison Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '0.75rem' }}>
            {/* Baseline Card */}
            <div
              style={{
                background: '#faf8f5',
                border: '1px solid var(--line)',
                borderRadius: '12px',
                padding: '0.9rem',
              }}
            >
              <div style={{ fontSize: '0.82rem', color: 'var(--muted)', fontWeight: '600' }}>{t('baseline', lang)}</div>
              <div style={{ fontSize: '1.05rem', fontWeight: '800', marginTop: '0.2rem' }}>{baseline?.date?.slice(0, 10)}</div>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', margin: '0.35rem 0' }}>{baseScore.toFixed(3)}</div>
              <ScoreBandBadge band={baseline?.band} lang={lang} size="small" />
            </div>

            {/* Recent Card */}
            <div
              style={{
                background: '#faf8f5',
                border: '1px solid var(--line)',
                borderRadius: '12px',
                padding: '0.9rem',
              }}
            >
              <div style={{ fontSize: '0.82rem', color: 'var(--muted)', fontWeight: '600' }}>{t('latest', lang)}</div>
              <div style={{ fontSize: '1.05rem', fontWeight: '800', marginTop: '0.2rem' }}>{recent?.date?.slice(0, 10)}</div>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', margin: '0.35rem 0' }}>{recentScore.toFixed(3)}</div>
              <ScoreBandBadge band={recent?.band} lang={lang} size="small" />
            </div>

            {/* Delta & Trajectory Card */}
            <div
              style={{
                background: trajectoryBg,
                border: `2px solid ${trajectoryColor}`,
                borderRadius: '12px',
                padding: '0.9rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
              }}
            >
              <div style={{ fontSize: '0.82rem', color: trajectoryColor, fontWeight: '700' }}>
                {t('score_change', lang)}
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: '900', color: trajectoryColor, margin: '0.2rem 0' }}>
                {deltaFormatted}
              </div>
              <div style={{ fontSize: '0.88rem', fontWeight: '700', color: trajectoryColor }}>
                {trajectoryText}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
