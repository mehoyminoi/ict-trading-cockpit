# Native Study-first startup

Implemented on `feature/study-first-startup-v0` over the operator-accepted quiet-Watch tree. Operator checks 296–300 remain pending. The [operator guide](STUDY_FIRST_STARTUP_OPERATOR_GUIDE.md) provides a retained separate demo.

## Routing and ownership

- Idle application startup opens Study. Active Trading Runs restore their existing runtime; Study offers a direct resume route and blocks staging a conflicting run.
- `StudyHomeWidget` displays context and emits navigation/staging requests. `MainWindow` supplies restored state and existing repositories. Neither introduces new storage.
- Suggestions use explicitly recorded Study Development Directions for defined competencies in the current plan revision. Most recently updated wins, using offset-aware timestamps; ties use competency ID only for stable presentation. Missing or undated basis is not guessed. This ordering is a provisional interaction choice, not skill ranking or new Trade Plan policy.
- Existing nonempty manual selection is retained during navigation. Startup does not persist an unfinished targeted-study task because the launcher does not currently own such a persisted draft. Study Find draft recovery remains a separate, explicitly labeled capture route.
- Staging invokes `ProcessRunLauncherWidget.prepare_targeted_study`, then reveals Review / Development → Practice & Launch. Only the existing explicit launch action creates a run. All eligibility, historical intent and governance requirements remain in force.
- The doorway has no dismissal obligation and no automatic phase transition. Calendar inspection need not create a run. Global navigation redesign, integrated Study task workspace and criteria authoring are later milestones.

## Verification scope

Developer evidence: **45 focused tests PASS** (five new Study-doorway/demo tests, four smoke-document tests, and 36 existing main-window/runtime/launcher/draft/Watch checks in isolated module processes). Native idle rendering inspected at 1120×876. Python 3.10 grammar for the four new/changed Python files and diff checks pass. No fresh full-suite result or operator acceptance is claimed.

Tests cover idle startup, write-free staging, active-run restart and handler guard, revision-scoped suggestions, timestamp offsets, manual selection, capture preservation and demo restart/directory guards. Existing launcher, runtime, main-window, draft and Watch regressions are also checked. Native offscreen rendering verifies the doorway fits at the tested desktop size; actual operator usability is not inferred.
