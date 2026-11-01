# Connected native Study workspace

## Purpose and implementation

The operator accepted the whole-workspace assessment after 358–359 PASS. Study intent was retained, but the global tabs divided the question, calendar and capture into separate visual contexts. This slice places the existing components inside one global Study surface.

A stable investigation header and selected-calendar-reference line sit above a local view selector: Start / study direction, Calendar / AMDX context, Capture / current draft. The existing editor and calendar instances are reparented, not copied or recreated. Each view scrolls beneath the header and retains its scroll position during navigation. Overview and direct review stay in their accepted dialogs; saved-find review remains reachable through its existing route. This is not the final Lab styling or a full replacement of global navigation.

Changing the selector is navigation only. Use Open Study Find from a selected investigation/calendar to establish a capture destination through the existing command. Merely selecting Capture / current draft opens whatever draft already exists; it must not silently retarget authored work. The header names the selected calendar reference (or run reference when applicable), while the capture continues to show its retained destination and explicit alignment action. Changing a view never asserts that TradingView is synchronized.

Start retains existing recorded competency guidance and active-run startup routing. A live run still opens its operational surface. AMDX remains a shared context lens; Study is broader than AMDX. No schema or storage-owner changes. Existing fresh-after-save, single-draft safeguards, Ctrl+Z, image paste and modal review/image protections remain.

## Routing contract

`WorkspaceTabs` centralizes the existing logical-page API: currentWidget/setCurrentWidget address underlying workspace pages; current_surface addresses the physical global tab. Existing MainWindow, tools and demo callers therefore retain their run/capture guards without duplicating editors. Inner Study navigation emits the existing currentChanged notification only when Study is visible, refreshing activation, context notices and current feedback scope. Global tab indexes still describe global surfaces and must not be used to infer a Study page. Feedback labels explicitly include the local Study view.

`StudyWorkspace` owns presentation and view selection only. It does not store investigation identities, write drafts, infer study targets or perform save/alignment commands. No view selection is persisted separately in this slice; restart uses existing startup/run/draft restoration rather than promising last-view restoration. Broader restoration can follow if useful without changing domain ownership.

## Accepted behavior retained and limits

- Resume/New still require resolving authored capture work, with the accepted local recovery route.
- Captures retain their exact context even if the calendar moves. Explicit alignment remains the only supported unfinished-context correction.
- View changes keep the same text editor and its undo stack. Saves/discards retain their existing semantics.
- Existing overview/review dialogs stay modal with their original leave guards. Their embedding is deferred until those guards have an explicit replacement.
- This consolidates navigation, not every field. The capture form remains long and needs scrolling; redundant contextual wording and capture-field layout are future composition work, not reasons to add more controls here.
- Start guidance does not fabricate recommendations from checkpoint prose or observed common threads. TDA pane parity and Watch operational layout are unchanged.

## Operator 360 — one Study frame, same draft

After publication, use the existing durable workspace. Enter Study and choose Calendar / AMDX context. Resume an existing investigation, choose the intended reference, and use Open Study Find. With a disposable sentence in the capture, move between the three Study views using the selector. The question/header should remain in place and the same draft should return. Ctrl+Z/redo should still work in its text editor. Scroll the capture: the header should remain available. Resolve the disposable capture through existing save/discard controls.

If useful, change the calendar while the disposable draft is authored: the header should show the selected reference while capture retains its own reference. No automatic reassignment. This is not a request to alter meaningful records.

## Operator 361 — prior work and return

From the same Study header, open Investigation overview or Review this investigation with existing material. Close normally and expect the same underlying Study view and draft. Move to another global workspace and back to Study; the local view should remain for this running session. Restart behavior remains existing Study-first/active-run routing, not last-view memory. No new full Study session is required.

360–361 pending. Local branch `feature/study-connected-workspace-v0`; publish draft stacked on #107 only with authorization. Do not merge. Includes preceding whole-workspace design/acceptance documentation.

## Validation

37 distinct targeted tests PASS: 27 covering connected navigation, integrated Study, resume, alignment, fresh next capture, Watch capture and workspace restoration; eight Study-home/workspace-clarity checks; two direct-review checks. After adding per-view scrolling, the two new navigation checks and two direct-review checks passed together again. Tests retain logical route identity, no unintended association writes, draft/undo preservation and reference distinction. Native offscreen views inspected at 1600×900 and 1120×800; the first render exposed whole-workspace scrolling and was corrected to keep the header outside per-view scrolling. Diff check passed. Existing capture form density remains a declared limitation, not final UX approval.

Operator acceptance: 360–361 PASS on published draft #108 (`46e84f8`). Next is capture layout; earlier pending notes above are historical.
