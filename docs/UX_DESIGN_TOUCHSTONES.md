# UX design touchstones

**Status:** Current design-review ledger, 2026-10-14. These phrases preserve compact product meaning recovered from the project history. Use them to challenge proposed layouts and interactions; do not treat them as slogans that substitute for task evaluation.

Read with [Workspace Parity](WORKSPACE_PARITY.md), [UX Context Reconciliation](UX_CONTEXT_RECONCILIATION.md), [UX Friction Research](UX_FRICTION_RESEARCH.md) and [Project Requirements](PROJECT_REQUIREMENTS.md).

## How to use this ledger

For each material UX proposal:

1. identify which touchstones apply to the task;
2. show how the proposal preserves them, or record the deliberate tradeoff;
3. exercise the relevant goal-based journey;
4. distinguish implemented behavior from presentation still being tested.

A mockup passing functional assertions does not close a touchstone. A touchstone can also be satisfied without copying an old widget arrangement exactly.

## Touchstones and current implications

| Touchstone | Required design meaning | Current state / cross-examination question |
| --- | --- | --- |
| **“A shiny new roofing nail gun…looking for the blueprints.”** | Features belong to an executable trading and learning process. | Process/runtime architecture is implemented. Does the proposed surface make the process clearer than the collection of tools? |
| **“Foundation and Rules define the operating constraints. Playbooks define valid methods. Process operates the trading day. Review / Development improves the system.”** | Major areas have distinct purposes and should be recognizable as such. | Domain ownership exists; mature section identity is unresolved. Can the technician tell which kind of work is happening at a glance? |
| **“A station really has three jobs: Action → Observe → Carry Forward.”** | A station guides an analytical operation, including legitimate manual chart work, and retains the conclusion needed later. | Actions, observations and completion exist; separate carry-forward presentation remains incomplete. Does Focus say what to do, what to notice and what survives? |
| **“The Trade Plan says what the process is. The session says what happened when you executed it today.”** | Versioned definitions and run evidence remain separate. | Strongly implemented. Does the UI make definition editing versus current-run recording unambiguous? |
| **“Your eye moves through TradingView and the cockpit in the same direction.”** | TDA uses spatial layout parity. Each revision-defined TDA Deck can pair with a four-pane TradingView layout: top-left maps to top-left, top-right to top-right, bottom-left to bottom-left and bottom-right to bottom-right. Both monitors should read like facing pages. | Focused operator trial accepts the relationship. Does each Deck preserve physical chart-cell correspondence, criteria and points of interest across repeated looks away and back? |
| **“Focus asks: What am I supposed to be doing right now? Deck asks: Where am I in the whole analytical picture?”** | Guided detail and bird's-eye orientation are distinct projections of the same state. | Native behavior exists; the rejected walkthrough blurred the purposes. Can Deck selection return directly to the matching Focus operation without losing the map? |
| **“The pane view gives the process a kind of working memory.” / “No duplicated workflows.”** | Prior conclusions remain glanceable; Focus and Deck never require copied entries. | Shared state is implemented and focused review validates quiet inactive panes plus subtle selection/state cues. Can the technician reacquire position peripherally after looking to TradingView? |
| **“The cockpit should remember where you were, what you had done, and what remained.”** | Restart and interruption recovery preserve both data and orientation. | Persistence is strong; visual reacquaintance needs review. Can the operator resume without reconstructing scope and location? |
| **“What changed since my last glance?”** | The Cockpit is a dynamic partner in reading the market, not a form that requires a complete reread. Stable state stays quiet; changed, unsafe, unresolved or newly actionable facts earn salience. | Accepted as a cross-suite standard. Can the technician return from TradingView and locate the meaningful delta before rereading stable context? |
| **“Salience should be earned.”** | Color, contrast and interruption reflect operational meaning rather than decoration or reassurance that nothing changed. | Accepted as a cross-suite standard. Does the strongest cue identify a genuine change, decision or safety condition? |
| **From “the cockpit knows where I am” to “the cockpit knows what transitions are legitimate from here, and why.”** | Navigation, completion and process decisions remain distinct and explainable. | Explicit transitions are implemented. Does the design expose legitimate next actions without turning navigation into certification? |
| **“Conceptual synchronization is the valuable part first.”** | Chart/process meaning should align before electronic automation. Build a data bridge only for information with a defined role. | Shared time/QT/AMDX context exists; broad TradingView control remains deferred. Does an integration reduce a known task cost? |
| **The windsock: “help organize the information without pretending it can replace interpretation.”** | Attention, interpretation, potency and authorization remain distinct. | Initial attention and authorization substrates exist. Does a cue orient the technician without claiming probability or permission it has not earned? |
| **“The process knows what you are doing, but it doesn’t yet know enough about when you are doing it.”** | Market time, session, QT and AMDX are shared foundational context. | Substrate is strong; spacious calendar/news rendering remains future work. Does each projection use the maintained context without inventing another owner? |
| **“Environment is how reality is presented; purpose is why the technician is doing the run.”** | Historical Backtest, Replay, Forward and Live stay distinct from Study, Rehearsal, Validation and Execution intent. | Model semantics are implemented. Does each workspace emphasize its operating purpose while retaining the shared runtime? |
| **“Lab teaches components. Replay integrates them. Forward proves them against live information flow. Live executes them with capital at risk. Review sends weaknesses back down the ladder.”** | The learning ladder has different operating contracts and evidence meanings; Review can route work downward. | Governance and routing substrate is substantial; mature differentiated workspaces are incomplete. Does the proposal feel like the correct rung? |
| **“Evidence Maturity Profile.”** | Evidence decision-usability is assessed by competency and progression boundary, separately from competency state, policy and eligibility. | Implemented as a nonnumeric six-dimension profile. Does the UX explain the weak dimension and offer a relevant next Study route without inventing a score? |
| **“Firm enough to lock me out of making mistakes while welcoming me warmly into…the solution—study time.”** | Explainable upward gates and easy downward practice belong together. | Gate and lower-stage staging machinery exists; Alpha 0.7 has no invented real thresholds and the welcoming Study-first experience remains proposed. Does a block provide a useful, low-friction remedy? |
| **“A platform that is both sturdy and receptive to future configuration.”** | Preserve provenance, revision and transaction safety while allowing plan-owned definitions, criteria and layouts to evolve. | Architecture is strong; configurable mature UI and physical-control vocabulary remain later work. Does the design add flexibility through explicit configuration rather than hidden special cases? |

## Required parity review for TDA proposals

Any TDA layout proposal should demonstrate these cases before implementation acceptance:

1. Show one four-pane TradingView deck beside its corresponding four-pane cockpit Deck.
2. Identify each chart role and matching station position without relying on memory or an external legend.
3. Follow the same top-left → top-right → bottom-left → bottom-right reading path on both displays, unless the revisioned deck explicitly defines another path.
4. Open a station from its Deck pane, perform its Action/Observe/Carry Forward work in Focus, and return to the unchanged spatial map.
5. Confirm that completed/current/pending state and the short retained conclusion are visible without expanding all four forms.
6. Reopen the run and verify that the deck, station, selection and recorded work restore together.
7. Reorder a disposable deck definition and verify that chart-role/layout metadata changes deliberately rather than through incidental navigation.

The first prototype can use static chart-role placeholders; electronic TradingView control is not required to test layout parity.


## Operator evidence — adjustable overview/detail space (2026-10-20)

During integrated Study check 304, the operator instinctively found and used the Saved Study Finds splitter and called its availability a welcome surprise. Adjustable pane widths are a positive discoverability result: preserve a recognizable drag handle where overview and detail compete for space. Use bounded splitters rather than an unrestricted dockable dashboard; retain meaningful pane identity and test minimum widths, keyboard routes and restart. This is a useful interaction direction, not approval to add resizers everywhere.


## Operator evidence — spatial restoration relative to external charts (2026-10-20)

After passing the 310 correction, the operator emphasized that stable window placement and size reduce daily effort because Cockpit is arranged relative to TradingView and potentially other programs. Treat restoring position, dimensions and useful divider proportions as working-context recovery, with sensible recovery when screens change. Analytical layout comes from the revisioned Trade Plan; these preferences describe the workstation arrangement and should not require routine manual reconstruction. The shared MainWindow restoration slice implements normal-close recovery; it does not control external applications.
