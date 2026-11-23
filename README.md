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
