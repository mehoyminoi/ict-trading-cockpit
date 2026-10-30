# Direct investigation review entry

## Purpose and scope

Apply the accepted task-directed-entry requirement: **Keep the current task ready to use; disclose supporting tasks when needed.** In the AMDX investigation area, Review this investigation opens the existing overview with review entry already visible and its first prompt focused. Investigation overview still opens with review entry collapsed. Both use the same editor, sources, save action and investigation scope. History remains read-only.

Hide review entry collapses the editor without clearing thoughts or selected support. Reopening it restores that content within the dialog. Closing still invokes the existing unsaved-review Discard/Cancel guard even when entry is hidden. Review drafts are not newly persisted across dialog closure or restart. No automatic save, checkpoint creation, task completion or competency advancement occurs on entry.

Schema 51 unchanged. Reuse `/tmp/ict-study-review-v0`. No new fixture or repeat of 348–349 is needed.

## Operator 350 — task-directed review and protected return

1. In the current investigation, click **Investigation overview…**. Review entry should be collapsed. Return to the investigation.
2. Click **Review this investigation…** beside the overview button. The review fields should already be visible and ready to type into, with retained material alongside. No second reveal click is needed.
3. Enter a disposable thought in any review prompt. Click **Hide review entry**, then **Review this investigation…** inside the dialog. Your text should remain.
4. Hide entry again and click **Return to investigation**. Choose **Cancel** in the unsaved-review warning. Reopen entry and confirm the thought remains. Then return and choose **Discard** for this disposable thought. The investigation and calendar reference should be unchanged.
5. Optional keyboard check: Tab to the outer Review this investigation button and press Space. It should open the same editor directly. Opening overview afterward should still start collapsed.

This is a short route/guard check, not another full Study workflow test. After acceptance, evaluate the full loop at a natural pause in a real study session: capture, retain a finding or question as useful, take stock when ready, and retrieve prior material. No minimum number of entries or forced conclusions. Notice whether reflection helps retain learning without breaking concentration, and whether history supplies useful next-study candidates; this slice does not implement analytical prioritization.

## Validation and delivery

19 targeted tests PASS across direct review, review checkpoint, history, investigation overview and MainWindow. Diff check passed. Automated verification covers direct and inspection entry, keyboard activation, no writes on entry, preserved capture/task/reference/tab, hidden-editor close protection, and saving through the existing repository. Publication pending as a draft stacked on #99; do not merge. Operator 350 pending.
