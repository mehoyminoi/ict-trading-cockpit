# E6 — Forex Factory provider assessment

**Status:** Provider preference accepted; implementation proposal and unresolved contract questions below are not yet accepted implementation decisions.

**Baseline:** `59a9b984b398a10f54847315569b8179a37b38e6`, schema v36, Trade Plan Alpha 0.7.

**Assessment:** 2026-10-10 operator date / 2026-10-11 UTC retrieval.

**Scope:** E6 real provider integration. E7 model predicates remain downstream.

## Operator preference

The operator uses Forex Factory's economic calendar with an account and selected it as the first choice, paid or otherwise. Trading Economics was an assessment candidate, not a selected dependency. An ordinary Forex Factory account must not be assumed to confer API or historical export access.

## Verified public interfaces

Forex Factory's [calendar](https://www.forexfactory.com/calendar) directly links to Weekly Export in ICS, CSV, JSON, and XML formats. Its legend distinguishes High, Medium, Low, and Non-Economic context. The linked JSON was accessible through public web retrieval without account authentication.

The inspected [JSON export](https://nfs.faireconomy.media/ff_calendar_thisweek.json) contains:

- `title`,
- `country` (currency codes such as USD, and the value All),
- offset-aware `date`,
- `impact` (observed Low, Medium, High, Holiday),
- `forecast`,
- `previous`.

This observed schema is not a guarantee that the provider will never change it. No provider-native event ID, actual value, release/cancellation status, source update timestamp, timing-precision flag, coverage envelope, or historical as-of timestamp was present in the inspected JSON.

The live calendar page shows some of these same records as All Day while JSON assigns them timestamps. Therefore an exported timestamp does not by itself establish precise event timing. The calendar also says times are approximate and subject to change.

The [Last Week calendar](https://www.forexfactory.com/calendar?week=last) displayed September 27–October 3 while its JSON export link still targeted `ff_calendar_thisweek.json` and returned October 4–10 records. Historical page navigation must not be treated as historical export selection. Neither arbitrary-date export access nor point-in-time reconstruction was verified.

The retrieval tool could not inspect the advertised XML/ICS/CSV formats; a direct XML request returned HTTP 403. Their fields, timezone rules, and suitability remain unverified. No attempt was made to bypass that response.

Forex Factory's [notices](https://www.forexfactory.com/notices) specify supplied interfaces/instructions and restrict copying/redistribution. The proposal uses the advertised export interface for a private local workflow; it does not assert redistribution rights, introduce arbitrary HTML scraping, or include captured vendor data in Git/test fixtures. License terms for any paid access or broader use remain to be established separately.

## Fit and gaps against the existing contracts

| Requirement | Assessment |
|---|---|
| Operator's familiar impact vocabulary | Explicit export values support a provider-specific mapping; preserve the native value. |
| Market time | Parse the supplied offset and convert through America/New_York. Do not infer precise timing from a date alone. |
| Event identity | JSON has no native ID. Any local ID must be identified as local; a title/time hash is not durable provider identity across rescheduling. |
| Normalized NFP/CPI/FOMC types | No normalized type field. An explicit, versioned mapping is needed; fuzzy title matching is not acceptable. FOMC minutes, statements, and member speeches must not collapse into one type. |
| Lifecycle status | Export does not certify Scheduled, Released, Cancelled, or Postponed. Do not derive these from missing actual values or elapsed wall time. |
| Historical facts | Imported/captured weeks can be retained. Other dates remain unavailable until a supported source is supplied. |
| Historical knowledge | A saved capture proves what that capture contained, not everything known at an arbitrary earlier Replay timestamp. |
| Negative day/week predicates | Requested bounds are not proof of provider coverage. Validate the source week, scope, parse completeness, and requested window separately. |
| Holiday/schedule facts | A currency bank holiday does not establish CME equity-index futures closure or early-close hours. |
| Restore | Existing run snapshots remain authoritative; restoring/viewing must not query or rewrite them. |

E3 currently records requested bounds as snapshot bounds after a successful `events_between` tuple response. E5 uses those bounds for absence decisions. Before normal startup consumes a real provider, the contract must represent actual coverage and source limitations rather than promote an HTTP success or empty list into full coverage.

## Proposed first vertical slice

**Supported weekly export -> validated local import -> immutable source capture -> run snapshot -> existing TDA/Watch/Review.**

Start with local export import so real source-format behavior can be tested without account credentials, purchase, polling, or an assumed historical API. Choose JSON versus XML/CSV/ICS after comparing representative exports, especially All Day and Tentative records. This is a proposal, not a decision that JSON alone is sufficient.

The narrow contract should preserve:

- declared source week and timezone basis, separate from requested futures-day bounds,
- source URL/file provenance, retrieval/import timestamp, and content digest,
- explicit source scope and completeness limitations,
- original fields and adapter/mapping revision,
- event identity provenance and timing precision,
- source knowledge/capture time separate from the run's market reference time.

Keep a cache capture separate from a run snapshot. A new import creates a new capture; it must not mutate old captures or historical runs. Offline operation may inspect a matching stored capture, but must disclose its original capture time and cannot claim a refreshed feed. No automatic freshness cutoff is chosen in this assessment.

Unknown source status, imprecise timing, incomplete scope, failed parsing, missing requested weeks, or unsupported historical knowledge must remain explicit. Do not silently drop uncertain records and then certify event absence. Alpha 0.7's manual gates remain in force; this slice does not publish automatic exclusions.

## Acceptance targets for the proposed slice

- Controlled synthetic fixtures exercise the real export field structure without committing vendor calendar data.
- Import shows source week, capture time, and limitations before associating a capture with a run.
- Wrong-week and unsupported-date cases cannot become Available-empty.
- Exact, All Day, and Tentative timing are not conflated; DST and 18:00 ET boundaries are exercised.
- Missing native identity, status, and normalized type remain honest.
- Partial/unknown coverage cannot prove negative event predicates.
- Multiple captures do not rewrite already-started runs; restart preserves source and run provenance.
- Normal startup without an explicitly configured/imported source remains Not Configured.
- Operator checks compare imported details against the source and exercise TDA -> Watch -> Review -> restart.
- Full automated suite and focused manual acceptance precede implementation merge.

## Open before adapter implementation

1. Compare supported export formats for explicit date-only/tentative semantics and timezone metadata. A manually downloaded representative export is sufficient if automated access is unavailable.
2. Define coverage scope, timing precision, source-status uncertainty, and local identity in the domain/snapshot contract; permit a justified migration rather than forcing those facts into a detail string.
3. Define which explicit source labels may map to normalized event types, and version that mapping independently of trading policy.
4. Verify account-supported paid or historical access only if needed. Do not substitute today's export for missing historical context.

No adapter, schema migration, automatic download, readiness rule, account-applicability policy, or Trade Plan revision was introduced by this assessment.
