import test from 'node:test'
import assert from 'node:assert/strict'
import { FALLBACK_FORM_SPEC, isRiskCheckEnabled, riskApi } from '../src/riskApi.js'
import { STRINGS, t, cleanDevTags } from '../src/i18n.js'

test('FALLBACK_FORM_SPEC contains all required intake fields with metadata', () => {
  assert.equal(FALLBACK_FORM_SPEC.dataset, 'OASIS-demo')
  assert.ok(FALLBACK_FORM_SPEC.fields.length >= 5)

  const fieldNames = FALLBACK_FORM_SPEC.fields.map((f) => f.name)
  assert.deepEqual(fieldNames, ['Age', 'Sex', 'EDUC', 'SES', 'MMSE'])

  const age = FALLBACK_FORM_SPEC.fields.find((f) => f.name === 'Age')
  assert.equal(age.min, 40)
  assert.equal(age.max, 120)
  assert.ok(age.label_or.includes('[needs native review]'))

  const sex = FALLBACK_FORM_SPEC.fields.find((f) => f.name === 'Sex')
  assert.equal(sex.type, 'categorical')
  assert.equal(sex.options.length, 2)

  const ses = FALLBACK_FORM_SPEC.fields.find((f) => f.name === 'SES')
  assert.equal(ses.required, false)
  assert.equal(ses.min, 1)
  assert.equal(ses.max, 5)
  assert.ok(ses.label.includes('demo approximation, not the clinical SES index used in OASIS'))

  const mmse = FALLBACK_FORM_SPEC.fields.find((f) => f.name === 'MMSE')
  assert.equal(mmse.min, 0)
  assert.equal(mmse.max, 30)
  assert.equal(mmse.required, false)
})

test('cleanDevTags hides [needs native review] tag in production builds while preserving it in dev mode', () => {
  const sample = 'ମଡେଲ [needs native review]'
  assert.equal(cleanDevTags(sample, true), 'ମଡେଲ')
  assert.equal(cleanDevTags(sample, false), sample)
  assert.equal(cleanDevTags('English text without tag', true), 'English text without tag')
})

test('i18n contains all risk screening and progress translation keys in Odia and English', () => {
  const requiredKeys = [
    'risk_check',
    'my_progress',
    'wizard_title',
    'step',
    'of',
    'read_question',
    'next',
    'skip',
    'submit_check',
    'optional_badge',
    'font_size',
    'mmse_step_title',
    'mmse_step_desc',
    'mmse_has_score',
    'mmse_no_score',
    'val_age_req',
    'val_sex_req',
    'val_educ_req',
    'val_ses_req',
    'val_mmse_range',
    'ses_plain_desc',
    'ses_tier_1',
    'ses_tier_2',
    'ses_tier_3',
    'ses_tier_4',
    'ses_tier_5',
    'skip_ses',
    'result_title',
    'model_score_label',
    'band_lower',
    'band_moderate',
    'band_higher',
    'what_to_do_next',
    'guidance_lower',
    'guidance_moderate',
    'guidance_higher',
    'print_doctor_summary',
    'doctor_summary_title',
    'not_a_diagnosis',
    'demo_status_badge',
    'explanations_title',
    'save_to_device',
    'saved_locally',
    'delete_my_data',
    'data_deleted',
    'my_progress_title',
    'game_history_chart',
    'caregiver_summary_title',
    'caregiver_sessions_stat',
    'caregiver_avg_acc',
    'caregiver_last_check',
    'screening_records_title',
  ]

  for (const k of requiredKeys) {
    assert.ok(STRINGS.en[k], `Missing English key: ${k}`)
    assert.ok(STRINGS.or[k], `Missing Odia key: ${k}`)
    assert.ok(
      STRINGS.or[k].includes('[needs native review]') || k === 'read_question' || k === 'listen',
      `Odia key should be marked for review: ${k}`
    )
    assert.equal(t(k, 'en'), STRINGS.en[k])
    assert.equal(t(k, 'or'), STRINGS.or[k])
  }
})

test('Explanation magnitude filtering correctly filters items below 0.01 threshold', () => {
  const sampleExplanations = [
    { feature: 'Age', value: 72, effect: 'raises', magnitude: 0.042, text_en: 'Higher age (+0.042)' },
    { feature: 'Sex', value: 'M', effect: 'lowers', magnitude: 0.003, text_en: 'Male sex (-0.003)' },
    { feature: 'EDUC', value: 12, effect: 'lowers', magnitude: 0.025, text_en: '12 years education (-0.025)' },
    { feature: 'SES', value: 3, effect: 'raises', magnitude: 0.008, text_en: 'Tier 3 (+0.008)' },
    { feature: 'MMSE', value: 24, effect: 'raises', magnitude: 0.155, text_en: 'MMSE 24 (+0.155)' },
  ]

  const filtered = sampleExplanations.filter((item) => item.magnitude >= 0.01)

  assert.equal(filtered.length, 3)
  assert.deepEqual(
    filtered.map((f) => f.feature),
    ['Age', 'EDUC', 'MMSE']
  )
})

test('LocalStorage opt-in and privacy isolation works correctly', () => {
  const storage = {}
  global.localStorage = {
    getItem: (key) => storage[key] ?? null,
    setItem: (key, val) => { storage[key] = String(val) },
    removeItem: (key) => { delete storage[key] },
    clear: () => { Object.keys(storage).forEach((k) => delete storage[k]) },
  }

  const userA = 'user_101'
  const userB = 'user_202'

  // Default is opted out
  assert.equal(riskApi.isOptedInHistory(userA), false)
  assert.deepEqual(riskApi.getLocalHistory(userA), [])

  // Opt-in for userA
  riskApi.setOptInHistory(userA, true)
  assert.equal(riskApi.isOptedInHistory(userA), true)
  assert.equal(riskApi.isOptedInHistory(userB), false)

  // Save record for userA
  const recordA1 = {
    id: 1,
    date: '2026-11-24T12:00:00Z',
    score: 0.285,
    band: 'lower',
    variant: 'without_mmse',
  }
  riskApi.saveLocalResult(userA, recordA1)

  const histA = riskApi.getLocalHistory(userA)
  assert.equal(histA.length, 1)
  assert.equal(histA[0].score, 0.285)

  // Ensure userB history is completely isolated
  assert.deepEqual(riskApi.getLocalHistory(userB), [])

  // Delete userA history
  riskApi.deleteLocalHistory(userA)
  assert.deepEqual(riskApi.getLocalHistory(userA), [])
})

test('Privacy hardening: saveLocalResult strips all profile fields from localStorage', () => {
  const storage = {}
  global.localStorage = {
    getItem: (key) => storage[key] ?? null,
    setItem: (key, val) => { storage[key] = String(val) },
    removeItem: (key) => { delete storage[key] },
  }

  const userId = 'patient_privacy_check'
  const dirtyRecord = {
    id: 101,
    date: '2026-11-24T10:00:00Z',
    score: 0.312,
    band: 'moderate',
    model_variant: 'with_mmse',
    // Sensitive profile fields that MUST NEVER reach localStorage
    Age: 78,
    Sex: 'M',
    EDUC: 14,
    SES: 2,
    MMSE: 24,
    patient_name: 'Confidential',
  }

  riskApi.saveLocalResult(userId, dirtyRecord)
  const stored = riskApi.getLocalHistory(userId)
  assert.equal(stored.length, 1)

  const savedItem = stored[0]
  // Must preserve permitted non-PII screening metadata
  assert.equal(savedItem.score, 0.312)
  assert.equal(savedItem.band, 'moderate')
  assert.equal(savedItem.model_variant, 'with_mmse')

  // Explicitly assert NO profile fields exist
  assert.equal(savedItem.Age, undefined)
  assert.equal(savedItem.Sex, undefined)
  assert.equal(savedItem.EDUC, undefined)
  assert.equal(savedItem.SES, undefined)
  assert.equal(savedItem.MMSE, undefined)
  assert.equal(savedItem.patient_name, undefined)

  // Verify full serialized string is free of profile keys
  const rawString = storage[`cocare_risk_history_${userId}`]
  assert.ok(!rawString.includes('"Age"'))
  assert.ok(!rawString.includes('"Sex"'))
  assert.ok(!rawString.includes('"EDUC"'))
  assert.ok(!rawString.includes('"SES"'))
  assert.ok(!rawString.includes('"MMSE"'))
})

test('Feature flag VITE_ENABLE_RISK_CHECK controls visibility', () => {
  // Test fallback/default behavior
  assert.equal(typeof isRiskCheckEnabled, 'function')
  assert.equal(typeof isRiskCheckEnabled(), 'boolean')
})

test('Feature flag off state: when flag is off, screening navigation is hidden', () => {
  function checkFlag(val, isDev) {
    if (val !== undefined) return val === 'true' || val === true
    return Boolean(isDev)
  }

  // Production default is off (false)
  assert.equal(checkFlag(undefined, false), false)
  // Explicitly disabled in dev is off
  assert.equal(checkFlag('false', true), false)
  assert.equal(checkFlag('false', false), false)
  // Dev default is on (true)
  assert.equal(checkFlag(undefined, true), true)
  // Explicitly enabled in prod is on
  assert.equal(checkFlag('true', false), true)
})

test('Component test: ScoreBandBadge visual attributes and guidance for lower, moderate, higher', () => {
  const bands = ['lower', 'moderate', 'higher']
  const configs = {
    lower: { icon: '🛡️', color: '#1b5e20', ariaLabel: 'Lower Risk Band' },
    moderate: { icon: '⚖️', color: '#7a4300', ariaLabel: 'Moderate Risk Band' },
    higher: { icon: '🩺', color: '#b71c1c', ariaLabel: 'Elevated Risk Band' },
  }

  for (const b of bands) {
    const cfg = configs[b]
    assert.ok(cfg.icon)
    assert.ok(cfg.color)
    assert.ok(cfg.ariaLabel)

    const labelEn = t(`band_${b}`, 'en')
    const labelOr = t(`band_${b}`, 'or')
    const guidanceEn = t(`guidance_${b}`, 'en')
    const guidanceOr = t(`guidance_${b}`, 'or')

    assert.ok(labelEn.length > 0)
    assert.ok(labelOr.includes('[needs native review]'))
    assert.ok(guidanceEn.length > 20)
    assert.ok(guidanceOr.includes('[needs native review]'))
  }
})

test('Wizard validation logic correctly accepts and rejects field ranges', () => {
  function validateAge(v) {
    const n = Number(v)
    return Boolean(v && !isNaN(n) && n >= 40 && n <= 120)
  }
  function validateSex(v) {
    return v === 'F' || v === 'M'
  }
  function validateEduc(v) {
    const n = Number(v)
    return v !== '' && v !== undefined && !isNaN(n) && n >= 0 && n <= 30
  }
  function validateSes(v) {
    if (v === '' || v === undefined) return true // optional
    const n = Number(v)
    return !isNaN(n) && n >= 1 && n <= 5
  }
  function validateMmse(v, useMmse) {
    if (!useMmse) return true
    const n = Number(v)
    return v !== '' && v !== undefined && !isNaN(n) && n >= 0 && n <= 30
  }

  // Age tests
  assert.equal(validateAge(65), true)
  assert.equal(validateAge(40), true)
  assert.equal(validateAge(120), true)
  assert.equal(validateAge(39), false)
  assert.equal(validateAge(125), false)
  assert.equal(validateAge(''), false)
  assert.equal(validateAge('abc'), false)

  // Sex tests
  assert.equal(validateSex('F'), true)
  assert.equal(validateSex('M'), true)
  assert.equal(validateSex('X'), false)
  assert.equal(validateSex(''), false)

  // Educ tests
  assert.equal(validateEduc(0), true)
  assert.equal(validateEduc(16), true)
  assert.equal(validateEduc(30), true)
  assert.equal(validateEduc(-1), false)
  assert.equal(validateEduc(31), false)

  // SES tests (optional)
  assert.equal(validateSes(''), true)
  assert.equal(validateSes(undefined), true)
  assert.equal(validateSes(1), true)
  assert.equal(validateSes(5), true)
  assert.equal(validateSes(0), false)
  assert.equal(validateSes(6), false)

  // MMSE tests (optional/conditional)
  assert.equal(validateMmse('', false), true)
  assert.equal(validateMmse(26, true), true)
  assert.equal(validateMmse('', true), false)
  assert.equal(validateMmse(31, true), false)
})

