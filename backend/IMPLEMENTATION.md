# Implementation record

Scope: existing 12-table schema, admin-only CRUD, login/me/password, categorized
responses, health removal. No remote writes or schema changes.

## Decisions

- Initial CRUD access is admin-only. Candidate/employer ownership endpoints are not exposed.
- IDs remain JSON integers, preserving the preview contract. JavaScript consumers must not
  round unsigned bigint values above Number.MAX_SAFE_INTEGER.
- Queries, transactions, and business validation live in each resource service.
  Controllers construct responses locally; routes register their five operations explicitly.
  Shared response/registration/persistence helper modules were removed at user request.
  No client-supplied table/column SQL is supported.
- Follow-up readability refactor: explicit named CRUD functions in each service/controller,
  decorator routes, dependency resolution only in routes, no Annotated aliases, no generic
  invalid/validate/_write functions, and explicit field/query handling.
  Local helpers remain only for named domain rules such as last-admin protection and skill locks.
- Development DB transport explicitly disables TLS. No credentials are persisted here.
- Existing unknown password hash formats fail authentication; no guessed compatibility.
- First-admin provisioning is an explicit operator command, never startup behavior.
- No automatic Git commit: repository began with an uncommitted scaffold.

## Verification and outstanding work

- Portable functional API tests cover create/list/detail/patch/delete for all 12 resources.
- SQLite tests cannot verify MySQL collation, unsigned bounds, locking, or server timestamps.
- MySQL integration test is opt-in with DB_TEST_URL, refuses application host, requires *_test
  schema, and wraps operations in an outer rollback transaction.
- Docker daemon unavailable. Full MySQL integration/concurrency verification remains outstanding.
- Login rate limit is per process; multi-worker deployments need a shared gateway limit.
- Password change does not revoke previously issued JWTs. Tokens expire naturally.
- S3 upload/delete, LLM execution, matching computation, audit history, and frontend admin UI
  are outside this implementation.
