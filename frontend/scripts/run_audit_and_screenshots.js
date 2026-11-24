import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const distDir = path.resolve(__dirname, '../dist')
const outputDir = path.resolve(__dirname, '../../docs/showcase/ui')

fs.mkdirSync(outputDir, { recursive: true })

// MIME types for simple static server
const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
}

function startStaticServer(port = 4173) {
  const server = http.createServer((req, res) => {
    let reqPath = req.url.split('?')[0]
    if (reqPath === '/' || reqPath === '') reqPath = '/index.html'

    let filePath = path.join(distDir, reqPath)
    if (!fs.existsSync(filePath)) {
      filePath = path.join(distDir, 'index.html') // SPA fallback
    }

    const ext = path.extname(filePath).toLowerCase()
    const contentType = MIME_TYPES[ext] || 'application/octet-stream'

    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(500)
        res.end('Error loading file')
        return
      }
      res.writeHead(200, { 'Content-Type': contentType })
      res.end(data)
    })
  })

  return new Promise((resolve) => {
    server.listen(port, '127.0.0.1', () => {
      console.log(`[Static Server] Serving dist on http://127.0.0.1:${port}`)
      resolve(server)
    })
  })
}

// Axe-core file path
const axePath = path.resolve(__dirname, '../node_modules/axe-core/axe.min.js')
const axeSource = fs.readFileSync(axePath, 'utf8')

async function runAudit(page, screenName) {
  await page.evaluate(axeSource)
  const results = await page.evaluate(async () => {
    return await window.axe.run(document, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'best-practice'],
      },
    })
  })

  const passes = results.passes.length
  const violations = results.violations.length
  const score = Math.round((passes / (passes + violations || 1)) * 100)

  console.log(`[Axe A11y] Screen: ${screenName} -> Passes: ${passes}, Violations: ${violations}, Score: ${score}%`)
  if (violations > 0) {
    console.log(`[Axe Violations on ${screenName}]:`)
    for (const v of results.violations) {
      console.log(`  - [${v.impact}] ${v.id}: ${v.help} (${v.nodes.length} occurrences)`)
    }
  }

  return { screenName, passes, violations, score, details: results.violations }
}

async function main() {
  const server = await startStaticServer(4173)

  const browser = await chromium.launch({
    headless: true,
  })

  const mockUsers = [
    { id: 'u_or', name: 'ଅନିତା ଦାସ', age: 68, lang: 'or', levels: { memory_match: 2, picture_recall: 1, find_it: 3 } },
    { id: 'u_en', name: 'Anita Rao', age: 68, lang: 'en', levels: { memory_match: 2, picture_recall: 1, find_it: 3 } },
  ]

  const mockSessions = [
    { id: 1, game: 'memory_match', accuracy: 0.85, old_level: 1, new_level: 2, completed: true, started_at: '2026-11-20T10:00:00Z' },
    { id: 2, game: 'picture_recall', accuracy: 0.75, old_level: 1, new_level: 1, completed: true, started_at: '2026-11-21T10:00:00Z' },
    { id: 3, game: 'find_it', accuracy: 0.90, old_level: 2, new_level: 3, completed: true, started_at: '2026-11-22T10:00:00Z' },
    { id: 4, game: 'memory_match', accuracy: 0.80, old_level: 2, new_level: 2, completed: true, started_at: '2026-11-23T10:00:00Z' },
    { id: 5, game: 'picture_recall', accuracy: 0.95, old_level: 1, new_level: 2, completed: true, started_at: '2026-11-24T10:00:00Z' },
  ]

  const auditReport = []

  // Capture for both languages and both viewports
  for (const lang of ['or', 'en']) {
    const isOdia = lang === 'or'
    const currentUser = mockUsers.find((u) => u.lang === lang)

    for (const vp of [
      { name: 'mobile', width: 360, height: 780 },
      { name: 'desktop', width: 1280, height: 850 },
    ]) {
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        locale: isOdia ? 'or-IN' : 'en-US',
      })

      const page = await context.newPage()

      // Route mock API calls
      await page.route('**/api/**', async (route) => {
        const url = route.request().url()
        const method = route.request().method()

        if (url.includes('/api/users') && method === 'GET') {
          return route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([currentUser]),
          })
        }
        if (url.includes('/api/users/') && method === 'GET') {
          return route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(currentUser),
          })
        }
        if (url.includes('/api/risk/form-spec')) {
          return route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              dataset: 'OASIS-demo',
              schema_version: '1.0.0',
              disclaimer: 'OASIS preliminary screening demo',
              fields: [
                { name: 'Age', label: 'Age (years)', label_or: 'ବୟସ (ବର୍ଷ) [needs native review]', type: 'number', required: true, min: 40, max: 120, step: 1 },
                { name: 'Sex', label: 'Biological Sex', label_or: 'ଜୈବିକ ଲିଙ୍ଗ [needs native review]', type: 'categorical', required: true, options: [{ value: 'F', label: 'Female', label_or: 'ମହିଳା [needs native review]' }, { value: 'M', label: 'Male', label_or: 'ପୁରୁଷ [needs native review]' }] },
                { name: 'EDUC', label: 'Years of Formal Education', label_or: 'ଆନୁଷ୍ଠାନିକ ଶିକ୍ଷା ବର୍ଷ [needs native review]', type: 'number', required: true, min: 0, max: 30, step: 1 },
                { name: 'SES', label: 'Socioeconomic Tier', label_or: 'ସାମାଜିକ-ଅର୍ଥନୈତିକ ସ୍ତର [needs native review]', type: 'integer_tier', required: false, min: 1, max: 5 },
                { name: 'MMSE', label: 'MMSE Score (0-30)', label_or: 'ମାନସିକ ସ୍ଥିତି ପରୀକ୍ଷା (୦-୩୦) [needs native review]', type: 'number', required: false, min: 0, max: 30 },
              ],
            }),
          })
        }
        if (url.includes('/api/risk/predict')) {
          return route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              probability: 0.2854,
              band: 'lower',
              threshold: 0.3301,
              model_variant: 'without_mmse',
              score_note: 'Model score calibrated to OASIS sample prevalence of 48.5%',
              disclaimer: 'This screening tool is an educational and preliminary triage demonstration based on OASIS data. It is NOT a medical diagnostic instrument.',
              explanation: [
                { feature: 'EDUC', value: 14, effect: 'lowers', magnitude: 0.032, text_en: '14 years education lowers score by 0.032 relative to typical training-data values', text_or: '୧୪ ବର୍ଷର ଶିକ୍ଷା ସ୍କୋର ୦.୦୩୨ କମାଇଛି [needs native review]' },
                { feature: 'Sex', value: 'F', effect: 'lowers', magnitude: 0.018, text_en: 'Female sex lowers score by 0.018 relative to typical training-data values', text_or: 'ମହିଳା ଲିଙ୍ଗ ସ୍କୋର ୦.୦୧୮ କମାଇଛି [needs native review]' },
              ],
            }),
          })
        }
        if (url.includes('/api/history/')) {
          return route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ sessions: mockSessions }),
          })
        }

        return route.continue()
      })

      // 1. Load Welcome screen & select user
      await page.goto('http://127.0.0.1:4173')
      await page.waitForLoadState('networkidle')

      // Click on existing user to go to Home
      const userBtn = page.locator('button.big').first()
      await userBtn.click()
      await page.waitForTimeout(300)

      // 2. Click "Risk Check" on Home
      const riskBtn = page.locator('button', { hasText: '🩺' })
      await riskBtn.click()
      await page.waitForTimeout(400)

      // Screen 1: Risk Check Wizard
      const wizardImgPath = path.join(outputDir, `risk_wizard_${vp.name}_${lang}.png`)
      await page.screenshot({ path: wizardImgPath, fullPage: true })
      console.log(`Saved screenshot: ${wizardImgPath}`)

      if (vp.name === 'mobile' && lang === 'or') {
        const audit = await runAudit(page, 'RiskCheckWizard (Mobile 360px)')
        auditReport.push(audit)
      }

      // Step through wizard:
      // Step 1 (Age) -> Next
      await page.locator('button', { hasText: '→' }).click()
      await page.waitForTimeout(200)

      // Step 2 (Sex) -> Next
      await page.locator('button', { hasText: '→' }).click()
      await page.waitForTimeout(200)

      // Step 3 (EDUC) -> Next
      await page.locator('button', { hasText: '→' }).click()
      await page.waitForTimeout(200)

      // Step 4 (SES) -> Next
      await page.locator('button', { hasText: '→' }).click()
      await page.waitForTimeout(200)

      // Step 5 (MMSE) -> Submit
      const submitBtn = page.locator('button.primary').last()
      await submitBtn.click()
      await page.waitForTimeout(500)

      // Screen 2: Risk Check Result
      const resultImgPath = path.join(outputDir, `risk_result_${vp.name}_${lang}.png`)
      await page.screenshot({ path: resultImgPath, fullPage: true })
      console.log(`Saved screenshot: ${resultImgPath}`)

      if (vp.name === 'mobile' && lang === 'or') {
        const audit = await runAudit(page, 'RiskCheckResult (Mobile 360px)')
        auditReport.push(audit)
      }

      // 3. Click "My Progress" from Result
      const progressBtn = page.locator('button', { hasText: '📈' }).first()
      await progressBtn.click()
      await page.waitForTimeout(500)

      // Screen 3: My Progress Dashboard
      const progressImgPath = path.join(outputDir, `my_progress_${vp.name}_${lang}.png`)
      await page.screenshot({ path: progressImgPath, fullPage: true })
      console.log(`Saved screenshot: ${progressImgPath}`)

      if (vp.name === 'mobile' && lang === 'or') {
        const audit = await runAudit(page, 'MyProgress (Mobile 360px)')
        auditReport.push(audit)
      }

      await context.close()
    }
  }

  await browser.close()
  server.close()

  console.log('\n--- ACCESSIBILITY AUDIT SUMMARY ---')
  for (const r of auditReport) {
    console.log(`${r.screenName}: Score ${r.score}% (${r.passes} passed, ${r.violations} violations)`)
  }

  // Save audit report JSON
  fs.writeFileSync(
    path.join(outputDir, 'accessibility_audit.json'),
    JSON.stringify(auditReport, null, 2),
    'utf8'
  )
}

main().catch((err) => {
  console.error('Error running audit and screenshot capture:', err)
  process.exit(1)
})
