# CO CARE

AI-assisted, culturally adapted cognitive games for elderly users.
Primary language: **Odia** · Fallback: **English**

This is the Minor-phase build: an elderly-friendly web app with 3 games, Odia-localized and generic content, session logging, and a transparent rule-based adaptive difficulty engine.

## Run it (Windows)

**Only Python is needed to run the app.** The frontend is already built into `frontend/dist`.

1. Double-click `start.bat`. The first run installs the Python packages.
2. Open http://localhost:8000 in a browser.
3. To try it on a phone, connect the phone to the same Wi-Fi and open `http://<your-PC-IP>:8000`.

You can also run it by hand:

```
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## Editing the frontend (needs Node.js 20+)

```
cd frontend
npm install
npm run dev        # live-reload dev server on http://localhost:5173 (keep the backend running too)
npm run build      # rebuild frontend/dist so the backend serves your changes
```

## Run the tests

```
cd backend
pip install pytest httpx
python -m pytest -q
```

## Project structure

```
backend/
  app/main.py        API routes (users, sessions, attempts, history, CSV export)
  app/adaptive.py    Adaptive difficulty rules + level settings per game   <- core research logic
  app/db.py          SQLite schema (users, user_levels, sessions, attempts, adaptation_log)
  app/content.py     Loads game content
  content/items_localized.json   Odia cultural items (study condition A)
  content/items_generic.json     Generic items        (study condition B)
  tests/test_api.py
frontend/
  src/App.jsx        Screen flow and API calls
  src/games/         MemoryMatch, PictureRecall, FindIt
  src/screens/       Welcome (consent), Home, Result, History, Settings
  src/i18n.js        Odia + English UI text (English is used when an Odia string is missing)
  src/speech.js      Read-aloud (browser voice for now; Indic-TTS audio in step 8)
```

## The three games

| Game | Skill | What gets harder with level (1 to 5) |
|---|---|---|
| Match the Pairs (ଯୋଡ଼ି ମିଳାନ୍ତୁ) | Memory | 3 to 8 pairs; preview 5 s to 2 s |
| Remember the Pictures (ଛବି ମନେ ରଖନ୍ତୁ) | Recall | 2 to 6 pictures to remember among 4 to 12 options |
| Find It (ଖୋଜି ବାହାର କରନ୍ତୁ) | Attention | Grid of 4 to 16; time limit 15 s to 8 s |

## Adaptive rules (`backend/app/adaptive.py`)

The rules are checked at the end of every game. The first rule that matches decides the result.

| Rule | Condition | Effect |
|---|---|---|
| R0_FIXED_MODE | User is in the fixed-difficulty condition | No change |
| R1_ABANDONED | Game stopped before finishing | Level −1 |
| R2_LOW_ACCURACY | Accuracy < down threshold (40% memory, 50% others) | Level −1 |
| R3_STRUGGLING | Accuracy < 70% **and** median response > 1.5 × target time | Level −1 |
| R4_HIGH_PERFORMANCE | Accuracy ≥ up threshold (70% memory, 85% others) **and** median response ≤ target time | Level +1 |
| R5_KEEP | Anything else | No change |

Every decision is saved in `adaptation_log` with the rule name, the reason and the numbers behind it.

## Study conditions

Set them per player in **Caregiver / researcher settings** on the home screen:
- **Content:** Odia (localized) or Generic. Tests research question 1.
- **Difficulty:** Adaptive or Fixed. Tests research question 2.

The same screen has CSV downloads of all tables for the analysis.

## Before the user study (TODO)

- [ ] A native Odia speaker checks all Odia text (`src/i18n.js` and `content/*.json`).
- [ ] Replace approximate emoji with real photos for items marked `"needs_photo": true` (e.g. pakhala, rasagola, chhena poda, Sambalpuri saree). Put images in `frontend/public/images/` and set `"image": "/images/<file>.jpg"`.
- [ ] Step 8: generate Odia audio with Indic-TTS and play it from `speech.js`.
- [ ] Ethics approval and printed consent form.

## Risk screening (ML)

A preliminary dementia and cognitive-risk screening aid trained on the OASIS cohort (practised first on OASIS, with adapter readiness for LASI-DAD when authorized data and codebook are provided).

> **Disclaimer**: This screening tool is strictly a preliminary risk screening aid for community and primary care workflows. It is **NOT a clinical diagnosis** and must never replace comprehensive neuropsychological or neurological evaluation by a qualified medical professional.

### Two Model Variants
- **`model_without_mmse`**: Designed for rapid community intake. Uses only self-reportable demographic variables that an older adult or caregiver can provide without clinical test administration:
  - `Age` (years, 40–120)
  - `Sex` (M/F)
  - `EDUC` (years of formal education, 0–30)
  - `SES` (socioeconomic status scale 1–5, optional with automatic imputation)
  - *Metrics on held-out test*: Sensitivity = 90.5% (95% CI: [75.0%, 100.0%]), ROC-AUC = 0.679.
- **`model_with_mmse`**: For settings where an administered cognitive test is available. Augments self-reportable features with the total score:
  - Adds `MMSE` / `HMSE` total score (0–30)
  - *Metrics on held-out test*: Sensitivity = 90.5% (95% CI: [76.2%, 100.0%]), Specificity = 74.5% (95% CI: [62.3%, 86.5%]), ROC-AUC = 0.929.

### API Contract (Stateless)
- **`GET /api/risk/form-spec`**: Returns `form_spec.json`, defining all fields, types, valid bounds, English labels, and Odia labels (flagged `[needs native review]`) for dynamic form rendering.
- **`POST /api/risk/predict`**: Accepts `{ "profile": { "Age": 75, "Sex": "M", "EDUC": 12, "SES": 3, "MMSE": 26 }, "use_mmse": true }`.
  - Returns estimated probability, risk band (`lower`, `moderate`, `higher`), decision threshold, and dependency-free transparent feature explanations (`raises` or `lowers` risk) with stable translation keys.
  - **Stateless guarantee**: Patient profiles are **never** logged or persisted to the SQLite database.
- **`GET /api/risk/model-info`**: Returns active model metadata, bootstrap 95% confidence intervals, and decision thresholds.

---

## Deploy on Vercel

CO CARE is deployed live on Vercel as well as configured for local execution.

### Live Production Deployment Links
- 🌐 **Web Application**: [https://cocare-zeta.vercel.app](https://cocare-zeta.vercel.app)
- 📖 **Interactive API Documentation (Swagger)**: [https://cocare-zeta.vercel.app/docs](https://cocare-zeta.vercel.app/docs)
- 🧠 **Risk Screening Model Info**: [https://cocare-zeta.vercel.app/api/risk/model-info](https://cocare-zeta.vercel.app/api/risk/model-info)
- 📋 **Screening Form Specification**: [https://cocare-zeta.vercel.app/api/risk/form-spec](https://cocare-zeta.vercel.app/api/risk/form-spec)
- ⚡ **Vercel Project Dashboard**: [https://vercel.com/ankitapriyadarshini-repos-projects/cocare](https://vercel.com/ankitapriyadarshini-repos-projects/cocare)

### Architectural Constraints Handled
1. **Read-Only / Ephemeral Filesystem**:
   - Vercel's execution environment has a read-only root filesystem with a temporary `/tmp` partition.
   - When running on Vercel (`VERCEL` environment variable detected), the backend automatically points SQLite to `/tmp/cocare.db`.
   - **Important Note**: Game session logging in `/tmp` will reset across serverless cold starts. Vercel deployment is intended as a **live demo**. For actual longitudinal research and participant study data collection, run the local deployment (`start.bat`) or configure a persistent cloud database.
2. **Serverless Bundle Size Limit (< 250 MB)**:
   - Heavy offline data science packages (`shap`, `matplotlib`, `seaborn`, `imbalanced-learn`) are isolated in `ml/requirements.txt` and excluded from deployment.
   - The runtime package footprint in `backend/requirements.txt` (`fastapi`, `pydantic`, `scikit-learn==1.6.1`, `joblib`) produces an uncompressed bundle of ~180 MB, well within Vercel's limit.
   - Explainability runs via dependency-free feature occlusion at inference time.

### Deployment Steps
1. Push the repository to GitHub.
2. Log into [Vercel](https://vercel.com) and click **Add New > Project**, then import your repository.
3. Configure project settings:
   - **Framework Preset**: Other (or Vite)
   - **Root Directory**: `./` (project root)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
4. Click **Deploy**. Vercel will build the frontend assets and deploy the serverless Python function at `api/index.py`.

### Post-Deployment Smoke Test
After deployment completes, verify the endpoints on your Vercel URL (`https://<your-project>.vercel.app`):
- [ ] Visit `https://<your-project>.vercel.app/` - Confirms React frontend loads.
- [ ] Visit `https://<your-project>.vercel.app/docs` - Confirms FastAPI Swagger documentation.
- [ ] `GET https://<your-project>.vercel.app/api/risk/model-info` - Returns 200 with model metadata.
- [ ] `GET https://<your-project>.vercel.app/api/risk/form-spec` - Returns 200 with screening form specification.
- [ ] `POST https://<your-project>.vercel.app/api/risk/predict` with body:
  ```json
  {
    "profile": { "Age": 74, "Sex": "M", "EDUC": 12, "SES": 3 },
    "use_mmse": false
  }
  ```
  Returns 200 with `probability`, `band`, and `explanation`.

