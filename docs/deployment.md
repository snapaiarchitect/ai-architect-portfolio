# Deployment

## Current state vs target

| | Now | Target (not done) |
|---|---|---|
| Host | GitHub Pages | Cloudflare static assets |
| Deploy trigger | `.github/workflows/static.yml`: push to `main` (or manual run) uploads the whole repository as the Pages artifact | to be defined at the move |
| Custom domain | `CNAME` contains `goaiarchitect.com` | same domain, DNS pointed at Cloudflare |
| Response headers | Not configurable on GitHub Pages | `cloudflare/_headers` (ready, inactive) |
| Embedded demo | `demo/gmi-savings-tracker.html` on this site; live tracker at `https://evo3-ecosystem.github.io/gmi-savings-tracker-v3/` | unchanged |

`cloudflare/_headers` is ignored by GitHub Pages. Its syntax was written from memory because the Cloudflare docs could not be fetched when it was authored. Verify it with `wrangler dev` or a preview deploy and inspect real responses before go-live.

## Manual steps still owed by the owner

These need repository-admin or DNS access and cannot be done from code.

1. GitHub: Settings > Pages > enable **Enforce HTTPS** (only selectable once the certificate for `goaiarchitect.com` has been issued).
2. DNS: confirm the records for `goaiarchitect.com` match what GitHub Pages requires today. When moving to Cloudflare, change them to the records Cloudflare gives for the new project, and lower the TTL beforehand.
3. Keep the GitHub Pages deployment (and any `gh-pages` branch, if one exists; none was found in the local clone) untouched until the Cloudflare site is verified on the real domain. Remove it only after that.
4. Before go-live on Cloudflare: test `cloudflare/_headers` in a preview deploy (see CSP TODOs in the file).
5. Watch the repository for issues titled "Scheduled link check failed" and "Site down (uptime check)", which the workflows open and update.

## Checks that run in CI

| Workflow | Trigger | What it does |
|---|---|---|
| `link-check.yml` | pull request, push to `main`, weekly Monday 06:17 UTC, manual | Runs `python3 scripts/check_site.py`, then lychee over `**/*.html` (retries, cache, accepts 200-299 and 429; skips `projects/` and a few hosts that block bots or are fonts/namespaces). On a scheduled failure, opens or comments on one issue. Uses `lycheeverse/lychee-action@v2.9.0`, a tag confirmed to exist via `git ls-remote`. |
| `uptime.yml` | every 30 minutes (minutes 7 and 37), manual | `curl -fsS --retry 3` on the three live URLs; fails if the tracker response carries `X-Frame-Options` or a CSP `frame-ancestors`. Opens or comments on one issue on failure; closes it on recovery. |
| `static.yml` | push to `main` | Existing Pages deploy. Not changed by this work. |

`scripts/check_site.py` rules (offline, stdlib only; `--selftest` exercises each rule):
`LOCAL_REF`, `IFRAME_TITLE`, `FORBIDDEN` (`goaiarchitect.io`, `localhost`, `127.0.0.1`; `projects/` excluded), `CDN_VERSION`, `CANONICAL`, `SITEMAP`, `ROBOTS`.

Note: `check_site.py` runs in `link-check.yml`, which is separate from the deploy workflow, so a failing check does not by itself block a Pages deploy. To make it a gate, add it as a step before the upload in `static.yml` or require the check in branch protection.

## Rollback plan

- Content regression on GitHub Pages: revert the offending commit on `main` (`git revert <sha>`) and push; `static.yml` redeploys. Or re-run an earlier successful deploy run from the Actions tab.
- After a move to Cloudflare: repoint DNS back to GitHub Pages (kept intact, see step 3) and wait for the lowered TTL.
- A bad headers change: remove or revert `_headers` and redeploy; the site works without it.

## "Last verified" policy

Any page that states a fact with a date ("last verified", "as of") must be re-checked at least every 90 days or the date removed. When verifying, update the date in the same commit. The weekly link check and the 30-minute uptime check are the automated signals; neither verifies content accuracy. The 90-day interval is a proposed policy for the owner to confirm or change.
