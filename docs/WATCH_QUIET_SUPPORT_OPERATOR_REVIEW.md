# Quiet Watch and support-return operator review

**Reviewed:** 2026-10-14 (America/Denver)  
**Artifact:** `prototypes/watch-quiet-support-v0.html`  
**Disposition:** Partial success. Preserve the support-return and peripheral-orientation gains; do not treat the Watch composition or full-stack AMDX renderer as accepted.

## Result

The focused trial made a meaningful improvement in quietness and reacquisition after looking away to TradingView. The contextual Study Find interaction is a strong accepted direction. The current AMDX rendering is not yet sufficiently spatial or effortless: the larger inspection view magnifies a flat list instead of revealing the nested time structure.

This review authorizes another focused design iteration, not native implementation, production behavior changes or a final Watch layout.

## Strong directions to preserve

- **Study Find access and return:** one button or hotkey opens an unobtrusive contextual surface. Clicking the main Cockpit body dismisses it. The technician can return without reconstructing the operating position.
- **Future capture capability:** the mature surface should preserve the existing native screenshot-paste, managed chart storage, multiple-image and Study Find association capabilities. The HTML fixture does not implement them.
- **Peripheral reacquisition:** subdued borders, completion cues and selected-state styling make it possible to leave for TradingView and find the Cockpit position again without rereading the whole screen.
- **Watch-point salience:** restrained orange markers successfully draw the eye toward the next relevant conditions.
- **Direct active-cycle entry:** one-action legal `X(C)` / `X(R)` entry and no second Save remain required.
- **Current-state scope:** normal Watch shows what the AMDX stack is now and where the technician is within it. History and comparison do not belong here.

## Problems exposed by the trial

- The AMDX list still requires deliberate reading. It does not provide a strong visual impression of containment or the selected level's place in the whole stack.
- Full-stack inspection feels like the Watch list made larger. It does not yet provide semantic zoom, nested context or a distinct analytical workspace.
- The green quiet-state cue attracts attention merely to announce that no attention is required.
- The Full Stack exit is placed far from the entry command. The technician repeatedly looks back to the entry location to leave.
- Operating Context is already somewhat dense and may become substantially worse when multiple named models and unnamed frameworks are present.
- The complete Watch composition still lacks a broker/process-safety projection and an intentional relationship to common monitor arrangements.

## Prototype corrections

The reviewed fixture receives three bounded corrections before another use:

1. Saving a Study Find clears its three input fields instead of the close path immediately restoring the saved text as an unfinished draft.
2. The ribbon command used to enter Full Stack becomes a stable **Return to Watch** command in the same location while inspection is open. The lower return control remains redundant and visible.
3. The quiet-state banner uses neutral border, marker and typography treatment. Escalation color is reserved for a state that actually needs attention.

These corrections address clear interaction defects. They do not resolve the AMDX topology or accept the exact visual treatment.

## Contextual support rail direction

A pin-capable support region is promising if it remains a **contextual support rail, not an unrestricted dashboard builder**. The main canvas stays stable, and a purpose profile may offer one active tool and at most one deliberately pinned companion. Candidate projections include:

- Study/Replay: Study Find and relevant source material;
- Validation: criteria or Trade Plan definition reference;
- Live: connection, account/environment, risk and order-state safety information.

Panels must not rearrange themselves automatically. Safety-critical state cannot be hidden accidentally. This does not authorize arbitrary docking, a wall of floating windows or a new persistence framework.

## Broker/process panel requirement

The next complete Watch study should include a synthetic NinjaTrader/other-broker projection early enough to judge the full composition. It should answer connection, environment/account, authorization gate, risk envelope, position/order state and staged-versus-submitted status. It must support process adherence rather than become a P&L dashboard, performance scoreboard or casino-like attention surface. No broker API or order submission is authorized by this UX study.

## Monitor-orientation question

The next composition must test at least these likely arrangements:

| Arrangement | Design question |
| --- | --- |
| TradingView left / Cockpit right on one ultrawide | Which orientation and next-action cues belong on Cockpit's chart-facing left edge? |
| Cockpit on a dedicated 16:9 monitor above TradingView | Which cues must survive the larger vertical eye movement and make return position obvious? |

The goal is one standard configuration or a small set of explicit profiles, not an infinitely configurable layout. Logical actions remain shared across mouse, keyboard and later macro-pad/CAD-mouse bindings.

## Trilium evidence and the AMDX consequence

The operator supplied a screenshot of the current Trilium AMDX/XAMD hierarchy. Its expanded path is materially similar to:

`AMDX/XAMD → 2026 · D → Q2 · M → May · M → W2 · A → weekday roles`

Disclosure triangles and collapsed siblings make the containment model natural: the technician can see both the selected path and its surrounding structure. The same screenshot demonstrates the failure mode of a giant indented tree—deep indentation, long vertical scanning and loss of working space.

Therefore the tree is evidence for the **navigation model**, not a layout to copy wholesale. The next Lab study should:

- expose the current path and a limited sibling neighborhood;
- synchronize tree, breadcrumb, calendar and selected-detail workspace;
- collapse non-path branches deliberately;
- support semantic zoom so moving between year, month, week, day, session and 90-minute detail changes the workspace projection;
- keep editing and analysis in the main workspace rather than inside the indentation;
- preserve one set of navigation actions for pointer, wheel/gesture, keyboard and later hardware mappings.

The screenshot's sample dates and roles are illustrative evidence only; they do not publish AMDX judgments or rules.

## Reported goal checks

The operator explicitly reported the direct update, return continuity and reload checks as passing. An unfinished capture draft also recovered. Saving the capture staged it, but the input fields incorrectly retained the saved text; this is the corrected defect above. No acceptance is inferred for unreported visual details or the sample market content.

## Next sequence

1. Retest the three corrected Watch behaviors.
2. Investigate Lab as a synchronized feature tree, calendar and detail workspace with semantic zoom.
3. Derive a compact Watch AMDX renderer from that accepted spatial model rather than enlarging the current flat list.
4. Compose a fuller Watch trial with the bounded support rail, synthetic broker/process panel, reduced Operating Context density and monitor-orientation variants.
5. Re-review before any native shell rewrite.

