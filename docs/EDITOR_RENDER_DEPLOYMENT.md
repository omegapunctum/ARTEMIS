# ARTEMIS editor on Render

This is a prepared owner-first deployment package, not a claim of a live service. The governing scope is [bounded hosting v1](work/2026-10-07_EDITOR_HOSTING_v1.md). Current resource provisioning requires the owner's connected Render account and approval of the actual bill. No real credentials belong in this repository or chat.

## Resources

`render.yaml` defines one Python web service (`0.5c-512mb`), a 1 GB persistent SQLite disk, and one private Key Value instance (`256mb`, no eviction, persistence enabled). Both services use Frankfurt; region selection is fixed at creation. Expected base resource cost checked 2026-10-07 is about USD 17.25/month before taxes, workspace charges and additional usage. Verify the final dashboard quote before creating anything. Free web instances cannot attach the required disk.

Automatic deployments and previews are disabled. Public signup, legacy endpoints, uploads and Airtable APIs are not included. The public form initially serves the pre-provisioned owner; normal contributor onboarding remains a later task. Publication still means an editorial candidate, not accepted historical knowledge or automatic Globe intake.

## Create and configure

Apply `render.yaml` from the reviewed `main` revision only after approval. Keep the generated `AUTH_SECRET_KEY` unchanged. Render injects the private `REDIS_URL`; do not copy it into public logs. Supply `ARTEMIS_OWNER_EMAIL` and a unique `ARTEMIS_OWNER_PASSWORD` through Render's secret environment settings. The bootstrap password needs 12–72 UTF-8 bytes because the existing bcrypt implementation has a byte-length limit. Do not paste the secret in chat.

The launcher validates a canonical HTTPS origin from `RENDER_EXTERNAL_URL` (or explicit `ARTEMIS_EDITOR_ORIGIN`), requires an existing mounted data directory, and runs one worker. Auth/editor initialization and owner creation happen at runtime before HTTP listen, not during build/pre-deploy. The owner is created only when absent. An existing owner retains ID/password/admin status; an existing unprivileged account cannot be automatically promoted. Updating the environment bootstrap password does not rotate a saved account's password. Public registration is absent server-side and hidden on the hosted landing. Use **Войти** with the provisioned account.

The stable database is `/var/data/artemis/editor.sqlite3`. Secret settings persist separately in Render. Cookies are Secure, HttpOnly and SameSite=Lax; auth uses the existing Redis rotation policy. There is no cross-origin Pages write API. The editor and its anonymous candidate cards share the backend origin.

## Acceptance after actual deployment

Do not report availability until the actual assigned HTTPS URL has passed `/api/ready`, `/editor/`, owner login/refresh, private draft save/readback, exact review, explicit anonymous publication and correction/history. Check blocked signup/legacy routes and missing private source expressions in anonymous responses. Record the deployed source commit and test results without credentials or private account data. Native interface evidence from the original pilot is not internet deployment verification.

Restart/redeploy the service and verify the saved object and both immutable snapshot responses. Render's disk is available to the running service only; a separate one-off job or cron service cannot access it. Use the service shell with the existing [SQLite backup/restore script](KNOWLEDGE_EDITOR_RUNBOOK.md#5-резервная-копия-и-восстановление), and a new backup destination under the disk. Export the backup to private off-device storage separately; same-disk backups alone cannot recover a lost disk. Restore to a separate directory/database and verify before any replacement of working data. Never overwrite the working database or silently regenerate the signing secret.

Attaching the disk prevents horizontal scaling and zero-downtime deployments. Expect a brief interruption during rollout. Do not scale worker count or attach another writer to the same file. Restore/rollback needs operator control and a verified backup; deployment rollback alone does not restore database contents.

Provider references: [Blueprints](https://render.com/docs/blueprint-spec), [persistent disks](https://render.com/docs/disks), [pricing](https://render.com/pricing), [compute plan IDs](https://render.com/docs/compute-plans).
