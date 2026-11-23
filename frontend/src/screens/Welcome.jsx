import { useEffect, useState } from 'react'
import { api } from '../api'
import { LANGS, t } from '../i18n'

// Pick an existing player or register a new one (with consent).
export default function Welcome({ onSelect }) {
  const [users, setUsers] = useState([])
  const [creating, setCreating] = useState(false)
  const [lang, setLang] = useState('or')
  const [name, setName] = useState('')
  const [age, setAge] = useState('')
  const [consent, setConsent] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listUsers().then(setUsers).catch(() => setError(t('error_server', lang)))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function create(e) {
    e.preventDefault()
    try {
      const u = await api.createUser({ name, age: age ? Number(age) : null, lang, consent_given: consent })
      onSelect(u)
    } catch {
      setError(t('error_server', lang))
    }
  }

  return (
    <div className="screen">
      <h1>{t('app_title', lang)}</h1>
      <p className="subtitle">{t('tagline', lang)}</p>

      <div className="lang-switch">
        {LANGS.map((l) => (
          <button key={l.code} className={lang === l.code ? 'active' : ''} onClick={() => setLang(l.code)}>
            {l.name}
          </button>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      {!creating ? (
        <>
          <h2>{t('who_is_playing', lang)}</h2>
          <div className="stack">
            {users.map((u) => (
              <button key={u.id} className="big" onClick={() => onSelect(u)}>
                👤 {u.name}
              </button>
            ))}
            <button className="big primary" onClick={() => setCreating(true)}>
              ➕ {t('new_player', lang)}
            </button>
          </div>
        </>
      ) : (
        <form className="stack" onSubmit={create}>
          <label>
            {t('your_name', lang)}
            <input value={name} onChange={(e) => setName(e.target.value)} required maxLength={80} />
          </label>
          <label>
            {t('your_age', lang)}
            <input type="number" inputMode="numeric" min={40} max={120} value={age} onChange={(e) => setAge(e.target.value)} />
          </label>
          <div className="consent">
            <h3>{t('consent_title', lang)}</h3>
            <p>{t('consent_text', lang)}</p>
            <label className="check">
              <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
              {t('consent_agree', lang)}
            </label>
          </div>
          <button className="big primary" disabled={!consent || !name.trim()}>{t('start', lang)}</button>
          <button type="button" className="big" onClick={() => setCreating(false)}>{t('back', lang)}</button>
        </form>
      )}
    </div>
  )
}
