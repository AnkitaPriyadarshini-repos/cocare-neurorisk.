export function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

export const sample = (arr, n) => shuffle(arr).slice(0, n)

export function Picture({ item, size = '3.2rem' }) {
  return item.image ? (
    <img src={item.image} alt="" style={{ width: size, height: size, objectFit: 'contain' }} />
  ) : (
    <span style={{ fontSize: size, lineHeight: 1 }} aria-hidden="true">{item.emoji}</span>
  )
}

// Columns that keep cards large on a phone.
export const columnsFor = (n) => (n <= 4 ? 2 : n <= 9 ? 3 : 4)
