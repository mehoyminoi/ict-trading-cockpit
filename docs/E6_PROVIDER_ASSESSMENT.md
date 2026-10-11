# E6 — Economic-calendar provider assessment

**Status:** Provider preference accepted; implementation proposal and unresolved contract questions below are not yet accepted implementation decisions.

**Baseline:** `59a9b984b398a10f54847315569b8179a37b38e6`, schema v36, Trade Plan Alpha 0.7.

**Assessment:** 2026-10-10 operator date / 2026-10-11 UTC retrieval.

**Scope:** E6 real provider integration. E7 model predicates remain downstream.

## Operator preference

The operator uses Forex Factory's economic calendar with an account and selected it as the first choice, paid or otherwise. Trading Economics was an assessment candidate, not a selected dependency. An ordinary Forex Factory account must not be assumed to confer API or historical export access.

The operator subsequently accepted considering alternate sources when they make implementation easier or safer. Forex Factory remains a preference, not an exclusive dependency. This authorizes comparative assessment; it does not select a paid subscription, accept a price, or publish provider-derived trading rules.

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

Initial automated retrieval could not inspect the advertised XML/ICS/CSV formats; a direct XML request returned HTTP 403. The operator subsequently downloaded and supplied XML through the advertised interface. That sample is inspected below; ICS/CSV remain uninspected. No attempt was made to bypass the automated response.

Forex Factory's [notices](https://www.forexfactory.com/notices) specify supplied interfaces/instructions and restrict copying/redistribution. The proposal uses the advertised export interface for a private local workflow; it does not assert redistribution rights, introduce arbitrary HTML scraping, or include captured vendor data in Git/test fixtures. License terms for any paid access or broader use remain to be established separately.

## Operator-supplied XML inspection

The operator supplied `ff_calendar_thisweek.xml` on 2026-10-10 local date. It parses successfully using its declared `windows-1252` encoding: 28,517 bytes, root `weeklyevents`, 83 `event` records, no root attributes. The sample's SHA-256 is `766b9a6bab3c953592249be1a96076b7025d1a8d501d93c2654c0648531ab14d`. The captured vendor file is not committed to the repository.

Every record contains `title`, `country`, `date`, `time`, `impact`, `forecast`, `previous`, and `url`. Dates use `MM-DD-YYYY`; times use a 12-hour clock. Empty forecast/previous elements occur. Source dates range from October 4 through October 9, 2026; observed dates do not certify the nominal weekly coverage or absence on October 10. There is no timezone declaration, occurrence ID, actual value, lifecycle status, source update time, timing precision, scope/completeness statement, or as-of envelope.

The sample adds event-detail URL provenance absent from the inspected JSON. URLs repeat within this single export: one bank-holiday URL appears three times and one employment-series URL twice. A URL or its numeric path component therefore cannot be used as a unique occurrence ID or as grounds to merge records. Two records of the employment series have different times and previous values; preserve both unless explicit occurrence semantics justify a different treatment.

All 83 XML records matched the previously retrieved 83-record JSON sample by title, currency, impact, forecast, previous value, and UTC-equivalent datetime. Interpreting the XML's unlabeled date/time as UTC produced 83 matches and no unmatched records, including date rollover. This establishes a **sample-level UTC inference**, not a verified provider-wide timezone contract. Do not interpret XML times as the operator's calendar-display timezone or apply a fixed four-hour offset across DST.

Comparing the [October 4–10 calendar page](https://www.forexfactory.com/calendar?week=oct4.2026) confirms that records displayed as All Day have clock times in XML, as in JSON. Neither format preserves those records' date-only precision. The sample contains no explicit All Day or Tentative time value; that is not evidence that every occurrence has exact timing or Scheduled status. Tentative representation in other exports/weeks remains unverified.

**Assessment outcome:** XML is readable and useful for source-link provenance, but does not close the timing/status/coverage gaps. JSON provides explicit offsets; XML provides detail links. Neither inspected format alone establishes complete precise context suitable for automatic exclusions. No further operator upload is required to document these findings; unresolved semantics can remain explicit in the proposed domain contract.

## Alternate-source assessment and recommendation

Documentation reviewed on 2026-10-11 UTC; no authenticated alternative-provider response has been verified.

| Source | Verified interface/capabilities | Implication for E6 |
|---|---|---|
| Trading Economics | [Response schema](https://docs.tradingeconomics.com/economic_calendar/schema/) documents a unique CalendarID, UTC Date, DateSpan for known versus estimated timing, Importance, source links, and LastUpdate. [Country/date queries](https://docs.tradingeconomics.com/economic_calendar/country/) are documented. | Strongest documented general-calendar candidate in this assessment; reduces identity/time ambiguity. Cancellation/rescheduling semantics, ID stability under changes, completeness, and paid entitlements still need validation. |
| Financial Modeling Prep | Official [stable economic-calendar endpoint](https://site.financialmodelingprep.com/developer/docs/stable/economics-calendar) is documented. The retrieved page did not expose enough response/precision/provenance detail to establish the required contract. | Secondary candidate; endpoint availability alone is insufficient to prefer it over Trading Economics. Calendar-specific pricing/access remains unverified. |
| Official BLS and Federal Reserve schedules | [BLS](https://www.bls.gov/schedule/news_release/) publishes release schedules, specifies Eastern Time, and advertises an ICS subscription. The [Fed](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) distinguishes meetings, statements, and minutes. | Useful narrowly scoped schedule sources and validation references. Combining them is additional integration work and cannot certify absence of all high-impact news or recreate Forex Factory impact classifications. |
| CME Group | Official [trading-hours interface](https://www.cmegroup.com/trading-hours.html) separates platforms and supports product/date selection for Globex holiday schedules. | Appropriate separate source for relevant futures closure/early-close facts. Select the exact product/platform and preserve timezone/revision provenance; a bank-holiday flag is insufficient. |

**Recommendation (proposed):** evaluate Trading Economics as the first API adapter candidate before committing to a Forex Factory-only importer. This is an engineering inference from documented fields, not a claim that its data is verified safer in production. Retain Forex Factory as the operator's comparison source and possible explicitly limited import option. Preserve provider identity and native impact; do not silently equate Trading Economics importance with Forex Factory red-news classification or silently switch providers for a run.

Trading Economics [advertises point-in-time access](https://docs.tradingeconomics.com/economic_calendar/point-in-time/), but the inspected examples show event-range dates without an independently specified knowledge/as-of cutoff. Actual historical-knowledge semantics and entitlement remain open; ordinary historical retrieval cannot be labeled as-of reconstruction. Its [limits](https://docs.tradingeconomics.com/get_started/rate-limits/) include 1,000 calendar rows per request and a general two requests/second limit. Partitioned retrieval and scoped completeness must be verified before any absence conclusion; no polling interval is selected here.

[API pricing](https://tradingeconomics.com/api/) depends on features, request volume, and distribution. The retrieved [pricing page](https://tradingeconomics.com/api/pricing.aspx) did not provide a usable calendar-specific amount. No cost is assumed. Before purchase or runtime wiring, obtain the relevant entitlement/quote and validate representative known/estimated-time records, rescheduling identity/status, date boundaries, response truncation, and historical access. A representative authorized export can support validation without putting credentials in chat or Git.

The recommended immediate work is the provider-independent capture/coverage/uncertainty contract, followed by a small Trading Economics capability check. The import-first loop below remains a fallback proposal; comparative authorization does not resolve these implementation choices.

## Fit and gaps against the existing contracts

| Requirement | Assessment |
|---|---|
| Operator's familiar impact vocabulary | Explicit export values support a provider-specific mapping; preserve the native value. |
| Market time | JSON provides an offset. XML has unlabeled date/time; UTC matches the inspected sample only. Preserve the timezone basis and its provenance, and convert through America/New_York only when justified. Both formats lose observed All Day precision. |
| Event identity | JSON has no native ID; XML detail URLs repeat and are not unique occurrence IDs. Any local ID must be identified as local; a title/time hash is not durable provider identity across rescheduling. |
| Normalized NFP/CPI/FOMC types | No normalized type field. An explicit, versioned mapping is needed; fuzzy title matching is not acceptable. FOMC minutes, statements, and member speeches must not collapse into one type. |
| Lifecycle status | Export does not certify Scheduled, Released, Cancelled, or Postponed. Do not derive these from missing actual values or elapsed wall time. |
| Historical facts | Imported/captured weeks can be retained. Other dates remain unavailable until a supported source is supplied. |
| Historical knowledge | A saved capture proves what that capture contained, not everything known at an arbitrary earlier Replay timestamp. |
| Negative day/week predicates | Requested bounds are not proof of provider coverage. Validate the source week, scope, parse completeness, and requested window separately. |
| Holiday/schedule facts | A currency bank holiday does not establish CME equity-index futures closure or early-close hours. |
| Restore | Existing run snapshots remain authoritative; restoring/viewing must not query or rewrite them. |

E3 currently records requested bounds as snapshot bounds after a successful `events_between` tuple response. E5 uses those bounds for absence decisions. Before normal startup consumes a real provider, the contract must represent actual coverage and source limitations rather than promote an HTTP success or empty list into full coverage.

## Proposed Forex Factory fallback vertical slice

**Supported weekly export -> validated local import -> immutable source capture -> run snapshot -> existing TDA/Watch/Review.**

Start with local export import so real source-format behavior can be tested without account credentials, purchase, polling, or an assumed historical API. JSON and operator-supplied XML have now been compared. Select a format and explicit uncertainty handling together; do not select XML merely because it is parseable or JSON merely because it has offsets. Optional paired captures must preserve separate acquisition provenance and must not assume different downloads represent one source revision. This remains a proposal, not an accepted implementation design.

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
- Repeated detail URLs do not collapse distinct records; unlabeled timezone/date rollover and declared XML encoding are exercised if XML is supported.
- Partial/unknown coverage cannot prove negative event predicates.
- Multiple captures do not rewrite already-started runs; restart preserves source and run provenance.
- Normal startup without an explicitly configured/imported source remains Not Configured.
- Operator checks compare imported details against the source and exercise TDA -> Watch -> Review -> restart.
- Full automated suite and focused manual acceptance precede implementation merge.

## Open before adapter implementation

1. Select a supported format and document honest timing/timezone semantics. XML inspection is complete for the supplied sample; All Day precision loss is confirmed. Tentative handling, provider-wide XML timezone rules, and ICS/CSV capabilities remain unverified. Further format inspection is optional if the first slice explicitly preserves these unknowns.
2. Define coverage scope, timing precision, source-status uncertainty, and local identity in the domain/snapshot contract; permit a justified migration rather than forcing those facts into a detail string.
3. Define which explicit source labels may map to normalized event types, and version that mapping independently of trading policy.
4. Verify account-supported paid or historical access only if needed. Do not substitute today's export for missing historical context.

No adapter, schema migration, automatic download, readiness rule, account-applicability policy, or Trade Plan revision was introduced by this assessment.
