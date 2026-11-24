# Deployment

CO CARE can run locally (recommended for collecting study data) or on Vercel as a live demo.

| Feature / Aspect | Local (`start.bat`) | Vercel |
|:---|:---|:---|
| Game session logging | Persistent SQLite file | Not persistent: SQLite is placed in `/tmp` and resets on cold starts |
| Intended use | Research data collection | Live demo and review |
| Risk-screening screens | Controlled by `VITE_ENABLE_RISK_CHECK` | Controlled by `VITE_ENABLE_RISK_CHECK` |

For real study data on a hosted deployment, a persistent database is required (not configured yet).

## Deploy on Vercel

Push the repository to GitHub: [https://github.com/AnkitaPriyadarshini-repos/cocare-neurorisk](https://github.com/AnkitaPriyadarshini-repos/cocare-neurorisk)

In Vercel: **Add New → Project**, import the repository.

**Settings**:
- **Framework preset**: Other (or Vite)
- **Root directory**: `./` (project root)
- **Build command**: `cd frontend && npm install && npm run build`
- **Output directory**: `frontend/dist`

Deploy. Vercel builds the frontend and serves the Python function at `api/index.py`.

When the `VERCEL` environment variable is present the backend points SQLite to `/tmp/cocare.db`.

### Keeping the serverless bundle small
- Runtime dependencies are limited to what inference needs (`fastapi`, `scikit-learn`, `joblib` and their numerical dependencies).
- Offline tooling (`shap`, `matplotlib`, `seaborn`, `imbalanced-learn`) lives in `ml/requirements.txt` and is not deployed.
- `.vercelignore` keeps `ml/`, `docs/` and markdown files out of the upload. Nothing in `backend/` or `api/` imports from `ml/` or `docs/`.
- Check the function size shown in the Vercel build log after each dependency change; Vercel's limit for Python functions is 250 MB uncompressed.
- The `scikit-learn` version must match between `ml/requirements.txt` and `backend/requirements.txt` so the exported models load.

## Study deployment versus demo deployment

The risk-screening screens are controlled by the build-time variable `VITE_ENABLE_RISK_CHECK` (Vite reads it when building, so redeploy after changing it).

| Deployment | `VITE_ENABLE_RISK_CHECK` | Audience |
|:---|:---:|:---|
| **Study (primary project)** | unset or `false` | Participants and field staff: screening navigation hidden, direct URLs redirect to Home |
| **Demo (separate Vercel project, e.g. `<your-demo-url>`)** | `true` | Reviewers and evaluators: screens enabled with a permanent DEMO banner |

Use a separate Vercel project for the public demo. Vercel preview deployments are behind Vercel login by default, so reviewers cannot open them without an invitation.

## Smoke test

Replace `<your-url>` with your deployment address (e.g., `https://cocare-zeta.vercel.app`).

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://<your-url>/                      # frontend loads
curl -s -o /dev/null -w "%{http_code}\n" https://<your-url>/docs                  # Swagger UI
curl -s https://<your-url>/api/risk/health
curl -s https://<your-url>/api/risk/model-info
curl -s https://<your-url>/api/risk/form-spec
curl -s -X POST https://<your-url>/api/risk/predict \
  -H "Content-Type: application/json" \
  -d '{"profile":{"Age":74,"Sex":"M","EDUC":12,"SES":3},"use_mmse":false}'
```

Each call should return HTTP 200 (the last one with a model score, band and explanation). Also open the app, create a player and play one game to check that the game routes work.
