import { t } from '../../i18n'

export default function ScoreBandBadge({ band, lang = 'or', size = 'normal' }) {
  const configs = {
    lower: {
      icon: '🛡️',
      color: '#1b5e20',
      bg: '#e8f5e9',
      border: '#a5d6a7',
      labelKey: 'band_lower',
      ariaLabel: 'Lower Risk Band'
    },
    moderate: {
      icon: '⚖️',
      color: '#b26a00',
      bg: '#fff8e1',
      border: '#ffe082',
      labelKey: 'band_moderate',
      ariaLabel: 'Moderate Risk Band'
    },
    higher: {
      icon: '🩺',
      color: '#b71c1c',
      bg: '#ffebee',
      border: '#ef9a9a',
      labelKey: 'band_higher',
      ariaLabel: 'Elevated Risk Band'
    }
  }

  const cfg = configs[band] || configs.moderate

  const style = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.6rem',
    padding: size === 'large' ? '0.6rem 1.2rem' : '0.4rem 0.8rem',
    borderRadius: '12px',
    backgroundColor: cfg.bg,
    color: cfg.color,
    border: `2px solid ${cfg.border}`,
    fontWeight: '700',
    fontSize: size === 'large' ? '1.25rem' : '1.05rem',
  }

  return (
    <div style={style} role="status" aria-label={cfg.ariaLabel}>
      <span aria-hidden="true" style={{ fontSize: size === 'large' ? '1.5rem' : '1.2rem' }}>
        {cfg.icon}
      </span>
      <span>{t(cfg.labelKey, lang)}</span>
    </div>
  )
}
