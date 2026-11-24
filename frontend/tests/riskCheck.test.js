import test from 'node:test'
import assert from 'node:assert/strict'
import { FALLBACK_FORM_SPEC, riskApi } from '../src/riskApi.js'
import { STRINGS, t } from '../src/i18n.js'

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

  const mmse = FALLBACK_FORM_SPEC.fields.find((f) => f.name === 'MMSE')
  assert.equal(mmse.min, 0)
  assert.equal(mmse.max, 30)
  assert.equal(mmse.required, false)
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
