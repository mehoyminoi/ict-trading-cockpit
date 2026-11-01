# Shared workspace restoration — bounded UX3 completion

Branch `feature/workspace-restoration-v0` starts from `bbf44f8`, the operator's published 306–310 PASS result. This carries the accepted demo behavior into the normal MainWindow and preserves the positively reviewed Study Review splitter.

## Ownership

The revisioned Trade Plan defines analytical structure: modes, Decks, station count/positions and chart roles. Personal workspace settings preserve how that work fits beside external charts: window size/position and divider widths. Restoring those preferences must not create a run, certify completion, or substitute a different startup destination.

MainWindow saves geometry on normal close and restores it after normal startup routing has completed. Study Review split state saves on dragging and on close when that workspace is visible. Hidden/unvisited review state is not overwritten on close. The existing TDA split setting is retained. All settings use the existing per-database `.workspace.ini`, so synthetic demos and the regular database remain separate. Missing or wrong-type settings fall back to defaults. Qt's geometry restoration handles screen bounds; physical multi-monitor/hotplug testing remains future operator evidence.

No schema change (47), plan revision, broker/order behavior, capture ownership or active-run routing changes. No attempt to configure TradingView or another application. Crash/forced-kill recovery of the last window movement is not claimed; geometry is saved on normal close.

## Milestone boundary

This closes the observed shared-shell restoration gap before proceeding to UX4 criteria study/authoring. It does not open a general layout editor or change the five-station TDA definition. The operator's motif is explicit: plan changes should determine analytical layout; routine use should not require rearranging the cockpit around charts each day.

## Validation

37 focused tests passed across workspace restoration, MainWindow, Study startup, mapped TDA Focus, Study Find review, runtime orientation, integrated Study tasks and smoke-test documentation. Restoration checks include normal-close geometry and divider recovery, invalid saved settings with an active run, and recovery from an off-screen saved position. Operator checks 311–312 remain pending.
