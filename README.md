# flexd-jobx-web

Monorepo JobX: portfolio artifacts, evidence-based skills, and job matching.

## Scope

- Backend: Python 3.11+, uv, FastAPI, SQLAlchemy async, MySQL 8, LangChain + LangGraph.
- Frontend: React, TypeScript strict, Vite, Tailwind CSS 4, shadcn-style owned components,
  React Hook Form, Zod, Redux Toolkit.
- Explicit CRUD for all 12 existing tables; CRUD is restricted to active admins.
- Authentication: public registration, login, current user, change password. No refresh/logout.
- Frontend is a scaffold with a local-only validated form, not an auth/CRUD dashboard.
- OpenAI-compatible LLM factory only; no `LLM_PROVIDER`. Agents and S3 operations are not yet exposed.

## Backend setup

Run these steps from `backend/`:

1. Copy `.env.example` to `.env` and configure your database credentials.
2. Generate a JWT secret with `uv run python -c "import secrets; print(secrets.token_hex(32))"`
   and set `JWT_SECRET_KEY`. Never commit this value.
3. Run `uv sync --locked`.
4. Run `uv run uvicorn app.main:app --reload`.

API documentation: <http://localhost:8000/docs>. No startup migrations, `create_all`, seeds,
DB writes, LLM calls, or S3 calls. Application tables must already exist.

The development DB connection explicitly disables TLS when `DB_TLS_ENABLED=false`.
Unencrypted database connections expose traffic to network observers; use a trusted private
network or SSH tunnel. Enable TLS with certificate validation for production.

First admin: `uv run python -m scripts.provision_admin`. This is an explicit write command;
it asks for password confirmation and `CREATE ADMIN` before creating an account. It is never
run automatically. Existing emails are not overwritten or promoted.

### Environment

All application settings use `APP_*`, `DB_*`, `STORAGE_*`, `JWT_*`, or `LLM_*`.
`APP_CORS_ORIGINS` is a JSON array. See `backend/.env.example` for all settings.

LLM setup: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_TEMPERATURE`,
`LLM_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES`. Credentials are passed explicitly to `ChatOpenAI`.
No provider-specific env names are required. Missing LLM/storage credentials do not prevent
normal CRUD/auth startup; their factories fail only when called without configuration.

`STORAGE_ACL=false` means future uploads should omit ACL entirely; it does not make objects
public. `STORAGE_PUBLIC_URL` is only a configured URL, not a bucket-policy change.

### API routes

Prefix: `/api/v1`. Each resource has POST/list GET/detail GET/PATCH/DELETE:

| Table | URL resource | Detail/list response keys |
| --- | --- | --- |
| `user` | `/users` | `user` / `users` |
| `candidate_profile` | `/candidate-profiles` | `candidate_profile` / `candidate_profiles` |
| `company_profile` | `/company-profiles` | `company_profile` / `company_profiles` |
| `artifact` | `/artifacts` | `artifact` / `artifacts` |
| `artifact_analysis` | `/artifact-analyses` | `artifact_analysis` / `artifact_analyses` |
| `artifact_contribution` | `/artifact-contributions` | `artifact_contribution` / `artifact_contributions` |
| `artifact_skill_evidence` | `/artifact-skill-evidences` | `artifact_skill_evidence` / `artifact_skill_evidences` |
| `skill` | `/skills` | `skill` / `skills` |
| `skill_alias` | `/skill-aliases` | `skill_alias` / `skill_aliases` |
| `job_post` | `/job-posts` | `job_post` / `job_posts` |
| `job_skill_requirement` | `/job-skill-requirements` | `job_skill_requirement` / `job_skill_requirements` |
| `job_match` | `/job-matches` | `job_match` / `job_matches` |

Detail IDs use `id`, except candidate profiles which use `user_id`. List parameters: `limit`
(1–100, default 20), `offset` (default 0). Lists sort by primary key ascending.
Ownership foreign keys are immutable on PATCH except `skill_alias.skill_id` and
`skill.parent_skill_id`; recreate a resource to change its ownership. Unknown fields are rejected.

Auth:

```http
POST  /api/v1/auth/login
POST  /api/v1/auth/register
GET   /api/v1/auth/me
PATCH /api/v1/auth/password
```

Register JSON: `{"name":"Budi","email":"budi@example.com","password":"strong-password-123","account_type":"candidate"}`.
Public registration accepts only `candidate` or `employer`; admin role and client-supplied
account status are rejected. Accounts are active, without automatic profile creation or
email verification. HTTP 201 returns only `data.user`; login separately to obtain a token.
Duplicate emails return HTTP 409. Registration is independently limited by
`APP_REGISTER_RATE_LIMIT` (default 5) and `APP_REGISTER_WINDOW_SECONDS` (default 60), per IP/process.

Login JSON: `{"email":"admin@example.com","password":"your-password"}`.
Successful login returns `data.user` and `data.auth` containing `access_token` and
`token_type`. Protected requests use `Authorization: Bearer <access_token>`.
Change-password JSON: `{"current_password":"...","new_password":"..."}`.
New passwords require 12–128 characters and are hashed with Argon2. Unknown legacy password
hashes fail closed; no guessed compatibility. Passwords are never stripped or logged.

Tokens verify signature, fixed algorithm, issuer, audience, subject, and expiry. Current
account status/role is checked from DB on every protected request. Password changes do not
revoke previously issued tokens; they remain valid until expiry. Use short expiry.
Login limit is per process/IP; configure a shared trusted gateway rate limit for multiple workers.

### Response contract

Detail/create/update: only singular resource key.

```json
{
  "message": {"success": "Skill alias retrieved"},
  "error": {},
  "data": {"skill_alias": {"id": "12", "skill_id": "1", "alias_name": "ReactJS", "normalized_alias": "reactjs"}}
}
```

List: only plural resource key plus pagination.

```json
{
  "message": {"success": "Skill aliases retrieved"},
  "error": {},
  "data": {
    "skill_aliases": [],
    "pagination": {"total": 0, "limit": 20, "offset": 0}
  }
}
```

Delete returns HTTP 200 with `data: {}`. Errors keep the envelope with `data: {}` and
attribute/entity descriptions under `error`. HTTP codes: 201 create, 401 auth, 403 role,
404 missing, 409 conflict, 422 validation, 429 login limit, 500 internal.
BIGINT IDs/amounts and DECIMAL values are JSON strings to avoid JavaScript precision loss.
Send large integer input as a string too. Datetime fields use UTC by application convention;
existing MySQL DATETIME columns have no timezone information.

FastAPI's `/docs`, `/openapi.json`, redirects, and protocol-level responses such as CORS
preflight retain framework-native formats; the envelope applies to application API responses.

### Domain safeguards

- Last active admin cannot be removed, deactivated, or demoted.
- Candidate/company/job owners must have the appropriate account role.
- Parent skill changes reject cycles and lock the hierarchy during writes.
- Artifact requires source URL or storage key; project dates must be ordered.
- Evidence analysis must belong to the same artifact.
- Salary ranges, scores, precision, enums, required fields, and foreign keys are validated.
- Published jobs require approval; match status must agree with both decisions.
- Database CASCADE/RESTRICT/SET NULL behavior is preserved. Admin DELETE can cascade;
  review affected data before calling it. No soft-delete columns are invented.
- `normalized_alias` is trimmed/lowercased by the server, not accepted from client input.

## Frontend setup

Node.js 22.12+ (22.x), 24.x, or 26+ is required by current test tooling.
From `frontend/`: copy `.env.example` to `.env`, run `npm ci`, then `npm run dev`.
Only `APP_PUBLIC_*` is exposed to browser code. Never put DB, AWS, JWT, or LLM secrets in
frontend env. API client validates envelopes and accepts a token explicitly; it does not
persist tokens in localStorage. Configure SPA fallback to `index.html` on deployment.

## Checks

Backend, from `backend/`:

```sh
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

Portable SQLite tests exercise all 60 CRUD operations, authentication, role restrictions,
response envelopes, and domain checks. They do not prove MySQL collation, unsigned bounds,
row locking/concurrency, or server timestamp behavior.

MySQL integration is opt-in: precreate matching tables in a dedicated local `*_test` schema,
set `DB_TEST_URL=mysql+asyncmy://...@127.0.0.1/jobx_test`, and run
`uv run pytest tests/test_mysql_integration.py -q`. The test rejects nonlocal hosts and
schemas without `_test`, uses an outer rollback, and does not create/drop application tables.

Frontend, from `frontend/`:

```sh
npm run lint
npm run test
npm run build
```

## Layout

Backend flow: routes (HTTP/dependencies), controllers (response), services
(queries/transactions/rules), models (ORM), schemas (input/output). Shared config and utilities
contain no dynamic client-selected table/column SQL. `agents/` is reserved for later workflows.
Frontend folders: assets, components, hooks, lib, schemas, pages, types, redux.

Dependency note: frontend overrides the ESLint parser's transitive `minimatch` to patched
11.x because its declared 9.x range is affected by GHSA-g3hv-75wg-m249. Remove the override
after typescript-eslint adopts a patched range. Lint, tests, and build are checked with it.
