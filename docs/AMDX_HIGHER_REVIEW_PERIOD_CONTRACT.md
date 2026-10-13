# Higher AMDX Review-period selection

**Status: concrete proposal for review, not an implemented selector.** The v41 adapter in PR #68 currently restores higher Observed context from the saved run-start timestamp only. The timestamp correction in source `9c476df520efec8a7e50a04c015e0de4da78d850` is implemented; the additional selection and proof storage described here are not. Native binding follows this contract review.

The recommendation is to let Review inspect higher context on either side of a calendar boundary inside its own futures trading day. Keep the original run reference intact, default to its context, and offer another orientation only when it changes the higher stack. Choosing orientation alone records no AMDX judgment and adds no completion or Save obligation.

## Place in the cockpit

Review retains the selected run's reviewed day and its explicit intraday selection. A higher orientation choice updates the five higher factual contexts together: 16-year, quadrennial, yearly, monthly and weekly. It does not propagate interpretations between levels, switch runs, retarget an intraday editor, rewrite the run snapshot or consult today's clock/provider/news.

Watch remains a quiet current-stack/current-position surface with direct permitted input. The mature Lab is intended to provide a spacious full-stack AMDX workspace, nearby quarter detail, prominent versioned plan definitions and purposeful evidence investigation. That accepted product direction is not yet a Lab implementation. Its broader Study-owned historical selection and information-availability basis are separate from this bounded Review contract. Comparisons remain lower priority and have no Watch route; final geometry, coverflow, shortcuts, classifiers and weighting adoption remain downstream.

## Reviewed window and defaults

Derive the reviewed futures date from the actual saved original run reference. Its window is **[18:00 on the previous New York calendar date, 18:00 on the reviewed date)**. Compare aware instants, including numeric offsets; a daylight-saving window may span 23 or 25 elapsed hours. The endpoint belongs to the next trading day and is excluded.

The proposed scope is the **whole reviewed futures day**, including its evening before a morning run started. This matches Review's existing all-session inspection, rather than treating wall-clock run creation/conclusion as historical market bounds. It is a recommendation awaiting review, not a claim that whole-day higher selection already exists. Missing or malformed original timestamps disable this higher selector; the accepted intraday legacy saved-Day fallback remains available independently. Do not guess higher scope from a container label, expectation claim or latest live timestamp.

Default to the exact original run-start reference. Resolve candidate higher context from deliberate points within the reviewed window: the original reference, the window start and New York midnight. Deduplicate by the five-level fingerprint `(cycle identity, factual position, position state)`. Under the current temporal policy only the calendar midnight may add a distinct higher orientation inside that window; most days need no extra choice. Present a derived boundary point as an orientation reference, not a newly captured market/news observation. A future policy adding another within-day boundary must revise this candidate derivation explicitly.

A run that starts after midnight can still inspect the preceding evening within its reviewed day. A run that starts before midnight can inspect the later calendar side. Availability depends on canonical temporal mapping, **not on whether an Expected or Observed claim already exists**. Inspection reads the existing current scoped heads; it is not an as-of reconstruction of what the technician knew at the selected historical time. No expectation, pairing baseline or phase is inferred by navigation.

## Occurrence versus quarter position

Calendar quarter rollover usually changes position within the **same yearly quartet**, not the yearly occurrence. For example, March 31 Q1 and April 1 Q2 both belong to yearly cycle 2026 and read the same scoped interpretation head. Ordinary quarter inspection remains available; another orientation does not create another profile for that year.

December 31 to January 1 changes the yearly occurrence. At the 2026/2027 boundary it also changes the anchored quadrennial and 16-year occurrences. Their interpretation heads remain independent. Monthly and weekly mapping continues to use the futures date, with each week's parent derived from its own Monday rather than the currently displayed month.

Derive candidates by resolving the approved reference points, not by filtering quartets for time-interval overlap with the reviewed window. A Friday weekly quartet has already ended at the window's start; a pre-first-Monday monthly quartet can begin after the window. Both still supply legitimate inspectable context. Friday/fifth-week/pre-first-Monday/closed states have no automatically selected input quarter. Deliberate Q1–Q4 inspection is possible; no Q5 or automatic Not Applicable judgment is invented.

## Selection, input and restoration

Changing orientation is read-only navigation: no anchor, claim, pair or command receipt. A deliberate legal phase choice uses the existing immediate revision action, including direct X(C)/X(R), subtype, uncertainty, applicability, clear and no-op semantics. Parent/child, run/channel/branch and separate occurrences stay independent.

Before input, freeze both the preserved original run reference and the selected higher orientation reference, plus reviewed bounds, temporal policy, run/channel/branch/cycle/quarter and inspected claim/pair heads. The selected reference describes temporal orientation; it does not establish evidence availability. Validate original reference and target policy under the owned transaction. Native binding also checks process permission and active selection throughout the gesture. A changed selection cancels the gesture; stale heads/source or write failure preserve committed meaning and require deliberate recovery, without automatic replay.

Recommend remembering a valid orientation while navigating within the same Review run, without a Save click. Keep that navigation preference separate from immutable interpretation history and comparison basis. A changed/unavailable source invalidates it visibly and disables input until context is resolved; changing runs must resolve that run's own context. Persistence of that preference across application restart and the exact control are renderer choices still open for evaluation.

## Proposed durable scope proof

Additional Observed references cannot safely be enabled merely by loosening the v0 guard: that would lose the distinction between the original source and deliberately selected context. Recommend immutable scope metadata tied to the Observed command, written atomically with its existing source/pair/receipt transaction. Preserve the original reference, reviewed bounds/timezone/policy revision, selected reference/source kind, cycle/quarter and inspected heads, including accepted no-op commands with nullable original results.

An additive metadata table is the recommended engineering approach, requiring a future migration and explicit archive/export coverage before implementation. **Current schema remains v41; no v42 migration is present or authorized by this document.** This would not be a second interpretation store or a new trading/action policy. Old commands retain their exact original receipts and v0 reference meaning, with no invented retroactive proof. A command identity cannot be reused to attach a different proof. Exact committed retries return their original result even after current source/selection changes; new requests validate current provenance and scope. Broad Study replay and historical information availability require their own contract.

## Worked cases

All times below are New York local time with their applicable offsets retained.

| Situation | Proposed result |
| --- | --- |
| May 12 evening → May 13 morning, reviewed futures day May 13 | Same higher fingerprint; run-start default, no redundant orientation choice. |
| December 31, 2026 evening → January 1, 2027 | One futures day; offer both calendar sides. Yearly, quadrennial and 16-year occurrences change; no inherited interpretations. |
| March 31 evening → April 1 | Yearly position Q1 → Q2, same 2026 yearly cycle and head. |
| April 1 morning run; inspect March 31 evening | Allowed within April 1's reviewed window even though before actual run start. This whole-day scope is proposed for review. |
| No Expected entry in selected occurrence | Observed inspection/entry remains available; no Expected claim or default comparison is manufactured. |
| Another run has a claim in the same occurrence | It does not supply this run's head. |
| Selected April 1 at exactly 18:00 | Outside April 1's window; next trading day, reject this Review selection. |
| Equivalent UTC and New York timestamps | Same instant and context. |
| Repeated 01:30 at -04:00 and -05:00 | Different instants even when the higher fingerprint is identical; source validation must distinguish them. |
| March 8 / November 1, 2026 daylight-saving windows | Respect 23 / 25 elapsed hours; no fixed 24-hour subtraction. |
| Friday October 9 | Inspect weekly quartet ending October 8 at 18:00; Distortion context, no active fifth input. |
| October 1 before the first Monday | Inspect the October monthly quartet despite its later start; Unassigned, explicit Q1–Q4 input only. |
| August 31, 2026 fifth Monday week | Monthly Distortion remains contextual, not a Q5 anchor. |
| Change orientation without entering a phase | No interpretation or receipt writes. |
| Source, heads or active gesture selection changes | Reject/cancel the new entry atomically; keep committed meaning. |
| Exact old committed retry after a source change | Return the original receipt/basis/result; no retrofitted proof. |
| Missing/malformed original reference | Explain unavailable higher selection; retain lower legacy behavior. |
| Navigate away and back within the same run | Recommend restoring valid orientation as navigation state, without adding interpretation history. |

## Verification and next boundary

Eighteen temporal assertions against the existing resolver verify ordinary-day deduplication, shared futures dates, year/quadrennial/16-year rollover, same-year quarter identity, pre-run whole-day membership, rollover exclusion, 23/25-hour windows, repeated-hour distinct instants, UTC equivalence and Friday/pre-Monday/fifth-week context. These are a disposable design harness, not new repository tests or an implemented selector. Action/no-op/retry/atomicity behavior is covered by the existing adapter tests; the proposed metadata/navigation integration still requires implementation and its own verification.

The implemented DST correction passed **313 focused tests in 13.20s**, then the complete **844-test suite across 72 isolated module processes in 508.64s**, with no failures/errors/skips or pytest warnings. All counts matched collection and all processes exited. ISO payload offsets, schema v41, Alpha 0.7 and all 260 smoke records are retained. No new operator trial is requested for this backend/document checkpoint.

Next: review the whole-day/default/explicit-orientation semantics above, implement the accepted scope proof/selection layer, then bind the quiet higher overview and adjacent input with complete gesture checks. The mature spacious Lab remains a planned presentation of the shared foundation, not a feature completed by this contract.
