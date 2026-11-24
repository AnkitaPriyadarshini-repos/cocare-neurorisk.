import { t } from '../../i18n'

/**
 * Persistent high-visibility banner displayed on all cognitive risk screening screens.
 * Explicitly alerts users and research participants of demo status and lack of validation.
 */
export default function DemoBanner({ lang = 'or' }) {
  return (
    <div
      className="demo-risk-banner"
      role="alert"
      style={{
        backgroundColor: '#fff3e0',
        color: '#8c3109',
        border: '2px solid #ffb74d',
        borderRadius: '12px',
        padding: '0.65rem 1rem',
        marginBottom: '1rem',
        fontSize: '0.9rem',
        lineHeight: '1.4',
        boxShadow: '0 2px 6px rgba(140, 49, 9, 0.08)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: '800' }}>
        <span aria-hidden="true" style={{ fontSize: '1.2rem' }}>⚠️</span>
        <span>{t('demo_banner_title', lang)}</span>
        <span style={{ fontSize: '0.78rem', background: '#fed7aa', color: '#7c2d12', padding: '0.15rem 0.45rem', borderRadius: '6px', fontWeight: '700' }}>
          OASIS DEMO
        </span>
      </div>
      <p style={{ margin: '0.25rem 0 0', color: '#43281c', fontSize: '0.85rem' }}>
        {t('demo_banner_desc', lang)}
      </p>
    </div>
  )
}
