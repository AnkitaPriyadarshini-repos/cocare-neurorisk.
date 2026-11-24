import { t } from '../../i18n'

/**
 * Lightweight inline SVG progress chart for elderly-friendly visualization.
 * Shows session accuracy (%) and level progression over time without external dependencies.
 */
export default function ProgressChart({ sessions = [], lang = 'or' }) {
  if (!sessions || sessions.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '1.5rem', background: '#faf8f5', borderRadius: '14px', border: '2px dashed var(--line)' }}>
        <p style={{ margin: 0, color: 'var(--muted)' }}>{t('no_game_history', lang)}</p>
      </div>
    )
  }

  // Sort sessions chronologically (oldest to newest)
  const sorted = [...sessions].sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
  const data = sorted.slice(-12) // show last 12 sessions for neat display

  const width = 580
  const height = 220
  const padding = { top: 25, right: 30, bottom: 40, left: 45 }
  const chartW = width - padding.left - padding.right
  const chartH = height - padding.top - padding.bottom

  const n = data.length
  const stepX = n > 1 ? chartW / (n - 1) : chartW / 2

  const points = data.map((d, i) => {
    const acc = Math.max(0, Math.min(1, d.accuracy ?? 0))
    const x = n > 1 ? padding.left + i * stepX : padding.left + chartW / 2
    const y = padding.top + chartH - acc * chartH
    return { x, y, acc, level: d.new_level ?? d.old_level ?? 1, date: d.started_at.slice(5, 10), game: d.game }
  })

  const pathD = points.length === 1
    ? ''
    : points.reduce((acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`), '')

  const areaD = points.length > 1
    ? `${pathD} L ${points[points.length - 1].x} ${padding.top + chartH} L ${points[0].x} ${padding.top + chartH} Z`
    : ''

  return (
    <div className="progress-chart-container" style={{ background: '#fff', border: '2px solid var(--line)', borderRadius: '16px', padding: '1rem', margin: '1rem 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.15rem' }}>📈 {t('game_history_chart', lang)}</h2>
        <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
          {points.length} {lang === 'or' ? 'ଖେଳ' : 'sessions'}
        </span>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: 'auto', display: 'block', overflow: 'visible' }}
        role="img"
        aria-label="Cognitive game accuracy trend over recent sessions"
      >
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1.0].map((frac) => {
          const y = padding.top + chartH - frac * chartH
          return (
            <g key={frac}>
              <line
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                stroke="#e0d7cb"
                strokeDasharray={frac === 0 ? undefined : '4 4'}
                strokeWidth={frac === 0 ? 2 : 1}
              />
              <text
                x={padding.left - 8}
                y={y + 4}
                textAnchor="end"
                fontSize="12"
                fill="#777"
                fontWeight="500"
              >
                {Math.round(frac * 100)}%
              </text>
            </g>
          )
        })}

        {/* Gradient fill */}
        <defs>
          <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#b4471b" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#b4471b" stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {areaD && <path d={areaD} fill="url(#chartGrad)" />}

        {/* Trend line */}
        {pathD && (
          <path
            d={pathD}
            fill="none"
            stroke="#b4471b"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Data points */}
        {points.map((p, i) => (
          <g key={i}>
            <circle
              cx={p.x}
              cy={p.y}
              r="6.5"
              fill="#fff"
              stroke="#b4471b"
              strokeWidth="3"
            />
            {/* Value badge on point */}
            <text
              x={p.x}
              y={p.y - 10}
              textAnchor="middle"
              fontSize="11"
              fontWeight="700"
              fill="#1d1d1b"
            >
              {Math.round(p.acc * 100)}%
            </text>
            {/* X-axis date label */}
            <text
              x={p.x}
              y={height - 12}
              textAnchor="middle"
              fontSize="11"
              fill="#5a5650"
            >
              #{i + 1}
            </text>
          </g>
        ))}
      </svg>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.4rem', fontSize: '0.85rem', color: 'var(--muted)' }}>
        <span>{lang === 'or' ? 'ପୂର୍ବରୁ → ସଦ୍ୟତମ' : 'Older → Most Recent'}</span>
        <span>{lang === 'or' ? 'ଲକ୍ଷ୍ୟ: ୮୦%+' : 'Target: 80%+'}</span>
      </div>
    </div>
  )
}
