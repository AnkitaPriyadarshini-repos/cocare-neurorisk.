// Read text aloud.
// Step 8 of the plan replaces this with pre-generated Indic-TTS audio files
// (public/audio/<lang>/<key>.mp3). Until then we use the browser's built-in voices.
// Many computers have no Odia voice, so if none is found we read the English text
// instead of letting an English voice mispronounce Odia script.

function findVoice(lang) {
  const voices = window.speechSynthesis?.getVoices() ?? []
  return voices.find((v) => v.lang?.toLowerCase().startsWith(lang))
}

export function speak(texts, lang) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  let useLang = lang
  let voice = findVoice(lang === 'or' ? 'or' : 'en')
  if (!voice && lang === 'or') {
    useLang = 'en'
    voice = findVoice('en')
  }
  const u = new SpeechSynthesisUtterance(texts[useLang] ?? texts.en)
  if (voice) u.voice = voice
  u.lang = useLang === 'or' ? 'or-IN' : 'en-IN'
  u.rate = 0.85 // slower for elderly listeners
  window.speechSynthesis.speak(u)
}
