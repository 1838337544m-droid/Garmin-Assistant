# Sync and next-day running assessment

2026-10-28. User requests implementation directly, local-only, reusing existing
Garmin Personal API. Goal: 10 km in under 60 minutes as soon as reasonably
possible. No promise of a completion date; no hard daily pace target of 6:00/km.
Subjective illness/pain/fatigue not supplied: preserve as unknown, never assume no.

## Design
Extend read-through API types with daily, sleep and HRV ranges. A history SQLite
database stores date-keyed records, activity IDs and sync manifests. First sync
backfills 93 days; subsequent syncs overlap 7 days with the previous completed
range. Full=true supports historical corrections. No background schedule.
Persist partial progress, but advance the complete-sync watermark only after all
chunks and all activity pages succeed. Report stale/errors and coverage.

Tomorrow analysis automatically syncs, uses an individualized multi-week baseline
and latest sleep/HRV plus recent running distance/duration/intensity. Future data
must be ignored. Red flags override wearable data. Missing/stale data cannot yield
a green clearance. Tomorrow always requires morning recheck because that night's
sleep is not observable today. Expose thresholds as pragmatic heuristics, not a
validated medical score or Garmin Training Readiness. Do not estimate injury
probability. Provide an explainable session option, target rationale and sources.

Evidence: manually checked publisher/PubMed sources (2024-2026) seed an explicit
reviewed registry. PubMed updates discover recent indexed abstracts at most weekly,
or on demand. Newly retrieved articles remain candidates; fetching a paper does
not validate or automatically rewrite decision rules. Failure falls back to the
reviewed registry, clearly dated. Do not transmit health data to the literature
service. No extra LLM key is required.

## Implementation sequence (inline)
1. RED: sync normalization/pagination/partial failure/idempotence and analysis
   missing-data, red-flag, individual baseline, future dates, distance surge.
2. GREEN: history.py, sync.py, readiness.py; official range dispatch.
3. RED/GREEN: research.py parsing/publication metadata/failure fallback/cache.
4. Add typed MCP tools and CLI; preserve original tools. Save human-readable
   report locally. Real full sync and real MCP calls; whole test suite and review.

## Review focus
- Partial sync or empty fields must not look like normal recovery.
- New, sparse, future-dated or malformed wearable data cannot enable hard running.
- Single HRV dips and load ratios must not become diagnosis or injury probability.
- Repeated syncs must not duplicate activities or overwrite prior data on failures.
- Research dates and automatic updates must not imply exhaustive review or
  validated changes to training rules.

## Execution record
Implemented all modules and 3 new MCP tools, preserving the original 8.
Live 93-day sync: 82 activity summaries; 93 daily/HRV/steps/stress/Body Battery
records; 91 dated sleep records with 2 official null-date/no-sleep placeholders.
Incremental sync checked. Europe PMC fallback verified with 9 indexed candidates
because local DNS cannot resolve eutils.ncbi.nlm.nih.gov. No health data sent.
Store Python virtualizes LOCALAPPDATA onto D:/WpSystem: resolve actual parent
before atomic file replacement. Reports saved in the accessible D:/garmin/reports.
Independent source review identified and led to regression tests for malformed
envelopes/dates, obsolete-record reconciliation, partial activity pages, nullable
nested values, invalid current HRV, and persistence of research refresh failures.
Final review found no remaining Critical/Important issue in fixes.
