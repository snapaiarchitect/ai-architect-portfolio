# Portfolio roadmap

Last updated 2026-11-18. Items are ordered within each group; nothing here is a promise of dates.

## Featured now
1. GMI Savings Tracker (ten tab cards and the live demo).
2. GenAI Engineering (`snapaiarchitect/genai-engineering`), figures quoted from its generated README.
3. Mobility Data Analytics (`snapaiarchitect/mobility-data`), shown as "refresh pending" with no figures.

## Next
- **Mobility refresh:** re-download the data, record the real counts, add tests and a scheduled refresh, then quote figures. The old "743,957 records" claim is not reproducible from the repository today.
- **GenAI:** re-run its audit and refresh the Supreme Court project (May 2026 data); link a live demo if one is published.
- **Link checker:** done as a deploy gate. The offline `site-check` job is the one to mark as a required status check; the external `links` job stays advisory on pull requests because other servers can flake.
- **Cloudflare move:** reconnect the connector with read scopes, inventory the account, then host the static site with `cloudflare/_headers` (test with `wrangler dev` first).

## Later: UI_INDEX (unemployment insurance adequacy, DC/MD/VA)
Left in development on purpose. Before it is featured:
- Run its tests in CI (today CI only validates JSON files).
- Trace the political-layer figures ($89.9M, "7 members", ratios up to 21:1) to the published data files.
- Document the statute behind "wage base frozen since 1992".
- Label the benefit-adequacy values and the $601.3M gap as 2026 projections.
- Fill in the inputs its own audit lists as missing or on fallback.
- Decide how to present the political layer (separate page, not the front card).
