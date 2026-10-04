# ICT Trading Cockpit — Living Requirements & Roadmap

**Status:** Living document  
**Purpose:** Canonical project requirements, priorities, architecture decisions, and progress record.  
**Recommended repository location:** `docs/PROJECT_REQUIREMENTS.md`

## 1. Project Mission

Build a local-first trading process operating system that makes discretionary trading more structured, repeatable, analyzable, and boring. The application should reduce emotional decision-making by guiding the user through a consistent process, recording what happened, and allowing accumulated data to evaluate the quality of the process over time.

The application is not primarily a P&L dashboard. Its first measure of success is **process adherence**. A fully compliant "No Trade — Process Followed" outcome is successful.

## 2. Core Product Principles

1. **Process over P&L.** Reward completion and adherence, not trading frequency or profitability.
2. **Structured data is the bedrock.** Summaries, images, dashboards, statistics, and journal pages are generated views of authoritative structured records.
3. **Guided when executing; flexible when designing.** Daily use should be focused and stepwise. Editing the process belongs in a separate Workbench/Lab environment.
4. **Revision controlled process.** TDA workflows, trade plans, checklists, management rules, templates, and safety rules should eventually be versioned and immutable once used.
5. **Incomplete is data, not failure.** Users may deliberately file incomplete records; missing values must remain genuinely unknown rather than being replaced with junk values.
6. **Low-friction interaction.** Buttons, keyboard navigation, mouse controls, and future macro-pad inputs should trigger shared application actions rather than duplicate logic.
7. **Local-first and resilient.** Temporary NAS, network, Trilium, or external-service outages must not stop core local data capture.
8. **Safe evolution.** Database schema changes use explicit migrations. Application behavior should be testable in small, known-good milestones.

## 3. Desired Operating Modes

### 3.1 Guided Mode — highest current priority

Purpose: daily pre-market/TDA workflow and disciplined study capture.

Characteristics:
- One manageable step visible at a time.
- Previous information remains one or two clicks away.
- Progressive disclosure minimizes distraction.
- Clear progress through the current process revision.
- Missing required fields guide the user back to the relevant step.
- Intentional incomplete override remains possible and is recorded.
- Drafts autosave and should restore after restart.

Current prototype steps:
1. Context — instrument, analysis date.
2. Bias — weekly bias, daily bias.
3. Draw / Thesis — primary draw, secondary draw, narrative.

These are prototypes, not a permanent commitment to the final TDA structure.

### 3.2 Workbench / Lab — high future priority

Purpose: design, research, reflection, film night/backtesting, configuration, and process improvement.

Expected capabilities:
- Edit workflow definitions.
- Edit TDA fields and ordering.
- Edit trade plans/checklists/risk and safety rules.
- Edit summary templates.
- View revision history.
- Analyze performance by revision and by adherence.
- Review friction flags or queued “review later” items.
- Backtesting-find capture and cataloging.

The Workbench should feel familiar to CAD/tuning software: configurable, modular, information-dense when desired, but separate from the focused daily workflow.

### 3.3 Live Trade Mode — intentionally later priority

Purpose: precision entry, order intent, management, and safety enforcement using context established in Guided Mode.

Expected future characteristics:
- Guided Mode sets the ball on the tee for Live Mode.
- Bias, draw, allowed setup, invalidation, risk, and other relevant context carry forward automatically.
- Explicit state machine for authorization/order lifecycle.
- Entry gating based on required checklist conditions.
- Exits/flatten are never gated.
- Max trades/day, loss limits, prop/live account rules, cooldowns, and lockouts are defined by the active trade-plan revision.
- Rule violations can trigger warnings, acknowledgement, timeout, review requirement, or entry lockout.
- Simulation testing is mandatory before any live execution integration.

## 4. Process Revision System — priority future capability

Each meaningful process definition should eventually have a revision identity, for example:

- Trade Plan Rev 4
- TDA Workflow Rev 7
- Entry Checklist Rev 3
- Management Rules Rev 2
- Risk Rules Rev 5
- Safety Rules Rev 4
- Summary Template Rev 3

Once a revision has been used for a real record, it should become immutable. Editing it creates a new draft revision that can later be published.

Historical records remain linked to the exact revisions used at the time.

This enables analysis such as:
- Win rate when Rev 4 was fully adhered to.
- Average handles/trade by revision.
- Average R by revision.
- Drawdown by revision.
- Sample size by revision.
- Complete-process trades vs non-adhered trades.
- TDA accuracy by workflow revision.

Performance and process adherence must remain separate dimensions.

## 5. Study, Backtesting, and Sharing — immediate/high priority

The application should make it easy to capture and share notable study ideas before live execution features are mature.

### 5.1 Structured observations

Support records for:
- Executed trades.
- Backtesting finds.
- Replay finds.
- Live market observations.
- TDA/pre-market observations.

### 5.2 Configurable summary templates

Users should eventually define templates such as:

- Trade Summary.
- Backtesting Find Summary.
- TDA Summary.
- Daily Review Summary.

Templates should consume structured data using placeholders and produce generated artifacts rather than become the authoritative record.

Desired outputs:
- Copyable text summary.
- Chart/image summary card.
- Stored/cataloged summary package.
- Easy sharing into external chat applications.

### 5.3 Chart screenshots

Near-term preference: use screenshots/captures from the existing TradingView workflow rather than rebuilding the charting environment.

Potential future flow:

`TradingView chart -> capture/import -> structured study/trade record -> generated share card`

An embedded TradingView-style chart can remain a later option if it becomes valuable, but is not currently a priority.

## 6. Interaction and Input Requirements

### 6.1 Current successful interaction patterns

- Guided Back/Next buttons.
- Standard Tab/Shift+Tab navigation inside steps, with workflow navigation at step boundaries.
- Logitech MX Master horizontal thumbwheel for previous/next workflow navigation.
- Logitech MX Master Back/Forward buttons for previous/next workflow navigation.

### 6.2 Input architecture direction

Application actions should be logically independent of their physical triggers.

Example future actions:
- `workflow.next`
- `workflow.back`
- `mark.friction`
- `capture.chart`
- `save.find`
- `complete.no_trade`
- `trade.arm`
- `trade.flatten`

Possible triggers:
- GUI button.
- Keyboard shortcut.
- Mouse button/wheel.
- Macro pad.
- SpaceMouse.
- Future custom HID/MIDI hardware.

Dangerous actions such as arming or order submission must have stronger safeguards than harmless navigation actions.

## 7. Friction / Process-Improvement Feedback — defer implementation, preserve concept

Guided Mode should eventually support a nearly instantaneous way to mark “something here felt wrong” without opening settings or interrupting the current process.

Future flow:

`notice friction -> one-action flag -> continue workflow -> review later in Workbench/Lab`

Possible future analysis:
- Friction heat map by workflow step/field/revision.
- Repeated Back/Next behavior.
- Time spent per step.
- Fields frequently revised before completion.
- Steps frequently skipped or overridden.

Do not prioritize this before enough real workflow usage exists to justify it.

## 8. TDA Status and Adherence

Current TDA states:
- `DRAFT`
- `COMPLETE`
- `INCOMPLETE_OVERRIDE`

Important semantic distinctions:
- `None` / SQL `NULL` means not assessed or missing.
- `Neutral` means assessed and genuinely neutral.
- A complete TDA may still produce “No Trade — Process Followed.”
- An incomplete override is intentionally recorded as non-conformant rather than being blocked or filled with fake answers.

Desired future adherence data:
- Required fields completed / total required.
- Overrides used.
- Missing requirements.
- Checklist adherence.
- Management adherence.
- Trade-plan violations.

## 9. Current Technical Architecture

### 9.1 Stack

- Python 3.10+
- PySide6 / Qt desktop GUI
- SQLite authoritative local database
- pytest
- Git local version control
- VS Code
- Linux primary workstation
- NAS for safe snapshots/backups, not the live database
- Trilium on a VM for future narrative/journal integration
- TradingView for charting/study
- NinjaTrader for eventual execution bridge

### 9.2 Application flow

```text
Guided / Workbench / Future Live UI
              |
              v
        Domain models
              |
              v
         Repositories
              |
              v
     Local SQLite database
              |
              +----> safe snapshots/backups ----> NAS
              |
              +----> future summary artifacts / Trilium
```

### 9.3 Database safety

- Live SQLite database resides on local SSD.
- WAL enabled.
- Foreign keys enabled.
- Multi-step DB operations use transactions.
- Live SQLite DB is not copied naively while active; use WAL-safe backup APIs.
- Schema evolution uses explicit version migrations (`PRAGMA user_version`).
- RAID is redundancy, not backup.

## 10. Multi-Device / Laptop Requirement

### 10.1 Requirement

The application should eventually be usable from a second Linux machine, including a laptop used while traveling. Desired laptop capabilities may include:
- Guided TDA.
- Backtesting/study capture.
- Summary generation/sharing.
- Access to existing historical data.
- Eventually the same trade-plan safety state if live execution is supported remotely.

The user already has VPN access into the home network and can reach Trilium and the NAS remotely.

### 10.2 Important constraint

**Do not run the live SQLite database directly from the NAS or over the VPN.** Network filesystems introduce locking, latency, and corruption/failure-mode concerns that are inappropriate for the authoritative local SQLite database.

A NAS backup is not automatically a multi-device synchronization system.

### 10.3 Recommended staged approach

#### Phase A — portable code, local data

Near term:
- Application code moves between machines using Git.
- Each machine keeps its own local SQLite database.
- NAS stores safe backups/snapshots.
- Study-only export/import can be added if needed.

This requires little architectural change now.

#### Phase B — shared study data

When two-device data access becomes important, choose either:
- a deliberate sync/export layer between local databases, or
- a small central application/database service reachable through the VPN.

#### Phase C — authoritative cross-device safety state

If trade lockouts, max-trade counters, daily loss limits, or account safety must be enforced consistently from multiple machines, a single authoritative shared state is required.

Preferred eventual architecture:

```text
Desktop ----\
             -> secure application/API service -> central PostgreSQL
Laptop  ----/                 ^
                               |
                              VPN
```

Local SQLite may still serve as an offline cache/local-first store, but cross-device live safety cannot safely depend on independently synced SQLite copies.

### 10.4 Planning decision now

Plan for multi-device operation at interfaces and data-model boundaries now, but do not build synchronization yet.

Specific implications:
- Stable UUIDs for records.
- Explicit timestamps and revision IDs.
- Avoid machine-specific assumptions in domain records.
- Keep storage paths configurable.
- Keep database access behind repository/service interfaces.
- Future sync metadata can be added without redesigning the GUI.

## 11. Current Implementation Progress

### Completed foundations

- Git repository and known-good commit workflow.
- Python virtual environment and packaging.
- PySide6 application skeleton.
- TDA domain model.
- Bias enum and TDA statuses.
- Text normalization/validation.
- SQLite connection infrastructure.
- WAL and foreign-key configuration.
- SQL schema and explicit migrations through schema version 3.
- TDA repository create/read/update behavior.
- Duplicate protection.
- Persistence across database reopen.
- Deliberate incomplete TDA support with nullable bias/draw fields.
- Linux XDG application-data path.
- Real application DB bootstrap and clean shutdown.
- Guided three-step workflow shell.
- Context step.
- Bias step.
- Draw / Thesis step.
- Guided navigation.
- Tab/Shift+Tab boundary experiment.
- MX Master horizontal thumbwheel navigation.
- MX Master Back/Forward navigation.
- Complete TDA path.
- Missing-field guidance.
- Intentional `INCOMPLETE_OVERRIDE` path.
- GUI-to-repository persistence.
- Quiet saved-state confirmation.
- Saved/reset state and Start New TDA.
- Stable UUID throughout a draft lifecycle.
- Draft-specific repository upsert with finalized-record protection.
- Debounced TDA draft autosave.
- Test suite currently at 42 passing tests at this checkpoint.

### Next planned milestone

Restore the most recent unfinished draft on application launch:
1. `TDARepository.get_latest_draft()`.
2. `TDAWorkflowWidget.load_tda()`.
3. Test each independently.
4. Wire restore behavior into startup.

## 12. Priority Roadmap

| Priority | Area | Status |
|---|---|---|
| P0 | Stable local data foundation | In progress / strong foundation |
| P0 | Guided TDA workflow | In progress |
| P0 | Draft autosave + restore | Autosave complete; restore next |
| P1 | Study/backtesting observation capture | Planned |
| P1 | Configurable text summaries | Planned early |
| P1 | Chart screenshot/import + share package | Planned early |
| P1 | Revision-controlled workflow/template definitions | Planned architecture; implementation later |
| P1 | Workbench/Lab shell | Planned |
| P2 | Process/revision analytics | Planned |
| P2 | Basic configurable bindings/macro actions | Prototype inputs working; generalized binding system later |
| P2 | Friction flags / Lab task queue | Concept preserved; intentionally deferred |
| P2 | Multi-device study access | Requirement accepted; sync implementation deferred |
| P3 | Trilium integration | Planned |
| P3 | NinjaTrader execution adapter | Later |
| P3 | Live Trade Mode / safety enforcement | Intentionally last major focus |
| P3 | Cross-device authoritative live safety | Later; requires central shared state |

## 13. Near-Term Development Sequence

1. Restore latest draft on launch.
2. Verify draft lifecycle end-to-end.
3. Begin expanding Guided Mode based on actual use rather than speculative field growth.
4. Introduce study/backtesting-find record concept.
5. Create first configurable text-summary template system.
6. Add quick copy/share workflow.
7. Add chart screenshot/import attachment flow.
8. Begin Workbench/Lab shell when configuration/revision needs justify it.
9. Add process revision definitions and immutable published revisions.
10. Build analytics around accumulated study/process data.
11. Defer live execution until the study/process system is mature.

## 14. Development Practices

### Start of session

```text
open project
-> activate .venv
-> git status
-> pytest
-> begin work
```

### End of session

```text
pytest
-> git status
-> inspect diff
-> stage intentional milestone
-> inspect staged diff
-> commit known-good milestone
-> confirm clean working tree
```

### General implementation rule

Prefer small vertical slices with tests over large feature batches. Keep domain rules, GUI behavior, persistence, and external integrations separated enough that any one layer can evolve without forcing a rewrite of the others.

## 15. Open Decisions / Questions

These should remain explicit rather than being silently decided in code:

- Final TDA step/field definitions.
- Exact workflow revision/publishing UX.
- Study observation taxonomy.
- Summary-template syntax and editor UX.
- Screenshot capture mechanism from TradingView workflow.
- Exact Workbench layout.
- Draft restoration policy if multiple drafts exist.
- Whether portable laptop use initially uses manual export/import, sync service, or central DB/API.
- Offline behavior for future multi-device operation.
- Central service technology when cross-device authoritative state becomes necessary.
- Trilium linking/package format.
- NinjaTrader bridge details and execution-state reconciliation.

---

**Guiding test for future features:** Does this reduce friction, improve process adherence, preserve honest data, or create a meaningful way to analyze/communicate that data? If not, it is probably not a current priority.
