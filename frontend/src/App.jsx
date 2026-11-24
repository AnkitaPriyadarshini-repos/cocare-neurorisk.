import { useRef, useState } from 'react'
import { api } from './api'
import FindIt from './games/FindIt'
import MemoryMatch from './games/MemoryMatch'
import PictureRecall from './games/PictureRecall'
import { t } from './i18n'
import { isRiskCheckEnabled } from './riskApi'
import MyProgress from './screens/MyProgress'
import RiskCheckResult from './screens/RiskCheckResult'
import RiskCheckWizard from './screens/RiskCheckWizard'
import { History, Home, Result, Settings } from './screens/Screens'
import Welcome from './screens/Welcome'

const GAME_COMPONENTS = { memory_match: MemoryMatch, picture_recall: PictureRecall, find_it: FindIt }

export default function App() {
  const [user, setUser] = useState(null)
  const [screen, setScreen] = useState('welcome')
  const [session, setSession] = useState(null)
  const [result, setResult] = useState(null)
  const [riskData, setRiskData] = useState(null)
  const [error, setError] = useState('')
  const pending = useRef(Promise.resolve()) // keeps attempt logging in order

  const lang = user?.lang ?? 'or'

  async function refreshUser(id) {
    const u = await api.getUser(id)
    setUser(u)
    return u
  }

  async function selectUser(u) {
    await refreshUser(u.id)
    setScreen('home')
  }

  async function play(game) {
    try {
      setError('')
      const s = await api.startSession(user.id, game)
      pending.current = Promise.resolve()
      setSession(s)
      setScreen('play')
    } catch {
      setError(t('error_server', lang))
    }
  }

  function onAttempt(a) {
    const sid = session.session_id
    pending.current = pending.current.then(() => api.logAttempt(sid, a)).catch(() => {})
  }

  async function onFinish(completed) {
    const sid = session.session_id
    await pending.current
    const r = await api.endSession(sid, completed)
    setResult(r)
    await refreshUser(user.id)
    setScreen('result')
  }

  let body
  if (screen === 'welcome') body = <Welcome onSelect={selectUser} />
  else if (screen === 'home')
    body = (
      <Home
        user={user}
        onPlay={play}
        onHistory={() => setScreen('history')}
        onSettings={() => setScreen('settings')}
        onSwitch={() => { setUser(null); setScreen('welcome') }}
        onRiskCheck={() => setScreen('risk_check')}
        onProgress={() => setScreen('progress')}
      />
    )
  else if (screen === 'risk_check' && isRiskCheckEnabled())
    body = (
      <RiskCheckWizard
        user={user}
        onComplete={(res, prof, mmse) => {
          setRiskData({ result: res, profile: prof, useMmse: mmse })
          setScreen('risk_result')
        }}
        onCancel={() => setScreen('home')}
      />
    )
  else if (screen === 'risk_result' && isRiskCheckEnabled())
    body = (
      <RiskCheckResult
        user={user}
        result={riskData?.result}
        profile={riskData?.profile}
        useMmse={riskData?.useMmse}
        onRetake={() => setScreen('risk_check')}
        onViewProgress={() => setScreen('progress')}
        onHome={() => setScreen('home')}
      />
    )
  else if (screen === 'progress' && isRiskCheckEnabled())
    body = (
      <MyProgress
        user={user}
        onRiskCheck={() => setScreen('risk_check')}
        onBack={() => setScreen('home')}
      />
    )
  else if (screen === 'play') {
    const Game = GAME_COMPONENTS[session.game]
    body = (
      <div className="screen">
        <div className="topbar">
          <span>{t(session.game, lang)} · {t('level', lang)} {session.level}</span>
          <button className="small" onClick={() => onFinish(false)}>✋ {t('stop', lang)}</button>
        </div>
        <Game key={session.session_id} session={session} lang={lang} onAttempt={onAttempt} onFinish={onFinish} />
      </div>
    )
  } else if (screen === 'result')
    body = <Result user={user} result={result} game={session.game} onAgain={play} onHome={() => setScreen('home')} />
  else if (screen === 'history') body = <History user={user} onBack={() => setScreen('home')} />
  else if (screen === 'settings')
    body = (
      <Settings
        user={user}
        onSaved={async () => { await refreshUser(user.id); setScreen('home') }}
        onBack={() => setScreen('home')}
      />
    )

  return (
    <main lang={lang}>
      {error && <p className="error">{error}</p>}
      {body}
    </main>
  )
}
