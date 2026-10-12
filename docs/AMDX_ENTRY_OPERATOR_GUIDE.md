# Working AMDX entry — first application surface

**Checkpoint:** shared durable Watch/TDA entry on `feature/intraday-qt-design-v0`, PR #61 ready for review; six functional operator checks PASS. Schema v38 / Alpha 0.7. This is a functional first surface for hands-on review; final layout, coverflow, higher-order cycle mapping and Review comparison policy remain open.

**Later follow-up:** the accepted working revision replaces incompatible anchors in one entry (PR #62). The native Review follow-up now adds separate observed editing and direct one-click X(C)/X(R) buttons across both channels; see `AMDX_OBSERVED_ENTRY_OPERATOR_GUIDE.md` for pending checks 255–259. This original guide/check set remains historical acceptance evidence; its read-only Review and submenu-only subtype descriptions are superseded on the new branch.

## Open the retained sandbox

From the repository root, with this feature branch synced and your usual Python environment active:

```bash
python tools/amdx_entry_demo.py
```

This opens the normal application in a separate synthetic Replay database at `/tmp/ict-amdx-entry/demo.db`. It starts at **2026-10-08 09:15 ET**, with NYAM as daily Q3 and NYAM's 09:00–10:30 interval as its own Q3. Restart using the same command: the same run, explicit reference and committed interpretations are restored automatically. There is no fixture Save step. The tool refuses to replace unrelated files or reseed a missing saved database.

For another fresh trial after concluding this fixture, use a new empty directory:

```bash
python tools/amdx_entry_demo.py --data-dir /tmp/ict-amdx-entry-second
```

The sandbox has no source feed or valid entry setup. It uses normal Alpha 0.7 manual gates; it does not publish a trading method or submit orders. Avoid concluding the fixture until the restart check is finished.

## Read and operate the panel

The **Working AMDX** panel stays above the runtime scroll area in TDA, Watch and Market Review. It shows the daily four-session quartet, the active session's four 90-minute quarters and nearby higher QT context. Higher fields retain their legacy/derived provenance; they are not converted into new cycle anchors. Earlier intraday flat fields remain inspectable, with new intraday entry directed through the quartet panel.

The current 90-minute quarter is ready for input. **A / M / D / X(?)** record an explicit anchor immediately. One anchor constrains the quartet; other roles are marked **implied**. Choosing M in NYAM's Q3 yields XAMD in that child quartet; it does not assign the daily NYAM parent M. X(?) is a known X role with an unresolved subtype, distinct from Unknown or Not Applicable. The secondary menu offers X(C), X(R), Unknown, Not Applicable and Clear this anchor.

Click a quarter—or use table arrow keys—to inspect/pin that target without recording. **Follow current** releases that inspection pin. Ordinary current-quarter entry does not pin the editor permanently, so the next clock interval becomes ready without an extra click. An open phase gesture/menu keeps its inspected target/reference across a clock boundary. After a successful choice or cancellation, an unpinned editor immediately resumes the latest current quarter. A deliberately pinned earlier target remains earlier until released; it cannot silently move to another session.

The daily/session profiles, entered versus implied roles and structural-rule tooltips explain the current working interpretation. Contradictory anchors remain visible as Conflict, without erasing inputs or adding an entry/completion gate. Actual price/news classification criteria are not implemented by these manual buttons. This surface edits the Expected/working branch; Market Review is read-only here, with no default comparison or observed-cycle entry inferred.

On successful commit the panel says **Recorded**. A failed write says **Not recorded**, retains the last committed result and visibly pins the attempted target for another deliberate choice or **Follow current**. A stale edit reloads that scope's latest committed interpretation without rewinding the current reference time; it requires another deliberate phase choice and does not replay automatically. A retry uses the reference at the start of that new gesture. History read failure disables recording and reports unavailable history. These paths are developer tested rather than manually simulated in this guide.

TDA/Watch content scrolls beneath the fixed panel. In this database-backed path the wheel scrolls content; mouse Back/Forward and station buttons continue navigation. The existing standalone runner retains its earlier wheel-station behavior. This narrow fit adjustment keeps controls reachable; it is not a final overall Cockpit layout redesign.

## Six short checks

These correspond to smoke items **245–250**. All six were reported **PASS** by the operator on 2026-10-11 and pushed in `17b874b2c7fb48f2b35d2e30b9e2a6affe019072`. The steps remain here for repeatable testing; future retests can report PASS / FAIL / QUESTION / NOT TESTED, with comments about cognitive effort and orientation.

1. **245 — Orientation:** open the command above. Confirm Working AMDX, Day and 90m rows, nearby higher QT context, and NYAM 90m Q3 ready for entry. Quarter inspection should not say Recorded or complete a station.
2. **246 — Direct input:** click **M** once. The 90m row should become **XAMD**, with Q3 entered and siblings implied. The Day row remains unresolved. There is no Save/Record step and no station completion.
3. **247 — Watch and parent scope:** enter Watch using **Finish TDA / Enter Live Watch**; the existing incomplete-TDA override is explicit. Click daily **NYAM/Q3**, then **D**. Day becomes **AMDX** (Asia A, London M, NYAM D, NYPM X(?)); the 90m quartet stays XAMD. You remain in Watch, with Return to Analysis available.
4. **248 — X subtype and revisions:** click daily **NYPM/Q4**, then choose **X(R)** from the secondary menu. The role should display X(R). Choose **X(?)** to return its subtype to unresolved. This does not turn X into Unknown. Earlier accepted revisions remain stored; there is no raw correctness/history list in the active panel.
5. **249 — Restart:** close and reopen with the same command. The same sandbox run and committed daily/90m profiles should return without a Save or reseed. Navigation selection may return to the current quarter; interpretation records are preserved independently of transient selection.
6. **250 — Follow versus pin:** with Follow current active, use **Demo reference → Advance by 90 minutes**; the next quarter becomes ready without recording anything. Click a quarter to pin it, advance again, and verify the pinned target stays put. Follow current releases it. Inspecting or advancing time does not itself assign a phase.

## Verification and next boundary

Developer checks cover real mouse/menu/keyboard actions, direct database commits, separate parent/child results, conflicts, clear/subtype/uncertainty revisions, clock/gesture boundaries, stale/storage failures, normal-window restart, sandbox reuse/refusal and fixed-panel reachability. The focused AMDX/domain/storage/runtime/E4/dual-view/E6 compatibility group passed **114 tests in 78.03s**. Full-suite results are recorded in `PROJECT_STATE.md`. Offscreen layouts were inspected for TDA Focus, Thesis and Watch at a requested 1024px width; this runtime's existing application minimum produced 1024×876. The panel fits that width, while runtime content remains scrollable. The operator has passed all six functional checks. Final rendering remains open, with a primary 16:9 workspace now required and a preference for one-entry quartet revision plus structurally valid role choices recorded for follow-up.

Next: review the accepted functional slice in PR #61 and refine the shared one-entry working-quartet revision action, including compatible anchors, X subtype, uncertainty and structural role limits. Keep criterion-content work, higher-order cycle identity, Review pairing and more spacious Study rendering distinct from final component polish. The backend preserves original revisions and definitions; no trade-plan criterion, probability, competency score or new authorization policy is adopted here.
