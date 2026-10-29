# Investigation review — operator trial 345–347

The purpose is to retain what a study pause produced: understanding, uncertainty and/or a next step. It is not a completion form. Any prompt may stay empty, and support is optional. A review does not change competency state or close the investigation.

After publication, use a new separate fixture because this slice upgrades to schema 51:

```bash
source .venv/bin/activate
python tools/study_criterion_demo.py --data-dir /tmp/ict-study-review-v0
```

Do not point an older application branch at this new fixture. The earlier findings fixture can remain untouched.

## 345 — Save uncertainty without manufacturing a conclusion

1. Keep the seeded investigation question. Open Investigation overview, then **Review this investigation…**. The review area appears beside source inspection; its divider can be adjusted.
2. Leave Current understanding and Next step empty. In the middle prompt, enter `Test: I do not yet know what could have distinguished the London interpretation before NYAM.`
3. Click **Keep review checkpoint**. Expect `Review kept`. The history should show the uncertainty-only review. No supporting material or conclusion is required.
4. Return to investigation. Your question and calendar position should remain unchanged.

## 346 — Retain multiple outcomes and selected support

1. Open Study Find, enter a disposable Pattern and Observation, and choose Save to investigation. Note that a fresh capture is ready; leave an unfinished note in that fresh capture to check preservation later.
2. Return to the investigation and reopen its overview/review area. Select the saved capture in the left material list and inspect it in the center.
3. Click **Use selected material as support**. Only that item should be included. Add a current understanding and an uncertainty and/or next step; multiple outcomes may coexist. (If you are still in the saved review from 345, choose Start a later checkpoint first.)
4. Save. Both checkpoints should appear in history. Selecting an older checkpoint shows its original question, wording and source basis without replacing the current editor. The new review should include the selected capture's retained detail.
5. Return to Study Find. Your unfinished capture note should still be there.

Linked drafts remain inspectable, but cannot be used as stable supporting captures until saved. Findings/partial answers and criterion results can also be explicitly selected when associated with this investigation. Unselected material is not silently treated as support.

## 347 — Cancellation and reopening

1. Open Investigation overview → Review this investigation. If the previous review is still displayed as saved, click Start a later checkpoint; if the inputs are already blank after reopening, skip that click. Type `Test note — safe to discard` in any prompt without saving. Click Return to investigation or press Escape, then choose Cancel. You should stay in the overview with the unsaved note intact.
2. Save it or deliberately discard it; confirm that saved checkpoints remain.
3. Close and reopen this same demo directory. Open Investigation overview → Review this investigation. The saved history and original selected source details should remain.

Qualitative feedback: did this help you keep simultaneous outcomes and identify a useful next step, or did it feel like a required form? Field wording and arrangement remain provisional. The review area is optional and starts hidden each time.

## Implementation and validation

Schema 51 adds independent immutable investigation review snapshots. Save validates scope and selected source snapshots within one transaction; unchanged retries reuse identity/time. Later source changes do not rewrite existing reviews. A stale selected source must be reselected before a new save. Chart references are paths, not duplicated image files. Review wording is protected against accidental dismissal but is not autosaved across application failure before Keep review checkpoint.

228 distinct targeted tests passed across the new review loop, existing findings/questions/overview, MainWindow, repositories and historical migrations. Actual schema-50 upgrade, rollback and old-reader rejection are covered. The first migration-test attempt lacked the remote parent commit locally; fetching it resolved that setup issue and the rerun passed. Optional panel rendered offscreen and visually inspected. Diff check passed. Operator 345–347 pending; no publication or merge claimed.

## Review checkpoint acceptance and analytical direction — 2026-10-29

345–347 PASS. The deliberate opportunity to take stock and retain simultaneous outcomes is accepted. It is a recording step that should fit a natural pause without interrupting a study groove. This is not acceptance of final layout or proof that it chooses the next useful study target.

The Next study step prompt records a technician-authored intention; it does not implement analytical prioritization. Later cross-session analysis should make recurring questions, uncertainties, reviewed errors and performance patterns inspectable with appropriate filters and visualizations. Repeated mentions may reflect interest or exposure, not deficiency. Distinguish questions raised, practice attempted and reviewed performance. Never turn record counts into independent sample counts, proficiency or a readiness score.

Immediate foundation: read-only retrieval across independent investigations for the current Trade Plan, preserving original questions/revisions and current working context. No additional checkpoint polish or repeated scripted navigation is required beyond validating the new retrieval path. Revisit review utility during a natural real-study pause later; preserve the accepted recording role while assessing whether analysis actually helps choose the next task.
