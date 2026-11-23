import { useEffect, useMemo, useRef, useState } from 'react'
import { label, t } from '../i18n'
import { columnsFor, Picture, sample, shuffle } from './util'

// Memory game: all cards are shown face-up for preview_ms, then turned over.
// Each pair of flips is one attempt (correct = the two cards match).
export default function MemoryMatch({ session, lang, onAttempt, onFinish }) {
  const { pairs, preview_ms } = session.params
  const deck = useMemo(() => {
    const chosen = sample(session.items, pairs)
    return shuffle([...chosen, ...chosen].map((item, i) => ({ key: i, item })))
  }, [session])

  const [previewing, setPreviewing] = useState(true)
  const [open, setOpen] = useState([]) // indexes currently face-up (max 2)
  const [matched, setMatched] = useState(new Set())
  const lastTime = useRef(0)

  useEffect(() => {
    const id = setTimeout(() => {
      setPreviewing(false)
      lastTime.current = performance.now()
    }, preview_ms)
    return () => clearTimeout(id)
  }, [preview_ms])

  function flip(i) {
    if (previewing || open.length === 2 || open.includes(i) || matched.has(deck[i].item.id)) return
    const next = [...open, i]
    setOpen(next)
    if (next.length < 2) return

    const [a, b] = next.map((k) => deck[k].item)
    const now = performance.now()
    const correct = a.id === b.id
    onAttempt({ item_id: a.id, correct, response_ms: Math.round(now - lastTime.current), error_type: correct ? null : 'mismatch' })
    lastTime.current = now

    setTimeout(() => {
      if (correct) {
        const m = new Set(matched).add(a.id)
        setMatched(m)
        if (m.size === pairs) onFinish(true)
      }
      setOpen([])
      lastTime.current = performance.now()
    }, correct ? 500 : 1100)
  }

  return (
    <div>
      <p className="instruction">{previewing ? t('memory_match_help', lang) : t('memory_match', lang)}</p>
      <div className="grid" style={{ gridTemplateColumns: `repeat(${columnsFor(deck.length)}, 1fr)` }}>
        {deck.map(({ key, item }, i) => {
          const faceUp = previewing || open.includes(i) || matched.has(item.id)
          return (
            <button
              key={key}
              className={`card ${faceUp ? 'up' : 'down'} ${matched.has(item.id) ? 'matched' : ''}`}
              onClick={() => flip(i)}
              aria-label={faceUp ? label(item, lang) : '?'}
            >
              {faceUp ? (
                <>
                  <Picture item={item} />
                  <span className="card-label">{label(item, lang)}</span>
                </>
              ) : (
                <span className="card-back">?</span>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
