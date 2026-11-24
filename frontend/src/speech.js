// Read text aloud.
// Step 8 of the plan replaces this with pre-generated Indic-TTS audio files.
// Detects available voices. If no native voice exists for the target language (e.g. Odia),
// do NOT fall back to reading with another language's voice.

export function findVoice(lang) {
  if (typeof window === 'undefined' || !window.speechSynthesis) return null
  const voices = window.speechSynthesis.getVoices() ?? []
  return voices.find((v) => v.lang?.toLowerCase().startsWith(lang)) ?? null
}

export function hasVoiceForLang(lang) {
  return Boolean(findVoice(lang))
}

export function speak(texts, lang) {
  if (typeof window === 'undefined' || !window.speechSynthesis) return
  window.speechSynthesis.cancel()

  const voice = findVoice(lang)
  // If no voice for target language, do not read with an alien voice
  if (!voice) return

  const textToRead = texts[lang] ?? texts.en
  if (!textToRead) return

  const u = new SpeechSynthesisUtterance(textToRead)
  u.voice = voice
  u.lang = lang === 'or' ? 'or-IN' : 'en-IN'
  u.rate = 0.85 // slower for elderly listeners
  window.speechSynthesis.speak(u)
}
