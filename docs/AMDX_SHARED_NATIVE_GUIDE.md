# Native maintained AMDX calendar integration

Normal MNQ Lab and newly launched TDA/Watch runs now read and edit the same maintained calendar. Historical Lab backfill needs no run, purpose collection or recurring destination choice. A larger thesis edit opens the full Lab stack beside its quarter editor; Watch keeps the current session/90-minute quartet and a quiet higher orientation line. Direct X(C)/X(R) and immediate phase recording remain available.

## Ownership and scope

A clean database initializes one MNQ MasterCalendar. Existing instrument collections require one deliberate selection in Lab using **Use existing AMDX data…**. No collection is automatically adopted, merged or deleted. New run launch is blocked until that choice is made. Existing instrument-unassigned runs keep their earlier run-owned workflow and records; this slice does not assign them MNQ or import their entries. The native primary Lab is configured for MNQ; the repository's other-instrument isolation is unchanged and another instrument is never substituted into that pane.

Normal historical Lab navigation uses Observed by default, with Expected selectable explicitly. Each channel keeps independent heads. Historical Observed values are not borrowed into current working Expected. The ordinary Lab maintains the canonical source without creating a run. **Full AMDX stack** from current TDA/Watch attaches that reference to the active run; a deliberate Expected thesis edit commits its calendar revision and run capture together. Changing its reference/channel or choosing **Study calendar** returns to independent study entry.

New-run launch atomically persists the run, immutable MNQ/master binding, original seven-layer Expected packet (or five higher plus Closed intraday absence), and operation receipt. Passive clocks, table inspection, rendering, tab navigation and restoration do not append phase history or captures. Existing flat QT forms/summaries remain available for legacy unbound runs; the bound TDA/Watch path hides them to keep maintained calendar orientation authoritative.

## Operational captures and failures

Direct TDA/Watch phase input uses `run_calendar.revise`. Existing TDA/Watch run-data actions routed through the shell's save boundary—including evidence/thesis notes, authorization and entry/watch conditions—use `run_calendar.consume(prepared, updated_run, ...)`. The updated run storage and the exact displayed Expected stack/capture receipt commit in one owned transaction. A changed displayed head, saved-run basis or capture parent rejects; it is not silently replaced with newer unseen context. A failed action reloads stored run data, blocks further shared actions until **Reload AMDX**, and retains failed observation/thesis text for retry.

Consumption receipts use version 2 of the existing run-calendar command envelope, retaining both inspected and updated raw run context. Schema remains v44, policy and packet/binding framing remain unchanged, and archives validate mixed version-1/version-2 chains. Exact retry returns the original operation after subsequent context changes. The updated packet retains the original immutable launch identity/environment/purpose; no new phase is fabricated by a data action. Process mode navigation/conclusion and retrospective Review edits retain their existing save semantics; this is not a new process-transition capture policy.

Press/release entry freezes its run, mode, reference, target head and capture scope. Leaving the surface, changing mode/run, or racing another writer prevents an unintended commit. Read/stale errors require deliberate reload. Current calendar corrections never fill absent launch heads or rewrite retained packets.

## Review and remaining work

Review labels the original launch Expected stack explicitly and opens a read-only full captured-stack dialog from its retained archive, without resolving today's master heads. Editable intraday Observed Review remains the existing independently scoped run assessment. Shared master Observed integration of those run assessments and bounded higher Review-period proof are separate next work; no automatic Expected comparison baseline or Watch history route is introduced.

Final rendering/topology, Study-first startup, coverflow/hotkeys, legacy-run assignment/import, large-history performance and objective/versioned plan classifiers remain separate. The data supports full stack inspection; this trial does not adopt final spacious Lab composition. `AMDX_SHARED_NATIVE_OPERATOR_GUIDE.md` provides a retained separate-database trial. Earlier smoke records 1–264 remain unchanged; 265–269 are PASS from the 2026-10-13 operator report. The accepted scope is the five documented functional behaviors; final rendering remains separate.
