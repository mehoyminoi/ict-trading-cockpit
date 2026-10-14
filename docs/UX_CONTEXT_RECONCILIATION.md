# UX context reconciliation: recovered history and operator review

**Review date:** 2026-10-13, America/Denver.  
**Status:** Historical comparison and operator-feedback record. No replacement layout, ribbon design, color treatment or native UI implementation is accepted here. Layout work is paused while this comparison is reviewed.

**Compared proposal:** `COCKPIT_UX_IMPLEMENTATION_PLAN.md` at `f72f05b489b503a8b8d0413df7148e45546bc8c0`, draft PR #76, plus its synthetic HTML walkthrough. Production baseline remains main `6aa8d4e`, schema v46 / Alpha 0.7. The source architecture and the proposed presentation are separate subjects of this review.

## 1. Main finding

The recovered history supports the existing process, learning and shared-calendar architecture. It also supports the operator's current objection to the walkthrough: the interface should lead attention through useful operations and selectively expose tools. A collection of simultaneously visible forms does not establish that experience.

The proposal preserves many data and ownership contracts, but its presentation does not sufficiently preserve guided Focus, quick Deck orientation, quiet capture, meaningful section identity or a calendar-like QT hub. These are interaction and information-hierarchy issues that can be assessed now, before final styling. Passing browser assertions established that the demo controls operated; they did not establish usability or acceptance of the composition.

## 2. Sources, order and overlap

The operator supplied two local recovery exports, read in this order:

| Source | Scope in these exports | Fingerprint |
| --- | --- | --- |
| `context_transcript_the_prequel(1).txt` (P) | 1,786 lines; feedback/capture foundation, process blueprint, executable TDA, Focus/Deck, Trading Day transitions and the 148-pass handoff | SHA-256 `349c4e373dd6d3218ce3329d957ad96ca1ccf678a88b48e3aca05b473c10f376` |
| `context_transcript(1).txt` (T) | 3,070 lines; repeated handoff, Session Runtime, Watch/Review, playbooks, temporal/QT context, Study pivot, practice environments and competency foundation | SHA-256 `de134c5dcd4aae1f4247e2778a4f21d0b2fe374558adb73abc3c8cf75207c306` |

The ending of P and opening of T repeat the 148-pass station-state/mouse-navigation handoff and the proposed Session Runtime sequence. Word-normalized matching finds an 815-token block across P 1636–1786 and T 1–129 despite formatting differences. The earlier cumulative feedback digest is also repeated at P 248–310 and T 1352–1414, with 52 identical nonempty lines. Treat these as shared evidence, not two independent approvals or two newly raised wishes.

These exports are excerpts of a longer development history. P begins with the already-existing feedback/capture foundation; T ends while the competency/Alpha 0.7 work is being developed. Their old branch/schema/test counts describe historical checkpoints. Later canonical requirements and the current implementation govern what is implemented and what remains open.

The raw transcripts remain unmodified and are not copied into Git. See [the historical source index](history/README.md). The evidence locators below refer to the supplied exports, not repository source line numbers.

## 3. Recovered context versus the proposal and walkthrough

| Theme | Recovered evidence | Assessment of the current proposal / walkthrough | Reconciliation |
| --- | --- | --- | --- |
| Guided Focus and accessible Deck | P 726–1009: operator likes the smaller working focus, requests the chart-aligned pane option, then reports intuitive switching. A Deck selection returning directly to Focus is explicitly requested and implemented. | The plan equates close integration with adjacent responsibilities; the demo keeps a station grid beside a general notes form. This loses the distinct work-versus-orientation interaction that was useful. | Preserve distinct Focus and Deck responsibilities and direct Deck → selected Focus access. Their proximity does not require permanent simultaneous expanded panels. Mature access mechanism remains open. |
| A station is an operation | P 731–894 separates Action, Observe and Carry Forward, including manual chart work and chart/pane roles. | The demo's TDA detail primarily presents a question and notes. It omits the action checklist/chart role that explains what to do before answering. | Retain action → observation → carry-forward meaning and required current-station decisions when designing Focus. Existing native action items and chart-role labels are reusable. |
| Quiet capture from Watch | P 1505 and 1740–1747; T 211–218 and 1450: capture should be callable as a lightweight action, without leaving the process to hunt for a separate tab. | The written plan says capture should be reachable, but the demo foregrounds a Study Find form in Lab and provides no equivalent quiet Watch capture route. | Keep a discoverable contextual command/shortcut and a clear return to the working task. A permanently open capture form is not required. Ribbon/task-bar access is a trial preference, not a settled control. |
| Quiet is selective attention | T 211–225 and 270–394: standing capture panels feel foreign; raw click/navigation logs feel like friction; splitting Market and Process Review reduces weight. T 2717 calls for progressively quieter Forward/Live surfaces. | Uniform panes, repeated explanations and simultaneous tasks still compete. The demo also places Market and Process Review side by side despite the accepted staged separation. | Quiet needs fewer competing tasks, clear primary actions, incidental detail on demand and preserved staged Review. Stored history does not imply foreground history. |
| QT hub as a calendar | T 1444–1556 explicitly requests a QT hub with a calendar-like experience and shared contextual rendering across the cockpit. | Shared temporal ownership is implemented, but the proposed table/quartet overview is not a calendar renderer. UX2 names full-stack investigation without explicitly promising real calendar navigation. | Retain the calendar hub as a mature rendering requirement. The latest operator message makes the month-grid and period-selection behavior more concrete. Shared storage does not by itself satisfy this UI need. |
| Shared substrate, distinct operating emphasis | T 2531–2719 separates focused Lab drills from integrated Replay rehearsal and progressively quieter Forward/Live operation. | The plan retains environment/purpose semantics, but the demo's destinations have nearly the same visual grammar and little at-a-glance identity. | Shared data/actions do not require identical compositions. Section identity and task emphasis need explicit review criteria. Replay should still rehearse the operational process; visual distinction must not create another runtime. |
| Orientation and interruption | P 1087–1100; T 338–394: remember where the operator was, restore the active working location, and anchor required actions. | The plan preserves restoration, but the demo relies heavily on headings and repeated status text to convey location. | Orientation must be immediately legible from context, task and meaningful state cues. Restart requires reacquaintance support as well as saved data. |
| Navigation versus completion | P 1562–1670, repeated in T: wheel/coarse Deck access and Back/Forward/precise navigation are useful; navigation never certifies a station. | The plan's blanket replacement of wheel navigation with explicit station actions risks treating a developer layout accommodation as an accepted final redesign. | Protect shared navigation semantics and established muscle memory. Resolve wheel scrolling versus navigation context deliberately; preserve explicit completion. Do not blindly reinstate a global wheel binding. |
| Study drives the near-term experience | T 2427–2486 and 2815–2821: operator wants the study/muscle-memory loop and an inviting route back to proficiency work. | UX1's Study doorway and recorded-basis staging fit this direction. A suggestion alone does not establish a useful Study workspace. | Keep the Study-first direction and evidence-backed remedies; review the complete task/return journey before expanding the shell. |
| Modular, revisioned authoring | T 958–970 and 2815–2821: configurable no-code playbooks and modularity, with deliberate plan revision boundaries. | The plan correctly keeps definitions, candidate/published revisions and later criteria authoring separate. | Preserve this architectural direction. Familiar software controls may improve access but do not authorize rule changes, invented scores or automatic policy adoption. |

The original supplied trade-plan documents still support preparation, expectations, retained AMDX/calendar context, Review and Study. They do not determine the mature navigation arrangement or override later operator feedback.

## 4. Latest feedback: what is historical reinforcement and what is new detail

| Current feedback | Classification and treatment |
| --- | --- |
| Lab calendar should resemble the actual month, with week/day/session cycle indications and editable lower stacks after selection | More explicit rendering behavior for the previously requested calendar-like QT hub. Record it as a mature requirement to work toward; it is not an instruction to implement a calendar before this review. |
| Full stack from 16-year to the smallest supported cycle should be visible or easily accessible; calendar reachable from other contexts | Reinforces foundational AMDX and low-motion access. Keep a quiet contextual summary and full-context access coherent; do not interpret visibility as requiring every editor to remain open. Existing supported layers remain the source of truth. |
| Quarter/session colors: Q1/Asia yellow; Q2/London red; Q3/NYAM green; Q4/NYPM blue | New explicit convention supplied in this review. Retain for later colorization; no exact RGB values are adopted. These identify temporal quarter/session positions, not A/M/D/X phase meanings or completion status. Preserve textual/non-color meaning and theme contrast. |
| Dense, homogeneous screens; major sections should be recognizable at a glance | Current usability finding with historical support for selective rendering, clear intent and different environment emphasis. It is not premature cosmetic feedback. |
| SolidWorks/CAD, Office and tuning-software toolbars/ribbons/tabs/icons | Specific current references for an exploratory interaction trial. Those named controls/software are not explicitly adopted in the two supplied exports. The familiar engineering-workspace/modularity direction is consistent with canonical requirements. |
| Study Find and other detail/subroutines should be tucked away but easy to invoke | Reinforces quiet capture and selective presentation. Trial ribbon/task-bar access with contextual return; do not silently hide a required current-step decision. |
| Related AMDX information is scattered across the screen | A composition problem in this walkthrough. Define one coherent context region/access path; supplementary inspection should maintain its relationship to the selected context rather than repeat disconnected summaries. |
| Focus/Deck have been combined again | Current correction of the proposal's over-literal adjacency interpretation. Guided task focus and easily accessible bird's-eye orientation must remain distinguishable. Older separate-tab implementations and later close-integration guidance can satisfy the same responsibilities through a reviewed interaction. |
| Flow still needs optimization | Keep review centered on entering a task, invoking support, returning, deliberately completing and resuming. Do not reduce this to individual dropdown convenience. |

The operator explicitly frames layout suggestions as exploratory. Record each suggestion and its reason without converting a possible ribbon, drawer, toggle or overlay into final product law.

## 5. Constraints that survive historical recovery

1. **Current ownership and provenance:** one maintained instrument calendar; independent working/Observed semantics; immutable original run captures; no guessed legacy instrument or comparison baseline.
2. **Later quarter semantics:** coupled AMDX/XAMD, legal one-entry revision and direct X(C)/X(R) where structurally allowed. The older flat independent dropdowns are historical implementations, not the next renderer.
3. **Later primary footprint:** the accepted 16:9 primary workspace supersedes old small companion-window examples. More available area does not require more permanently visible forms.
4. **Process and learning remain shared:** environment, purpose, competency state/evidence, eligibility and account context remain distinct. No arbitrary maturity/proficiency threshold or new enforcement policy is inferred from historical examples.
5. **Current lifecycle:** deliberate runs are not automatically created for every market session. Closing/reopening does not conclude a run. Explicit transitions and completion retain their own meanings.
6. **Review semantics:** Market then Process Review, with interpretation and adherence independent; successful no-trade work can still yield observations and Study Finds. Optional AMDX comparison/history belongs in purposeful Study/Review, with no Watch route.
7. **Later visual obligations:** contextual definitions, low working-memory burden, direct return and truthful unavailable/not-configured states remain required. Charts stay external; historical chart-parity enthusiasm does not authorize an integration project now.

## 6. Corrections needed before another layout iteration

Revise the interaction specification around three concrete journeys, then review a small prototype of the chosen journey:

- **Guided TDA:** current station action/question → deliberate observation → Deck orientation or prior-result inspection → selected Focus work → explicit completion. Preserve chart/station relationships and required decisions.
- **Quiet Watch:** current thesis/context and next relevant action → optional capture or full-context inspection → return to the same working place. Ordinary support tools should not become parallel obligations.
- **Lab calendar:** question or recorded study direction → actual calendar period selection → coherent whole-stack orientation and selected lower context → deliberate entry/investigation → capture/Review when useful.

For the calendar specification, distinguish New York civil calendar cells, futures Trading Day labels and approved QT period boundaries. A month grid must not silently turn a fifth week, Friday or an unassigned period into a normal Q5/phase. Date/period inspection must not advance an operational clock, create a run or overwrite a retained capture. These are existing action/time constraints to preserve, not new classifiers.

Review three presentation states separately: **always visible**, **one-action support access**, and **purposeful deep exploration**. Apply the operator's quietness and proximity goals to those states before choosing whether a command lives in a ribbon, toolbar, shortcut, drawer or another control.

The proposed UX1–UX4 sequence remains a useful implementation inventory, but its layout assumptions and usability exits need this reconciliation first. In particular, UX2 must name the calendar renderer; UX3 must preserve guided Focus/Deck access and staged Review; quiet capture access should span the relevant Study/Watch journey rather than wait for an unrelated standalone form rewrite. This is a sequencing recommendation for review, not new implementation approval.

## 7. Review evidence and work boundary

The review compared both supplied transcripts, their duplicate handoff/digest, current canonical requirements and the f72f05b proposal. Existing native `TDAStationRunnerWidget` still contains Focus/Deck views, chart-role/action-item display and Deck selection returning to Focus. The presentation gaps do not require a new data store or a rebuilt process engine.

This checkpoint changes documentation only. Production source, schema v46, Alpha 0.7, both HTML walkthroughs and the downloadable export remain unchanged. All 280 smoke records remain unchanged. Existing implementation and browser-pass counts are retained historical validation, not acceptance of the proposed UI. No regular operator database is opened and no new smoke test or pull is needed to review this comparison.

The next user review is the recovered meaning and the correction priorities. A new renderer comes after that review, with the calendar/ribbon/quiet-access choices still explicit rather than assumed.

## Canonical companions

- [Compared UX/Study plan](COCKPIT_UX_IMPLEMENTATION_PLAN.md)
- [Product requirements](PROJECT_REQUIREMENTS.md)
- [Decision/supersession audit](DECISION_AUDIT.md)
- [Functional walkthrough](COCKPIT_FUNCTIONAL_WALKTHROUGH.md)
- [Current project state](PROJECT_STATE.md)
- [Historical source index](history/README.md)
