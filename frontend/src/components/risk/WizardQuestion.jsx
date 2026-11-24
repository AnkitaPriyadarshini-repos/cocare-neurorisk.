import { speak } from '../../speech'
import { t } from '../../i18n'

export default function WizardQuestion({
  field,
  value,
  onChange,
  error,
  lang = 'or'
}) {
  const isOdia = lang === 'or'
  const title = isOdia && field.label_or ? field.label_or : field.label
  const help = isOdia && field.help_text_or ? field.help_text_or : field.help_text

  function handleListen() {
    speak(
      {
        en: `${field.label}. ${field.help_text || ''}`,
        or: `${field.label_or || field.label}। ${field.help_text_or || ''}`
      },
      lang
    )
  }

  return (
    <div className="wizard-question" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.5rem', lineHeight: '1.3' }}>{title}</h2>
        <button
          type="button"
          onClick={handleListen}
          className="small"
          aria-label={t('read_question', lang)}
          style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.8rem', minHeight: '44px' }}
        >
          🔊 {t('read_question', lang)}
        </button>
      </div>

      {help && (
        <p style={{ margin: 0, color: 'var(--muted)', fontSize: '1.05rem', lineHeight: '1.4' }}>
          {help}
        </p>
      )}

      {/* Field Input Widget */}
      <div style={{ marginTop: '0.5rem' }}>
        {field.name === 'Sex' ? (
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            {field.options?.map((opt) => {
              const optLabel = isOdia && opt.label_or ? opt.label_or : opt.label
              const isSelected = value === opt.value
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => onChange(opt.value)}
                  className={`big ${isSelected ? 'primary' : ''}`}
                  style={{
                    flex: '1 1 140px',
                    minHeight: '76px',
                    fontSize: '1.25rem',
                    fontWeight: isSelected ? '700' : '500',
                    borderWidth: '3px',
                    borderColor: isSelected ? 'var(--primary)' : 'var(--line)'
                  }}
                  aria-pressed={isSelected}
                >
                  {opt.value === 'F' ? '👩 ' : '👨 '}
                  {optLabel}
                </button>
              )
            })}
          </div>
        ) : field.type === 'integer_tier' || field.name === 'SES' ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {[1, 2, 3, 4, 5].map((tier) => {
              const tierKey = `ses_tier_${tier}`
              const isSelected = Number(value) === tier
              return (
                <button
                  key={tier}
                  type="button"
                  onClick={() => onChange(tier)}
                  className={isSelected ? 'primary' : ''}
                  style={{
                    minHeight: '64px',
                    justifyContent: 'flex-start',
                    textAlign: 'left',
                    padding: '0.6rem 1rem',
                    fontSize: '1.1rem',
                    borderWidth: isSelected ? '3px' : '2px',
                    borderColor: isSelected ? 'var(--primary)' : 'var(--line)'
                  }}
                  aria-pressed={isSelected}
                >
                  <span style={{ fontWeight: '700', marginRight: '0.5rem' }}>
                    {isSelected ? '✓ ' : ''}{tier}.
                  </span>
                  <span>{t(tierKey, lang)}</span>
                </button>
              )
            })}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <button
                type="button"
                className="big"
                style={{ width: '68px', minHeight: '68px', fontSize: '1.8rem', padding: 0 }}
                onClick={() => {
                  const curr = Number(value) || field.min || 0
                  if (curr > (field.min ?? 0)) onChange(curr - (field.step || 1))
                }}
                aria-label="Decrease"
              >
                −
              </button>
              <input
                type="number"
                inputMode="numeric"
                min={field.min}
                max={field.max}
                step={field.step || 1}
                value={value ?? ''}
                onChange={(e) => onChange(e.target.value === '' ? '' : Number(e.target.value))}
                style={{
                  flex: 1,
                  minHeight: '68px',
                  fontSize: '1.6rem',
                  textAlign: 'center',
                  fontWeight: '700',
                  borderRadius: '14px'
                }}
                aria-describedby={error ? `${field.name}-error` : undefined}
              />
              <button
                type="button"
                className="big"
                style={{ width: '68px', minHeight: '68px', fontSize: '1.8rem', padding: 0 }}
                onClick={() => {
                  const curr = value === '' || value === undefined ? (field.min || 0) : Number(value)
                  if (curr < (field.max ?? 120)) onChange(curr + (field.step || 1))
                }}
                aria-label="Increase"
              >
                +
              </button>
            </div>
            {field.name === 'Age' && (
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {[60, 65, 70, 75, 80].map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    className="small"
                    style={{ flex: 1, minHeight: '44px' }}
                    onClick={() => onChange(preset)}
                  >
                    {preset}
                  </button>
                ))}
              </div>
            )}
            {field.name === 'EDUC' && (
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {[
                  { yrs: 0, lbl: '0 (None)' },
                  { yrs: 5, lbl: '5 (Primary)' },
                  { yrs: 10, lbl: '10 (Matric)' },
                  { yrs: 12, lbl: '12 (+2)' },
                  { yrs: 15, lbl: '15 (Grad)' }
                ].map((item) => (
                  <button
                    key={item.yrs}
                    type="button"
                    className="small"
                    style={{ flex: 1, minHeight: '44px' }}
                    onClick={() => onChange(item.yrs)}
                  >
                    {item.lbl}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Validation Message */}
      {error && (
        <div
          id={`${field.name}-error`}
          role="alert"
          style={{
            color: 'var(--wrong)',
            backgroundColor: '#ffebee',
            padding: '0.6rem 1rem',
            borderRadius: '10px',
            border: '2px solid #ef9a9a',
            fontSize: '1rem',
            fontWeight: '600'
          }}
        >
          ⚠️ {error}
        </div>
      )}
    </div>
  )
}
