import { useEffect, useState } from 'react'
import { api } from '../api'
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

  const latestScreening = screeningHistory.length > 0 ? screeningHistory[0] : null

  function handleDeleteScreenings() {
    riskApi.deleteLocalHistory(user?.id)
    setScreeningHistory([])
    setDeletedNotice(true)
    setTimeout(() => setDeletedNotice(false), 3000)
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

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem' }}>
          <div style={{ background: '#faf8f5', padding: '0.75rem', borderRadius: '12px', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>{t('caregiver_sessions_stat', lang)}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: '800' }}>{totalSessions}</div>
          </div>

          <div style={{ background: '#faf8f5', padding: '0.75rem', borderRadius: '12px', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>{t('caregiver_avg_acc', lang)}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: '800' }}>
              {avgAccuracy !== null ? `${avgAccuracy}%` : '—'}
            </div>
          </div>

          <div style={{ background: '#faf8f5', padding: '0.75rem', borderRadius: '12px', border: '1px solid var(--line)' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>{t('caregiver_last_check', lang)}</div>
            <div style={{ marginTop: '0.35rem' }}>
              {latestScreening ? (
                <ScoreBandBadge band={latestScreening.band} lang={lang} size="normal" />
              ) : (
                <span style={{ fontSize: '0.95rem', color: 'var(--muted)' }}>—</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Cognitive Game Trends (ProgressChart) */}
      <ProgressChart sessions={sessions} lang={lang} />

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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.15rem' }}>
            📋 {t('screening_records_title', lang)}
          </h2>
          {screeningHistory.length > 0 && (
            <button
              type="button"
              className="small link"
              onClick={handleDeleteScreenings}
              style={{ margin: 0, color: 'var(--wrong)' }}
            >
              🗑️ {t('delete_my_data', lang)}
            </button>
          )}
        </div>

        {deletedNotice && (
          <div style={{ marginBottom: '0.75rem', color: 'var(--wrong)', fontSize: '0.9rem', fontWeight: '700' }}>
            {t('data_deleted', lang)}
          </div>
        )}

        {screeningHistory.length === 0 ? (
          <p style={{ margin: 0, color: 'var(--muted)', fontSize: '0.95rem' }}>
            {t('no_screening_history', lang)}
          </p>
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
