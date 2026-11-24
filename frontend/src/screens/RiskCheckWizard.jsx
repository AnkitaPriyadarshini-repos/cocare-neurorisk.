import { useEffect, useState } from 'react'
import WizardQuestion from '../components/risk/WizardQuestion'
import { t } from '../i18n'
import { FALLBACK_FORM_SPEC, riskApi } from '../riskApi'
import { speak } from '../speech'

export default function RiskCheckWizard({ user, onComplete, onCancel }) {
  const lang = user?.lang ?? 'or'
  const isOdia = lang === 'or'

  const [formSpec, setFormSpec] = useState(FALLBACK_FORM_SPEC)
  const [profile, setProfile] = useState({
    Age: 65,
    Sex: 'F',
    EDUC: 10,
    SES: 3,
    MMSE: 26,
  })
  const [useMmse, setUseMmse] = useState(false)
  const [stepIndex, setStepIndex] = useState(0)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [fontSizeMode, setFontSizeMode] = useState('normal') // normal | large | xlarge

  // Fetch dynamic form spec on mount
  useEffect(() => {
    riskApi.getFormSpec().then((spec) => {
      if (spec && spec.fields) {
        setFormSpec(spec)
      }
    }).catch(() => {})
  }, [])

  // Standard steps: Age, Sex, EDUC, SES, then MMSE toggle step
  // Total steps: 5
  const totalSteps = 5

  const fontScale = {
    normal: '1rem',
    large: '1.18rem',
    xlarge: '1.35rem',
  }[fontSizeMode]

  function getField(name) {
    return formSpec.fields?.find((f) => f.name === name) || FALLBACK_FORM_SPEC.fields.find((f) => f.name === name)
  }

  function handleFieldChange(name, val) {
    setError('')
    setProfile((prev) => ({ ...prev, [name]: val }))
  }

  function validateCurrentStep() {
    if (stepIndex === 0) {
      const age = Number(profile.Age)
      if (!profile.Age || isNaN(age) || age < 40 || age > 120) {
        setError(t('val_age_req', lang))
        return false
      }
    } else if (stepIndex === 1) {
      if (!profile.Sex || (profile.Sex !== 'F' && profile.Sex !== 'M')) {
        setError(t('val_sex_req', lang))
        return false
      }
    } else if (stepIndex === 2) {
      const educ = Number(profile.EDUC)
      if (profile.EDUC === '' || isNaN(educ) || educ < 0 || educ > 30) {
        setError(t('val_educ_req', lang))
        return false
      }
    } else if (stepIndex === 3) {
      if (profile.SES !== undefined && profile.SES !== '') {
        const ses = Number(profile.SES)
        if (isNaN(ses) || ses < 1 || ses > 5) {
          setError(t('val_ses_req', lang))
          return false
        }
      }
    } else if (stepIndex === 4) {
      if (useMmse) {
        const mmse = Number(profile.MMSE)
        if (profile.MMSE === '' || isNaN(mmse) || mmse < 0 || mmse > 30) {
          setError(t('val_mmse_range', lang))
          return false
        }
      }
    }
    setError('')
    return true
  }

  function handleNext() {
    if (!validateCurrentStep()) return
    if (stepIndex < totalSteps - 1) {
      setStepIndex((prev) => prev + 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      handleSubmit()
    }
  }

  function handleBack() {
    setError('')
    if (stepIndex > 0) {
      setStepIndex((prev) => prev - 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      onCancel()
    }
  }

  async function handleSubmit() {
    if (!validateCurrentStep()) return
    setSubmitting(true)
    setSubmitError('')

    const payload = {
      Age: Number(profile.Age),
      Sex: profile.Sex,
      EDUC: Number(profile.EDUC),
    }
    if (profile.SES !== '' && profile.SES !== undefined) {
      payload.SES = Number(profile.SES)
    }
    if (useMmse && profile.MMSE !== '' && profile.MMSE !== undefined) {
      payload.MMSE = Number(profile.MMSE)
    }

    try {
      const res = await riskApi.predictRisk(payload, useMmse)
      onComplete(res, payload, useMmse)
    } catch (err) {
      setSubmitError(err.message || 'Error communicating with assessment model')
      setSubmitting(false)
    }
  }

  function renderStepContent() {
    if (stepIndex === 0) {
      const f = getField('Age')
      return <WizardQuestion field={f} value={profile.Age} onChange={(v) => handleFieldChange('Age', v)} error={error} lang={lang} />
    }
    if (stepIndex === 1) {
      const f = getField('Sex')
      return <WizardQuestion field={f} value={profile.Sex} onChange={(v) => handleFieldChange('Sex', v)} error={error} lang={lang} />
    }
    if (stepIndex === 2) {
      const f = getField('EDUC')
      return <WizardQuestion field={f} value={profile.EDUC} onChange={(v) => handleFieldChange('EDUC', v)} error={error} lang={lang} />
    }
    if (stepIndex === 3) {
      const f = getField('SES')
      return (
        <div>
          <div style={{ display: 'inline-block', marginBottom: '0.5rem', background: '#e0e0e0', padding: '0.2rem 0.6rem', borderRadius: '8px', fontSize: '0.85rem' }}>
            {t('optional_badge', lang)}
          </div>
          <WizardQuestion field={f} value={profile.SES} onChange={(v) => handleFieldChange('SES', v)} error={error} lang={lang} />
        </div>
      )
    }
    if (stepIndex === 4) {
      const mmseField = getField('MMSE')
      return (
        <div className="mmse-step" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
            <h2 style={{ margin: 0, fontSize: '1.45rem', lineHeight: '1.3' }}>
              🧠 {t('mmse_step_title', lang)}
            </h2>
            <button
              type="button"
              className="small"
              onClick={() => {
                speak(
                  {
                    en: `${t('mmse_step_title', 'en')}. ${t('mmse_step_desc', 'en')}`,
                    or: `${t('mmse_step_title', 'or')}। ${t('mmse_step_desc', 'or')}`,
                  },
                  lang
                )
              }}
              style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.8rem', minHeight: '44px' }}
            >
              🔊 {t('read_question', lang)}
            </button>
          </div>

          <p style={{ margin: 0, color: 'var(--muted)', fontSize: '1.05rem', lineHeight: '1.4' }}>
            {t('mmse_step_desc', lang)}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button
              type="button"
              className={!useMmse ? 'primary big' : 'big'}
              onClick={() => setUseMmse(false)}
              style={{
                justifyContent: 'flex-start',
                textAlign: 'left',
                borderWidth: !useMmse ? '3px' : '2px',
                borderColor: !useMmse ? 'var(--primary)' : 'var(--line)',
              }}
              aria-pressed={!useMmse}
            >
              <span style={{ fontSize: '1.3rem', marginRight: '0.6rem' }}>{!useMmse ? '◉' : '○'}</span>
              <span>
                <strong>{t('mmse_no_score', lang)}</strong>
                <small style={{ display: 'block', color: !useMmse ? '#fff' : 'var(--muted)', fontSize: '0.85rem' }}>
                  {isOdia ? 'କେବଳ ବୟସ, ଲିଙ୍ଗ ଓ ଶିକ୍ଷା ଆଧାରରେ ଯାଞ୍ଚ କରିବ [needs native review]' : 'Screens using age, sex, and education demographics only'}
                </small>
              </span>
            </button>

            <button
              type="button"
              className={useMmse ? 'primary big' : 'big'}
              onClick={() => setUseMmse(true)}
              style={{
                justifyContent: 'flex-start',
                textAlign: 'left',
                borderWidth: useMmse ? '3px' : '2px',
                borderColor: useMmse ? 'var(--primary)' : 'var(--line)',
              }}
              aria-pressed={useMmse}
            >
              <span style={{ fontSize: '1.3rem', marginRight: '0.6rem' }}>{useMmse ? '◉' : '○'}</span>
              <span>
                <strong>{t('mmse_has_score', lang)}</strong>
                <small style={{ display: 'block', color: useMmse ? '#fff' : 'var(--muted)', fontSize: '0.85rem' }}>
                  {isOdia ? 'ଡାକ୍ତର ଦେଇଥିବା ୩୦ ମଧ୍ୟରୁ ସ୍କୋର ଯୋଗ କରନ୍ତୁ [needs native review]' : 'Add official test score out of 30'}
                </small>
              </span>
            </button>
          </div>

          {useMmse && (
            <div style={{ marginTop: '0.75rem', padding: '1rem', background: '#fff', border: '2px solid var(--line)', borderRadius: '14px' }}>
              <WizardQuestion
                field={mmseField}
                value={profile.MMSE}
                onChange={(v) => handleFieldChange('MMSE', v)}
                error={error}
                lang={lang}
              />
            </div>
          )}
        </div>
      )
    }
  }

  const progressPercent = Math.round(((stepIndex + 1) / totalSteps) * 100)

  return (
    <div className="screen risk-check-wizard" style={{ fontSize: fontScale }}>
      {/* Top bar with back, font-size toggle, and exit */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <button type="button" className="small" onClick={handleBack} aria-label={t('back', lang)}>
          ← {t('back', lang)}
        </button>

        {/* Font size toggle for elderly vision support */}
        <div style={{ display: 'flex', gap: '0.3rem', background: '#ece6dc', padding: '0.2rem', borderRadius: '10px' }} role="group" aria-label={t('font_size', lang)}>
          <button
            type="button"
            className="small"
            style={{
              minHeight: '36px',
              padding: '0.2rem 0.5rem',
              background: fontSizeMode === 'normal' ? 'var(--card)' : 'transparent',
              border: fontSizeMode === 'normal' ? '2px solid var(--line)' : 'none',
              fontWeight: fontSizeMode === 'normal' ? '700' : '500',
              fontSize: '0.85rem',
            }}
            onClick={() => setFontSizeMode('normal')}
          >
            A
          </button>
          <button
            type="button"
            className="small"
            style={{
              minHeight: '36px',
              padding: '0.2rem 0.5rem',
              background: fontSizeMode === 'large' ? 'var(--card)' : 'transparent',
              border: fontSizeMode === 'large' ? '2px solid var(--line)' : 'none',
              fontWeight: fontSizeMode === 'large' ? '700' : '500',
              fontSize: '1rem',
            }}
            onClick={() => setFontSizeMode('large')}
          >
            A+
          </button>
          <button
            type="button"
            className="small"
            style={{
              minHeight: '36px',
              padding: '0.2rem 0.5rem',
              background: fontSizeMode === 'xlarge' ? 'var(--card)' : 'transparent',
              border: fontSizeMode === 'xlarge' ? '2px solid var(--line)' : 'none',
              fontWeight: fontSizeMode === 'xlarge' ? '700' : '500',
              fontSize: '1.15rem',
            }}
            onClick={() => setFontSizeMode('xlarge')}
          >
            A++
          </button>
        </div>

        <button type="button" className="small link" onClick={onCancel} style={{ margin: 0, textDecoration: 'none' }}>
          ✕ {t('stop', lang)}
        </button>
      </div>

      {/* Wizard Header and Progress Bar */}
      <div style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.4rem' }}>
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>🩺 {t('wizard_title', lang)}</h1>
          <span style={{ fontSize: '0.95rem', color: 'var(--muted)', fontWeight: '600' }}>
            {t('step', lang)} {stepIndex + 1} {t('of', lang)} {totalSteps}
          </span>
        </div>

        {/* Visual progress bar */}
        <div
          style={{
            height: '10px',
            backgroundColor: '#e6ded3',
            borderRadius: '5px',
            overflow: 'hidden',
          }}
          role="progressbar"
          aria-valuenow={progressPercent}
          aria-valuemin="0"
          aria-valuemax="100"
        >
          <div
            style={{
              width: `${progressPercent}%`,
              height: '100%',
              backgroundColor: 'var(--primary)',
              transition: 'width 0.25s ease',
            }}
          />
        </div>
      </div>

      {/* Main Question Card */}
      <div
        style={{
          background: 'var(--card)',
          border: '2px solid var(--line)',
          borderRadius: '16px',
          padding: '1.25rem',
          minHeight: '260px',
        }}
      >
        {renderStepContent()}

        {error && (
          <div className="error" style={{ marginTop: '1rem', fontSize: '1rem' }} role="alert">
            ⚠️ {error}
          </div>
        )}
      </div>

      {submitError && (
        <div className="error" style={{ marginTop: '1rem', fontSize: '1rem' }} role="alert">
          ❌ {submitError}
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="stack" style={{ marginTop: '1.5rem' }}>
        <button
          type="button"
          className="big primary"
          onClick={handleNext}
          disabled={submitting}
        >
          {submitting
            ? '⏳ ...'
            : stepIndex === totalSteps - 1
            ? `✓ ${t('submit_check', lang)}`
            : `${t('next', lang)} →`}
        </button>

        {stepIndex === 3 && (
          <button
            type="button"
            className="small"
            onClick={() => {
              handleFieldChange('SES', '')
              setStepIndex((prev) => prev + 1)
            }}
          >
            {t('skip', lang)} (SES)
          </button>
        )}
      </div>
    </div>
  )
}
