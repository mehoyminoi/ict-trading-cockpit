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
9. **Close the alpha feedback loop.** While the product is being dogfooded, friction and feature wishes should be capturable in seconds and retained in a human-readable form for later prioritization.

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

Current/near-term flow:

`TradingView chart -> clipboard/file capture -> managed attachment -> structured study/trade record -> generated share card`

Clipboard image paste is an accepted high-value bridge for TradingView/Ksnip use.

### 5.4 Responsive chart gallery — alpha priority 6/10

Chart images are first-class study data and should become automatically visible when reviewing a Study Find or Trade Summary rather than requiring filename-by-filename navigation.

Desired behavior:
- 1 image: large primary view.
- 2 images: side-by-side when space permits.
- 3 images: balanced 2+1 or equivalent responsive arrangement.
- 4+ images: compact responsive grid with easy access to full resolution.
- Clicking/selecting an image opens the original full-resolution capture.
- Layout should adapt to available panel/window size rather than assume one fixed geometry.
- The gallery infrastructure should eventually be shared by Study Find, Trade Summary, Film Night, and Lab review views.

Priority: **6/10**. Important for visual review and Film Night, but below the immediate alpha feedback loop and Trade Summary data-capture path.

An embedded TradingView-style chart can remain a later option if it becomes valuable, but is not currently a priority.

## 6. Interaction and Input Requirements

### 6.1 Current successful interaction patterns

- Guided Back/Next buttons.
- Standard Tab/Shift+Tab navigation inside steps, with workflow navigation at step boundaries.
- Logitech MX Master horizontal thumbwheel for previous/next workflow navigation.
- Logitech MX Master Back/Forward buttons for previous/next workflow navigation.
- Clipboard chart paste from the normal TradingView/Ksnip workflow.

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

## 7. Alpha Feedback / Friction Capture — alpha priority 9/10

During alpha testing, the application should provide a nearly instantaneous way to record friction, missing capability, workflow confusion, or a feature wish without abandoning the current trading/study context.

Priority: **9/10**. This is now an early alpha capability rather than a deferred analytics feature because it closes the feedback loop while the product is being actively dogfooded.

### 7.1 Design goal

The capture mechanism should take only a few seconds and should not force the user into a separate planning system while trading or reviewing charts.

Preferred flow:

`notice friction/wish -> one action/hotkey -> short note -> continue workflow`

A friction marker should automatically capture useful context where available, such as:
- Timestamp.
- Active app area/tab/workflow.
- Current record or draft identifier when applicable.
- Current workflow step or field when available.
- A lightweight category such as `friction`, `wish`, `bug`, or `review later`.
- Freeform human-readable note.

The note text is the important artifact. Structured context exists to make later triage easier, not to make capture cumbersome.

### 7.2 Human-readable review/export

Feedback records should be easy to review inside the suite and easy to bring into development/planning sessions.

Near-term acceptable outputs include:
- A simple chronological Feedback/Review queue in the application.
- Copy selected/all as Markdown or plain text.
- A generated Markdown feedback digest suitable for pasting into ChatGPT or committing to project notes.

This should not require GitHub issue creation during capture. Later, selected feedback items can be promoted into roadmap items, GitHub issues, or completed/archived states.

### 7.3 Future analysis

Once enough usage exists, the same data may support:
- Friction heat maps by workflow step/field/revision.
- Repeated Back/Next behavior.
- Time spent per step.
- Fields frequently revised before completion.
- Steps frequently skipped or overridden.

Those analytics remain later work; fast capture is the current requirement.

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
- GitHub remote repository / connected development workflow
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

- Git repository, GitHub remote, and known-good commit workflow.
- Python virtual environment and packaging.
- PySide6 application skeleton.
- TDA domain model.
- Bias enum and TDA statuses.
- Text normalization/validation.
- SQLite connection infrastructure.
- WAL and foreign-key configuration.
- SQL schema and explicit migrations through schema version 6.
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
- TDA draft autosave and restart restore.
- Study Find domain/repository/capture workflow.
- Study Find text summary generation/copy.
- Multiple managed chart attachments.
- Study Find clipboard chart paste.
- Study Review split-pane workflow and full-size chart opening.
- Separate Study Find draft model/table.
- Debounced Study Find draft autosave and restart restore.
- Draft chart-path restoration and safe image numbering.
- Final Study Find save clears its draft.
- Test suite currently at 95 passing tests at this checkpoint.

### Next planned milestones

1. Add low-friction alpha Feedback/Friction capture.
2. Build first Trade Summary UI with draft autosave from the beginning.
3. Dogfood Study Find + Trade Summary during TradingView replay/backtesting.
4. Use captured friction/wishes to revise priorities.
5. Add responsive chart-gallery behavior when it becomes the best next visual-review improvement.

## 12. Priority Roadmap

| Priority | Area | Status |
|---|---|---|
| 10/10 | Stable local data foundation and preservation | Strong foundation / ongoing |
| 10/10 | Guided TDA workflow and draft reliability | Working alpha |
| 9/10 | Alpha Feedback/Friction capture and human-readable review/export | **Next early capability** |
| 9/10 | Trade Summary capture with draft autosave and Trade Source/Account Context | Immediate next product workflow |
| 9/10 | Study/backtesting observation capture and clipboard chart bridge | Working alpha |
| 8/10 | Dogfood TradingView replay/backtest workflow and gather real records | Begin as soon as Trade Summary exists |
| 7/10 | Economic-news/calendar context and later filters/lockouts | Planned |
| 6/10 | Responsive chart gallery / Film Night visual review foundation | Restored to roadmap; planned |
| 6/10 | Actions/intent layer and reduced button dependence | Started with Paste Chart; expand incrementally |
| 6/10 | Workbench/Lab shell | Planned when review/configuration needs justify it |
| 5/10 | Revision-controlled workflow/template definitions | Architecture direction accepted; implementation later |
| 4/10 | Process/revision analytics | Planned after useful sample size |
| 4/10 | Multi-device study access | Requirement accepted; sync implementation deferred |
| 3/10 | Trilium integration | Planned |
| 2/10 | NinjaTrader execution adapter | Later |
| 1/10 | Live Trade Mode / safety enforcement | Intentionally last major focus |

## 13. Near-Term Development Sequence

1. Implement minimal alpha Feedback/Friction capture and human-readable review/export.
2. Build first Trade Summary UI using the existing calculation/render pipeline.
3. Include Trade Source / Account Context in Trade Summary from the start.
4. Give Trade Summary draft autosave/restart restore from its first usable version.
5. Reuse the managed attach/paste/preview/copy chart workflow in Trade Summary.
6. Begin actual TradingView replay/backtesting sessions using Study Find + Trade Summary.
7. Periodically ingest the Feedback/Friction queue into roadmap/prioritization sessions.
8. Add responsive chart gallery (priority 6/10) when visual review friction justifies the next slice.
9. Continue expanding actions/intents and reducing button proliferation based on real use.
10. Defer live execution until the study/process system is mature.

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
- Exact Workbench layout.
- Feedback capture categories and whether context tagging should remain fully automatic or allow optional editing.
- Feedback queue lifecycle: open / promoted / resolved / archived.
- Exact responsive gallery layout behavior beyond the 1–3 image priority cases.
- Draft restoration policy if multiple drafts exist.
- Whether portable laptop use initially uses manual export/import, sync service, or central DB/API.
- Offline behavior for future multi-device operation.
- Central service technology when cross-device authoritative state becomes necessary.
- Trilium linking/package format.
- NinjaTrader bridge details and execution-state reconciliation.

---

**Guiding test for future features:** Does this reduce friction, improve process adherence, preserve honest data, close the alpha feedback loop, or create a meaningful way to analyze/communicate that data? If not, it is probably not a current priority.
