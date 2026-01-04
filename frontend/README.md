# Frontend (Angular) for GraphDB Web UI Clone

## Project Overview
This Angular application provides a user interface for interacting with RDF data via a Flask backend. It includes:

- SPARQL query editor with Monaco syntax highlighting
- Result display in a table
- Navigation view showing query results as a selectable table
- Graph view placeholder (to be implemented with D3/Vis.js)
- Query history

## Prerequisites
- Node.js 20+ (recommended LTS) and npm
- Angular CLI 18+ (installed globally via `npm install -g @angular/cli`)
- Python 3.10+ with Flask backend running on `http://localhost:5000` (ensure the `/api/queries` endpoint is available)

## Installation
```bash
# From the frontend directory
npm install
```

## Running the Development Server
```bash
npm start
```
This starts `ng serve` on `http://localhost:4200`. The app automatically proxies API requests to the Flask backend.

## Building for Production
```bash
npm run build
```
The output is located in `dist/frontend`.

## Testing
Unit tests are located in `src/app/**/__tests__` and can be run with:
```bash
ng test
```

## Project Structure
- `src/app/components/` – Angular components (QueryEditor, GraphView, Navigation, etc.)
- `src/app/services/` – Service for API calls (`QueryService`)
- `src/app/state/` – Simple state store (`AppState`)
- `src/app/app.module.ts` – Module declarations and imports

## Extending the Graph View
The GraphView component currently contains a placeholder. To add graph rendering:
1. Install a visualization library (e.g., `npm i d3` or `vis-network`).
2. Import the library in `GraphViewComponent`.
3. Use the `AppState.result$` observable to retrieve data and render.

## Contributing
Feel free to open pull requests or issues. For major changes, please create an issue first.

---
*Generated with Claude Code*