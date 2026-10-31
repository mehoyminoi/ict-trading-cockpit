# Study capture layout — writing, charts and completion

## Purpose

After operator 360–361 PASS, Study views share a stable frame. This slice reorganizes the existing capture fields/actions instead of adding new data requirements. The accepted fields, validation, single draft, save-to-investigation transaction, fresh next capture, contextual defaults and explicit alignment remain authoritative.

## Composition

- Date, instrument and session occupy a compact metadata row. Pattern and available move share another row.
- Observation and Notes occupy the writing side of a resizable horizontal divider; chart preview, attachment list and image actions occupy the other side. This is presentation, not a new chart data model.
- Keep question for later and Keep finding sit beside the writing area, with their feedback immediately below. Selected-text semantics and optional composers remain unchanged.
- Add, Copy and Remove image actions are grouped below the chart attachments. Existing clipboard image paste and managed image storage are unchanged.
- Generate Summary remains visible. The generated-summary preview, template details and Copy Summary are disclosed when requested; Generate opens the preview directly. Hiding it preserves the generated text and capture content.
- Destination, save feedback, combined/standalone save, last-saved inspection, More and guarded discard remain together in the completion area. More also exposes detailed association provenance; the actual save destination remains visible separately.
- The routine all-matching context explanation is hidden. Actual capture-field differences remain visibly explained; retained-versus-selected reference and explicit alignment controls remain available. Nothing silently corrects a date or changes a destination.

Existing widget instances are reused and the familiar metadata/Observation/move/Notes keyboard order is explicitly retained. This changes no required fields, statistical meaning, plan definitions, repository ownership or schema (53). The shared capture widget gets the layout, while Watch's existing contextual dock commands and save/return semantics stay unchanged.

## Limits

This remains native Qt without final styling. The long capture form still scrolls, especially at narrower sizes. The new divider can be adjusted within the current session; no cross-restart divider preference is added in this slice. Duplicate contextual wording is only reduced where it is routine or secondary provenance; target/reference warnings are not suppressed to make the screen look cleaner. The chart-side position is not yet a global chart-facing-edge setting. No automatic tags, inferred timeframe, required confluence list, or analytical recommendation is introduced.

## Operator 362 — write and handle a chart

After publication, use the durable workspace and a disposable capture or existing work you intend to keep. Check the compact metadata and writing/chart arrangement. Type a short observation, adjust the divider, navigate away/back and verify the same text remains; undo/redo should still work. Paste a chart if useful and check normal preview/selection and image controls. Existing quick question/finding actions should remain beside the text. No new full study session is required.

## Operator 363 — summary and completion

Generate Summary should reveal the summary immediately. Hide/reopen it: text and draft should remain. Check the visible save destination; More → Show association details should disclose existing provenance without changing it. Save through the intended action and expect the same success feedback and fresh next capture as before. If using a disposable mismatched date, the context warning must remain visible; do not save meaningful work under an incorrect reference merely to test it. Resolve disposable work normally.

362–363 pending. Local branch `feature/study-capture-layout-v0`, draft stacked on #108 only when publication is authorized. Do not merge.

## Validation

37 targeted tests PASS: 11 media/next-capture/context/connected-navigation checks and 26 layout/save-to-investigation/summary/question-inbox/Watch checks. The two new layout checks reran after association disclosure was added. They verify draft and destination preservation, native undo, no data writes from disclosure/divider changes, immediate summary reveal and visible mismatching-context guidance. Native offscreen composition inspected at 1600×900 and 1120×800; narrower views still require scrolling. Diff check passed. Operator density/usability judgment remains pending.

## Acceptance and bounded correction

Operator 362–363 PASS overall, with improved navigation noted. Two follow-ups: Ctrl+Y did not redo; Generate Summary on an incomplete capture emitted a terminal error without useful in-app guidance. Local correction adds Ctrl+Y to editable Observation/Notes while preserving native shortcuts; catches summary validation/template/database errors; reports the missing field in reserved local feedback and the existing bottom status bar; focuses a known missing field; preserves draft, prior summary and clipboard. Summary disclosure opens on successful generation, not on failure. The bottom status bar also reports successful generation. No automatic capture save is implied.

The operator clarified that “log” meant a fixed global status location, not a diagnostics browser. This correction starts using the existing bottom status bar for summary actions. It does not claim all existing errors are normalized or protected from later status messages. See UX_INTERACTION_STANDARDS.md.

Retest: in Observation or Notes, type, Ctrl+Z, then Ctrl+Y. With Pattern empty and other required fields filled, Generate Summary should identify Pattern both locally and in the bottom status bar, focus it, and retain the existing summary/draft. Fill Pattern and retry; summary should open and the status report success. Copy Summary on invalid input must not replace the clipboard. Publication of this correction is pending authorization on #109; no merge.

Correction validation: 10 targeted feedback/layout/summary/media tests PASS. New tests exercise actual Ctrl+Z/Ctrl+Y key events, visible local/global error messages, stable local feedback height, success transition and draft/summary/clipboard preservation. The earlier disclosure test used an incomplete capture and only checked panel visibility; it now supplies valid required fields for successful generation. Operator retest remains pending. Diff check passed.
