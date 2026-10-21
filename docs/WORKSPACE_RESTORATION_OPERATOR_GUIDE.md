# Workspace restoration — operator guide

After publication, use the existing startup demo with a new separate directory:

```bash
python tools/study_startup_demo.py --data-dir /tmp/ict-workspace-restoration-v0
```

This tests the actual cockpit MainWindow. Reuse the same command/directory for restarts. No Trading Run needs to be started, and TDA checks 306–310 do not need repeating.

## 311 — Main window position and size

Resize the cockpit noticeably, move it to a useful place beside your charts, and close it normally using the window close control. Reopen with the same command. Expect the same size and position after drawing settles. With no active run, Study remains the starting tab; restoration is not intended to resume the last arbitrary tab. If your monitor arrangement changed, Qt may move the window onto an available screen.

## 312 — Study Review divider

Open **Study Review**. Drag the divider between **Saved Study Finds** and its detail area to a noticeably different width. The list may be empty; that is fine. Close and reopen the same demo, then select **Study Review** again. Expect the same division at the restored window size. Visit Study, close and reopen once more, then return to Study Review: leaving Review hidden must not discard its saved width.

Report 311–312 PASS / FAIL / QUESTION. No display reconfiguration, real-data migration, order activity or further TDA retest is required.
