import { useEffect, useState } from 'react'
import { api } from '../api'
import { LANGS, t } from '../i18n'

export const GAMES = [
  { id: 'memory_match', icon: '🃏' },
  { id: 'picture_recall', icon: '🖼️' },
  { id: 'find_it', icon: '🔍' },
]

export function Home({ user, onPlay, onHistory, onSettings, onSwitch, onRiskCheck, onProgress }) {
  const lang = user.lang
  return (
    <div className="screen">
      <h1>🙏 {user.name}</h1>
      <h2>{t('choose_game', lang)}</h2>
      <div className="stack">
        {GAMES.map((g) => (
          <button key={g.id} className="big game" onClick={() => onPlay(g.id)}>
            <span className="game-icon">{g.icon}</span>
            <span>
              {t(g.id, lang)}
              <small>{t('level', lang)} {user.levels?.[g.id] ?? 1}</small>
            </span>
          </button>
        ))}
      </div>
      {/* Elderly-friendly Health Risk Check & My Progress navigation entry */}
      <div className="row" style={{ marginTop: '0.25rem' }}>
        <button className="primary" onClick={onRiskCheck} style={{ fontWeight: '700' }}>
          🩺 {t('risk_check', lang)}
        </button>
        <button onClick={onProgress}>
          📈 {t('my_progress', lang)}
        </button>
      </div>
      <div className="row">
        <button onClick={onHistory}>📅 {t('history', lang)}</button>
        <button onClick={onSwitch}>👥 {t('switch_player', lang)}</button>
      </div>
      <button className="link" onClick={onSettings}>⚙️ {t('settings', lang)}</button>
    </div>
  )
}

export function Result({ user, result, game, onAgain, onHome }) {
  const lang = user.lang
  const { metrics, decision } = result
  const stars = metrics.accuracy >= 0.85 ? 3 : metrics.accuracy >= 0.5 ? 2 : 1
  return (
    <div className="screen center">
      <h1>{t('well_done', lang)}</h1>
      <p className="stars">{'⭐'.repeat(stars)}</p>
      <p className="message">{t(decision.message_key, lang)}</p>
      <p>
        {t('correct_answers', lang)}: {Math.round(metrics.accuracy * 100)}%
        {' · '}
        {t('level', lang)} {decision.old_level} → {decision.new_level}
      </p>
      <details className="why">
        <summary>{t('why', lang)}</summary>
        <p><code>{decision.rule}</code></p>
        <p>{decision.reason}</p>
      </details>
      <div className="stack">
        <button className="big primary" onClick={() => onAgain(game)}>🔁 {t('play_again', lang)}</button>
        <button className="big" onClick={onHome}>🏠 {t('home', lang)}</button>
      </div>
    </div>
  )
}

export function History({ user, onBack }) {
  const lang = user.lang
  const [data, setData] = useState(null)
  useEffect(() => {
    api.history(user.id).then(setData)
  }, [user.id])

  return (
    <div className="screen">
      <h1>📅 {t('history', lang)}</h1>
      {!data ? (
        <p>…</p>
      ) : data.sessions.length === 0 ? (
        <p>{t('no_history', lang)}</p>
      ) : (
        <table className="history">
          <thead>
            <tr><th>Date</th><th>Game</th><th>%</th><th>{t('level', lang)}</th></tr>
          </thead>
          <tbody>
            {data.sessions.map((s) => (
              <tr key={s.id} title={s.reason}>
                <td>{s.started_at.slice(0, 16)}</td>
                <td>{t(s.game, lang)}{s.completed ? '' : ' ✋'}</td>
                <td>{Math.round((s.accuracy ?? 0) * 100)}</td>
                <td>{s.old_level} → {s.new_level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <button className="big" onClick={onBack}>{t('back', lang)}</button>
    </div>
  )
}

// For the caregiver / researcher: language and study conditions, data export.
export function Settings({ user, onSaved, onBack }) {
  const [u, setU] = useState(user)
  async function set(field, value) {
    const updated = await api.updateUser(user.id, { [field]: value })
    setU({ ...u, ...updated })
  }
  const opt = (field, values) => (
    <div className="lang-switch">
      {values.map(([v, text]) => (
        <button key={v} className={u[field] === v ? 'active' : ''} onClick={() => set(field, v)}>{text}</button>
      ))}
    </div>
  )
  return (
    <div className="screen">
      <h1>⚙️ {t('settings', 'en')}</h1>
      <h3>{t('language', 'en')}</h3>
      {opt('lang', LANGS.map((l) => [l.code, l.name]))}
      <h3>{t('content_version', 'en')}</h3>
      {opt('content_version', [['localized', t('localized', 'en')], ['generic', t('generic', 'en')]])}
      <h3>{t('difficulty_mode', 'en')}</h3>
      {opt('difficulty_mode', [['adaptive', t('adaptive', 'en')], ['fixed', t('fixed', 'en')]])}
      <h3>{t('export_data', 'en')}</h3>
      <div className="row">
        {['users', 'sessions', 'attempts', 'adaptation_log'].map((tb) => (
          <a key={tb} className="button" href={`/api/export/${tb}.csv`}>{tb}.csv</a>
        ))}
      </div>
      <button className="big" onClick={() => onSaved(u)}>{t('back', 'en')}</button>
      <button className="link" onClick={onBack}>Cancel</button>
    </div>
  )
}
