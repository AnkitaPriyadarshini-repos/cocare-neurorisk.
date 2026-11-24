// Frontend API client for cognitive risk screening module.
// Strictly privacy-preserving: patient profile is transmitted solely for stateless inference.
// LocalStorage history is purely opt-in on the client device.

async function request(method, path, body) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    let errMessage = `${method} ${path} failed with HTTP ${res.status}`
    try {
      const data = await res.json()
      if (data.detail) errMessage = data.detail
    } catch {}
    throw new Error(errMessage)
  }
  return res.json()
}

// Fallback form specification in case backend is offline or cold starting
export const FALLBACK_FORM_SPEC = {
  dataset: 'OASIS-demo',
  schema_version: '1.0.0',
  disclaimer:
    'This screening tool is an educational and preliminary triage demonstration based on OASIS data. It is NOT a medical diagnostic instrument. Please consult a qualified healthcare professional or neurologist.',
  fields: [
    {
      name: 'Age',
      label: 'Age (years)',
      label_or: 'ବୟସ (ବର୍ଷ) [needs native review]',
      type: 'number',
      required: true,
      min: 40,
      max: 120,
      step: 1,
      help_text: 'Participant age in complete years (40-120).',
      help_text_or: 'ଅଂଶଗ୍ରହଣକାରୀଙ୍କ ସମ୍ପୂର୍ଣ୍ଣ ବୟସ (୪୦-୧୨୦)। [needs native review]',
    },
    {
      name: 'Sex',
      label: 'Biological Sex',
      label_or: 'ଜୈବିକ ଲିଙ୍ଗ [needs native review]',
      type: 'categorical',
      required: true,
      options: [
        { value: 'F', label: 'Female', label_or: 'ମହିଳା [needs native review]' },
        { value: 'M', label: 'Male', label_or: 'ପୁରୁଷ [needs native review]' },
      ],
      help_text: 'Biological sex assigned at birth.',
      help_text_or: 'ଜନ୍ମ ସମୟର ଜୈବିକ ଲିଙ୍ଗ। [needs native review]',
    },
    {
      name: 'EDUC',
      label: 'Years of Formal Education',
      label_or: 'ଆନୁଷ୍ଠାନିକ ଶିକ୍ଷା ବର୍ଷ [needs native review]',
      type: 'number',
      required: true,
      min: 0,
      max: 30,
      step: 1,
      help_text: 'Total completed years of school and college (0-30).',
      help_text_or: 'ସ୍କୁଲ ଏବଂ କଲେଜ ଶିକ୍ଷାର ସମୁଦାୟ ବର୍ଷ (୦-୩୦)। [needs native review]',
    },
    {
      name: 'SES',
      label: 'Socioeconomic Tier (1 = Highest, 5 = Lowest)',
      label_or: 'ସାମାଜିକ-ଅର୍ଥନୈତିକ ସ୍ତର (୧ = ଉଚ୍ଚ, ୫ = ନିମ୍ନ) [needs native review]',
      type: 'integer_tier',
      required: false,
      min: 1,
      max: 5,
      step: 1,
      help_text: 'Hollingshead socioeconomic index (1: Upper, 2: Upper-Middle, 3: Middle, 4: Lower-Middle, 5: Lower). Optional.',
      help_text_or: 'ହୋଲିଙ୍ଗସହେଡ ସୂଚକାଙ୍କ (୧: ଉଚ୍ଚ, ୨: ଉଚ୍ଚ-ମଧ୍ୟମ, ୩: ମଧ୍ୟମ, ୪: ନିମ୍ନ-ମଧ୍ୟମ, ୫: ନିମ୍ନ)। ଇଚ୍ଛାଧୀନ। [needs native review]',
    },
    {
      name: 'MMSE',
      label: 'Mini-Mental State Examination Score (0-30)',
      label_or: 'ମାନସିକ ସ୍ଥିତି ପରୀକ୍ଷା ସ୍କୋର (୦-୩୦) [needs native review]',
      type: 'number',
      required: false,
      min: 0,
      max: 30,
      step: 1,
      help_text: 'Standardized 30-point cognitive examination. Provide ONLY if administered by a trained health professional.',
      help_text_or: 'ମାନକ ୩୦-ପଏଣ୍ଟ ପରୀକ୍ଷା। କେବଳ ତାଲିମପ୍ରାପ୍ତ କର୍ମୀଙ୍କ ଦ୍ୱାରା ହୋଇଥିଲେ ଦିଅନ୍ତୁ। [needs native review]',
    },
  ],
}

export const riskApi = {
  // 1. Fetch intake form specification
  getFormSpec: async () => {
    try {
      return await request('GET', '/risk/form-spec')
    } catch (err) {
      console.warn('Using fallback form specification due to network error:', err)
      return FALLBACK_FORM_SPEC
    }
  },

  // 2. Stateless assessment prediction
  predictRisk: async (profile, useMmse = false) => {
    return await request('POST', '/risk/predict', { profile, use_mmse: useMmse })
  },

  // 3. Model metadata and diagnostics
  getModelInfo: async () => {
    return await request('GET', '/risk/model-info')
  },

  // 4. Opt-in local-only screening history helpers (LocalStorage)
  getLocalHistory: (userId) => {
    if (!userId) return []
    try {
      const raw = localStorage.getItem(`cocare_risk_history_${userId}`)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  },

  saveLocalResult: (userId, record) => {
    if (!userId) return
    try {
      const history = riskApi.getLocalHistory(userId)
      const updated = [record, ...history].slice(0, 30) // keep last 30 assessments
      localStorage.setItem(`cocare_risk_history_${userId}`, JSON.stringify(updated))
    } catch (e) {
      console.error('Failed to save assessment to localStorage:', e)
    }
  },

  deleteLocalHistory: (userId) => {
    if (!userId) return
    try {
      localStorage.removeItem(`cocare_risk_history_${userId}`)
    } catch (e) {
      console.error('Failed to clear localStorage assessment history:', e)
    }
  },

  isOptedInHistory: (userId) => {
    if (!userId) return false
    try {
      return localStorage.getItem(`cocare_risk_optin_${userId}`) === 'true'
    } catch {
      return false
    }
  },

  setOptInHistory: (userId, enabled) => {
    if (!userId) return
    try {
      localStorage.setItem(`cocare_risk_optin_${userId}`, enabled ? 'true' : 'false')
      if (!enabled) {
        riskApi.deleteLocalHistory(userId)
      }
    } catch (e) {
      console.error('Failed to update opt-in preference:', e)
    }
  },
}
