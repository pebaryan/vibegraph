# AGENTS.md

## Build

| Command | Description |
|---------|-------------|
| `npm run build` / `ng build` | Build the Angular application using the default configuration (development). |
| `ng build --configuration=production` | Build a production bundle with optimizations, source maps disabled, and hashed filenames. |
| `npm start` / `ng serve` | Start the development server with live reload and HMR. |
| `ng serve --configuration=production` | Serve a production‑ready build locally. |

## Backend

| Command | Description |
|---------|-------------|
| `pip install -r backend/requirements.txt` | Install backend dependencies |
| `python backend/app.py` | Run the Flask backend locally |
| `flake8 backend/` | Lint backend Python code |
| `pytest` | Run backend tests (if any) |
| `open http://localhost:5000/apidocs/` | Swagger UI for API docs |

## Lint

The repository does not expose a dedicated `lint` npm script, but Angular’s built‑in TSLint/ESLint integration is available.

```
# Run the default linter across the entire project
ng lint
```

**Targeted linting**

```
# Lint a single file2011ready build locally. |

## Lint

The repository does not expose a dedicated `lint` npm script, but Angular’s built‑in TSLint/ESLint integration is available.

```
# Run the default linter across the entire project
ng lint
```

**Targeted linting**

```
# Lint a single file
ng lint --files=src/app/app.component.ts

# Lint all files in a folder
ng lint --files=src/app/**
```

**Running ESLint directly**

```
npx eslint .
```

## Tests

Angular uses Jasmine/Karma.

```
# Run the entire test suite
ng test
```

**Subset of tests**

```
# All specs in a folder
ng test --include=src/app/**/component/**/*.spec.ts

# Single spec file
ng test --include=src/app/app.component.spec.ts

# Single spec within a file (unique description)
ng test --grep="should render title"
```

**Run once (CI)**

```
ng test --watch=false --browsers=ChromeHeadless
```

## Code Style Guidelines

| Topic | Guideline |
|-------|-----------|
| **Imports** | Core Angular imports first, third‑party next, then local modules. Alphabetical within each group. |
| **Formatting** | Prettier with default Angular config. Run `npx prettier --write .`. |
| **TypeScript** | Prefer `readonly` for immutable fields. Enable `strictNullChecks`. Avoid `any`; use `unknown` or proper interfaces. |
| **Naming** | Components: `PascalCase` + `Component`. Services: `PascalCase` + `Service`. Variables: `camelCase`. Constants: `UPPER_SNAKE_CASE`. |
| **Error handling** | Propagate via Observables or `async/await`. Do not swallow silently. Use `HttpErrorResponse` for HTTP errors. |
| **Testing** | `.spec.ts` suffix. Use `TestBed` to configure modules. |
| **Comments** | JSDoc for public APIs. Inline only for non‑trivial logic. |
| **File structure** | Component files together (`component.ts`, `.html`, `.scss`). Services in `services/`. State in `state/`. |
| **Angular best practices** | Use `ng generate` for new components/services/modules. |
| **Observables** | Prefer `async` pipe in templates. |
| **Change detection** | Use `OnPush` when possible. |
| **RxJS** | Prefer `pipe`, `map`, `switchMap`, `catchError`. Avoid `any`. |
| **Dependency injection** | Constructor injection; avoid `@Inject` unless necessary. |
| **Environment** | Store in `src/environments/*.ts` and import via `environment`. |
| **Angular Material** | Import modules individually. |
| **Monaco editor** | Lazy load; keep instance in a service. |
| **Security** | Sanitize user input; use `DomSanitizer`. |
| **Accessibility** | Semantic HTML, ARIA, test with axe. |
| **Testing utilities** | `ComponentFixture`, `DebugElement`. |

## Cursor / Copilot Rules

No custom cursor or Copilot rule files are present.

## Additional Notes

* Angular CLI watches files during `ng serve` and `ng test` in dev mode.
* For CI: `ng lint --quiet` to fail on lint errors.
* Prettier config in `.prettierrc` if present; otherwise default.
* TypeScript 5.4.2 is used.
* Environment values in `src/environments/`.
* Use `ng test --watch=false` for CI.
* For production builds: `ng build --configuration=production` then `ng lint --quiet`.
* Generate new components with `ng generate component <name>`.

---

*This file is intended for agents that automate tasks in this repository. Keep it up to date as scripts and conventions change.*
