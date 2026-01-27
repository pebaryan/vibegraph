# AGENTS.md

This file is for automated agents working in this repo. Keep it accurate.

## Project Overview
- Backend: Flask + RDFLib (SPARQL endpoints, graph storage, search).
- Frontend: Angular app with SPARQL query editor.
- Data is persisted under `backend/data/` and query history under `backend/query_history/`.

## Repo Layout
- `backend/` Flask API, RDFLib graph management, SPARQL protocol endpoints.
- `frontend/` Angular UI.
- `examples/` SPARQL client scripts.
- `tests/` (backend tests live in `backend/tests/`).

## How to Run
### Backend
```
# From repo root
pip install -r backend/requirements.txt
python backend/app.py
```
Backend listens on `http://localhost:5000`.

### Frontend
```
cd frontend
npm install
npm start
```
Frontend listens on `http://localhost:4200`.

## Build
| Command | Description |
|---------|-------------|
| `npm run build` / `ng build` | Build Angular app (dev). |
| `ng build --configuration=production` | Production build. |
| `npm start` / `ng serve` | Dev server with live reload. |
| `ng serve --configuration=production` | Serve production build locally. |

## Lint
```
ng lint
ng lint --files=src/app/app.component.ts
ng lint --files=src/app/**

npx eslint .
```

## Tests
Backend (pytest):
```
pytest
```
Frontend (Karma/Jasmine):
```
ng test
ng test --include=src/app/**/component/**/*.spec.ts
ng test --include=src/app/app.component.spec.ts
ng test --grep="should render title"
ng test --watch=false --browsers=ChromeHeadless
```

## SPARQL Endpoints (Protocol)
These are implemented in `backend/routes/sparql_enhanced.py` and proxied by `backend/routes/sparql.py`.
- `/sparql` (GET/POST) proxy entry point.
- `/sparql/query` (GET/POST) read queries.
- `/sparql/update` (POST) updates.
- `/sparql/info` (GET) capabilities.

Content types supported:
- `application/sparql-query` for read queries.
- `application/sparql-update` for updates.
- JSON and form-encoded `query`/`update` are accepted for app clients.

## Graph Storage & Config
- Graph metadata: `backend/data/graph_data.json`.
- Turtle files: `backend/data/graphs_data/<graph_id>.ttl`.
- Query history: `backend/query_history/<graph_id>/`.
- Config: `backend/config.py`.

## Code Style Guidelines
- TypeScript: prefer `readonly`, avoid `any`.
- Angular imports: core -> third‑party -> local, alphabetical within groups.
- Use `OnPush` where possible; prefer async pipe.
- Python: keep error handling explicit; return JSON error payloads.

## Notes for Agents
- The SPARQL proxy in `backend/routes/sparql.py` should stay thin and call enhanced handlers.
- If you update SPARQL parsing/serialization, update tests in `backend/tests/test_sparql*.py`.
- Keep README and `backend/swagger.yaml` in sync with API changes.

---
If anything here is wrong or incomplete, update this file along with the code change.
