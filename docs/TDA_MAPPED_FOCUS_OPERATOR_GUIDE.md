# TDA mapped Focus — operator guide

This local trial has not been published yet. Wait for publication confirmation. Use a new separate directory initially, then reuse it:

```bash
python tools/tda_mapped_focus_demo.py --data-dir /tmp/ict-tda-mapped-focus-v0
```

The demo uses the actual current station definitions and stores synthetic station work only. No Trading Run starts. The first Deck has five stations; the fifth is intentionally shown at row 3, pending a future four-chart assignment review.

## 306 — Map and Focus.

Click Top right in the left map. The Focus heading should name IPDA Premium / Discount and the corresponding mapped position. Enter `Mapped Focus trial observation`. Its abbreviated text should appear in the same map pane. Select another pane and return; the observation remains, and the station is in progress rather than complete.
## 307 — Resizing and typing.

Drag the vertical divider between map and Focus. Neither side should collapse away. In Observation, type `1234`; this must remain text. Press Alt+3 to open bottom left. It should navigate without certifying either station. Bare numbers are not shortcuts.
## 308 — Full overview return.

Click Open full Deck overview. Both published Decks remain available. Click a station in the second Deck. Focus should open beside that Deck's map with the selected station highlighted. Navigation should not mark complete.
## 309 — Explicit completion.

Return to the first Deck's Daily Context station (row 3). Enter a short observation and click Mark Station Complete & Continue. Only that station becomes complete; Focus advances into the next Deck and its adjacent map follows.
## 310 — Restart.

Change the divider width, select a station and leave a recognizable unfinished observation. Close and reopen using the same command. Selected station, observation, completion state and divider width should restore. The demo should still have no Trading Run.

Report each item PASS / FAIL / QUESTION. This is interaction review, not final station content, four-chart assignment, or final styling approval.
