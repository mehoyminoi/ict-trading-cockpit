# One-entry working-quartet revision — action review

**Status:** operator authorized implementation after this review on 2026-10-11. Implemented on `feature/amdx-quartet-revision-v1`; developer validation and new operator checks are in `AMDX_QUARTET_REVISION_OPERATOR_GUIDE.md`. The initial PR #61 remains a separate functionally accepted slice. Follow-up checks 251–254 are accepted from the operator’s completed smoke report on 2026-10-12. The final renderer remains open; mature X(C)/X(R) entry must be directly available in one click.

**Baseline:** PR #61's initial entry has six operator checks PASS and a 546-pass developer suite. Its command accumulates the latest anchor for each quarter. The follow-up now implements a separate revision action while preserving those stored-action semantics. Schema v39 adds protected command receipts and a forward-version guard; Alpha 0.7 remains unchanged. The sections below retain the reviewed recommendation and cases; they are implemented by the new policy.

The intended normal flow is: select the relevant quarter, make one valid phase choice, and see the whole working quartet change immediately. It does not require finding an older anchor, clearing it first, saving separately, or leaving Watch.

## 1. Valid phase choices

The role menu uses the union of the two supplied orders, not the currently selected order:

| Quarter | AMDX role | XAMD role | Normal phase choices |
| --- | --- | --- | --- |
| Q1 | A | X | A, X(?) / X(C) / X(R) |
| Q2 | M | A | A, M |
| Q3 | D | M | M, D |
| Q4 | X | D | D, X(?) / X(C) / X(R) |

Every valid position/phase pair selects exactly one order. Invalid normal choices are unavailable in every input adapter and rejected by the shared command, including keyboard/hardware callers. Unknown, Not Applicable and clear are separate actions rather than phase choices. This does not remove the analytical domain's ability to retain conflicting rule evidence, explicit alternatives or old invalid inputs.

## 2. Proposed shared action

Call the logical command **Revise working quartet**. Its policy is:

1. Pin the run, Expected/working scope, containing cycle, selected quarter, inspected head and explicit market reference at gesture start.
2. Validate the selected phase against both structural orders. Select the one order supported by the new position/phase pair.
3. Replace the current explicit anchor at the selected quarter. The new choice is explicit technician judgment; sibling roles remain conditional structural implications.
4. Retain other active technician anchors compatible with the chosen order. Keep a retained X subtype only when it belongs to that same cycle and X quarter.
5. Retire incompatible role anchors from the new active interpretation. Identify their relationship to the earlier claim; do not delete or mutate them in history. A valid phase choice also retires a prior Not Applicable marker so ordinary input can restore an applicable quartet without hunting for that marker.
6. Keep explicit Unknown markers at other quarters as non-constraining judgments. A resolved order may still imply a role there; show both the technician's uncertainty and the conditional role rather than presenting an implied phase as observed certainty.
7. Append and commit one new quartet claim atomically, recording the incoming choice, previous head, retained/retired basis and derived order/subtype. Report success only after commit.

Normal working revision deliberately selects the new working hypothesis. It does not resolve disagreement between independent classifier results or erase a deliberately retained alternative. Those remain separate analytical records/branches. The ordinary command is defined for the manual Expected/working basis used by the current UI. If a legacy/programmatic head contains rule-origin anchors, preserve that mixed basis and reject an unsupported manual rewrite rather than silently retiring rule output; an explicit analytical basis/alternative action belongs to later integration. Stored rule evaluations remain independent.

## 3. X subtype, uncertainty and clear

| Action | Proposed effect |
| --- | --- |
| Choose the same order using another quarter | Retain compatible explicit anchors, including a compatible X(C)/X(R) at the same X quarter. Add the new explicit judgment. |
| Switch AMDX ↔ XAMD | Retire incompatible active phase anchors. X moves to another quarter; its new subtype is unresolved unless the incoming choice explicitly supplies C/R there. |
| Choose X(?) at the existing X quarter | Explicitly replace C/R with an unresolved subtype. Do not interpret X(?) as Unknown. |
| Mark the selected quarter Unknown | Replace that quarter's explicit phase anchor with a non-constraining Unknown marker. In an applicable quartet, other retained phase anchors may still determine the order and conditional role; if none remain, both orders are unresolved. Unknown does not itself undo a quartet's Not Applicable judgment. |
| Clear the selected anchor | Remove that explicit anchor from the new active basis; infer only from the other retained anchors. Never reactivate a retired or previously replaced anchor. |
| Mark this quartet Not Applicable | Record a separate, explicit quartet-applicability judgment, retire its current active phase/Unknown anchors, and show Not Applicable rather than a forced order. Preserve the earlier claim in history. The future menu should name this quartet-wide meaning clearly. |
| Clear that Not Applicable marker | Return to an unassigned applicable quartet. The previously retired phase anchors do not reactivate. A new valid phase can also restore applicability directly. |
| Repeat an already explicit identical role/subtype | No new claim if the resulting active interpretation is unchanged and the inspected head is still current. Selecting a currently implied role for the first time is a new explicit judgment, so it does create a claim. |

Unknown and clearing a phase anchor do not choose another phase or promise to reset the entire quartet when independent compatible anchors remain. A new phase choice is the one-entry order-changing operation. Clearing a quartet's separate Not Applicable judgment is an explicit applicability action; an Unknown entry leaves that judgment intact, even at the quarter from which it was recorded. This separates applicability from role uncertainty in the proposed new action policy; existing records retain their original semantics. Notes/annotations and analytical completion remain independent actions.

The original accumulation action still appends accepted choices. The new command implements the older declared semantic no-op. Identical-input no-op commands receive an immutable idempotency receipt but no extra claim; explicitly selecting an implied phase for the first time remains a new judgment.

## 4. Concrete cases to review

Each row applies to one containing quartet; its parent and children are unchanged.

| Existing working basis | New deliberate action | Proposed result |
| --- | --- | --- |
| No entry | Q3=D | AMDX: A / M / D / X(?). Only Q3 is entered. |
| Q1=A → AMDX | Q3=M | XAMD: X(?) / A / M / D. Q1=A is retired from the active basis, preserved in the earlier claim. No cleanup click. |
| Q3=D → AMDX | Q1=A | AMDX retained; Q1 and Q3 are now explicit. |
| Q3=D and Q4=X(R) → AMDX | Q2=M | AMDX retained with Q4=X(R). The same X quarter retains its subtype. |
| Q3=D and Q4=X(R) → AMDX | Q3=M | XAMD with Q1=X(?). Q4's earlier R is not copied to Q1. |
| Q1=A → AMDX, then Q3=M → XAMD | Clear Q3 | Unresolved order. Retired Q1=A does not return. |
| Q1=A and Q3=D → AMDX | Q3=Unknown | AMDX remains conditional on Q1=A; Q3's entered judgment is Unknown while D remains structurally implied. |
| Q3=D only → AMDX | Q3=Unknown | Both orders unresolved; no phase anchor remains. |
| Current quartet Not Applicable | Q3=D | AMDX selected directly; Not Applicable remains in history only. |
| Current Q4 explicitly X(R) | Repeat Q4=X(R) | No new revision when the inspected head and active meaning are unchanged. |

## 5. Transaction, history and gesture requirements

The command must perform the scoped-head check, basis selection and insert in one repository-owned transaction. A stale editor never decides which newly changed anchors to retire; reload its inspected target and require a new deliberate choice. A failure leaves the committed interpretation intact and the attempted target visibly available for retry. Exact retries of a command identity return the original result, including after later edits; changed content under the same identity is rejected.

Preserve the accepted clock behavior: the claim uses its gesture's target/reference, an unpinned successful or cancelled gesture resumes the latest current quarter, and explicit inspection/failure pins remain visible. Navigation, hover, passive clock movement and control rendering create no claim. Mode/gate/station state and parent/child interpretations do not change through this action.

Existing Accept/Clear transcripts replay under their original accumulation policy. New claims must explicitly identify the new action-policy version; an old record cannot be reread as if it used the replacement policy. Retain enough original before/after basis to validate the incoming choice and every retained/retired anchor on reload. Archive and database readers need mixed-history support and an explicit forward-compatibility guard. Exact payload/DDL changes belong to implementation and are not decided by this review document.

## 6. Implementation and presentation boundary

The first implementation would add the versioned shared action, durable replay/compatibility support, structurally valid input choices and targeted failure/restart/gesture tests. Ordinary working revision must not be implemented as several visible cleanup commands that can partially commit. Existing analytical conflict support remains available outside this normal revision path.

Future renderers use the accepted primary 16:9 workspace target, with quiet whole-stack orientation, nearby detail, session/day and active 90-minute visibility, and contextual hover explanations. This contract does not choose a final table/coverflow renderer, add a Save button or impose cycle completion. Higher-order temporal mapping, classifier criteria, comparison default and broader Study rendering remain separate.

Implementation uses the `revise-working-v1` action policy with v2 claims/archives, retained predecessor/action/retirement/applicability basis and mixed v1/v2 replay. v1 exports and old stored bytes remain intact. The new receipt table reserves command identities, including no-ops, and its transaction includes any cycle/claim writes. A v38 application explicitly rejects a migrated v39 database. PR #61's six functional PASS results cover the original entry; checks 251–254 cover this follow-up and are accepted from the completed operator smoke report on 2026-10-12.
