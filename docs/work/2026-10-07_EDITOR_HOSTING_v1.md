# Knowledge Editor — bounded hosted deployment

## Authorization and scope

On 2026-10-07 the owner explicitly confirmed backend deployment after PR #474 merged at `c65198468a5b2e5ffac9c59cd8463f48626e0ad2`, then selected Render. This opens hosting preparation and verification only; it does not reopen epistemic promotion, source-file intake, Globe ingestion, product gates or deferred research.

Prospective independent Architecture review by `/root/editor_postmerge_security`: `ACCEPT_SCOPE`, before code. Required boundaries: explicit route allowlist, registration absent server-side, pre-listen owner bootstrap preserving existing accounts, production Redis/stable secret/secure cookies, single worker/instance, runtime-mounted SQLite and SQLite-aware backup. Creating paid resources requires a connected account and concrete spending approval; neither is implied by the technical verdict.

## Deployment specification

Use one Render Python web service, one 1 GB persistent disk at `/var/data/artemis`, and a private paid Render Key Value instance for refresh sessions. Render provides the HTTPS endpoint. The same-origin editor uses the existing editor routes and auth login/refresh/logout/me; legacy API, uploads, Airtable routes and public registration are absent. The hosted landing hides the unavailable registration button and the deployment runbook directs the pre-provisioned owner to login. This is an initial owner deployment, not open contribution onboarding.

Before importing auth modules, configure production mode, a stable platform secret, Redis, secure HttpOnly SameSite cookies, an absolute mounted data directory and the operator owner address. Bootstrap a new owner account before HTTP listen using a secret supplied in the provider's secret settings; never reset or promote an existing account silently. An existing account must already have operator rights. Reject invalid/overlong bootstrap credentials before bcrypt. Do not print credentials, account addresses or private content. Set one worker and one instance; do not enable automatic deploys or previews.

Readiness checks exercise the database and Redis and return generic status. Hosted errors/cache/security headers must omit private diagnostic values. Existing local entrypoint and all frozen/domain/Globe/Airtable data stay unchanged.

## Verification and stop

Require configuration failures, owner bootstrap preservation, secure cookie and real Redis login/rotation, blocked registration/legacy routes, a complete editor API loop on the isolated app, private/public boundaries, restart and SQLite backup/restore. No UI redesign is included. Existing native interface evidence applies only to unchanged UI behavior; actual internet readiness must be verified after hosting is provisioned.

Preparation is complete when a tested package and independent current-source review are ready. Public availability stays unprovisioned until actual resource creation, HTTPS/readiness/auth/editor checks and persistence verification succeed. If account access or spending approval is missing, report that blocker with the concrete configuration and price. Do not claim a live URL or restore success from disk snapshots alone.

The disk is runtime-only (not build/pre-deploy/one-off jobs), deployments can interrupt service, and disk snapshots do not replace SQLite backup API recovery verification. Backups on the same disk do not provide off-device recovery. Existing runbook remains the backup/restore procedure.

References checked 2026-10-07: https://render.com/docs/disks, https://render.com/docs/blueprint-spec, https://render.com/docs/compute-plans, https://render.com/pricing. Expected base resource cost is approximately USD 17.25/month (web 7, Key Value 10, disk 0.25), subject to actual account plan, taxes and usage. This is an estimate, not a spending authorization.
