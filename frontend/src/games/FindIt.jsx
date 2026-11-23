import { useEffect, useMemo, useRef, useState } from 'react'
import { label, t } from '../i18n'
import { speak } from '../speech'
import { columnsFor, Picture, sample } from './util'

// Attention game: a target picture is shown; find it among `grid_size` pictures
// before `time_limit_ms`. Every tap is an attempt; running out of time is logged
// as a wrong attempt with error_type 'timeout'. The round ends on the right tap or timeout.
export default function FindIt({ session, lang, onAttempt, onFinish }) {
  const { grid_size, time_limit_ms, rounds } = session.params
  const [round, setRound] = useState(1)
  const [wrong, setWrong] = useState(new Set())
  const [found, setFound] = useState(false)
  const lastTime = useRef(0)

  const { grid, target } = useMemo(() => {
    const g = sample(session.items, grid_size)
    return { grid: g, target: g[Math.floor(Math.random() * g.length)] }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session, round])

  const next = () => (round === rounds ? onFinish(true) : setRound((r) => r + 1))
  const timerRef = useRef(null)

  useEffect(() => {
    setWrong(new Set())
    setFound(false)
    lastTime.current = performance.now()
    timerRef.current = setTimeout(() => {
      onAttempt({ round_no: round, item_id: target.id, correct: false, response_ms: time_limit_ms, error_type: 'timeout' })
      next()
    }, time_limit_ms)
    return () => clearTimeout(timerRef.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [round])

  function tap(item) {
    if (found || wrong.has(item.id)) return
    const now = performance.now()
    const correct = item.id === target.id
    onAttempt({ round_no: round, item_id: item.id, correct, response_ms: Math.round(now - lastTime.current), error_type: correct ? null : 'wrong_item' })
    lastTime.current = now
    if (correct) {
      setFound(true)
      clearTimeout(timerRef.current)
      setTimeout(next, 800)
    } else {
      setWrong(new Set(wrong).add(item.id))
    }
  }

  return (
    <div>
      <p className="round">{t('round', lang)} {round} / {rounds}</p>
      <div className="target">
        <span>{t('find_this', lang)}</span>
        <Picture item={target} size="3.5rem" />
        <strong>{label(target, lang)}</strong>
        <button className="small" onClick={() => speak(target.label, lang)} aria-label={t('listen', lang)}>🔊</button>
      </div>
      <div className="timer" style={{ animationDuration: `${time_limit_ms}ms` }} key={round} />
      <div className="grid" style={{ gridTemplateColumns: `repeat(${columnsFor(grid.length)}, 1fr)` }}>
        {grid.map((item) => (
          <button
            key={item.id}
            className={`card up ${wrong.has(item.id) ? 'wrong' : ''} ${found && item.id === target.id ? 'right' : ''}`}
            onClick={() => tap(item)}
          >
            <Picture item={item} />
          </button>
        ))}
      </div>
    </div>
  )
}
