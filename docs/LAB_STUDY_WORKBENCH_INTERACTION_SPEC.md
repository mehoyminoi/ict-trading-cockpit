# Broader Study-first Lab workbench interaction specification

**Status:** First broader-Lab composition ready for operator review in the [disposable standalone prototype](prototypes/lab-study-workbench-v0.html). The accepted AMDX Lab direction is retained as one lens; no native layout, final information architecture or production workflow is accepted here.

Read with [Cockpit UX implementation plan](COCKPIT_UX_IMPLEMENTATION_PLAN.md), [UX design touchstones](UX_DESIGN_TOUCHSTONES.md), [Lab AMDX operator review](LAB_AMDX_CALENDAR_TREE_OPERATOR_REVIEW.md), [Quiet Watch operator review](WATCH_QUIET_SUPPORT_OPERATOR_REVIEW.md) and [workspace parity](WORKSPACE_PARITY.md).

## Review question

Can Lab welcome a tired technician into one useful next study action, then coordinate the competency, plan definition, chart evidence, samples and foundational AMDX context without becoming either an AMDX-only application or a wall of dockable tools?

This trial tests the broader Lab identity and one complete study-return loop. It does not test final visual styling, real screenshot storage, a full competency catalog, statistical analysis, native navigation or progression eligibility.

## Source-grounded study loop

The supplied trading-plan references separate objectives, methodology, risk, strategy rules, preparation, journaling, measurement and optimization. The operator's current plan further distinguishes pre-market TDA/AMDX/account preparation from post-market logging, comparison, plan review and nightly study. Lab should not flatten those activities into one checklist.

The prototype therefore uses this bounded learning loop:

1. **Choose one competency question.** The startup recommendation explains why this is the best current use of limited energy.
2. **Read the current definition.** Plan-owned rules and alternative hypotheses remain distinct from today's observation.
3. **Gather chart evidence.** A Study Find inherits instrument, period and AMDX context and can later own screenshots.
4. **Test a sample.** Backtest, Replay and Forward evidence remain labeled by environment and purpose.
5. **Evaluate the gap.** Lab identifies the evidence dimension that still needs work without inventing a readiness percentage.
6. **Revise deliberately or continue gathering.** Definition changes remain revisioned plan work; one observation never silently rewrites the rule.
7. **Route outward when appropriate.** Replay integrates, Forward tests live information flow, Review routes weaknesses back, and Watch remains an operational surface.

## Workbench and lens model

The combined top-left selector tests a CAD-like workbench metaphor. The mature shell may separate global workbench from local lens, but the distinction is semantic now:

| Layer | Examples | Meaning |
| --- | --- | --- |
| Cockpit workbench | TDA, Watch, Lab, Review | The operation being performed |
| Lab lens | Study Plan, Evidence, Criteria, Samples, AMDX Calendar | A projection supporting the selected study question |
| Contextual support | Source reference, Study Find capture, AMDX context | One adjacent tool; optionally pinned |

Changing a lens does not change the selected competency, study question, draft, environment or process state. Changing workbench is a legitimate process/navigation action and should preserve a return anchor.

## Study-first opening

Lab opens with **Study this competency** rather than a generic dashboard. The recommendation contains:

- one competency and precise question;
- why it is recommended now;
- the weakest evidence dimension in words;
- a bounded next action and rough effort;
- **Resume study**, **Choose another** and dismiss/continue-navigation choices.

The recommendation is guidance, not an automatic assignment or progression decision. Dismissing it leaves the whole Lab available. Resuming restores the prior lens and working context.

## Stable composition

The prototype keeps three coordinated regions without treating their exact widths as accepted:

- **Study map:** selected competency, nearby work, evidence state and learning-ladder position. It supplies orientation rather than a complete catalog.
- **Main workspace:** one active Lab lens with enough room for the operation at hand.
- **Contextual support rail:** one active support tool and at most one pinned companion. The main canvas does not rearrange itself automatically.

AMDX context remains quietly accessible throughout, but the center becomes the full AMDX calendar only when that lens is chosen. Study Find remains one action or hotkey away and returns to the same lens and question.

## Lens responsibilities

### Study Plan

Shows the current question, working definition, why the question matters, evidence gap and next action. It is the default resumed lens. It does not expose every Trade Plan section.

### Evidence

Shows chart-linked Study Finds, observations, counterexamples and source identity. Evidence never becomes a definition merely because it was captured. The mature version preserves screenshot paste, managed chart storage and Study Find association.

### Criteria

Compares the current published rule with candidate definitions or weighting approaches. A candidate can be tested without silently replacing the published plan. Revision, provenance and effective scope remain explicit.

### Samples

Groups Backtest, Replay and Forward samples by environment and purpose. It highlights missing coverage and representative counterexamples rather than collapsing evidence into one confidence score.

### AMDX Calendar

Provides a compact preview and direct route into the accepted tree/calendar/workspace checkpoint. It remains one foundational Lab lens using the shared maintained calendar, not a separate catalog and not Lab's whole identity.

## Contextual Study Find

**Capture Study Find** opens from any lens and inherits the active competency, question, instrument and temporal/AMDX reference. The operator may add an observation, pattern label and screenshots. Closing preserves the draft; saving returns to the exact lens, selection and support state. Clicking the main body dismisses the surface without losing the draft.

The HTML trial stages text only. It represents—not implements—the existing native screenshot-paste and managed-image capabilities.

## Attention and color policy

- Quiet borders, typography and spacing establish hierarchy.
- Color is reserved for current/selected state, evidence needing attention, restrained news/action cues and stable named-session identity.
- “Nothing required” must not demand attention.
- Completion does not imply mastery, eligibility or permission to trade.
- The active lens and competency remain recognizable after looking to TradingView and back.

## Architecture boundary

The journey should compose existing ownership rather than invent a new dashboard database:

| Prototype concept | Existing substrate | Possible additive follow-up |
| --- | --- | --- |
| Competency recommendation | Competency/evidence maturity and Development Direction | Read model plus recommendation presentation |
| Study question and definition | Trade Plan definitions/criteria and revision ownership | Focused question projection |
| Chart evidence | Study Find draft/save and managed chart images | Context-seeding and stable return adapter |
| Samples | Backtest/Replay/Forward run and evidence metadata | Purpose-grouped query/projection |
| AMDX preview/full lens | Shared maintained AMDX calendar | Broader-Lab route/return composition |
| Routes to other workbenches | Existing process transitions and runtime state | Explicit return-anchor presentation |

No new persistence owner, eligibility rule, classifier, broker action or automatic plan revision is authorized.

## Goal-based operator review

Use the prototype at a normal 16:9 size. Judge the journey, not the sample market conclusion.

1. Start cold. Decide whether **Study this competency** answers “what is the best use of my limited energy?” without trapping you in a modal workflow.
2. Resume the proposed AMDX competency and identify the question, current definition, evidence gap and next bounded action.
3. Move among Study Plan, Evidence, Criteria and Samples. Confirm the selected competency/question remains stable while each area feels like a different operation.
4. Capture the observation **“London traded outside Asia, then closed back inside”** as a Study Find. Close and reopen once to confirm draft recovery, then save and return.
5. Open AMDX Calendar. Confirm it feels foundational and readily available without becoming the whole identity of Lab.
6. Change the support rail between Source, Study Find and AMDX Context; pin and unpin one companion. Confirm the layout stays stable and does not become a dashboard builder.
7. Use the workbench selector and the route-to-Review/Watch controls. Confirm they communicate legitimate destinations and a return anchor without pretending those workbenches are implemented in this file.
8. Reload. Confirm the recommendation dismissal, active competency, lens, draft/evidence count and pinned support choice can be reacquired.

Record where the journey feels like study rather than administration, where the main canvas is too dense or too empty, whether the lens identities are distinct at a glance, and whether the recommendation is genuinely helpful after a long day.

## Acceptance boundary and next milestones

This trial may accept the broader Lab identity, Study-first entry, lens relationships and contextual support-return behavior while rejecting exact controls, content density, labels, geometry or styling.

After review:

1. refine the broader Lab composition once, if the journey exposes a concrete issue;
2. derive a complete Watch composition including the broker/process-safety panel and monitor-orientation profiles;
3. specify the smallest native composition slice only after both Study/Lab and Watch relationships are understood;
4. retain final acceptance for real-data, native-input and repeated-use evaluation.

