import { useEffect, useState } from 'react'
import DemoBanner from '../components/risk/DemoBanner'
import DoctorSummaryPrint from '../components/risk/DoctorSummaryPrint'
import ScoreBandBadge from '../components/risk/ScoreBandBadge'
import { t } from '../i18n'
import { riskApi } from '../riskApi'
import { hasVoiceForLang, speak } from '../speech'

export default function RiskCheckResult({
  user,
  result,
  profile,
  useMmse,
  onRetake,
  onViewProgress,
  onHome,
}) {
  const lang = user?.lang ?? 'or'
  const isOdia = lang === 'or'

  const [showDoctorSummary, setShowDoctorSummary] = useState(false)
  const [optedIn, setOptedIn] = useState(() => (user?.id ? riskApi.isOptedInHistory(user.id) : false))
  const [savedNotice, setSavedNotice] = useState(false)
  const [deletedNotice, setDeletedNotice] = useState(false)
  const [canSpeak, setCanSpeak] = useState(() => hasVoiceForLang(lang))

  const band = result?.band || 'moderate'
  const score = result?.probability !== undefined ? result.probability : 0.5
  const scoreNote = result?.score_note || 'Model score calibrated to OASIS sample prevalence of 48.5%'

  // Synchronize opt-in and voice capabilities if user or lang changes
  useEffect(() => {
    if (user?.id) {
      setOptedIn(riskApi.isOptedInHistory(user.id))
    }
    setCanSpeak(hasVoiceForLang(lang))
    function updateVoices() {
      setCanSpeak(hasVoiceForLang(lang))
    }
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.addEventListener('voiceschanged', updateVoices)
      return () => {
        window.speechSynthesis.removeEventListener('voiceschanged', updateVoices)
      }
    }
  }, [user?.id, lang])

  // Filter explanations to only items with magnitude >= 0.01
  const significantExplanations = (result?.explanation || []).filter(
    (item) => item && typeof item.magnitude === 'number' && item.magnitude >= 0.01
  )

  function handleToggleOptIn(e) {
    const isChecked = e.target.checked
    setOptedIn(isChecked)
    setDeletedNotice(false)
    riskApi.setOptInHistory(user.id, isChecked)

    if (isChecked) {
      // Store ONLY { date, band, score, model_variant } - NEVER profile fields
      const record = {
        date: new Date().toISOString(),
        score,
        band,
        model_variant: result?.model_variant || (useMmse ? 'with_mmse' : 'without_mmse'),
      }
      riskApi.saveLocalResult(user.id, record)
      setSavedNotice(true)
      setTimeout(() => setSavedNotice(false), 3000)
    }
  }

  function handleDeleteData() {
    riskApi.deleteLocalHistory(user.id)
    riskApi.setOptInHistory(user.id, false)
    setOptedIn(false)
    setSavedNotice(false)
    setDeletedNotice(true)
    setTimeout(() => setDeletedNotice(false), 3500)
  }

  function handleReadResults() {
    if (!canSpeak) return
    const guidanceText = t(`guidance_${band}`, lang)
    const readText = {
      en: `Screening summary: ${t(`band_${band}`, 'en')}. Model score: ${score}. ${guidanceText}`,
      or: `ସ୍କ୍ରିନିଂ ସାରାଂଶ: ${t(`band_${band}`, 'or')}। ମଡେଲ ସ୍କୋର: ${score}। ${guidanceText}`,
    }
    speak(readText, lang)
  }

  return (
    <div className="screen risk-check-result">
      {/* Persistent DEMO banner */}
      <DemoBanner lang={lang} />

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.6rem' }}>🩺 {t('result_title', lang)}</h1>
        <button
          type="button"
          className="small"
          onClick={handleReadResults}
          disabled={!canSpeak}
          aria-label={canSpeak ? t('listen', lang) : t('voice_not_available', lang)}
          title={!canSpeak ? t('voice_not_available', lang) : undefined}
          style={{
            opacity: canSpeak ? 1 : 0.45,
            cursor: canSpeak ? 'pointer' : 'not-allowed',
          }}
        >
          {canSpeak ? `🔊 ${t('listen', lang)}` : `🔇 ${t('listen', lang)}`}
        </button>
      </div>

      {/* Main Result Card */}
      <div
        style={{
          background: 'var(--card)',
          border: '3px solid var(--line)',
          borderRadius: '18px',
          padding: '1.25rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
          marginBottom: '1rem',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <div style={{ fontSize: '0.95rem', color: 'var(--muted)', marginBottom: '0.25rem' }}>
              {t('model_score_label', lang)}
            </div>
            <div style={{ fontSize: '2.4rem', fontWeight: '800', color: 'var(--ink)' }}>
              {score.toFixed(4)}
            </div>
          </div>
          <ScoreBandBadge band={band} lang={lang} size="large" />
        </div>

        {/* Prevalence calibration note */}
        <div
          style={{
            marginTop: '0.85rem',
            padding: '0.5rem 0.75rem',
            background: '#f9f6f0',
            borderRadius: '10px',
            fontSize: '0.85rem',
            color: 'var(--muted)',
            lineHeight: '1.4',
          }}
        >
          ℹ️ {scoreNote}
        </div>

        {/* What to do next section */}
        <div style={{ marginTop: '1.2rem', borderTop: '2px dashed var(--line)', paddingTop: '1rem' }}>
          <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.2rem' }}>
            🧭 {t('what_to_do_next', lang)}
          </h2>
          <p style={{ margin: 0, fontSize: '1.05rem', lineHeight: '1.5', color: 'var(--ink)' }}>
            {t(`guidance_${band}`, lang)}
          </p>
        </div>

        {/* Factors / Explanations section */}
        {significantExplanations.length > 0 && (
          <div style={{ marginTop: '1.2rem', borderTop: '1px solid var(--line)', paddingTop: '0.85rem' }}>
            <h3 style={{ margin: '0 0 0.5rem', fontSize: '1rem', color: '#2e2c29' }}>
              🔍 {t('explanations_title', lang)}
            </h3>
            <ul style={{ margin: 0, paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.95rem' }}>
              {significantExplanations.map((item, idx) => {
                const text = isOdia && item.text_or ? item.text_or : item.text_en
                const isProtective = item.effect === 'lowers'
                return (
                  <li key={idx} style={{ color: 'var(--ink)' }}>
                    <span>{isProtective ? '📉 ' : '📈 '}</span>
                    <strong>{item.feature}:</strong> {text}
                  </li>
                )
              })}
            </ul>
          </div>
        )}

        {/* Disclaimer banner */}
        <div
          style={{
            marginTop: '1.25rem',
            background: '#fff3e0',
            border: '2px solid #ffe082',
            borderRadius: '12px',
            padding: '0.75rem 1rem',
            fontSize: '0.9rem',
            color: '#3e2723',
            lineHeight: '1.4',
          }}
        >
          <strong>⚠️ {t('not_a_diagnosis', lang)}</strong>
          <div style={{ fontSize: '0.82rem', marginTop: '0.3rem', color: '#3e2723' }}>
            {t('demo_status_badge', lang)}
          </div>
        </div>
      </div>

      {/* Doctor Summary Modal or Drawer */}
      {showDoctorSummary ? (
        <DoctorSummaryPrint
          user={user}
          result={result}
          profile={profile}
          useMmse={useMmse}
          onClose={() => setShowDoctorSummary(false)}
          lang={lang}
        />
      ) : (
        <button
          type="button"
          className="big"
          onClick={() => setShowDoctorSummary(true)}
          style={{ marginBottom: '1rem', borderColor: 'var(--primary)' }}
        >
          {t('print_doctor_summary', lang)}
        </button>
      )}

      {/* On-device Opt-In Storage Section */}
      <div
        style={{
          background: '#fff',
          border: '2px solid var(--line)',
          borderRadius: '16px',
          padding: '1rem',
          marginBottom: '1.25rem',
        }}
      >
        <label className="check" style={{ cursor: 'pointer', margin: 0 }}>
          <input
            type="checkbox"
            checked={optedIn}
            onChange={handleToggleOptIn}
          />
          <span style={{ fontSize: '0.98rem' }}>
            <strong>{t('save_to_device', lang)}</strong>
            <small style={{ display: 'block', color: 'var(--muted)', fontSize: '0.82rem' }}>
              {t('save_to_device_desc', lang)}
            </small>
            <p style={{ margin: '0.35rem 0 0', fontSize: '0.82rem', color: '#6d4c41', lineHeight: '1.35' }}>
              ℹ️ {t('shared_device_consent', lang)}
            </p>
          </span>
        </label>

        {savedNotice && (
          <div style={{ marginTop: '0.5rem', color: 'var(--right)', fontSize: '0.9rem', fontWeight: '700' }}>
            {t('saved_locally', lang)}
          </div>
        )}

        {deletedNotice && (
          <div style={{ marginTop: '0.5rem', color: 'var(--wrong)', fontSize: '0.9rem', fontWeight: '700' }}>
            {t('data_deleted', lang)}
          </div>
        )}

        {optedIn && (
          <div style={{ marginTop: '0.75rem', textAlign: 'right' }}>
            <button
              type="button"
              className="small link"
              onClick={handleDeleteData}
              style={{ margin: 0, color: 'var(--wrong)' }}
            >
              🗑️ {t('delete_my_data', lang)}
            </button>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="stack">
        <button type="button" className="big primary" onClick={onViewProgress}>
          📈 {t('my_progress', lang)}
        </button>
        <div className="row">
          <button type="button" onClick={onRetake}>
            🔁 {t('wizard_title', lang)}
          </button>
          <button type="button" onClick={onHome}>
            🏠 {t('home', lang)}
          </button>
        </div>
      </div>
    </div>
  )
}
