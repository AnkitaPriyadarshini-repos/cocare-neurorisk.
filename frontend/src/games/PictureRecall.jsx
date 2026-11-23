import { useEffect, useMemo, useRef, useState } from 'react'
import { label, t } from '../i18n'
import { columnsFor, Picture, sample, shuffle } from './util'

// Recall game: show `show_count` pictures for `display_ms`, then the user picks
// them out of `option_count` pictures. Each pick is one attempt.
// A round ends after `show_count` picks.
export default function PictureRecall({ session, lang, onAttempt, onFinish }) {
  const { show_count, option_count, display_ms, rounds } = session.params
  const [round, setRound] = useState(1)

  const { targets, options } = useMemo(() => {
    const opts = sample(session.items, option_count)
    return { targets: opts.slice(0, show_count), options: shuffle(opts) }
    // a new set of pictures each round
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session, round])

  const [phase, setPhase] = useState('show') // 'show' | 'pick'
  const [picked, setPicked] = useState({}) // item id -> true/false (correct?)
  const lastTime = useRef(0)

  useEffect(() => {
    setPhase('show')
    setPicked({})
    const id = setTimeout(() => {
      setPhase('pick')
      lastTime.current = performance.now()
    }, display_ms)
    return () => clearTimeout(id)
  }, [round, display_ms])

  function pick(item) {
    if (phase !== 'pick' || item.id in picked) return
    const now = performance.now()
    const correct = targets.some((x) => x.id === item.id)
    onAttempt({ round_no: round, item_id: item.id, correct, response_ms: Math.round(now - lastTime.current), error_type: correct ? null : 'wrong_item' })
    lastTime.current = now
    const next = { ...picked, [item.id]: correct }
    setPicked(next)
    if (Object.keys(next).length === show_count) {
      setTimeout(() => (round === rounds ? onFinish(true) : setRound(round + 1)), 1200)
    }
  }

  return (
    <div>
      <p className="round">{t('round', lang)} {round} / {rounds}</p>
      {phase === 'show' ? (
        <>
          <p className="instruction">{t('remember_these', lang)}</p>
          <div className="grid" style={{ gridTemplateColumns: `repeat(${columnsFor(show_count)}, 1fr)` }}>
            {targets.map((item) => (
              <div key={item.id} className="card up">
                <Picture item={item} size="4rem" />
                <span className="card-label">{label(item, lang)}</span>
              </div>
            ))}
          </div>
          <div className="timer" style={{ animationDuration: `${display_ms}ms` }} key={round} />
        </>
      ) : (
        <>
          <p className="instruction">{t('which_did_you_see', lang)} ({Object.keys(picked).length} / {show_count})</p>
          <div className="grid" style={{ gridTemplateColumns: `repeat(${columnsFor(options.length)}, 1fr)` }}>
            {options.map((item) => (
              <button
                key={item.id}
                className={`card up ${item.id in picked ? (picked[item.id] ? 'right' : 'wrong') : ''}`}
                onClick={() => pick(item)}
              >
                <Picture item={item} />
                <span className="card-label">{label(item, lang)}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
