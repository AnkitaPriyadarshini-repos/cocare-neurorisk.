import { t } from '../../i18n'
import ScoreBandBadge from './ScoreBandBadge'

export default function DoctorSummaryPrint({
  user,
  result,
  profile,
  useMmse,
  onClose,
  lang = 'or',
  dateStr = '',
}) {
  const displayDate = dateStr || (result?.date ? result.date.slice(0, 10) : 'Assessment Report')

  function handlePrint() {
    window.print()
  }

  return (
    <div className="doctor-summary-modal" style={{ background: '#fff', border: '3px solid var(--line)', borderRadius: '16px', padding: '1.5rem', margin: '1rem 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid var(--line)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.4rem' }}>{t('doctor_summary_title', lang)}</h2>
          <small style={{ color: 'var(--muted)' }}>CO CARE Cognitive Health Study · {displayDate}</small>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button type="button" className="small primary" onClick={handlePrint}>
            🖨️ Print
          </button>
          <button type="button" className="small" onClick={onClose}>
            ✕ {t('back', lang)}
          </button>
        </div>
      </div>

      {/* Prominent Demo & Non-Validation Statement */}
      <div style={{ background: '#fff3e0', border: '2px solid #ffb74d', borderRadius: '10px', padding: '0.8rem 1rem', marginBottom: '1rem', color: '#b4471b' }}>
        <strong style={{ fontSize: '0.95rem' }}>⚠️ RESEARCH DEMONSTRATION ONLY — NOT CLINICALLY VALIDATED</strong>
        <p style={{ margin: '0.35rem 0 0', fontSize: '0.85rem', color: '#5d4037', lineHeight: '1.4' }}>
          This summary was produced by a research demonstration model trained on the US-based OASIS longitudinal cohort (N=150). It has <strong>NOT been clinically validated on Indian populations (LASI-DAD)</strong>. It is provided solely as an informational reference for discussion during a routine health consultation and is <strong>NOT a medical diagnosis</strong>.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ background: '#faf8f5', padding: '0.8rem', borderRadius: '10px' }}>
          <strong>Participant:</strong> {user?.name || 'Anonymous'}<br />
          <strong>Age:</strong> {profile?.Age} years<br />
          <strong>Biological Sex:</strong> {profile?.Sex === 'M' ? 'Male' : 'Female'}<br />
          <strong>Education:</strong> {profile?.EDUC} years<br />
          <strong>Socioeconomic Tier:</strong> {profile?.SES ? `Tier ${profile.SES}` : 'Not specified'}
        </div>
        <div style={{ background: '#faf8f5', padding: '0.8rem', borderRadius: '10px' }}>
          <strong>Cognitive Screening (MMSE):</strong> {useMmse && profile?.MMSE !== undefined ? `${profile.MMSE} / 30 (Professional)` : 'Not administered (Demographics only)'}<br />
          <strong>Model Variant:</strong> {result?.model_variant}<br />
          <strong>Model Score:</strong> <strong>{result?.probability}</strong> (Decision Threshold: {result?.threshold})<br />
          <div style={{ marginTop: '0.5rem' }}>
            <ScoreBandBadge band={result?.band} lang={lang} size="normal" />
          </div>
        </div>
      </div>

      {/* Model Score Definition and Prevalence Note */}
      <div style={{ fontSize: '0.88rem', color: '#333', background: '#f5f5f5', border: '1px solid #e0d7cb', padding: '0.75rem 1rem', borderRadius: '10px', marginBottom: '1rem', lineHeight: '1.4' }}>
        <strong>Model Score Definition:</strong> The model score of <strong>{result?.probability}</strong> (decision threshold: {result?.threshold}) represents an estimated preliminary screening stratification value calibrated to the training sample prevalence ({result?.score_note || 'OASIS sample prevalence of 48.5%'}). It indicates whether demographic or cognitive screening parameters suggest clinical discussion; it does not represent probability of disease or a medical diagnosis.
      </div>

      {result?.explanation && result.explanation.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: '0.5rem 0' }}>Feature Contributions (Occlusion Analysis):</h3>
          <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.95rem' }}>
            {result.explanation.filter(e => e.magnitude >= 0.01).map((e, idx) => (
              <li key={idx}>
                <strong>{e.feature}</strong> ({e.value}): {e.effect === 'raises' ? 'Raised' : 'Lowered'} score by {e.magnitude} ({e.text_en})
              </li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ background: '#fff3e0', border: '1px solid #ffe082', borderRadius: '10px', padding: '0.8rem 1rem', fontSize: '0.88rem', color: '#5d4037' }}>
        <strong>Notice to Clinician:</strong> {t('not_a_diagnosis', lang)}
        <br />
        <span style={{ fontSize: '0.82rem', color: '#8d6e63' }}>{result?.disclaimer}</span>
      </div>
    </div>
  )
}
