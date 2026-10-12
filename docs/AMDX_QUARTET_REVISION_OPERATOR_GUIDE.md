# One-entry AMDX quartet revision — operator checks

**Checkpoint:** follow-up branch `feature/amdx-quartet-revision-v1`, based on the functionally accepted PR #61. Schema v39 / Alpha 0.7. The ten reviewed action cases are implemented; four new checks 251–254 are NOT TESTED. Earlier checks 245–250 retain their original PASS results.

## Open a fresh retained sandbox

From the repository root, with your usual Python environment active:

```bash
git fetch origin
git switch feature/amdx-quartet-revision-v1
git pull --ff-only
python tools/amdx_entry_demo.py --data-dir /tmp/ict-amdx-quartet-v1
```

This uses the normal application with a separate synthetic Replay database, starting at 2026-10-08 09:15 ET. Use the same command and directory for restart. Keep this fixture open/unconcluded until the restart check is finished. Existing unrelated files are never replaced; if this directory already contains a concluded trial, choose a new empty directory.

Schema v39 adds immutable command receipts and a forward-version guard. Opening an earlier application database migrates it forward without rewriting old claims; a v38 app cannot reopen a migrated v39 file. The dedicated sandbox keeps this review separate from your earlier fixture and normal data. No provider, classifier, published plan change or order submission is involved.

## What changed

One valid phase entry now revises the whole selected quartet. Compatible explicit anchors remain; contradictory anchors are retired from the active basis and remain in their earlier immutable claims. You do not have to find and clear them. Parent and child quartets still remain independent.

Normal choices are Q1 A/X, Q2 A/M, Q3 M/D and Q4 D/X across both orders. Unsupported direct buttons and X subtype menu choices are disabled; their contextual tooltips explain the role limits. The shared action rejects invalid placements too.

X(C)/X(R) remains only at the same compatible X quarter. Switching the order moves X and leaves its subtype unresolved unless you explicitly choose C/R at the new X quarter. Unknown is a selected-quarter judgment and can coexist with an implied role; the panel distinguishes both. Not Applicable is a separate whole-quartet judgment. A new valid phase restores applicability directly; its menu can also explicitly clear Not Applicable.

Repeating an already explicit identical choice reports **Already current**, with no extra interpretation revision. First explicitly selecting an implied role creates a new judgment. Saved command receipts make even no-op retries idempotent; these receipts are not additional profile revisions or an active history list.

## Four short checks

Use the Day row throughout these checks. You can leave TDA unfinished; none of these actions completes a station or grants entry. The current child/90m row should remain independent. Report PASS / FAIL / QUESTION / NOT TESTED for 251–254.

1. **251 — Valid choices:** inspect Day Q3: only M/D should be enabled, with X subtype choices disabled. Inspect Q2: only A/M. Q1 offers A/X and Q4 D/X. Inspection and trying a disabled button should not report Recorded.
2. **252 — One-entry order change:** select Day Q1 and choose A: Day becomes AMDX. Select Q3 and choose M: Day becomes XAMD immediately, without clearing Q1. Choose Clear this anchor at Q3: Day becomes Unresolved; the retired Q1=A must not return. Earlier claims remain stored, rather than erased or presented as a raw correctness list.
3. **253 — X subtype and repeat:** select Day Q4, choose X(R), then select Q3 and choose D. Day stays AMDX and Q4 stays X(R). Choose D again: status says Already current. Choose M at Q3: Day becomes XAMD with Q1=X(?); Q4's former R must not move to Q1.
4. **254 — Uncertainty, applicability and restart:** while Day is XAMD, select Q1 and choose X(?), then Q3 and choose Unknown. Day remains conditionally XAMD, with Q3 showing Unknown / M and entered / implied. Choose Not Applicable · whole quartet, then Unknown: the profile stays Not Applicable. Choose Clear Not Applicable: it becomes Unresolved without restoring old phases. Choose Not Applicable again, then M at Q3: XAMD returns directly. Close/reopen with the same command/directory: the same run and Day profile return automatically.

## Verification boundary

Developer checks cover all 16 position/role pairs, compatible retention and retirement, X subtype, separate uncertainty/applicability, repeated-input no-ops, mixed old/new replay, immutable receipts, exact retries after later edits, competing writers, atomic receipt/claim rollback, v38 migration/old-reader rejection, normal-window restore and gesture boundaries. The focused group passed **133 checks in 108.59s**; full-suite results are recorded in `PROJECT_STATE.md`.

The existing panel fit was inspected in TDA Focus, Thesis and Watch at 1024px width (the existing runtime minimum produced 1024×876). This does not implement the future primary 16:9 renderer, coverflow or higher-order mapping. Those remain separate presentation/architecture work. New manual acceptance is pending; the previous six PASS results apply to the original entry slice.
