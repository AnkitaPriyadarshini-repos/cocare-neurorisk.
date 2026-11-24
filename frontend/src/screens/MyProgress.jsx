import { useEffect, useState } from 'react'
import { api } from '../api'
import AssessmentCompare from '../components/risk/AssessmentCompare'
import DemoBanner from '../components/risk/DemoBanner'
import ProgressChart from '../components/risk/ProgressChart'
import ScoreBandBadge from '../components/risk/ScoreBandBadge'
import { t } from '../i18n'
import { riskApi } from '../riskApi'

export default function MyProgress({ user, onRiskCheck, onBack }) {
  const lang = user?.lang ?? 'or'
  const isOdia = lang === 'or'

  const [gameHistory, setGameHistory] = useState(null)
  const [screeningHistory, setScreeningHistory] = useState(() => (user?.id ? riskApi.getLocalHistory(user.id) : []))
  const [deletedNotice, setDeletedNotice] = useState(false)

  useEffect(() => {
    if (user?.id) {
      api.history(user.id).then(setGameHistory).catch(() => setGameHistory({ sessions: [] }))
      setScreeningHistory(riskApi.getLocalHistory(user.id))
    }
  }, [user?.id])

  const sessions = gameHistory?.sessions || []
  const totalSessions = sessions.length
  const completedSessions = sessions.filter((s) => s.completed)
  const avgAccuracy =
    completedSessions.length > 0
      ? Math.round(
          (completedSessions.reduce((sum, s) => sum + (s.accuracy ?? 0), 0) /
            completedSessions.length) *
            100
        )
      : null

  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  const recentSessionsCount = sessions.filter(
    (s) => s.started_at && new Date(s.started_at) >= thirtyDaysAgo
  ).length

  const latestScreening = screeningHistory.length > 0 ? screeningHistory[0] : null

  function handleDeleteScreenings() {
    riskApi.deleteLocalHistory(user?.id)
    setScreeningHistory([])
    setDeletedNotice(true)
    setTimeout(() => setDeletedNotice(false), 3000)
  }

  function handleExportCSV() {
    if (screeningHistory.length === 0) return
    const headers = ['Date', 'Model_Score', 'Risk_Band', 'Model_Variant']
    const rows = screeningHistory.map((h) => [
      h.date?.slice(0, 10),
      typeof h.score === 'number' ? h.score.toFixed(4) : h.score,
      h.band,
      h.model_variant || h.variant,
    ])
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `cocare_screening_history_${user?.id || 'record'}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  function handlePrint() {
    window.print()
  }

  return (
    <div className="screen my-progress-screen">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.6rem' }}>📈 {t('my_progress_title', lang)}</h1>
        <button type="button" className="small" onClick={onBack}>
          ← {t('back', lang)}
        </button>
      </div>

      {/* Persistent DEMO banner */}
      <DemoBanner lang={lang} />

      {/* Caregiver & Family Summary Card */}
      <div
        style={{
          background: 'var(--card)',
          border: '3px solid var(--line)',
          borderRadius: '16px',
          padding: '1.25rem',
          marginBottom: '1rem',
          boxShadow: '0 3px 10px rgba(0,0,0,0.04)',
        }}
      >
        <h2 style={{ margin: '0 0 0.75rem', fontSize: '1.2rem', color: '#8c3109' }}>
          👨‍👩‍👦 {t('caregiver_summary_title', lang)}
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem' }}>
          <div style={{ background: '#faf8f5', padding: '0.75rem', borderRadius: '12px', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>{t('caregiver_sessions_stat', lang)}</div>
            <div style={{ fontSize: '1.7rem', fontWeight: '800' }}>{totalSessions}</div>
          </div>

          <div style={{ background: '#faf8f5', padding: '0.75rem', borderRadius: '12px', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>{t('caregiver_avg_acc', lang)}</div>
            <div style={{ fontSize: '1.7rem', fontWeight: '800' }}>
              {avgAccuracy !== null ? `${avgAccuracy}%` : '—'}
            </div>
          </div>

          <div style={{ background: '#faf8f5', padding: '0.75rem', borderRadius: '12px', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>{t('caregiver_last_check', lang)}</div>
            <div style={{ marginTop: '0.35rem' }}>
              {latestScreening ? (
                <ScoreBandBadge band={latestScreening.band} lang={lang} size="small" />
              ) : (
                <span style={{ fontSize: '0.95rem', color: 'var(--muted)' }}>—</span>
              )}
            </div>
          </div>

          <div style={{ background: '#faf8f5', padding: '0.75rem', borderRadius: '12px', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>{t('active_30_days', lang)}</div>
            <div style={{ fontSize: '1.7rem', fontWeight: '800' }}>{recentSessionsCount}</div>
          </div>
        </div>
      </div>

      {/* Cognitive Game Trends (ProgressChart) */}
      <ProgressChart sessions={sessions} lang={lang} />

      {/* Longitudinal Assessment Trajectory Comparison (when >= 2 checks exist) */}
      <AssessmentCompare history={screeningHistory} lang={lang} />

      {/* Opt-in Local Screening Records */}
      <div
        style={{
          background: 'var(--card)',
          border: '2px solid var(--line)',
          borderRadius: '16px',
          padding: '1.25rem',
          marginBottom: '1.5rem',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.15rem' }}>
            📋 {t('screening_records_title', lang)}
          </h2>
          {screeningHistory.length > 0 && (
            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="small"
                onClick={handlePrint}
                style={{ fontSize: '0.85rem', padding: '0.3rem 0.6rem' }}
                aria-label={t('print_progress_report', lang)}
              >
                🖨️ {t('print_progress_report', lang)}
              </button>
              <button
                type="button"
                className="small"
                onClick={handleExportCSV}
                style={{ fontSize: '0.85rem', padding: '0.3rem 0.6rem' }}
                aria-label={t('export_csv', lang)}
              >
                📥 CSV
              </button>
              <button
                type="button"
                className="small link"
                onClick={handleDeleteScreenings}
                style={{ margin: 0, color: 'var(--wrong)', fontSize: '0.85rem' }}
              >
                🗑️ {t('delete_my_data', lang)}
              </button>
            </div>
          )}
        </div>

        {deletedNotice && (
          <div style={{ marginBottom: '0.75rem', color: 'var(--wrong)', fontSize: '0.9rem', fontWeight: '700' }}>
            {t('data_deleted', lang)}
          </div>
        )}

        {screeningHistory.length === 0 ? (
          <div
            style={{
              background: '#faf8f5',
              border: '2px dashed var(--line)',
              borderRadius: '14px',
              padding: '1.5rem',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '2.2rem', marginBottom: '0.4rem' }}>🩺</div>
            <h3 style={{ margin: '0 0 0.4rem', fontSize: '1.1rem' }}>{t('empty_screening_title', lang)}</h3>
            <p style={{ margin: '0 0 1rem', color: 'var(--muted)', fontSize: '0.92rem', lineHeight: '1.4', maxWidth: '420px', marginLeft: 'auto', marginRight: 'auto' }}>
              {t('empty_screening_desc', lang)}
            </p>
            <button
              type="button"
              className="small primary"
              onClick={onRiskCheck}
              style={{ minHeight: '44px', padding: '0.5rem 1.25rem', fontSize: '1rem', fontWeight: '700' }}
            >
              ✨ {t('start_first_check', lang)}
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="history" style={{ width: '100%', fontSize: '0.88rem' }}>
              <thead>
                <tr>
                  <th>{t('date', lang)}</th>
                  <th>{t('score', lang)}</th>
                  <th>{t('band', lang)}</th>
                  <th>{t('variant', lang)}</th>
                </tr>
              </thead>
              <tbody>
                {screeningHistory.map((rec) => (
                  <tr key={rec.id}>
                    <td>{rec.date?.slice(0, 10)}</td>
                    <td><strong>{typeof rec.score === 'number' ? rec.score.toFixed(3) : rec.score}</strong></td>
                    <td>
                      <ScoreBandBadge band={rec.band} lang={lang} size="normal" />
                    </td>
                    <td>
                      <small style={{ color: 'var(--muted)' }}>
                        {rec.variant === 'with_mmse'
                          ? (isOdia ? 'MMSE ସହିତ' : 'With MMSE')
                          : (isOdia ? 'ଜନସଂଖ୍ୟା ମାତ୍ର' : 'Demographics')}
                      </small>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="stack">
        <button type="button" className="big primary" onClick={onRiskCheck}>
          🩺 {t('risk_check', lang)}
        </button>
        <button type="button" className="big" onClick={onBack}>
          🏠 {t('home', lang)}
        </button>
      </div>
    </div>
  )
}
