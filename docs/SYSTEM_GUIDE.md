# ICT Trading Cockpit — System Guide

**Status:** Human-readable architecture guide  
**Purpose:** Explain how the Cockpit fits together so the operator can reason about the system, terminology, and future ideas without accidentally changing scope or conflating temporary UI with the underlying domain model.

This guide is **explanatory**, not the highest source of authority.

When sources disagree, follow the precedence in `docs/HANDOFF.md`:

1. verified current implementation/tests,
2. accepted current requirements,
3. explicit later durable decisions,
4. decision-audit supersession status,
5. earlier decisions,
6. this guide / project-evolution summaries,
7. raw historical transcript discussion.

Use:

- `PROJECT_STATE.md` for the exact current checkpoint,
- `PROJECT_REQUIREMENTS.md` for accepted current product requirements/roadmap,
- `DECISIONS.md` for durable design decisions,
- `DECISION_AUDIT.md` for supersession/conflict status,
- `PROJECT_EVOLUTION.md` for chronological architectural history.

---

# 1. What the Cockpit is

The ICT Trading Cockpit is a local-first **trading-process operating system**.

It is intended to help a market technician:

1. define an explicit, versioned trading process,
2. perform top-down analysis,
3. identify what matters next,
4. observe the market with low operational friction,
5. evaluate opportunities against the current Trade Plan,
6. authorize trades only when the process permits them,
7. review decisions honestly,
8. turn repeated observations into structured evidence,
9. practice weaknesses deliberately,
10. progress from Study toward Live execution only when evidence justifies it.

The Cockpit is **not primarily**:

- a P&L dashboard,
- a generic journal,
- a replacement for TradingView,
- an automatic strategy engine,
- a hidden scoring system.

A process-compliant **No Trade / Stand Down** can be a successful operating outcome.

---

# 2. The highest-level system map

The simplest useful picture is:

```text
                         TRADE PLAN
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
      Foundation        Rules / Safety       Playbooks
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                          Process
                             │
                    TDA → Watch → Review
                             │
                             ▼
                     Structured Records
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
       Process Evidence              Competency Evidence
              │                             │
              └──────────────┬──────────────┘
                             ▼
                   Review / Development
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
       Targeted Practice              Plan Revision
              │
              ▼
   Study → Replay → Forward → Live
```

The core idea is cyclical:

> operate the current plan → collect structured evidence → review what happened → practice or revise → operate again.

---

# 3. Canonical terminology

## Trade Plan

The authoritative, versioned definition of the trading process and its non-negotiable rules.

It owns definitions that materially affect trading behavior, such as:

- competencies,
- Playbooks,
- setup criteria,
- authorization gates,
- market/time restrictions,
- risk/safety rules,
- later progression requirements.

Changing authoritative plan-owned definitions requires a **new Trade Plan revision**.

Current Trade Plan revision: see `PROJECT_STATE.md`.

---

## Process

The part of the system that operates the current Trade Plan.

Current conceptual daily loop:

```text
TDA / Analysis
      ↓
    Watch
      ↓
Post-Market Review
```

---

## Review / Development

The part of the system that improves the trading system and technician.

It is **parallel to Process**, not merely the last screen after a trading day.

It is where accumulated evidence can eventually support:

- targeted Study,
- cross-run learning,
- competency review,
- process/revision comparison,
- revision proposals,
- Evidence Maturity interpretation.

---

## Trading Day

Top-level operating container for one futures trading day.

The canonical futures-day rollover is **18:00 America/New_York**.

---

## Trading Run

One intentional execution of the process inside a Trading Day.

The normal case is one Trading Run spanning the operator's active decision process.

Asia, London, NYAM, and NYPM are **market-session context inside a run**, not mandatory separate runs.

Additional Trading Runs are deliberate exceptions.

---

## Environment

How market information is being presented.

The accepted environments are:

| Environment | Default purpose |
|---|---|
| Historical Backtest / Lab | Study |
| Replay | Rehearsal |
| Forward Test | Validation |
| Live | Execution |

Environment does **not** itself prove eligibility.

---

## Purpose / Intent

Why the operator is doing the run.

Environment and intent are separate dimensions.

Example:

- Environment: Replay
- Default purpose: Rehearsal
- Additional focused intent: practice Time / Session Awareness

A Replay run can therefore have a study focus without becoming Historical Backtest.

---

## Eligibility

What level of practice/execution the technician is currently justified to use.

Eligibility is separate from:

- environment,
- study intent,
- account type.

The conceptual order is:

```text
Eligibility
    ↓
Activity / purpose
    ↓
Account / capital context
```

---

## Account context

The capital/account context used only where relevant.

Expected mapping:

```text
Study      → no account
Replay     → no account
Forward    → Sim / Paper
Live       → Prop / Cash
```

Account type does not determine competency.

---

# 4. Process Blueprint

The process model is:

```text
Process
  ↓
Mode
  ↓
Deck
  ↓
Station
```

A Station is an intentional analytical operation.

A mature Station separates:

```text
Action
  ↓
Observe
  ↓
Carry Forward
```

## Action

What the operator must do.

This may be a manual chart task.

Example:

> Mark the relevant higher-timeframe liquidity.

## Observe

What the technician sees after performing the action.

Example:

> Price is trading below previous-day high while a weekly high remains unmitigated.

## Carry Forward

What must remain relevant later in the process.

Example:

> Primary draw remains above current price.

A future indicator may automate the **Action**, but the Station concept itself can remain stable.

---

# 5. Focus and Deck

Focus and Deck are two views of the same underlying process state.

## Focus

Answers:

> What am I doing right now?

## Deck

Answers:

> Where am I in the larger analytical workspace?

They are not separate workflows.

```text
              Shared Station State
                /             \
               /               \
              ▼                 ▼
         Focus View          Deck View
        current task       whole-workspace
```

Navigation does not silently certify completion.

The operator can move around without the Cockpit pretending that analytical work has been completed.

---

# 6. Daily operating loop

The current core loop is:

```text
TDA / ANALYSIS
     │
     │ establish thesis, draw, context,
     │ watch points, candidates
     ▼
WATCH
     │
     │ observe unfolding evidence,
     │ candidate state, thesis changes
     ▼
POST-MARKET REVIEW
     │
     ├── Market Review
     │     What actually happened?
     │
     └── Process Review
           How well was the process followed?
```

## Important rule

Interpretation quality and process adherence are different dimensions.

A trade can:

- make money while violating process,
- lose money while following process,
- result in no trade while being completely successful from a process perspective.

---

# 7. Review interpretation outcomes

The current useful interpretation taxonomy includes:

- Materially Accurate
- Changed — Critical Information Missed
- Changed — Unexplained / Study Needed
- Changed — External / Exogenous Event

“Unexplained / Study Needed” means:

> I cannot currently explain this from my present technical understanding.

It does **not** mean:

> the market was random.

That distinction matters because unexplained behavior can become a Study candidate.

---

# 8. The learning and progression ladder

The learning architecture is:

```text
Historical Backtest / Lab
          STUDY
            │
            │ learn components
            ▼
          Replay
        REHEARSAL
            │
            │ integrate full process
            ▼
       Forward Test
        VALIDATION
            │
            │ prove capability against
            │ live information flow
            ▼
           Live
        EXECUTION
            │
            │ capital at risk
            ▼
          Review
            │
            └──── weaknesses route back down
```

A compact phrase used throughout the architecture is:

> Lab teaches components → Replay integrates them → Forward validates them under live information flow → Live executes them with capital at risk → Review routes weaknesses back down the ladder.

Moving **up** should eventually require evidence.

Moving **down** should be frictionless.

---

# 9. Competency architecture

A competency is a skill/mechanic the Trade Plan considers important enough to train and eventually validate.

Current Alpha 0.7 competency definitions are:

- HTF liquidity recognition
- Draw on liquidity
- Displacement / FVG recognition
- Premium / discount context
- Time / session awareness

These five are not five unrelated UI controls.

They are the same shared **Trade Plan-owned competency definitions** referenced throughout the Cockpit.

---

# 10. Competency Definition vs State vs Evidence

These must remain separate.

```text
           COMPETENCY DEFINITION
         "What skill matters?"
                  │
                  │ plan-owned
                  ▼
           COMPETENCY STATE
    "Where is the technician now?"
                  ▲
                  │
                  │ may eventually change
                  │ based on reviewed evidence
                  │
           COMPETENCY EVIDENCE
      "What observations support
        or challenge that state?"
```

## Competency Definition

Versioned Trade Plan data.

Example:

```text
ID: draw-on-liquidity
Name: Draw on liquidity
Category: Market Structure
```

## Competency State

Mutable technician/profile state.

Current examples include:

- Not Assessed
- Under Study
- Rehearsal Needed
- Validation Needed
- Proficient

These are workflow states, **not percentages**.

## Competency Evidence

Structured, human-readable observations attached to the competency.

Evidence does not automatically change state.

---

# 11. Current “paper doll” controls vs underlying concepts

Some current controls exist mainly to prove the architecture.

| Current control | Underlying concept |
|---|---|
| Competency checkbox | Declare deliberate competency focus for a run |
| Competency dropdown | Filter the shared competency evidence set |
| Study outcome selector | Produce a reviewed outcome that can become evidence |
| Evidence list | Human-readable history of observations |
| Evidence summary counts | Descriptive aggregation only |
| AVAILABLE / NOT CONFIGURED / BLOCKED | Progression availability state, not competency score |
| Models in Play controls | Current setup/opportunity context, not the definition of all valid trading ideas |

Do not mistake the temporary control for the domain concept.

The UI can change while the underlying concept remains stable.

---

# 12. Competency evidence lifecycle

The current implemented v28 path is:

```text
Choose competency focus
        ↓
Run Study / Replay / Forward
        ↓
Reach Review
        ↓
Record reviewed Study outcome + note
        ↓
Create CompetencyEvidence
        ↓
Persist by run + competency
        ↓
Review / Development
        ↓
Human reads accumulated evidence
```

One run + one focused competency produces one current evidence record.

Re-reviewing the same run updates/replaces that record rather than manufacturing multiple samples from the same run.

---

# 13. What an evidence record means

An evidence record currently preserves useful provenance such as:

- competency ID/name/category,
- Trading Run ID,
- Trade Plan revision,
- environment,
- purpose,
- Study question,
- hypothesis,
- scope,
- reviewed outcome,
- review note,
- market-time context,
- QT context,
- recorded timestamp.

Example:

```text
Competency:
    Draw on liquidity

Trade Plan:
    Alpha 0.7

Environment / Purpose:
    Replay / Rehearsal

Focus:
    Can I identify the draw before lower-timeframe confirmation?

Outcome:
    Refined

Review note:
    External liquidity was correctly identified,
    but the intermediate swing was misclassified.

Market / QT context:
    [structured snapshot]

Trading Run:
    [stable run ID]
```

This is evidence.

It is **not yet a proficiency score**.

---

# 14. Evidence vs metrics vs Evidence Maturity

Keep these layers separate:

```text
Raw reviewed evidence
        ↓
Aggregation
        ↓
Derived measurements / KPIs
        ↓
Evidence Maturity interpretation
        ↓
Trade Plan progression rule
        ↓
Eligibility decision
```

## Evidence

Individual structured observations.

## Metrics / KPIs

Derived summaries across many observations.

Possible future examples:

- sample count,
- reviewed outcome frequency,
- correct recognition rate,
- repeated failure mode frequency,
- environment distribution,
- condition-specific performance.

These are **not yet defined as progression rules**.

## Evidence Maturity

Future interpretation of whether the evidence is broad/deep enough to trust.

Example questions:

- Has the concept only been studied historically?
- Has it survived Replay integration?
- Has it been demonstrated prospectively in Forward?
- Does Live evidence support or weaken confidence?
- Are important market conditions still missing from the sample?

## Progression rule

Explicit Trade Plan policy defining what evidence is sufficient for a higher level.

These rules do not currently exist.

---

# 15. Why we do not use “67% = proficient”

A simple percentage without provenance can hide critical information.

For example:

```text
67% success
```

does not answer:

- success at what?
- in which environment?
- with hindsight or live information flow?
- under which market conditions?
- against which Trade Plan revision?
- across how many samples?
- which failure modes remain?

The Cockpit architecture prefers:

```text
Study:
  recognition repeatedly demonstrated

Replay:
  integrated process mostly successful,
  recurring failure under condition X

Forward:
  insufficient prospective evidence

Conclusion:
  more Forward validation required
```

That conclusion is explainable.

---

# 16. Adding a newly adopted ICT concept

Not every ICT concept needs to exist in every Trade Plan.

A concept becomes a competency only when the current Trade Plan decides it is foundational enough to train/assess explicitly.

The intended flow is:

```text
New or newly-adopted ICT concept
            │
            ▼
Is it important enough to become
a formal technician competency?
            │
           Yes
            │
            ▼
Add CompetencyDefinition
            │
            ▼
Publish new Trade Plan revision
            │
            ▼
Shared competency catalog now exposes it
            │
       ┌────┼────┬────┐
       ▼    ▼    ▼    ▼
     Study Replay Forward Review
            │
            ▼
      New evidence begins
      accumulating from this
      revision forward
```

## Historical-data caution

Older records should **not automatically** be relabeled as evidence for the new competency.

There may be useful historical data that relates to the new concept, but assigning old observations to a newly defined competency requires an explicit mapping/backfill decision.

That future feature should distinguish:

- original evidence captured under the old Trade Plan,
- later retrospective classification/mapping,
- evidence genuinely collected after the competency became authoritative.

This protects historical truth.

---

# 17. Data-driven discovery of missing competencies

A future possibility is that repeated Study Finds, Review outcomes, friction patterns, or derived metrics reveal a recurring skill gap that is **not yet represented in the Trade Plan**.

That can suggest:

> We may need a new competency definition.

But the data should not silently create one.

The safe architecture is:

```text
Repeated observations / metrics
            ↓
Potential missing competency identified
            ↓
Human Review / Development decision
            ↓
Add definition to draft Trade Plan
            ↓
Publish new Trade Plan revision
            ↓
Begin authoritative evidence collection
```

The human/Trade Plan remains responsible for deciding that the concept matters.

---

# 18. Development Direction

Development Direction is the human-reviewed synthesis layer between accumulated evidence and later governance.

It answers:

> What deliberate work should happen next for this competency, based on the evidence I have reviewed?

Initial directions are:

- Study
- Rehearsal
- Validation
- Monitor / Gather Evidence
- No Active Focus

Keep the layers distinct:

```text
Study Outcome
= what this run taught us

Competency Evidence
= the structured observation/provenance

Development Direction
= what the technician chooses to work on next

Competency State
= where the skill sits in the broader training ladder

Evidence Maturity
= future confidence/governance over the evidence

Eligibility
= whether explicit Trade Plan rules permit the higher level
```

Development Direction is mutable technician/review state. It preserves the Trade Plan revision under which the synthesis was made, but it does not alter the plan-owned competency definition.

In v0 it is explicitly human-authored. The Cockpit does not claim to discover a recurring weakness automatically.

A Development Direction may optionally reference specific evidence records that informed the judgment. The evidence link supports traceability; it is not required to make the direction valid.

A direction does not automatically mutate Competency State, Evidence Maturity, or Eligibility.

---

# 18A. Current competency evidence review surface

The current Review / Development evidence history remains inspectable, while explicit human synthesis layers such as Cross-Run Observation and Development Direction are editable Review / Development state.

It answers:

- What evidence has accumulated?
- Which competency does it belong to?
- In which environment/purpose did it occur?
- What was the reviewed outcome?
- What was the Study question/scope?
- What did the technician conclude?
- Under which Trade Plan revision did it occur?

It can filter by competency and show simple descriptive counts.

Those counts are **not scores**.

---

# 18B. Cross-Run Observation

Cross-Run Observation is the human interpretation layer over multiple reviewed evidence records for one competency.

It answers:

> What seems to be happening across these reviewed runs?

It is intentionally separate from Development Direction:

```text
Competency Evidence
= individual reviewed observations

Competency Synthesis
= descriptive coverage across evidence

Cross-Run Observation
= human interpretation of what seems to be happening

Development Direction
= what the technician chooses to do next

Evidence Maturity
= future confidence/governance

Eligibility
= future Trade Plan-governed permission
```

Examples of Cross-Run Observations:

- "Session context is reliable in NYAM but inconsistent in London."
- "Intermediate-liquidity classification breaks down after large expansion."
- "The issue appears only in older evidence; recent Replay runs do not reproduce it."
- "No stable recurring behavior is clear yet; evidence is mixed."

Cross-Run Observation is not automatic pattern detection. The Cockpit may display descriptive counts and history, but the technician authors the interpretation.

The term **Cross-Run Observation** is deliberate. Avoid **Pattern Observation**, which can be confused with market-pattern hunting rather than synthesis of reviewed study data.

For v0, one current mutable observation per competency is sufficient. Supporting evidence is optional. Saving an observation does not alter Development Direction, Competency State, Evidence Maturity, progression, or Eligibility.

---

# 19. Playbooks

A Playbook is a declarative, versioned reusable trading method owned by the Trade Plan.

A Playbook may define:

- applicability/context,
- watch points,
- entry criteria,
- targets,
- management guidance,
- risk guidance,
- authorization requirements.

Trading Runs preserve the relevant Playbook revision/snapshot so future Review can reconstruct what rules were actually in force.

---

# 20. Models are scaffolds, not cages

Named ICT models are useful structures, but the Cockpit should not force every valid market opportunity into a named model.

A future opportunity may originate from:

- a named Playbook,
- a technician-defined hypothesis,
- a day-specific setup,
- a temporal condition,
- an empirically discovered tendency,
- another Trade Plan rule.

The system should separate **source** from **validity**.

---

# 21. Opportunity state

These ideas should not be collapsed into one checkbox:

```text
Available
   ↓
Contextually Relevant
   ↓
Temporally Eligible
   ↓
Developing
   ↓
Setup Conditions Satisfied
   ↓
Authorized
   ↓
Executed / Expired / Invalidated
```

An opportunity can be relevant without being authorized.

---

# 22. Authorization

Authorization has separate layers.

```text
Setup / Candidate Conditions
            +
Trade Plan / Safety Gates
            ↓
       Authorization
```

Current semantics:

- Pending blocks entry.
- Blocked blocks entry.
- Clear safety gates + satisfied setup criteria can authorize entry.
- Authorization can later expire if context becomes stale.
- Exit/flatten must never be blocked by entry authorization logic.

Authorization is permission according to recorded state.

It is **not order placement**.

---

# 23. Future execution lifecycle

Future broker integration should preserve an explicit state machine:

```text
Analysis
   ↓
Candidate
   ↓
Evidence / Checklist
   ↓
Authorization
   ↓
Arm
   ↓
Submit
   ↓
Manage
   ↓
Close / Flatten
```

NinjaTrader integration comes after this state machine is proven in simulation.

---

# 24. Market time as first-class state

Time is not decorative metadata.

Canonical timezone:

```text
America/New_York
```

Futures day rollover:

```text
18:00 ET
```

Replay/Historical runs use selected historical market time rather than wall-clock time.

This lets the Cockpit reason about:

- sessions,
- killzones,
- temporal quarters,
- upcoming/active/closed windows,
- historical context consistently.

---

# 25. QT / AMDX architecture

Keep these layers separate:

```text
Raw time / QT facts
        ↓
AMDX / XAMD interpretation
        ↓
Possible directional meaning
        ↓
Opportunity relevance
        ↓
Authorization
```

The lower layer does not automatically imply the higher layer.

Example:

> A quarter alignment exists.

does not automatically mean:

> Price will move higher.

and certainly does not mean:

> Entry is authorized.

---

# 26. QT hierarchy

Current conceptual hierarchy includes:

- 16-year cycle,
- Quadrennial,
- Yearly,
- Monthly,
- Weekly,
- Daily,
- Session,
- 90-minute cycle.

The 22.5-minute cycle remains omitted unless later work justifies restoring it.

Raw stack alignment is currently descriptive context.

---

# 27. Economic news / calendar context

Future structured news context can influence:

- TDA,
- QT/AMDX interpretation,
- opportunity context,
- authorization,
- later analytics.

Examples include:

- NFP,
- CPI,
- FOMC,
- holidays,
- early closes,
- red-folder events.

The intended model is structured context, not merely a calendar widget.

---

# 28. Structured records and derived outputs

Authoritative records live in structured data.

Derived outputs include:

- Trade Summary text,
- Study Find text,
- screenshots,
- share cards,
- future reports,
- Trilium packages.

The rule is:

```text
Structured record
      ↓
Derived representation
```

not:

```text
Generated summary
      ↓
only copy of important data
```

---

# 29. Summary templates

Summary templates are versioned Workbench configuration.

They are **not Trade Plan rules** because they affect representation rather than trading permission.

Published revisions are immutable.

Generated output preserves template provenance.

---

# 30. Workbench vs Lab

These are related but not identical.

## Workbench

Configuration/design/research administration.

Possible responsibilities:

- Trade Plan editing,
- Playbook editing,
- workflow configuration,
- summary-template editing,
- revision publishing,
- evidence configuration,
- later analytics configuration.

## Lab

Study operating environment.

Lab is where the technician deliberately investigates market behavior or practices a skill.

```text
Workbench
"design the system"

Lab
"practice / investigate within the system"
```

---

# 31. Study Find

Study Find is a structured notable-observation record.

It may capture:

- pattern/context,
- available move,
- notes,
- charts.

Long term it can be linked to:

- Trading Run,
- competency,
- Trade Plan revision,
- Review/Development follow-up.

A Study Find is not automatically competency evidence unless a deliberate relationship exists.

---

# 32. Trade Summary

Trade Summary is a structured trade/execution record with shareable generated output.

Long-term it should link clearly to:

- Trading Run,
- Trade Plan revision,
- relevant Playbook,
- authorization state,
- process provenance.

---

# 33. Revision and provenance

The central historical question is:

> What exact rules/process/context were in force when this decision was made?

Useful provenance may include:

- Trade Plan revision,
- Process Blueprint/workflow revision,
- Playbook revision/snapshot,
- competency definition revision through the Trade Plan,
- management/risk/safety rule revision,
- summary-template revision.

Revision control is cross-cutting architecture, not a standalone feature destination.

---

# 33A. Stable revision vs candidate revision

Trade Plan revisioning protects a known-good system while allowing deliberate experimentation beside it.

Example:

```text
rX — stable / trusted
- profitable/successful operating baseline
- exact models, competencies, rules, and process remain fixed
- historical evidence keeps its original meaning

        ↓ branch/evolve deliberately

rY — candidate
- add a model
- add a competency
- refine a rule
- collect new Study/Rehearsal/Validation evidence
- compare against rX before deciding whether rY should become trusted
```

The important rule is:

> Development of rY must never rewrite what rX meant.

That applies particularly to competency evidence.

If a competency definition is identical in rX and rY, evidence from both revisions may remain meaningfully comparable.

If the competency definition changes, older evidence remains valid evidence of performance against the **old definition**. It does not silently become evidence of the revised skill.

If rY adds an entirely new competency, pre-rY records do not automatically count toward it. A future retrospective mapping tool may inspect old records, but any mapping must be explicit and preserve both original and retrospective provenance.

This is why Trade Plan revision identity is not merely an audit field. It is part of the Cockpit's experimental method:

```text
What was the trusted system?
What changed in the candidate?
Which evidence belongs to which definition?
Did the change actually improve the system?
```

Competency Synthesis should therefore preserve revision provenance while avoiding noisy warnings based only on whole-plan revision differences. A meaningful caution requires evidence that the competency definition itself changed.

---

# 34. Why historical truth matters

Suppose Trade Plan Alpha 0.7 permits one interpretation and Alpha 0.8 changes it.

A 0.7 run must not silently appear to have used 0.8 rules later.

Therefore:

```text
Run
  ↓
stores/snapshots governing revision
  ↓
future Review can reconstruct
what the technician actually knew/used then
```

This is essential for honest process analytics.

---

# 35. Current progression and attainment states

Current progression eligibility uses:

- AVAILABLE
- NOT CONFIGURED
- BLOCKED

These are current permission results, not competency scores.

## AVAILABLE

The configured Trade Plan progression policy is satisfied now.

## NOT CONFIGURED

The current Trade Plan does not define how to decide that upward boundary.

This does **not** mean approved. Under Alpha 0.7 it remains deliberately non-restrictive because no real progression policy has yet been published.

## BLOCKED

A configured policy exists and at least one required condition is not satisfied or cannot be safely evaluated.

The C3 evaluator explains the contributing requirement results.

Current Eligibility remains derived on demand rather than stored as mutable truth.

## Historical Progression Attainment

C4 adds a separate historical concept:

> This configured boundary was deliberately crossed while eligibility was AVAILABLE.

Progression Attainment stores the governing Trade Plan revision, policy, environment, time, and the eligibility snapshot that justified the crossing.

Historical attainment is never rewritten merely because current eligibility later changes.

The separation is:

```text
Competency State
= what skill is believed to exist

Current Eligibility
= what the current Trade Plan permits now

Progression Attainment
= what boundary was actually cleared/crossed historically

Development Direction
= what work should happen next
```

---

# 36. Eligibility loss, revalidation, and regression

A current BLOCKED result does not automatically mean skill regression.

When a previously attained boundary loses current support, C4 distinguishes the condition before interpreting its cause.

## Eligibility Loss Detected

If the same Trade Plan revision and policy previously supported an attained boundary but current eligibility is now BLOCKED, Cockpit may identify:

> Eligibility Loss Detected

This is an objective comparison, not a competency judgment.

## Revalidation Required

If historical attainment belongs to a different Trade Plan revision/policy and the current revision is BLOCKED, the appropriate default interpretation is revalidation, not regression.

Prior skill/proficiency is not erased merely because current contextual evidence is insufficient.

## Confirmed Competency Regression

This is a human-reviewed interpretation that the underlying skill itself has materially deteriorated.

It is never inferred automatically from one policy failure.

Even after confirmation, v0 does not automatically mutate Competency State, Evidence Maturity, or Development Direction.

## Never attained

If a boundary has never been attained and current eligibility is BLOCKED, this is simply not-yet-attained progression. It is not regression.

## Voluntary step-down

Choosing a lower environment despite higher eligibility is non-punitive. Historical attainment remains intact and Competency State is unchanged.

## Temporary operating pause

News, risk limits, personal condition, account restrictions, market closure, and similar operating constraints remain a separate layer.

Future effective access may compose:

```text
Progression Eligibility
        +
Temporary Operating / Safety Restrictions
        ↓
Effective Environment Access
```

Temporary operating restrictions must not be mislabeled as progression regression.

## Recovery

Regression/revalidation recovery uses the same transparent Trade Plan progression policy:

```text
Study / Rehearsal / Validation work
        ↓
new reviewed evidence / governance updates
        ↓
same progression-policy evaluation
        ↓
AVAILABLE again
```

No separate recovery score or hidden readiness mechanism is introduced.

---


# 37. Evidence Maturity

Evidence Maturity is the governance layer that asks:

> Can this evidence set support a trustworthy decision at this progression boundary?

It does not say how skilled the technician is and does not make the progression decision.

The accepted v0 profile is non-numeric and examines:

- Volume / Sample Depth,
- Environment Relevance,
- Recency,
- Consistency,
- Context Coverage,
- Revision Relevance.

The profile is boundary-aware:

```text
Trade Plan
+ competency
+ progression boundary
```

Candidate boundaries:

- Study -> Rehearsal,
- Rehearsal -> Validation,
- Validation -> Execution.

The accepted v0 human states are:

- Not Assessed,
- Insufficient Evidence,
- Developing Evidence,
- Decision-Usable Evidence.

These labels describe decision-usability of the evidence, not readiness to advance. The state layer is deliberately removable if real use shows it is too evaluative; the six-dimensional profile remains the durable substrate.

Keep the layers separate:

```text
Evidence Maturity
= can the evidence support a trustworthy decision?

Progression Policy
= what rule does the Trade Plan apply?

Eligibility
= is that rule currently satisfied?
```

No numeric readiness percentage or hidden weighted score is implied.

---

# 37A. Progression Policy

Progression Policy is the Trade Plan-owned layer that says what must be true before an upward training boundary may be crossed.

It is revisioned with the Trade Plan because changing progression requirements changes permission semantics.

v0 uses one policy per boundary:

- Study -> Rehearsal,
- Rehearsal -> Validation,
- Validation -> Execution.

A boundary policy can contain competency-scoped and boundary/global gating requirements. Required competencies are explicit.

The v0 policy vocabulary is intentionally small:

- Evidence Maturity State,
- Competency State,
- Evidence Purpose Present,
- Human Certification.

Every listed requirement must pass. There is no weighting, majority vote, empty-policy auto-pass, or casual override.

C2 defines the policy. C3 evaluates it.

---

# 37B. Competency continuity across Trade Plan revisions

A Trade Plan revision change does not automatically erase skill.

If a competency definition is unchanged from rX to rY, prior evidence and proficiency can remain meaningful. What may need to change is **contextual validation under the new plan**.

Example:

```text
rX:
Draw on Liquidity = Proficient

rY:
Draw on Liquidity definition unchanged
but session/process/model context changed

Result:
Competency knowledge may remain Proficient
while rY requires fresh Rehearsal/Validation
before higher-level eligibility is restored
```

This avoids confusing:

```text
"I understand this competency"
```

with:

```text
"I have proven this competency inside the revised system"
```

If the competency definition materially changes, old evidence stays valid for the old definition but must not silently certify the new definition. The correct re-entry point may be Study, Rehearsal, or Validation depending on the change.

A new competency starts without inherited evidence unless a later explicit retrospective mapping is performed.

Future definition-level identity/fingerprinting should make unchanged-vs-changed competency continuity machine-verifiable.

---

# 37C. Learning-rate analytics direction

Long term, the Cockpit should analyze not only whether progression occurred, but how efficiently trustworthy competence was built.

Useful future questions include:

- How long did this competency take from first exposure to useful proficiency?
- Which rung consumed the most time?
- Did related prior competencies shorten the learning curve?
- How much additional benefit came from more Study before Rehearsal?
- At what point did additional practice show diminishing returns?
- Which competency families/genres show similar learning curves?

The goal is lifetime mastery with increasingly efficient allocation of deliberate-practice time.

This is a future analytics layer. It does not justify current readiness percentages or arbitrary progression thresholds.

---


# 37D. Operator-loop progression guardrails

C5 completes the Milestone C progression-governance loop by defining **where** progression is enforced and how the operator recovers from a block.

Progression eligibility is a **new-run / upward-environment transition guardrail**:

```text
Study -> Replay
Replay -> Forward
Forward -> Live
```

For a configured boundary:

- **AVAILABLE** permits the deliberate upward launch and that crossing may record immutable Progression Attainment,
- **BLOCKED** prevents the upward launch, explains the exact failing/unknown requirements, and keeps lower-rung operation available,
- **NOT CONFIGURED** remains explicitly ungoverned by progression policy; under Alpha 0.7 this is deliberately non-restrictive and creates no attainment.

The launcher is the enforcement point for starting a higher environment. Progression eligibility is **not** a continuous runtime kill switch.

Once a run has legitimately started:

- later progression changes do not terminate it,
- later progression changes do not silently demote its environment,
- run provenance remains historical truth,
- a future new upward transition is evaluated again under current policy.

Progression remains separate from trade/setup authorization:

```text
Progression Eligibility
= may I start/use this higher environment?

Trade / Setup Authorization
= may I enter this trade now?
```

A progression AVAILABLE result does not authorize a trade. A trade/setup Clear result does not grant progression eligibility. Exit/flatten remains outside both entry and progression gating.

When configured progression is BLOCKED, Cockpit may provide deterministic assistance derived from the explicit requirement state:

- show the governing boundary,
- show concise blocker names,
- reveal requirement detail on demand,
- stage the recommended lower environment without auto-starting,
- route directly to **Review / Development > Progression**.

This assistance is not inferred coaching and does not mutate Competency State, Evidence Maturity, Development Direction, regression classification, or historical attainment.

The normal lower route is:

```text
Replay blocked   -> Historical Backtest / Study
Forward blocked  -> Replay / Rehearsal
Live blocked     -> Forward / Validation
```

Voluntary or staged downward movement is non-punitive.

Human Certification remains authored under **Rules / Safety > Progression Policy**. Review / Development > Progression explains the requirement and current result without creating a second authoritative edit path.

Current C5 integration state is derived on demand. No persisted readiness/current-status table or numeric score is introduced.

Milestone C is complete with this operator-loop integration. Alpha 0.7 still publishes no real progression policy, so its Replay/Forward/Live boundaries remain NOT CONFIGURED until a later Trade Plan revision deliberately defines real requirements.


# 38. The current architectural frontier

The learning/progression chain is now structurally complete through Milestone C:

```text
Targeted Study
      ↓
Competency Evidence
      ↓
Replay Integration
      ↓
Forward Validation
      ↓
Progression / Eligibility
      ↓
Live Execution
```

The next major roadmap frontier is **Context maturity — QT/AMDX, news, and distortions**. Continuous operator-loop hardening remains parallel and should be driven by friction observed during real use rather than generic polish.

Do not let older detailed feature discussions silently displace this frontier.

---

# 39. Current and near-future milestone structure

The accepted milestone order is:

1. Competency evidence loop
2. Review / Development synthesis
3. Evidence Maturity and progression governance
4. Continuous operator-loop hardening in parallel
5. Context maturity: QT/AMDX, news, distortions
6. Execution-safety simulation
7. NinjaTrader integration
8. Shared / multi-device operation

---

# 40. What is intentionally not the current priority

These remain valid possible future features, but they are not the center of gravity:

- Film Night visual polish,
- responsive chart galleries,
- broad Live-Watch expansion,
- deep TradingView integration,
- hardware controls,
- large KPI dashboards,
- embedded charting,
- multi-device synchronization,
- NinjaTrader live order submission.

Real operator friction can promote an item earlier if it becomes blocking.

---

# 41. Source-of-truth map

```text
Question                               Source of truth
────────────────────────────────────────────────────────
What code currently exists?           Git + tests
Where did we stop?                    PROJECT_STATE.md
What should the product become?       PROJECT_REQUIREMENTS.md
Why was this architecture chosen?     DECISIONS.md
Which old idea was superseded?        DECISION_AUDIT.md
How did architecture evolve?          PROJECT_EVOLUTION.md
How should a new chat resume?         HANDOFF.md
How do I understand the system?       SYSTEM_GUIDE.md
What trading rules are authoritative? Versioned Trade Plan data
```

---

# 42. Common terminology mistakes to avoid

## “The dropdown is the competency system.”

No.

The dropdown is a temporary evidence-filter UI.

The competency is a shared domain object.

---

## “Evidence is the score.”

No.

Evidence is the underlying observation/history.

Metrics can later be derived from evidence.

---

## “A high metric automatically means Live-ready.”

No.

A Trade Plan progression policy must define how evidence/metrics relate to eligibility.

---

## “Replay means Study.”

Not exactly.

Replay is the **Rehearsal environment**.

It can have a Study focus, but its default purpose is integration/rehearsal.

---

## “Forward is just paper trading.”

Too narrow.

Forward is **Validation** against live unfolding information without normal Live-capital consequences.

The account context may be Sim/Paper.

---

## “Prop vs cash is the progression ladder.”

No.

Account type comes after eligibility.

---

## “A concept exists in ICT, therefore it must be a competency.”

No.

The Trade Plan decides which concepts are foundational enough to define as competencies.

---

## “Old records should automatically count toward a newly added competency.”

No.

Retrospective mapping must be explicit and preserve provenance.

---

## “QT alignment authorizes a trade.”

No.

QT/time facts are context. Authorization remains a separate process.

---

# 43. A full example

Assume the Trade Plan contains:

```text
Competency:
Draw on liquidity
```

The technician notices weakness during Review.

```text
Review
  ↓
"Repeatedly identified the wrong intermediate draw"
  ↓
Targeted Study suggested
```

The technician starts Historical Study:

```text
Environment: Historical Backtest
Purpose: Study
Competency focus: Draw on liquidity
Question:
"Can I distinguish external draw from intermediate liquidity?"
```

The run is reviewed:

```text
Outcome: Refined
Note:
"Correctly identified external draw in most examples,
but misread consolidations after large expansion."
```

The Cockpit stores evidence.

Later the technician performs Replay:

```text
Environment: Replay
Purpose: Rehearsal
Competency focus: Draw on liquidity
```

More evidence accumulates.

Future Review / Development may eventually conclude:

```text
Historical recognition:
well demonstrated

Replay integration:
improving

Forward validation:
insufficient evidence
```

A future Trade Plan progression rule may then say:

```text
Forward remains required before Live use of this competency
can be considered sufficiently demonstrated.
```

The important chain is:

```text
Definition
  ↓
Deliberate practice
  ↓
Evidence
  ↓
Metrics / synthesis
  ↓
Evidence Maturity
  ↓
Explicit progression rule
  ↓
Eligibility
```

No layer silently invents the next one.

---

# 44. How to evaluate a new feature idea

When a new idea appears, ask:

1. Is this a new **domain concept**, or merely a UI representation?
2. Who owns it: Trade Plan, profile state, evidence, Workbench configuration, or runtime?
3. Does it change historical interpretation?
4. Does it require revision identity?
5. Is it descriptive evidence or an evaluative conclusion?
6. Does it affect eligibility or authorization?
7. Is there enough evidence to automate the decision?
8. Does it strengthen the current frontier, or is it a downstream convenience?

This checklist helps keep useful ideas from accidentally changing architecture.

---

# 45. Guide maintenance rule

Update this guide when a change materially alters:

- canonical terminology,
- subsystem ownership,
- major process loops,
- learning/progression architecture,
- competency/evidence semantics,
- authorization/eligibility relationships,
- source-of-truth boundaries,
- the distinction between current UI and underlying domain concepts.

Do **not** update it for every bug fix, label tweak, or minor control change.

When this guide becomes inconsistent with canonical requirements/decisions, fix the guide rather than treating it as an alternate authority.
